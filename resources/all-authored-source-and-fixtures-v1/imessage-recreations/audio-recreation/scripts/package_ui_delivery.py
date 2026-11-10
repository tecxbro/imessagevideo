#!/usr/bin/env python3
"""Freeze the UI audio supplement without modifying prior video deliveries."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

PROJECT=Path(__file__).resolve().parents[2]
AUDIO=PROJECT/'audio-recreation'
MAIN=Path('/workspace/sites/message-motion')
MEDIA=Path('/workspace/sites/message-motion-originals')
def sha(data): return hashlib.sha256(data).hexdigest()
def js(data): return (json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode()
def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_bytes(data);os.replace(tmp,path)

delivery=json.loads((MAIN/'verification/ui-public-delivery.json').read_text())
assert delivery['pass'] and delivery['passed']==delivery['total']==41
publication=json.loads((MAIN/'verification/ui-publication.json').read_text())
assert all(s['deployment']['status']=='succeeded' for s in publication['sites'])
steps=AUDIO/'steps.md'
if '\n22. ' not in steps.read_text():
    atomic(steps,(steps.read_text()+'''\n22. Final unauthenticated public audit passed41/41 exact whole-file SHA256/size/container checks, covering twelve new videos, eighteen standalone audio layers, the sound kit, workflow archive and page assets. The audio Blob path passes with the observed generic M4A transport MIME. Both Sites are live as public version3; all35 controller/bridge tests, focused audio self-tests, frame/PCM/packet audits and encoded peak checks pass. Browser/audio audition remains explicitly unverified.\n23. Freeze a separate portable UI-audio supplement containing new preview videos, all42 audio exports, pinned optional music inputs, canonical cue sheets, licensed/custom sound kit contents, code, provenance and final publication evidence. Include a post-publication source-only skill snapshot with the full execution log. Validate ZIP CRC and every SHA before declaring the supplement ready; leave the original650MB delivery and previous archives unchanged.\n''').encode())

# Keep the published workflow's build snapshot immutable, and make a final local
# snapshot which can additionally record the successful publication itself.
skill_prefix='imessage-motion-recreation/'
with zipfile.ZipFile(PROJECT/'imessage-motion-recreation-with-ui-audio-skill.zip') as src:
    skill={n:src.read(n) for n in src.namelist() if not n.endswith('/') and n!=skill_prefix+'checksums.json'}
updates={'references/ui-audio/execution-steps.md':steps.read_bytes(),
         'references/ui-audio/publication.audit.json':js(publication),
         'references/ui-audio/public-delivery.audit.json':js(delivery)}
for name,data in updates.items():
    skill[skill_prefix+name]=data
    for folder in [PROJECT/'skill/imessage-motion-recreation',Path('/workspace/.agents/skills/imessage-motion-recreation')]: atomic(folder/name,data)
skill[skill_prefix+'checksums.json']=js({n[len(skill_prefix):]:sha(d) for n,d in sorted(skill.items())})
final_skill=PROJECT/'imessage-motion-recreation-ui-audio-final-skill.zip'
with zipfile.ZipFile(final_skill.with_suffix('.tmp'),'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
    for name,data in sorted(skill.items()): out.writestr(name,data)
os.replace(final_skill.with_suffix('.tmp'),final_skill)

payload={}
def add(path,rel=None):
    assert path.is_file(),path
    name=rel or str(path.relative_to(PROJECT))
    assert name not in payload,name
    payload[name]=path
for path in sorted((AUDIO/'ui-previews').glob('*.mp4')): add(path)
assert len(payload)==12
for path in sorted((AUDIO/'ui-mixes').glob('*/*')):
    if path.is_file() and path.suffix in ['.flac','.m4a','.json','.md','.txt']: add(path)
for ident in ['01-photonhq','02-danieltian','03-photon-mini','04-poke','05-linq','06-gallery']:
    add(AUDIO/'mixes'/ident/'music.flac')
    for name in ['music.mp3','provenance.json']: add(AUDIO/'ai'/ident/name)
for base,patterns in [(AUDIO/'scripts',['render_ui.py','render_mix.py','library_bank.py','normalize_ui_cues.py','package_ui_previews.py']),
                      (AUDIO/'ui-cues',['canonical-*.json']),
                      (AUDIO/'verification',['ui-preview-packages.json','ui-sound-kit.json','reference-levels.json'])]:
    for pattern in patterns:
        for path in sorted(base.glob(pattern)): add(path)
add(steps)
add(final_skill,'workflow/imessage-motion-recreation-ui-audio-final-skill.zip')
add(MAIN/'dist/audio-new/provenance.json','audio-recreation/provenance.json')
add(MAIN/'verification/ui-publication.json','verification/publication.json')
add(MAIN/'verification/ui-public-delivery.json','verification/public-delivery.json')
docs={'README.md':b'''# iMessage UI audio supplement

Listen publicly: https://message-motion-studio.orchidhq.chatgpt.site/sound.html#05-linq/ui

UI sounds are the primary study: 183 frame-aligned cues across six films.
The 12 previews preserve the accepted GSAP picture streams. `-ui.mp4` uses a
clearly labelled whole-stem listening boost; `-recreated.mp4` combines production
effects with a quiet optional music bed. Reference-film samples are not used in
these new tracks. The old full visual gallery and frozen delivery remain intact.

`audio-recreation/ui-mixes/ID/ui.flac` is the production UI master; full_mix.flac
and music.flac are the quiet-music mix and its music layer. AAC listening copies,
individual routing/gains, cue snapshots, original executed code, peak/codec
measurements and independent audits live beside them. The earlier new-music
stem and generated MP3 are pinned separately for optional exact default inputs.

The prepared library contains 37 CC0 candidates (only a subset used), including
actual single-key recordings. Eight procedural effects are provided separately.
Source pages, license texts and original/prepared hashes document provenance.
No account secrets, download cookies or signed HTTP response URLs are included.

Run `python audio-recreation/scripts/render_ui.py --self-test`, inspect --plan,
then use `--id 05-linq --no-music` for future UI-only work. Python needs NumPy
and SciPy, and FFmpeg/ffprobe must be installed. The no-music variant reads no
music file or AI service and writes into a separate no-music subdirectory.

The workflow ZIP is source-only and includes the chronological execution log
plus successful publication evidence. Verify `checksums.json` for this complete
supplement. HTTP/signal/code audits passed; interactive browser/audio audition
was unavailable because the computer-use runtime failed at startup.
'''}
# Merge the distributable kit into the same runnable audio-recreation layout.
with zipfile.ZipFile(AUDIO/'ui-sound-kit.zip') as kit:
    for name in kit.namelist():
        if name.endswith('/') or name in ['ui-sound-kit/checksums.json','ui-sound-kit/README.md']: continue
        rel='audio-recreation/'+name.removeprefix('ui-sound-kit/')
        data=kit.read(name)
        if rel in payload: assert payload[rel].read_bytes()==data,rel
        else: docs[rel]=data
checks={name:sha(path.read_bytes()) for name,path in sorted(payload.items())}
checks.update({name:sha(data) for name,data in sorted(docs.items())})
docs['checksums.json']=js(checks)
out=PROJECT/'imessage-ui-audio-delivery.zip';tmp=out.with_suffix('.tmp')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name,path in sorted(payload.items()): z.write(path,name)
    for name,data in sorted(docs.items()): z.writestr(name,data)
os.replace(tmp,out)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(checks)+1
    for name,digest in checks.items(): assert sha(z.read(name))==digest,name
with zipfile.ZipFile(final_skill) as z:
    assert z.testzip() is None
    for name,digest in json.loads(z.read(skill_prefix+'checksums.json')).items(): assert sha(z.read(skill_prefix+name))==digest
for folder in [PROJECT/'skill/imessage-motion-recreation',Path('/workspace/.agents/skills/imessage-motion-recreation')]:
    atomic(folder/'checksums.json',js({str(p.relative_to(folder)):sha(p.read_bytes()) for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='checksums.json'}))
report={'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'files':len(checks)+1,
        'crc_and_all_payload_checksums_pass':True,'source_only_final_skill':{'path':str(final_skill),'bytes':final_skill.stat().st_size,'sha256':sha(final_skill.read_bytes())},
        'published_skill_build_snapshot_unchanged':True,'original_video_delivery_unchanged':True}
atomic(AUDIO/'verification/ui-delivery-package.json',js(report));print(json.dumps(report,indent=2))
