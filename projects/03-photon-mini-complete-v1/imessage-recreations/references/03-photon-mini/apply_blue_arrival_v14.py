from pathlib import Path
import copy,json
P=Path(__file__).parent

def sample(track,t):
 if t<=track[0]['t']:return track[0]['value']
 for a,b in zip(track,track[1:]):
  if t<=b['t']:
   p=(t-a['t'])/(b['t']-a['t']);ease=b.get('ease','linear')
   if ease=='easeOut':p=1-(1-p)**3
   elif ease=='easeInOut':p=4*p**3 if p<.5 else 1-(-2*p+2)**3/2
   return a['value']+(b['value']-a['value'])*p
 return track[-1]['value']

def apply_blue(scene):
 s=copy.deepcopy(scene);root=next(x for x in s['layers'] if x['id']=='p03-204');bubble=next(x for x in root['children'] if x['id']=='p03-128');records=json.loads((P/'lunch-blue-v14-measurements.json').read_text());keys={k:[] for k in ['x','y','scaleX','scaleY','opacity','blur']}
 for r in records:
  f=r['frame'];q=r['blue']
  if not q:continue
  t=f/30;cam={k:sample(root['keyframes'][k],t) for k in ['x','y','scaleX','scaleY']};x,y,x2,y2=q['bbox'];h=90 if f==509 else q['h'];v={'x':(x-cam['x'])/cam['scaleX'],'y':(y-cam['y'])/cam['scaleY'],'scaleX':q['w']/309/cam['scaleX'],'scaleY':h/86/cam['scaleY'],'opacity':.82 if f==509 else 1,'blur':1 if f==509 else 0}
  for k in keys:keys[k].append({'t':t,'value':v[k],'ease':'linear'})
 bubble['start']=509/30;bubble['keyframes']=keys
 for c in bubble['children']:
  if c.get('fill')=='url(#blue)':c['fill']='url(#lunch-blue-v14)'
 s['gradients']=[x for x in s.get('gradients',[]) if x['id']!='lunch-blue-v14'];s['gradients'].append({'id':'lunch-blue-v14','type':'linear','x1':'0%','y1':'0%','x2':'0%','y2':'100%','stops':[{'offset':'0%','color':'#4eb7f5'},{'offset':'100%','color':'#1f98f3'}]});s['lunch_blue_v14']={'scope':[509,617],'notice':'Measured native outgoing bubble birth/flight/width/height independently from unchanged phone/UI camera. Original source gradient fit is vertical; former scene gradient was horizontal. Frame509 is bottom-censored and uses neighboring full height, measured opening opacity approximation. Text remains live SF Pro Text.'};return s
if __name__=='__main__':
 s=json.loads((P/'joint-v14-provisional.scene.json').read_text());s=apply_blue(s);(P/'blue-arrival-v14.scene.json').write_text(json.dumps(s,indent=2))
