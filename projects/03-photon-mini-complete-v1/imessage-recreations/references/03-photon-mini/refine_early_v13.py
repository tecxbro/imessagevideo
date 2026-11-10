"""Apply measured early-device/UI trajectories to a source03 authoring scene.
Does not mutate canonical inputs or render full videos. Stable IDs support merges.
"""
from pathlib import Path
import json,copy,sys,hashlib
import numpy as np
from PIL import Image
from scipy import signal,ndimage
P=Path(__file__).parent;B=P/'early-v13-measure';sys.path.insert(0,str(P.parents[1]/'engines'));from render_pillow import state

def keys(values):return [{'t':f/30,'value':float(v),'ease':'linear'}for f,v in values]
def blue_components(im):
 a=np.asarray(im).astype(float);blue=(a[:,:,2]>90)&(a[:,:,2]-a[:,:,0]>35)&(a[:,:,1]>35)&(a[:,:,2]-a[:,:,1]>8);labels,n=ndimage.label(blue);out=[]
 for i,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  y,x=sl;w=x.stop-x.start;h=y.stop-y.start;area=(labels[sl]==i).sum()
  if area>25:out.append(dict(x=x.start*2,y=y.start*2,w=w*2,h=h*2,ratio=w/h,area=int(area),fill=float(area/(w*h))))
 return out

def measured_data():
 records=json.loads((B/'camera-fit-hardware-y.json').read_text());poses={}
 for r in records:
  f=r['frame'];s=r['scale'];x=r['x'];y=r['hardwareY']
  if r['cost']>20 or 343<=f<=357:s=(r['right']-r['left'])/768*1.002;x=(r['left']+r['right'])/2-400*s
  if 310<=f<=334:
   s=float(np.interp(f,[310,311,312,313,314,334],[2.2,2.222,2.208,2.199,2.194,2.194]));x=r['right']-784*s
   a=np.asarray(Image.open(B/'source'/f'{f-48:04d}.png').convert('L'));y=float(np.where(a<75)[0].min()*2-12*s)
  elif f<310 or f>=335:x=960-400*s
  poses[f]={'scale':s,'x':x,'y':y}
 # Device motion is continuous within shots; denoise 2px half-resolution sample
 # quantization without smoothing across the source's hard send-camera cuts.
 for f in range(59,111):poses[f]['y']=next(r['y'] for r in records if r['frame']==f)
 for first,last in [(59,110),(111,177),(178,210),(211,309),(310,334),(335,350),(351,413)]:
  fs=list(range(first,last+1));v=np.array([poses[f]['y']for f in fs]);win=min(9,len(v)//2*2-1);smooth=signal.savgol_filter(v,win,2) if win>=5 else v
  for f,y in zip(fs,smooth):poses[f]['y']=float(y)
 return records,poses

def apply_early(scene):
 scene=copy.deepcopy(scene);by={}
 def walk(ls):
  for l in ls:by[l['id']]=l;walk(l.get('children',[]))
 walk(scene['layers']);phone=by['p03-86'];records,poses=measured_data();UI={}
 for f in poses:
  if f<=210:sc=1;uy=0
  elif f<=220:sc=float(np.interp(f,[210,214,215,216,217,218,219,220],[1,.98,.94,.94,.94,.94,.94,.94]));uy=float(np.interp(f,[210,214,215,216,217,218,219,220],[0,40,75,80,90,98,100,105]))
  elif f<=354:sc=.94;uy=105
  else:sc=float(np.interp(f,[354,370],[.94,1]));uy=float(np.interp(f,[354,370],[105,0]))
  UI[f]={'scale':sc,'x':400*(1-sc),'y':uy}
 phone['start']=59/30;phone['keyframes']={k:keys([(f,p['scale'] if k.startswith('scale') else p[k])for f,p in poses.items()])for k in ['x','y','scaleX','scaleY']}
 # Separate the physical device, the Messages UI and the independently moving
 # email sheet. Global lifecycle values remain native-frame exact.
 hardware=phone['children'][:6];sheet=by['p03-77'];ui=[l for l in phone['children'][6:] if l['id']!='p03-77'];group={'id':'early-messages-ui-v13','type':'group','children':ui,'keyframes':{k:keys([(f,u['scale'] if k.startswith('scale') else u[k])for f,u in UI.items()])for k in ['x','y','scaleX','scaleY']}}
 dim_values={f:0 for f in poses}
 for f in poses:
  if 211<=f<=224:
   a=np.asarray(Image.open(B/'source'/f'{f-48:04d}.png'));dim_values[f]=float(np.clip(1-np.median(a[10:40,370:420,:3])/252,0,.4))
  elif 225<=f<=355:dim_values[f]=.4
  elif 356<=f<=370:
   a=np.asarray(Image.open(B/'source'/f'{f-48:04d}.png'));dim_values[f]=float(np.clip(1-float(a[500,480,:3].mean())/252,0,.4))
 dim={'id':'early-mail-backdrop-v13','type':'rect','x':29,'y':25,'width':742,'height':1608,'radius':120,'fill':'#000000','keyframes':{'opacity':keys(list(dim_values.items()))}}
 phone['children']=hardware+[group,dim,sheet];sheet['children']=[l for l in sheet['children'] if l['id']!='p03-51'];black=copy.deepcopy(by['p03-51']);black['id']='early-email-black-backplate-v13';black['keyframes']={'opacity':keys([(212,0),(225,0),(230,1),(354,1),(355,0)])};phone['children']=hardware[:3]+[group,dim,black]+hardware[3:]+[sheet];by['p03-52']['keyframes']={'opacity':keys([(212,0),(225,0),(230,1)])};by['p03-52']['y']=164;by['p03-52']['height']=100;by['p03-53']['fill']='#fcfcfc';sheet['start']=212/30;sheet['end']=355/30
 for child in sheet['children']:
  if child['id'] not in ['p03-51','p03-52']:child['end']=min(child.get('end',345/30),345/30)
 # Accurate first-phone header fade, independent of the device chrome.
 for identifier in ['p03-14','p03-15','p03-16','p03-17','p03-18','p03-19','p03-21','p03-22']:
  l=by[identifier];l.setdefault('keyframes',{})['opacity']=keys([(59,.2),(60,.55),(61,.85),(63,1)])
 # Full source outgoing/card components are independently projected into the
 # Messages UI; this recovers real arrivals instead of moving all content via
 # the hardware camera.
 btracks={k:[]for k in ['x','y','scaleX','scaleY']};ctracks={k:[]for k in btracks};pane={k:[]for k in ['x','y']};button=[];measurements=[]
 for f,p in poses.items():
  im=Image.open(B/'source'/f'{f-48:04d}.png').convert('RGB');comps=blue_components(im);u=UI[f];s=p['scale'];baseX=p['x'];baseY=p['y'];bubble=[b for b in comps if 3.5<b['ratio']<5.5 and b['w']>150];cards=[b for b in comps if b['w']>100 and b['x']<baseX+150*s];circles=[b for b in comps if .8<b['ratio']<1.2 and b['w']>20 and b['h']>20 and b['fill']>.5]
  for target,candidates,denom in [(btracks,bubble,518),(ctracks,cards,517)]:
   if not candidates or 214<=f<=357:continue
   b=max(candidates,key=lambda b:b['area']);sc=b['w']/(denom*s*u['scale']);lx=((b['x']-baseX)/s-u['x'])/u['scale'];ly=((b['y']-baseY)/s-u['y'])/u['scale']
   for k,v in [('x',lx),('y',ly),('scaleX',sc),('scaleY',sc)]:target[k].append((f,v))
  if 214<=f<=344 and circles:
   c=max(circles,key=lambda b:b['area']);cx=c['x']+c['w']/2;cy=c['y']+c['h']/2;pane['x'].append((f,(cx-baseX)/s-697));pane['y'].append((f,(cy-baseY)/s-271));button.append((f,((c['w']+c['h'])/2+1)/(78*s)))
  measurements.append({'frame':f,'camera':p,'messages_ui':u,'components':comps})
 for identifier,tracks in [('p03-27',btracks),('p03-50',ctracks)]:
  l=by[identifier];l['end']=13.8;l['keyframes']={k:keys(v)for k,v in tracks.items()};l['keyframes']['opacity']=keys([(f,1)for f,_ in tracks['x']]);l['start']=tracks['x'][0][0]/30
 by['p03-35']['end']=13.8
 # The native pane/control/text persists until the localized perspective exit.
 pane['x']=[(212,pane['x'][0][1])]+pane['x'];pane['y']=[(212,1600),(213,1200)]+pane['y'];sheet['keyframes']={k:keys(v)for k,v in pane.items()};arrow=by['p03-59'];arrow['originX']=39;arrow['originY']=39;arrow['keyframes']={'scaleX':keys(button),'scaleY':keys(button)}
 # Original native glyph outlines preserve staggered reveals and clipped exits;
 # two colored icon components remain explicitly bounded bitmap artwork.
 scene['layers']=[l for l in scene['layers'] if l['id']not in ['p03-1','p03-7']];intro=json.loads((B/'intro-native-layers.json').read_text());plates=[]
 for f,w,h,cy in [(52,1800,340,535),(53,1700,330,535),(54,1540,300,535),(55,1260,260,528),(56,950,220,514),(57,700,180,493),(58,510,144,466)]:
  plates.append({'id':f'early-header-morph-v13-{f}','type':'rect','x':960-w/2,'y':cy-h/2,'width':w,'height':h,'radius':h/2,'fill':'#fcfcfc','stroke':'#f1f1f1','strokeWidth':1,'shadow':{'x':0,'y':5,'blur':6,'color':'#0000000d'},'start':f/30,'end':(f+1)/30})
 scene['layers']=plates+intro+scene['layers'];exits=json.loads((B/'email-exit-artwork-provenance.json').read_text())['records'];sprites=[]
 for r in exits:
  x,y,x2,y2=r['bounds'];f=r['source_frame'];sprites.append({'id':f'early-email-perspective-v13-{f}','type':'image','src':r['asset'],'x':x,'y':y,'width':x2-x,'height':y2-y,'start':f/30,'end':(f+1)/30,'semanticText':'Dinner This Week email editor exit','bitmapLimitation':r['editability']})
 index=next(i for i,l in enumerate(scene['layers']) if l['id']=='p03-86');scene['layers'][index+1:index+1]=sprites
 # Replace measured static component skins while retaining the native motion
 # containers. These remove the diagnosed placeholder logo, type and tail gaps.
 skins=json.loads((B/'message-skin-geometry.json').read_text())
 def skin_node(name,identifier,**extra):return {'id':identifier,'type':'image',**copy.deepcopy(skins[name]),**extra}
 by['p03-27']['children']=[skin_node('blue-draft','early-blue-original-skin-v13')];by['p03-27']['semanticText']='Draft an email to Alice about our dinner.';by['p03-27']['bitmapLimitation']='Original static message UI copy/gradient is bitmap; independent native arrival/camera/opacity remain editable.'
 by['p03-50']['children']=[skin_node('mail-pre','early-mail-pre-skin-v13',end=354/30),skin_node('mail-pressed','early-mail-pressed-skin-v13',start=205/30,end=214/30,keyframes={'opacity':keys([(205,1),(208,1),(214,0)])}),skin_node('mail-post','early-mail-post-skin-v13',start=354/30)];by['p03-50']['semanticText']='Mail · To: Alice';by['p03-50']['bitmapLimitation']='Original static card UI and pressed state are bounded bitmap components; native card motion/scale/lifetimes remain editable.'
 for identifier,name in [('p03-35','working'),('p03-81','sent'),('p03-85','reply')]:
  layer=by[identifier];g=skins[name];old_y=layer.get('y',0);layer['x']=g['x'];layer['y']=g['y'];layer['children']=[{'id':'early-original-'+name+'-skin-v13','type':'image','src':g['src'],'x':0,'y':0,'width':g['width'],'height':g['height']}];layer['semanticText']={'working':'Working on it.','sent':'Sent.','reply':"I'll let you know when she replies."}[name];layer['bitmapLimitation']='Internal static UI copy/shape is bitmap; native arrival, pose and opacity remain independently editable.'
  for k in layer.get('keyframes',{}).get('y',[]):k['value']+=g['y']-old_y
  if name=='sent':
   layer['start']=356/30;layer['originY']=g['height']/2;layer['keyframes']={'opacity':keys([(356,0),(358,.15),(360,.45),(364,.95),(366,1)]),'y':keys([(356,g['y']+90),(358,g['y']+70),(360,g['y']+35),(364,g['y']+5),(366,g['y'])]),'scaleX':keys([(356,.05),(358,.15),(360,.35),(362,.7),(364,.9),(366,1)]),'scaleY':keys([(356,.05),(358,.15),(360,.35),(362,.7),(364,.9),(366,1)])}
  elif name=='reply':
   layer['start']=372/30;layer['originY']=g['height']/2;layer['keyframes']={'opacity':keys([(372,0),(374,.5),(376,.9),(378,1)]),'y':keys([(372,g['y']+40),(374,g['y']+20),(378,g['y'])]),'scaleX':keys([(372,.05),(374,.4),(376,.8),(378,1)]),'scaleY':keys([(372,.05),(374,.4),(376,.8),(378,1)])}
 for identifier,replacement in json.loads((B/'pane-outline-replacements.json').read_text()).items():
  node=by[identifier];node.clear();node.update(copy.deepcopy(replacement))
 # Source send-camera hardware uses a thinner original ring than the generic
 # whole-device texture. Keep only actual ring/sensor pixels, with a separate
 # native silhouette. The pane/UI is excluded from these bounded assets.
 hw=json.loads((B/'send-hardware-geometry.json').read_text());hide=keys([(59,1),(309,1),(310,0),(334,0),(335,1)])
 for node in hardware:node.setdefault('keyframes',{})['opacity']=copy.deepcopy(hide)
 body={'id':'early-send-native-silhouette-v13','type':'path','d':hw['silhouette_path'],'fill':'#000000',**hw['path_transform'],'start':310/30,'end':335/30}
 ring={'id':'early-send-original-ring-v13','type':'image',**hw['ring'],'start':310/30,'end':335/30,'bitmapLimitation':'Only thin original hardware ring pixels; no internal UI.'}
 sensor={'id':'early-send-original-sensor-v13','type':'image',**hw['sensor'],'start':310/30,'end':335/30,'bitmapLimitation':'Original physical sensor-island texture only.'}
 phone['children'].insert(3,body);phone['children'].insert(4,ring);phone['children'].insert(-1,sensor)
 black['keyframes']['opacity']=keys([(212,0),(225,0),(230,1),(309,1),(310,0),(334,0),(335,1),(354,1),(355,0)])
 by['p03-53'].setdefault('keyframes',{})['opacity']=keys([(212,1),(309,1),(310,0),(334,0),(335,1)]);pane_shape={'id':'early-native-continuous-pane-v13','type':'path','d':hw['pane_path'],'fill':'#fcfcfc',**hw['pane_transform'],'start':310/30,'end':335/30};sheet['children'].insert(2,pane_shape)
 by['p03-52'].setdefault('keyframes',{})['fill']=[{'t':212/30,'value':'#858585'},{'t':309/30,'value':'#808080','ease':'linear'},{'t':334/30,'value':'#808080'},{'t':335/30,'value':'#858585'}]
 by['p03-60'].setdefault('keyframes',{})['opacity']=keys([(212,1),(309,1),(310,0),(334,0),(335,1)]);close_title={'id':'early-native-closeup-title-v13','type':'path','d':hw['closeup_title_path'],'fill':'#000000',**hw['pane_transform'],'start':310/30,'end':335/30,'semanticText':'Dinner This Week (visible portion)','editableAs':'native original glyph outlines'};sheet['children'].append(close_title)
 scene['source']['notes']+=' Earlyv13: original native intro glyph poses, separate header morph, measured hardware camera and MessagesUI motion, projected bubble/card arrivals, sheet birth/rise and localized bounded pane perspective exit; device/camera/backdrop remain native. Internal message/card/icon/pane pixels and thin hardware lighting are bitmap; semantic original intro/email text glyphs are native editable outlines.'
 return scene,measurements

if __name__=='__main__':
 base=Path(sys.argv[1]) if len(sys.argv)>1 else P/'final-v12.scene.json';scene,measurements=apply_early(json.loads(base.read_text()));out=P/'early-v13.scene.json';out.write_text(json.dumps(scene,indent=2)+'\n');(B/'component-measurements.json').write_text(json.dumps(measurements,indent=2)+'\n');(P/'early-v13-scope.json').write_text(json.dumps({'baseline':str(base),'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'frames_inclusive':[[0,413]],'scope':'Only early native intro/mainphone; late-mail13.8–14.333 and all later phases untouched.','helper':'refine_early_v13.apply_early(scene)','bitmap_provenance':['early-v13-measure/intro-outline-provenance.json','early-v13-measure/email-exit-artwork-provenance.json']},indent=2)+'\n');print(out)
