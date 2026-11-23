from pathlib import Path
from PIL import Image
import numpy as np,json
p=Path(__file__).parent; root=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
cfg=p/'project/scene.json';j=json.loads(cfg.read_text())
for f,profiles in j['profileRegistrations'].items():
 a=np.asarray(Image.open(root/f'{int(f):06}.png').convert('RGB'),dtype=np.int16)
 for n,pose in enumerate(profiles):
  x,y,r,b=pose['chip']
  x0,x1=round(x+(r-x)*.25),round(r-8)
  y0,y1=round(y+5),round(b-5)
  q=a[y0:y1,x0:x1]
  R,G,B=np.moveaxis(q,2,0)
  tone=((G>R+36)&(G>B+27)&(R<173),
        (B>R+28)&(B>G+61)&(R>G+16),
        (R>G+35)&(G>B+34)&(B<179))[n]
  rows,cols=np.where(tone)
  if len(cols)<10: 
   print(f,n,'insufficient signal')
   continue
  left=x0+np.percentile(cols,.1)
  top=y0+np.percentile(rows,.4)
  right=x0+np.percentile(cols,99.9)+1
  bottom=y0+np.percentile(rows,99.7)+1
  # At the last soft frames, infer the edge from the earlier measured ink.
  if int(f)>=285:
    if right-left<pose['text'][2]*.72:
      center=(left+right)/2
      left=center-pose['text'][2]*.44
      right=center+pose['text'][2]*.44
  pose['text']=np.round([left-.55,top-.55,right-left+1.1,bottom-top+1.1],2).tolist()
  u,v,c,d=pose['glyph']
  glyph_width=min(c,max(20,round(left-8-u)),[30,32,31][n])
  if glyph_width<c and n==1: u+=(c-glyph_width)*.15
  pose['glyph']=[u,v,glyph_width,d]
  if int(f) in (271,275,283,286):print(f,n,pose['text'],pose['glyph'])
cfg.write_text(json.dumps(j,indent=2)+'\n')
