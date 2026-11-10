"""Identity-specific native affine cameras for separate, editable app cards.
Measurements contain genuine source-feature pose observations, not source frames.
"""
from pathlib import Path
import copy,json,sys,math,numpy as np
p=Path(__file__).parent;sys.path.insert(0,str(p.parent.parent/'engines'))
from render_pillow import state

def valid(q):
 if q.get('inliers',0)<25 or q.get('affineRms',99)>1.6:return False
 a=np.array(q['affine'])[:,:2];sv=np.linalg.svd(a,compute_uv=False)
 if np.linalg.det(a)<=0 or min(sv)<.18 or max(sv)>6 or max(sv)/min(sv)>1.35:return False
 xy=np.array(q['pointsFrom']);return np.linalg.eigvalsh(np.cov(xy.T)).min()>4

def trusted_frames(rows,index):
 good={r['frame'] for r in rows if valid(r['cards'][index])}
 return {f for f in good if f-1 in good or f+1 in good}

def decompose(M):
 U,sv,V=np.linalg.svd(M)
 if np.linalg.det(U)<0:U[:,-1]*=-1;sv[-1]*=-1
 if np.linalg.det(V)<0:V[-1,:]*=-1;sv[-1]*=-1
 return math.degrees(math.atan2(U[1,0],U[0,0])),float(sv[0]),float(sv[1]),math.degrees(math.atan2(V[1,0],V[0,0]))

def build_spec(scene,rows):
 grid=next(x for x in scene['layers'] if x['id']=='measured-collage-v13');cards=grid['children'];data={r['frame']:r for r in rows};spec={'startFrame':903,'endFrame':974,'cards':[],'diagnosis':'Footer-only observations lose identity/pose after the footer leaves the viewport. Independent source-feature cameras preserve each static app plane; native nested rotations represent full measured 2D affine transforms without scene rasterization.'}
 for i,c in enumerate(cards):
  base=state(c,31);track=[];accepted=[];allowed=trusted_frames(rows,i)
  for f in range(903,975):
   prior=state(c,f/30);q=data.get(f,{}).get('cards',[None]*20)[i]
   if q is not None and f in allowed:
    A=np.array(q['affine']);M=A[:,:2]@np.diag([base['scaleX'],base['scaleY']]);origin=A[:,:2]@np.array([base['x'],base['y']])+A[:,2];op=1.;method='source-features';accepted.append(f)
   else:M=np.diag([prior['scaleX'],prior['scaleY']]);origin=np.array([prior['x'],prior['y']]);op=0. if f>=947 else prior['opacity'];method='source-feature-disappearance' if f>=947 else 'unobserved-previous-native-prior'
   rotation,sx,sy,inner=decompose(M)
   track.append({'frame':f,'x':float(origin[0]),'y':float(origin[1]),'rotation':rotation,'scaleX':sx,'scaleY':sy,'innerRotation':inner,'opacity':op,'method':method,'inliers':q.get('inliers',0) if q else 0,'rms':q.get('affineRms') if q else None})
  # Equivalent SVD rotations can differ by180deg. Unwrap them for editable camera continuity.
  for name in ('rotation','innerRotation'):
   values=np.unwrap(np.radians([r[name] for r in track]));
   for r,v in zip(track,values):r[name]=float(np.degrees(v))
  spec['cards'].append({'index':i,'id':c['id'],'acceptedFrames':accepted,'track':track})
 art=p/'collage-v15-measure/art-refinements-working.json'
 if art.exists():spec['artRefinements']=json.loads(art.read_text())
 return spec

def apply_collage_cameras(scene,spec):
 scene=copy.deepcopy(scene);old=next(x for x in scene['layers'] if x['id']=='measured-collage-v13');old['end']=903/30
 new={'id':'native-affine-collage-cameras-v15','type':'group','start':903/30,'end':32.5,'children':[]}
 def reid(node):
  node['id']='v15-camera-'+node['id']
  for child in node.get('children',[]):reid(child)
 for q in spec['cards']:
  c=copy.deepcopy(old['children'][q['index']]);reid(c);c.pop('keyframes',None);c.update(x=0,y=0,rotation=0,scaleX=1,scaleY=1,opacity=1,start=903/30,end=32.5)
  art=next((a for a in spec.get('artRefinements',[]) if a['index']==q['index']),None)
  if art:
   interior=c['children'][1];image=next(x for x in reversed(interior['children']) if x['type']=='image');image.update(src=art['src'],height=art['height'],provenance={'kind':art['kind'],'observedArtCoverage':art['observedArtCoverage'],'provenanceFile':'assets/collage-art-v15/provenance.json'})
   if len(art.get('footerPaths',[]))==2:c['children']=c['children'][:2]+copy.deepcopy(art['footerPaths'])+c['children'][4:]
  c['keyframes']={'rotation':[{'t':r['frame']/30,'value':r['innerRotation'],'ease':'linear'} for r in q['track']]}
  wrapper={'id':f'collage-v15-native-affine-camera-{q["index"]}','type':'group','children':[c],'keyframes':{key:[{'t':r['frame']/30,'value':r[key],'ease':'linear'} for r in q['track']] for key in ('x','y','rotation','scaleX','scaleY','opacity')},'semanticAppIndex':q['index'],'measurementKind':'Bounded original artwork correspondence; native editable affine camera'}
  new['children'].append(wrapper)
 scene['layers'].insert(scene['layers'].index(old)+1,new)
 # The native eBay camera covers the same independently bounded card. Prevent the old partial-image poses doubling it.
 poses=next(x for x in scene['layers'] if x['id']=='measured-collage-projected-poses-v14')
 poses['children']=[x for x in poses['children'] if not x['id'].startswith('app-pose-ebay-')]
 scene['source']['notes']+=' CollageV15: separate static app artwork and native editable two-rotation affine camera per card, measured by identity-specific source-feature correspondence; weak/unobserved matches retain explicitly declared previous native priors. No full-frame/video playback. Internal bitmap UI remains declared.'
 return scene

if __name__=='__main__':
 src=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();scene=json.load(open(src));rows=json.load(open(p/'collage-v15-measure/source-feature-tracks.json'));spec=build_spec(scene,rows);(p/'collage-v15-measure/camera-spec-working.json').write_text(json.dumps(spec,indent=2));scene=apply_collage_cameras(scene,spec)
 def norm(n):
  if n.get('src') and not n['src'].startswith(('data:','http:','https:','/')):n['src']=str((src.parent/n['src']).resolve())
  for c in n.get('children',[]):norm(c)
 for x in scene['layers']:norm(x)
 for f in scene.get('fonts',[]):
  if f.get('src') and not f['src'].startswith(('data:','http:','https:','/')):f['src']=str((src.parent/f['src']).resolve())
 out.write_text(json.dumps(scene,indent=2));print('accepted',sum(len(x['acceptedFrames']) for x in spec['cards']),'of',20*72)
