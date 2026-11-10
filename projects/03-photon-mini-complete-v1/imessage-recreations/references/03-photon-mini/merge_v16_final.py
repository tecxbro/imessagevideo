"""Reproduce the bounded V16 early/chrome/lunch/game/tail merge from immutableV15."""
from pathlib import Path
import json,subprocess,sys,hashlib
from apply_early_entry_v17 import apply_entry
from apply_lunch_chrome_v16 import apply_chrome
from apply_brand_cut_v16 import apply_brand_cut
from apply_lunch_material_copy_v16 import apply_material_copy
from apply_return_camera_v16 import apply_return
P=Path(__file__).resolve().parent
scene=json.loads((P/'final-v15.scene.json').read_text())
scene=apply_entry(scene);scene=apply_chrome(scene);scene=apply_brand_cut(scene)
scene=apply_material_copy(scene);scene=apply_return(scene)
staging=P/'joint-v16-before-game.scene.json';staging.write_text(json.dumps(scene,indent=2))
elements=P.parent.parent/'outputs/03-photon-mini/game-entry-review-08/game-entry-review-elements.json'
subprocess.run([sys.executable,str(P/'apply-game-entry-review.py'),'--input',str(staging),'--output',str(P/'joint-v16-before-pizza.scene.json'),'--elements',str(elements)],check=True)
import importlib.util
helper=importlib.util.spec_from_file_location('pizza_top_gap',P/'apply-pizza-top-gap.py');module=importlib.util.module_from_spec(helper);helper.loader.exec_module(module)
scene=module.apply_pizza_gap(json.loads((P/'joint-v16-before-pizza.scene.json').read_text()))
scene['source']['notes']+=' V16 bounded repairs: measured early independentpage/message/status entry211–229; physical lunchsettle497–516; nativeparagraph glyphoutlines/actualcardpress/composer541–617 and735–799; separateUI/physical returncamera; missing originalpizza738–740; nativegamepresentation813–849; correctopaquePhotoncut1185. Two tiny1–2px gameaperture extraction remnants remain candid segmentationresiduals; no wholeframe/screen/video runtime layer.'
(P/'joint-v16-provisional.scene.json').write_text(json.dumps(scene,indent=2))
print('JointV16 provisionalcomplete; finalasset/scope/boundary checks beforefreeze')
