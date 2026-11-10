"""Read-only exact active-branch audit for separated native shadow/opacity.
Zero entries prove compatibility; nonzero scopes conservatively include offscreen
or fully occluded actors, because their native branch still changes.
"""
from pathlib import Path
import sys,json,hashlib
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'engines'));from render_pillow import state

def audit(scene):
 def relevant(n):return bool(n.get('shadow')) or any(relevant(c) for c in n.get('children',[]))
 def prune(n):return {**n,'children':[prune(c) for c in n.get('children',[]) if relevant(c)]}
 tree=[prune(n) for n in scene['layers'] if relevant(n)];frames=[]
 for f in range(round(scene['duration']*scene['fps'])):
  t=f/scene['fps'];hits=[]
  def walk(n):
   s=state(n,t)
   if not(s.get('start',0)<=t<s.get('end',scene['duration'])) or s['opacity']<=0:return
   if s.get('shadow') and s['opacity']<1:hits.append({'id':n['id'],'opacity':s['opacity']})
   for c in n.get('children',[]):walk(c)
  for n in tree:walk(n)
  if hits:frames.append({'frame':f,'nodes':hits})
 ranges=[]
 for r in frames:
  f=r['frame']
  if ranges and ranges[-1][1]==f-1:ranges[-1][1]=f
  else:ranges.append([f,f])
 return {'affectedBranchFrames':len(frames),'ranges':ranges,'frames':frames}

if __name__=='__main__':
 rows=[]
 for name in ('01-photonhq','02-danieltian','03-photon-mini','04-poke','05-linq','06-gallery'):
  path=root/f'outputs/{name}/motion-canvas.mp4.render.json';m=json.load(open(path));scene=json.load(open(m['scene']));rec={'reference':name,'scene':m['scene'],'sceneSha256':m['sceneSha256'],'captureEngineSha256':m['engineSha256'],**audit(scene)};rows.append(rec);print(name,rec['affectedBranchFrames'],rec['ranges'],flush=True)
 (Path(__file__).parent/'capture-audit.json').write_text(json.dumps({'condition':'Visible ancestor lifecycle and0<same-node opacity<1 with authored shadow; exact changed native branch. Offscreen/occluded instances included conservatively.','captures':rows},indent=2)+'\n')
