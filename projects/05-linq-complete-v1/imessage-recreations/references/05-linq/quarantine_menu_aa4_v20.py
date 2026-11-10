"""Verification-only directional-menu sampling study; production files protected."""
from pathlib import Path
import importlib.util,json,hashlib,time
import numpy as np
from PIL import Image
R=Path.cwd()
D=R/'verification/method-parity/05-linq/native-review/aa4-lifecycle'
assert not (D/'promotion-journal.json').exists(),'Released quarantine is frozen; do not rerender/overwrite it'
(D/'aa4').mkdir(exist_ok=True,parents=True)
(D/'aa1-controls').mkdir(exist_ok=True)
scene_path=R/'outputs/05-linq/final-v20/scene.json'
scene=json.load(open(scene_path))
engine_path=R/'engines/render_pillow.py'
engine_sha=hashlib.sha256(engine_path.read_bytes()).hexdigest()
assert engine_sha=='5c7e3477e1ab9872df9fad4edc0622c14c44ced74f0671ee18f04d517b6ae33c'
spec=importlib.util.spec_from_file_location('pillow_menu_quarantine',engine_path)
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.register_fonts(scene,str(scene_path.parent))
cache=R/'outputs/05-linq/cache/pillow'
protected={f:(p.stat().st_ino,p.stat().st_size,p.stat().st_mtime_ns)for f in range(1458)for p in [cache/f'{f:06}.png']}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
master_sha=sha(R/'outputs/05-linq/pillow.mp4')
rows=[]
started=time.monotonic()
for aa,frames,folder in [(4,range(98,131),'aa4'),(1,[98,111,130],'aa1-controls')]:
    for frame in frames:
        engine.GROUP_CACHE.clear()
        engine.LEAF_CACHE.clear()
        out=D/folder/f'{frame:06}.png'
        image=engine.render(scene,frame/scene['fps'],str(scene_path.parent),aa)
        engine.atomic_png(image,out)
        row={'frame':frame,'antialias':aa,'png':str(out.relative_to(R)),'sha256':sha(out)}
        rows.append(row)
        (D/'capture-progress.json').write_text(json.dumps({'completed':rows,'seconds':time.monotonic()-started},indent=2)+'\n')
        print(json.dumps({'frame':frame,'antialias':aa}),flush=True)
assert sha(R/'outputs/05-linq/pillow.mp4')==master_sha
assert all(protected[f]==(p.stat().st_ino,p.stat().st_size,p.stat().st_mtime_ns)for f in range(1458)for p in [cache/f'{f:06}.png'])
report={'sceneSHA256':sha(scene_path),'engineSHA256':engine_sha,'protectedProductionPictureSHA256':master_sha,'all1458ProductionCacheStatsUnchanged':True,'productionPictureUnchanged':True,'captures':rows,'seconds':time.monotonic()-started,'method':'Published native Pillow engine imported without modification; one verification-only AA4 render per frame98–130, fresh AA1 controls98/111/130; local render caches cleared between frames to bound memory, not alter sampling.','authoredLifecycle':{'composerContinuation':[99,109],'extremeMenuRows':[101,126],'independentOutgoingMenu':[127,127],'blankCut':[128,128],'incomingGames':[129,130]},'notice':'No master, source scene, engine code or production cache write. Production promotion requires dense source/G/current-P comparison and parent gate.'}
(D/'capture.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'seconds':report['seconds'],'captures':len(rows),'productionUntouched':True}))
