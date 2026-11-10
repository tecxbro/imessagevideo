#!/usr/bin/env python3
"""CC0 UI-library acquisition/preparation and real single-key playback API.

No reference-film audio or procedural synthesis is used here. Kenney effects
are licensed library UI sounds (their acoustic/synthetic origin is unstated).
Unicae Single Keys are actual keyboard recordings according to the author.
Selection uses source names and signal measurements, not invented listening.

  python audio-recreation/scripts/library_bank.py fetch
  python audio-recreation/scripts/library_bank.py prepare
  python audio-recreation/scripts/library_bank.py list --tag keyboard
  python audio-recreation/scripts/library_bank.py render key_001 /tmp/key.wav --gain-db -12 --pitch 1.02
  python audio-recreation/scripts/library_bank.py validate

Import with importlib.util, then render_asset(id, pitch=1, gain_db=-12, pan=0).
The result is float32 [samples,2] at48kHz. Pitch is varispeed: it also changes
duration. Prepared files peak at−6dBFS; gain is applied after pitch/pan peak
alignment. No random process is introduced. write_wav exports PCM24.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import urllib.request
import wave
import zipfile

os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
import numpy as np
import scipy
from scipy import signal

ROOT = Path(__file__).resolve().parents[1] / 'library'
SR = SAMPLE_RATE = 48000
PEAK = 10 ** (-6 / 20)
UA = 'Mozilla/5.0'
KENNEY_PAGE = 'https://kenney.nl/assets/interface-sounds'
KENNEY_API = 'https://kenney.nl/download-link/6173736574732f696e746572666163652d736f756e6473'
KEYBOARD_PAGE = 'https://opengameart.org/content/keyboard-soundpack-1-typing-and-single-keystrokes'
KEYBOARD_ZIP = 'https://opengameart.org/sites/default/files/unicae_games_keyboard_soundpack_1_0.zip'
ARCHIVES = {'kenney': 'kenney-interface-sounds.zip', 'keyboard': 'unicae_games_keyboard_soundpack_1_0.zip'}
KENNEY_SELECTION = {
    'click_001': ['click', 'primary'], 'click_002': ['click'], 'click_003': ['click', 'primary'],
    'click_004': ['click'], 'click_005': ['click'],
    'tick_001': ['tick', 'primary'], 'tick_002': ['tick', 'primary'], 'tick_004': ['tick'],
    'select_001': ['selection', 'primary'], 'select_002': ['selection', 'primary'], 'select_005': ['selection'],
    'switch_001': ['switch', 'multi_transient_candidate'], 'switch_004': ['switch', 'multi_transient_candidate'],
    'toggle_001': ['toggle'], 'toggle_004': ['toggle'],
    'drop_001': ['drop', 'pop_candidate'], 'drop_002': ['drop', 'pop_candidate'],
    'pluck_001': ['pluck', 'pop_candidate'], 'scroll_001': ['scroll', 'swipe_candidate'],
    'open_001': ['open', 'card_candidate'], 'close_001': ['close', 'card_candidate'],
    'maximize_001': ['maximize', 'swipe_candidate'], 'minimize_001': ['minimize', 'swipe_candidate'],
    'glass_001': ['glass', 'confirmation_candidate'], 'confirmation_001': ['confirmation_candidate'],
}
KEY_SELECTION = [1, 3, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch_file(url: str, target: Path, max_bytes: int, referer: str | None = None) -> dict:
    headers = {'User-Agent': UA}
    if referer:
        headers['Referer'] = referer
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=headers)
    temporary = target.with_suffix(target.suffix + '.part')
    total = 0
    try:
        with urllib.request.urlopen(request, timeout=60) as response, temporary.open('wb') as handle:
            response_headers = dict(response.headers)
            final_url = response.url
            while block := response.read(65536):
                total += len(block)
                if total > max_bytes:
                    raise ValueError(f'Download exceeded the bounded size: {url}')
                handle.write(block)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return {'requested_url': url, 'resolved_url': final_url, 'bytes': total,
            'sha256': sha(target), 'response_headers': response_headers}


def fetch() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    collection = {'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'paid_calls': 0,
                  'accounts_created': False, 'source_samples_from_reference_films': False, 'downloads': {}}
    for name, url in [('kenney-response.html', KENNEY_PAGE), ('keyboard-source-page.html', KEYBOARD_PAGE)]:
        collection['downloads'][name] = fetch_file(url, ROOT / name, 1024 * 1024)
    link = fetch_file(KENNEY_API, ROOT / 'kenney-download-link.json', 16384, KENNEY_PAGE)
    collection['downloads']['kenney-download-link.json'] = link
    url = json.loads((ROOT / 'kenney-download-link.json').read_text())['url']
    if not url.startswith('https://kenney.nl/download/'):
        raise ValueError('Kenney public API returned an unexpected download origin')
    collection['downloads'][ARCHIVES['kenney']] = fetch_file(url, ROOT / 'archives' / ARCHIVES['kenney'], 8 * 1024 * 1024, KENNEY_PAGE)
    collection['downloads'][ARCHIVES['keyboard']] = fetch_file(KEYBOARD_ZIP, ROOT / 'archives' / ARCHIVES['keyboard'], 16 * 1024 * 1024, KEYBOARD_PAGE)
    (ROOT / 'download-collection.json').write_text(json.dumps(collection, indent=2) + '\n')


def safe_extract(source: str) -> dict:
    archive = ROOT / 'archives' / ARCHIVES[source]
    destination = ROOT / 'sources' / source
    inventory = []
    with zipfile.ZipFile(archive) as package:
        entries = package.infolist()
        if len(entries) > 250 or sum(x.file_size for x in entries) > 32 * 1024 * 1024:
            raise ValueError('Archive exceeds expected entry/expanded-size limits')
        for info in entries:
            path = PurePosixPath(info.filename)
            mode = stat.S_IFMT(info.external_attr >> 16)
            if path.is_absolute() or '..' in path.parts or '\\' in info.filename or mode not in [0, stat.S_IFREG, stat.S_IFDIR]:
                raise ValueError(f'Unsafe or nonregular ZIP member: {info.filename}')
            if info.file_size > 16 * 1024 * 1024:
                raise ValueError('Unexpected large archive member')
            selected = (not info.is_dir() and
                        ((source == 'kenney' and (info.filename.startswith('Audio/') or info.filename == 'License.txt')) or
                         (source == 'keyboard' and (info.filename.startswith('Single Keys/') or info.filename == 'readme.txt'))))
            item = {'member': info.filename, 'bytes': info.file_size, 'extracted': selected}
            if selected:
                target = destination.joinpath(*path.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                contents = package.read(info)
                if len(contents) != info.file_size:
                    raise ValueError('ZIP member size mismatch')
                target.write_bytes(contents)
                item['sha256'] = hashlib.sha256(contents).hexdigest()
            inventory.append(item)
    return {'archive': str(archive.relative_to(ROOT)), 'sha256': sha(archive), 'bytes': archive.stat().st_size,
            'inventory': inventory, 'typing_loops_extracted': False if source == 'keyboard' else None,
            'expanded_files_bytes': sum(i['bytes'] for i in inventory if i['extracted'])}


def decode(path: Path) -> tuple[np.ndarray, dict]:
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
                            'stream=codec_name,sample_rate,channels,bits_per_raw_sample', '-of', 'json', str(path)],
                           check=True, capture_output=True, text=True)
    metadata = json.loads(probe.stdout)['streams'][0]
    result = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-filter_threads', '1', '-i', str(path),
                             '-map', '0:a:0', '-ar', str(SR), '-ac', '2', '-f', 'f32le', '-c:a', 'pcm_f32le',
                             '-threads', '1', 'pipe:1'], check=True, capture_output=True)
    samples = np.frombuffer(result.stdout, dtype='<f4').reshape(-1, 2).astype(np.float64)
    if not len(samples) or not np.isfinite(samples).all():
        raise ValueError(f'Invalid decoded sound: {path}')
    return samples, metadata


def finish(x: np.ndarray) -> np.ndarray:
    fade = np.ones(len(x))
    attack = max(2, min(round(.00025 * SR), len(x) // 5))
    release = max(2, min(round(.012 * SR), len(x) // 2))
    fade[:attack] = np.sin(np.linspace(0, np.pi / 2, attack)) ** 2
    fade[-release:] = np.cos(np.linspace(0, np.pi / 2, release)) ** 2
    x = x * fade[:, None]
    x -= fade[:, None] * (np.sum(x, axis=0) / np.sum(fade))
    x[[0, -1]] = 0
    return x


def prepare_samples(x: np.ndarray) -> tuple[np.ndarray, dict]:
    envelope = np.max(np.abs(x), axis=1)
    peak = float(envelope.max())
    if peak < 1e-8:
        raise ValueError('Source sound is effectively silent')
    active = np.flatnonzero(envelope > peak * 10 ** (-50 / 20))
    first = max(0, int(active[0]) - round(.002 * SR))
    end = min(len(x), int(active[-1]) + 1 + round(.012 * SR))
    if end - first < 16:
        raise ValueError('Source sound is unexpectedly short')
    trimmed = finish(x[first:end].copy())
    pre_peak = float(np.max(np.abs(trimmed)))
    trimmed *= PEAK / pre_peak
    return trimmed.astype(np.float32), {'decoded_source_samples': len(x), 'source_peak': peak,
            'trim_start_sample_48k': first, 'trim_end_sample_48k': end,
            'onset_offset_samples_48k': int(active[0]) - first,
            'threshold_relative_db': -50, 'retained_pre_roll_ms': 2, 'retained_post_roll_ms': 12,
            'declick_attack_ms': .25, 'maximum_release_ms': 12, 'release_limit': 'half of clip length', 'dc_removed': True,
            'normalization_gain_db': 20 * math.log10(PEAK / pre_peak), 'peak_target_dbfs': -6}


def write_wav(path: str | Path, samples: np.ndarray) -> Path:
    path = Path(path)
    if samples.ndim != 2 or samples.shape[1] != 2 or not np.isfinite(samples).all() or np.max(np.abs(samples)) >= 1:
        raise ValueError('Expected finite, nonclipped stereo samples')
    path.parent.mkdir(parents=True, exist_ok=True)
    packed = np.rint(np.asarray(samples, dtype=np.float64) * (2 ** 23 - 1)).astype(np.int32).reshape(-1)
    raw = np.column_stack([(packed >> shift) & 255 for shift in [0, 8, 16]]).astype(np.uint8).tobytes()
    with wave.open(str(path), 'wb') as handle:
        handle.setnchannels(2); handle.setsampwidth(3); handle.setframerate(SR); handle.writeframes(raw)
    return path


@lru_cache(maxsize=64)
def read_wav(path: str) -> np.ndarray:
    with wave.open(path, 'rb') as handle:
        if (handle.getnchannels(), handle.getframerate(), handle.getsampwidth()) != (2, SR, 3):
            raise ValueError('Prepared bank format must be stereo48kPCM24')
        raw = np.frombuffer(handle.readframes(handle.getnframes()), dtype=np.uint8).reshape(-1, 3)
    values = raw[:, 0].astype(np.int32) | raw[:, 1].astype(np.int32) << 8 | raw[:, 2].astype(np.int32) << 16
    values = np.where(values >= 2 ** 23, values - 2 ** 24, values)
    return values.reshape(-1, 2).astype(np.float64) / (2 ** 23 - 1)


def attack_peak_sample(x: np.ndarray, window_s: float = .08) -> int:
    """Dominant peak in the first80ms of significant activity.

    This is a repeatable alignment proxy, not a claim about which physical
    key action produced a transient. It avoids late release/maximize peaks.
    """
    envelope = np.max(np.abs(x), axis=1)
    active = np.flatnonzero(envelope > float(envelope.max()) * .05)
    if not len(active):
        return 0
    first = int(active[0]); end = min(len(x), first + max(1, round(window_s * SR)))
    return first + int(np.argmax(envelope[first:end]))


def statistics(x: np.ndarray) -> dict:
    peak = float(np.max(np.abs(x)))
    mono = np.mean(x, axis=1)
    spectrum = np.abs(np.fft.rfft(mono * np.hanning(len(mono))))
    frequency = np.fft.rfftfreq(len(mono), 1 / SR)
    return {'samples': len(x), 'duration_s': len(x) / SR, 'sample_rate': SR, 'channels': 2,
            'peak': peak, 'peak_dbfs': 20 * math.log10(peak) if peak else None,
            'rms': float(np.sqrt(np.mean(x ** 2))), 'dc': np.mean(x, axis=0).tolist(),
            'peak_time_ms': int(np.argmax(np.max(np.abs(x), axis=1))) / SR * 1000,
            'attack_peak_sample': attack_peak_sample(x), 'attack_peak_window_s': .08,
            'spectral_centroid_hz': float(np.sum(frequency * spectrum) / max(np.sum(spectrum), 1e-15)),
            'finite': bool(np.isfinite(x).all()), 'clipped_samples': int(np.count_nonzero(np.abs(x) >= 1)),
            'endpoints_zero': bool(np.all(x[[0, -1]] == 0)), 'last_half_ms_peak': float(np.max(np.abs(x[-24:])))}


def manifest() -> dict:
    return json.loads((ROOT / 'manifest.json').read_text())


def render_asset(asset_id: str, *, pitch: float = 1., gain_db: float = -12., pan: float = 0.) -> np.ndarray:
    """Render a licensed asset at48k stereo. Gain follows−6dBFS peak alignment.

    pitch0.5..2 is bandlimited varispeed, not time stretching. pan−1..1.
    IDs map to exact source files; no typing bed or reference film is loaded.
    """
    if not all(math.isfinite(v) for v in [pitch, gain_db, pan]) or not .5 <= pitch <= 2 or not -1 <= pan <= 1:
        raise ValueError('Finite pitch0.5..2, pan−1..1 and gain_db required')
    entries = {a['id']: a for a in manifest()['assets']}
    if asset_id not in entries:
        raise ValueError(f'Unknown library asset: {asset_id}')
    x = read_wav(str(ROOT / entries[asset_id]['prepared_file'])).copy()
    if pitch != 1:
        ratio = Fraction(pitch).limit_denominator(1000)
        x = signal.resample_poly(x, ratio.denominator, ratio.numerator, axis=0)
        x = finish(x)
    angle = (pan + 1) * np.pi / 4
    gains = np.array([np.cos(angle), np.sin(angle)])
    gains[np.abs(gains) < 1e-15] = 0
    x *= gains
    peak = float(np.max(np.abs(x)))
    x *= PEAK * 10 ** (gain_db / 20) / max(peak, 1e-15)
    x[[0, -1]] = 0
    if not np.isfinite(x).all() or np.max(np.abs(x)) >= 1:
        raise ValueError('Requested gain would clip; lower gain_db')
    return x.astype(np.float32)


def prepare() -> dict:
    ROOT.mkdir(parents=True, exist_ok=True)
    archives = {source: safe_extract(source) for source in ARCHIVES}
    kenney_license = ROOT / 'sources/kenney/License.txt'
    keyboard_readme = ROOT / 'sources/keyboard/readme.txt'
    keyboard_page = ROOT / 'keyboard-source-page.html'
    if 'CC0' not in kenney_license.read_text() or 'CC0' not in keyboard_page.read_text():
        raise ValueError('Required source-specific CC0 evidence is missing')
    sources = {
      'kenney': {'author': 'Kenney', 'title': 'Interface Sounds1.0', 'page_url': KENNEY_PAGE,
                 'download_flow': KENNEY_API, 'license': 'CC0-1.0', 'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/',
                 'license_file': str(kenney_license.relative_to(ROOT)), 'license_sha256': sha(kenney_license),
                 'source_kind': 'licensed_library_ui_effect', 'production_origin': 'Not specified; do not claim an acoustic recording',
                 'source_page': 'kenney-response.html', 'source_page_sha256': sha(ROOT / 'kenney-response.html'), **archives['kenney']},
      'keyboard': {'author': 'unicaegames', 'title': 'Keyboard Soundpack1: Typing and Single Keystrokes',
                   'page_url': KEYBOARD_PAGE, 'download_url': KEYBOARD_ZIP, 'license': 'CC0-1.0',
                   'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/',
                   'license_basis': 'Author listing on OpenGameArt explicitly labels CC0; included readme says free to use however you like',
                   'readme_file': str(keyboard_readme.relative_to(ROOT)), 'readme_sha256': sha(keyboard_readme),
                   'source_page': 'keyboard-source-page.html', 'source_page_sha256': sha(keyboard_page),
                   'source_kind': 'licensed_real_single_key_recording',
                   'recording_provenance_author_claim': {'keyboard': 'Cherry KC1000', 'microphone': 'Shure SM7B', 'postprocess': 'Izotope Neutron2'},
                   'named_character_identity': 'Not provided; numbered variants are not assigned to physical key labels', **archives['keyboard']}}
    candidates = [('kenney_' + name, 'kenney', ROOT / 'sources/kenney/Audio' / (name + '.ogg'), tags)
                  for name, tags in KENNEY_SELECTION.items()]
    candidates += [(f'key_{number:03}', 'keyboard', ROOT / 'sources/keyboard/Single Keys' / f'keypress-{number:03}.wav',
                    ['keyboard', 'single_key', 'real_recording', 'primary']) for number in KEY_SELECTION]
    assets = []
    sequence = [np.zeros((round(.2 * SR), 2), dtype=np.float32)]
    position = .2
    for asset_id, source, path, tags in candidates:
        x, stream = decode(path)
        prepared, processing = prepare_samples(x)
        file = write_wav(ROOT / 'prepared' / (asset_id + '.wav'), prepared)
        assets.append({'id': asset_id, 'source': source, 'source_kind': sources[source]['source_kind'],
                       'original_file': str(path.relative_to(ROOT)), 'original_sha256': sha(path), 'original_stream': stream,
                       'prepared_file': str(file.relative_to(ROOT)), 'prepared_sha256': sha(file),
                       'license': 'CC0-1.0', 'tags': tags, 'processing': processing,
                       'statistics': statistics(prepared.astype(np.float64)), 'audition_start_s': position,
                       'selection_basis': 'Source filename/category and signal validation; no listening performed',
                       'semantic_limit': 'Candidate labels are routing suggestions, not certification of a specific proprietary UI sound'})
        sequence.extend([prepared * .5, np.zeros((round(.2 * SR), 2), dtype=np.float32)])
        position += len(prepared) / SR + .2
    collection = {'format_version': 1, 'sample_rate': SR, 'channels': 2, 'encoding': 'PCM24 WAV',
                  'peak_target_dbfs': -6, 'human_listening_performed': False, 'model_listening_performed': False,
                  'reference_film_samples_used': False, 'procedural_samples_included': False,
                  'typing_beds_used': False, 'sources': sources, 'assets': assets,
                  'code_sha256': sha(Path(__file__)),
                  'toolchain': {'numpy': np.__version__, 'scipy': scipy.__version__,
                                'ffmpeg': subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True).stdout.splitlines()[0]},
                  'fallback_guidance': 'Existing separate synthesis bank can supply message whooshes/custom textures. Do not present its generated effects as recordings.',
                  'audition': {'file': 'audition.mp3', 'order': [a['id'] for a in assets],
                               'duration_s': position, 'gain_db_relative_to_prepared': -6.0206, 'listened': False}}
    raw = np.concatenate(sequence).astype('<f4').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-threads', '1', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'pipe:0',
                    '-map_metadata', '-1', '-c:a', 'libmp3lame', '-q:a', '2', '-threads', '1', str(ROOT / 'audition.mp3')],
                   input=raw, check=True, capture_output=True)
    collection['audition']['sha256'] = sha(ROOT / 'audition.mp3')
    (ROOT / 'manifest.json').write_text(json.dumps(collection, indent=2) + '\n')
    return collection


def validate() -> dict:
    data = manifest(); reports = []
    for source in data['sources'].values():
        if sha(ROOT / source['archive']) != source['sha256']:
            raise ValueError('Source archive provenance hash mismatch')
    for a in data['assets']:
        if sha(ROOT / a['original_file']) != a['original_sha256']:
            raise ValueError('Extracted original source hash mismatch: ' + a['id'])
        file = ROOT / a['prepared_file']
        if sha(file) != a['prepared_sha256']:
            raise ValueError('Prepared file hash mismatch: ' + a['id'])
        x = read_wav(str(file)); s = statistics(x)
        if not s['finite'] or s['clipped_samples'] or not s['endpoints_zero'] or max(abs(v) for v in s['dc']) > 1e-6:
            raise ValueError('Prepared signal check failed: ' + a['id'])
        if abs(s['peak_dbfs'] + 6) > .001 or s['last_half_ms_peak'] > .005:
            raise ValueError('Prepared headroom/tail check failed: ' + a['id'])
        for pitch, pan in [(1., -1.), (1.03, 1.), (.97, 0.)]:
            sample = render_asset(a['id'], pitch=pitch, gain_db=-12, pan=pan)
            if not np.isfinite(sample).all() or np.max(np.abs(sample)) > .126:
                raise ValueError('Rendered variation safety failed')
            if abs(pan) == 1 and np.any(sample[:, 1 if pan < 0 else 0]):
                raise ValueError('Hard-pan silence check failed')
        first = render_asset(a['id'], pitch=1.03)
        if not np.array_equal(first, render_asset(a['id'], pitch=1.03)):
            raise ValueError('Playback API is not deterministic')
        reports.append({'id': a['id'], 'prepared_sha256': a['prepared_sha256'], 'statistics': s})
    result = {'status': 'pass', 'assets': len(reports), 'checks': ['archive/source/prepared provenance', 'PCM24 48k stereo',
                'finite/no clipping', '−6dBFS peak headroom', 'zero endpoints/DC/clean tails',
                'deterministic bandlimited pitch/gain/pan variations', 'hard-pan silent opposite channel'], 'reports': reports}
    (ROOT / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('fetch'); sub.add_parser('prepare'); sub.add_parser('validate')
    listing = sub.add_parser('list'); listing.add_argument('--tag')
    one = sub.add_parser('render'); one.add_argument('asset_id'); one.add_argument('output', type=Path)
    one.add_argument('--pitch', type=float, default=1.); one.add_argument('--gain-db', type=float, default=-12.)
    one.add_argument('--pan', type=float, default=0.)
    args = parser.parse_args()
    if args.command == 'fetch': fetch()
    elif args.command == 'prepare':
        data = prepare(); print(json.dumps({'prepared': len(data['assets']), 'manifest': str(ROOT / 'manifest.json')}))
    elif args.command == 'validate':
        result = validate(); print(json.dumps({'status': result['status'], 'assets': result['assets']}))
    elif args.command == 'list':
        print(json.dumps([{'id': a['id'], 'tags': a['tags'], 'duration_s': a['statistics']['duration_s']}
                          for a in manifest()['assets'] if not args.tag or args.tag in a['tags']], indent=2))
    else:
        samples = render_asset(args.asset_id, pitch=args.pitch, gain_db=args.gain_db, pan=args.pan)
        write_wav(args.output, samples); print(json.dumps(statistics(samples)))


if __name__ == '__main__':
    main()
