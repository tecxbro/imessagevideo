from pathlib import Path
import sys,json
from PIL import Image
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
sc=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
previous=root/'probe-a'

def spans(flags):
    sides=np.flatnonzero(np.diff(np.r_[False,flags,False]))
    return [(int(l),int(r)) for l,r in zip(sides[::2],sides[1::2])]

def bounds(test,rect,min_run=0,prc=(0,100)):
    x0,y0,x1,y1=(int(round(x)) for x in rect)
    test=test[y0:y1,x0:x1]
    y,x=np.where(test)
    if not len(y):
        return None
    if min_run:
        keep=test.sum(1)>=min_run
        y,x=np.where(test&keep[:,None])
        if not len(y):
            return None
    lo,hi=prc
    return [int(np.percentile(x,lo))+x0,int(np.percentile(y,lo))+y0,int(np.percentile(x,hi))+1+x0,int(np.percentile(y,hi))+1+y0]

def measurements(f,directory):
    a=np.asarray(Image.open(directory/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    red,green,blue=np.moveaxis(a,2,0)
    tone=(red+green+blue)/3
    dx,dy,z=interpolate(sc['tracks']['sofiaMeasuredCamera'],f)
    rail=[]
    for l,r in ((round(dx)-10,round(dx+z*32)),(round(dx+z*368),round(dx+z*400)+11)):
        median=np.median(tone[210:700,l:r],axis=0)
        rail.append({t:[[x+l,y+l] for x,y in spans(median<t)] for t in (95,160,221,240,249)})
    band=tone[:,425:575].mean(1)
    top=next(i for i,t in enumerate(band) if t<174)
    dark=(tone<126)
    notch=bounds(dark,(405,max(0,top+4),595,max(29,top+85)),20,(.3,99.7))
    white_top=bounds((tone>=249)&(blue-green<=3),(420,max(0,round(top+94*z)),575,253),15,(0,100))
    # The screen has a broad central tint plate. These are its falling and rising boundaries.
    chromed=(tone>220)&(tone<249)&(blue-red<10)
    mid_x=round(dx+z*145)
    chrome=[(i,j) for i,j in spans(chromed[max(top,0):min(320,max(86,round(top+200*z))),mid_x]) if j-i>5]
    cyan=(blue-red>62)&(green-red>55)&(blue>=204)
    cx0,cx1=int(dx+140*z),int(dx+382*z)
    cy0=max(65,int(dy+125*z))
    cyan_spans=spans((cyan[cy0:620,cx0:cx1]).sum(1)>max(9,int(14*z)))
    cyan_boxes=[bounds(cyan,(cx0,cy0+t,cx1,cy0+b),6,(.2,99.8)) for t,b in cyan_spans if b-t>11]
    neutral=(tone>187)&(tone<240)&(blue-red>=0)&(blue-red<=11)
    ix0,ix1=round(dx+33*z),round(dx+242*z)
    iy0,iy1=max(160,round(dy+180*z)),min(530,round(dy+320*z))
    received_spans=spans(neutral[iy0:iy1,ix0:ix1].sum(1)>round(28*z))
    rx1=round(dx+310*z)
    received=[bounds(neutral,(ix0,iy0+t,rx1,iy0+b),round(28*z),(.1,99.9)) for t,b in received_spans if b-t>9]
    prop=cyan_boxes[0] if cyan_boxes else [ix0,iy0,ix1,iy1]
    if len(received)==2:
        first,second=received
        lines=[]
        for l,t,r,b in (first,second):
            lines.append(bounds(tone<149,(l+8,t+3,r-4,b-3),4,(.5,99.5)))
        today=bounds(tone<167,(int(dx+158*z),max(second[3]+6,round(dy+296*z)),int(dx+245*z),min(round(dy+372*z),cyan_boxes[1][1]+2)),3,(0,100))
    else:
        today=None
        lines=[]
    # Keyboard background differs from white screen by more than 17 levels.
    k0=round(dx+z*48); k1=round(dx+z*352)
    kb=(blue-red>=1)&(blue-red<17)&(tone>168)&(tone<235)
    origin=max(320,round(dy+475*z))
    end=min(860,round(dy+597*z))
    tray_spans=spans((kb[origin:end,k0:k1]).mean(1)>.68)
    tray=next((t+origin for t,b in tray_spans if b-t>=8),None)
    if tray is None:
        tray=round(dy+519*z)
    light=(tone>242)&(np.ptp(a,axis=2)<7)
    bright=(light[tray:995,k0:k1].mean(1)>.47)
    row_spans=[(t+tray,b+tray) for t,b in spans(bright) if b-t>12]
    groups=[]
    for i,(t,b) in enumerate(row_spans[:4]):
        coverage=light[t+2:min(t+10,b),round(dx+10*z):round(dx+390*z)].mean(0)
        offset=round(dx+10*z)
        columns=[[l+offset,r+offset] for l,r in spans(coverage>.68) if r-l>12]
        groups.append(([t,b],columns))
    composer= bounds((tone<230)&(tone>147),(round(dx+75*z),tray-62,round(dx+365*z),tray-6),8,(0,100))
    return dict(top=top,notch=notch,chrome=[(i+top,j+top) for i,j in chrome],rails=rail,cyan=cyan_boxes,received=received,ink=lines,today=today,keys=groups,composer=composer,tray=tray)

out={}
for f in range(319,330):
    rows=[measurements(f,d) for d in (source,previous)]
    out[f]=rows
    print(f)
    for row in rows:
        print(row)
(root/'sofia-measured.json').write_text(json.dumps(out,indent=2)+'\n')
