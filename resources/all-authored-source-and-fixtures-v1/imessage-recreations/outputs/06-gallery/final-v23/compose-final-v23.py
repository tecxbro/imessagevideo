"""Freeze source06 native-reviewed birthday entrances and preserve actual22 artifacts."""
from pathlib import Path
import json, hashlib, os, shutil, re, subprocess, fcntl
R = Path('/workspace/imessage-recreations')
D = R/'verification/final/06-gallery/v23'
REF = R/'references/06-gallery'
OUT = R/'outputs/06-gallery'
BASE = OUT/'final-v22/scene.json'
TARGET = OUT/'final-v23'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE) == '9ac48e4bac35d613a2a13fc724004b1102db0448a257aea7c4d7e5058b4e0a15'
if (TARGET/'scene.json').exists():
    raise RuntimeError('Unique final-v23 already exists; never overwrite an accepted snapshot')
q = json.load(open(D/'native-release.json'))
p = json.load(open(D/'scope-final.json'))
assert not p['changedOutsideCaptureUnion']
assert p['changedFrames'] == q['changedNative']
assert q['allChangedImprove'] and q['allControlsPixelIdentical'] and q['changedNativeCovered']
source = REF/'scene-birthday-birth-v23.json'
assert sha(source) == q['sceneSHA256'] == p['targetSha256']
# Retain actual22G including every lossless frame before touching its writer.
backup = OUT/'iterations/final-v22-before-v23'
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
pool = REF/'assets/final-v23-normalized'
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
s['source']['notes'] += ' Finalv23 preserves accepted22 typography and portraits and closes measured independent birthday UI start/opacity/y lifecycles in five existing actors. All other22 evaluated graphics are preserved. Same genuine static UI internals and parent camera; no screen/frame playback. Remaining optical/material/AA differences are disclosed, not a100% identity claim.'
author = REF/'scene-final-v23-composed.json'
author.write_text(json.dumps(s,indent=2)+'\n')
subprocess.run(['python',str(R/'engines/snapshot_scene.py'),str(author),str(TARGET)],check=True)
base_ranges = json.load(open(R/'verification/final/06-gallery/v22/cumulative20-scope.json'))['exactChangedRanges']
nums = sorted({n for a,b in base_ranges+p['exactChangedRanges'] for n in range(a,b+1)})
cumulative = []
for n in nums:
    if cumulative and cumulative[-1][1] == n-1:
        cumulative[-1][1] = n
    else:
        cumulative.append([n,n])
(D/'composition.json').write_text(json.dumps({'baseSHA256':sha(BASE),'scene':str(TARGET/'scene.json'),'sceneSHA256':sha(TARGET/'scene.json'),'payloadSHA256':sha(REF/'birthday-birth-v23-elements.json'),'nativeReviewedSHA256':q['sceneSHA256'],'source22Delta':p['exactChangedRanges'],'cumulative20Ranges':cumulative,'normalizedAssets':len(assets),'preserved22':str(backup),'gate':'birthday native gate pass; encoded G23 source gate pending'},indent=2))
(D/'normalized-assets.json').write_text(json.dumps(assets,indent=2))
(D/'source-gate.json').write_text(json.dumps({'status':'PENDING','reason':'Native birthday-source pass; require encoded G23 mapped1483scan/24peak before R/H/P/MC captures','sceneSHA256':sha(TARGET/'scene.json')},indent=2))
# Only source06 changes in shared state, under the existing package lock.
with open(R/'.delivery-state.lock','a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    state = json.load(open(R/'delivery-state.json'))
    old = json.loads(json.dumps(state))
    state['scenes']['06-gallery'] = {'scene':'outputs/06-gallery/final-v23/scene.json','timeline_scan':'verification/timeline-scans/06-gallery-v23/scan.json','source_report':'verification/final/06-gallery/source-gsap-v23/index.html','source_visual_gate':'verification/final/06-gallery/v23/source-gate.json'}
    for key in state['scenes']:
        if key != '06-gallery':
            assert state['scenes'][key] == old['scenes'][key]
    temp = R/f'.delivery-state-{os.getpid()}.json'
    temp.write_text(json.dumps(state,indent=2)+'\n')
    temp.replace(R/'delivery-state.json')
    (D/'state-publication.json').write_text(json.dumps({'onlySceneChanged':'06-gallery','previous':old['scenes']['06-gallery'],'current':state['scenes']['06-gallery'],'sceneSHA256':sha(TARGET/'scene.json')},indent=2))
print(json.dumps({'sceneSHA256':sha(TARGET/'scene.json'),'assets':len(assets),'captureGSourceDelta':p['exactChangedRanges'],'otherMethodsCumulativeFrames':len(nums)}))
