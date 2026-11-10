"""Measured component lifecycle/camera correction, built from immutable v9.

Images below are bounded static app/card artwork or genuine emoji. Conversation
bodies and their held letterforms are editable vector paths, never frame playback.
All independent object poses are source-native frame measurements.
"""
from pathlib import Path
import importlib.util,json,copy,argparse
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes,label,find_objects
ROOT=Path(__file__).resolve().parent; BASE=ROOT.parent.parent
F=ROOT/'measurements/native-transition'; P=ROOT/'measurements/object-poses-v10'; A=ROOT/'assets'
spec=importlib.util.spec_from_file_location('trace',ROOT.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)
S=json.loads((BASE/'outputs/05-linq/final-v9/scene.json').read_text())
ledger=json.loads((BASE/'outputs/05-linq/final-v9/snapshot.json').read_text())
def restore(o):
 if isinstance(o,dict):
  for k,v in list(o.items()):
   if k in ('src','path') and isinstance(v,str):
    q=BASE/'outputs/05-linq/final-v9'/v
    if q.exists():o[k]=str(q.resolve())
   else:restore(v)
 elif isinstance(o,list):
  for x in o:restore(x)
restore(S)
layers=S['layers']; provenance=[]
def get(id):return next(x for x in layers if x['id']==id)
def key(rows,prop,offset=0,default=0):return [{'t':r['frame']/30,'value':float(r.get(prop,default)+offset),'ease':'linear'} for r in rows if r.get(prop) is not None]
def im(f):return np.array(Image.open(F/f'{f:06}.png').convert('RGB'))
def asset(name,ar,box=None,frame=None,notes='bounded static app UI artwork; internal copy is raster'):
 path=A/(name+'.png');Image.fromarray(ar).save(path)
 provenance.append({'path':'assets/'+path.name,'source_frame':frame,'box':box,'kind':notes})
 return str(path)
def image(name,src,x,y,w,h):return {'type':'image','id':'v10-'+name,'src':src,'x':x,'y':y,'width':w,'height':h}
def rect(name,x,y,w,h,fill,r=0):return {'type':'rect','id':'v10-'+name,'x':x,'y':y,'width':w,'height':h,'fill':fill,'radius':r}
def group(name,ch,**kw):return dict(type='group',id=name,children=ch,**kw)
def profile(name,minframe=None,maxframe=None,maxmse=.15):
 d=json.loads((P/(name+'.json')).read_text());rows=[r for r in d['poses'] if r['alpha']>.05 and r['mse'] is not None and r['mse']<maxmse and (minframe is None or r['frame']>=minframe) and (maxframe is None or r['frame']<=maxframe)]
 return d,rows
def native_bubble(name,ar,semantic):
 """Isolate shape and ink at the original component's local coordinates."""
 ar=ar.astype(float);h,w=ar.shape[:2];blue=np.median(ar[:,:,2]-ar[:,:,0])>30
 if blue:mask=(ar[:,:,2]-ar[:,:,0]>70)&(ar[:,:,0]<150)
 else:mask=(ar.max(2)-ar.min(2)<4)&(ar.mean(2)>210)&(ar.mean(2)<242)
 vals=np.round(ar[mask]).astype(np.uint8);colors,cnt=np.unique(vals,axis=0,return_counts=True);bg=colors[cnt.argmax()].astype(float)
 outer=np.clip((255-ar[:,:,0])/(255-bg[0]),0,1);core=binary_fill_holes(outer>.7);outer[core]=1
 # Filled black ink and colored emoji occupy holes in the same native body.
 colored=(ar.max(2)-ar.min(2)>20)&core if not blue else np.zeros((h,w),bool)
 emojis=[];labels,n=label(colored);slices=find_objects(labels)
 for sl in slices:
  if sl is None:continue
  yy,xx=sl
  if (labels[sl]>0).sum()<12:continue
  emojis.append([max(0,xx.start-7),max(0,yy.start-7),min(w,xx.stop+7),min(h,yy.stop+7)])
 if name=='gotit':emojis.append([367,16,420,72])
 # Merge touching expanded colored subcomponents into whole individual emoji.
 changed=True
 while changed:
  changed=False
  for i,b in enumerate(emojis):
   for j in range(i):
    a=emojis[j]
    if b[0]<=a[2]+4 and b[2]>=a[0]-4 and b[1]<=a[3]+4 and b[3]>=a[1]-4:
     emojis[j]=[min(a[0],b[0]),min(a[1],b[1]),max(a[2],b[2]),max(a[3],b[3])];emojis.pop(i);changed=True;break
   if changed:break
 if blue:ink=np.clip((ar[:,:,0]-bg[0])/(255-bg[0]),0,1)*core
 else:ink=np.clip((bg[0]-ar.mean(2))/max(bg[0],1),0,1)*core
 for b in emojis:ink[b[1]:b[3],b[0]:b[2]]=0
 od,stats=trace.trace_alpha(outer);gd,gstats=trace.trace_alpha(ink)
 color='#'+''.join(f'{int(v):02x}' for v in bg)
 parts=[{'type':'path','id':'v10-'+name+'-body','d':od,'fill':color},{'type':'path','id':'v10-'+name+'-letters','d':gd,'fill':'#ffffff' if blue else '#000000','semanticText':semantic}]
 for i,b in enumerate(emojis):
  src=asset(name+'-genuine-emoji-'+str(i),np.uint8(ar[b[1]:b[3],b[0]:b[2]]),notes='individual genuine colored emoji, static bounded crop')
  parts.append(image(name+'-emoji-'+str(i),src,b[0],b[1],b[2]-b[0],b[3]-b[1]))
 provenance.append({'component':name,'kind':'editable native body and glyph outlines','semanticText':semantic,'bodyTrace':stats,'inkTrace':gstats,'backgroundRGB':bg.tolist()})
 return parts
def actor(name,id,semantic=None,raster=False,minframe=None,maxframe=None,maxmse=.15):
 d,rows=profile(name,minframe,maxframe,maxmse);box=d['reference_box'];ar=np.array(Image.open(P/(name+'-reference.png')).convert('RGB'))
 children=[image(name+'-art',asset('v10-'+name,ar,box,notes='bounded static rich-app card UI; internal text is raster'),0,0,ar.shape[1],ar.shape[0])] if raster else native_bubble(name,ar,semantic)
 g=group(id,children,x=box[0],y=0,start=rows[0]['frame']/30,end=(rows[-1]['frame']+1)/30,keyframes={'y':key(rows,'y'),'opacity':key(rows,'alpha')})
 if name=='chess-question':
  # This bubble changes hue while appearing/disappearing. Its body is painted
  # toward white, not a fixed cyan color with a scalar opacity.
  mask=(ar[:,:,2]-ar[:,:,0]>150)&(ar[:,:,0]<80);yy,xx=np.nonzero(mask);colors=[]
  for r in rows:
   sy=yy+int(round(r['y']));sx=xx+box[0];valid=(sy>=0)&(sy<720);vals=im(r['frame'])[sy[valid],sx[valid]];rgb=np.median(vals,axis=0);colors.append({'t':r['frame']/30,'value':'#'+''.join(f'{int(v):02x}' for v in rgb),'ease':'linear'})
  children[0]['keyframes']={'fill':colors};g['keyframes'].pop('opacity')
 return g,rows
def replace(id,g):
 ix=next(i for i,x in enumerate(layers) if x['id']==id);layers[ix]=g
def add_actor(name,id,*args,**kwargs):
 g,rows=actor(name,id,*args,**kwargs);replace(id,g);return g,rows

# First old chat: complete fade and two genuinely blank frames before board birth.
add_actor('chess-preview','broad-v5-group-2',raster=True,minframe=149,maxmse=.03)
add_actor('chess-question','broad-v5-group-7',semantic='Yo i’m bored, chess battle?')
add_actor('chess-reply','broad-v5-group-15',semantic='Always down ♟')
for id in ['broad-v5-group-2','broad-v5-group-7','broad-v5-group-15']:get(id)['end']=206/30
get('broad-v5-group-9')['end']=get('broad-v5-group-9')['start'] # obsolete placeholder typing dots

# Outgoing first board stays in front of the new blue message during overlap.
b=get('broad-v5-group-20');affine=P/'first-board-affine.json';rows=json.loads((affine if affine.exists() else P/'first-board.json').read_text());features={x['frame']:x for x in json.loads((ROOT/'measurements/transition-features.json').read_text())}
ref=features[246]['board_top_bounds'];center=(ref[0]+ref[2])/2
if not affine.exists():
 for r in rows:
  bb=features[r['frame']].get('board_top_bounds')
  r['x']=152 if r['frame']<254 else (152+(sum([bb[0],bb[2]])/2-center) if bb and bb[0]>0 else bb[2]-(ref[2]-152) if bb else r['x'])
b.update(start=209/30,end=266/30,keyframes={'x':key(rows,'x'),'y':key(rows,'y'),'opacity':key(rows,'alpha')})
b['shadow']={'x':0,'y':0,'blur':5,'color':'#00000022'}
# The source selection has a blue f2 cell plus soft f3/f4 hints. Reuse that one
# bounded static app-state patch after removing its pawn, which stays native.
patch=im(219)[357:593,557:641].copy()
for yy in range(145,236):
 left=np.median(patch[yy,:14],axis=0);right=np.median(patch[yy,74:],axis=0)
 for xx in range(14,74):patch[yy,xx]=left+(right-left)*(xx-14)/60
src=asset('v10-chess-selection-state',patch,[557,357,641,593],219,'bounded static board selection artwork; white pawn removed and independently animated')
base=np.array(Image.open(ROOT/'assets/chess-board-without-moving-pawns.png').convert('RGB'))[357:593,405:489].astype(float);delta=patch.astype(float)-base;mask=np.ones((236,84),bool);mask[65:236,14:74]=False;den=np.sum(delta[mask]**2);ks=[]
for f in range(213,241):
 obs=im(f)[357:593,557:641].astype(float)-base;ks.append({'t':f/30,'value':float(np.clip(np.sum(obs[mask]*delta[mask])/den,0,1)),'ease':'linear'})
selection=image('selection-art',src,405,357,84,236);selection['keyframes']={'opacity':ks};selection.update(start=213/30,end=241/30)
b['children'][1]=selection

flight,frows=add_actor('flight-question','g-357',semantic='hey can you find me a one way flight from Atlanta to San Francisco in July? looking for something cheap')
layers.remove(b);layers.insert(layers.index(flight)+1,b)
reply,rrows=actor('flight-reply','v10-flight-reply',semantic='On it! 👀 Found a few options, here’s the cheapest one way:')
card,crows=actor('flight-preview','v10-flight-preview',raster=True)
replace('g-366',group('g-366',[reply,card],start=min(reply['start'],card['start']),end=352/30))
bg=get('broad-v5-background-45');bg.update(children=[copy.deepcopy(reply),copy.deepcopy(card)],start=352/30,opacity=1,blur=0,keyframes={'blur':[{'t':352/30,'value':0},{'t':355/30,'value':10}]})
for ch in bg['children']:
 ch.pop('start',None);ch.pop('end',None)
 def unique(o):
  o['id']='background-'+o['id']
  for c in o.get('children',[]):unique(c)
 unique(ch)
for g in layers:
 if g['id'] in ['broad-v5-group-55','rich-group-4']:g['start']=min(g['start'],356/30)

# Cash chat actors have separate births, then leave together under the panel.
gro,grows=add_actor('groceries','broad-v5-group-25',semantic='can you order my weekly groceries?')
sure,srows=actor('cash-reply','v10-cash-reply',semantic='Sure, it’ll be $166.89')
request,qrows=actor('cash-request','v10-cash-request',raster=True,maxframe=772)
for g,rr,offset in [(gro,grows,-274),(sure,srows,-117)]:
 rr=[x for x in rr if x['frame']<759]+[dict(x,y=x['y']+offset,alpha=1) for x in qrows if x['frame']>=759]
 g['keyframes']={'y':key(rr,'y'),'opacity':key(rr,'alpha')};g['end']=773/30
replace('broad-v5-group-37',group('broad-v5-group-37',[sure,request],start=sure['start'],end=773/30))

# Apple Cash composer and sheet rise independently. Preserve native digit wheel.
old=get('linq-measured-v6-group-36');camera=json.loads((P/'cash-ui-cameras.json').read_text())
composerart=asset('v10-cash-composer-ui',im(807)[126:230,172:790],[172,126,790,230],807)
cr=[x for x in camera if x['frame']<818]
composer=group('v10-cash-composer',[image('cash-composer-ui',composerart,172,126,618,104)],start=768/30,end=827/30,keyframes={'y':key(cr,'composer_y')+[{'t':827/30,'value':-300}]})
pr=[]
for f in range(770,839):
 ar=im(f).astype(float);m=(ar.max(2)<245)&(ar.max(2)-ar.min(2)<12);m[:,:180]=False;m[:,780:]=False;labs,n=label(m);found=[]
 for sl in find_objects(labs):
  if sl is None:continue
  yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
  if w>450 and h>20:found.append([xx.start,yy.start,xx.stop,yy.stop])
 if not found:continue
 bb=max(found,key=lambda q:(q[2]-q[0])*(q[3]-q[1]));y=(bb[1]-235 if bb[1]>0 else bb[3]-695)
 sy=min(710,max(0,bb[1]+60));v=float(np.median(ar[sy:sy+3,390:420]));alpha=float(np.clip((255-v)/(255-17),0,1))
 pr.append({'frame':f,'y':y,'alpha':alpha})
panelart=im(807)[230:701,182:778].copy();panelart[344-230:438-230,350-182:636-182]=17
panelui=asset('v10-cash-sheet-ui-with-native-amount',panelart,[182,230,778,701],807,'bounded static Cash sheet artwork; amount cut out for independent native rolling digits')
def cashink(ar):
 al=np.clip((ar.astype(float).mean(2)-17)/238,0,1);return np.dstack([np.full((*al.shape,3),255,np.uint8),np.uint8(np.round(al*255))])
prefix=asset('v10-cash-amount-prefix',cashink(im(807)[344:438,350:468]),[350,344,468,438],807,'bounded static internal UI glyphs $16, with original grayscale edge treatment')
suffix=asset('v10-cash-amount-suffix',cashink(im(807)[344:438,509:618]),[509,344,618,438],807,'bounded static internal UI glyphs .89')
digitarts=[];digitlayers=[];posesbyf={r['frame']:r for r in pr}
for i,(value,frame) in enumerate([(2,780),(3,789),(4,795),(5,801),(6,807)]):
 dy=int(posesbyf[frame]['y']);ar=im(frame)[344+dy:438+dy,468:509];digitarts.append(ar)
 path=asset('v10-cash-unit-'+str(value),cashink(ar),[468,344+dy,509,438+dy],frame,'bounded original internal UI digit; independently placed on clipped native rolling rail')
 digitlayers.append(image('cash-unit-'+str(value),path,0,i*94,41,94))
stack=np.concatenate(digitarts,0).astype(float);offsets=np.arange(377);models=np.stack([stack[k:k+94] for k in offsets]);roll=[]
for f in range(773,811):
 if f not in posesbyf:continue
 y=int(posesbyf[f]['y'])+344
 if y+94>720:off=0.
 else:
  obs=im(f)[y:y+94,468:509].astype(float);alpha=posesbyf[f]['alpha'];obs=255-(255-obs)/max(alpha,.05);err=np.mean((models-obs)**2,axis=(1,2,3));k=int(np.argmin(err));off=float(k)
  if 0<k<376:
   den=err[k-1]-2*err[k]+err[k+1]
   if den>0:off+=float(np.clip(.5*(err[k-1]-err[k+1])/den,-.5,.5))
 roll.append({'frame':f,'y':-off})
rail=group('v10-cash-units-rail',digitlayers,keyframes={'y':key(roll,'y')})
units=group('v10-cash-units-viewport',[rail],x=468,y=344,clip={'x':0,'y':0,'width':41,'height':94})
amount=group('v10-cash-amount',[image('amount-prefix',prefix,350,344,118,94),units,image('amount-suffix',suffix,509,344,109,94)],semanticText='$162.89 → $166.89')
(ROOT/'measurements/long-panels-v10/cash-unit-roll.json').write_text(json.dumps(roll,indent=2))
panel=group('v10-cash-panel',[image('cash-panel-ui',panelui,182,230,596,471),amount],start=pr[0]['frame']/30,end=838/30,keyframes={'y':key(pr,'y'),'opacity':key(pr,'alpha')})
replace(old['id'],group(old['id'],[composer,panel],start=768/30,end=840/30))
def walk(o):
 yield o
 for ch in o.get('children',[]):yield from walk(ch)
for ch in walk(panel):
 if ch['id']=='linq-measured-v6-group-25':
  ch['keyframes']['y']=[{'t':t,'value':v,'ease':'linear'} for t,v in [(25.6,0),(25.7,-100),(25.8,-200),(25.85,-300),(25.9,-400),(26.15,-400),(26.2,-500),(26.35,-500),(26.4,-600),(26.55,-600),(26.6,-700),(26.75,-700),(26.8,-800)]]

got,gotrows=add_actor('gotit','g-631',semantic='Got it, ordering now 🛒')
xrows=json.loads((P/'gotit-x.json').read_text());last=gotrows[-1]
got['keyframes']['y']=key(gotrows,'y')+[{'t':r['frame']/30,'value':r['y']-2,'ease':'linear'} for r in xrows if r['frame']>last['frame']]
got['keyframes']['x']=[{'t':got['start'],'value':99}]+[{'t':r['frame']/30,'value':r['x']-2,'ease':'linear'} for r in xrows if r['frame']>=last['frame']]
got['end']=873/30

# Full chess canvas crosses left while the next independent page enters right.
chess=get('broad-v5-group-41');xs=[r for r in json.loads((P/'second-chess-x.json').read_text()) if r['x'] is not None]
chess.update(start=xs[0]['frame']/30,end=(xs[-1]['frame']+1)/30,keyframes={'x':key(xs,'x')})
# The sprite keyframes were already corrected to source relative coords; align default too.
queen=chess['children'][1];queen['x']=180;queen['y']=128
win=get('broad-v5-group-43');win['end']=chess['end'];win['keyframes']['x']=key(xs,'x',-237)
get('g-831')['end']=chess['end']

# Fare-card translation and seat-grid reveal are separate source-native tracks.
seatdata=json.loads((ROOT/'measurements/long-panels-v10/flight-seats.json').read_text());ss=seatdata['poses']
fare=get('rich-group-4');fare['end']=423/30
fare['keyframes']['x']=[x for x in fare['keyframes']['x'] if x['t']<412/30]+key(ss,'x')
originalfare=copy.deepcopy(fare['children'][0]);originalfare['end']=414/30
movingcards=image('fare-cards-only',seatdata['farePath'],188,0,582,720);movingcards['start']=414/30
fare['children']=[originalfare,movingcards]
fare['clip']={'x':188,'y':0,'width':582,'height':720}
# Clip the moving content from a fixed wrapper; a translating clip would drift.
fare.pop('clip')
ix=layers.index(fare);layers[ix]=group('rich-group-4',[fare|{'id':'v10-moving-fare-cards'}],start=fare['start'],end=fare['end'],clip={'x':188,'y':0,'width':582,'height':720})
gridbase=group('v10-seat-base',[image('seat-base-art',seatdata['gridPath'],188,0,582,720)],start=414/30,end=423/30)
layers.insert(ix,gridbase)
seat=get('rich-group-6');summary=[]
def summarytop(f):
 a=im(f)[:,215:745].astype(int);rows=((a.min(2)>230)&(a.max(2)-a.min(2)<12)).sum(1);valid=np.where((rows>440)&(np.arange(720)>400))[0];return int(valid[0]) if len(valid) else None
refwhite=summarytop(450)
for f in range(428,469):
 t=summarytop(f)
 if t is not None:summary.append({'frame':f,'y':t-refwhite+512})
ring=rect('seat-c10-selection',398,195,30,41,'none',7);ring.update(stroke='#ffffff',strokeWidth=3,start=432/30)
summaryart=image('flight-summary',seatdata['summaryPath'],208,0,544,208)
summaryg=group('v10-seat-summary',[summaryart],start=summary[0]['frame']/30,end=15.63,keyframes={'y':key(summary,'y')})
seat.update(children=[image('seat-grid-overlay',seatdata['gridPath'],188,0,582,720),ring,summaryg],start=414/30,keyframes={'opacity':key(ss,'gridAlpha')})

# The two scrolling rich applications retain static bounded internal UI, with
# independently editable document/camera/row states and five actual photo nodes.
food=json.loads((ROOT/'measurements/long-panels-v10/foodash.json').read_text());rr=food['poses']
foodchildren=[image('foodash-document',food['path'],0,0,584,1132)]
initial=image('foodash-initial-row',food['initialRow'],0,440,584,110);initial.update(end=1036/30,keyframes={'opacity':[{'t':1028/30,'value':1},{'t':1035/30,'value':0}]});foodchildren.append(initial)
subtotal=image('foodash-subtotal33',food['initialSubtotal'],0,918,584,90);subtotal.update(end=1056/30,keyframes={'opacity':[{'t':1051/30,'value':1},{'t':1055/30,'value':0}]});foodchildren.append(subtotal)
foodg=group('rich-group-12',foodchildren,start=rr[0]['frame']/30,end=1074/30,keyframes={'x':key(rr,'x'),'y':key(rr,'y'),'scaleX':key(rr,'scale'),'scaleY':key(rr,'scale')})
replace('rich-group-12',foodg)
rest=json.loads((ROOT/'measurements/long-panels-v10/restaurant.json').read_text());rr=rest['poses']
photos=[image('restaurant-photo-'+p['name'],p['path'],p['x'],303,p['width'],334) for p in rest['photos']]
rail=group('v10-restaurant-rail',photos,keyframes={'x':key(rr,'q')})
photoClip=group('v10-restaurant-photo-viewport',[rail],clip={'x':188,'y':303,'width':586,'height':334})
pressed=rect('directions-pressed',196,123,356,68,'#888888',34);pressed['keyframes']={'opacity':[{'t':r['frame']/30,'value':max(0,min(1,(r.get('buttonRGB',18)-18)/118)),'ease':'linear'} for r in rr]}
# Keep the original button label/icons above the native pressed fill.
buttonlabel=im(1110)[143:172,292:462];v=1-buttonlabel.mean(2)/255;fg=(buttonlabel.mean(2)-18)/(255-18);gd,_=trace.trace_alpha(np.clip(fg,0,1));labelpath={'type':'path','id':'v10-directions-label','d':gd,'x':292,'y':144,'fill':'#ffffff'}
restg=group('rich-group-14',[rect('restaurant-white-sheet',188,-35,586,1400,'#ffffff',32),rect('restaurant-sheet-handle',455,-20,50,8,'#aaaaaa',4),image('restaurant-document',rest['path'],188,0,586,860),pressed,labelpath,photoClip],start=rr[0]['frame']/30,end=1150/30,keyframes={'y':key(rr,'y'),'opacity':key(rr,'alpha')})
replace('rich-group-14',restg)

check=json.loads((ROOT/'measurements/long-panels-v10/checkin.json').read_text());box=check['box'];rr=check['poses'];parts=native_bubble('checkin',np.array(Image.open(check['path'])),'Oh, and check-in just opened for your July 2 flight to SFO! Gate 37, Seat 10C — tap to get your boarding pass. ✈️')
replace('g-925',group('g-925',parts,x=box[0],start=rr[0]['frame']/30,end=39.75,keyframes={'y':key(rr,'y'),'opacity':key(rr,'alpha')}))

# Root late helper reserves Games/Four/boarding/gallery; merge after this builder.
OUT=ROOT/'scene-transition-v10.json';OUT.write_text(json.dumps(S,indent=2)+'\n')
(ROOT/'assets/transition-v10-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(OUT,flush=True)
