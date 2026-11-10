"""Freeze source06 native-reviewed semantic repairs and preserve actual21 artifacts."""
from pathlib import Path
import json, hashlib, os, shutil, re, subprocess, fcntl
R = Path('/workspace/imessage-recreations')
D = R/'verification/final/06-gallery/v22'
REF = R/'references/06-gallery'
OUT = R/'outputs/06-gallery'
BASE = OUT/'final-v21/scene.json'
TARGET = OUT/'final-v22'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE) == 'dc55d9a07a4920e3aa5de3ebde4115cede4affc7549bde1548c62ef2dbed6894'
if (TARGET/'scene.json').exists():
    raise RuntimeError('Unique final-v22 already exists; never overwrite an accepted snapshot')
q = json.load(open(D/'native-release.json'))
p = json.load(open(D/'scope-exact-boundary.json'))
assert not p['changedOutsideCaptureUnion']
assert p['changedFrames'] == 32
assert q['allChangedImprove'] and q['allControlsPixelIdentical'] and q['changedNativeCovered']
source = REF/'scene-late-review-v22.json'
assert sha(source) == q['sceneSHA256'] == p['targetSha256']
# Retain actual21G including every lossless frame before touching its writer.
backup = OUT/'iterations/final-v21-before-v22'
cache = Path(json.load(open(OUT/'gsap.mp4.render.json'))['frameDirectory'])
backup.mkdir(parents=True,exist_ok=True)
records = []
for file in [OUT/'gsap.mp4',OUT/'gsap.mp4.render.json']:
    dest = backup/file.name
    if not dest.exists():
        if file.suffix == '.mp4':
            os.link(file,dest)
        else:
            shutil.copy2(file,dest)
    assert sha(file) == sha(dest)
for n in range(1483):
    a = cache/f'{n:06d}.png'
    b = backup/'cache/gsap'/a.name
    b.parent.mkdir(parents=True,exist_ok=True)
    if not b.exists():
        os.link(a,b)
    digest = sha(a)
    assert digest == sha(b)
    records.append({'frame':n,'sha256':digest})
(backup/'preservation.json').write_text(json.dumps({'sceneSHA256':sha(BASE),'frames':records},indent=2))
s = json.load(open(source))
pool = REF/'assets/final-v22-normalized'
assets = {}
def normal(src):
    if src.startswith('data:'):
        return src
    if src.startswith(('http:','https:')):
        raise ValueError('Remote dependency')
    file = Path(src)
    if not file.is_absolute():
        file = source.parent/file
    digest = sha(file)
    name = re.sub(r'^(?:[a-f0-9]{16}-)+','',file.name)
    dest = pool/digest/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():
        shutil.copy2(file,dest)
    assert sha(dest) == digest
    assets[str(dest)] = {'original':str(file),'sha256':digest}
    return str(dest)
def walk(ns):
    for n in ns:
        if n.get('src'):
            n['src'] = normal(n['src'])
        assert not n.get('keyframes',{}).get('src')
        walk(n.get('children',[]))
walk(s['layers'])
for f in s.get('fonts',[]):
    f['src'] = normal(f['src'])
s['source']['notes'] += ' Finalv22 preserves accepted21 portraits and fixes only32 actual native states: measured Done fade, independent outgoing/incoming black title, provider word separation, mascot/letter reveal, fading CTA suffix identity and final now lifecycle. Other1451 source21 states are evaluated-markup identical. Native words/letter contours/cameras remain editable; genuine existing internal UI/photos remain rasterized where disclosed. Remaining optical/material/AA differences are not a100% identity certification.'
author = REF/'scene-final-v22-composed.json'
author.write_text(json.dumps(s,indent=2)+'\n')
subprocess.run(['python',str(R/'engines/snapshot_scene.py'),str(author),str(TARGET)],check=True)
(D/'composition.json').write_text(json.dumps({'baseSHA256':sha(BASE),'scene':str(TARGET/'scene.json'),'sceneSHA256':sha(TARGET/'scene.json'),'payloadSHA256':sha(REF/'late-review-v22-elements.json'),'nativeReviewedSHA256':q['sceneSHA256'],'source21Delta':p['exactChangedRanges'],'cumulative20Ranges':[[205,209],[613,621],[1117,1117],[1179,1189],[1257,1261],[1263,1264],[1329,1335],[1366,1366]],'normalizedAssets':len(assets),'preserved21':str(backup),'gate':'native32 pass; encoded G22 source gate pending'},indent=2))
(D/'normalized-assets.json').write_text(json.dumps(assets,indent=2))
(D/'source-gate.json').write_text(json.dumps({'status':'PENDING','reason':'Native32source pass; require encoded G22 mapped1483scan/24peak before R/H/P/MC captures','sceneSHA256':sha(TARGET/'scene.json')},indent=2))
# Only source06 changes in shared state, under the existing package lock.
with open(R/'.delivery-state.lock','a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    state = json.load(open(R/'delivery-state.json'))
    old = json.loads(json.dumps(state))
    state['scenes']['06-gallery'] = {'scene':'outputs/06-gallery/final-v22/scene.json','timeline_scan':'verification/timeline-scans/06-gallery-v22/scan.json','source_report':'verification/final/06-gallery/source-gsap-v22/index.html','source_visual_gate':'verification/final/06-gallery/v22/source-gate.json'}
    for key in state['scenes']:
        if key != '06-gallery':
            assert state['scenes'][key] == old['scenes'][key]
    temp = R/f'.delivery-state-{os.getpid()}.json'
    temp.write_text(json.dumps(state,indent=2)+'\n')
    temp.replace(R/'delivery-state.json')
    (D/'state-publication.json').write_text(json.dumps({'onlySceneChanged':'06-gallery','previous':old['scenes']['06-gallery'],'current':state['scenes']['06-gallery'],'sceneSHA256':sha(TARGET/'scene.json')},indent=2))
print(json.dumps({'sceneSHA256':sha(TARGET/'scene.json'),'assets':len(assets),'captureGSourceDelta':p['exactChangedRanges'],'otherMethodsCumulativeFrames':41}))
