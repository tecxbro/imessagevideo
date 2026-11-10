"""Measured component cameras. UI, hardware, and keyboard are independent."""
import copy,json
import numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at,track,flat,amend
FPS=30000/1001

def largest(mask,predicate):
    labels,_=ndimage.label(mask);out=[]
    for i,sl in enumerate(ndimage.find_objects(labels),1):
        if sl is None:continue
        yy,xx=sl;v=dict(bbox=[xx.start,yy.start,xx.stop,yy.stop],width=xx.stop-xx.start,height=yy.stop-yy.start,area=int((labels[sl]==i).sum()))
        if predicate(v):out.append(v)
    return max(out,key=lambda v:v['area'])['bbox']if out else None

def apply(scene,p):
    by={l['id']:l for l in scene['layers']}
    ui=json.loads((p/'measurements-v8/ui-camera-tracks.json').read_text())['measurements']
    # Source800/801 gray audio edges connect to the keyboard mask; repair that
    # observed segmentation ambiguity using its held body and map pan reference.
    components=json.loads((p/'measurements-v8/component-tracks.json').read_text())['measurements']
    maps={r['frame']:r.get('map_footer_bbox')for r in components}
    for r in ui:
        if r['frame']in[800,801]:
            dx=maps[r['frame']][0]-maps[802][0]
            r['keyboard_bbox']=[258+dx,871,1367+dx,1080]
            r['composer_ink_bbox']=[497+dx,763,780+dx,808]
    early=[r for r in ui if r['frame']<552]
    # The same native keyboard controls are reused at both camera scales.
    kb=by['p0220'];kb['children']=copy.deepcopy(by['p0427']['children'])
    for l in flat(kb['children']):l['id']='early-v8-'+l['id']
    comp=by['p0165'];comp['children']=copy.deepcopy(by['p0372']['children'])
    for l in flat(comp['children']):l['id']='early-v8-'+l['id']
    # Composer measured ink at late840:406,763..690,808 and pose228,735,.84.
    def composer_rows(rows):
        out=[]
        for r in rows:
            b=r.get('composer_ink_bbox')
            if not b:continue
            w,h=b[2]-b[0],b[3]-b[1]
            if w<150 or h<25:continue
            if r['frame']>=800:
                sx=sy=.84;x=b[0]-178;y=735
            else:
                sx=.84*w/284;sy=.84*h/45;x=b[0]-178*w/284;y=b[1]-28*h/45
            out.append(dict(time=r['time'],x=x,y=y,scaleX=sx,scaleY=sy))
        return out
    for group,rows in [(comp,early),(by['p0372'],[r for r in ui if r['frame']>=750])]:
        poses=composer_rows(rows)
        for prop in ['x','y','scaleX','scaleY']:track(group,prop,poses)
    for group,rows in [(kb,early),(by['p0427'],[r for r in ui if r['frame']>=719])]:
        poses=[]
        for r in rows:
            b=r.get('keyboard_bbox')
            if not b:continue
            scale=(b[2]-b[0])/1258
            poses.append(dict(time=r['time'],x=b[0],y=b[1],scaleX=scale,scaleY=scale))
        for prop in ['x','y','scaleX','scaleY']:track(group,prop,poses)
    # Suggestion grows independently while the keyboard camera zooms.
    locrows=[r for r in early if r.get('location_header_ink_bbox')]
    if locrows:
        loc=dict(id='v8-currentlocation',type='group',start=locrows[0]['time'],end=17.7,children=[
            dict(id='v8-location-arrow',type='path',d='M0 22 L45 0 L31 45 L27 24 Z',fill='#000000'),
            dict(id='v8-location-text',type='text',x=65,y=-5,text='Current Location',fontSize=50,fontFamily='SF Pro Display',fontWeight=400,fill='#000000')])
        # A Display50 phrase has an ink span440×49 including the native arrow.
        poses=[]
        for r in locrows:
            b=r['location_header_ink_bbox'];poses.append(dict(time=r['time'],x=b[0],y=b[1],scaleX=(b[2]-b[0])/450,scaleY=(b[3]-b[1])/49))
        for prop in ['x','y','scaleX','scaleY']:track(loc,prop,poses)
        scene['layers'].append(loc)
        menu=dict(id='v8-keyboard-menu',type='group',start=locrows[0]['time'],end=17.7,children=[
            dict(id='v8-menu-A',type='text',x=18,y=0,text='A',fontSize=55,fontFamily='SF Pro Display',fill='#000000'),
            *[dict(id='v8-menu-dash'+str(i),type='rect',x=i*3,y=13+i*11,width=20-i*5,height=4,radius=2,fill='#000000')for i in range(3)]])
        poses=[]
        for r in locrows:
            b=r['keyboard_bbox'];s=(b[2]-b[0])/1258;h=r['location_header_ink_bbox'][3]-r['location_header_ink_bbox'][1];poses.append(dict(time=r['time'],x=b[0]+1155*s,y=r['location_header_ink_bbox'][1],scaleX=h/49,scaleY=h/49))
        for prop in ['x','y','scaleX','scaleY']:track(menu,prop,poses)
        scene['layers'].append(menu)
    # Incoming chat camera is inferred only from incoming bubble geometry.
    where=[];spot=[]
    for r in early:
        for b in r.get('chat_bubbles',[]):
            w,h=b[2]-b[0],b[3]-b[1]
            if r['frame']>=407 and 300<w<700 and h>80:
                where.append(dict(time=r['time'],frame=r['frame'],x=b[0],y=b[1],scaleX=w/533,scaleY=w/533))
            if r['frame']>=380 and 690<w<900 and h>80:
                spot.append(dict(time=r['time'],frame=r['frame'],x=b[0],y=b[1],scaleX=w/707,scaleY=w/707))
    for group,rows in [(by['p0155'],where),(by['p0146'],spot)]:
        for prop in ['x','y','scaleX','scaleY']:track(group,prop,rows)
        for l in group['children']:
            if l['type']=='text':l['fontFamily']='SF Pro Display'
    # Suppress the first bubble tail once another consecutive incoming bubble appears.
    by['p0146']['children'][1]['end']=407/FPS
    # Extend the chat camera to the thumb, option card and offscreen first bubble.
    refw=next(r for r in where if r['frame']==450);refs=next(r for r in spot if r['frame']==450)
    for identifier,rx,ry,rs in [('p0151',858,249,1),('p0135',360,-30,1),('p0146',refs['x'],refs['y'],refs['scaleX'])]:
        poses=[]
        for r in where:
            if r['frame']<450:continue
            ratio=r['scaleX']/refw['scaleX'];poses.append(dict(time=r['time'],x=r['x']+(rx-refw['x'])*ratio,y=r['y']+(ry-refw['y'])*ratio,scaleX=rs*ratio,scaleY=rs*ratio))
        if identifier=='p0146':poses=[r for r in poses if r['time']>spot[-1]['time']]
        if poses:
            for prop in ['x','y','scaleX','scaleY']:track(by[identifier],prop,poses)
    for l in by['p0135']['children'][:2]:l['fill']='#e4e4e7'
    # Separate late conversation components, measured against already-fitted840.
    components=json.loads((p/'measurements-v8/component-tracks.json').read_text())['measurements']
    late=[r for r in components if 695<=r['frame']<=829]
    source=np.array(Image.open(p/'native/28.0.png').convert('RGB')).astype(int)
    refmap=largest(np.abs(source-[227,227,224]).max(2)<5,lambda q:q['width']>200 and q['width']>q['height']*1.3)
    refdistance=largest(np.abs(source-[236,236,236]).max(2)<5,lambda q:q['width']>200 and q['width']>q['height']*2)
    am=(source[:,:,0]>120)&(source[:,:,0]<210)&(source[:,:,1]-source[:,:,0]>1)&(source[:,:,1]-source[:,:,0]<10)&(source[:,:,2]-source[:,:,0]>7)&(source[:,:,2]-source[:,:,0]<25)
    refaudio=largest(am,lambda q:q['width']>200 and 1.8<q['width']/q['height']<3.5)
    for identifier,field,reference,first in [('p0300','map_footer_bbox',refmap,734),('p0307','distance_bbox',refdistance,756),('p0310','audio_bbox',refaudio,799)]:
        group=by[identifier];gx,gy,gs=at(group,'x',840/FPS),at(group,'y',840/FPS),at(group,'scaleX',840/FPS);poses=[]
        for r in late:
            b=r.get(field)
            if not b or r['frame']<first:continue
            ratio=(b[2]-b[0])/(reference[2]-reference[0]);poses.append(dict(time=r['time'],x=b[0]+(gx-reference[0])*ratio,y=(b[3]+(gy-reference[3])*ratio if identifier=='p0300'else b[1]+(gy-reference[1])*ratio),scaleX=gs*ratio,scaleY=gs*ratio))
        if poses:
            for prop in ['x','y','scaleX','scaleY']:track(group,prop,poses)
            if identifier=='p0310':group['start']=poses[0]['time'];group['keyframes']['opacity']=[dict(t=poses[0]['time'],value=1),dict(t=29.2,value=1),dict(t=29.6,value=0,ease='easeInOut')]
    # Small-device hardware stays small through799; its late zoom is independent.
    poses=[]
    for r in late:
        b=r.get('physical_device_bbox')
        if not b or b[2]-b[0]<500:continue
        scale=(b[2]-b[0])/974
        if r['frame']>=800 and r['frame']<=809:
            scale=1170/974
            y=-1000
        elif b[1]<=0:continue
        else:y=b[1]-10*scale
        poses.append(dict(time=r['time'],x=b[0]-13*scale,y=y,scaleX=scale,scaleY=scale))
    for prop in ['x','y','scaleX','scaleY']:track(by['p0292'],prop,poses)
    # Compact header blue art uses a distinct UI transform.
    art=Image.open(p/'assets/poke-square.png').convert('RGB');z=np.array(art).astype(int);mask=(z[:,:,2]-z[:,:,0]>20)&(z[:,:,2]-z[:,:,1]>0)&(z[:,:,0]<150);yy,xx=np.where(mask);localleft=350+xx.min()*164/art.width;localtop=-6+yy.min()*164/art.height;localwidth=(xx.max()-xx.min()+1)*164/art.width
    poses=[]
    for r in late:
        b=r.get('header_blue_bbox')
        if not b or r['frame']<705:continue
        scale=(b[2]-b[0])/localwidth;poses.append(dict(time=r['time'],x=b[0]-localleft*scale,y=b[1]-localtop*scale,scaleX=scale,scaleY=scale))
    if poses:
        for prop in ['x','y','scaleX','scaleY']:track(by['p0298'],prop,poses)
        by['p0298']['end']=(max(r['frame']for r in late if r.get('header_blue_bbox'))+1)/FPS
        by['p0298']['keyframes']['opacity']=[dict(t=705/FPS,value=1)]
    # Scanline side rails after the zoom translate independently from audio.
    rails=[]
    for r in late:
        if r['frame']<800:continue
        a=np.array(Image.open(p/f"measurements-v8/decoded/{r['frame']:06}.png").convert('RGB'))
        mask=a[900].max(1)<80;indices=np.where(mask)[0];left=indices[indices<350]
        if len(left)>5:rails.append(dict(time=r['time'],x=float(left.max()+1-170)))
    if rails:track(by['native28-hardware'],'x',rails)
    by['native28-hardware']['start']=800/FPS
    by['p0292']['end']=800/FPS
    return scene
