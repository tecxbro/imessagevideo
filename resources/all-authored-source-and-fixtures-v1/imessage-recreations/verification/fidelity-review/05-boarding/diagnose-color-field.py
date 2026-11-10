from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/05-boarding';BASE=R/'outputs/05-linq/final-v11';sc=json.load(open(BASE/'scene.json'));g=next(l for l in sc['layers']if l['id']=='g-942');fits=json.load(open(P/'exposure-fit.json'));rows=[]
for q in fits['frames']:
    f=q['frame'];S=np.array(Image.open(P/'source'/f'{f-1181:04d}.png').convert('RGB')).astype(float);field=next(l for l in g['children']if l['id']==f'root-boarding-color-field-{f}');T=np.array(Image.open(BASE/field['src']).convert('RGBA')).astype(float);z=np.arange(720)-q['baseY']-round(field['y']);valid=(z>=0)&(z<len(T));B=T[np.clip(z,0,len(T)-1),:,:3];al=T[np.clip(z,0,len(T)-1),:,3];mask=valid[:,None]&(al>254)&(S.max(2)<220)&(S.max(2)-S.min(2)>12)&(S.mean(2)>15)&(abs(S-B).mean(2)<12)
    yy,xx=np.mgrid[0:720,0:960];train=mask&((yy%4)==0)&((xx%4)==0);test=mask&((yy%4)==2)&((xx%4)==2);row=dict(frame=f,validPixels=int(mask.sum()),originalMAE=float(abs(S[mask]-B[mask]).mean()),degrees=[])
    for degree in [3,4,5,6]:
        terms=[(i,j)for i in range(degree+1)for j in range(degree+1-i)];x=(xx[train]-480)/480;y=(yy[train]-360)/360;A=np.stack([x**i*y**j for i,j in terms],1);target=S[train];co=np.linalg.lstsq(A,target,rcond=1e-11)[0]
        for _ in range(2):
            keep=abs(A@co-target).mean(1)<5;co=np.linalg.lstsq(A[keep],target[keep],rcond=1e-11)[0]
        vx=(xx[test]-480)/480;vy=(yy[test]-360)/360;V=np.stack([vx**i*vy**j for i,j in terms],1);error=float(abs(V@co-S[test]).mean());row['degrees'].append(dict(degree=degree,validationMAE=error,terms=terms,coefficients=co.tolist()))
    rows.append(row);print(f,row['originalMAE'],[(d['degree'],d['validationMAE'])for d in row['degrees']],flush=True)
(P/'color-field-diagnosis.json').write_text(json.dumps(rows,indent=2))
