from pathlib import Path
import json,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parent.parent
cam={x['frame']:x['camera_y'] for x in json.loads((D/'native-birthday-camera-v17.json').read_text())}
for x in json.loads((D/'native-birthday-center-v17.json').read_text())+json.loads((D/'native-birthday-tail-v17.json').read_text()):
 if x['frame'] not in cam and x['center_top_y'] is not None:cam[x['frame']]=x['center_top_y']-10
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss','27','-i',str(D/'source.mp4'),'-t',str(36/30),'-f','rawvideo','-pix_fmt','gray','-threads','1','pipe:1'],stdout=subprocess.PIPE);out=[]
for f in range(810,846):
 raw=p.stdout.read(1920*1080)
 if len(raw)!=1920*1080:raise RuntimeError('Short Tracks title decode')
 a=np.frombuffer(raw,np.uint8).reshape(1080,1920);m=a<140;m[:,:150]=False;m[:,1770:]=False
 if f in cam:m[max(0,int(cam[f])-5):]=False
 y,x=np.nonzero(m);bb=None if len(x)<30 else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)];out.append({'frame':f,'bbox':bb,'pixels':len(x)})
 if f==834:Image.fromarray(a).convert('RGB').save(D/'keyframes/027.80.png')
p.wait();(D/'native-tracks-title-v17.json').write_text(json.dumps(out,indent=2));print(out)
# Compare candidate fonts after fitting native reference bounds; keep text editable.
a=np.asarray(Image.open(D/'keyframes/027.80.png').convert('L'));m=a<140;y,x=np.nonzero(m);bb=[x.min(),y.min(),x.max()+1,y.max()+1];crop=a[bb[1]:bb[3],bb[0]:bb[2]];scores=[]
for path in list((R/'shared/fonts').glob('SF-Pro-Display-*.otf'))+list((R/'references/01-photonhq/assets').glob('Inter-[4567]00.ttf')):
 f=ImageFont.truetype(str(path),280);im=Image.new('L',(2200,500),255);ImageDraw.Draw(im).text((0,0),'Tracks what',font=f,fill=0);mm=np.asarray(im)<140;yy,xx=np.nonzero(mm);ib=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];c=im.crop(ib).resize((int(bb[2]-bb[0]),int(bb[3]-bb[1])),Image.Resampling.LANCZOS);scores.append({'font':path.name,'path':str(path),'mae':float(np.abs(np.asarray(c).astype(float)-crop).mean()),'ink_bbox':ib})
scores.sort(key=lambda x:x['mae']);(D/'tracks-title-font-fit-v17.json').write_text(json.dumps(scores,indent=2));print('FONTS',scores[:3])
