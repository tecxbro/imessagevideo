from PIL import Image
import numpy as np, math

G = Image.open("fit/g.png").convert("RGBA")
def comp(sx,sy,Y,X=60,ox=125.5,oy=61):
    M=np.array([[sx,0,X+ox-sx*ox],[0,sy,Y+oy-sy*oy],[0,0,1.]])
    im=G
    x1,y1=im.width,im.height
    p=M@np.array([[0,x1,x1,0],[0,0,y1,y1],[1,1,1,1]])
    bx0,by0,bx1,by1=math.floor(p[0].min()),math.floor(p[1].min()),math.ceil(p[0].max()),math.ceil(p[1].max())
    left,top,right,bottom=max(0,round(bx0)),max(0,round(by0)),min(960,round(bx1)),min(720,round(by1))
    d2u=np.array([[1,0,left],[0,1,top],[0,0,1.]])
    inv=d2u*1.0
    inv=units=np.linalg.inv(M)@d2u
    piece=im.transform((right-left,bottom-top),Image.Transform.AFFINE,tuple(inv[:2].ravel()),resample=Image.Resampling.BICUBIC)
    cv=Image.new("RGBA",(960,720),(253,253,253,255))
    cv.alpha_composite(piece,(left,top))
    return np.asarray(cv.convert("RGB"))

src=np.array(Image.open("all/135.png").convert("RGB")).astype(int)  # f149 settled
mine=comp(1,1,360).astype(int)
for reg,name in [((20,340,370,180),"patch"),((55,355,270,70),"bubble"),((120,370,130,32),"text")]:
    x,y,w,h=reg
    d=np.abs(mine[y:y+h,x:x+w]-src[y:y+h,x:x+w])
    print(name,"MAE",round(float(d.mean()),3),"max",int(d.max()))
# where are diffs on bubble
d=np.abs(mine[355:425,55:325]-src[355:425,55:325]).max(axis=2)
ys,xs=np.where(d>40)
print("bubble diff>40:",len(ys), "at", list(zip(xs[:10],ys[:10])) if len(ys)<20 else "...")
# ink-only mae
dk=np.all(src[355:425,55:325]<150,axis=2)|np.all(mine[355:425,55:325]<150,axis=2)
print("ink MAE:",round(float(np.abs(mine[355:425,55:325]-src[355:425,55:325])[dk].mean()),2))
# save visual
Image.fromarray(np.concatenate([mine[350:430,50:330],src[350:430,50:330]],axis=0).astype('uint8')).save("fit/sbs.png")
