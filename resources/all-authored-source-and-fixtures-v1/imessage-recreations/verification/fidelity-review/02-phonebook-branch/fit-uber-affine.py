from pathlib import Path
import numpy as np,json
from scipy.optimize import minimize
from PIL import Image,ImageDraw
P=Path('/workspace/imessage-recreations/verification/fidelity-review/02-phonebook-branch');art=np.array(Image.open(P/'uber-480.png').crop((35,69,630,179)));im=Image.fromarray(art);src=Image.open(P/'uber-477.png');target=np.array(src).astype(float);box=(20,45,650,185)
def warp(p):
 a,b,e,tx,ty=p
 inv=[1/a,-b/a/e,297.5-tx/a+b*ty/a/e,0,1/e,55-ty/e]
 return im.transform((680,230),Image.Transform.AFFINE,inv,Image.Resampling.BILINEAR,fillcolor=(253,253,253))
def loss(p):
 aa=np.array(warp(p)).astype(float);d=np.abs(np.clip(253-aa,0,253)-np.clip(253-target,0,253));return d[box[1]:box[3],box[0]:box[2]].mean()
p0=[1,0,.84,331.5,112.5];r=minimize(loss,p0,method='Powell',bounds=[(.9,1.1),(-1,1),(.65,1.2),(320,345),(100,130)],options={'maxiter':30,'xtol':.0001,'ftol':.00005});print(r.fun,r.x);f=warp(r.x);sheet=Image.new('RGB',(1360,230),'white');sheet.paste(src,(0,0));sheet.paste(f,(680,0));sheet.save(P/'uber-affine-fit.png');(P/'uber-affine-fit.json').write_text(json.dumps(dict(params=r.x.tolist(),crop_mae=float(np.abs(np.array(f).astype(float)-target).mean()),fit_loss=r.fun,success=bool(r.success)),indent=2))
