from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, json, copy
root=Path('/workspace/imessage-recreations');d=root/'references/06-gallery';s=json.loads((d/'scene.json').read_text());prov=json.loads((d/'assets/asset-provenance.json').read_text());count=0;cut=181/30

def mt(t):return t if t<41 else t-cut
def uid(p):
 global count;count+=1;return f'rene-final11-{p}-{count}'
def rect(x,y,w,h,c='#ffffff',r=0,**kw):return dict(type='rect',id=uid('rect'),x=x,y=y,width=w,height=h,fill=c,radius=r,**kw)
def img(src,x,y,w,h,**kw):return dict(type='image',id=uid('image'),src=src,x=x,y=y,width=w,height=h,**kw)
def txt(t,x,y,z=48,c='#222222',weight=400,**kw):return dict(type='text',id=uid('text'),text=t,x=x,y=y,fontFamily='SF Pro Display',fontSize=z,fontWeight=weight,lineHeight=z*1.14,fill=c,**kw)
def group(ch,a,b,**kw):return dict(type='group',id=uid('group'),children=ch,start=mt(a),end=mt(b),**kw)
def tr(*pairs):return [{'t':mt(t),'value':v,'ease':'linear'} for t,v in pairs]
def crop(t,box,name,rounding=None,kind='isolated static graphic asset'):
 im=Image.open(d/f'keyframes/{t}.png').convert('RGBA').crop(box)
 if rounding:
  mask=Image.new('L',im.size);ImageDraw.Draw(mask).ellipse((0,0,im.width-1,im.height-1),fill=255);im.putalpha(mask)
 path=f'assets/{name}.png';im.save(d/path);prov.append({'path':path,'timestamp':float(t),'box':box,'kind':kind});return path
f48=ImageFont.truetype(str(root/'shared/fonts/SF-Pro-Display-Regular.otf'),48)
def inktext(t,x,ink_y,z=48,c='#222222',weight=400,**kw):
 ff=ImageFont.truetype(str(root/f'shared/fonts/SF-Pro-Display-{"Medium" if weight==500 else "Regular"}.otf'),round(z));return txt(t,x,ink_y-ff.getbbox(t.split('\n')[0])[1],z,c,weight,**kw)
def bubble(t,x,y,w,h,ink_y,blue=False):
 fill='#43b2eb' if blue else '#ededed';tail=f'M {w-70} {h-20} Q {w-39} {h+17} {w-23} {h+20} Q {w-50} {h-3} {w-31} {h-32} Z' if blue else f'M 38 {h-28} Q 72 {h-4} 28 {h+21} Q 49 {h+17} 75 {h-12} Z'
 return dict(type='group',id=uid('bubble'),x=x,y=y,children=[rect(0,0,w,h,fill,min(h/2,75)),dict(type='path',id=uid('tail'),d=tail,fill=fill),inktext(t,40,ink_y-y,48,'#ffffff' if blue else '#222222')])

# Native conversation scroll and independently moving composer/keyboard from measured4/6.5/7.5s.
dan=crop('004.00',(429,154,520,246),'dan-large-memoji',True)
rene_small=crop('004.00',(448,672,506,736),'rene-small-avatar')
eyes=crop('004.00',(852,694,909,743),'booking-eyes')
camp=crop('007.50',(1099,568,1152,619),'calendar-camp-emoji')
phone=Image.open(d/'keyframes/006.50.png').convert('RGBA').crop((337,0,1593,1080));mask=Image.new('L',phone.size);dr=ImageDraw.Draw(mask);dr.rectangle((0,0,58,1079),fill=255);dr.rectangle((1200,0,1255,1079),fill=255);phone.putalpha(mask);phone.save(d/'assets/lower-phone-hardware.png');prov.append({'path':'assets/lower-phone-hardware.png','timestamp':6.5,'box':[337,0,1593,1080],'kind':'physical side hardware only; screen transparent'})
thread=[inktext('Dan',591,62,29,'#888888'),img(dan,429,154,91,92),bubble('Not me, I organized the last\none',550,98,655,154,133),inktext('Rene',591,302,29,'#888888'),bubble('Oct 17 is the first weekend\nall of you are free',550,339,655,154,373),bubble('Want me to book the\nlakeside cabin Dan sent?\nBefore someone “gets\nbusy” again',550,502,655,273,538),img(eyes,852,694,57,49),img(rene_small,448,672,58,64)]
priya=group([inktext('Priya',591,825,29,'#888888'),img('assets/priya-memoji.png',428,897,94,94),bubble('Ok we gotta commit 😭',550,863,580,110,900)],5.2,8,keyframes={'opacity':tr((5.2,0),(5.4,1))})
blue=group([bubble('Let’s go! Book it',1040,1033,434,111,1068,True)],6.0,8,keyframes={'opacity':tr((6,0),(6.15,1))})
done=group([inktext('Rene',585,1200,29,'#888888'),bubble('Done. In your calendars',548,1235,660,97,1269),img(rene_small,441,1272,58,64),img(camp,1099,1268,53,51)],6.8,8,keyframes={'opacity':tr((6.8,0),(6.95,1))})
thread +=[priya,blue,done]
chat=group(thread,3.7,8,keyframes={'y':tr((3.7,120),(4,0),(5.2,-260),(6.5,-470),(7,-600),(7.5,-700))})
composer=[dict(type='circle',id=uid('plus-circle'),x=437,y=847,width=120,height=120,fill='#fcfcfc'),rect(477,902,38,6,'#000000',3),rect(493,886,6,38,'#000000',3),rect(580,847,900,120,'#fdfdfd',65),inktext('iMessage',620,882,52,'#cccccc'),rect(1407,875,24,36,'none',12,stroke='#cccccc',strokeWidth=5),dict(type='path',id=uid('mic'),d='M 1398 897 Q 1398 926 1419 926 Q 1440 926 1440 897 M 1419 926 L 1419 938 M 1406 938 L 1432 938',fill='none',stroke='#cccccc',strokeWidth=5)]
keyboard=[rect(395,1008,1144,400,'#e8e8ed',76),inktext('“The”',526,1060,49,'#666666'),inktext('the',937,1060,49,'#666666'),inktext('to',1323,1060,49,'#666666')]+[rect(410+i*111,1146,94,110,'#ffffff',20) for i in range(10)]
lower=group([img('assets/lower-phone-hardware.png',337,0,1256,1080),chat,group(composer,3.7,8,keyframes={'y':tr((3.7,30),(4,0),(6.5,-77),(7.5,-102))}),group(keyboard,3.7,8,keyframes={'y':tr((3.7,30),(4,0),(6.5,-66),(7.5,-90))})],3.7,8,keyframes={'x':tr((3.7,0),(6.5,0),(7.5,-6)),'opacity':tr((3.7,0),(4,1))})
s['layers']=[g for g in s['layers'] if g.get('start') not in [3.6,7.2]]
for g in s['layers']:
 if g.get('start')==1.1:
  g['end']=4;g['keyframes']['scaleX'] +=tr((3.5,1.214),(3.9,1.756));g['keyframes']['scaleY'] +=tr((3.5,1.214),(3.9,1.756));g['keyframes']['x'] +=tr((3.5,535),(3.9,344));g['keyframes']['y'] +=tr((3.5,70),(3.9,-870));g['keyframes']['opacity']=tr((1.1,1),(3.7,1),(4,0))
s['layers'].append(lower)

# The authentic bounded product artwork gives the lockscreen its exact wallpaper and rounded phone.
lock=crop('015.00',(391,0,1531,1020),'authentic-lockscreen-product',kind='bounded static phone/lockscreen artwork; internal UI text is bitmap; outer camera and clipping editable')
messages=crop('014.00',(1060,551,1281,771),'messages-icon-large')
s['layers']=[g for g in s['layers'] if g.get('start')!=13.8]
for g in s['layers']:
 if g.get('start')==12.5:g['end']=13.6
s['layers'].append(group([img(lock,0,0,1140,1020)],13.8,15.37,x=391,clip={'x':0,'y':-550,'width':1140,'height':1570,'radius':175},keyframes={'y':tr((13.8,-1050),(14,-909),(14.4,-400),(14.8,0))}))
watches=inktext('Watches your',321,616,124,'#000000',500);watches['keyframes']={'x':tr((13.6,458),(13.9,321))}
inbox=inktext('inbox',1325,616,124,'#000000',500);inbox['keyframes']={'x':tr((13.6,1188),(13.9,1325))}
# Fit each text segment to the observed source width while retaining editable text.
for t,target in [(watches,686),(inbox,273)]:
 ff=ImageFont.truetype(str(root/'shared/fonts/SF-Pro-Display-Medium.otf'),124);im=Image.new('L',(1800,400));ImageDraw.Draw(im).text((0,0),t['text'],font=ff,fill=255);bb=im.getbbox();t['scaleX']=target/(bb[2]-bb[0])
icon=img(messages,1060,551,221,220,originX=110.5,originY=110,keyframes={'scaleX':tr((13.6,0),(13.9,1)),'scaleY':tr((13.6,0),(13.9,1))})
s['layers'].append(group([watches,icon,inbox],13.6,14.55,keyframes={'y':tr((13.6,-120),(14,0),(14.3,300),(14.55,700))}))

# Thirteen actual portrait discs, measured at21/21.5/22.1, with explicit depth order.
main21={0:(774,90,199,199),1:(1112,156,177,175),2:(710,328,269,269),3:(1174,395,169,169),4:(1150,451,225,225),5:(847,710,230,231),6:(1223,675,154,146),7:(905,854,148,148)}
main215={0:(710,136,191,193),1:(1030,185,219,222),2:(549,402,208,210),3:(1247,445,162,165),4:(877,556,254,248),5:(660,738,191,190),6:(1105,729,179,180),7:(872,808,131,137)}
main221={0:(710,136,191,193),1:(980,270,219,222),2:(527,400,183,185),3:(1220,490,184,186),4:(773,588,239,239),5:(623,725,168,170),6:(1042,770,174,175),7:(849,797,131,137)}
extra=[(8,(657,234,796,375),(1138,415,106,106),(1196,420,106,106)),(9,(944,210,1069,330),(850,234,80,80),(690,162,100,100)),(10,(977,438,1081,539),(874,461,100,100),(955,434,100,100)),(11,(495,402,679,583),(551,383,131,131),(624,350,131,131)),(12,(594,686,744,834),(698,614,105,105),(744,574,105,105))]
paths={i:f'assets/portrait-{i}.png' for i in range(8)}
for i,b,p215,p221 in extra:
 paths[i]=crop('021.00',b,f'portrait-extra-{i}',True,'isolated photographic portrait disc');main21[i]=(b[0],b[1],b[2]-b[0],b[3]-b[1]);main215[i]=p215;main221[i]=p221
faces=[]
for i in [9,8,10,11,12,3,7,6,1,0,5,2,4]:
 natural=Image.open(d/paths[i]).size;pts=[main21[i],main215[i],main221[i]];nw,nh=natural
 face=group([img(paths[i],0,0,nw,nh)],20.5,22.9,shadow={'x':0,'y':18,'blur':16,'color':'#00000024'},keyframes={'x':tr((20.5,960-nw/2),(21,pts[0][0]),(21.5,pts[1][0]),(22.1,pts[2][0])),'y':tr((20.5,540-nh/2),(21,pts[0][1]),(21.5,pts[1][1]),(22.1,pts[2][1])),'scaleX':tr((20.5,.3),(21,pts[0][2]/nw),(21.5,pts[1][2]/nw),(22.1,pts[2][2]/nw)),'scaleY':tr((20.5,.3),(21,pts[0][3]/nh),(21.5,pts[1][3]/nh),(22.1,pts[2][3]/nh)),'opacity':tr((20.5,0),(20.65,1))});faces.append(face)
oldfaces=lambda g:len(g.get('children',[]))==1 and 'portrait-' in g['children'][0].get('src','')
s['layers']=[g for g in s['layers'] if not oldfaces(g)]
insert=next(i for i,g in enumerate(s['layers']) if g.get('start')==21.9);s['layers'][insert:insert]=faces
for g in s['layers']:
 if g.get('start')==18.5:
  g['keyframes']['scaleX']=tr((18.5,1),(20.4,1),(20.9,.5));g['keyframes']['scaleY']=tr((18.5,1),(20.4,1),(20.9,.5))
 if g.get('start')==21.9:
  clone=copy.deepcopy(faces)
  def rename(q):
   q['id']+='-glass-backdrop'
   for z in q.get('children',[]):rename(z)
  for q in clone:rename(q)
  g['children'][1]['children']=clone

# Measure per-frame native text poses from the reference. Rebuild as editable text, not reference frames.
def clusters(arr,dark=False):
 gray=np.mean(arr[:,:,:3],axis=2);mask=gray<230 if dark else gray>25;xs=np.where(mask.any(axis=0))[0];groups=[]
 for x in xs:
  if not groups or x-groups[-1][-1]>22:groups.append([x])
  else:groups[-1].append(x)
 out=[]
 for cc in groups:
  x0,x1=cc[0],cc[-1]+1;yy,xx=np.where(mask[:,x0:x1])
  if len(yy)<100:continue
  y0,y1=int(yy.min()),int(yy.max())+1;vals=gray[y0:y1,x0:x1][mask[y0:y1,x0:x1]];color=int(np.percentile(vals,5 if dark else 95));out.append({'box':[int(x0+200),y0+300,int(x1),y1],'x0':int(x0),'x1':int(x1),'y0':y0,'y1':y1,'color':max(0,min(255,color))})
 return out
tracks={};icontracks=[];measurements=[]
for p in sorted((d/'black-word-measurements').glob('*.png')):
 t=41+(int(p.stem)-1)/30;arr=np.asarray(Image.open(p).convert('RGB'));cc=clusters(arr)
 if t<43.3:
  names=['Does','the','work','for','you'][:len(cc)] if len(cc)<=5 else ['Does','the','__briefcase__','work','for','you']
 else:names=['Lives','where','you2'] if len(cc)==3 else []
 if len(names)!=len(cc):continue
 for name,b in zip(names,cc):
  x,y=b['x0']+200,b['y0']+300;row={'t':t,'x':x,'y':y,'width':b['x1']-b['x0'],'height':b['y1']-b['y0'],'color':b['color']};measurements.append({'name':name,**row})
  if name=='__briefcase__':icontracks.append(row)
  else:tracks.setdefault(name,[]).append(row)
# Authentic isolated icon, independent native transformations and no placeholder glyph.
if icontracks:
 pick=min(icontracks,key=lambda q:abs(q['t']-42.5));n=round((pick['t']-41)*30)+1;a=np.asarray(Image.open(d/f'black-word-measurements/{n:03d}.png').convert('RGB'));x0=pick['x']-200;y0=pick['y']-300;art=a[y0:y0+pick['height'],x0:x0+pick['width']];alpha=np.clip((art.mean(axis=2)-9)*255/246,0,255).astype('uint8');rgba=np.full((*alpha.shape,4),255,dtype='uint8');rgba[:,:,3]=alpha;Image.fromarray(rgba).save(d/'assets/briefcase-source-icon.png');prov.append({'path':'assets/briefcase-source-icon.png','timestamp':pick['t'],'box':[pick['x'],pick['y'],pick['x']+pick['width'],pick['y']+pick['height']],'kind':'isolated white briefcase icon'})
# Delete faded-background groups. The stage remains opaque while word layers animate.
s['layers']=[g for g in s['layers'] if g.get('start') not in [mt(41),mt(43.35)]]
s['layers'].append(group([rect(0,0,1920,1080,'#090909')],41,44.4))
font=ImageFont.truetype(str(root/'shared/fonts/SF-Pro-Display-Medium.otf'),124)
for name,rows in tracks.items():
 word='you' if name=='you2' else name;im=Image.new('L',(1200,400));ImageDraw.Draw(im).text((0,0),word,font=font,fill=255);bb=im.getbbox();iw,ih=bb[2]-bb[0],bb[3]-bb[1];keys={'x':[],'y':[],'scaleX':[],'scaleY':[],'fill':[]}
 for a in rows:
  sx,sy=a['width']/iw,a['height']/ih;t=mt(a['t']);keys['x'].append({'t':t,'value':a['x']-bb[0]*sx});keys['y'].append({'t':t,'value':a['y']-bb[1]*sy});keys['scaleX'].append({'t':t,'value':sx});keys['scaleY'].append({'t':t,'value':sy});keys['fill'].append({'t':t,'value':'#'+f'{a["color"]:02x}'*3})
 q=txt(word,0,0,124,'#ffffff',500,keyframes=keys);q.update(start=mt(rows[0]['t']),end=mt(rows[-1]['t']+1/30));s['layers'].append(q)
if icontracks:
 iw,ih=Image.open(d/'assets/briefcase-source-icon.png').size;q=img('assets/briefcase-source-icon.png',0,0,iw,ih,start=mt(icontracks[0]['t']),end=mt(icontracks[-1]['t']+1/30));q['keyframes']={k:[{'t':mt(a['t']),'value':a[k] if k in ['x','y'] else a['width']/iw if k=='scaleX' else a['height']/ih} for a in icontracks] for k in ['x','y','scaleX','scaleY']};s['layers'].append(q)
(d/'native-black-word-tracks.json').write_text(json.dumps(measurements,indent=2))

# Original brand wordmark, revealed with an independently editable cover mask; exact source exit49.0.
word=crop('048.50',(893,485,1260,607),'rene-original-wordmark',kind='original brand wordmark artwork; mask and transform editable')
s['layers']=[g for g in s['layers'] if g.get('start')!=mt(47.4)]
logo_measure=json.loads((root/'verification/fidelity-review/06-gallery/end-timing/logo-measurements.json').read_text())['frames']
mascotrows=[];wordrows=[]
for p in sorted((root/'verification/fidelity-review/06-gallery/end-timing').glob('logo-*.png')):
 frame=int(p.stem.split('-')[-1]);t=frame/30
 if t>=49:continue
 cc=clusters(np.asarray(Image.open(p).convert('RGB')),True)
 if cc:
  b=cc[0];mascotrows.append({'t':t,'x':b['x0']+200,'y':b['y0']+300,'w':b['x1']-b['x0'],'h':b['y1']-b['y0']})
 if len(cc)>1:
  b=cc[1];wordrows.append({'t':t,'x':b['x0']+200,'y':b['y0']+300,'w':b['x1']-b['x0'],'h':b['y1']-b['y0']})
asset=Image.open(d/'assets/rene-mascot.png').convert('RGBA');mm=np.asarray(asset)[:,:,3]>25;yy,xx=np.where(mm);bb=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1];iw,ih=bb[2]-bb[0],bb[3]-bb[1]
if mascotrows:
 q=img('assets/rene-mascot.png',0,0,asset.width,asset.height,start=mt(47.4),end=mt(49));q['keyframes']={'x':[{'t':mt(a['t']),'value':a['x']-bb[0]*a['w']/iw} for a in mascotrows],'y':[{'t':mt(a['t']),'value':a['y']-bb[1]*a['h']/ih} for a in mascotrows],'scaleX':[{'t':mt(a['t']),'value':a['w']/iw} for a in mascotrows],'scaleY':[{'t':mt(a['t']),'value':a['h']/ih} for a in mascotrows]};s['layers'].append(q)
if wordrows:
 wi=Image.open(d/word).convert('RGB');mask=np.min(np.asarray(wi),axis=2)<230;yy,xx=np.where(mask);left,top=int(xx.min()),int(yy.min());cover=rect(367,0,0,122,'#ffffff',keyframes={'x':[{'t':mt(a['t']),'value':a['w']+left} for a in wordrows],'width':[{'t':mt(a['t']),'value':max(0,367-a['w']-left)} for a in wordrows]});g=group([img(word,0,0,367,122),cover],wordrows[0]['t'],49,keyframes={'x':[{'t':mt(a['t']),'value':a['x']-left} for a in wordrows],'y':[{'t':mt(a['t']),'value':a['y']-top} for a in wordrows]});s['layers'].append(g)
s['source']['notes']+=' Finalv11 closes measured broad-review failures: continuous native intro scroll/message timing; authentic bounded lockscreen artwork with editable rounded clip/camera; thirteen actual portrait discs and measured orbits; every-frame native word pose/fill tracks over an opaque black background; actual briefcase icon and measured original brand reveal/exit. Internal lockscreen text is bitmap.'
(d/'scene.json').write_text(json.dumps(s,indent=2));(d/'assets/asset-provenance.json').write_text(json.dumps(prov,indent=2));print('Rene v11 broad corrections',len(tracks),'word tracks',len(faces),'portraits')
