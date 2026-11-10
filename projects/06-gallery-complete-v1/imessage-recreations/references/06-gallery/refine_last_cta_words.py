from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
r=Path('/workspace/imessage-recreations');d=r/'references/06-gallery';s=json.loads((d/'scene.json').read_text());cut=181/30

def mt(t):return t-cut
tracks={};data=[]
for p in sorted((d/'final-word-measurements').glob('*.png')):
 t=49.1+(int(p.stem)-1)/30;a=np.asarray(Image.open(p).convert('RGB'));gray=a.mean(axis=2);m=gray<230;xx=np.where(m.any(axis=0))[0];cc=[]
 for x in xx:
  if not cc or x-cc[-1][-1]>22:cc.append([x])
  else:cc[-1].append(x)
 groups=[]
 for c in cc:
  x0,x1=int(c[0]),int(c[-1])+1;y,x=np.where(m[:,x0:x1])
  if len(y)<100:continue
  y0,y1=int(y.min()),int(y.max())+1;val=gray[y0:y1,x0:x1][m[y0:y1,x0:x1]];groups.append({'t':t,'x':x0+200,'y':y0+300,'width':x1-x0,'height':y1-y0,'color':int(np.percentile(val,5))})
 names=['Just','like','a','friend'][:len(groups)] if t<50.55 else ['Start','now'][:len(groups)]
 if len(names)!=len(groups):continue
 for name,row in zip(names,groups):tracks.setdefault(name,[]).append(row);data.append({'name':name,**row})
s['layers']=[g for g in s['layers'] if abs(g.get('start',0)-mt(49.1))>1e-6 and abs(g.get('start',0)-mt(50.55))>1e-6]
f=ImageFont.truetype(str(r/'shared/fonts/SF-Pro-Display-Medium.otf'),124)
for name,rows in tracks.items():
 im=Image.new('L',(1200,400));ImageDraw.Draw(im).text((0,0),name,font=f,fill=255);bb=im.getbbox();iw,ih=bb[2]-bb[0],bb[3]-bb[1];keys={z:[] for z in ['x','y','scaleX','scaleY','fill']}
 for a in rows:
  xscale,yscale=a['width']/iw,a['height']/ih;t=mt(a['t']);keys['x'].append({'t':t,'value':a['x']-bb[0]*xscale});keys['y'].append({'t':t,'value':a['y']-bb[1]*yscale});keys['scaleX'].append({'t':t,'value':xscale});keys['scaleY'].append({'t':t,'value':yscale});keys['fill'].append({'t':t,'value':'#'+f'{a["color"]:02x}'*3})
 s['layers'].append({'id':'source-measured-final-word-'+name,'type':'text','text':name,'fontFamily':'SF Pro Display','fontSize':124,'fontWeight':500,'fill':'#000000','x':0,'y':0,'start':mt(rows[0]['t']),'end':mt(rows[-1]['t']+1/30),'keyframes':keys})
s['source']['notes']+=' Finalv12 also rebuilds each final CTA word from measured per-frame type bounds and fill, preserving editable text and original partial-word timing.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'native-final-word-tracks.json').write_text(json.dumps(data,indent=2));print({n:len(v) for n,v in tracks.items()})
