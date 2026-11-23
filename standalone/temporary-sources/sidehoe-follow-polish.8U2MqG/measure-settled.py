from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from render import Film,fit_ink,layer,interpolate
from artwork import messages_font

root=Path(sys.argv[1]); source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
data=json.loads((root/'project/scene.json').read_text())
film=Film(data)
def front_fit(frame,ref,caption,box,paper,initial,spec=None):
    x,y,w,h=box
    l,t,r,b=max(0,round(x)-8),max(0,round(y)-6),min(400,round(x+w)+12),min(827,round(y+h)+5)
    base=Image.fromarray(np.uint8(np.rint(np.broadcast_to(paper[t:b,None,:],(b-t,r-l,3)).copy()))).convert('RGBA')
    target=ref[t:b,l:r].astype(np.int16)
    def score(params):
        xx,yy,ww,hh,weight,shade,spread=map(float,params)
        view=base.copy()
        fit_ink(view,caption,(xx-l,yy-t,ww,hh),round(weight),1,spread,
                family=messages_font,ink=(round(shade),)*3,fractional=True)
        rgb=np.asarray(view,dtype=np.int16)[:,:,:3]
        return float(abs(rgb-target).mean())
    old=[*box,*initial]
    before=score(old)
    params=old[:] if spec is None else spec[:]
    best=score(params)
    for scale in (1,.52,.25):
        for i,step in enumerate((.6,.66,1.35,.58,17,10,.32)):
            center=params[i]
            for n in (-2,-1,1,2):
                trial=params[:]; trial[i]=center+n*step*scale
                if not (320<=trial[4]<=570 and 12<=trial[5]<=255 and .20<=trial[6]<=3.5 and trial[3]>3.5):
                    continue
                error=score(trial)
                if error<best:
                    best,params=error,trial
    if best>before-.10:
        return None
    color=[round(float(params[5]))]*3
    return {'box':[round(float(a),4) for a in params[:4]],'weight':round(float(params[4])),
            'color':color,'blur':round(float(params[6]),4)}

def composer(ref,reg,ky):
    orig=reg['composerY']; red=ref[:,:,0]
    y0=max(0,round(orig)-9)
    y1=min(round(ky)-1,round(orig)+39)
    middle=np.mean(red[y0:y1,202:273],axis=1)
    i=np.flatnonzero(middle<240)
    if len(i)<2 or i[-1]-i[0]<26:
        return None
    t,b=y0+i[0],y0+i[-1]
    center=(t+b)/2
    lo=red[round(center),60:82]
    hi=red[round(center),362:384]
    l,r=60+int(lo.argmin()),362+int(hi.argmin())
    if lo.min()>244 or hi.min()>244 or r-l<280:
        return None
    a=red[round(center)-10:round(center)+11,29:61]
    yy,xx=np.where(a<211)
    if not len(xx): return None
    cx,cy=float(29+(xx.min()+xx.max())/2),float(round(center)-10+(yy.min()+yy.max())/2)
    f=np.flatnonzero((red[round(cy),18:65]<246) & (abs(np.arange(18,65)-cx)<17.0))
    if len(f)<19: return None
    radius=min(16.4,float((f[-1]-f[0]+1)/2))
    yy,xx=np.where(red[round(center)-9:round(center)+12,l+7:l+98]<222)
    if not len(xx): return None
    label=[float(l+7+xx.min()),float(round(center)-9+yy.min()),float(xx.max()-xx.min()+1),float(yy.max()-yy.min()+1)]
    area=red[round(center)-13:round(center)+16,r-40:r-8]
    yy,xx=np.where(area<225)
    if not len(xx): return None
    mic=[float(r-40+(xx.max()+xx.min())/2),float(round(center)-13+yy.min()+.39*(yy.max()-yy.min())),
         round(float((yy.max()-yy.min()+1)/27),4)]
    return dict(outline=[float(l),float(t+.35),float(r),float(b+.12)],
                plus=[cx,cy,radius],microphone=mic,text=label,stroke=1.16)

def frame_fit(f):
    frame=str(f)
    reg=data['followSettledRegistration'].get(frame)
    assert reg,frame
    x,y,s=film.track('followMeasuredCamera',f)
    aspect=1
    if 'camera' in reg:
        x,y,s,aspect=reg['camera']
    source_frame=Image.open(source/f'{f:06}.png').convert('RGB')
    ref=np.asarray(source_frame.transform((400,827),Image.Transform.AFFINE,(s,0,x,0,s*aspect,y),
                                          Image.Resampling.BICUBIC),dtype=np.int16)
    paint={}
    bounds,stops=reg['blue']
    l,t,r,b=bounds
    h=b-t
    grid=np.linspace(t,b,len(stops)+2)[1:-1]
    pigment=np.stack([np.interp(np.arange(827),grid,c) for c in np.asarray(stops).T],axis=1)
    words=data['copy']['follow'][1]
    for j,line in enumerate(words):
        u,v=l+14,t+h*(.205+.31*j)
        w=min(r-l-34,max(12,len(line)*8))
        hh=h*.24
        look=front_fit(f,ref,line,[u,v,w,hh],pigment,[420,247,.55],
                       [u-3,v-1,w+2,hh+1,426,250,.76])
        paint.setdefault('blueInkAppearance',[]).append(look or {'box':[u,v,w,hh],'weight':420,'color':[247]*3,'blur':.55})
    for i,(extent,boxes) in enumerate(reg['bubbles']):
        shade=(239,239,242) if i==0 else (232,232,235)
        color=np.repeat([shade],827,axis=0)
        for j,(msg,box) in enumerate(zip(data['copy']['follow'][i+2],boxes,strict=True)):
            p=front_fit(f,ref,msg,box,color,[420 if i==0 else 475,86 if i==0 else 39,.55])
            if p: paint.setdefault('inkAppearance',{})[f'{i}:{j}']=p
    comp=composer(ref,reg,reg['layout'][0])
    if comp: paint['composer']=comp
    print(f,list(paint),len(paint.get('inkAppearance',{})),flush=True)
    return frame,paint

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=7) as pool:
        result=dict(pool.map(frame_fit,range(634,660)))
    (root/'settled-ink-fit.json').write_text(json.dumps(result,indent=2)+'\n')
