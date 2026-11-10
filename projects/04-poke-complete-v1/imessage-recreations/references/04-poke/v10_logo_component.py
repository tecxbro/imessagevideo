"""Two static genuine logo materials with separately editable native palm paths."""
from pathlib import Path
import copy,json,math
import numpy as np
from PIL import Image
from scipy import ndimage
from v10_shape_trace import vector_outline
FPS=30000/1001

def largest(mask):
    labels,n=ndimage.label(mask)
    if not n:return mask
    areas=np.bincount(labels.ravel());areas[0]=0
    return labels==int(areas.argmax())

def material(p,name):
    file=p/'assets'/('poke-'+name+'.png');a=np.array(Image.open(file).convert('RGBA'));rgb=a[:,:,:3].astype(float);h,w=rgb.shape[:2];yy,xx=np.mgrid[:h,:w]
    region=(xx>.12*w)&(xx<.9*w)&(yy>.12*h)&(yy<.9*h)&(a[:,:,3]>100)
    white=(rgb.min(2)>150)&(rgb.max(2)-rgb.min(2)<65)&region;symbol=largest(white);erase=ndimage.binary_dilation(symbol,iterations=4);valid=(~erase)&(a[:,:,3]>100);weight=ndimage.gaussian_filter(valid.astype(float),18)
    for ch in range(3):
        values=ndimage.gaussian_filter(rgb[:,:,ch]*valid,18)/np.maximum(.0001,weight);a[:,:,ch][erase]=np.clip(values[erase],0,255).astype(np.uint8)
    out=p/'assets'/('poke-'+name+'-material-v10.png');Image.fromarray(a).save(out)
    blue=(rgb[:,:,2]-rgb[:,:,0]>20)&(rgb[:,:,2]-rgb[:,:,1]>0)&(rgb[:,:,0]<150);yy,xx=np.where(blue);box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
    return 'assets/'+out.name,box,(w,h)

def apply(scene,p):
    by={l['id']:l for l in scene['layers']};circle=by['p0012'];square=by['p0014'];oldcircle=copy.deepcopy(circle);oldsquare=copy.deepcopy(square);materials={name:material(p,name)for name in['circle','square']};groups=[];records=[]
    for frame in range(64,81):
        a=np.array(Image.open(p/f'measurements-v8/decoded/{frame:06}.png').convert('RGB')).astype(float);blue=(a[:,:,2]-a[:,:,0]>20)&(a[:,:,2]-a[:,:,1]>0)&(a[:,:,0]<150);blue[:,:450]=False;blue[:,1000:]=False;blue[850:]=False;body=ndimage.binary_fill_holes(largest(blue));yy,xx=np.where(body);left,right,top,bottom=int(xx.min()),int(xx.max()+1),int(yy.min()),int(yy.max()+1);width=right-left;scale=width/476;cx=(left+right)/2;cy=(top+bottom)/2
        white=(a.min(2)>150)&(a.max(2)-a.min(2)<65)&body;white[:max(0,round(top+.1*(bottom-top)))]=False;white[round(top+.89*(bottom-top)):]=False;glyph=largest(white);paths=[vector_outline(glyph,(0,0,0,0),(cx,cy),scale)]
        # Source radius from four native top/bottom corner insets20localpx in.
        inset_y=20*scale;radii=[]
        for row in[round(top+inset_y),round(bottom-1-inset_y)]:
            xs=np.where(body[row,left:right])[0]
            if len(xs):
                for inset in[xs.min()/scale,(width-1-xs.max())/scale]:radii.append(inset+20+math.sqrt(max(0,40*inset)))
        radius=float(np.clip(np.median(radii),75,238));blend=float(np.clip((frame-72)/7,0,1));children=[dict(id='v10-logo-surface-'+str(frame),type='rect',x=-238,y=-238,width=476,height=476,radius=radius,fill='#244964',shadow=dict(x=0,y=14,blur=22,color='#d6dfe5'))]
        for name,opacity in[('circle',1),('square',blend)]:
            src,box,size=materials[name];factor=476/(box[2]-box[0]);children.append(dict(id=f'v10-logo-material-{frame}-{name}',type='image',src=src,x=-238-box[0]*factor,y=-238-box[1]*factor,width=size[0]*factor,height=size[1]*factor,opacity=opacity,clip=dict(x=-238,y=-238,width=476,height=476,radius=radius)))
        children.append(dict(id='v10-palm-'+str(frame),type='path',d=' '.join(paths),fill='#ffffff'))
        groups.append(dict(id='v10-logo-morph-'+str(frame),type='group',x=cx,y=cy,scaleX=scale,scaleY=scale,start=frame/FPS,end=(frame+1)/FPS,children=children))
        records.append(dict(frame=frame,body_bbox=[left,top,right,bottom],x=cx,y=cy,scale=scale,clip_radius=radius,static_material_blend=blend,glyph_paths=len(paths)))
    circle['end']=64/FPS;square['start']=81/FPS;index=scene['layers'].index(square);scene['layers'][index:index]=groups
    (p/'measurements-v8/logo-morph-v10.json').write_text(json.dumps({'method':'Native white-palm silhouettes traced as individually editable static SVG paths at originalframes64–80; two static genuine logo texture materials have only the old palm removed by normalized neighboring texture fill. Per-frame body/corner geometry is measured; no source frame or varying whole-logo bitmap is used.','measurements':records},indent=2))
    (p/'assets/logo-material-v10-provenance.json').write_text(json.dumps({'inputs':['assets/poke-circle.png','assets/poke-square.png'],'outputs':[m[0]for m in materials.values()],'modification':'White palm removed from static genuine logo backgrounds with normalized neighboring genuine texture; palm is rebuilt with editable native paths. Only two static material rasters, no logo video or source frame sequence.'},indent=2))
    return scene
