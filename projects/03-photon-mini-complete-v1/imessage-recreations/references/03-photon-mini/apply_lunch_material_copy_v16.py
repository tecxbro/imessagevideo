"""Native measured lunch paragraph, card press and composer; immutable element input."""
from pathlib import Path
import copy,json
P=Path(__file__).resolve().parent

def apply_material_copy(scene,elements=None):
 scene=copy.deepcopy(scene);elements=elements or json.loads((P/'lunch-material-copy-v16-elements.json').read_text())
 def find(nodes,identifier):
  for n in nodes:
   if n['id']==identifier:return n
   result=find(n.get('children',[]),identifier)
   if result:return result
  return None
 def reid(n,prefix):
  n['id']=prefix+n['id']
  for c in n.get('children',[]):reid(c,prefix)
 for rid,prefix,start,end in [('p03-204','',541,618),('measured-lunch-ui-v13','lunch13-',735,800)]:
  root=find(scene['layers'],rid);para=find(root['children'],prefix+'p03-133');text=find(root['children'],prefix+'p03-132')
  text.setdefault('keyframes',{})['opacity']=[dict(t=0,value=1,ease='hold'),dict(t=start/30,value=0,ease='hold'),dict(t=end/30,value=1,ease='hold')]
  outlined=copy.deepcopy(elements['paragraph_outline']);reid(outlined,prefix);outlined.update(start=start/30,end=end/30);para['children'].append(outlined)
 root=find(scene['layers'],'p03-204');inner=find(root['children'],'measured-preview-inner-affine-v14');body=find(root['children'],'p03-135');tail=find(root['children'],'p03-134')
 black=[]
 for item in [tail,body]:
  original=item['fill'];item.setdefault('keyframes',{})['fill']=[dict(t=0,value=original,ease='hold'),dict(t=605/30,value='#e8e8e8',ease='hold'),dict(t=615/30,value=original,ease='hold')]
  q={k:copy.deepcopy(v) for k,v in item.items() if k not in ['id','keyframes']};q.update(id='card-press-v16-'+item['id'],fill='#000000');black.append(q)
 inner['children'].append(dict(id='card-press-material-v16',type='group',start=605/30,end=615/30,children=black,keyframes=dict(opacity=[dict(t=q['frame']/30,value=q['press_alpha'],ease='hold') for q in elements['press']]),semanticText='Pressed Uber Eats rich card',provenance=dict(kind='Native pressed-card union material',measured_frames=[605,614],notice='Source page stays253; only the card receives independent press. Three white information-panel probes and gray footer measure this.')))
 root['children'].append(dict(id='lunch-sheet-presentation-predim-v16',type='rect',x=29,y=30,width=742,height=1600,radius=120,fill='#000000',start=616/30,end=618/30,keyframes=dict(opacity=[dict(t=616/30,value=1/253,ease='hold'),dict(t=617/30,value=2/253,ease='hold')]),semanticText='Messages page before rich-app presentation',provenance=dict(kind='Native measured page material',notice='Source blank page253→252→251 at615→616→617 before618 sheet. Measured original information-card white probes agree. World background/hardware remain undimmed.')) )
 if any(g['id']==elements['gradient']['id'] for g in scene.get('gradients',[])):raise ValueError('Already applied native composer material')
 scene.setdefault('gradients',[]).append(copy.deepcopy(elements['gradient']))
 for rid,prefix,start,end in [('p03-204','',596,618),('measured-lunch-ui-v13','lunch13-',735,800)]:
  root=find(scene['layers'],rid);old=find(root['children'],prefix+'p03-112');old['opacity']=0
  children=copy.deepcopy(elements['composer_children'])
  for child in children:reid(child,prefix)
  new=dict(id=prefix+'lunch-composer-measured-v16',type='group',start=start/30,end=end/30,children=children,semanticText='Message composer',provenance=dict(kind='Native composer material/control geometry',measured_source_frame=750,notice='Input left180/top1513,width540; pluscentre119. Left-aligned native source placeholder outlines. Separate material and glyphs avoid blanket8px blur. Main composer appears596–617, returning composer735–799 shares independent UI camera. No full-frame/screen bitmap.'))
  root['children'].insert(root['children'].index(old)+1,new)
 scene['lunch_material_copy_v16']=dict(scopes=[[541,617],[735,799]],notice='Native paragraph glyph outlines, actual605–614card press and corrected composer lifecycle/geometry. Accepted621–729 menu/V5 stencil and all independently owned food/Order actors remain unchanged.')
 return scene

if __name__=='__main__':
 scene=json.loads((P/'final-v15.scene.json').read_text())
 (P/'lunch-material-copy-v16-applied.scene.json').write_text(json.dumps(apply_material_copy(scene),indent=2))
 print('Applied native lunch materials/copy')
