"""Scoped measured SMS coverage/reveal and mail camera repairs against V8."""
from pathlib import Path
import copy,json,math
import numpy as np
p=Path(__file__).parent

def affine_components(M):
 U,s,V=np.linalg.svd(np.array(M,dtype=float)/2)
 if np.linalg.det(U)<0:U[:,-1]*=-1;s[-1]*=-1
 if np.linalg.det(V)<0:V[-1,:]*=-1;s[-1]*=-1
 ua=math.degrees(math.atan2(U[1,0],U[0,0]));va=math.degrees(math.atan2(V[1,0],V[0,0]));candidates=[]
 for turn in range(-4,5):
  angle=90*turn;scales=s[::-1] if turn%2 else s
  candidates.append((abs(ua+angle)+abs(va-angle),ua+angle,float(scales[0]),float(scales[1]),va-angle))
 _,a,sx,sy,b=min(candidates,key=lambda q:q[0]);return a,sx,sy,b

def opacity_gate(layer,frames):
 assert not layer.get('keyframes',{}).get('opacity'),'Expected opaque V8 mail base'
 frames=set(frames);keys=[{'t':0,'value':1}];last=1
 for f in range(min(frames),max(frames)+2):
  value=0 if f in frames else 1
  if value!=last:keys.append({'t':f/30,'value':value,'ease':'hold'});last=value
 layer.setdefault('keyframes',{})['opacity']=keys

def apply_v9_repairs(scene,sms=None,mail=None):
 scene=copy.deepcopy(scene);sms=sms or json.load(open(p/'v9-repair/sms-spec-frozen-v9.json'));mail=mail or json.load(open(p/'v9-repair/mail-spec-frozen-v9.json'));byid={n['id']:n for n in scene['layers']};byid[sms['numericOriginalId']]['start']=sms['numericOriginalResume'];scene['layers'].extend(copy.deepcopy(sms['materialNodes'])+copy.deepcopy(sms['numericNodes']));gated={};added=[]
 if sms.get('alphaRepair'):
  repair=sms['alphaRepair'];original=byid[repair['originalId']];clone=copy.deepcopy(original);clone.update(id='v9-sms-alpha-restored-card',src=repair['src'],start=repair['frames'][0]/30,end=(repair['frames'][1]+1)/30,provenance=repair);opacity_gate(original,range(repair['frames'][0],repair['frames'][1]+1));scene['layers'].append(clone)
 for id,frames in sms.get('replacementScopes',{}).items():opacity_gate(byid[id],frames)
 for pose in mail['poses']:
  original=byid[pose['originalId']];frame=pose['frame'];assert frame!=300 and (297<=frame<=314);gated.setdefault(original['id'],[]).append(frame);image=copy.deepcopy(original);image['id']=f'v9-mail-art-{frame}-{original["id"]}';image['start']=frame/30;image['end']=(frame+1)/30;image['opacity']=1;image.pop('keyframes',None);image['provenance']={'kind':'Existing authentic static mail artwork with measured content affine camera; bitmap internal UI copy.','sourceNativeFrame':frame,'frontArtworkId':original['id'],'measuredLocalMatrix':pose['measuredLocalMatrix'],'ecc':pose['ecc']};M=np.array(pose['matrixWorld']);origin=pose['originWorld']
  if pose['mode']=='axis-affine':
   image.update(x=origin[0],y=origin[1],scaleX=float(M[0,0]),scaleY=float(M[1,1]),rotation=0);added.append(image)
  else:
   a,sx,sy,b=affine_components(M);image.update(x=0,y=0,scaleX=1,scaleY=1,rotation=b,width=original['width']*2,height=original['height']*2,authoringUnitsPerCanvasUnit=2)
   added.append({'id':f'v9-mail-camera-{frame}-{original["id"]}','type':'group','x':origin[0],'y':origin[1],'rotation':a,'scaleX':sx,'scaleY':sy,'start':frame/30,'end':(frame+1)/30,'children':[image],'measurementKind':'Observed source-content affine, represented by native rotations/scales; original static artwork retained'})
 for id,frames in gated.items():opacity_gate(byid[id],frames)
 scene['layers'].extend(added);scene['source']['notes']+=' V9 measured250–259 SMS repair replaces only six individually bounded incomplete SMS card actors with observed component poses during the short3D entrance; internal glyph/corner lighting is explicitly bitmap, while native card box/camera/lifecycle remain editable;250–257 rolling numeric states are native semantic alpha-contour paths and258+ original copy is preserved. Mail297–299/301–314 uses actual per-card affine content registration of existing authentic static artwork, represented by native transforms, with300 held exactly. Weak/nonimproving fits retain original artwork/camera. Bitmap UI internals remain declared; no full-frame or video playback.'
 return scene,{'sourceScope':[[250,259],[297,299],[301,314]],'preservedFrames':[260,300],'smsMaterialAssets':len(sms['materialNodes']),'numericStates':len(sms['numericNodes']),'mailPoses':len(added),'mailActors':len(gated)}

if __name__=='__main__':
 import sys
 src=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();scene,report=apply_v9_repairs(json.load(open(src)))
 def normalize(n):
  if n.get('src') and not n['src'].startswith(('data:','http:','https:','/')):n['src']=str((src.parent/n['src']).resolve())
  for c in n.get('children',[]):normalize(c)
 for n in scene['layers']:normalize(n)
 out.write_text(json.dumps(scene,indent=2)+'\n');(out.parent/'candidate-scope.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)
