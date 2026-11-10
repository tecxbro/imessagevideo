from pathlib import Path
import importlib.util,json
P=Path(__file__).parent

def apply(name,fn,s):
 spec=importlib.util.spec_from_file_location(name.replace('-','_'),P/name);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return getattr(m,fn)(s)

s=json.loads((P/'final-v13.scene.json').read_text());s=apply('apply_mini_own_v14.py','apply_own',s);s=apply('apply_cart_v14.py','apply_cart',s)
s=apply('apply_blue_arrival_v14.py','apply_blue',s)
s=apply('apply_preview_arrival_v14.py','apply_preview',s)
s=apply('apply_header_v14.py','apply_header',s)
s=apply('apply_food_orbit.py','apply_food',s)
s=apply('apply-root-zoom.py','apply_zoom',s);s=apply('apply-root-backplane-v5.py','apply_backplane',s)
(P/'joint-v14-provisional.scene.json').write_text(json.dumps(s,indent=2));print('joint provisional written')
