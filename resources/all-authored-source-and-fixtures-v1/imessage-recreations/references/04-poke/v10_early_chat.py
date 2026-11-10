"""Native transition measurements with UI controls excluded from hardware probes."""
import json,numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at,track,amend

def parts(mask):
    labels,_=ndimage.label(mask);out=[]
    for i,sl in enumerate(ndimage.find_objects(labels),1):
        if sl is None:continue
        yy,xx=sl;out.append(dict(bbox=[xx.start,yy.start,xx.stop,yy.stop],width=xx.stop-xx.start,height=yy.stop-yy.start,area=int((labels[sl]==i).sum())))
    return out

def apply(scene,p):
    by={l['id']:l for l in scene['layers']};fps=scene['fps'];measurements=[];selected=[];choice=[]
    refcandidate=np.array(Image.open(p/'measurements-v8/v9-candidate-000371.png').convert('RGB')).astype(int)
    def circle(a):
        mask=(a.min(2)>120)&(a.max(2)<200)&(a.max(2)-a.min(2)<15);mask[:,400:]=False;mask[:,:100]=False;mask[300:]=False;mask=ndimage.binary_closing(mask,structure=np.ones((3,3)))
        c=[v for v in parts(mask)if 75<v['width']<160 and 30<v['height']<100]
        return max(c,key=lambda v:v['area'])if c else None
    refcircle=circle(refcandidate);g=by['p0142'];rtime=371/fps;oldstate={k:at(g,k,rtime)for k in['x','y','scaleX','scaleY']};b=refcircle['bbox'];local=dict(left=(b[0]-oldstate['x'])/oldstate['scaleX'],top=(b[1]-oldstate['y'])/oldstate['scaleY'],width=refcircle['width']/oldstate['scaleX'],height=refcircle['height']/oldstate['scaleY'])
    for n in range(361,450):
        a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(int);row=dict(frame=n,time=n/fps)
        if n>=380:
            c=[v for v in parts(np.abs(a-[230,230,230]).max(2)<4)if v['width']>800 and 120<v['height']<300]
            if c:
                v=max(c,key=lambda v:v['area']);b=v['bbox'];scale=v['width']/958;selected.append(dict(frame=n,time=n/fps,x=b[0],y=b[1],scaleX=scale,scaleY=scale));row['selected_bbox']=b
        v=circle(a)
        if v:
            b=v['bbox'];sx=v['width']/local['width'];sy=v['height']/local['height'];top=b[1]
            if top<=2:
                sy=sx;top=b[3]-local['height']*sy
            choice.append(dict(frame=n,time=n/fps,x=b[0]-local['left']*sx,y=top-local['top']*sy,scaleX=sx,scaleY=sy));row['choice_bbox']=b
        measurements.append(row)
    for group,rows in[(by['p0135'],selected),(by['p0142'],choice)]:
        for prop in['x','y','scaleX','scaleY']:track(group,prop,rows)
    by['p0142']['end']=(choice[-1]['frame']+2)/fps
    # Preserve the reference caption's actual ink after adjusting its capsule.
    source=np.array(Image.open(p/'measurements-v8/decoded/000371.png').convert('RGB')).astype(int)
    def labelbox(a):
        c=a[65:140,300:650];mask=(c.min(2)>90)&(c.max(2)<200)&(c.max(2)-c.min(2)<15);yy,xx=np.where(mask)
        return [xx.min()+300,yy.min()+65,xx.max()+301,yy.max()+66]
    target=labelbox(source);oldbox=labelbox(refcandidate);node=next(l for l in by['p0142']['children']if l['type']=='text');newstate={k:at(by['p0142'],k,rtime)for k in oldstate};transformed=[newstate['x']+(oldbox[0]-oldstate['x'])*newstate['scaleX']/oldstate['scaleX'],newstate['y']+(oldbox[1]-oldstate['y'])*newstate['scaleY']/oldstate['scaleY'],newstate['x']+(oldbox[2]-oldstate['x'])*newstate['scaleX']/oldstate['scaleX'],newstate['y']+(oldbox[3]-oldstate['y'])*newstate['scaleY']/oldstate['scaleY']];sx=(target[2]-target[0])/(transformed[2]-transformed[0]);sy=(target[3]-target[1])/(transformed[3]-transformed[1]);nx=newstate['x']+node['x']*newstate['scaleX'];ny=newstate['y']+node['y']*newstate['scaleY'];node['x']=(target[0]-(transformed[0]-nx)*sx-newstate['x'])/newstate['scaleX'];node['y']=(target[1]-(transformed[1]-ny)*sy-newstate['y'])/newstate['scaleY'];node['scaleX']=sx;node['scaleY']=sy
    # Incoming Where is absent through413. Before-first-keyframe hold must not
    # make its414measured pose visible before that actual entry.
    by['p0155']['start']=414/fps
    spot=by['p0146'];tail=spot['children'][1];tail.pop('end',None);tail['originY']=140
    ui=json.loads((p/'measurements-v8/ui-camera-tracks.json').read_text())['measurements'];reference=next(r for r in ui if r['frame']==450);refbox=next(b for b in reference['chat_bubbles']if b[2]-b[0]>700);refscale=(refbox[2]-refbox[0])/707;thumb=[];tailposes=[]
    for r in ui:
        if not 407<=r['frame']<=449:continue
        c=[b for b in r.get('chat_bubbles',[])if 690<b[2]-b[0]<900]
        if not c:continue
        b=c[0];s=(b[2]-b[0])/707;ratio=s/refscale;thumb.append(dict(time=r['time'],x=b[0]+(858-refbox[0])*ratio,y=b[1]+(249-refbox[1])*ratio,scaleX=ratio,scaleY=ratio));tailposes.append(dict(time=r['time'],scaleY=float(np.clip(((b[3]-b[1])/s-140)/24,0,1.5))))
    for prop in['x','y','scaleX','scaleY']:track(by['p0151'],prop,thumb)
    track(tail,'scaleY',tailposes)
    # Source457–459plus cross lies on row500. Pick the OUTERMOST left run,
    # not the rightmost dark object in the first170pixels.
    rails=[]
    for n in range(453,463):
        a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB'));indices=np.where(a[500].max(1)<80)[0];runs=[]
        for x in indices:
            if runs and x==runs[-1][-1]+1:runs[-1].append(int(x))
            else:runs.append([int(x)])
        left=[v for v in runs if len(v)>4 and v[0]<60];right=[v for v in runs if len(v)>4 and v[0]>1270]
        if not right:continue
        hi=min(v[0]for v in right)
        if left:
            lo=min(left,key=lambda v:v[0])[-1]+1;scale=(hi-lo)/1272;x=lo-92*scale
        else:
            scale=(hi-719.5)/636;x=719.5-728*scale
        rails.append(dict(frame=n,time=n/fps,x=x,scaleX=scale))
    for prop in['x','scaleX']:track(by['p0109'],prop,rails)
    (p/'measurements-v8/early-chat-v10.json').write_text(json.dumps({'method':'Exact selected-card/capsule/source reaction anchor bounds;414Where visibility and tail fold. Source457–459hardware probe repairs plus-control contamination by outermost run selection.','measurements':measurements,'rails':rails},indent=2))
    return scene
