"""Bake one tiny native period outline into the immutable element spec."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from measure_lunch_refinement_v16 import find
from apply_menu_thumbnail_clips_v15 import affine_group
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
scene=json.loads((P/'final-v16.scene.json').read_text())
phone=next(n for n in scene['layers']if n['id']=='p03-86')
rgb=np.array(Image.open(P/'mail-edit-v17-source/0302.png').convert('RGB'),float)[708:716,1164:1171]
alpha=np.clip((253-rgb.mean(2))/253,0,1)
period_d,_=trace_alpha(alpha,1164,708)
rows=json.loads((P/'mail-edit-v17-elements.json').read_text())['first_line_poses']
camera300=np.array(next(r['copy_world_matrix']for r in rows if r['frame']==300))
camera302=np.array(next(r['copy_world_matrix']for r in rows if r['frame']==302))
_,parent300=find(phone,'p03-77',300)
local=np.linalg.inv(parent300)@camera300@np.linalg.inv(camera302)
period=dict(id='mail-return-final-period-v17',type='path',d=period_d,fill='#020202',semanticText='.',provenance=dict(kind='Native original period glyph outline',source_frame=302,source_crop=[1164,708,1171,716],notice='Finaltypedperiod replaces the removed originalcaret; no font/layout or camera change.'))
period_group=affine_group(local[:2],'mail-return-final-period-local-v17',[period])
period_group.update(start=335/30,end=342/30)
p=P/'mail-return-copy-v17-elements.json'
spec=json.loads(p.read_text())
spec['period_group']=period_group
p.write_text(json.dumps(spec,indent=2))
print('One native period serialized')
