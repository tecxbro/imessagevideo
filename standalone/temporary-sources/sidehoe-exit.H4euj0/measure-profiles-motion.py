from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import label,find_objects,binary_closing,binary_fill_holes,minimum_filter
from scipy.optimize import least_squares
import json, sys

root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
path=root/'project/scene.json'
s=json.loads(path.read_text())
t=s['tracks']
media=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def per_component(mask,lo,top,min_area,reverse=False):
    cc,n=label(binary_closing(mask,iterations=2))
    records=[]
    for i,(rows,cols) in enumerate(find_objects(cc),1):
        component=(cc[rows,cols]==i)
        if component.sum()<min_area:
            continue
        records.append((int(component.sum()),(lo+cols.start,top+rows.start,lo+cols.stop,top+rows.stop),i))
    return sorted(records,reverse=True),cc

def ink(q,box,method):
    l,t,r,b=[min(1000,max(0,round(v))) for v in box]
    if r-l<3 or b-t<3:
        return None
    region=q[t:b,l:r]
    mask=method(region)
    xx=np.flatnonzero(mask.sum(0)>=2)
    yy=np.flatnonzero(mask.sum(1)>=2)
    if len(xx)<3 or len(yy)<3:
        return None
    return [l+int(xx[0]),t+int(yy[0]),int(xx[-1]-xx[0]+1),int(yy[-1]-yy[0]+1)]

def color_field(rgb,j):
    R,G,B=np.moveaxis(rgb,2,0)
    return (G-np.maximum(R,B),np.minimum(R,B)-G,R-B)[j]

def locate(full,f,j,reference_x,reference_y,diam):
    search=int(diam*.67)
    top,bottom=max(0,round(reference_y-search)),min(1000,round(reference_y+search))
    left,right=max(0,round(reference_x-search)),min(1000,round(reference_x+search))
    block=full[top:bottom,left:right]
    if block.size<200:
        return None
    yy,xx=np.mgrid[top:bottom,left:right]+.5
    rgba=block.astype(np.int16)
    reading=color_field(rgba,j)
    cut=[14,12,27][j]
    if j==1 and f>=290:
        cut=max(2,9-(f-290)*.55)
    m=(reading>cut)
    if j==2:
        m&=(rgba[:,:,0]>223)&(rgba[:,:,1]>168)
    if j==1:
        m&=rgba[:,:,0]>197
    choices,labels=per_component(m,left,top,600 if j!=2 else 550)
    if not choices:
        return None
    count, (l,a,r,b), component = choices[0]
    if (r-l)<30 or b-a<54 or count<600 or b-a<min(diam*.37,bottom-top-3):
        return None
    over=(r>=999 or b>=999)
    center0=[reference_x if over and r>=999 else (l+r)/2,(a+b)/2]
    ry=(b-a)/2
    rx=ry if over and r>=999 else (r-l)/2
    mask=binary_fill_holes(labels==component)
    js,is_=np.where(mask)
    angles=np.floor((np.arctan2(js+.5+top-center0[1],is_+.5+left-center0[0])+np.pi)*24/np.pi).astype(int).clip(0,47)
    weights=np.hypot(is_+.5+left-center0[0],js+.5+top-center0[1])
    rim=[]
    for idx in range(48):
        points=np.flatnonzero(angles==idx)
        if points.size:
            key=points[weights[points].argmax()]
            loc=[is_[key]+left+.5,js[key]+top+.5]
            if loc[0]<right-2 and loc[0]>left+2 and loc[1]>top+2 and loc[1]<bottom-2:
                rim.append(loc)
    if len(rim)<18:
        return None
    rim=np.array(rim)
    initial=np.array([*center0,rx,ry])
    span=np.array([max(18,diam*.15),23,32,25])
    def estimate(v):
        cx,cy,rx,ry=v
        residual=(np.hypot((rim[:,0]-cx)/rx,(rim[:,1]-cy)/ry)-1)*ry
        return np.append(residual,.10*(v-initial))
    lower=initial-span
    lower[2:]=np.maximum(lower[2:],18)
    fit=least_squares(estimate,initial,bounds=(lower,initial+span),loss='soft_l1',
                       f_scale=2.5,max_nfev=46)
    cx,cy,rx,ry=fit.x
    if j==1 and f>=291:
        # The pale right cheek becomes indistinguishable from paper.
        # Infer the hidden radius from the measured vertical disk extent.
        rx=max(rx,ry*.97)
    if j==1 and f>=293:
        # Use the stronger left boundary and the radius of the adjacent
        # actor as the right part of the pink disk recedes into paper.
        old_left=cx-rx
        rx=diam*.49
        ry=max(ry,diam*.47)
        cx=float(np.clip(old_left+rx,reference_x-28,reference_x+14))
        cy=float(np.clip(cy,reference_y-4,reference_y+9))
    rx+=.8+.6*(f==287); ry+=.65
    distance=np.hypot((xx-cx)/rx,(yy-cy)/ry)
    color=[]
    sampled=[]
    for y in np.linspace(.08,.92,9):
        yy0=cy+(2*y-1)*ry
        ring=(np.abs(yy-yy0)<7)&(distance>.76)&(distance<.93)
        if j==1:
            ring&=(xx<cx+rx*.25)
        pigment=full[top:bottom,left:right][ring&(reading>=(max(1,cut*.6) if j==1 else 6))]
        if len(pigment)>8:
            color.append(np.median(pigment,axis=0));sampled.append(y)
    if len(color)<3:
        return None
    stops=np.array([np.interp(np.linspace(0,1,9),sampled,q) for q in np.array(color).T]).T
    gradient=np.array([np.interp(yy[:,0],cy+np.linspace(-1,1,9)*ry,c) for c in stops.T]).T
    contrast=(np.max(abs(rgba-gradient[:,None,:]),axis=2)>35)&(rgba.min(2)<185)&(distance<.94)
    if j==1 and f>=293:
        contrast=(np.max(abs(rgba-gradient[:,None,:]),axis=2)>24)&(rgba.min(2)<223)&(distance<.92)
    candidates,marks=per_component(contrast,left,top,420)
    if candidates:
        _,(lx,ty,hx,by),picked=candidates[0]
        if hx-lx>rx*.66 and by-ty>ry*1.05 and hx-lx<rx*1.8:
            head=[lx-1,ty-1,hx+1,by+1]
        else:
            head=None
    else:
        head=None
    end=cy+ry
    threshold=157 if j!=1 or f<289 else 240
    name=ink(full,(cx-rx*.70,end+10,cx+rx*.69,end+ry*.50+10),
            lambda a:(a.mean(2)<threshold)&(np.ptp(a,axis=2)<40))
    if not name:
        name=[cx-rx*.28,end+17,rx*.56,ry*.25]
    y0=max(name[1]+name[3]+4,cy+ry*1.56) if j==1 and f>=293 else name[1]+name[3]+4
    phigh=max(2,round(cut*.63)) if j==1 and f>=292 else 13
    tone_mask=lambda rgb: (color_field(rgb, j)>phigh)&(rgb.min(2)>165)
    yl,yt,yr,yb=tuple(max(0,min(1000,round(v))) for v in (cx-rx*.87,y0,cx+rx*.86,y0+ry*.56))
    roi=full[yt:yb,yl:yr]
    found,rs=per_component(tone_mask(roi),yl,yt,110) if roi.size else ([],None)
    chip=None
    if found:
        _,chip,_=found[0]
    if not chip:
        chip=[cx-rx*.73,y0+5,cx+rx*.73,y0+ry*.34]
    x0,y0,x1,y1=chip
    c0,t0,c1,t1=[max(0,min(1000,round(v))) for v in chip]
    swatch=full[t0:t1,c0:c1]
    tones=swatch[swatch.min(2)>164] if swatch.size else []
    base=np.rint(np.median(tones,axis=0)).astype(int).tolist() if len(tones) else [[219,253,228],[253,219,251],[254,242,218]][j]
    box=[x0+(x1-x0)*.25,y0+(y1-y0)*.18,x1-(x1-x0)*.08,y1-(y1-y0)*.12]
    letters=ink(full,box,lambda c:(color_field(c,j)>(21 if j==1 and f>=290 else 31))&(c.min(2)<213))
    if letters is None:
        letters=[box[0],box[1],max(1,box[2]-box[0]),max(1,box[3]-box[1])]
    width,height=x1-x0,y1-y0
    glyph=[x0+width*.10,y0+height*.13,max(3,width*.135),max(3,height*.71)]
    fade=(.95 if f<288 else [1,.91,.80,.62,.42,.34,.26,.22][min(7,f-288)]) if j==1 else 1.
    if j==1 and f>=296:
        fade*=max(.37,1-(f-296)*.04)
    if j==2 and f==287:
        fade=.73
    return dict(oval=np.round([cx,cy,rx*2,ry*2],3).tolist(),tone=np.rint(stops).astype(int).tolist(),
        name=np.round(name,3).tolist(),chip=np.round(chip,3).tolist(),head=head,chipColor=base,
        text=np.round(letters,3).tolist(),glyph=np.round(glyph,3).tolist(),
        veil=round(float(fade),4),outline=round(interpolate(t['lisaOutline'],f)[0],3) if j==0 else 0.)

data={}
for f in (*range(267,271),*range(287,313)):
    a=np.asarray(Image.open(media/f'{f:06d}.png').convert('RGB'),dtype=np.int16)
    lx,y,w=interpolate(t['lisaProfileBounds'],f)
    ellax,=interpolate(t['ellaProfileX'],f)
    if f>=287:
        centers=(lx,ellax,1023 if f==287 else 1120)
    else:
        centers=(272,546,823)
    poses=[]
    for j,cx in enumerate(centers):
        pose=locate(a,f,j,cx,y if f>=287 else 436,w)
        if pose and j==1 and f<271:
            pose["veil"]=1
        if pose and j==2 and f<271:
            pose['nameCharacters']={267:2,268:2,269:2,270:3}[f]
        poses.append(pose)
    if poses[0] is None and f<312:
        print('Missing Lisa',f)
    data[f]=poses
    print(f,[(p['oval'],p['veil'],p['chip']) if p else None for p in poses],flush=True)
(root/'new-profiles.json').write_text(json.dumps(data,indent=2)+'\n')
