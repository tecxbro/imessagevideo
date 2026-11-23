from concurrent.futures import ProcessPoolExecutor
from copy import copy,deepcopy
from pathlib import Path
from PIL import Image
from render import Film, blur, composite, layer, registered_portrait
import json,sys
import numpy as np

p=Path(sys.argv[1])
scene=json.loads((p/'project/scene.json').read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')

def solve(f):
    key=str(f)
    m=deepcopy(scene['profileMotionRegistration'][key])
    goal=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.float32)
    base=np.asarray(Film(scene).frame(f),dtype=np.float32)
    modified=False
    for index,pose in enumerate(m['actors']):
        if not pose:
            continue
        cx,cy,width,height=pose['oval']
        asset=scene['profiles'][index][1]
        if asset=='lisa' and pose.get('wink',True):
            asset='lisa-wink'
        x0,y0,x1,y1=pose['head']
        l=max(0,round(cx-width*.40))
        t=max(0,round(cy-height*.435))
        r=min(1000,round(cx+width*.401))
        b=min(1000,round(cy+height*.437))
        source_image=goal[t:b,l:r]
        draw_w,draw_h=r-l,b-t
        head_start=[(x0+x1)/2,(y0+y1)/2,x1-x0,y1-y0]
        focus=pose.get('headFocus',0)
        if isinstance(focus,list):
            focus_x,focus_y=focus
        else:
            focus_x,focus_y=focus,focus
        values=[*head_start,focus_x,focus_y]
        visibility=pose.get('veil',1)
        head_alpha,rim_fade,head_wash,disk_wash=pose.get('exposure',
                    (visibility,(1-visibility)*.72 if index==1 else 0,0,0))
        def fit(v):
            xx,yy,w,h,vx,vy=map(float,v)
            head=[xx-w/2,yy-h/2,xx+w/2,yy+h/2]
            art,left,top=registered_portrait(cx,cy,width,height,pose['tone'][0],
                      asset,head,gradient=pose['tone'],head_opacity=head_alpha,
                      right_fade=rim_fade,head_wash=head_wash,disk_wash=disk_wash)
            im=layer(draw_w,draw_h)
            composite(im,blur(art,(vx,vy)),left-l,top-t,visibility if index==2 else 1)
            im=blur(im,tuple(m['focus']))
            paper=Image.new('RGBA',im.size,(253,253,253,255))
            paper.alpha_composite(im)
            a=np.asarray(paper.convert('RGB'),dtype=np.float32)
            error=float(np.abs(a-source_image).mean())
            return error
        initial=best=fit(values)
        for mul in (1,.52,.25):
            for i,step in enumerate((2.2,2.4,3.7,3.8,.70,.83)):
                start=values[i]
                for sign in (-2,-1,1,2):
                    change=values[:]
                    change[i]=start+step*sign*mul
                    if i>=4:
                        change[i]=max(0,change[i])
                    error=fit(change)
                    if error<best:
                        best,values=error,change
        xx,yy,w,h,fx,fy=values
        if best<initial-.06:
            pose['head']=[round(q,4) for q in (xx-w/2,yy-h/2,xx+w/2,yy+h/2)]
            pose['headFocus']=[round(fx,4),round(fy,4)]
            modified=True
    check=copy(scene)
    check['profileMotionRegistration']=copy(scene['profileMotionRegistration'])
    check['profileMotionRegistration'][key]=m
    current=np.asarray(Film(check).frame(f),dtype=np.float32)
    before=float(np.abs(goal-base).mean())
    after=float(np.abs(goal-current).mean())
    print(f,round(before,5),round(after,5),flush=True)
    if after<before and modified:
        return (key,m)

if __name__=='__main__':
    with ProcessPoolExecutor(max_workers=4) as pool:
        accepted=dict(z for z in pool.map(solve,range(260,271)) if z)
    (p/'profile-face-fit.json').write_text(json.dumps(accepted,indent=2)+'\n')
