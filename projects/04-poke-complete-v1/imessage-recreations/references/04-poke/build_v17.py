"""Bounded original portrait/caption native geometry, independent child cameras."""
from pathlib import Path
import json,copy
from v8_utils import at,track,resolved
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v16/scene.json').read_text());fps=s['fps'];rows=json.loads((p/'measurements-v8/caption-ink-98-108-v17.json').read_text())['measurements']
for gid,nid in [('p0007','p0006'),('p0010','p0009')]:
 g=next(l for l in s['layers'] if l['id']==gid);n=next(l for l in g['children'] if l['id']==nid);r=[r for r in rows if r['id']==nid]
 for prop in ['x','y','scaleX','scaleY']:
  before=dict(time=97/fps,**{prop:at(n,prop,97/fps)});after=dict(time=109/fps,**{prop:at(n,prop,109/fps)});track(n,prop,[before,*r,after])
# Native image affine cameras use the full observed ellipse matrix, not a forced circle.
import numpy as np,math
portrait=json.loads((p/'measurements-v8/portrait-98-108-v17-parent.json').read_text());pose_rows={name:[]for name in ['braden','sydney']}
for row in portrait['records']:
 for actor in row['actors']:
  m=np.array(actor['matrix'],float);a=m[:,:2];values,vectors=np.linalg.eigh(a);order=np.argsort(values)[::-1];values=values[order];vectors=vectors[:,order];angle=math.degrees(math.atan2(vectors[1,0],vectors[0,0]));prior=pose_rows[actor['name']]
  if prior:angle+=round((prior[-1]['rotation']-angle)/180)*180
  pose_rows[actor['name']].append(dict(frame=row['frame'],time=row['time'],tx=m[0,2],ty=m[1,2],eigenX=float(values[0]),eigenY=float(values[1]),rotation=angle,inverse_rotation=-angle))
for gid,nid,name in [('p0007','p0005','braden'),('p0010','p0008','sydney')]:
 g=next(l for l in s['layers'] if l['id']==gid);old=next(l for l in g['children'] if l['id']==nid)
 if old.get('keyframes',{}).get('opacity'):raise ValueError('Unexpected original image opacity')
 old.setdefault('keyframes',{})['opacity']=[dict(t=0,value=1),dict(t=98/fps,value=0,ease='hold'),dict(t=109/fps,value=1,ease='hold')]
 child=dict(id='v17-'+name+'-art',type='image',src=old['src'],x=0,y=0,width=274,height=274);camera=dict(id='v17-'+name+'-image-camera',type='group',start=98/fps,end=109/fps,children=[child]);rows=[]
 for r in pose_rows[name]:
  t=r['time'];gx,gy,scale=[at(g,k,t)for k in ['x','y','scaleX']]
  if abs(scale-at(g,'scaleY',t))>1e-8 or at(g,'rotation',t)!=0:raise ValueError('Unexpected parent affine')
  rows.append(dict(time=t,x=(r['tx']-gx)/scale,y=(r['ty']-gy)/scale,scaleX=r['eigenX']/scale,scaleY=r['eigenY']/scale,rotation=r['rotation'],inverse_rotation=r['inverse_rotation']))
 for prop in ['x','y','scaleX','scaleY','rotation']:track(camera,prop,rows)
 track(child,'rotation',rows,'inverse_rotation');g['children'].insert(g['children'].index(old)+1,camera)
# Independently measured found-message early entry. Original map/modal and later message remain unchanged.
g=next(l for l in s['layers'] if l['id']=='p0230');ledger=json.loads((p/'measurements-v8/found-early-camera-v17.json').read_text());rows=[dict(time=r['frame']/fps,y=r['body_bounds'][1]-1)for r in ledger['records']if r['status']=='coherent_original_graybody' and 549<=r['frame']<=574];before=dict(time=548/fps,y=at(g,'y',548/fps));after=dict(time=575/fps,y=at(g,'y',575/fps));track(g,'y',[dict(time=547/fps,y=at(g,'y',547/fps)),before,*rows,after])
for nid in ['p0227','p0228-early','p0229']:
 old=next(n for n in g['children'] if n['id']==nid)
 if old.get('keyframes',{}).get('opacity'):raise ValueError('Unexpected early message opacity')
 old.setdefault('keyframes',{})['opacity']=[dict(t=0,value=1),dict(t=549/fps,value=0,ease='hold'),dict(t=579/fps,value=1,ease='hold')]
outline=json.loads((p/'measurements-v8/found-early-outline-v17.json').read_text());body=dict(id='v17-found-early-body',type='path',d=outline['d'],fill='#ececec',x=1.25,y=1.25,scaleX=1.25,scaleY=1.25);text=resolved(next(n for n in g['children']if n['id']=='p0229'),569/fps);text.update(id='v17-found-early-text',y=text['y']+2.5,opacity=1);g['children'].append(dict(id='v17-found-early-ui',type='group',start=549/fps,end=579/fps,children=[body,text]))
s['title']='Poke Apple Messages launch — native recreation v17 bounded intro geometry'
s['source']['notes']+=' V17 separately fits original98–108 Braden/Sydney caption ink; side-censored text uses surviving inner edge and complete glyph height instead of treating partial width as scale. TextRegular face, original97/109controls, independent body camera and actual109phase cut are retained. V16 modal/location correction is immutable and unchanged. Portrait geometry uses source-only steepest RGB body-edge ellipses, RMS.16–.78px, preserving independent existing opacity and authentic static art; paired native transforms express each full symmetric affine matrix. The early found-message actual549first coherent body and dense549–574entrance replace a guessed ease that put557about115px too low. One static editable original569outline and native existing TextRegular sentence restore the measured pill/tail and2px ink offset, preserving548/575/579and all later message states.'
(p/'scene-v17-candidate.json').write_text(json.dumps(s,indent=2,ensure_ascii=False));print('V17 candidate ready')
