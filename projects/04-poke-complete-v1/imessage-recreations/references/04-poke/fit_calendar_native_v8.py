"""Fit individual editable calendar glyph bounds against saved actual native PNGs."""
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageFont
from v8_utils import at
p=Path(__file__).parent;s=json.loads((p/'scene-v8-batch-candidate.json').read_text());card=next(l for l in s['layers']if l['id']=='p0100');refs={n:np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(int)for n in[184,212,259]};cands={n:np.array(Image.open(p.parent.parent/f'outputs/04-poke/v8-batch-checks/{n:06}.png').convert('RGB')).astype(int)for n in refs};records=[]
def ink(a,roi,color):
 x,y,x2,y2=roi;c=a[y:y2,x:x2]
 if color=='black':mask=c.max(2)<120
 elif color=='gray':mask=(c.min(2)>70)&(c.max(2)<210)&(c.max(2)-c.min(2)<20)
 else:mask=(c[:,:,1]-c[:,:,0]>35)&(c[:,:,2]-c[:,:,0]>65)
 yy,xx=np.where(mask)
 if len(xx)<20:return None
 return [int(xx.min()+x),int(yy.min()+y),int(xx.max()+x+1),int(yy.max()+y+1)]
for l in card['children']:
 if l['type']!='text':continue
 n=184 if l['y']<500 else 212 if l['y']<1140 else 259
 cy=at(card,'y',n*1001/30000);x=188+l['x'];y=cy+l['y'];fontSize=l['fontSize'];family='Text'if l['fontFamily'].endswith('Text')else'Display';weight={400:'Regular',500:'Medium',600:'Semibold',700:'Bold'}[l.get('fontWeight',400)];f=ImageFont.truetype(str(p.parent.parent/f'shared/fonts/SF-Pro-{family}-{weight}.otf'),round(fontSize));width=max(f.getlength(v)for v in l['text'].split('\n'));height=(len(l['text'].split('\n'))-1)*l.get('lineHeight',fontSize*1.2)+fontSize*1.2
 anchor=l.get('textAnchor','start');left=x-(width/2 if anchor=='middle'else width if anchor=='end'else 0);roi=(max(190,int(left-12)),max(0,int(y-12)),min(1250,int(left+width+16)),min(1080,int(y+height+16)))
 if roi[3]-roi[1]<fontSize:continue
 color='black'if l['fill']=='#000000'else'gray'if l['fill']=='#999999'else'blue';a=ink(refs[n],roi,color);b=ink(cands[n],roi,color)
 if not a or not b:continue
 sx=(a[2]-a[0])/(b[2]-b[0]);sy=(a[3]-a[1])/(b[3]-b[1])
 if not(.8<sx<1.2 and .8<sy<1.2):continue
 records.append(dict(id=l['id'],frame=n,text=l['text'],source_bbox=a,candidate_bbox=b,x=a[0]-(b[0]-x)*sx-188,y=a[1]-(b[1]-y)*sy-cy,scaleX=l.get('scaleX',1)*sx,scaleY=l.get('scaleY',1)*sy))
(p/'measurements-v8/calendar-ink-fit.json').write_text(json.dumps({'method':'Exact source vs actual production GSAP native PNGs. Per-native-text-node ink-box registration; no UI bitmaps.','measurements':records},indent=2));print(records)
