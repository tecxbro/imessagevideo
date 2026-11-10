"""Rebuild measured montage cameras, native game geometry, and declared static app UI."""
from pathlib import Path
import copy,json,sys,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
p=Path(__file__).parent;sys.path.insert(0,str(p.parent/'02-danieltian'))
from trace_glyphs import trace_alpha
s=json.loads((p/'late-v13.scene.json').read_text());phone=next(x for x in s['layers'] if x['id']=='p03-371');lunch=next(x for x in s['layers'] if x['id']=='p03-204');lunch['end']=800/30;phone['start']=800/30
for x in s['layers']:
 if x.get('end')==26.7:x['end']=800/30
boxes=json.loads((p/'montage-native/hardware-boxes.json').read_text());boxes={r['frame']:r['box'] for r in boxes};poses={}
for f,b in boxes.items():
 if b:
  sx=(b[2]-b[0])/(496*800/508);sy=(b[3]-b[1])/(1036*1658/1053);poses[f]={'x':b[0]-2*800/508*sx,'y':b[1]-8*1658/1053*sy,'scaleX':sx,'scaleY':sy}
# The first five new montage frames have both top and bottom cropped. Use
# measured side-bezel modes, and preserve the centered stage projection.
for f in range(800,805):
 a=np.array(Image.open(p/'montage-native'/f'{f-794:03}.png'));m=(a.max(2)<95);counts=m[250:950].sum(0);left=np.argmax(counts[500:900])+500;right=np.argmax(counts[1020:1420])+1020;sx=(right-left)/768;poses[f]={'x':960-400*sx,'y':540-829*sx,'scaleX':sx,'scaleY':sx}
for f in range(800,891):
 if f not in poses:
  bef=max(k for k in poses if k<f);aft=min(k for k in poses if k>f);u=(f-bef)/(aft-bef);poses[f]={k:poses[bef][k]*(1-u)+poses[aft][k]*u for k in poses[bef]}
phone['keyframes']={k:[{'t':f/30,'value':poses[f][k],'ease':'linear'} for f in range(800,891)] for k in ['x','y','scaleX','scaleY']}
# Authentic incoming app cards remain separate native containers.
for ident in ['p03-257','p03-268']:
 c=next(x for x in phone['children'] if x['id']==ident);c['start']=800/30;c['end']=850/30
 if ident=='p03-268':c['keyframes']={'opacity':[{'t':800/30,'value':0},{'t':806/30,'value':1,'ease':'linear'}]}
# Hide all old invented app interiors; actual state boundaries were measured.
for ident in ['p03-289','p03-305','p03-362','p03-370']:
 c=next(x for x in phone['children'] if x['id']==ident);c['opacity']=0
# Game content is native traced flat geometry, never a frame texture.
world={'id':'measured-game-v13','type':'group','start':813/30,'end':850/30,'children':[]};records=[]
def pathmask(mask,fill,identifier):
 yy,xx=np.where(mask)
 if not len(xx):return None
 x0,y0,x1,y1=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)
 d,stats=trace_alpha(mask[y0:y1,x0:x1].astype(float))
 return {'id':identifier,'type':'path','d':d,'x':x0,'y':y0,'fill':fill} if d else None
for f in range(813,850):
 a=np.array(Image.open(p/'montage-native'/f'{f-794:03}.png').convert('RGB'));rgb=a.astype('int16');bg=(rgb[:,:,2]-rgb[:,:,0]>5)&(rgb[:,:,0]>165)&(rgb[:,:,0]<230)&(np.abs(rgb[:,:,0]-rgb[:,:,1])<7);bg[:90]=False;bg[:,:730]=False;bg[:,1190:]=False;l,n=ndimage.label(bg);areas=np.bincount(l.ravel());areas[0]=0;label=areas.argmax();yy,xx=np.where(l==label);top=int(yy.min());left=int(xx.min());right=int(xx.max()+1);bottom=int(yy.max()+1);pose=poses[f];screenleft=pose['x']+28*pose['scaleX'];screenright=pose['x']+772*pose['scaleX'];screenbottom=pose['y']+1630*pose['scaleY'];panel={'id':f'game-frame-{f}','type':'group','start':f/30,'end':(f+1)/30,'clip':{'x':screenleft,'y':max(top,pose['y']+30*pose['scaleY']),'width':screenright-screenleft,'height':screenbottom-max(top,pose['y']+30*pose['scaleY']),'radius':65*pose['scaleX']},'children':[]}
 # Independent native background gradient and sheet shape.
 values=[]
 for y in np.linspace(top+5,min(bottom-5,1075),8).astype(int):
  col=a[y,max(0,left):min(1920,right)];keep=(col[:,2].astype(int)-col[:,0].astype(int)>5)&(col[:,0]>165)
  values.append(np.median(col[keep],axis=0) if keep.any() else np.array([195,198,211]))
 gid=f'game-gradient-{f}';s.setdefault('gradients',[]).append({'id':gid,'type':'linear','x1':'0%','y1':'0%','x2':'0%','y2':'100%','stops':[{'offset':f'{i*100/7}%','color':'#'+''.join(f'{int(round(v)):02x}' for v in q)} for i,q in enumerate(values)]});panel['children'].append({'id':f'game-bg-{f}','type':'rect','x':screenleft,'y':top,'width':screenright-screenleft,'height':screenbottom-top,'radius':60*pose['scaleX'],'fill':f'url(#{gid})'})
 # Crop only individual flat game objects, excluding the native background.
 region=np.zeros(a.shape[:2],bool);region[max(top+100,0):min(round(screenbottom),1080),max(round(screenleft),0):min(round(screenright),1920)]=True
 neutral=(rgb.max(2)-rgb.min(2)<14)&(rgb.mean(2)<187);green=(rgb[:,:,1]>rgb[:,:,0]*1.12)&(rgb[:,:,1]>rgb[:,:,2]*1.2)&(rgb[:,:,1]>65);peg=(rgb[:,:,2]>rgb[:,:,0]*1.1)&(rgb[:,:,0]<95)&(rgb[:,:,1]<110);fg=region&(neutral|green|peg)
 # Fixed palette retains independent shaded cube/peg faces across frames.
 palette=np.array([[49,50,49],[65,66,63],[84,85,82],[105,106,103],[128,129,124],[148,150,143],[163,165,157],[91,131,17],[111,151,19],[126,166,20],[137,178,23],[39,34,70],[58,52,90],[83,77,115]],dtype=float);pixels=a[fg].astype(float)
 if len(pixels):
  labs=np.argmin(np.sum((pixels[:,None,:]-palette[None,:,:])**2,2),1);index=np.full(a.shape[:2],-1,int);index[fg]=labs
  for i,color in enumerate(palette):
   mask=index==i;path=pathmask(mask,'#'+''.join(f'{round(v):02x}' for v in color),f'game-object-face-{f}-{i}')
   if path:panel['children'].append(path)
 # Header and score are editable native vector outlines with semantic text.
 bx0=max(0,round(screenleft+30*pose['scaleX']));bx1=min(1920,round(screenright-30*pose['scaleX']));by0=max(0,top+4);by1=min(1080,top+round(200*pose['scaleY']));crop=a[by0:by1,bx0:bx1].astype(float);alpha=np.clip((190-crop.mean(2))/170,0,1);alpha[crop.mean(2)>150]=0;d,stats=trace_alpha(alpha);panel['children'].append({'id':f'game-caption-score-{f}','type':'path','d':d,'x':bx0,'y':by0,'fill':'#20202a','semanticText':'Jump Jump; '+('3' if f<830 else '4')});# Source app sheet dims the chat and then covers it with a black display.
 shade=max(0,min(1,(f-813)/11));panel['children'].insert(0,{'id':f'game-underlay-{f}','type':'rect','x':screenleft,'y':pose['y']+30*pose['scaleY'],'width':screenright-screenleft,'height':screenbottom-(pose['y']+30*pose['scaleY']),'radius':115*pose['scaleX'],'fill':'#000000','opacity':shade})
 # Underlay must include the device cap above the sheet, outside panel clip.
 under=panel['children'].pop(0);panel['clip']={'x':screenleft,'y':pose['y']+30*pose['scaleY'],'width':screenright-screenleft,'height':screenbottom-(pose['y']+30*pose['scaleY']),'radius':115*pose['scaleX']};panel['children'].insert(0,under)
 world['children'].append(panel);records.append({'frame':f,'panel_box':[screenleft,top,screenright,screenbottom],'palette_object_faces':len(panel['children'])-2})
s['layers'].insert(s['layers'].index(phone)+1,world)
# Rich static app UI artwork is isolated to the phone display. Each of four
# app states is a separate declared asset and independently animated layer.
assets=[]
for name,ref,start,end in [('uber-driver',851,850,865),('health',870,865,875),('manus',879,875,885),('google-signin',887,885,891)]:
 pose=poses[ref];image=Image.open(p/'montage-native'/f'{ref-794:03}.png').convert('RGB');x0=round(pose['x']+28*pose['scaleX']);y0=round(pose['y']+30*pose['scaleY']);x1=round(pose['x']+772*pose['scaleX']);y1=round(pose['y']+1630*pose['scaleY']);file=f'assets/montage-{name}-original-v13.png';image.crop((x0,y0,x1,y1)).save(p/file);group={'id':'measured-app-ui-'+name+'-v13','type':'group','start':start/30,'end':end/30,'children':[{'id':'app-ui-art-'+name,'type':'image','src':file,'x':x0,'y':y0,'width':x1-x0,'height':y1-y0}],'clip':{'x':x0,'y':y0,'width':x1-x0,'height':y1-y0,'radius':115*pose['scaleX']},'keyframes':{k:[] for k in ['x','y','scaleX','scaleY']}}
 for f in range(start,end):
  q=poses[f];sx=q['scaleX']/pose['scaleX'];sy=q['scaleY']/pose['scaleY'];
  for k,v in [('x',q['x']-pose['x']*sx),('y',q['y']-pose['y']*sy),('scaleX',sx),('scaleY',sy)]:group['keyframes'][k].append({'t':f/30,'value':v,'ease':'linear'})
 s['layers'].insert(s['layers'].index(world)+1,group);assets.append({'file':file,'source_frame':ref,'source_box':[x0,y0,x1,y1],'scope':'Static rich product UI only; internal copy is bitmap. Native phone, clipping, camera and state lifetime remain editable.'})
s['source']['notes']+=' V13 montage: perframe native camera, corrected app state boundaries; native independently traced shaded game faces and score/header outlines; four declared bounded static product UI assets. No whole sourceframe or sourcevideo layer.'
f=p/'montage-v13.scene.json';f.write_text(json.dumps(s,indent=2));(p/'montage-v13-changes.json').write_text(json.dumps({'baseline':'late-v13.scene.json','delta':[800,890],'assets':assets,'game_measurements':records,'poses':poses,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()},indent=2));print('built',len(world['children']),len(assets))
