"""Reproduce the one-state native gray backplane patch from immutableV17."""
from pathlib import Path
import json,hashlib
from apply_mail_gray354_v18 import apply_gray354
P=Path(__file__).resolve().parent
scene=apply_gray354(json.loads((P/'final-v17.scene.json').read_text()))
scene['source']['notes']+=' V18exact354: nativegrayMessagesbackplanefootprint appearsatfirstreturnframebehindexistingclosingMailpane; obsoletepillhiddenonly354. Nativegrayfill/outerboundary measuredfromuniformsourcecomponent.353/355andallcamera/hardware/foreground/worldstatespreserved. No new rasterasset.'
raw=json.dumps(scene,indent=2)+'\n'
assert hashlib.sha256(raw.encode()).hexdigest()=='b6aff22844a321dceb1017d06a00e4b305b683081c5446f0433f0a0679d8b5c1'
(P/'joint-v18-reproduced.scene.json').write_text(raw)
print('V18authoringhash/parityverified; immutableinputunchanged')
