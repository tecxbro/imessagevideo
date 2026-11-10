"""Static genuine Memoji assets with independently measured circle cameras."""
import copy,json,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
from v8_utils import at,track

def body(a,x0,x1):
    mask=(a.max(2)-a.min(2)>10)&(a.min(2)<245);mask[:200]=False;mask[:, :x0]=False;mask[:, x1:]=False;labels,_=ndimage.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0
    if sizes.max()<5000:return None
    ys,xs=np.where(labels==sizes.argmax())
    return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]


def apply(scene,p):
    by={l['id']:l for l in scene['layers']};fps=scene['fps'];records=[];provenance=[]
    for name,id,bounds,crop in [('braden','p0007',(0,550),(154,312,446,604)),('sydney','p0010',(880,1440),(1000,308,1296,604))]:
        # Late held pose uses a genuine isolated Memoji from its own phase,
        # rather than an early facial expression stretched into the phone view.
        ref=Image.open(p/'measurements-v8/decoded/000109.png').convert('RGBA');art=ref.crop(crop);alpha=Image.new('L',art.size,0);draw=ImageDraw.Draw(alpha);draw.ellipse((1,1,art.width-2,art.height-2),fill=255);art.putalpha(alpha);path=p/f'assets/{name}-native109-v11.png';art.save(path);provenance.append(dict(asset='assets/'+path.name,source_frame=109,crop=list(crop),purpose='Genuine isolated circular Memoji only; no UI/chrome/text. Static late-phase expression.'))
        original=by[id];late=copy.deepcopy(original);original['end']=109/fps;late['start']=109/fps
        def rename(node):
            node['id']='v11-late-'+node['id']
            for c in node.get('children',[]):rename(c)
        rename(late);late['children'][0]['src']='assets/'+path.name;scene['layers'].insert(scene['layers'].index(original)+1,late)
        for group,frames in[(original,list(range(3 if name=='braden'else 8,31))+list(range(98,109))),(late,range(109,142))]:
            image=group['children'][0];asset=np.array(Image.open(p/image['src']).convert('RGBA'));amask=(asset[:,:,:3].max(2)-asset[:,:,:3].min(2)>10)&(asset[:,:,:3].min(2)<245)&(asset[:,:,3]>100);ys,xs=np.where(amask);ab=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];poses=[]
            for n in frames:
                a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(int);b=body(a,*bounds)
                if b is None:continue
                # Late right/left stage clipping is absent in this bounded set.
                if b[0]==0 or b[2]==1440:
                    width=b[3]-b[1]
                    if b[0]==0:b[0]=b[2]-width
                    else:b[2]=b[0]+width
                width=b[2]-b[0];worldwidth=width/(ab[2]-ab[0])*asset.shape[1];worldheight=worldwidth*asset.shape[0]/asset.shape[1];t=n/fps;gx,gy,sx,sy=[at(group,k,t)for k in['x','y','scaleX','scaleY']]
                poses.append(dict(time=t,x=(b[0]-gx)/sx-ab[0]/asset.shape[1]*worldwidth/sx,y=(b[1]-gy)/sy-ab[1]/asset.shape[0]*worldheight/sy,width=worldwidth/sx,height=worldheight/sy));records.append(dict(frame=n,role=name,source_body_bbox=b,asset=image['src']))
            for prop in['x','y','width','height']:track(image,prop,poses)
    (p/'assets/favorites-v11-provenance.json').write_text(json.dumps(provenance,indent=2));(p/'measurements-v8/favorites-v11.json').write_text(json.dumps(dict(method='Largest genuine chromatic circle per bounded side region; diameter from complete horizontal span. Per-image native geometry preserves independent caption camera.3–30and109–141only; no low-opacity circle inference.',measurements=records),indent=2))
