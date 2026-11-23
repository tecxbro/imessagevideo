import json
from pathlib import Path
import sys

from PIL import Image
import numpy as np
from scipy.ndimage import label, find_objects, binary_closing

ROOT = Path(__file__).parent
sys.path.insert(0,str(ROOT/'project'))
from render import interpolate
S = json.loads((ROOT/'project/scene.json').read_text())
SRC = Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
PRE = Path('/tmp/sidehoe-phone.tJtcYo/final-frames')

def camera(f):
    tracks = S['tracks']
    if f >= 650:
        return interpolate(tracks['followBodyRegistration'],f)
    x,y,s = interpolate(tracks['followMeasuredCamera'],f)
    ky, = interpolate(tracks['followKeyboardY'],f)
    return x,y,s,1,ky

def crop(image, bounds):
    left,top,right,bottom = bounds
    x,y = max(0,round(left)), max(0,round(top))
    return (x,y,image[y:min(1000,round(bottom)), x:min(1000,round(right))])

def components(image,bounds,mask,minimum):
    x,y,piece = crop(image,bounds)
    if not piece.size:
        return []
    m=mask(piece)
    labels,count=label(m)
    out=[]
    for i, region in enumerate(find_objects(labels),1):
        yr,xr=region
        area=(labels[region]==i).sum()
        if area<minimum:
            continue
        out.append((int(area),[x+xr.start,y+yr.start,x+xr.stop,y+yr.stop]))
    return sorted(out,reverse=True)

def bound(image, bounds, mask, limit=2):
    x,y,piece=crop(image,bounds)
    active=mask(piece)
    xx=np.flatnonzero(active.sum(axis=0)>=limit)
    yy=np.flatnonzero(active.sum(axis=1)>=limit)
    if len(xx)==0 or len(yy)==0:
        return None
    return [x+int(xx[0]),y+int(yy[0]),x+int(xx[-1])+1,y+int(yy[-1])+1]

def key_rows(q, r, ky, s):
    lo,hi=r
    detect=lambda a: (a.min(axis=2)>=246)&(np.ptp(a,axis=2)<10)
    parts=components(q,(lo+4,ky-2,hi-4,ky+215*s),detect,90)
    parts=[part for area,part in parts if 18 < part[2]-part[0] < 80 and 17 < part[3]-part[1] < 60]
    rows=[]
    for j,n in enumerate((10,9,7)):
        estimate=ky+(9+52*j)*s
        group=sorted([b for b in parts if abs(b[1]-estimate)<20])
        if len(group)==n+1 and j==2:
            group=group[1:]
        if len(group)!=n:
            rows.append(None)
            continue
        boxes=np.array(group)
        rows.append([round(float(v),3) for v in (
            boxes[0,0],np.median(boxes[:,1]),np.polyfit(np.arange(n),boxes[:,0],1)[0],
            np.median(boxes[:,2]-boxes[:,0]),np.median(boxes[:,3]-boxes[:,1])
        )])
    return rows

def lines(q, bounds, n, tone):
    l,t,r,b=bounds
    h=b-t
    ink=lambda a:(a.max(axis=2)<tone) & (np.ptp(a,axis=2)<25)
    areas = ((.12,.48),(.49,.86)) if n==2 else ((.10,.371),(.372,.63),(.635,.91))
    return [bound(q,(l+15,t+v*h,r-11,t+w*h),ink,2) for v,w in areas]

def measure(q,f):
    x,y,s,asp,ky=camera(f)
    sy=s*asp
    abs_box=lambda x1,y1,x2,y2:(x+x1*s,y+y1*sy,x+x2*s,y+y2*sy)
    grey=lambda a:(a[:,:,0]>219)&(a[:,:,0]<238)&(np.ptp(a,axis=2)<10)
    grey_one=lambda a:(a[:,:,0]>223)&(a[:,:,0]<244)&(np.ptp(a,axis=2)<11)
    cyan=lambda a:(a[:,:,0]<246)&(a[:,:,0]>115)&(a[:,:,1]-a[:,:,0]>7)&(a[:,:,2]-a[:,:,0]>9)
    dark=lambda a:a.max(2)<151
    marks={}
    for name,box,predicate,area in (
        ('island',abs_box(120,-14,280,70),lambda a:a.max(2)<65,130),
        ('badge',abs_box(159,61,241,135),dark,80),
        ('gray1',abs_box(23,209,326,290),grey_one,900),
        ('gray2',abs_box(23,320,350,444),grey,900),
        ('blue',abs_box(110,145,386,233),cyan,800),
    ):
        opts=components(q,box,predicate,area)
        marks[name] = opts[0][1] if opts else None
    if marks['badge']:
        l,t,r,b=marks['badge']
        marks['name']=bound(q,(l-10,b+1,r+10,b+20),dark)
    else:
        marks['name']=None
    if marks['gray1'] and marks['gray2']:
        marks['gray1_ink']=lines(q,marks['gray1'],2,197)
        marks['gray2_ink']=lines(q,marks['gray2'],3,176)
        marks['today']=bound(q,(x+175*s,marks['gray1'][3]+20*sy,x+228*s,marks['gray2'][1]-10*sy),lambda a:a.max(2)<185)
    if marks['blue']:
        l,t,r,b=marks['blue']
        swatch = q[t:b,l:r]
        row=np.median(swatch[:,8:-14],axis=1)
        marks['blueStops']=[np.rint(row[int(k*(len(row)-1))]).astype(int).tolist() for k in (0.10,.25,.45,.65,.82,.96)]
    marks['keys']=key_rows(q,(x+13*s,x+388*s),y+ky*sy,s)
    marks['keyboardTray'] = bound(q, abs_box(26,ky-9,374,ky+8),lambda a: (a[:,:,0]>188)&(a[:,:,0]<231)&(np.ptp(a,axis=2)<16),8)
    marks['home']=bound(q,abs_box(112,776,284,821),lambda a:a.max(2)<73,6)
    marks['headerEnd']=bound(q,abs_box(45,130,352,160),lambda a:(a.mean(2)<243)&(a.min(2)>191),90)
    if marks['keys'][0]:
        top=marks['keys'][0][1]
        marks['composer'] = bound(q,(x+66*s,top-56*sy,x+381*s,top-12*sy),
                                  lambda a:(a.mean(2)<237)&(a.min(2)>162),8)
    return marks

def main():
    result={}
    for f in range(631,660):
        rec=[measure(np.asarray(Image.open(root/f'{f:06d}.png').convert('RGB'),dtype=np.int16),f) for root in (SRC,PRE)]
        if f in (636,643,649,653,655,657,659):
            print(f)
            for k in rec[0]:
                print(k,rec[0][k],rec[1].get(k))
        result[f]=rec
    (ROOT/'measured.json').write_text(json.dumps(result, indent=2)+'\n')

if __name__=='__main__':
    main()
