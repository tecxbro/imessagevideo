from pathlib import Path
from PIL import Image
import numpy as np
import sys,json,math
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
path=p/'project/scene.json'
scene=json.loads(path.read_text())
obs=json.loads((p/'inbox-measure.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def bbox(rect,luma,threshold,rows=2):
 l,t,r,b=[int(round(v)) for v in rect]
 l,r=max(0,l),min(1000,r)
 t,b=min(1000,max(0,t)),min(1000,max(0,b))
 if r<=l or b<=t:return None
 dark=luma[t:b,l:r]<threshold
 usable=dark.sum(1)>=rows
 y,x=np.where(dark&usable[:,None])
 if not len(x):return None
 return [float(l+x.min()),float(t+y.min()),float(l+x.max()+1),float(t+y.max()+1)]

def sized(row):
 x,y,r,b=row
 return [round(x,4),round(y,4),round(r-x,4),round(b-y,4)]

error={}
for f in range(42,102):
 row,prior=obs[str(f)]
 rgb=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
 luma=rgb.mean(2)
 header_y,z=interpolate(scene['tracks']['inboxChromePose'],f)
 origin=500-410*z
 def local(rect):
  return [round((rect[0]-origin)/z,4),round((rect[1]-header_y)/z,4),round((rect[2]-rect[0])/z,4),round((rect[3]-rect[1])/z,4)]
 pins=[]
 for j,(x,sample) in enumerate(zip((169,411,651),row['pins'],strict=True)):
  offsets=[2.8,-2.5,-7.8]; lifts=[-7.2,-5.6,-3.4]; widths=[.982,.984,.987]
  if sample and sample[1]>1 and j!=1:
   l,t,r,b=sample
   pins.append([round(((l+r)/2-origin)/z-x,3),
                round(((t+b)/2-header_y)/z-473,3),
                round((r-l)/z/162,5)])
  else:
   pins.append([offsets[j],lifts[j],widths[j]])
 pinlabels=[]
 for j,rect in enumerate(row['labels']):
  if rect and rect[3]-rect[1]>12 and f<52:
   # The first displaced row can enter the labels' search box.
   if rect[3]-rect[1]<=27 and rect[2]-rect[0]>=40:
    pinlabels.append(local(rect))
    continue
  pinlabels.append(None)
 clock = local(row['clock']) if row['clock'] and row['clock'][1]>1 else [96,194,66,26]
 heading = local(row['headline']) if row['headline'] and row['headline'][1]>1 else [332,307,153,32]
 status = local(row['status']) if row['status'] and row['status'][1]>1 else [568,198,169,26]
 top,scale=interpolate(scene['tracks']['inboxIdentifiedRowPose'],f)
 place=lambda x:500+(x-500)*scale
 actual={i:r for i,*r in row['rows']}
 oldrows={i:r for i,*r in prior['rows']}
 dots=[]
 for i,r in actual.items():
  x,y,x1,y1=r[0]
  if y>15 and y1<990 and y1-y>=8 and i>0:
   dots.append(((y+y1)/2-(top+(752+i*171)*scale)))
 drift=float(np.clip(np.median(dots),-10,10)) if dots else 0
 rows=[]
 max_name=(115,142,76,105,79,30,125,76,105)
 max_quote=(84,280,270,208,294,223,278,301,208)
 widths=(96,115,112,105,92,93,93,103,96)
 for j in range(len(scene['inboxRows'])):
  mid=top+(752+j*171)*scale+drift
  a=actual.get(j)
  if a:
   x1,y1,x2,y2=a[0]
   if (y2-y1)>=7 and y1>0 and y2<999:
    mid=(y1+y2)/2
  if mid<-84 or mid>1080:
   continue
  name=bbox((place(284),mid-52*scale,place(471),mid-23*scale),luma,134,3)
  quote=bbox((place(284),mid-17*scale,place(633),mid+12*scale),luma,192,3)
  time=bbox((place(654),mid-51*scale,place(792),mid-22*scale),luma,210,3)
  def select(rect,default,min_w,min_h=9):
   if rect:
    have=sized(rect)
    if have[2]>=min_w and min_h<=have[3]<36:
     return have
   return default
  name=select(name,[place(294),mid-41*scale,max_name[j]*scale,21*scale], max_name[j]*.63*scale)
  quote=select(quote,[place(294),mid-9*scale,max_quote[j]*scale,17*scale], max_quote[j]*.58*scale,8)
  if j in (6,7) and f>=62:
   target_width=(365,284)[j-6]*scale
   quote[2]=max(quote[2],target_width)
  time=select(time,[place(787-widths[j]),mid-41*scale,widths[j]*scale,17*scale],widths[j]*.62*scale,8)
  alpha=(1 if f<=47 else {48:.82,49:.50,50:.30,51:.24,52:.17,53:.10,54:.04}.get(f,0)) if j==0 else 1
  portrait= [place(235),round(mid-.3,3),68.4*scale]
  slot=bbox((place(191),mid-46*scale,place(279),mid+46*scale),luma,241,4)
  if slot and slot[1]>1 and slot[3]<999 and 55*scale<=slot[2]-slot[0]<=82*scale:
   portrait=[round((slot[0]+slot[2])/2,2),round((slot[1]+slot[3])/2,2),round(slot[2]-slot[0]+.6,3)]
  name_key=scene['inboxRows'][j][0]
  backdrop=scene.get('inboxRowColors',{}).get(name_key,'')
  if 30<mid<968 and (43<=f<=50 or 60<=f):
   terms=[]
   for theta in (.16,.31,.47,.62,2.52,2.68,2.84,3.0,3.24,3.40,3.55):
    x=round(portrait[0]+portrait[2]*.42*math.cos(theta))
    y=round(portrait[1]+portrait[2]*.42*math.sin(theta))
    value=rgb[y,x]
    if 100<value.mean()<241 and np.ptp(value)>6:
     terms.append(value)
   if len(terms)>5:
    g=np.rint(np.median(terms,axis=0)).astype(int)
    backdrop='#%02x%02x%02x'%tuple(g)
  cx=place(177)
  if a and a[0][2]-a[0][0]>=8:
   cx=(a[0][0]+a[0][2])/2
  rows.append([j,[round(cx-8.35*scale,3),round(mid-8.4*scale,3),16.7*scale,16.7*scale],
               portrait, name,quote,time,round(mid+73*scale,3),alpha,backdrop])
 home=None
 home_guess=top+2263*scale
 home_top=max(0,round(home_guess-121))
 home_bottom=min(1000,round(home_guess+54))
 if home_top>=home_bottom:
  match=[]
 else:
  band=luma[home_top:home_bottom,round(place(355)):round(place(646))]
  match=np.flatnonzero((band<178).sum(1)>=190*scale)
 if len(match)>=2:
  y0,y1=int(match[0])+home_top,int(match[-1])+home_top+1
  xmin,xmax=round(place(267)),round(place(733))
  mask=(luma[y0:y1,xmin:xmax]<194).sum(0)>=max(1,(y1-y0)//2)
  xs=np.flatnonzero(mask)+xmin
  if len(xs)>215*scale:
   x0,x1=int(xs[0]),int(xs[-1])+1
   tone=np.rint(np.median(rgb[y0:y1,445:555,:],axis=(0,1))).astype(int).tolist()
   home=[[x0,y0,x1,y1],tone]
 error[str(f)]={'chrome':{'clockInk':clock,'headingInk':heading,'statusInk':status,'pins':pins,
                          'pinLabels':pinlabels,'chromeY':0},'rows':rows,'home':home}
scene['inboxScrollRegistration']=error
path.write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
