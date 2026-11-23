from pathlib import Path
import json
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates,minimum_filter,maximum_filter,gaussian_filter
from scipy.optimize import least_squares

root=Path(__file__).parent
sys.path.insert(0,str(root/'title-project'))
from artwork import curved_heart
from render import Film,interpolate
scene=json.loads((root/'title-project/scene.json').read_text())
tracks=scene['tracks']['personalHearts']
case=json.loads((root/'title-project/scene.json').read_text())
# Use an independent, authored title plate to isolate the overlays.
for track in case['tracks']['personalHearts']:
    for row in track:
        row[-1]=0
film=Film(case)
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
mask=np.asarray(curved_heart(180,180,(247,143,253)).getchannel('A'),dtype=np.float32)/255
tone=np.array([247.,143.,253.])
result={}
for f in range(186,207):
    base=np.asarray(film.frame(f),dtype=np.float32)
    reference=np.asarray(Image.open(src/f'{f:06d}.png').convert('RGB'),dtype=np.float32)
    chroma=lambda v:np.stack((v[:,:,0]-v[:,:,1],v[:,:,2]-v[:,:,1],v[:,:,1]),axis=-1)
    output=[]
    for group in ((0,1,2),(3,4),(5,6,7,8)):
        guide=np.array([interpolate(tracks[i],f) for i in group],dtype=float)
        x,y,w,h=guide[:,:4].T
        left=max(0,int(min(x-w*.78))-10)
        top=max(0,int(min(y-h*.78))-10)
        right=min(1000,int(max(x+w*.78))+11)
        bottom=min(1000,int(max(y+h*.78))+11)
        xi,yi=np.meshgrid(np.arange(left,right,2)+.5,np.arange(top,bottom,2)+.5)
        base_roi=base[top:bottom:2,left:right:2]
        aim=chroma(reference[top:bottom:2,left:right:2])
        local_luma=base_roi[:,:,1]
        edge=(maximum_filter(local_luma,size=4)-minimum_filter(local_luma,size=4))
        weight=np.where(edge>24,.37,1.)[:,:,None]*[1.,1.,.10]
        seeds=np.column_stack([guide,np.zeros(len(guide)),np.full(len(guide),.6)])
        def loss(p):
            v=base_roi.copy()
            for x,y,w,h,a,alpha,shear,sigma in p.reshape(-1,8):
                a=np.deg2rad(a)
                dx,dy=xi-x,yi-y
                uy=(np.sin(a)*dx+np.cos(a)*dy)/h
                ux=(np.cos(a)*dx-np.sin(a)*dy)/w-shear*uy
                coverage=map_coordinates(mask,[(uy+.5)*180-.5,(ux+.5)*180-.5],order=1,mode='grid-constant',
                                         cval=0,prefilter=False)
                coverage=gaussian_filter(coverage,sigma/2)*alpha
                v=v+(tone-v)*coverage[:,:,None]
            error=(chroma(v)-aim)*weight
            regular=(p.reshape(-1,8)-seeds)*[.85,.85,.44,.44,.12,5.,14.,2.1]
            return np.concatenate((error.ravel(),regular.ravel()))
        lower=seeds+[-7,-7,-8,-8,-18,-1,-.26,-.52]
        upper=seeds+[7,7,8,8,18,1,.26,1.52]
        lower[:,2:4]=np.maximum(lower[:,2:4],3)
        lower[:,5],upper[:,5]=0,1
        guess=np.clip(seeds,lower+.00001,upper-.00001)
        sol=least_squares(loss,guess.ravel(),bounds=(lower.ravel(),upper.ravel()),loss='soft_l1',
                     f_scale=6.5,diff_step=.005,max_nfev=28)
        output.extend(np.round(sol.x.reshape(-1,8),4).tolist())
    result[f]=output
    print(f,flush=True)
(root/'title-hearts-fit.json').write_text(json.dumps(result,indent=2)+'\n')
