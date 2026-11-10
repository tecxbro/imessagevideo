"""Refine physical body from complete silhouettes; retain source view cap813–835."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent;P=R/'verification/fidelity-review/03-game'
records=json.load(open(P/'presentation-measurements.json'))
image=Image.open(REF/'assets/phone-hardware.png').convert('RGBA');rgb=np.asarray(image).astype(float);a=rgb[:,:,3,None]/255;template=rgb[:,:,:3]*a+253*(1-a)
def box(pixels,threshold,region=None):
    mask=pixels.mean(2)<threshold
    if region is not None:mask&=region
    labels,count=ndimage.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0;index=sizes.argmax();yy,xx=np.where(labels==index)
    return [float(xx.min()),float(yy.min()),float(xx.max()+1),float(yy.max()+1)]
thresholds=[225,235,243];tb={v:box(template,v)for v in thresholds}
for row in records:
    f=row['frame'];pixels=np.asarray(Image.open(REF/'montage-native'/f'{f-794:03}.png').convert('RGB')).astype(float)
    region=np.zeros(pixels.shape[:2],bool);region[:,650:1280]=True
    samples=[]
    for v in thresholds:
        source=box(pixels,v,region);t=tb[v]
        sx=(source[2]-source[0])/((t[2]-t[0])*800/template.shape[1]);sy=(source[3]-source[1])/((t[3]-t[1])*1658/template.shape[0])
        x=source[0]-t[0]*800/template.shape[1]*sx;y=source[1]-t[1]*1658/template.shape[0]*sy
        samples.append(dict(threshold=v,box=source,scaleX=sx,scaleY=sy,x=x,y=y))
    body={k:float(np.median([q[k]for q in samples]))for k in ['x','y','scaleX','scaleY']}
    body['thresholdFits']=samples;row['body']=body
    top=row['sheetTop'];neutral=(pixels.max(2)-pixels.min(2)<6)&(pixels.mean(2)>70)&(pixels.mean(2)<253)
    roi=np.zeros(neutral.shape,bool);roi[round(body['y'])+5:top,round(body['x']):round(body['x']+800*body['scaleX'])]=True
    labels,count=ndimage.label(neutral&roi);sizes=np.bincount(labels.ravel());sizes[0]=0
    if len(sizes)>1 and sizes.max()>1000:
        index=sizes.argmax();mask=ndimage.binary_fill_holes(labels==index);yy,xx=np.where(mask);color=np.median(pixels[labels==index],axis=0)
        row['view']=dict(box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],color=color.tolist(),opacity=float(np.mean(color)/253),area=int(mask.sum()))
    print(f,body['x'],body['y'],body['scaleX'],body['scaleY'],row['view'],flush=True)
(P/'presentation-refined.json').write_text(json.dumps(records,indent=2))
