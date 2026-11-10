"""Measure isolated title components; raw reference crops are not output layers."""
from pathlib import Path
import subprocess,json
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss','8','-i',str(D/'source.mp4'),'-t','4.5','-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'],stdout=subprocess.PIPE)
rows=[];tiles=[]
def box(mask):
 y,x=np.nonzero(mask)
 return None if len(x)<25 else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
for f in range(240,375):
 data=p.stdout.read(1920*1080*3)
 if len(data)!=1920*1080*3:raise RuntimeError('Incomplete reference decode')
 a=np.frombuffer(data,np.uint8).reshape(1080,1920,3);z=a.astype(float);m=np.max(a,axis=2)<180
 green=(z[:,:,1]>z[:,:,0]*1.35)&(z[:,:,1]>z[:,:,2]*1.08)&(z[:,:,0]<150)&(z[:,:,1]<200)
 row={'frame':f,'parts':{}}
 gb=box(green)
 if gb:
  lo=max(0,gb[1]-15);hi=min(1080,gb[3]+30);band=np.zeros_like(m);band[lo:hi]=m[lo:hi]
  for name,left,right in [('The',0,gb[0]),('best contact',gb[0],gb[2]),('in your phone',gb[2],1920)]:
   mm=band.copy();mm[:,:left]=False;mm[:,right:]=False;b=box(mm)
   if b:row['parts'][name]=b
  mm=m.copy();mm[:hi+5]=False;b=box(mm)
  if b:row['parts']['with multiplayer mode']=b
 else:
  xs=np.where(m.any(axis=0))[0];groups=[]
  for x in xs:
   if not groups or x-groups[-1][-1]>30:groups.append([int(x)])
   else:groups[-1].append(int(x))
  for g in groups:
   mm=np.zeros_like(m);mm[:,g[0]:g[-1]+1]=m[:,g[0]:g[-1]+1];b=box(mm)
   if b and (f<276 or b[2]-b[0]>200) and 'Introducing' not in row['parts']:row['parts']['Introducing']=b
   elif b and 1030<b[0]<1170:row['parts']['mascot']=b
   elif b and b[0]>=1170:
    prev=row['parts'].get('Rene');row['parts']['Rene']=b if prev is None else [min(prev[0],b[0]),min(prev[1],b[1]),max(prev[2],b[2]),max(prev[3],b[3])]
 rows.append(row)
 if f in [240,255,270,285,300,315,320,325,330,345,360,372]:
  tile=Image.fromarray(a).resize((640,360));ImageDraw.Draw(tile).text((0,0),str(f),fill='red');tiles.append(tile)
p.wait();assert p.returncode==0
(D/'native-title-component-tracks.json').write_text(json.dumps(rows,indent=2))
sheet=Image.new('RGB',(1280,360*((len(tiles)+1)//2)),'white')
for i,t in enumerate(tiles):sheet.paste(t,(i%2*640,i//2*360))
sheet.save(D/'assets/title-motion-source.jpg')
for row in rows:
 if row['frame'] in [240,255,270,285,300,315,320,325,330,345,360,372]:print(row)
