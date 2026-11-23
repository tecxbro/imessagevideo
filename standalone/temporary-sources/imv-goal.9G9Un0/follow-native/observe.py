import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

work=Path(__file__).parent
project=work.parent/'sidehoe-clean-project'
sys.path.insert(0,str(project))

prior={
    int(row['frame']):row for row in csv.DictReader(
        open('sidehoe-skill-trial/repair/reviewer-audit/follow-pointer.csv'))
}
frames=range(672,698)
labels=('source','pre2000','encoded')
read=lambda label,f: np.asarray(Image.open(work/label/f'{f:06d}.png').convert('RGB'))

def cross(values,index,limit,direction):
    for x in range(index, limit, direction):
        y=x+direction
        a,b=values[x],values[y]
        if a<=0<b:
            return x+direction*(-a)/(b-a)
    return None

def rail(image,hints):
    rgb=image.astype(np.float32)
    zones=[(360,460),(740,840),(1500,1580)]
    result=[]
    for x,dir_ in zip(hints,[-1,1]):
        zs=[]
        for y0,y1 in zones:
            lum=np.median(rgb[y0:y1].mean(2),axis=0)
            # Registration is independently calculated in each band; hints only bound the search.
            left=max(5,round(x)-60);right=min(1995,round(x)+60)
            trough=left+int(np.argmin(lum[left:right]))
            stage_idx=round(x+dir_*110)
            stage=float(np.median(lum[stage_idx-6:stage_idx+7]))
            dark=float(lum[trough])
            if stage-dark<60 or not (12<trough<1988):
                continue
            stop=max(1,round(x)-90) if dir_<0 else min(1998,round(x)+90)
            edge=cross(lum-(stage+dark)/2,trough,stop,dir_)
            low=cross(lum-(dark+.2*(stage-dark)),trough,stop,dir_)
            high=cross(lum-(dark+.8*(stage-dark)),trough,stop,dir_)
            if edge is None or low is None or high is None:continue
            zs.append([round(edge,3),round(abs(high-low),3),round(dark,2)])
        if len(zs)!=len(zones):
            raise ValueError((hints,x,zs))
        data=np.asarray(zs)
        result.append(dict(x=round(float(np.median(data[:,0])),3),
                           bandSpread=round(float(np.ptp(data[:,0])),3),
                           edgeWidth20to80=round(float(np.median(data[:,1])),3),
                           minimumLuma=round(float(np.median(data[:,2])),3),
                           zones=zs))
    return result

def components(im, roi, seed, threshold, candidate_alpha=None):
    x0,y0,x1,y1=roi
    sub=im[y0:y1,x0:x1].mean(2)
    mask=sub<threshold
    if candidate_alpha is not None:
        mask &= candidate_alpha[y0:y1,x0:x1]
    lab,n=ndimage.label(mask,np.ones((3,3)))
    records=[]
    for idx,bb in enumerate(ndimage.find_objects(lab),1):
        if bb is None:continue
        yy,xx=bb
        ww,hh=xx.stop-xx.start,yy.stop-yy.start
        iy,ix=np.where(lab[bb]==idx)
        if len(ix)<85 or ww<=10 or hh<=18:continue
        t=y0+yy.start
        top_x=(np.median(ix[iy==0])+xx.start+x0)
        sx,sy=seed
        err=(float(top_x)-sx)**2+(t-sy)**2
        if err<60**2:
            records.append((err,dict(tip=[round(float(top_x),2),int(t)],area=len(ix),bbox=[x0+xx.start,t,x0+xx.stop,y0+yy.stop],minLuma=round(float(sub[bb][lab[bb]==idx].min()),2))))
    return min(records,key=lambda q:q[0])[1] if records else None

result=[]
evaluated=json.loads((work/'evaluated.json').read_text())
for f in frames:
    state=evaluated[str(f)]
    if not state:
        result.append(dict(frame=f,controls='follow actors absent in evaluator'))
        continue
    alpha=Image.open(work/'mask'/f'{f:06d}.png')
    isolated_alpha=np.asarray(alpha.resize((2000,2000),Image.Resampling.BILINEAR))>12
    pages={label:read(label,f) for label in labels}
    for label in labels:
        xp,yp=state['cursorPivot']
        if label=='source':
            default=[958,1118]
            row=prior.get(f,{})
            guess=[float(row['source_tip_x']),float(row['source_tip_y'])] if row.get('source_tip_x') else default
            xs,ys=guess
            roi=[round(xs-18),round(ys-12),round(xs+110),min(1430,round(ys+177))]
        else:
            guess=[xp+7,yp+7]
            roi=[round(xp-15),round(yp-10),round(xp+155),round(yp+185)]
        measurements=[]
        for threshold in [85,110,150,185]:
            measurements.append(components(pages[label],roi,guess,threshold,None if label=='source' else isolated_alpha))
        state[label]=dict(rail=rail(pages[label],state['railOuter']),pointer=measurements,roi=roi)
    result.append(dict(frame=f,**state))
(work/'analysis.json').write_text(json.dumps(result,indent=2,default=lambda v:v.item())+'\n')
for r in result:
    if 'source' not in r:print(r);continue
    print(r['frame'],[r[l]['pointer'][1] and r[l]['pointer'][1]['tip'] for l in labels],
          [[round(edge['x'],1) for edge in r[l]['rail']] for l in labels],
          [round(x,1) for x in r['cursorPivot']],
          [r['source']['pointer'][i] and r['source']['pointer'][i]['tip'] for i in (0,2,3)])
