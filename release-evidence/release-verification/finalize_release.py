#!/usr/bin/env python3
"""Write the outer release index after the immutable skill ZIP is verified."""
from pathlib import Path
import hashlib, json, shutil

root = Path(__file__).resolve().parents[1]
base = root / 'complete-library'
skill = root / 'skill/imessage-motion-recreation'
drive = json.loads((base / 'drive-config.json').read_text())
release = json.loads((base / 'skill-v3-drive.json').read_text())
manifest = json.loads((skill / 'library/manifest.json').read_text())
audit = json.loads((base / 'registry.audit.json').read_text())
assert release['verified'] and release['full_download_sha256_verified']
assert hashlib.file_digest((root / release['file_name']).open('rb'), 'sha256').hexdigest() == release['sha256']

bootstrap = {
    'schema_version': 1,
    'title': 'iMessage Motion — Complete Private Library',
    'account_email': drive['account_email'],
    'root_folder': drive['root'],
    'skill_release': release,
    'start_here': 'Download and extract the skill ZIP; read SKILL.md and open library/index.html. Retrieve full private example packs through library/materialize.py and the authorized Drive tools.',
    'library_manifest': manifest,
    'verification_summary': audit,
    'publication_scope': 'Owner-private. No new public source/font publication was authorized. Existing public visual galleries are unchanged.',
}
(base / 'library-index.json').write_text(json.dumps(bootstrap, indent=2) + '\n')
readme = f'''# iMessage Motion — Complete Private Library

This folder belongs to the selected Personal account: {drive['account_email']}.

## Start here

1. Download [the complete v3 skill ZIP]({release['drive_url']}). Extract the ZIP.
2. Read `imessage-motion-recreation/SKILL.md`. Open `library/index.html` for example previews, full renderer source, and private project pointers. The films need a network connection in this compact viewer; offline copies are in the complete project packs.
3. For a new company, begin with `library/RESEARCH-FIRST.md` and its company-profile schema. Research the product and real user workflow, choose suitable measured motions and components, then build, synchronize UI sounds, and compare actual rendered frames.
4. To retrieve a complete example, use `library/materialize.py list` and `plan --archive <archive-id>`. An authorized agent fetches the listed private Drive parts, then `assemble` verifies their hashes and safely extracts the complete project. See `library/README.md` for exact commands. These binary parts are pieces of a ZIP; they must be assembled in order rather than opened separately.

The compact skill ZIP is {release['bytes']:,} bytes. SHA256: `{release['sha256']}`.

## What is included

- All six accepted measured scenes, their declared image/font assets, source clips, retained authoring programs, analysis and capture evidence.
- Genuine shared Remotion, GSAP, Motion Canvas, HTML/SVG and Pillow renderers, plus five explicit per-example run entrypoints. These are the actual authored implementations; they are not five independently rewritten standalone applications per film.
- Thirty finished reference-audio videos and thirty silent picture masters; the original frozen delivery is also preserved byte-for-byte.
- Complete UI audio source, cue data, mix reports, stock downloads/license pages, generated inputs and portable rebuild/mux helpers. Reference-audio versions contain the original source audio; UI-audio versions use the documented sourced/generated effects and music. The source and license records distinguish them.
- Pinned font inputs and Linux fallbacks, fixtures, later director/review source and reproduction instructions. Fonts retain their original license conditions; this is a private archive, not a new distribution license.
- Fourteen source motion studies, visual comparisons, nine editable neutral components, nine motion starters, full source viewer, research and direction workflow, and checksum-based retrieval tools. These are the actual counted resources, not a claim of seventy completed effects.

Figma is an unvalidated prototype, not a completed sixth renderer. Historical authoring programs may need superseded measurement inputs; the supported cold-build route uses the accepted scene with the shared adapters. Install pinned dependencies and recreate caches rather than treating installed third-party packages as authored source.

## Verification and index

All twelve large archives / seventy-eight parts (1,835,791,196 bytes) passed owner-private permission, size and full authenticated-download SHA256 checks. `library-index.json` contains their observed Drive IDs/URLs and exact hashes, plus this skill release. The packaged skill indexes all 14,161 archive entries and verifies 4,632 runtime asset paths.

Five cold-rendered sample frames match the corresponding accepted frames byte-for-byte; the audio cold build reproduces all seven accepted test outputs; twenty-two font mappings and forty-two toolkit/retrieval contracts pass. This does not claim a new full render of all thirty films or interactive browser QA of the private viewer. Full verification reports are included in the skill.

Library folder: {drive['root']['url']}

The existing public visual gallery remains https://message-motion-studio.orchidhq.chatgpt.site . Automatic approval review rejected making the new full source/font library public. This complete library remains private to the selected Personal Drive account; file sharing has not been expanded.
'''
(base / 'START-HERE.md').write_text(readme)

# Keep legacy installed-only helpers; the full source inventory also preserves them.
installed = Path('/workspace/.agents/skills/imessage-motion-recreation')
shutil.copytree(skill, installed, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
checks = {str(p.relative_to(installed)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted(installed.rglob('*')) if p.is_file() and p.name != 'checksums.json'
          and '__pycache__' not in p.parts and not p.name.endswith(('.tmp', '.pyc'))}
(installed / 'checksums.json').write_text(json.dumps(checks, indent=2) + '\n')
for p in skill.rglob('*'):
    if p.is_file() and p.name != 'checksums.json' and '__pycache__' not in p.parts and not p.name.endswith('.pyc'):
        assert p.read_bytes() == (installed / p.relative_to(skill)).read_bytes()
for name, digest in checks.items():
    assert hashlib.sha256((installed / name).read_bytes()).hexdigest() == digest
summary = {
    'immutable_skill_zip_sha256': release['sha256'],
    'skill_readback_verified': True,
    'installed_skill_version': json.loads((installed / 'version.json').read_text()),
    'installed_files_checked': len(checks),
    'source_and_installed_match': True,
    'bootstrap_files': {name: {'bytes': (base/name).stat().st_size, 'sha256': hashlib.sha256((base/name).read_bytes()).hexdigest()} for name in ['START-HERE.md', 'library-index.json']},
}
(base / 'release-local.audit.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
