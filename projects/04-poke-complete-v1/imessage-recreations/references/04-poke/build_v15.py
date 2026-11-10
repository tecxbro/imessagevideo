"""Bounded original-art circle motion and independent compact-header card pose."""
from pathlib import Path
import json,copy,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at,track
from v10_shape_trace import vector_outline
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v14/scene.json').read_text());fps=s['fps'];old=next(l for l in s['layers']if l['id']=='p0012');pose=json.loads((p/'measurements-v8/palm-rotation-40-63-v15-parent.json').read_text());asset=p/'assets/poke-circle.png';assert hashlib.sha256(asset.read_bytes()).hexdigest()==pose['asset_sha256'];file=p/'measurements-v8/circle-palm-vector-v15.json'
if not file.exists():
    a=np.array(Image.open(asset).convert('RGBA').resize((476,476),Image.Resampling.LANCZOS));rgb=a[:,:,:3];yy,xx=np.mgrid[:476,:476];mask=(rgb.min(2)>150)&(rgb.max(2)-rgb.min(2)<65)&(xx>57)&(xx<429)&(yy>57)&(yy<429);labels,_=ndimage.label(mask);areas=np.bincount(labels.ravel());areas[0]=0;mask=labels==int(areas.argmax());d=vector_outline(mask,(0,0,0,0),(238,238),1);file.write_text(json.dumps(dict(asset_sha256=pose['asset_sha256'],d=d,method='Single static editable white-palm silhouette from genuine original logo material; whole-logo photos/video are not used as frame output. Source angle/offset are independent native transforms.'),indent=2))
vector=json.loads(file.read_text());assert vector['asset_sha256']==pose['asset_sha256'];g=copy.deepcopy(old);g.update(id='v15-circle-art',start=40/fps,end=64/fps);g['children']=[dict(id='v15-circle-blue-material',type='image',src='assets/poke-circle-material-v10.png',x=-238,y=-238,width=476,height=476)];palm=dict(id='v15-circle-palm-camera',type='group',children=[dict(id='v15-circle-palm',type='path',d=vector['d'],fill='#ffffff')]);rows=[]
for row in pose['frames']:
    n=row['frame'];t=n/fps;cx,cy=row['source_body']['center_from_top_width'];scale=row['source_body']['diameter']/476;dx,dy=row['translation_pixels_after_body_normalization'];gx,gy,gsx,gsy=[at(old,k,t)for k in['x','y','scaleX','scaleY']];rows.append(dict(time=t,x=(cx+dx*scale-gx)/gsx,y=(cy+dy*scale-gy)/gsy,scaleX=scale/gsx,scaleY=scale/gsy,rotation=row['clockwise_degrees_relative_to_original_asset']))
for prop in['x','y','scaleX','scaleY','rotation']:track(palm,prop,rows)
g['children'].append(palm);old['end']=40/fps;s['layers'].insert(s['layers'].index(old)+1,g)
# The caption is an independent measured native text role, not artwork motion.
cap=next(n for n in s['layers']if n['id']=='p0015');rows=json.loads((p/'measurements-v8/circle-caption-ink-v15.json').read_text())['measurements']
for prop in['x','y','scaleX','scaleY']:
    first=dict(time=39/fps,**{prop:at(cap,prop,39/fps)});after=dict(time=64/fps,**{prop:at(cap,prop,64/fps)});track(cap,prop,[first,*rows,after])
cap.setdefault('keyframes',{}).setdefault('fill',[]).append(dict(t=40/fps,value='#818181',ease='hold'))
# The selected app card has its own source-measured scroll and type roles.
card=next(n for n in s['layers']if n['id']=='p0262');fit=json.loads((p/'measurements-v8/selected-card-type-ink-v15.json').read_text())
for node in card['children']:
    if node['id']=='p0264':node['fontFamily']='SF Pro Text'
    if node['id']=='p0265':node.update(fontFamily='SF Pro Display',fontWeight=600)
by={n['id']:n for n in card['children']}
for row in fit['measurements']:
    for prop in['x','y','scaleX','scaleY']:by[row['id']][prop]=row[prop]
late=copy.deepcopy(card);late['id']='v15-selected-card-camera';late['start']=734/fps;late['end']=789/fps
# Preserve every earlier camera interpolation by using a separately bounded actor.
card['end']=734/fps
for node in late['children']:node['id']='v15-'+node['id']
content=dict(id='v15-selected-card-content',type='group',end=789/fps,children=[n for n in late['children']if n['type']in['image','text']]);late['children']=[n for n in late['children']if n['type']not in['image','text']]+[content]
late['keyframes']={};camera=json.loads((p/'measurements-v8/selected-card-camera-v15.json').read_text())['measurements']
for prop in['x','y','scaleX','scaleY']:track(late,prop,camera)
s['layers'].insert(s['layers'].index(card)+1,late)
# Keep a geometry-only proof before adding independently measured material.
geometry=copy.deepcopy(s);(p/'scene-v15-geometry-only.json').write_text(json.dumps(geometry,indent=2,ensure_ascii=False))
material=json.loads((p/'measurements-v8/header-material-v15.json').read_text());s['gradients'].append(material['gradient']);header=next(n for n in s['layers']if n['id']=='p0298');glass=next(n for n in header['children']if n['id']=='v10-small-header-glass')
if glass.get('keyframes',{}).get('opacity'):raise ValueError('Unexpected prior glass opacity track')
newglass=copy.deepcopy(glass);newglass.update(id='v15-small-header-glass',start=734/fps,end=800/fps,height=material['height'],fill='url(#small-header-glass-v15)');newglass.pop('keyframes',None);glass.setdefault('keyframes',{})['opacity']=[dict(t=0,value=1),dict(t=734/fps,value=0,ease='hold'),dict(t=800/fps,value=1,ease='hold')];header['children'].insert(header['children'].index(glass)+1,newglass)
# Foreground contact logo is genuine isolated artwork, separate from the glass.
logo=next(n for n in header['children']if n['id']=='p0295');art=json.loads((p/'assets/poke-header-logo-native758-v15-provenance.json').read_text())
if logo.get('keyframes',{}).get('opacity'):raise ValueError('Unexpected original logo opacity')
newlogo=copy.deepcopy(logo);newlogo.update(id='v15-contact-logo-art',start=734/fps,end=800/fps,src=art['asset'],x=art['x'],y=art['y'],width=art['width'],height=art['height']);newlogo.pop('keyframes',None);logo.setdefault('keyframes',{})['opacity']=[dict(t=0,value=1),dict(t=734/fps,value=0,ease='hold'),dict(t=800/fps,value=1,ease='hold')];header['children'].insert(header['children'].index(logo)+1,newlogo)
s['title']='Poke Apple Messages launch — native recreation v15 bounded circle and header correction'
s['source']['notes']+=' V15 source-only 40–63 white-palm registration finds a real oscillating artwork rotation (native55 +7degclockwise, shape correlation .995); native palm transforms separate that from unchanged circle-body geometry/material. Earlier6–39 and64onward artwork remains unchanged. Source selected-card photo/title registration restores its independent734–788scroll, actual125/256compact scale, confirmed789content cutoff and source-confirmed content/body cutoff789; hardware/header material remains a separate component to800. Card typography uses independently ranked TextSemibold/DisplaySemibold with actual browser ink fits. Header material is a separate native gradient fitted from source flat-gray pixels over a verified clean720–722screen, not a hardware transform or source-frame image. The contact logo uses one genuine isolated native758brand texture; contact title, card and all screen UI remain editable native elements.'
(p/'scene-v15-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False))
