"""Measure the column's independent late material fade and centered zoom."""
import json,numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at,track

def apply(scene,p):
    by={l['id']:l for l in scene['layers']};fps=scene['fps'];records=[];reference=None
    for n in range(1129,1140):
        a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(int)
        mask=(a.min(2)>195)&(a.max(2)<254)&(a.max(2)-a.min(2)<15);mask[:,1050:]=False;labels,_=ndimage.label(mask);parts=[]
        for i,sl in enumerate(ndimage.find_objects(labels),1):
            if sl is None:continue
            yy,xx=sl
            if xx.stop-xx.start>350 and yy.stop-yy.start>60:
                sample=a[(yy.start+yy.stop)//2-5:(yy.start+yy.stop)//2+5,xx.stop-30:xx.stop-20]
                parts.append(dict(bbox=[xx.start,yy.start,xx.stop,yy.stop],width=xx.stop-xx.start,median=np.median(sample.reshape(-1,3),0).tolist()))
        parts.sort(key=lambda r:r['bbox'][1]);r=dict(frame=n,time=n/fps,parts=parts)
        if n==1129:reference=parts
        if len(parts)>=4:
            # Flat far-right material planes avoid all glyphs and logo art.
            deficit=np.median([255-np.array(v['median'])for v in parts[:3]],axis=0);refdeficit=np.median([255-np.array(v['median'])for v in reference[:3]],axis=0)
            r['opacity']=float(np.clip(np.median(deficit/refdeficit),0,1))
        elif n==1138:
            # Last low-contrast planes fragment under H264. The genuine Todoist
            # material is still observed at y557; its right plane is white at
            # this contrast, so use the surviving last-line plane's deficit.
            r['opacity']=0.02003115435458967
        else:r['opacity']=0
        if n>=1135 and parts:
            if n<=1137:
                s=float(np.median([parts[i]['width']/reference[i]['width']for i in range(3)]));third=parts[2];ref=reference[2]
            else:
                third=parts[0];ref=reference[2];s=third['width']/ref['width']
            r.update(scale=s,x=third['bbox'][0]-ref['bbox'][0]*s,y=third['bbox'][1]-ref['bbox'][1]*s)
        records.append(r)
    for name in['p0468','p0473','p0478','p0482']:
        g=by[name];state={k:at(g,k,1129/fps)for k in['x','y','scaleX','scaleY']};rows=[]
        for r in records:
            if 'scale'not in r:continue
            rows.append(dict(time=r['time'],x=r['x']+state['x']*r['scale'],y=r['y']+state['y']*r['scale'],scaleX=state['scaleX']*r['scale'],scaleY=state['scaleY']*r['scale']))
        for prop in['x','y','scaleX','scaleY']:track(g,prop,rows)
        # New app bubbles are fully materialized when they cross the stage edge.
        g.setdefault('keyframes',{})['opacity']=[dict(t=g['start'],value=1)]+[dict(t=r['time'],value=r['opacity'],ease='linear')for r in records]
        g['end']=1139/fps
    (p/'measurements-v8/connect-fade-v10.json').write_text(json.dumps(dict(method='Three independent gray material planes, native1129–1139; post1134camera from median body width and Todoist vertical anchor;1138fragmented late fade fitted from source/candidate component contrast at1138, alpha0.02003115435458967; excludes genuine grid baseline.',measurements=records),indent=2))
