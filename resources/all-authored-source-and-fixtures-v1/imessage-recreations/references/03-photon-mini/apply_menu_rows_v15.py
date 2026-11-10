"""Apply independent measured motion to six bounded static rich-app UI rows."""
from pathlib import Path
import copy,json,math,numpy as np
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent

def apply_rows(scene):
 s=copy.deepcopy(scene);assets=json.loads((P/'menu-rows-v15/assets.json').read_text())['rows'];frames=json.loads((P/'menu-rows-v15/measurements.json').read_text())['frames'];clip=next(x for x in s['layers'] if x['id']=='measured-menu-clip-v13');menu=clip['children'][0];body=next(x for x in menu['children'] if x['id']=='menu13-p03-202');proof=[];groups=[]
 for i,asset in enumerate(assets):
  observations=[(r['frame'],next(q for q in r['rows'] if q['row']==i)) for r in frames];observations=[(f,q) for f,q in observations if q['status']=='measured'];first=observations[0][0];row=body['children'][i];old=copy.deepcopy(row.get('keyframes',{}).get('opacity',[{'t':0,'value':row.get('opacity',1)}]));new=[q for q in old if q['t']<first/30];new.append({'t':first/30,'value':0,'ease':'hold'});new.append({'t':730/30,'value':sample(old,730/30),'ease':'hold'});new.extend(q for q in old if q['t']>730/30);row.setdefault('keyframes',{})['opacity']=new
  keys={k:[] for k in ['x','y','rotation','scaleX','scaleY','opacity']};inner=[]
  for f,q in observations:
   M=np.array(q['matrix'],dtype='float64');U,D,V=np.linalg.svd(M[:,:2])
   if np.linalg.det(U)<0:U[:,1]*=-1;D[1]*=-1
   if np.linalg.det(V)<0:V[1,:]*=-1;D[1]*=-1
   angle=lambda a:math.degrees(math.atan2(a[1,0],a[0,0]));values={'x':M[0,2],'y':M[1,2],'rotation':angle(U),'scaleX':D[0],'scaleY':D[1],'opacity':q['opacity']}
   for k in keys:keys[k].append({'t':f/30,'value':float(values[k]),'ease':'hold'})
   inner.append({'t':f/30,'value':angle(V),'ease':'hold'});proof.append({'frame':f,'row':i,'max_affine_recomposition_error':float(np.max(abs(U@np.diag(D)@V-M[:,:2]))),'source_inliers':q['inliers'],'source_inlier_RMS':q['inlier_RMS']})
  groups.append({'id':f'measured-menu-row-{i}-v15','type':'group','start':first/30,'end':730/30,'keyframes':keys,'children':[{'id':f'menu-row-{i}-inner-v15','type':'group','keyframes':{'rotation':inner},'children':[{'id':f'menu-row-{i}-art-v15','type':'image','src':asset['asset'],'width':asset['dimensions'][0],'height':asset['dimensions'][1],'semanticText':asset['name'],'provenance':{'source_frame':asset['source_frame'],'source_crop':asset['source_crop'],'kind':'Separate static rich-app UI row artwork','notice':asset['editability']}}]}]})
 outer={k:copy.deepcopy(v) for k,v in clip.items() if k not in ['children','id','start','end']};outer.update(id='measured-menu-row-art-clip-v15',start=618/30,end=730/30);inverse={k:[] for k in ['x','y','scaleX','scaleY']}
 for f in range(618,730):
  t=f/30;v={k:sample(clip['keyframes'][k],t) for k in inverse};values={'x':-v['x']/v['scaleX'],'y':-v['y']/v['scaleY'],'scaleX':1/v['scaleX'],'scaleY':1/v['scaleY']}
  for k in inverse:inverse[k].append({'t':t,'value':values[k],'ease':'hold'})
 outer['children']=[{'id':'menu-row-world-coordinates-v15','type':'group','keyframes':inverse,'children':groups}];s['layers']=[l for l in s['layers'] if l['id']!='measured-menu-row-art-clip-v15'];index=next((i for i,l in enumerate(s['layers']) if l['id'].startswith('root-backplane-stencil-')),next(i for i,l in enumerate(s['layers']) if l['id']=='measured-lunch-bezel-overlay-v13'));s['layers'].insert(index,outer);s['menu_row_foreground_v15']={'scope':[618,729],'assets':6,'notice':'Six separately cropped static rich-app UI rows, each under independently source-measured native affine motion/opacity. Internal row labels/prices/descriptions/photos/originalplus controls are bitmap artwork. Outer panel/header/physicalcamera/hardware/cart/selection actors stay native and separate. Original native vector rows remain as a gated fallback and restore exactly at730. No fullframe, sourcevideo or per-frame row playback.','affine_proof':proof};return s
if __name__=='__main__':
 s=json.loads((P/'final-v14.scene.json').read_text());s=apply_rows(s);(P/'menu-rows-v15.scene.json').write_text(json.dumps(s,indent=2));print('built',len(s['menu_row_foreground_v15']['affine_proof']),'row poses')
