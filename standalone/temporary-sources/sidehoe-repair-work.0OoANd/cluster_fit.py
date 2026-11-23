from pathlib import Path
import json
import numpy as np
from PIL import ImageColor
from phones import load
p=Path('sidehoe-skill-trial/repair/project/scene.json')
d=json.loads(p.read_text()); t=d['tracks']
outer=t['clusterPose']
def at(track,f):
    a=np.array(track)
    return np.array([np.interp(f,a[:,0],a[:,i]) for i in range(1,a.shape[1])])
ios=[]
for i,(actor,cx,cy,base_radius,_,color) in enumerate(d['cluster']):
    seed=[*t['clusterEntrance'][i][-1][:4]]
    prior=t['clusterEntrance'][i][-1][1:4]
    expected_color=np.array(ImageColor.getrgb(color))
    track=[]
    for f in range(227,254):
        dx,dy,scale=at(outer,f)
        prediction=np.array([500+(cx-500)*scale+dx,492+(cy-500)*scale+dy,2*base_radius*scale])
        initial=np.clip((f-226)/8,0,1)
        if f<=234:
            projection=(1-initial)*np.array(prior)+initial*prediction
        else:
            projection=prediction
        x,y,diam=projection
        radius=diam/2
        x0=max(0,round((x-radius*1.39)/2));x1=min(500,round((x+radius*1.39)/2))
        y0=max(0,round((y-radius*1.39)/2));y1=min(500,round((y+radius*1.39)/2))
        if x1<=x0 or y1<=y0:
            values=projection
        else:
            a=load('source',f)[y0:y1,x0:x1]
            local_y,local_x=np.mgrid[y0:y1,x0:x1]*2
            distance=np.linalg.norm(a-expected_color,axis=2)
            radial=np.hypot((local_x-x),(local_y-y))
            mask=(distance<=21)&(radial<radius*1.32)
            ys,xs=np.where(mask)
            if len(xs)<30:
                values=projection
            else:
                l,h=np.percentile(xs,[.9,99.1])
                u,b=np.percentile(ys,[.9,99.1])
                w1=l+h+2*x0
                h1=u+b+2*y0
                size1=max(h-l,b-u)*2+3
                if not (.64*diam<=size1<=1.25*diam and abs(w1-x)<radius*.52 and abs(h1-y)<radius*.52):
                    values=projection
                else:
                    values=np.array([w1,h1,size1])
                    values=.91*values+.09*projection
        track.append([f,*[round(float(z),2) for z in values],1])
    print(i, track[0],track[10],track[-1])
    ios.append(track)
t['clusterVisibleDisks']=ios
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
