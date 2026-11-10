from pathlib import Path
import subprocess,numpy as np,json
from PIL import Image,ImageDraw
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-provider-timing';P.mkdir(exist_ok=True);w,h=1320,400
cmd=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss','44.4','-i',str(R/'references/06-gallery/source.mp4'),'-frames:v','91','-vf','crop=1320:400:300:350','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'];data=subprocess.check_output(cmd);a=np.frombuffer(data,np.uint8).reshape(-1,h,w,3);ms=[];sheet=Image.new('RGB',(1320,16*125),'white');d=ImageDraw.Draw(sheet)
for i,b in enumerate(a):
 f=1332+i;Rr,G,B=[b[:,:,j].astype(float) for j in range(3)];gr=(G>Rr+25)&(G>B+15);bl=(B>Rr+35)&(G>Rr+10);m=b.mean(2)<80
 def box(m):
  yy,xx=np.where(m);return [int(xx.min()+300),int(yy.min()+350),int(xx.max()+301),int(yy.max()+351)] if len(xx) else None
 ms.append(dict(frame=f,time=f/30,green_pixels=int(gr.sum()),blue_pixels=int(bl.sum()),green_box=box(gr),blue_box=box(bl),black_box=box(m)))
 if i%3==0:
  j=i//3;x=(j%2)*660;y=(j//2)*125;im=Image.fromarray(b).resize((660,200)).crop((0,25,660,130));sheet.paste(im,(x,y+20));d.text((x+5,y),f'{f/30:.3f} [{f}]',fill='red');Image.fromarray(b).save(P/f'{f:06d}.png')
(P/'measurements.json').write_text(json.dumps(ms,indent=2));sheet.save(P/'strip.jpg',quality=92);print(len(a),str(P/'strip.jpg'))
