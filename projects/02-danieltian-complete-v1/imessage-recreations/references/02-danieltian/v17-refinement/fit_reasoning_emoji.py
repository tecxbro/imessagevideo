"""Fit independent authentic emoji using chroma, excluding adjacent neutral glyphs."""
from pathlib import Path
from PIL import Image
import numpy as np,cv2,json
from scipy.optimize import least_squares
R=Path(__file__).resolve().parent
art=json.loads((R/'emoji-art/provenance.json').read_text())
clusters={q['frame']:q['clusters']for q in json.loads((R/'reasoning-color-clusters.json').read_text())}
results={}
def classify(f):
    c=clusters.get(f,[]);out={}
    left=sorted([q for q in c if q['center'][0]<450 and q['pixels']>60],key=lambda q:q['center'][1])
    if f<=363:
        names=['heads']+(['house']if f>=289 else[])+(['car']if f>=292 else[])+(['food']if f>=295 else[])
        if len(left)==len(names):out.update(zip(names,left))
    for q in c:
        x,y=q['center']
        if q['pixels']<20:continue
        if 450<x<1000 and 300<y<700 and q['pixels']>out.get('pin',{}).get('pixels',0):out['pin']=q
        if x>1000 and 300<y<700 and q['pixels']>out.get('heart',{}).get('pixels',0):out['heart']=q
    return out
for name,info in art.items():
    rgba=np.asarray(Image.open(info['file']).convert('RGBA')).astype(np.float32)
    delta=(rgba[:,:,:3]-253)*(rgba[:,:,3:4]/255)
    signal=np.stack([delta[:,:,0]-delta[:,:,1],delta[:,:,1]-delta[:,:,2]],2)
    colormask=np.abs(signal).max(2)>12
    yy,xx=np.nonzero(colormask);refbox=[xx.min(),yy.min(),xx.max()+1,yy.max()+1]
    refcenter=np.array([(refbox[0]+refbox[2])/2,(refbox[1]+refbox[3])/2])
    refsize=np.array([refbox[2]-refbox[0],refbox[3]-refbox[1]])
    poses=[]
    for f in range(272,373):
        objects=classify(f)
        if name not in objects:continue
        obj=objects[name];x0,y0,x1,y1=obj['bounds'];pad=24
        left=max(0,x0-pad);top=max(0,y0-pad);right=min(1920,x1+pad);bottom=min(1080,y1+pad+45)
        rgb=np.asarray(Image.open(R/'reasoning-source'/f'source-{f:04d}.png').convert('RGB')).astype(np.float32)[top:bottom,left:right]
        target=np.stack([rgb[:,:,0]-rgb[:,:,1],rgb[:,:,1]-rgb[:,:,2]],2)
        center=np.array(obj['center']);scale=np.array([x1-x0,y1-y0])/refsize
        sx,sy=scale
        initial=np.array([center[0],center[1],sx,sy,1.,max(0.,(7-(f-272)*1.2)) if f<280 else .15])
        # Full pin stem can enter/leave the color test with gray chroma; use head width to seed aspect.
        if name=='pin':initial[3]=initial[2]
        lo=np.array([center[0]-22,center[1]-22,max(.03,sx*.55),max(.03,sy*.45),.15,0.])
        hi=np.array([center[0]+22,center[1]+22,sx*1.65+0.1,sy*2.5+.1,1.8,15.])
        if name=='pin':lo[3]=max(.03,sx*.55);hi[3]=sx*1.65+.1
        initial=np.maximum(lo+.0001,np.minimum(hi-.0001,initial))
        def predict(p):
            cx,cy,ax,ay,alpha,sigma=p
            matrix=np.array([[ax,0,cx-left-refcenter[0]*ax],[0,ay,cy-top-refcenter[1]*ay]],dtype=np.float32)
            warped=cv2.warpAffine(signal,matrix,(right-left,bottom-top),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
            if sigma>.03:warped=cv2.GaussianBlur(warped,(0,0),sigma,borderType=cv2.BORDER_CONSTANT)
            return warped*alpha
        def residual(p):return ((predict(p)-target)/35).ravel()
        eps=np.array([.2,.2,.003,.003,.005,.06])
        def jac(p):
            vals=[]
            for k,step in enumerate(eps):
                a=p.copy();b=p.copy();a[k]+=step;b[k]-=step
                if k==5 and b[k]<0:b[k]=0
                vals.append((residual(a)-residual(b))/(a[k]-b[k]))
            return np.stack(vals,1)
        fit=least_squares(residual,initial,jac=jac,bounds=(lo,hi),max_nfev=32,ftol=.001,xtol=.0001,gtol=.005)
        cx,cy,sx,sy,alpha,sigma=fit.x
        pose={'frame':f,'x':float(cx-refcenter[0]*sx),'y':float(cy-refcenter[1]*sy),'width':float(info['width']*sx),'height':float(info['height']*sy),'opacity':float(alpha),'blur':float(sigma),'rmsChroma':float(np.sqrt(np.mean((predict(fit.x)-target)**2))),'sourceColorBounds':obj['bounds'],'nfev':fit.nfev}
        poses.append(pose)
        if f in [272,273,275,280,293,300,320,360,361,363,367]:print(name,f,{k:round(v,3)if isinstance(v,float)else v for k,v in pose.items()},flush=True)
    results[name]={'art':info,'poses':poses}
    (R/'emoji-fit-candidate.json').write_text(json.dumps(results,indent=2))
print('complete',flush=True)
