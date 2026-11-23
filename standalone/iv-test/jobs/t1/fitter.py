from PIL import Image
import numpy as np, json, math

G = Image.open("fit/g.png").convert("RGBA")
PX,PY,PW,PH = 20,340,370,180

def composite_patch(sx, sy, Y, X=60, ox=125.5, oy=61):
    M = np.array([[sx,0,X+ox-sx*ox],[0,sy,Y+oy-sy*oy],[0,0,1.]])
    im,x0,y0 = G,0,0
    x1=x0+im.width; y1=y0+im.height
    p=M@np.array([[x0,x1,x1,x0],[y0,y0,y1,y1],[1,1,1,1]])
    bx0,by0,bx1,by1 = math.floor(p[0].min()),math.floor(p[1].min()),math.ceil(p[0].max()),math.ceil(p[1].max())
    left=max(0,round(bx0)); top=max(0,round(by0)); right=min(960,round(bx1)); bottom=min(720,round(by1))
    dest_to_units=np.array([[1,0,left],[0,1,top],[0,0,1.]])
    units_to_src=np.array([[1,0,-x0],[0,1,-y0],[0,0,1.]])
    inv=units_to_src@np.linalg.inv(M)@dest_to_units
    piece=im.transform((right-left,bottom-top),Image.Transform.AFFINE,tuple(inv[:2].ravel()),resample=Image.Resampling.BICUBIC)
    canvas=Image.new("RGBA",(960,720),(253,253,253,255))
    canvas.alpha_composite(piece,(left,top))
    return np.asarray(canvas.convert("RGB"))[PY:PY+PH,PX:PX+PW]

def fit_frame(patch, guess):
    best=None
    for dsy in np.arange(-0.018,0.019,0.006):
        for dsx in np.arange(-0.024,0.025,0.008):
            for dY in np.arange(-1.2,1.21,0.6):
                mae=float(np.abs(composite_patch(guess[0]+dsx,guess[1]+dsy,guess[2]+dY).astype(int)-patch).mean())
                if best is None or mae<best[0]: best=(mae,guess[0]+dsx,guess[1]+dsy,guess[2]+dY)
    m0,sx0,sy0,Y0=best
    for dsy in np.arange(-0.006,0.0061,0.002):
        for dsx in np.arange(-0.008,0.0081,0.002):
            for dY in np.arange(-0.6,0.61,0.2):
                mae=float(np.abs(composite_patch(sx0+dsx,sy0+dsy,Y0+dY).astype(int)-patch).mean())
                if mae<best[0]: best=(mae,sx0+dsx,sy0+dsy,Y0+dY)
    return best

track=json.load(open("doors_track.json"))
out={}
import time,sys
t0=time.time()
for r in track:
    if r.get('present') is False: continue
    f=r['f']
    if f>99: break
    im=np.array(Image.open(f"all/{f-14:03d}.png").convert("RGB"))
    patch=im[PY:PY+PH,PX:PX+PW].astype(int)
    guess=(r['w']/251, r['h']/61, r['y1']-61)
    b=fit_frame(patch,guess)
    out[f]=dict(mae=round(b[0],3),sx=round(b[1],4),sy=round(b[2],4),Y=round(b[3],2))
    print(f"f{f:3d} mae={b[0]:.2f} sx={b[1]:.4f} sy={b[2]:.4f} Y={b[3]:.2f}",flush=True)
json.dump(out,open("fit/params.json","w"),indent=0)
print("elapsed",round(time.time()-t0,1))
