from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,cv2,json
R=Path(__file__).resolve().parent;D=R/'emoji-art';D.mkdir(exist_ok=True)
items={'heads':(280,[185,510,290,615]),'pin':(280,[635,505,706,615]),'heart':(280,[1275,510,1375,610]),'car':(300,[181,682,282,762]),'food':(300,[181,787,281,876])}
records={}
for name,(f,bounds)in items.items():
 rgb=np.asarray(Image.open(R/'reasoning-source'/f'source-{f:04d}.png').convert('RGB')).astype(float)
 x0,y0,x1,y1=bounds;crop=rgb[y0:y1,x0:x1];color=(crop.max(2)-crop.min(2)>10)&(crop.min(2)<240)
 ink=crop.min(2)<248;num,labels=cv2.connectedComponents(ink.astype(np.uint8));selected=np.unique(labels[color]);selected=selected[selected>0]
 mask=np.isin(labels,selected).astype(np.uint8)
 mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
 # Fill enclosed art highlights while retaining transparent exterior.
 flood=mask.copy();cv2.floodFill(flood,None,(0,0),1);mask=np.maximum(mask,1-flood)
 outer=cv2.dilate(mask,np.ones((3,3),np.uint8));core=cv2.erode(mask,np.ones((3,3),np.uint8))
 alpha=np.where(core>0,1,np.where(outer>0,np.clip((253-crop.min(2))/80,0,1),0))
 fg=np.where(alpha[:,:,None]>.001,253+(crop-253)/np.maximum(alpha[:,:,None],.001),0)
 rgba=np.dstack([np.clip(fg,0,255),alpha*255]).astype(np.uint8)
 file=D/(name+'.png');Image.fromarray(rgba).save(file)
 records[name]={'frame':f,'bounds':bounds,'file':str(file.resolve()),'width':x1-x0,'height':y1-y0,'sourceArtwork':'Authentic bounded Apple emoji, static single-reference artwork; exterior transparent.'}
(D/'provenance.json').write_text(json.dumps(records,indent=2))
canvas=Image.new('RGB',(700,180),(253,253,253));draw=ImageDraw.Draw(canvas)
for i,(name,item)in enumerate(records.items()):
 art=Image.open(item['file']);canvas.paste(art,(i*140,30),art);draw.text((i*140,5),name,fill='black')
canvas.save(D/'contact.jpg')
