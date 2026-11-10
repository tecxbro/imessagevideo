"""Reproduce the disjoint V15 foreground, collage and semantic peak merge."""
from pathlib import Path
import hashlib,json,subprocess,sys
from apply_menu_rows_split_v15 import apply_rows
from apply_menu_thumbnail_clips_v15 import apply_thumbnail_clips
from apply_collage_cameras_v15 import apply_collage_cameras
P=Path(__file__).resolve().parent
scene=json.loads((P/'final-v14.scene.json').read_text())
scene=apply_rows(scene)
scene=apply_thumbnail_clips(scene)
spec_path=P/'collage-v15-measure/cameras-and-art-frozen-v15.json'
assert hashlib.sha256(spec_path.read_bytes()).hexdigest()=='36e2b1c253b13e6b600a9867d5201d8cb55dd14681d62bffdd4f6e47228bee91'
scene=apply_collage_cameras(scene,json.loads(spec_path.read_text()))
staging=P/'joint-v15-before-review.scene.json'
staging.write_text(json.dumps(scene,indent=2))
elements=P.parent.parent/'outputs/03-photon-mini/remaining-peaks-review-03/remaining-peaks-review-elements.json'
subprocess.run([sys.executable,str(P/'apply-remaining-peaks-review.py'),'--input',str(staging),'--output',str(P/'joint-v15-provisional.scene.json'),'--elements',str(elements)],check=True)
scene=json.loads((P/'joint-v15-provisional.scene.json').read_text())
scene['source']['notes']+=' V15 foreground: six separately bounded static menu-row UI assets with independently measured native copy/photo planes, native panel/header/hardware/cart/selection cameras, four food entrance photo textures and independent original controls; internal UI copy is bitmap and explicitly declared. No whole-source-frame or source-video playback layer.'
(P/'joint-v15-provisional.scene.json').write_text(json.dumps(scene,indent=2))
print('V15 joint provisional complete; validate before freezing')
