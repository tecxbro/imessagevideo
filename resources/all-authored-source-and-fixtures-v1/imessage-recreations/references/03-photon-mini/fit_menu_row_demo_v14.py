"""Read-only affine registration experiment for a bounded static menu row."""
from pathlib import Path
from PIL import Image
import numpy as np,json
from scipy import ndimage,optimize
p=Path(__file__).parent;r={r['frame']:r for r in json.loads((p/'menu-world-v13-measurements.json').read_text())};ref=651;target=700;row=2;rr=r[ref];qq=rr['matches'][row];ss=rr['scale'];box=(round(qq['x']-489*ss),round(qq['y']-12*ss),round(qq['x']+190*ss),round(qq['y']+224*ss));template=Image.open(p/'lunch-native'/f'{ref-609:03}.png').crop(box).convert('RGB');out=p/'menu-row-demo-v14';out.mkdir(exist_ok=True);template.save(out/'row-2.png');W,H=template.size;tr=np.array(template.resize((round(W/2),round(H/2)),Image.Resampling.LANCZOS),dtype=float);src=np.array(Image.open(p/'lunch-native'/f'{target-609:03}.png').resize((960,540),Image.Resampling.LANCZOS),dtype=float);grad=np.hypot(ndimage.sobel(tr.mean(2),0),ndimage.sobel(tr.mean(2),1));mask=((grad>15)|(tr.max(2)-tr.min(2)>20))&(tr.mean(2)<242);yy,xx=np.where(mask);sel=np.linspace(0,len(xx)-1,min(3500,len(xx))).astype(int);xx=xx[sel];yy=yy[sel];u=(xx+.5)/tr.shape[1]-.5;v=(yy+.5)/tr.shape[0]-.5;wanted=tr[yy,xx]/255;gx=np.stack([ndimage.sobel(src[:,:,c],axis=1)/8 for c in range(3)],2)/255;gy=np.stack([ndimage.sobel(src[:,:,c],axis=0)/8 for c in range(3)],2)/255;src=src/255
q=r[target]['matches'][row];ratio=r[target]['scale']/ss;left=q['x']+(box[0]-qq['x'])*ratio;top=q['y']+(box[1]-qq['y'])*ratio;ini=np.array([left+W*ratio/2,top+H*ratio/2,W*ratio,0,0,H*ratio]);
def at(img,x,y):return np.stack([ndimage.map_coordinates(img[:,:,c],[y/2,x/2],order=1,mode='nearest') for c in range(3)],1)
def residual(z):
 x=z[0]+z[2]*u+z[4]*v;y=z[1]+z[3]*u+z[5]*v;return (at(src,x,y)-wanted).ravel()
def jac(z):
 x=z[0]+z[2]*u+z[4]*v;y=z[1]+z[3]*u+z[5]*v;dx=at(gx,x,y)/2;dy=at(gy,x,y)/2;return np.stack([dx,dy,dx*u[:,None],dy*u[:,None],dx*v[:,None],dy*v[:,None]],2).reshape(-1,6)
lo=ini+np.array([-25,-40,-W*.15,-W*.08,-H*.08,-H*.15]);hi=ini+np.array([25,40,W*.15,W*.08,H*.08,H*.15]);fit=optimize.least_squares(residual,ini,jac=jac,bounds=(lo,hi),loss='soft_l1',f_scale=.08,max_nfev=60,xtol=1e-5,ftol=1e-5,gtol=1e-5);z=fit.x;A=np.array([[z[2]/W,z[4]/H],[z[3]/W,z[5]/H]]);U,D,V=np.linalg.svd(A)
if np.linalg.det(U)<0:U[:,1]*=-1;D[1]*=-1
if np.linalg.det(V)<0:V[1,:]*=-1;D[1]*=-1
angles=[float(np.degrees(np.arctan2(U[1,0],U[0,0]))),float(np.degrees(np.arctan2(V[1,0],V[0,0])))];result={'source_frame':ref,'target_frame':target,'row':row,'source_box':box,'image_size':[W,H],'initial':ini.tolist(),'fit':z.tolist(),'matrix':A.tolist(),'singular_values':D.tolist(),'rotations':angles,'cost_before':float(np.abs(residual(ini)).mean()*255),'cost_after':float(np.abs(residual(z)).mean()*255),'success':bool(fit.success),'evaluations':fit.nfev};(out/'fit.json').write_text(json.dumps(result,indent=2));print(result)
