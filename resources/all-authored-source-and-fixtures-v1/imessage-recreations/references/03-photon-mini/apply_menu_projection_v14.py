from pathlib import Path
import copy,json
P=Path(__file__).parent

def apply_projection(scene):
 s=copy.deepcopy(scene);clip=copy.deepcopy(next(x for x in json.loads((P/'projection-v14.scene.json').read_text())['layers'] if x['id']=='measured-menu-clip-v13'))
 def rename(n):
  n['id']='proj14-'+n['id'];n['children']=[c for c in n.get('children',[]) if c['id']!='menu13-p03-151'] if 'children' in n else n.get('children',[])
  if not n['children']:n.pop('children',None)
  for c in n.get('children',[]):rename(c)
 rename(clip);clip['start']=618/30;clip['end']=730/30;clip['id']='measured-menu-projection-v14';s['layers']=[x for x in s['layers'] if x['id']!='measured-menu-projection-v14'];ix=next(i for i,x in enumerate(s['layers']) if x['id']=='measured-menu-clip-v13');s['layers'][ix]['start']=730/30;s['layers'].insert(ix,clip);s['menu_projection_v14']={'scope':[618,729],'notice':'Foreground row photo widths and copy geometry follow measured x/y projection independently; original photo plus controls are retained and duplicate native overlays removed. Background Messages page is owned separately by root backplane helper.'};return s
