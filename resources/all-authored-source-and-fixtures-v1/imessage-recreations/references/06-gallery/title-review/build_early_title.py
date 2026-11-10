from pathlib import Path
import json,copy
R=Path(__file__).resolve().parent;scene=json.loads((R.parent.parent.parent/'outputs/06-gallery/final-v18/scene.json').read_text());records=json.loads((R/'measurements.json').read_text());outlines={q['label']:q for q in json.loads((R/'native-outlines.json').read_text())};icon=json.loads((R/'icon-poses.json').read_text());by={q['id']:q for q in scene['layers']};replace={};append=[]
def keys(rows):return {k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in rows] for k in ['x','y','scaleX','scaleY','opacity']}
def glyph(label,id):
 a=outlines[label];poses=[]
 for rec in records:
  if label not in rec['parts']:continue
  q=rec['parts'][label];b=q['bbox'];poses.append(dict(frame=rec['frame'],x=b[0],y=b[1],scaleX=(b[2]-b[0])/a['width'],scaleY=(b[3]-b[1])/a['height'],opacity=q['opacity']))
 node=dict(id=id,type='group',start=poses[0]['frame']/30,end=(poses[-1]['frame']+1)/30,keyframes=keys(poses),children=[dict(id='native-title19-'+id,type='path',d=a['path'],fill=a['fill'],semanticText=label,editability='Native bounded semantic glyph contours; not live font text.',sourceFrame=a['sourceFrame'],sourceBounds=a['sourceBounds'])]);return node
for j,label in enumerate(['The','best contact','in your phone','with multiplayer mode']):replace['rene-v16-title-'+str(j)]=glyph(label,'rene-v16-title-'+str(j))
for id in ['rene-v16-introducing','rene-v16-mascot','rene-v16-Rene']:
 q=copy.deepcopy(by[id]);q['end']=321/30;replace[id]=q
watch=dict(id='g-1173',type='group',start=379/30,end=408/30,children=[glyph('Watches your','title19-watches-your'),glyph('inbox','title19-inbox'),dict(id='title19-independent-messages',type='image',src=str((R.parent/'assets/root-lock/messages-icon-canonical.png').resolve()),x=0,y=0,width=222,height=222,start=400/30,end=408/30,keyframes=keys(icon),editability='Original bounded Messages app artwork under independent measured native camera/opacity.')]);replace['g-1173']=watch
spec=dict(replacements=replace,append=append,scope=[[321,407]],provenance=dict(source='source-native exact original source frames',nativeTypography='Six isolated source semantic fragments traced into native glyph outlines; measured frame-by-frame pose/opacity. Green fill is the canonical FFmpeg reference mode#158556; source video color metadata is unspecified, so cross-decoder appearance is separately limited.',icon='Existing canonical bounded original Messages app artwork; independently fitted native size/position/opacity400–407. No full reference frame/video layer.',failure='Ratio-only green classifier admitted low-level black-glyph chroma noise from the lower line; its bbox inflated scaleY to2.8. Strong absolute/adaptive chroma and separate line masks prevent that semantic contamination. Title semantic handoffs are measured321 and379, not inherited323/375.'))
(R/'early-title-elements.json').write_text(json.dumps(spec,indent=2))
def absolute(x):
 if isinstance(x,dict):
  if x.get('src') and not x['src'].startswith(('data:','http:','https:','/')):x['src']=str((R.parent.parent.parent/'outputs/06-gallery/final-v18'/x['src']).resolve())
  for v in x.values():absolute(v)
 elif isinstance(x,list):
  for v in x:absolute(v)
absolute(scene);scene['layers']=[copy.deepcopy(replace.get(n['id'],n)) for n in scene['layers']];(R/'early-title.scene.json').write_text(json.dumps(scene,indent=2));print('Built early title only321–407',flush=True)
