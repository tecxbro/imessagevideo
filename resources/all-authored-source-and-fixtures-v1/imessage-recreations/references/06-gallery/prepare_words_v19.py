"""Original native glyphs with measured right-to-left blur/opacity handoff."""
from pathlib import Path
import json,copy,importlib.util
from functools import lru_cache
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,map_coordinates,label,find_objects,binary_dilation
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;F=D/'native-late-v19';s=json.loads((D.parent.parent/'outputs/06-gallery/final-v18/scene.json').read_text());snap=D.parent.parent/'outputs/06-gallery/final-v18'
def restore(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src' and isinstance(v,str) and not v.startswith('data:'):o[k]=str((snap/v).resolve())
   else:restore(v)
 elif isinstance(o,list):
  for q in o:restore(q)
restore(s)
@lru_cache(maxsize=8)
def gray(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB')).mean(2).astype(np.float32)
spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace);glyphs=[]
for name,frame,box,letters in [('tracks',846,[215,400,1710,660],'Trackswhat'),('you',882,[725,470,1195,720],'you')]:
 x0,y0,x1,y1=box;ink=(255-gray(frame)[y0:y1,x0:x1])/255;labs,n=label(ink>.35);components=[]
 for k,sl in enumerate(find_objects(labs),1):
  if sl is not None and int((labs[sl]==k).sum())>80:components.append((sl[1].start,k,sl))
 components.sort();print(name,[(sl[1].start+x0,sl[1].stop+x0) for _,k,sl in components],flush=True);assert len(components)==len(letters),(name,len(components))
 for j,(letter,(_,k,sl)) in enumerate(zip(letters,components)):
  component=binary_dilation(labs==k,iterations=2);aa=ink*component;top=max(0,sl[0].start-2);bottom=min(ink.shape[0],sl[0].stop+2);left=max(0,sl[1].start-2);right=min(ink.shape[1],sl[1].stop+2);a=aa[top:bottom,left:right];x=x0+left;y=y0+top;path,stats=trace.trace_alpha(a,x,y);padded=np.pad(a,45);glyphs.append(dict(name=name,letter=letter,id=f'v19-{name}-glyph-{j}',x=x-45,y=y-45,art=padded,path=path,semantic=letter,history=[]))
T=glyphs[0];u=glyphs[-1];tposes=[];uposes=[]
def at(g,wx,wy,sigma,dx=0,dy=0):
 ar=gaussian_filter(g['art'],sigma,mode='constant',cval=0);return map_coordinates(ar,[wy-g['y']-dy,wx-g['x']-dx],order=1,mode='constant',cval=0)
wy,wx=np.mgrid[400:700:2,220:410:2]
for f in range(846,874):
 target=(255-gray(f)[400:700:2,220:410:2])/255
 def residual(v):
  dy,b,a=v;return (a*at(T,wx,wy,b,dy=dy)-target).ravel()
 init=[(f-846)*.7,min(8,max(0,(f-864)*.7)),max(.05,1-max(0,f-864)/10)];fit=least_squares(residual,init,bounds=([-5,0,0],[40,16,1.05]),max_nfev=55,diff_step=.005,ftol=.0003,xtol=.0003);dy,b,a=map(float,fit.x);tposes.append(dict(frame=f,dy=dy,blur=b,opacity=a))
wy,wx=np.mgrid[465:680:2,1035:1260:2]
for f in range(864,891):
 target=(255-gray(f)[465:680:2,1035:1260:2])/255
 def residual(v):
  dx,dy,b,a=v;return (a*at(u,wx,wy,b,dx=dx,dy=dy)-target).ravel()
 init=[max(-3,38-(f-864)*1.8),-1,.5,1];fit=least_squares(residual,init,bounds=([-15,-15,0,.1],[70,15,14,1.05]),max_nfev=55,diff_step=.005,ftol=.0003,xtol=.0003);dx,dy,b,a=map(float,fit.x);uposes.append(dict(frame=f,dx=dx,dy=dy,blur=b,opacity=a))
tby={q['frame']:q for q in tposes};uby={q['frame']:q for q in uposes};sigmas=[0,.5,1,2,3,4,6,8,12,16];blurs={g['id']:{b:gaussian_filter(g['art'],b,mode='constant',cval=0) for b in sigmas} for g in glyphs};previous={g['id']:{'opacity':1 if g['name']=='tracks' else 0,'blur':0 if g['name']=='tracks' else 12} for g in glyphs};records=[]
for f in range(846,891):
 targetFull=(255-gray(f))/255;td=tby.get(f,tposes[-1]);ud=uby.get(f,dict(dx=uposes[0]['dx']+(864-f)*3.5,dy=uposes[0]['dy']));state={}
 for g in glyphs:
  dx=0 if g['name']=='tracks' else ud['dx'];dy=td['dy'] if g['name']=='tracks' else ud['dy'];left=max(0,int(np.floor((g['x']+dx)/2))*2);right=min(1920,int(np.ceil((g['x']+dx+g['art'].shape[1])/2))*2);top=max(0,int(np.floor((g['y']+dy)/2))*2);bottom=min(1080,int(np.ceil((g['y']+dy+g['art'].shape[0])/2))*2);wy,wx=np.mgrid[top:bottom:2,left:right:2];ks={b:map_coordinates(ar,[wy-g['y']-dy,wx-g['x']-dx],order=1,mode='constant',cval=0) for b,ar in blurs[g['id']].items()};state[g['id']]=dict(dx=dx,dy=dy,left=left,right=right,top=top,bottom=bottom,wx=wx,wy=wy,Ks=ks,**previous[g['id']])
 order=list(reversed(glyphs[:10]))+list(reversed(glyphs[10:]))
 for iteration in range(4):
  for g in order:
   z=state[g['id']];wx,wy=z['wx'],z['wy'];otherWhite=np.ones(wx.shape,np.float32)
   for h in glyphs:
    if h['id']==g['id']:continue
    o=state[h['id']]
    if o['opacity']<.0001 or o['right']<=z['left'] or o['left']>=z['right'] or o['bottom']<=z['top'] or o['top']>=z['bottom']:continue
    ar=blurs[h['id']][o['blur']];mask=map_coordinates(ar,[wy-h['y']-o['dy'],wx-h['x']-o['dx']],order=1,mode='constant',cval=0);otherWhite*=1-o['opacity']*mask
   target=targetFull[z['top']:z['bottom']:2,z['left']:z['right']:2];residual=target-(1-otherWhite);best=None
   for b,k in z['Ks'].items():
    v=otherWhite*k;den=float(np.sum(v*v));dot=float(np.sum(residual*v));a=float(np.clip(dot/max(.0001,den),0,1));cost=a*a*den-2*a*dot
    if best is None or cost<best[0]:best=(cost,b,a)
   z['blur']=best[1];z['opacity']=best[2]
 for g in glyphs:
  z=state[g['id']];row=dict(frame=f,dx=z['dx'],dy=z['dy'],blur=z['blur'],opacity=z['opacity']);g['history'].append(row);previous[g['id']]={k:row[k] for k in ['blur','opacity']}
 records.append(dict(frame=f,tracksDY=td['dy'],youDX=ud['dx'],youDY=ud['dy'],glyphs={g['id']:{k:state[g['id']][k] for k in ['opacity','blur']} for g in glyphs}));print('fit',f,flush=True)
nodes=[]
for g in glyphs:
 rows=g['history'];node=dict(type='path',id=g['id'],d=g['path'],fill='#000000',semanticText=g['letter'],start=846/30,end=891/30,keyframes={k:[dict(t=r['frame']/30,value=r[v],ease='linear') for r in rows] for k,v in [('x','dx'),('y','dy'),('opacity','opacity'),('blur','blur')]});nodes.append(node)
old=next(q for q in s['layers'] if q['id']=='g-1310');old['start']=old['end']=891/30;s['layers'].extend(nodes)
(D/'word-v19-measurements.json').write_text(json.dumps(dict(tracksCamera=tposes,youCamera=uposes,frames=records),indent=2));(D/'word-v19-patch.json').write_text(json.dumps(dict(replace={'g-1310':old},append=nodes),indent=2));(D/'scene-words-v19.json').write_text(json.dumps(s,indent=2)+'\n');print('wrote',len(nodes),'native glyphs')
