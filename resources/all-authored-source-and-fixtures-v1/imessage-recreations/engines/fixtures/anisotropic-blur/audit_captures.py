"""Read-only audit of captures affected by a local-space blur correction."""
from pathlib import Path
import sys,json,numpy as np
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'engines'))
from render_pillow import state,matrix

def audit(scene):
 def relevant(n):
  return bool(n.get('blur',0)) or any(bool(k['value']) for k in n.get('keyframes',{}).get('blur',[])) or any(relevant(c) for c in n.get('children',[]))
 def prune(n):
  return {**n,'children':[prune(c) for c in n.get('children',[]) if relevant(c)]}
 tree=[prune(n) for n in scene['layers'] if relevant(n)];affected=[];details=[]
 for frame in range(round(scene['fps']*scene['duration'])):
  t=frame/scene['fps'];hits=[]
  def walk(n,parent):
   s=state(n,t)
   if t<s.get('start',0) or t>=s.get('end',scene['duration']) or s['opacity']<=0:return
   M=parent@matrix(s)
   if s.get('blur',0):
    a,b=M[:2,0],M[:2,1];sx,sy=np.linalg.norm(a),np.linalg.norm(b)
    if abs(sx-sy)>1e-6*max(sx,sy) or abs(a@b)>1e-6*sx*sy:hits.append(n['id'])
   for c in n.get('children',[]):walk(c,M)
  for n in tree:walk(n,np.eye(3))
  if hits:affected.append(frame);details.append({'frame':frame,'ids':hits})
 ranges=[]
 for f in affected:
  if ranges and ranges[-1][1]==f-1:ranges[-1][1]=f
  else:ranges.append([f,f])
 return {'affectedFrames':len(affected),'ranges':ranges,'frames':details}

if __name__=='__main__':
 rows=[]
 for name in ('01-photonhq','02-danieltian','03-photon-mini','04-poke','05-linq','06-gallery'):
  meta=json.load(open(root/f'outputs/{name}/motion-canvas.mp4.render.json'));scene=json.load(open(meta['scene']));r={'reference':name,'scene':meta['scene'],'sceneSha256':meta['sceneSha256'],'captureEngineSha256':meta['engineSha256'],**audit(scene)};rows.append(r);print(name,r['ranges'],flush=True)
 (Path(__file__).parent/'capture-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
