from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json
r=Path('/workspace/imessage-recreations');d=r/'references/05-linq';s=json.loads((d/'scene.json').read_text());provenance=json.loads((d/'assets/asset-provenance.json').read_text())
def extract(t,b,name):
 im=Image.open(d/f'keyframes/{t}.png').convert('RGBA').crop(b);m=Image.new('L',im.size);mp=m.load();pp=im.load()
 for y in range(im.height):
  for x in range(im.width):
   rr,gg,bb,_=pp[x,y];mp[x,y]=255 if max(rr,gg,bb)-min(rr,gg,bb)<65 and (rr+gg+bb)/3>120 else 0
 m=m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3));dr=ImageDraw.Draw(m);dr.rectangle((0,0,im.width-1,2),fill=0);dr.rectangle((0,im.height-3,im.width-1,im.height-1),fill=0);dr.rectangle((0,0,2,im.height-1),fill=0);dr.rectangle((im.width-3,0,im.width-1,im.height-1),fill=0)
 ImageDraw.floodfill(m,(0,0),128,thresh=0);mp=m.load()
 for y in range(im.height):
  for x in range(im.width):mp[x,y]=0 if mp[x,y]==128 else 255
 im.putalpha(m.filter(ImageFilter.GaussianBlur(.25)));path=f'assets/{name}.png';im.save(d/path);provenance.append({'path':path,'timestamp':float(t),'box':b,'kind':'isolated chess sprite; expanded crop and exterior flood fill remove board texture'});print(name,im.getbbox());return path,im.size
white,ws=extract('008.20',(549,425,643,519),'white-pawn-transparent');black,bs=extract('008.20',(472,265,566,365),'black-pawn-transparent');queen,qs=extract('029.00',(455,128,527,202),'black-queen-transparent')
for g in s['layers']:
 if g.get('start')==6.97:
  g['start']=6.9;g['keyframes']['opacity']=[{'t':6.9,'value':0},{'t':6.9333333,'value':.3},{'t':7,'value':.6466458},{'t':7.1,'value':1}]
  for q in g['children']:
   if 'white-pawn-sprite' in q.get('src',''):
    q.update(src=white,x=q['x']-8,y=q.get('y',0)-8,width=ws[0],height=ws[1]);
    for k in q['keyframes']['y']:k['value']-=8
   if 'black-pawn-sprite' in q.get('src',''):
    q.update(src=black,x=q['x']-8,y=q.get('y',0)-14,width=bs[0],height=bs[1]);
    for k in q['keyframes']['y']:k['value']-=14
 if g.get('start')==28.83:
  q=g['children'][1];q.update(src=queen,width=qs[0],height=qs[1]);
  for k in q['keyframes']['x']:k['value']-=8
  for k in q['keyframes']['y']:k['value']-=8
s['source']['notes']+=' Finalv7 fixes an identified sprite-alpha failure: the previous corner flood seed retained wood/background; expanded object crops, zeroed border and exterior flood fill now isolate the actual pieces. Board fade is fitted to source7s empty-cell colors.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'assets/asset-provenance.json').write_text(json.dumps(provenance,indent=2))
