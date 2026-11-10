#!/usr/bin/env python3
"""Integrate accepted UI audio metadata and an auditable source-only skill."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
MAIN = Path('/workspace/sites/message-motion')
MEDIA = Path('/workspace/sites/message-motion-originals')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(data)
    os.replace(tmp, path)

def js(data):
    return (json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode()

def metadata():
    path = MAIN / 'dist/sound-data.json'
    films = json.loads(path.read_text())
    refs = {r['id']: r for r in json.loads((ROOT/'verification/reference-levels.json').read_text())}
    descriptions = {
        '01-photonhq': 'One visible button press. The moving titles stay quiet.',
        '02-danieltian': 'Individual key sounds, the real typing pause, sends and replies.',
        '03-photon-mini': 'Typing, selection, cart feedback and message movement.',
        '04-poke': 'Typed input, button feedback, sends and incoming messages.',
        '05-linq': 'Keystrokes, app controls, amount changes and message sends.',
        '06-gallery': 'Sends and arrivals. The empty composer has no typing sounds.',
    }
    public = {'focus': 'UI details first; optional quiet music', 'reference_film_samples_reused': False,
              'sources': [{'author': 'Kenney', 'license': 'CC0-1.0', 'url': 'https://kenney.nl/assets/interface-sounds'},
                          {'author': 'unicae games', 'license': 'CC0-1.0', 'url': 'https://opengameart.org/content/keyboard-soundpack-1-typing-and-single-keystrokes'}],
              'custom_effects': 'Deterministic procedural synthesis for message movement and panel transitions',
              'music': 'Optional original text-prompted instrumental beds; ElevenLabs Music v2.5 through Fal, one job per film, no reference-waveform conditioning',
              'audition': 'UI-only previews use a labelled whole-stem boost; downloaded production effects retain their intended mix gain',
              'browser_qa': 'Unavailable: browser startup failed before page access; code, signal, packet and HTTP checks are separate evidence',
              'films': []}
    for f in films:
        report = json.loads((ROOT/'ui-mixes'/f['id']/'report.json').read_text())
        assert report['status'] == 'pass' and report['validation']['status'] == 'pass'
        info = report['exports']['full_mix.m4a']['file']
        ref_i = refs[f['id']]['integrated_lufs']
        new_i = info['loudness']['integrated_lufs']
        target = min(ref_i, new_i)
        f.update(description=descriptions[f['id']],
                 audio_status=f"{report['rendered_event_count']} frame-aligned UI sounds. CC0 library effects and custom synthesis; no samples from the reference film.",
                 reference_gain=10**((target-ref_i)/20), recreated_gain=10**((target-new_i)/20),
                 reference_lufs=ref_i, recreated_lufs=new_i, comparison_target_lufs=target,
                 source_samples_reused=False, reference_samples_reused=False, library_samples_used=True,
                 ui_gain=1, ui_event_count=report['rendered_event_count'])
        public['films'].append({'id': f['id'], 'visual_events': report['canonical_event_count'],
                                'audible_events': report['rendered_event_count'],
                                'silent_controls': report['skipped_event_count'],
                                'event_counts': report['kind_counts'],
                                'ui_report_sha256': sha((ROOT/'ui-mixes'/f['id']/'report.json').read_bytes()),
                                'production_code_sha256': report['code_sha256'],
                                'background_mix_lufs': new_i,
                                'ui_only_boost_db': report['ui_preview']['whole_stem_boost_db']})
    write(path, js(films))
    write(MAIN/'dist/audio-new/provenance.json', js(public))
    html = MAIN/'dist/sound.html'
    text = html.read_text().replace('aria-label="Original synthesized sound effects stem"', 'aria-label="Downloaded and custom UI sound effects stem"')
    text = text.replace('Both soundtrack modes use the same independent picture recreation. Rene keeps the graphic sequences and skips the live-action interval in both modes.', 'All three sound modes use the same independent picture recreation. Rene keeps the graphic sequences and skips the live-action interval in every mode.')
    write(html, text.encode())
    return public

def skill(public):
    folder = PROJECT/'skill/imessage-motion-recreation'
    installed = Path('/workspace/.agents/skills/imessage-motion-recreation')
    doc = '''# UI sound recreation: details before music

Use this workflow when the visible interface needs convincing keystrokes, taps, sends, arrivals and control feedback. Music is secondary. Start with a UI-only preview and retain it as the primary review mode.

1. Inventory visible actions at native frames on the accepted picture. Give each film one cue owner when multi-agent work is authorized. Read the actual video/scene, including transition states. Distinguish source frames from rendered frames and preserve any omitted-source time map.
2. Emit keys only for visible human composer changes. Keep actual pauses. Do not assign keys to titles, AI replies, caret blinks or camera-carried old text. A send that clears the composer is not backspace. If several characters first appear together, emit one key at that observed frame and record the character count; do not fabricate unseen timing. Treat a whole selected-phrase deletion as one observed action.
3. Prefer licensed, provenance-pinned effects where suitable. This case used Kenney Interface Sounds and unicae games Keyboard Soundpack #1, both CC0. The latter author describes physical keyboard recordings. Kenney's collection is a library of UI effects; do not invent its production origin or claim proprietary Apple sound equivalence. Preserve source page, license text, original/prepared hashes and download route. Do not distribute cookies, signed response URLs or authentication material.
4. Extract single keys rather than typing loops. Decode to 48 kHz stereo, trim cleanly, remove DC/declick boundaries and leave headroom. Preserve and diagnose failed candidates before correcting them. Use stable seeded variation, restrained levels and no constant keyboard bed.
5. Map each semantic action explicitly to a licensed asset or a declared custom sound. Generate short movement/transition sounds procedurally where needed. The renderer uses dominant early-attack peak alignment for keys/clicks and onset alignment for movement sounds. Record actual sample offsets using rational native cadence. Controls merely appearing can stay silent.
6. Align to the picture the viewer receives. Poke's source restaurant selection appears at633, while the accepted GSAP picture shows645; the new sound follows645. Preserve the12-frame visual discrepancy instead of claiming that source and recreation are identical.
7. Render the UI stem first, without a loudness target that raises sparse effects. Review an explicitly labelled boosted UI-only audition separately from production gain. Only then add an optional quiet music bed. Current render_ui.py --no-music reads no music file and writes into a separate no-music subdirectory. It does not require AI generation. Keep previously accepted exports immutable.
8. Validate exact frame/sample span, finite PCM, headroom, boundary behavior, non-clipping codec output and provenance. AAC can overshoot safe PCM: one earlier112kbps encode reached+0.80dBTP. Investigate bitrate/codec gain, measure the actual encoded copy and retain correction evidence. Do not normalize UI-only stems to a full-program LUFS target.
9. Copy the accepted video stream and newly encoded audio into MP4; map streams explicitly so source-film audio cannot leak into a new mix. Prove video and AAC packet hashes unchanged by muxing. Preserve all original master videos and immutable deliveries.
10. Offer UI-only, quiet-music and reference modes over the same picture. Say which mode contains the supplied soundtrack. Match comparison loudness without raising peaks or erasing manual volume/mute state. Keep production stems, download links, source licenses and a reusable sound kit accessible.

## Reproduction layout

The bundled audio-recreation directory contains source code, canonical event schedules, original production-code snapshots, safe license/provenance manifests and validation reports. It intentionally excludes audio/video/font binaries. Download the separately published UI sound kit and merge its prepared library and synthesis bank into the same audio-recreation layout, or use library_bank.py fetch/prepare with the pinned source licenses and hashes. Python requires NumPy/SciPy; FFmpeg/ffprobe must be installed. Canonical scenes and pinned music inputs belong beside this template in the host recreation project.

Run python audio-recreation/scripts/render_ui.py --self-test, inspect --plan, then use --id ID --no-music for a UI-only build. The accepted six reports and their render_ui.source.py.txt snapshots describe the actual production version; the current CLI additionally supports no-music without overwriting them. Music-generating calls are optional and stochastic. Pin downloaded generated assets for repeatable mixes; never claim that rerunning an AI prompt reproduces identical audio.

## Evidence and limits

The case contains185 visual events:183 rendered sounds and two intentionally silent control appearances. Source01 has one visible click, source02 preserves its typing pause, and Rene has no typing. Frame/sample and signal checks do not prove perceptual equivalence. Browser startup was unavailable in this session, so no interactive playback or human audition is claimed. Model descriptions and their conflicting tempo guesses are retained as model evidence, not listening certification. Never claim100% sonic identity from waveform error, renderer parity or successful export.

See execution-steps.md for the chronological root log and library/steps.md for acquisition/preparation corrections. Every retry must identify the observed failure, the likely cause, the changed variable and the evidence resolving it. Keep old successful artifacts rather than regenerating them to hide earlier decisions.
'''
    skill_md = (folder/'SKILL.md').read_text()
    marker = '\n## 8. Recreate UI sound, then add optional music\n'
    if marker not in skill_md:
        skill_md += marker + '\nFollow [the UI audio workflow](references/ui-audio-workflow.md). Visible actions determine effects; music does not determine keystrokes. Deliver a UI-only comparison, licensed sample provenance, deterministic custom accents and separate production stems.\n'
    additions = {'SKILL.md': skill_md.encode(), 'references/ui-audio-workflow.md': doc.encode(),
                 'references/ui-audio/execution-steps.md': (ROOT/'steps.md').read_bytes(),
                 'references/ui-audio/public-provenance.json': js(public)}
    for base, patterns in [(ROOT/'scripts', ['library_bank.py', 'normalize_ui_cues.py', 'render_ui.py', 'render_mix.py', 'package_ui_previews.py']), (ROOT/'synthesis', ['*.py', '*.md']),
                           (ROOT/'library', ['manifest.json', 'LICENSES.md', 'steps.md', 'validation.json', 'final-audit.json']),
                           (ROOT/'library/licenses', ['*']), (ROOT/'ui-cues', ['canonical-*.json']),
                           (ROOT/'ai', ['music-requests.json', 'generated-job-registry.json'])]:
        for pattern in patterns:
            for path in sorted(base.glob(pattern)):
                if path.is_file():
                    additions['references/ui-audio/audio-recreation/'+str(path.relative_to(ROOT))] = path.read_bytes()
    for path in sorted((ROOT/'ui-mixes').glob('*/*')):
        if path.name in ['report.json','final-audit.json','schedule.snapshot.json','render_ui.source.py.txt','README.md','renderer-api-compatibility.json']:
            additions['references/ui-audio/audio-recreation/'+str(path.relative_to(ROOT))] = path.read_bytes()
    for path in sorted((ROOT/'mixes').glob('*/render_mix.source.py.txt')):
        additions['references/ui-audio/audio-recreation/'+str(path.relative_to(ROOT))] = path.read_bytes()
    for name in ['ui-preview-packages.json','ui-sound-kit.json','reference-levels.json']:
        additions['references/ui-audio/audio-recreation/verification/'+name] = (ROOT/'verification'/name).read_bytes()
    # Merge the prior portable source package. Do not add bulky working caches.
    prefix = 'imessage-motion-recreation/'
    with zipfile.ZipFile(PROJECT/'imessage-motion-recreation-skill-public-update.zip') as old:
        payload = {n:old.read(n) for n in old.namelist() if not n.endswith('/') and n != prefix+'checksums.json'}
    for name, data in additions.items():
        payload[prefix+name] = data
        for dest in [folder, installed]:
            write(dest/name, data)
    checks = {name[len(prefix):]:sha(data) for name,data in sorted(payload.items())}
    payload[prefix+'checksums.json'] = js(checks)
    forbidden = ('.mp4','.mov','.wav','.mp3','.m4a','.flac','.ogg','.woff','.woff2','.ttf','.otf')
    for name,data in payload.items():
        assert not name.lower().endswith(forbidden), name
        for secret in [b'siwc_bypass_bearer_token', b'mcp_account_id=', b'X-Amz-Signature=', b'Authorization: Bearer ey']:
            assert secret not in data, (name,secret)
    out = PROJECT/'imessage-motion-recreation-with-ui-audio-skill.zip'
    tmp = out.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in sorted(payload.items()):
            z.writestr(name,data)
    os.replace(tmp,out)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(payload)
        for rel,digest in checks.items():
            assert sha(z.read(prefix+rel)) == digest
    for dest in [folder, installed]:
        tree = {str(p.relative_to(dest)):sha(p.read_bytes()) for p in sorted(dest.rglob('*')) if p.is_file() and p.name!='checksums.json'}
        write(dest/'checksums.json', js(tree))
    write(MAIN/'dist/imessage-motion-recreation-skill.zip', out.read_bytes())
    report = {'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),
              'files':len(payload),'all_checksums_pass':True,'source_only':True,'old_archives_preserved':True}
    write(ROOT/'verification/ui-skill-package.json', js(report))
    print(json.dumps(report))

if __name__ == '__main__':
    public = metadata()
    skill(public)
