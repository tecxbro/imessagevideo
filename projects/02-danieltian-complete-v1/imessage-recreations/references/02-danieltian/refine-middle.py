"""ID-scoped middle reconstruction from exact source measurements; native UI geometry and semantic glyph contours."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,json,copy,re,sys,hashlib
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations/references/02-danieltian');M=R/'assets/middle-measure';A=R/'assets/middle-art';A.mkdir(exist_ok=True);BASE=R/'scene-final-v9.json';scene=json.loads(BASE.read_text());orig={l['id']:l for l in scene['layers']};D=json.loads((R/'middle-measurements.json').read_text());RUNS=json.loads((R/'middle-body-runs.json').read_text());patch={};ledger=[];gradients=[]
def rgb(n):return np.array(Image.open(M/f'source-{n:04d}.png').convert('RGB'))
def asset(n,box,name,matte=None):
 a=Image.fromarray(rgb(n)).crop(tuple(map(int,box))).convert('RGBA')
 if matte is not None:a.putalpha(matte)
 p=A/(name+'.png');a.save(p);ledger.append(dict(kind='bounded original graphic artwork',sourceFrame=n,sourceBounds=list(map(int,box)),asset=str(p),editability='Independent bitmap graphic artwork; no complete reference frame.'));return dict(type='image',id='middle-art-'+name,src=str(p),x=box[0],y=box[1],width=box[2]-box[0],height=box[3]-box[1],sourceFrame=n,sourceBounds=list(map(int,box)))
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
def circles(n):
 a=rgb(n).astype(float);masks={'lyft':(a[:,:,0]>170)&(a[:,:,2]>120)&(a[:,:,1]<90),'airbnb':(a[:,:,0]>160)&(a[:,:,1]<120)&(a[:,:,2]>65)&(a[:,:,2]<170),'resy':(a[:,:,0]>175)&(a[:,:,1]<120)&(a[:,:,2]<a[:,:,0]*.30),'green':(a[:,:,1]>220)&(a[:,:,0]<190)&(a[:,:,2]<150)};out={}
 for name,mask in masks.items():
  mask=ndimage.binary_closing(mask,iterations=2);lab,num=ndimage.label(mask,np.ones((3,3)));areas=np.bincount(lab.ravel());cc=[]
  for li,sl in enumerate(ndimage.find_objects(lab),1):
   if not sl:continue
   y,x=sl;w=x.stop-x.start;h=y.stop-y.start
   if w>25 and h>25 and areas[li]>300 and .5<w/h<1.7:cc.append([x.start,y.start,x.stop,y.stop])
  out[name]=cc
 return out
CIRC={}
for n in range(540,1021,15):
 CIRC[n]=circles(n) if n<=615 or n==675 else dict(green=[c['box'] for c in D[str(n)]['components'] if c['cls']=='green'],lyft=[],airbnb=[],resy=[])
# Canonical original header artwork: two separate bounded graphic pieces, matte limited to the avatar circle and glass title capsule.
for name,box,shape in [('header-circle',(835,46,1088,300),'circle'),('header-title',(690,258,1230,358),'pill')]:
 w,h=box[2]-box[0],box[3]-box[1];matte=Image.new('L',(w*4,h*4));draw=ImageDraw.Draw(matte)
 if shape=='circle':draw.ellipse((0,0,w*4-1,h*4-1),fill=255)
 else:draw.rounded_rectangle((0,0,w*4-1,h*4-1),radius=49*4,fill=255)
 globals()[name.replace('-','_')]=asset(675,box,name,matte.resize((w,h),Image.Resampling.LANCZOS))
baseGreen=min(CIRC[675]['green'],key=lambda b:abs((b[0]+b[2])/2-915));header_ms=[]
for n,cc in CIRC.items():
 if n<600:continue
 choices=[b for b in cc['green'] if 750<(b[0]+b[2])/2<1100 and b[1]<400]
 if not choices:continue
 b=min(choices,key=lambda q:abs((q[0]+q[2])/2-915));sx=(b[2]-b[0])/(baseGreen[2]-baseGreen[0]);sy=(b[3]-b[1])/(baseGreen[3]-baseGreen[1]);header_ms.append(dict(t=n/30,x=b[0]-baseGreen[0]*sx,y=b[1]-baseGreen[1]*sy,scaleX=sx,scaleY=sy))
patch['group-1077']=dict(id='group-1077',type='group',children=[header_circle,header_title],start=19.95,end=34.2,keyframes={k:[dict(t=m['t'],value=m[k]) for m in header_ms] for k in ['x','y','scaleX','scaleY']},editability='Native header pose; original separately editable avatar-cluster and glass-title artwork. Glass refraction inside the static artwork is not a live backdrop shader.')
# Independently measured entering agents. They remain separate from the search capsule and assembled group header.
fly=[]
for name in ['lyft','airbnb','resy','green']:
 b=min(CIRC[675][name],key=lambda q:abs((q[0]+q[2])/2-(915 if name=='green' else 1010)));pad=3;box=(b[0]-pad,b[1]-pad,b[2]+pad,b[3]+pad);w=box[2]-box[0];h=box[3]-box[1];matte=Image.new('L',(w*4,h*4));ImageDraw.Draw(matte).ellipse((0,0,w*4-1,h*4-1),fill=255);node=asset(675,box,'fly-'+name,matte.resize((w,h),Image.Resampling.LANCZOS));node['x']=node['y']=0;ms=[]
 for n in range(540,616,15):
  choices=CIRC[n][name]
  if not choices:continue
  q=max(choices,key=lambda q:(q[2]-q[0])*(q[3]-q[1]));hh=q[3]-q[1];ww=q[2]-q[0]
  if q[2]>1916:ww=hh
  if q[0]<4:ww=hh;q=[q[2]-ww,q[1],q[2],q[3]]
  ms.append(dict(t=n/30,x=q[0]-pad*ww/(b[2]-b[0]),y=q[1]-pad*hh/(b[3]-b[1]),scaleX=ww/(b[2]-b[0]),scaleY=hh/(b[3]-b[1])))
 if ms:fly.append(dict(id='middle-fly-'+name,type='group',children=[node],start=max(18.25,ms[0]['t']-.12),end=20.0,keyframes={k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']}))
# Muse's white circle crosses the viewport from outside its edge; fit its actual gray circular outline, never stretch a clipped arc to a full avatar.
muse_ms=[]
for n in [555,570,585,600]:
 a=rgb(n).astype(float);mask=(a.min(2)>155)&(a.max(2)<245)&(a.max(2)-a.min(2)<10);lab,num=ndimage.label(mask,np.ones((3,3)));candidates=[]
 for li,sl in enumerate(ndimage.find_objects(lab),1):
  if not sl:continue
  y,x=sl;w=x.stop-x.start;h=y.stop-y.start
  if w>100 and h>15 and (n!=555 or y.stop<100) and (n!=570 or y.start>800) and (n!=585 or 300<y.start<700) and (n!=600 or 800<x.start<1100):candidates.append((abs(w-h),li,sl))
 if not candidates:continue
 _,li,sl=min(candidates);ys,xs=np.where(lab==li);fit=np.linalg.lstsq(np.stack([2*xs,2*ys,np.ones(len(xs))],1),xs*xs+ys*ys,rcond=None)[0];cx,cy,c=fit;rad=np.sqrt(max(1,c+cx*cx+cy*cy));muse_ms.append(dict(t=n/30,x=float(cx-rad),y=float(cy-rad),scaleX=float(2*rad/235),scaleY=float(2*rad/236)))
mu=asset(585,(1038,379,1273,615),'fly-muse');mu['x']=mu['y']=0;fly.append(dict(id='middle-fly-muse',type='group',children=[mu],start=18.3,end=20.0,keyframes={k:[dict(t=m['t'],value=m[k]) for m in muse_ms] for k in ['x','y','scaleX','scaleY']}));patch['group-1068']=dict(id='group-1068',type='group',children=fly,start=18.25,end=20.)
# Preserve the actual blurred search state after the selected capsules collapse.
query=asset(540,(405,248,1515,396),'search-query');query.update(id='pb-result-search',start=17.15,end=18.8,keyframes={'opacity':[dict(t=17.15,value=0),dict(t=17.45,value=1),dict(t=18.15,value=1),dict(t=18.5,value=.65),dict(t=18.75,value=0)],'blur':[dict(t=18.15,value=0),dict(t=18.5,value=7),dict(t=18.75,value=12)]});oldquery=copy.deepcopy(orig['pb-result-search']);oldquery['id']='middle-query-before-18';oldquery['end']=18.
if oldquery.get('src') and not str(oldquery['src']).startswith('/'):oldquery['src']=str((BASE.parent/oldquery['src']).resolve())
query['id']='middle-query-after-18';query['start']=18.;patch['pb-result-search']=dict(id='pb-result-search',type='group',children=[oldquery,query],start=oldquery.get('start',17.15),end=18.8)
# Correct source18.0 capsule collapse and checked-control retirement while preserving earlier phonebook edits.
for name,target in [('lyft',211),('airbnb',339),('resy',451)]:
 lid='pb-capsule-'+name;l=copy.deepcopy(orig[lid]);children=l['children']
 for c in children:
  if 'check' in c['id']:c.setdefault('keyframes',{})['opacity']=[q for q in c.get('keyframes',{}).get('opacity',[]) if q['t']<18]+[dict(t=18,value=0,ease='hold')]
 sparse=[dict(t=17.75,value=604),dict(t=18,value=target),dict(t=18.3,value=117)];widths=[]
 for fn in range(532,552):
  tt=fn/30
  if tt<=sparse[0]['t']:val=sparse[0]['value']
  elif tt>=sparse[-1]['t']:val=sparse[-1]['value']
  else:
   aa,bb=next((aa,bb) for aa,bb in zip(sparse,sparse[1:]) if aa['t']<=tt<=bb['t']);f=(tt-aa['t'])/(bb['t']-aa['t']);val=aa['value']+(bb['value']-aa['value'])*f
  widths.append(dict(t=tt,value=val))
 inner=dict(id=lid+'-content-compensation',type='group',children=children,keyframes={'scaleX':[dict(t=q['t'],value=604/q['value']) for q in widths]});clip=dict(id=lid+'-collapsing-clip',type='group',clip=dict(x=0,y=0,width=604,height=117,radius=58),children=[inner],keyframes={'scaleX':[dict(t=q['t'],value=q['value']/604) for q in widths]});l['children']=[clip,dict(id=lid+'-closing-border',type='rect',fill='none',stroke='#EEEEEE',strokeWidth=1.5,width=604,height=117,radius=58.5,start=18,end=18.35,keyframes={'width':widths})];patch[lid]=l
# Repair ambiguous OCR names by source row order; all measurements remain exact decoded-frame positions.
for ns,q in RUNS.items():
 n=int(ns);rr=q['runs']
 if n==735:
  for r,name in zip(rr,['kickoff','airbnb-command','lyft-command','resy-command','budget']):r['name']=name
 if n==765:
  for r,name in zip(rr,['airbnb-command','lyft-command','resy-command','budget']):r['name']=name
 if n in [780,795,810] and rr:rr[0]['name']='airbnb-command'
 if n==825 and rr:rr[0]['name']='lyft-command'
 if n==870:rr.insert(0,dict(y=0,height=43,name='budget',text='Source clipped Budget card'))
 if n==960 and rr:rr[-1]['name']='airbnb-booked'
 if n==990 and rr:rr[-1]['name']='resy-booked'
# Every element continues through camera motion until it actually leaves the viewport.
CANON={'kickoff':(675,953),'airbnb-command':(690,924),'lyft-command':(690,1007),'resy-command':(735,647),'budget':(780,261),'how-about':(885,452),'airbnb-booked':(1005,235),'lyft-booked':(1005,704),'resy-booked':(1005,432)}
COPY={'kickoff':'hey team, @Justina needs a Photon\nteam offsite. Tomorrow.','airbnb-command':'@Airbnb find a place in Tahoe for 9','lyft-command':'@Lyft 2 XL rides from 880 Harrison St,\n9am tomorrow','resy-command':'@Resy find a sushi spot.\nThe team loves sushi','budget':'Budget?','how-about':'How about this one?','airbnb-booked':'Booked✅','lyft-booked':'2 XLs booked.\nPhoton HQ → Airbnb in Tahoe, 9am✅','resy-booked':'Sushi for 9, booked🍣'}
START={'kickoff':21.28,'airbnb-command':22.2,'lyft-command':22.72,'resy-command':23.3,'budget':24.35,'how-about':28.85,'airbnb-booked':31.8,'lyft-booked':32.4,'resy-booked':32.9};END={'kickoff':25.35,'airbnb-command':27.25,'lyft-command':28.05,'resy-command':28.5,'budget':29.3,'how-about':34.2,'airbnb-booked':34.2,'lyft-booked':34.2,'resy-booked':34.2}
MS={};BODY={};middle=[]
def body_parts(n,left,top,width,height,semantic,name,kind='gray'):
 a=rgb(n);pad=4;roi=a[max(0,int(top)-pad):min(1080,int(top+height)+30),int(left)-pad:int(left+width)+pad];row0=max(0,int(top)-pad);col0=int(left)-pad;bgsel=(roi.min(2)>180)&(roi.max(2)<248)&(roi.max(2)-roi.min(2)<25)
 if kind=='gray':
  vals,cnt=np.unique(roi[bgsel],axis=0,return_counts=True);bg=vals[cnt.argmax()] if len(vals) else np.array([231,230,234]);mask=roi.min(2)<246
 else:
  vals=roi[(roi[:,:,2]-roi[:,:,0].astype(float)>70)&(roi[:,:,0]<120)];bg=np.median(vals,0).astype(int);mask=ndimage.binary_fill_holes((roi[:,:,2]-roi[:,:,0].astype(float)>70)&(roi[:,:,0]<120))
 cy=mask[:,int(width/2)+pad];ys=np.flatnonzero(cy);ctop=int(ys.min()+row0);cbot=int(ys.max()+row0+1);coreH=cbot-ctop;left=int(left);width=int(width);crop=a[ctop:cbot,left:left+width].astype(float);children=[]
 fill='#'+''.join(f'{int(v):02x}' for v in bg)
 if kind=='blue':
  gid='middle-blue-'+name;stops=[]
  for f in [0.05,.5,.95]:
   row=crop[min(coreH-1,int(coreH*f))];sel=(row[:,2]-row[:,0]>70)&(row[:,0]<120);color=np.median(row[sel],axis=0).astype(int) if sel.any() else bg;stops.append(dict(offset=str(int(f*100))+'%',color='#'+''.join(f'{v:02x}' for v in color)))
  gradients.append(dict(id=gid,type='linear',x1='0%',x2='0%',y1='0%',y2='100%',stops=stops));fill='url(#'+gid+')'
 children.append(dict(id='middle-body-'+name,type='rect',width=width,height=coreH,radius=min(coreH/2,70*RUNS[str(n)]['scale']),fill=fill))
 # Native semantic type contours. Source background is excluded algebraically; the blue mention and colorful emoji stay independent.
 if kind=='gray':alpha=np.clip((float(bg.mean())-crop.mean(2))/float(bg.mean()),0,1);alpha[crop.max(2)-crop.min(2)>35]=0;textfill='#000000'
 else:alpha=np.clip((crop[:,:,0]-int(bg[0]))/(255-int(bg[0])),0,1);textfill='#FFFFFF'
 d,stats=trace_alpha(alpha);children.append(dict(id='middle-glyphs-'+name,type='path',d=d,fill=textfill,semanticText=semantic,sourceFrame=n,editability='Native editable semantic glyph contours, not live font text.'))
 color=(crop[:,:,2]-crop[:,:,0]>50)&(crop[:,:,1]-crop[:,:,0]>20)
 if kind=='gray' and color.any():
  vals,cnt=np.unique(crop[color].astype('uint8'),axis=0,return_counts=True);blue=vals[cnt.argmax()];aa=np.clip((int(bg[0])-crop[:,:,0])/(int(bg[0])-int(blue[0])),0,1);aa*=ndimage.binary_dilation(color,iterations=2);d,st=trace_alpha(aa);children.append(dict(id='middle-blue-mention-'+name,type='path',d=d,fill='#'+''.join(f'{v:02x}' for v in blue),semanticText='@Justina',sourceFrame=n))
 # Original color emoji fragments, individually bounded; black body copy remains native contours.
 emoji=(crop.max(2)-crop.min(2)>35)&~color if kind=='gray' else np.zeros(crop.shape[:2],bool);labels,num=ndimage.label(ndimage.binary_dilation(emoji,iterations=1),np.ones((3,3)))
 for li,sl in enumerate(ndimage.find_objects(labels),1):
  if not sl:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if w<8 or h<8:continue
  b=(max(left,left+xx.start-2),max(ctop,ctop+yy.start-2),min(left+width,left+xx.stop+2),min(cbot,ctop+yy.stop+2));im=asset(n,b,name+'-emoji-'+str(li));im['x']-=left;im['y']-=ctop;children.append(im)
 ledger.append(dict(kind='native message geometry and semantic glyphs',semanticText=semantic,sourceFrame=n,sourceBounds=[left,ctop,left+width,cbot],fill=fill,**stats));return children,ctop,coreH,bg
for name,(cn,cw) in CANON.items():
 cq=RUNS[str(cn)];cr=next(r for r in cq['runs'] if r['name']==name);children,cy,ch,bg=body_parts(cn,cq['left'],cr['y'],cw,cr['height'],COPY[name],name);scan=cq['scale'];ms=[]
 for ns,q in RUNS.items():
  n=int(ns);rr=[r for r in q['runs'] if r['name']==name]
  if not rr:continue
  r=rr[0];ratio=q['scale']/scan;y=float(r['y']+(cy-cr['y'])*ratio)
  if r['y']<=3:y=r['y']+r['height']-ch*ratio
  ms.append(dict(t=n/30,x=float(q['left']),y=y,scaleX=ratio,scaleY=ratio))
 ms.sort(key=lambda m:m['t']);BODY[name]=dict(cn=cn,left=cq['left'],top=cy,width=cw,height=ch,scale=scan,bg=bg.tolist(),children=children);MS[name]=ms
 # Spring in the incoming second bubble changes its capsule padding slightly, while glyphs retain the measured camera scale.
 if name=='airbnb-command':children[0]['keyframes']={'scaleX':[dict(t=22.2,value=1),dict(t=22.5,value=1.035),dict(t=23.,value=1)],'scaleY':[dict(t=22.2,value=1),dict(t=22.5,value=1.027),dict(t=23.,value=1)]}
 node=dict(id='middle-message-'+name,type='group',children=children,start=START[name],end=END[name],keyframes={k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']});middle.append(node)
# One authentic native Messages tail fragment, normalized to source-world units, remains separate so only the most recent Muse bubble has a tail.
a=rgb(675).astype(float);box=(407,694,517,784);tile=a[box[1]:box[3],box[0]:box[2]];bg=np.array(BODY['airbnb-command']['bg']);aa=np.clip((255-tile.mean(2))/(255-bg.mean()),0,1);aa[ndimage.binary_fill_holes(aa>.35)]=1;d,stats=trace_alpha(aa,box[0]-417,box[1]-749)
for name,end in [('kickoff',22.2),('airbnb-command',22.72),('lyft-command',23.3),('resy-command',28.5),('budget',29.3),('how-about',34.2),('airbnb-booked',34.2),('lyft-booked',34.2),('resy-booked',34.2)]:
 node=next(l for l in middle if l['id']=='middle-message-'+name);b=BODY[name];tail=dict(id='middle-tail-'+name,type='path',d=d,fill='#'+''.join(f'{v:02x}' for v in b['bg']),y=b['height'],scaleX=b['scale'],scaleY=b['scale'],start=START[name],end=end);node['children'].insert(1,tail)
# Labels are outlined source glyphs and use the same native pose as their corresponding response bubble.
for name,cn,roi,text in [('kickoff',675,(430,307,570,365),'Muse'),('budget',780,(460,490,640,555),'Resy'),('airbnb-booked',1005,(560,335,720,390),'Airbnb'),('lyft-booked',1005,(560,520,700,578),'Lyft'),('resy-booked',1005,(560,760,700,815),'Resy')]:
 b=BODY[name];a=rgb(cn);x0,y0,x1,y1=roi;aa=np.clip((253-a[y0:y1,x0:x1].mean(2))/253,0,1);d,stats=trace_alpha(aa,x0-b['left'],y0-b['top']);node=next(l for l in middle if l['id']=='middle-message-'+name);node['children'].append(dict(id='middle-agent-label-'+name,type='path',d=d,fill='#000000',semanticText=text,sourceFrame=cn))
# Outgoing bubbles survive the subsequent card reveal until they scroll away.
for name,cn,semantic,st,en in [('budget-reply',780,'~$100 per person',25.35,29.9),('love-it',930,'Love it',30.4,33.5)]:
 co=max((c for c in D[str(cn)]['components'] if c['cls']=='blue'),key=lambda c:c['area']);bb=co['box'];children,cy,ch,bg=body_parts(cn,bb[0],bb[1],bb[2]-bb[0],bb[3]-bb[1],semantic,name,'blue');scan=RUNS[str(cn)]['scale'];ms=[];widthkeys=[]
 for ns,q in RUNS.items():
  n=int(ns)
  if not(st<=n/30<en):continue
  cc=[c for c in D[ns]['components'] if c['cls']=='blue' and c['box'][2]-c['box'][0]>130 and c['box'][3]-c['box'][1]>65 and c['box'][0]>900]
  if not cc:continue
  c=max(cc,key=lambda c:c['area']);b=c['box'];ratio=q['scale']/scan;ms.append(dict(t=n/30,x=b[0],y=b[1],scaleX=ratio,scaleY=ratio));widthkeys.append(dict(t=n/30,value=(b[2]-b[0])/ratio))
 children[0]['keyframes']={'width':widthkeys};children[1]['keyframes']={'opacity':[dict(t=st,value=0),dict(t=25.8 if name=='budget-reply' else 30.7,value=0),dict(t=25.95 if name=='budget-reply' else 30.9,value=1)]};middle.append(dict(id='middle-message-'+name,type='group',children=children,start=st,end=en,keyframes={k:[dict(t=m['t'],value=m[k]) for m in ms] for k in ['x','y','scaleX','scaleY']}));BODY[name]=dict(cn=cn,left=bb[0],top=cy,width=bb[2]-bb[0],height=ch,scale=scan,bg=bg.tolist());MS[name]=ms
# Faded outgoing replies still obey the shared source camera after blue detection becomes too pale.
for name,anchor,endtime in [('budget-reply',870,30.0),('love-it',930,33.5)]:
 n0=anchor;t0=n0/30;bm=min(MS[name],key=lambda m:abs(m['t']-t0));hm=min(MS['how-about'],key=lambda m:abs(m['t']-t0));ss=RUNS[str(n0)]['scale'];worldx=(bm['x']-960*(1-ss))/ss;dy=(bm['y']-hm['y'])/ss
 for ns,q in RUNS.items():
  n=int(ns);t=n/30
  if t<=MS[name][-1]['t'] or t>endtime:continue
  hh=[m for m in MS['how-about'] if abs(m['t']-t)<.001]
  if hh:MS[name].append(dict(t=t,x=960+(worldx-960)*q['scale'],y=hh[0]['y']+dy*q['scale'],scaleX=q['scale']/BODY[name]['scale'],scaleY=q['scale']/BODY[name]['scale']))
 node=next(l for l in middle if l['id']=='middle-message-'+name);node['end']=endtime;node['keyframes']={k:[dict(t=m['t'],value=m[k]) for m in MS[name]] for k in ['x','y','scaleX','scaleY']}
 if name=='love-it':node['keyframes']['opacity']=[dict(t=30.4,value=1),dict(t=32.5,value=1),dict(t=33.,value=.35),dict(t=33.5,value=0)]
 # Independent native outgoing tail from the actual source blue bubble.
 b=BODY[name];cn=b['cn'];ar=rgb(cn).astype(float);x0=int(b['left']+b['width']-100);y0=int(b['top']+b['height']-40);x1=min(1920,int(b['left']+b['width']+15));y1=min(1080,int(b['top']+b['height']+30));rr=ar[y0:y1,x0:x1];aa=np.clip((255-rr[:,:,0])/(255-b['bg'][0]),0,1);aa[ndimage.binary_fill_holes(aa>.35)]=1;dd,stt=trace_alpha(aa,x0-b['left'],y0-b['top']);tail=dict(id='middle-outgoing-tail-'+name,type='path',d=dd,fill='#'+''.join(f'{v:02x}' for v in b['bg']),keyframes={'x':[dict(t=q['t'],value=q['value']-b['width']) for q in node['children'][0]['keyframes']['width']]});node['children'].insert(1,tail)
# At33s Resy is typing; its final confirmation arrives later.
rnode=next(l for l in middle if l['id']=='middle-message-resy-booked');rnode['children'][0]['keyframes']={'width':[dict(t=32.9,value=175),dict(t=33.,value=175),dict(t=33.4,value=432)],'height':[dict(t=32.9,value=93),dict(t=33.,value=93),dict(t=33.4,value=101)]}
for c in rnode['children']:
 if c['id'].startswith(('middle-glyphs-','middle-art-resy-booked-emoji')):c.setdefault('keyframes',{})['opacity']=[dict(t=32.9,value=0),dict(t=33.25,value=0),dict(t=33.4,value=1)]
for i in range(3):rnode['children'].append(dict(id='middle-resy-typing-dot-'+str(i),type='circle',x=51+i*30,y=40,width=14,height=14,fill='#B4B4B8',start=32.9,end=33.3))
# Original rich-link product artwork is a single bounded card, independently transformed; its bitmap UI text is declared.
card=asset(855,(515,462,1252,1008),'airbnb-reservation-card');card['x']=card['y']=0;cms=[dict(t=28.5,x=515,y=462,scaleX=1,scaleY=1)];s0=RUNS['855']['scale']
for ns,q in RUNS.items():
 n=int(ns)
 if n<870:continue
 rr=[r for r in q['runs'] if r['name']=='how-about']
 if not rr:continue
 ratio=q['scale']/s0*.98;bottom=rr[0]['y']-34*q['scale'];cms.append(dict(t=n/30,x=q['left'],y=bottom-546*ratio,scaleX=ratio,scaleY=ratio))
# The entry pose differs slightly from the held rich-link shape. Keep authentic held pixels outside the header, and reconstruct only its hidden underlay from the clean earlier card.
baseart=Image.open(A/'airbnb-reservation-card.png').convert('RGB').resize((693,514),Image.Resampling.LANCZOS);held=Image.fromarray(rgb(885)).crop((533,213,1226,727));hm=min(header_ms,key=lambda q:abs(q['t']-29.5));matte=Image.new('L',(1920,1080));draw=ImageDraw.Draw(matte)
def hb(box):return tuple([box[0]*hm['scaleX']+hm['x'],box[1]*hm['scaleY']+hm['y'],box[2]*hm['scaleX']+hm['x'],box[3]*hm['scaleY']+hm['y']])
draw.ellipse(hb((835,46,1088,300)),fill=255);draw.rounded_rectangle(hb((690,258,1230,358)),radius=49*hm['scaleX'],fill=255);held.paste(baseart,(0,0),matte.crop((533,213,1226,727)));heldpath=A/'airbnb-reservation-held.png';held.save(heldpath);card['src']=str(heldpath);card['width']=693;card['height']=514
for m in cms:m['scaleX']*=737/693;m['scaleY']*=546/514
cms.insert(0,dict(t=28.25,x=511,y=740,scaleX=.4*737/693,scaleY=.4*546/514));ledger.append(dict(kind='bounded held product artwork with occluded underlay reconstruction',sourceFrame=885,sourceBounds=[533,213,1226,727],asset=str(heldpath),underlaySourceFrame=855,underlayLimit='Only the area occluded by the independently rendered header is inferred from the clean earlier card.'))
middle.append(dict(id='middle-airbnb-rich-card',type='group',children=[card],start=28.25,end=33.3,keyframes={k:[dict(t=m['t'],value=m[k]) for m in cms] for k in ['x','y','scaleX','scaleY']},editability='Independent original rich-link product artwork; bitmap internal product UI/text.'))
# Camera-correct circular participant avatars; each response keeps its own avatar when a new agent enters.
def avatar_node(name,src,poses,st,en):
 return dict(id='middle-avatar-'+name,type='group',children=[dict(id='middle-avatar-image-'+name,type='image',src=str(src),width=126,height=126)],start=st,end=en,keyframes={k:[dict(t=m['t'],value=m[k]) for m in poses] for k in ['x','y','scaleX','scaleY']})
def avatar_poses(names):
 poses=[]
 for ns,q in RUNS.items():
  n=int(ns);available=[]
  for name in names:
   mm=[m for m in MS[name] if abs(m['t']-n/30)<.001]
   if mm:available.append((names.index(name),name,mm[0]))
  if not available:continue
  _,name,m=max(available);b=BODY[name];S=q['scale'];poses.append(dict(t=n/30,x=960+(267-960)*S,y=m['y']+b['height']*m['scaleY']-126*S,scaleX=S,scaleY=S))
 return poses
middle.append(avatar_node('muse',R/'assets/muse-full-avatar.png',avatar_poses(['kickoff','airbnb-command','lyft-command','resy-command']),21.0,28.5))
for name,src in [('budget','resy.png'),('how-about','airbnb.png'),('airbnb-booked','airbnb.png'),('lyft-booked','lyft.png'),('resy-booked','resy.png')]:middle.append(avatar_node(name,R/'assets'/src,avatar_poses([name]),START[name],END[name]))
# Exact source reaction artwork, independently attached to the corresponding source message pose.
for name,cn,box,parent,st,en in [('command-like',735,(1310,367,1450,526),'airbnb-command',23.8,27.8),('budget-like',810,(1068,665,1195,803),'budget-reply',26.85,29.9)]:
 raw=rgb(cn)[box[1]:box[3],box[0]:box[2]];mask=ndimage.binary_dilation(raw.min(2)<248,iterations=6);im=asset(cn,box,name,Image.fromarray(mask.astype('uint8')*255));b=BODY[parent];mm=min(MS[parent],key=lambda m:abs(m['t']-cn/30));dx=(box[0]-mm['x'])/mm['scaleX'];dy=(box[1]-mm['y'])/mm['scaleY'];im['x']=dx;im['y']=dy;im['width']/=mm['scaleX'];im['height']/=mm['scaleY'];middle.append(dict(id='middle-reaction-'+name,type='group',children=[im],start=st,end=en,keyframes={k:[dict(t=m['t'],value=m[k]) for m in MS[parent]] for k in ['x','y','scaleX','scaleY']}))
# Missing source typing states. These are native gray capsules, dots and separately measured avatars/labels.
for name,cn,box,st,en in [('muse-typing',630,(408,555,656,687),20.85,21.3),('airbnb-typing',825,(497,788,698,895),27.35,28.3)]:
 w,h=box[2]-box[0],box[3]-box[1];S=RUNS[str(cn)]['scale'];children=[dict(id=name+'-body',type='rect',width=w,height=h,radius=h/2,fill='#E7E6E9')]+[dict(id=name+'-dot-'+str(i),type='circle',x=w*.3+i*w*.18,y=h*.5-9*S,width=18*S,height=18*S,fill='#AFAFB4') for i in range(3)];middle.append(dict(id='middle-'+name,type='group',children=children,x=box[0],y=box[1],start=st,end=en))
# Fit the actual source typing dots instead of guessing their diameter/spacing.
def typing_dots(cn,box):
 aa=rgb(cn).astype(float);l,t,r,b=box;reg=aa[t:b,l:r];hh,ww=reg.shape[:2];x0=int(ww*.18);x1=int(ww*.82);y0=int(hh*.2);y1=int(hh*.8);center=reg[y0:y1,x0:x1];bg=np.median(reg[:,int(ww*.15):int(ww*.85)],axis=1);diff=np.max(np.abs(center-bg[y0:y1,None,:]),2)>12;lab,num=ndimage.label(diff,np.ones((3,3)));out=[]
 for li,sl in enumerate(ndimage.find_objects(lab),1):
  if not sl:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if w<7 or h<7 or w>45 or h>45 or not(.6<w/h<1.5):continue
  color=np.median(center[yy,xx][lab[yy,xx]==li],axis=0).astype(int);out.append(dict(x=l+x0+xx.start,y=t+y0+yy.start,width=w,height=h,fill='#'+''.join(f'{v:02x}' for v in color)))
 return sorted(out,key=lambda q:q['x'])[:3]
for name,cn,box in [('muse-typing',630,(408,555,656,687)),('airbnb-typing',825,(497,788,698,895))]:
 node=next(l for l in middle if l['id']=='middle-'+name);node['children']=[c for c in node['children'] if '-dot-' not in c['id']]
 for j,dot in enumerate(typing_dots(cn,box)):node['children'].append(dict(id='middle-source-dot-'+name+'-'+str(j),type='circle',**{**dot,'x':dot['x']-box[0],'y':dot['y']-box[1]}))
for name,cn,box,en in [('resy-booked',990,(572,884,747,977),33.3),('budget-reply',765,(1382,802,1598,920),25.8),('love-it',915,(1306,704,1484,796),30.75)]:
 node=next(l for l in middle if l['id']=='middle-message-'+name);node['children']=[c for c in node['children'] if not c['id'].startswith('middle-resy-typing-dot-')];pose=min(MS[name],key=lambda q:abs(q['t']-cn/30))
 for j,dot in enumerate(typing_dots(cn,box)):node['children'].append(dict(id='middle-source-dot-'+name+'-'+str(j),type='circle',x=(dot['x']-pose['x'])/pose['scaleX'],y=(dot['y']-pose['y'])/pose['scaleY'],width=dot['width']/pose['scaleX'],height=dot['height']/pose['scaleY'],fill=dot['fill'],start=START.get(name,25.35 if name=='budget-reply' else 30.4),end=en))
# Exact source Muse label for its preceding typing state.
a=rgb(630);aa=np.clip((253-a[485:540,425:550].mean(2))/253,0,1);dd,ss=trace_alpha(aa,425,485);middle.append(dict(id='middle-muse-typing-label',type='path',d=dd,fill='#000000',start=20.85,end=21.3,semanticText='Muse',sourceFrame=630))
patch['group-1118']=dict(id='group-1118',type='group',children=middle,start=20.5,end=34.2);patch['group-1139']=dict(id='group-1139',type='group',children=[],start=28.2,end=32.7);patch['group-1158']=dict(id='group-1158',type='group',children=[],start=31.8,end=34.2)
# Rebase the immutable input before constructing a local preview; the reusable patch contains only scoped root replacements.
def rebase(l,root):
 if l.get('src') and not str(l['src']).startswith(('data:','http:','https:')):l['src']=str((root/l['src']).resolve())
 for c in l.get('children',[]):rebase(c,root)
for l in scene['layers']:rebase(l,BASE.parent)
for f in scene.get('fonts',[]):f['src']=str((BASE.parent/f['src']).resolve())
scene['layers']=[copy.deepcopy(patch.get(l['id'],l)) for l in scene['layers']];scene.setdefault('gradients',[]).extend(gradients);scene['source']['notes']+=' Middle18–34.2 scoped measured reconstruction: original source UI glyph contours/native capsule geometry, independently tracked agents/header, persistent scrolling message elements, bounded original product/reaction artwork. No complete source-frame/video layer.'
(R/'middle-refinement.json').write_text(json.dumps(dict(replacements=patch,gradients=gradients,changed_intervals=[[17.75,34.2]],provenance=ledger,headerMeasurements=header_ms,flyingMuseMeasurements=muse_ms,bodyPoseMeasurements=MS),indent=2));(R/'scene-middle-v9.json').write_text(json.dumps(scene,indent=2));print('Middle scoped replacements',list(patch),'messages',len(middle),flush=True)
