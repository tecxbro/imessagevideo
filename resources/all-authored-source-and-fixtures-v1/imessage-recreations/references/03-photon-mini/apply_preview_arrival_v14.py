from pathlib import Path
import copy,json,numpy as np,math,hashlib
from apply_blue_arrival_v14 import sample
P=Path(__file__).parent

def apply_preview(scene):
 s=copy.deepcopy(scene);root=next(x for x in s['layers'] if x['id']=='p03-204');card=next(x for x in root['children'] if x['id']=='p03-148');ledger=P/'food-preview-native-measure/preview-arrival-affine-measurements.json';data=json.loads(ledger.read_text());keys={k:[] for k in ['x','y','scaleX','scaleY','rotation','opacity','blur']};innerkeys=[];proof=[]
 for r in data['frames']:
  f=r['frame'];t=f/30;cam={k:sample(root['keyframes'][k],t) for k in ['x','y','scaleX','scaleY']};M=np.array(r.get('nativeChildLocalMatrix',r['matrix']),dtype='float64')
  if 'nativeChildLocalMatrix' not in r:M[:,:2]@=np.diag([523/520,277/274.7721179624665])
  A=np.diag([1/cam['scaleX'],1/cam['scaleY']])@M[:,:2];v=(M[:,2]-[cam['x'],cam['y']])/[cam['scaleX'],cam['scaleY']];U,D,V=np.linalg.svd(A)
  if np.linalg.det(U)<0:U[:,1]*=-1;D[1]*=-1
  if np.linalg.det(V)<0:V[1,:]*=-1;D[1]*=-1
  angle=lambda q:math.degrees(math.atan2(q[1,0],q[0,0]));vals={'x':float(v[0]),'y':float(v[1]),'scaleX':float(D[0]),'scaleY':float(D[1]),'rotation':angle(U),'opacity':r['opacity'],'blur':r.get('estimatedSourceBlur',0)/math.sqrt(cam['scaleX']*cam['scaleY'])}
  for k in keys:keys[k].append({'t':t,'value':vals[k],'ease':'hold'})
  innerkeys.append({'t':t,'value':angle(V),'ease':'hold'});proof.append({'frame':f,'world_matrix':M.tolist(),'recomposition_max_error':float(np.max(abs(U@np.diag(D)@V-A)))})
 # The settled legacy card after567 is deliberately preserved.
 t=567/30;old={'x':card.get('x',0),'y':sample(card['keyframes']['y'],t),'scaleX':card['scaleX'],'scaleY':card['scaleY'],'rotation':0,'opacity':1,'blur':0}
 for k in keys:keys[k].append({'t':t,'value':old[k],'ease':'hold'})
 innerkeys.append({'t':t,'value':0,'ease':'hold'});card['start']=546/30;card['keyframes']=keys;card['children']=[{'id':'measured-preview-inner-affine-v14','type':'group','keyframes':{'rotation':innerkeys},'children':card['children']}];s['preview_arrival_v14']={'scope':[546,566],'ledger_sha256':hashlib.sha256(ledger.read_bytes()).hexdigest(),'notice':'Authentic separate static app-art asset remains unchanged. Independently measured arrival world affine is decomposed into native two-rotation/scales for complete editable card geometry/copy. Tiny546 is bounded opticalfit with declared uncertainty;547–566 are highconfidence image-featurefits. Original settledcard state567+ is preserved.','affine_proof':proof};return s
if __name__=='__main__':
 s=json.loads((P/'blue-arrival-v14.scene.json').read_text());s=apply_preview(s);(P/'preview-arrival-v14.scene.json').write_text(json.dumps(s,indent=2))
