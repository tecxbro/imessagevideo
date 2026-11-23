from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
from scipy.ndimage import label,find_objects
p=Path(__file__).parent
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
proj=p/'withdrawal-project'
scene_path=proj/'scene.json'
scene=json.loads(scene_path.read_text())
sys.path.insert(0,str(proj))
from render import interpolate
s=scene['tracks']
wallet=json.loads((p/'withdrawal-measurements.json').read_text())
for f in (694,695):
    record=wallet[str(f)][0]
    a=np.asarray(Image.open(src/f'{f:06d}.png').convert('RGB'),dtype=np.int16)
    l,r=record['rails']
    stage_x,stage_y,scale=interpolate(s['followMeasuredCamera'],f)
    sample=a[:,l:r,0]
    key_y=(707,672)[f-694]
    tray=np.median(sample[key_y-36:key_y],axis=1)
    top=next((key_y-36+i for i,y in enumerate(tray) if 181<y<235),key_y-round(8*scale))
    case=np.median(a[592:625],axis=(0,2))
    ramps=[]
    for lo,hi in ((round(stage_x-13),l+5),(r-5,round(stage_x+400*scale+13))):
        ramps.append([lo,hi,np.rint(np.interp(np.linspace(lo,hi,17),np.arange(1000),case)).astype(int).tolist()])
    blue=record['blue'][0][1].copy()
    if f==694:blue[1]=73
    items=record['gray'][-3:-1]
    ink=[]
    for j,(left,top_c,right,bottom) in enumerate(items):
        h=bottom-top_c
        cuts=((.14,.49),(.50,.88)) if j==0 else ((.11,.37),(.377,.65),(.65,.92))
        lines=[]
        for open_,close in cuts:
            yy1,yy2=round(top_c+h*open_),round(top_c+h*close)
            xx=int(left+max(19,h*.18))
            area=a[yy1:yy2,xx:right-10]
            use=area.max(axis=2)<(213 if j==0 else 178)
            ys=np.flatnonzero(use.sum(1)>=2)
            xs=np.flatnonzero(use.sum(0)>=2)
            if not ys.size or not xs.size:
                lines.append([xx,yy1,round((right-xx)*(.90 if close<.8 else .55)),round(h*.19)])
            else:
                lines.append([xx+int(xs[0]),yy1+int(ys[0]),int(xs[-1]-xs[0]+1),int(ys[-1]-ys[0]+1)])
        ink.append([(left,top_c,right,bottom),lines])
    border_y=key_y
    rows=[]
    width=(r-l-11)/10
    px0=l+6
    for (yy,count,ww),initial_offset in zip([r0 for r0 in record['tray'] if r0[1]>=7], (0,.5,1.5)):
        rows.append([round(px0+initial_offset*width,3)+2,yy,width,ww,round(40*scale),10])
    assert len(rows)==3
    today_y=(295,327)[f-694]
    scene['threadRegistration']['follow'][str(f)]=dict(
        rails=[l,r],keys=[top,[215,216,221],rows],items=ink,
        today=[473,today_y,54 if f==694 else 49,19 if f==694 else 15],
        blue=blue,edgeRamps=ramps,corners=[20 if f==694 else 16,29 if f==694 else 26],
        no=record['gray'][-1],railStart=150 if f==695 else 20,
        focus=[12,-13,2.2] if f==694 else [16,10,1.75]
    )
scene_path.write_text(json.dumps(scene,indent=2)+'\n')
