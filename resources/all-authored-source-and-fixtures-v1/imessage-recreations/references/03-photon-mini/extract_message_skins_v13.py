"""Isolate static original message/card components, keeping native trajectories."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
P=Path(__file__).parent;B=P/'early-v13-measure';D=P/'assets/early-message-skins-v13';D.mkdir(exist_ok=True);sys.path.insert(0,str(P));from refine_early_v13 import blue_components,measured_data
_,poses=measured_data();records=[];layers={};images={150:Image.open(B/'validation-source/009.png').convert('RGB'),195:Image.open(B/'source-full-0195.png').convert('RGB'),205:Image.open(B/'validation-source/011.png').convert('RGB'),390:Image.open(B/'validation-source/017.png').convert('RGB')}
def isolate(name,f,box,normalization):
 im=images[f];a=np.array(im);x1,y1,x2,y2=box;crop=a[y1:y2,x1:x2];mask=crop.min(2)<248;labels,n=ndimage.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0;selected=ndimage.binary_fill_holes(labels==int(sizes.argmax()));ys,xs=np.where(selected);tight=(x1+int(xs.min()),y1+int(ys.min()),x1+int(xs.max()+1),y1+int(ys.max()+1));rgba=np.dstack([crop,(selected*255).astype('uint8')]);art=Image.fromarray(rgba).crop((tight[0]-x1,tight[1]-y1,tight[2]-x1,tight[3]-y1));asset=D/(name+'.png');art.save(asset);unit,refX,refY=normalization;w=tight[2]-tight[0];h=tight[3]-tight[1];geometry={'src':str(asset.relative_to(P)),'x':(tight[0]-refX)*unit,'y':(tight[1]-refY)*unit,'width':w*unit,'height':h*unit};records.append({'name':name,'source_frame':f,'bounds':list(tight),'asset':str(asset.relative_to(P)),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'editability':'Original internal UI copy/gradient/shape is bitmap; its native component trajectory/lifetime/opacity remain independently editable.','native_geometry':geometry});layers[name]=geometry;return art,tight
thumbs=[]
for name,f in [('mail-pre',195),('mail-pressed',205),('mail-post',390)]:
 im=images[f];cs=blue_components(Image.open(B/'source'/f'{f-48:04d}.png').convert('RGB'));c=max([b for b in cs if b['x']<800 and b['w']>300],key=lambda b:b['area']);box=(c['x']-6,c['y']-5,c['x']+c['w']+7,min(1080,round(c['y']+c['w']*.75+20)));art,_=isolate(name,f,box,(517/c['w'],c['x'],c['y']));thumbs.append((name,art))
c=max([b for b in blue_components(Image.open(B/'source'/'0102.png').convert('RGB')) if 3.5<b['ratio']<5.5 and b['w']>400],key=lambda b:b['area']);art,_=isolate('blue-draft',150,(c['x']-5,c['y']-5,c['x']+c['w']+6,c['y']+c['h']+6),(518/c['w'],c['x'],c['y']));thumbs.append(('blue-draft',art))
for name,f,box in [('working',150,(400,620,950,800)),('sent',390,(500,515,850,650)),('reply',390,(500,650,1350,850))]:
 p=poses[f];unit=1/p['scale'];art,tight=isolate(name,f,box,(unit,p['x'],p['y']));thumbs.append((name,art))
contact=Image.new('RGB',(480*4,360*2),'#ddd')
for i,(name,art)in enumerate(thumbs):
 bg=Image.new('RGBA',art.size,'#d68be5');bg.alpha_composite(art);bg.thumbnail((460,320));contact.paste(bg.convert('RGB'),((i%4)*480,(i//4)*360+35));ImageDraw.Draw(contact).text(((i%4)*480+8,(i//4)*360+10),name,fill='black')
contact.save(B/'message-skin-contact.jpg');(B/'message-skin-geometry.json').write_text(json.dumps(layers,indent=2)+'\n');(B/'message-skin-provenance.json').write_text(json.dumps({'records':records,'diagnosis':'Original previews exposed generic mail-logo/gradient substitutes, wrong message tails and remaining type/spacing differences. Isolate bounded original static UI components; do not flatten the scene or bake camera/arrival motion. Pressed card is a separate actual UI state.'},indent=2)+'\n');print([(r['name'],r['bounds'])for r in records])
