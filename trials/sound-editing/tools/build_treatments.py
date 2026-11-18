"""Build neutral-labelled comparison exports; assignment lives only in keys/."""
import copy
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import numpy as np
from check_cues import PACKET_HASH_METHOD, add, decode, packet_hash

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
sys.path.insert(0, str(BASE / 'audio-recreation/scripts'))
from render_mix import encode, loudness, sha256


def write(path, data):
    path.write_text(json.dumps(data, indent=2)+'\n')


def mux(picture, audio, output):
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(picture), '-i', str(audio), '-map', '0:v:0',
                    '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', '-movie_timescale', '48000',
                    '-n', str(output)], check=True)
    if packet_hash(output) != packet_hash(picture):
        raise ValueError('Picture packet identity changed')


def main():
    key_path = BASE / 'keys/treatments.json'
    if key_path.exists():
        raise SystemExit('Refusing to overwrite assignment key')
    asset_root = REPO / 'resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation'
    original_receipt = json.loads((BASE / 'references/receipt.json').read_text())
    picture = REPO / 'projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/gsap.mp4'
    report = json.loads((asset_root / 'mixes/04-poke/mix-report.json').read_text())
    music_input = asset_root / 'mixes/04-poke/music.flac'
    if sha256(music_input) != report['exports']['music.flac']['sha256']:
        raise ValueError('Pinned music input changed')
    mp3 = asset_root / 'ai/04-poke/music.mp3'
    if sha256(mp3) != report['audio_inputs'][0]['sha256']:
        raise ValueError('Pinned generated source changed')
    library = json.loads((BASE / 'audio-recreation/library/manifest.json').read_text())
    labels = set()
    while len(labels) < 3:
        labels.add('T-' + secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ') + secrets.choice('23456789'))
    labels = sorted(labels); secrets.SystemRandom().shuffle(labels)
    modes = ['accepted UI-only', 'sparse editorial UI', 'UI with existing pinned music']
    mapping = dict(zip(labels, modes))
    write(key_path, {'assignments': mapping, 'editorial_decisions': {
        'sparse_keys_retained_ordinals': [0, 4, 6, 9, 12],
        'sparse_policy': 'Five phrase/burst anchors replace fourteen adjacent key accents; no timing invented. Panel whooshes -5 dB and sends -3 dB. Other semantic cues unchanged.',
        'music_policy': 'Existing pinned Poke generated instrumental; music.flac -20 dB. No generation or network request.'}})
    key_path.chmod(0o600)
    original_ui = decode(asset_root / 'ui-mixes/04-poke/ui.flac')
    music_wave = decode(music_input) * .1
    productions = []
    for label, mode in mapping.items():
        folder = BASE / 'blind' / label
        folder.mkdir(); (folder / 'references').mkdir()
        cues = []; ui = np.zeros_like(original_ui)
        for cue in original_receipt['cues']:
            c = copy.deepcopy(cue); ordinal = c['ordinal']; kind = c['canonical_event']['kind']
            if mode == modes[1] and kind == 'typing' and ordinal not in [0, 4, 6, 9, 12]:
                continue
            gain_db = -5 if mode == modes[1] and kind == 'panel_open' else -3 if mode == modes[1] and kind == 'message_send' else 0
            wave = np.load(BASE / c['reference'], allow_pickle=False) * 10 ** (gain_db/20)
            add(ui, wave, c['clip_start_sample_unclipped'])
            c['treatment_gain_db'] = gain_db
            ref = folder / 'references' / f'cue-{ordinal:02}.npy'; np.save(ref, wave)
            c['reference'] = f'references/{ref.name}'; c['reference_sha256'] = sha256(ref)
            cues.append(c)
        if mode != modes[1]:
            ui = original_ui.copy()
        ui[[0, -1]] = 0
        music = music_wave.copy() if mode == modes[2] else np.zeros_like(ui)
        music[[0, -1]] = 0
        full = ui + music
        for name, samples in [('ui', ui), ('music', music), ('full_mix', full)]:
            encode(folder / f'{name}.flac', samples, aac=False)
        encode(folder / 'production.m4a', full, aac=True, bitrate='192k')
        mux(picture, folder / 'production.m4a', folder / 'production.mp4')
        receipt = copy.deepcopy(original_receipt)
        receipt['cues'] = cues
        receipt['picture_packet_hash_method'] = PACKET_HASH_METHOD
        receipt['picture_file_sha256'] = sha256(picture)
        receipt['picture_file_hash_method'] = 'SHA-256 of all original gsap.mp4 file bytes, including container and all streams; not decoded frames'
        if np.any(music):
            # Reference is the pinned input with declared gain, not decoded from
            # the stem whose integrity the review is intended to assess.
            ref = folder / 'references/continuous.npy'; np.save(ref, music)
            receipt['background_reference'] = {'reference': 'references/continuous.npy',
                'reference_sha256': sha256(ref), 'source_sha256': sha256(music_input), 'gain_db': -20.,
                'alignment_sample': 0, 'role': 'declared continuous reference waveform; subtract exact expected signal, not fitted signal'}
        (folder / 'receipts').mkdir()
        write(folder / 'receipts/production.json', receipt)
        impacts = [{'ordinal': c['ordinal'], 'frame': c['canonical_event']['frame'], 'sample': c['event_sample'],
                    'asset': c['source'].get('asset_id', c['source'].get('effect')),
                    'reference_sha256': c['reference_sha256'], 'gain_db': c['treatment_gain_db'],
                    'clip_start_sample': c['clip_start_sample_unclipped'],
                    'alignment_offset_samples': c['clip_alignment_offset_samples']} for c in cues]
        write(folder / 'cue-impacts.json', impacts)
        music_provenance = None
        if np.any(music):
            source = report['audio_inputs'][0]
            music_provenance = {'source_file': str(music_input.relative_to(REPO)), 'source_sha256': sha256(music_input),
                'source_mp3_sha256': sha256(mp3), 'generation_provider': source['provenance']['provider'],
                'generation_endpoint': source['provenance']['endpoint_id'], 'existing_generation_request_id': source['provenance']['request_id'],
                'source_provenance_sha256': source['provenance_sha256'], 'mix_report_sha256': sha256(asset_root / 'mixes/04-poke/mix-report.json'),
                'gain_db': -20., 'new_generation': False, 'reference_film_audio_reused': False,
                'license': 'Provider-generated asset; no standalone CC license or account entitlement evidence archived. Pinned existing private-review use only; external-release clearance unverified.'}
        manifest = {'label': label, 'picture': {'file_sha256': sha256(picture), 'file_hash_method': receipt['picture_file_hash_method'],
            'packet_sha256': packet_hash(picture), 'packet_hash_method': PACKET_HASH_METHOD, 'decoded_frame_hash': None},
            'ui_sources': library['sources'], 'ui_asset_receipts': [{k: c[k] for k in ['ordinal', 'source', 'target_peak_dbfs', 'pitch', 'pan', 'treatment_gain_db']} for c in cues],
            'library_manifest_sha256': sha256(BASE / 'audio-recreation/library/manifest.json'),
            'procedural_source_sha256': sha256(BASE / 'audio-recreation/synthesis/ui_synth.py'),
            'procedural_license': 'Original project synthesis source; not asserted CC0',
            'music_source': music_provenance, 'sample_rate': 48000, 'samples': len(full),
            'production_loudness': loudness(decode(folder / 'production.mp4')),
            'stem_sha256': {name: sha256(folder / f'{name}.flac') for name in ['ui', 'music', 'full_mix']},
            'stem_sum_max_error': float(np.max(np.abs(decode(folder/'ui.flac') + decode(folder/'music.flac') - decode(folder/'full_mix.flac')))),
            'build_script_sha256': sha256(Path(__file__))}
        productions.append((label, folder, full, receipt, manifest))
    target = min(m['production_loudness']['integrated_lufs'] for _, _, _, _, m in productions) - 1.
    summary = []
    for label, folder, full, receipt, manifest in productions:
        gain_db = min(0., target - manifest['production_loudness']['integrated_lufs'])
        gain = 10**(gain_db/20)
        encode(folder / 'comparison.m4a', full*gain, aac=True, bitrate='192k')
        mux(picture, folder / 'comparison.m4a', folder / 'comparison.mp4')
        for c in receipt['cues']:
            source = folder / c['reference']; dest = source.with_name(source.stem + '-review.npy')
            np.save(dest, np.load(source, allow_pickle=False)*gain)
            c['reference'] = f'references/{dest.name}'; c['reference_sha256'] = sha256(dest)
        if 'background_reference' in receipt:
            ref = receipt['background_reference']; source = folder/ref['reference']; dest = source.with_name('continuous-review.npy')
            np.save(dest, np.load(source, allow_pickle=False)*gain)
            ref['reference'] = f'references/{dest.name}'; ref['reference_sha256'] = sha256(dest)
        receipt['comparison_gain_db'] = gain_db
        write(folder / 'receipts/comparison.json', receipt)
        measured = loudness(decode(folder / 'comparison.mp4'))
        manifest['comparison'] = {'gain_db': gain_db, 'attenuation_only': True, 'target_lufs': target, 'measured': measured}
        if measured['true_peak_dbtp'] > manifest['production_loudness']['true_peak_dbtp'] + .1:
            raise ValueError('Review copy raised true peak')
        manifest['export_sha256'] = {p.name: sha256(p) for p in folder.glob('*.mp4')}
        write(folder / 'provenance.json', manifest)
        summary.append({'label': label, 'cues': len(receipt['cues']), 'production': manifest['production_loudness'],
                        'comparison': measured, 'comparison_gain_db': gain_db})
    write(BASE / 'blind/levels.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
