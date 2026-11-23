from pathlib import Path
from PIL import Image
import numpy as np,sys,json
p=Path(__file__).parent
sys.path.insert(0,str(p/'project'))
from render import interpolate
spec=p/'project/scene.json'
s=json.loads(spec.read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
obs=json.loads((p/'intro-parts.json').read_text())
out={}

def box(luma,region,limit,min_pixels=7):
    l,t,r,b=map(int,region)
    y,x=np.where(luma[t:b,l:r]<limit)
    if len(x)<min_pixels:
        return None
    return [float(x.min()+l),float(y.min()+t),float(x.max()-x.min()+1),float(y.max()-y.min()+1)]

for f in range(10):
    a=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    luma=a.mean(2)
    lefts=(175,560,177,398,701)
    rights=(370,840,329,608,851)
    cut_top=(192,185,288,306,293)
    cut_end=(320,331,397,445,398)
    offset=max(0,4-f)
    dark=(200,190,177,162,149,142,139,138,137,136)[f]
    coords=[]
    for j,(l,t,r,b) in enumerate(zip(lefts,cut_top,rights,cut_end,strict=True)):
        if j in (0,1):
            lower=b if f<4 else 293
        elif j==3:
            lower=435 if f<1 else (416 if f<=2 else 395)
        else:
            lower=b if f<3 else 375
        ink=box(luma,(l,t,r,lower),dark,12)
        if ink is None or (f<=1 and j in (2,4)):
            coords.append(None)
            continue
        x,y,w,h=ink
        # Preserve icon footprints and apply source blur outside the legible ink.
        sx=.65+max(0,5-f)*.27
        sy=.66+max(0,5-f)*.49
        angle=0.
        if f==0 and j in (0,1):
            x+=2
            w*=.91
            h*=.67
            angle=22 if j==1 else -23
            sx+=.4
            sy+=.3
        if f==1 and j==1:
            sy+=.4
        opacity=(.60,.77,.88,.96,1,1,1,1,1,1)[f]
        if j in (2,4):
            opacity*=.89
        coords.append([x,y,w,h,opacity,sx,sy,angle])
    measured=obs[str(f)][0]
    rows=[]
    for j in range(2):
        if f<2: continue
        dot=measured['dots'][j]
        mid=(dot[1]+dot[3])/2 if dot else 756+j*154
        if dot and (dot[3]-dot[1])<8:
            mid=756+j*154
        width=14.0+f*.22
        dot_x=(dot[0]+dot[2])/2-width/2 if dot else 205-f*1.2
        opacity=(0,0,.14,.25,.38,.53,.66,.78,.88,.99)[f]
        label,preview,time=measured['inks'][j]
        # At low coverage the dark-pixel bounds do not see the entire line.
        label=box(luma,(293,int(mid-49),478,int(mid-19)),218,11)
        preview=box(luma,(289,int(mid-17),580,int(mid+12)),224,11)
        time=box(luma,(646,int(mid-48),780,int(mid-17)),230,7)
        def field(value,nominal):
            return value if value and value[2] >= nominal[2]*.65 and value[3]>=9 else nominal
        label=field(label,[306,mid-42,[104,130][j],19])
        preview=field(preview,[307,mid-10,[87,259][j],17])
        time=field(time,[667-j*16,mid-41,[105,121][j],17])
        backdrop=s.get('inboxRowColors',{}).get(s['inboxRows'][j][0],'')
        rows.append([j,[dot_x,mid-width/2,width,width],[255,mid,65.2],
                     label,preview,time,mid+67,opacity,backdrop])
    center=interpolate(s['tracks']['inboxIntroPin1'],f)[1]
    note=[379.,center-109,245.,79.,(0,0,0,.11,.28,.42,.61,.77,.87,.92)[f],max(.85,5-(f-3)*.67)]
    out[str(f)]={'chrome':coords,'rows':rows,'note':note,'rowFocus':[.35+(9-f)*.28,.45+(9-f)*.47]}
s['inboxIntroRegistration']=out
spec.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
