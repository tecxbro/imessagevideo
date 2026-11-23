from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,sys
import json
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
s=json.loads((root/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
base=Path('/tmp/sidehoe-sofia.fuoOwt/clean-frames')
new=root/sys.argv[1]
def spans(mask):
    x=np.flatnonzero(np.diff(np.r_[False,mask,False]))
    return list(zip(x[::2],x[1::2]))

def ink(image,rect,threshold,minimum=0):
    l,t,r,b=map(int,rect)
    mask=image[t:b,l:r]<threshold
    if minimum:
        mask &= mask.sum(1)[:,None]>=minimum
    y,x=np.where(mask)
    if len(y):
        return [int(l+x.min()),int(t+y.min()),int(l+x.max()+1),int(t+y.max()+1)]
    return None

def inspect(f,a):
    l=a.mean(2)
    step={}
    if f<162:
        x,y,w=interpolate(s['tracks']['assistantMeasuredPosition'],f)
        tx,ty,tw,th=interpolate(s['tracks']['assistantLine1'],f)
        dx,dy,dw,dh=interpolate(s['tracks']['assistantLine2'],f)
        tint=a[800:900,939:995]
        pose1=(tx-32,ty-21,tx+tw+32,min(ty+th+9,dy))
        pose2=(dx-32,max(dy-13,ty+th-1),dx+dw+32,min(y-22,dy+dh+15))
        shape=(365,max(0,round(y+46)),643,round(y+153))
        step['island']=ink(l,shape,147,40)
        i,j,k,m=step['island'] or shape
        step['islandRGB']=np.rint(np.median(a[j+9:m-12,426:555],axis=(0,1))).astype(int).tolist()
        step['tint']=np.rint(np.median(tint,axis=(0,1))).astype(int).tolist()
        step['type']=[ink(l,pose,threshold,2) for pose in (pose1,pose2) for threshold in (68,129,193)]
        step['side']=[]
        for f0 in range(round(y+180),990,26):
            band=l[f0-5:f0+6,870:974].mean(0)
            edge=band[-12:].mean()
            shade=band.min()
            columns=np.flatnonzero(band<shade+(edge-shade)*.60)
            if len(columns)>6:
                step['side'].append([f0,int(columns[0]+870),int(columns[-1]+871),int(round(shade)),int(round(edge))])
    else:
        o=s['followSettledRegistration']['631']
        x,y,z=interpolate(s['tracks']['followMeasuredCamera'],f)
        steps=[]
        for sx in [(310,682),(329,668),(400,614)]:
            med=np.median(l[:,slice(*sx)],axis=1)
            loud=np.flatnonzero(med[400:]<240)
            steps.append(loud[-1]+400)
        outgoing=(a[:,:,2]-a[:,:,0]>15)&(a[:,:,1]-a[:,:,0]>9)&(a[:,:,2]>219)
        gry=(l>107)&(l<243)&(np.ptp(a,axis=2)<13)
        yy=np.flatnonzero(outgoing[:490,430:685].sum(1)>35)
        step['bottom']=list(map(int,steps))
        step['blue']=ink(np.where(outgoing,0,255),(410,0,688,480),1,18)
        k=round(y+545*z)
        section=(np.ptp(a,axis=2)<12)&(l<244)&(l>181)
        px=np.arange(343,652)
        q=np.flatnonzero(section[max(0,k-40):k+82,px].mean(axis=1)>.64)
        step['trayY']=int(max(0,k-40)+q[0]) if len(q) else None
        y0,y1=max(1,round(y+197*z)),round(y+423*z)
        step['bubs']=[(int(y0+i),int(y0+j)) for i,j in spans(gry[y0:y1,359:609].sum(1)>79) if j-i>=8]
        step['badge']=ink(l,(456,max(0,round(y+49*z)),548,max(7,round(y+130*z))),106,9)
    return step
result={}
for i,fs in enumerate(([154,156,158,159,160,161],[624,625,626,627,628,629,630])):
    w=192
    box=(87,220,944,942) if i==0 else (280,0,720,850)
    sheet=Image.new('RGB',(w*len(fs),963),'white')
    d=ImageDraw.Draw(sheet)
    for col,f in enumerate(fs):
        values=[]
        pics=[Image.open(o/f'{f:06}.png').convert('RGB') for o in (source,base,new)]
        for row,im in enumerate(pics):
            values.append(inspect(f,np.array(im,dtype=np.int16)))
            guide=im.crop(box)
            guide.thumbnail((w-4,300),Image.Resampling.LANCZOS)
            x=col*w;y=row*321
            sheet.paste(guide,(x,y+18));d.text((x+4,y+3),f'{f} {("source","last","revised")[row]}',fill='black')
        result[f]=values
    sheet.save(root/f'measure-{sys.argv[1]}-{i}.jpg',quality=92)
(root/f'measure-{sys.argv[1]}.json').write_text(json.dumps(result,indent=2)+'\n')
