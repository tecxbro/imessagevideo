"""Bridge the early measured UI into the separately cloned mail-exit camera."""
from pathlib import Path
from PIL import Image
import numpy as np,json,copy,sys
p=Path(__file__).parent;sys.path.insert(0,str(p.parents[1]/'engines'));from render_pillow import state
s=json.loads((p/'mail-tail-v14.scene.json').read_text());mail=next(x for x in s['layers'] if x['id']=='late-mail-native-state-v5');fade=next(x for x in mail['children'] if x['id']=='late-mail-ui-fade');first=next(x for x in s['layers'] if x['id']=='p03-86');early=next(x for x in first['children'] if x['id']=='early-messages-ui-v13')
def freeze(layer,t):
 if t<layer.get('start',0) or t>=layer.get('end',42):return None
 q=copy.deepcopy(state(layer,t))
 if q.get('opacity',1)<1e-8:return None
 for key in ['keyframes','start','end']:q.pop(key,None)
 q['id']='mail14-'+q['id'];q['children']=[z for c in layer.get('children',[]) if (z:=freeze(c,t)) is not None] if 'children' in layer else q.get('children')
 if q.get('children') is None:q.pop('children',None)
 return q
frozen=freeze(early,413/30);fade['children']=[frozen];proof=[]
def images(node,t,parent=(0,0,1,1)):
 q=state(node,t);px,py,sx,sy=parent;cur=(px+q.get('x',0)*sx,py+q.get('y',0)*sy,sx*q.get('scaleX',1),sy*q.get('scaleY',1));out=[]
 if node['type']=='image':
  im=Image.open(p/node['src']).convert('RGB');a=np.array(im);area=int(((a[:,:,2].astype(int)-a[:,:,0]>30)&(a[:,:,2]>170)&(a[:,:,0]<190)).sum());out.append((area*cur[2]*cur[3],node,cur))
 for c in node.get('children',[]):out+=images(c,t,cur)
 return out
for f in range(414,430):
 t=f/30;_,art,(x,y,sx,sy)=next(z for z in images(mail,t) if z[1]['id']=='mail14-early-mail-post-skin-v13');im=Image.open(p/'mail-tail-native-v14'/f'{f-413:03}.png').convert('RGB');w=max(1,round(art['width']*sx));h=max(1,round(art['height']*sy));rr=np.array(Image.open(p/art['src']).convert('RGB').resize((w,h),Image.Resampling.BILINEAR),dtype=float);xx=round(x);yy=round(y);x0=max(0,xx);x1=min(1920,xx+w);y0=max(0,yy);y1=min(1080,yy+h);rr=rr[y0-yy:y1-yy,x0-xx:x1-xx];ss=np.array(im,dtype=float)[y0:y1,x0:x1];m=(rr[:,:,2]-rr[:,:,0]>30)&(rr[:,:,2]>170)&(rr[:,:,0]<190);d=253-rr;v=253-ss;alpha=float(np.clip(np.sum(d[m]*v[m])/max(np.sum(d[m]*d[m]),1),0,1));q=next((z for z in fade['keyframes']['opacity'] if abs(z['t']-t)<1e-8),None)
 if q:q['value']=alpha
 else:fade['keyframes']['opacity'].append({'t':t,'value':alpha,'ease':'linear'})
 proof.append({'frame':f,'blue_art':art['id'],'ui_opacity':alpha})
fade['keyframes']['opacity'].sort(key=lambda q:q['t']);s['source']['notes']+=' V14 mail UI bridge: the oldv5exit cloned obsoletev4 UI. Reuse the actual measured early UI state at413 with independent subsequent physical camera and perframe blue-art opacity; semantic layers retained.'
(p/'early-mail-ui-v14.scene.json').write_text(json.dumps(s,indent=2));(p/'early-mail-ui-v14-changes.json').write_text(json.dumps({'scope':[414,429],'frozen_early_state':413,'measurements':proof},indent=2));print([(r['frame'],round(r['ui_opacity'],3)) for r in proof])
