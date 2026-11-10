"""Measured scene-state cuts and component travel from native flat-color masks."""
import copy,json
import numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at,track,amend,flat
FPS=30000/1001

def apply(scene,p):
    by={l['id']:l for l in scene['layers']};rows=json.loads((p/'measurements-v8/bubble-tracks.json').read_text())['measurements']
    def update(identifier,poses,start=None,end=None):
        l=by[identifier]
        for prop in ['x','y','scaleX','scaleY']:track(l,prop,poses)
        if start is not None:l['start']=start
        if end is not None:l['end']=end
    sarah=[];locked=[];mood=[];menu=[];selected=[]
    for r in rows:
        n=r['frame']
        for c in r['gray']:
            b=c['bbox'];w,h=c['width'],c['height']
            if 142<=n<=149 and w>1100:
                s=w/1188;sarah.append(dict(time=r['time'],x=b[0],y=b[1],scaleX=s,scaleY=s))
            if 264<=n<=320 and 500<w<550 and h>50:
                s=w/528;y=b[1] if b[1]>0 else b[3]-175*s;locked.append(dict(time=r['time'],x=b[0],y=y,scaleX=s,scaleY=s))
            if 264<=n<=360 and 600<w<950 and h<260 and b[0]<300:
                s=w/918;y=b[1] if b[1]>0 else b[3]-215*s;mood.append(dict(time=r['time'],x=b[0],y=y,scaleX=s,scaleY=s))
            if 295<=n<=360 and 590<w<800 and h>350:
                s=w/606;menu.append(dict(time=r['time'],x=b[0],y=b[1],scaleX=s,scaleY=s))
        if 361<=n<=379:
            matches=[c for c in r['selected']if c['width']>900 and c['height']>150]
            if matches:
                c=max(matches,key=lambda c:c['area']);b=c['bbox'];s=c['width']/958
                if n<=362:s=1.09 # right side clipped by the stage
                selected.append(dict(time=r['time'],x=b[0],y=b[1],scaleX=s,scaleY=s))
    update('p0066',sarah,142/FPS);by['p0066']['keyframes']['opacity']=[dict(t=142/FPS,value=1),dict(t=7.1,value=1),dict(t=7.75,value=0,ease='easeInOut')]
    by['p0066']['keyframes']['blur']=[dict(t=142/FPS,value=9),dict(t=146/FPS,value=3),dict(t=150/FPS,value=0)]
    # Display glyphs follow the measured native appearance in these text bubbles.
    by['p0066']['children'][2]['fontFamily']='SF Pro Display'
    update('p0113',locked,locked[0]['time']);update('p0117',mood,mood[0]['time'],361/FPS)
    by['p0113']['children'][1]['end']=281/FPS
    for name in ['p0113','p0117']:
        by[name]['children'][2]['fontFamily']='SF Pro Display'
    update('p0132',menu,menu[0]['time'],361/FPS)
    update('p0135',selected,361/FPS)
    # Selected option body is native Messages lavender gray, not incoming gray.
    for c in by['p0135']['children'][:2]:c['fill']='#e4e4e7'
    choice=[]
    for r in selected:
        ratio=r['scaleX']/(970/958)
        choice.append(dict(time=r['time'],x=177*ratio,y=58+(r['y']-201),scaleX=ratio,scaleY=ratio))
    update('p0142',choice,361/FPS)
    # Found/check/result controls remain compact during the physical pullback.
    late=[r for r in rows if 695<=r['frame']<=734]
    found=[];result=[]
    for r in late:
        n=r['frame']
        matches=[c for c in r['gray']if c['width']>400 and 40<c['height']<180 and c['bbox'][1]>200]
        if matches and n<=729:
            c=max(matches,key=lambda c:c['area']);b=c['bbox'];s=c['width']/945
            found.append(dict(time=r['time'],x=b[0],y=b[1],scaleX=s,scaleY=s))
        matches=[c for c in r['selected']if 300<c['width']<450 and 60<c['height']<130 and c['bbox'][1]>400]
        if matches:
            c=max(matches,key=lambda c:c['area']);b=c['bbox'];s=c['width']/768
            result.append(dict(time=r['time'],x=b[0],y=b[1],scaleX=s,scaleY=s))
    # Underlying conversation already changes while the restaurant sheet dismisses.
    dismiss=[]
    for n in range(664,670):
        a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB')).astype(float)
        border=float(np.median(a[:,:20]));target=236*border/255
        mask=(np.abs(a-target).max(2)<4);mask[650:]=False
        labels,_=ndimage.label(mask);matches=[]
        for i,sl in enumerate(ndimage.find_objects(labels),1):
            if sl is None:continue
            yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
            if 850<w<1050 and 90<h<220:matches.append((w*h,[xx.start,yy.start,xx.stop,yy.stop]))
        if matches:
            b=max(matches)[1];sc=(b[2]-b[0])/945;dismiss.append(dict(time=n/FPS,x=b[0],y=b[1],scaleX=sc,scaleY=sc))
    if dismiss:
        found=dismiss+found
        by['p0230']['keyframes']['opacity']=[dict(t=18.25,value=1),dict(t=19.25,value=1),dict(t=19.3,value=0),dict(t=663/FPS,value=0),dict(t=664/FPS,value=1,ease='hold'),dict(t=24.5,value=1)]
        by['p0259']['start']=664/FPS
        check=[dict(time=r['time'],x=r['x']+27,y=r['y']+198,scaleX=r['scaleX'],scaleY=r['scaleY'])for r in dismiss]
        if check:update('p0259',check)
    update('p0230',found)
    if result:update('p0262',result)
    # Before focus settles, keep composer/keyboard in the measured compact
    # physical frame rather than interpolating them from the earlier full screen.
    components=json.loads((p/'measurements-v8/component-tracks.json').read_text())['measurements']
    compact=[r for r in components if 708<=r['frame']<750 and r.get('physical_device_bbox')and r['physical_device_bbox'][1]>0]
    for identifier,bx,byy,scale in [('p0372',439,875,.52),('p0427',423,960,.514)]:
        poses=[]
        for r in compact:
            b=r['physical_device_bbox'];poses.append(dict(time=r['time'],x=bx+b[0]-406,y=byy+b[1]-71,scaleX=scale,scaleY=scale))
        if poses:
            update(identifier,poses,start=708/FPS)
            by[identifier]['keyframes']['opacity']=[dict(t=708/FPS,value=1),dict(t=29.2,value=1),dict(t=29.6,value=0,ease='easeInOut')]
    by['p0292']['keyframes']['opacity']=[dict(t=708/FPS,value=1)]
    # First native focused phone frame710 is deliberately defocused. Source24s
    # focus sharpens gradually; geometry is measured separately from this blur.
    for name in ['p0292','p0298','p0230','p0259','p0262','p0372','p0427']:
        l=by[name];l.setdefault('keyframes',{})['blur']=[dict(t=705/FPS,value=8),dict(t=710/FPS,value=8),dict(t=719/FPS,value=2),dict(t=728/FPS,value=0)]
    # Check label follows the found bubble with its own measured source spacing.
    poses=[]
    for r in found:
        if r['time']<708/FPS:continue
        poses.append(dict(time=r['time'],x=r['x']+7,y=r['y']+96*(r['scaleX']/.492),scaleX=r['scaleX'],scaleY=r['scaleY']))
    if poses:update('p0259',poses)
    # The first audio frame is already visible, partly covered by the frosted
    # composer; color-component detection excluded this occluded silhouette.
    audio=by['p0310'];audio['start']=800/FPS
    for prop,value in [('x',578),('y',546),('scaleX',1),('scaleY',1)]:
        amend(audio,prop,[dict(t=800/FPS,value=value)],800/FPS,800/FPS)
    audio['keyframes']['opacity']=[dict(t=800/FPS,value=1),dict(t=29.2,value=1),dict(t=29.6,value=0,ease='easeInOut')]
    # Restore the verified late840 anchor for every amended property. Without
    # this, the final measurement829 would be held over a passing static pose.
    base=json.loads((p/'scene-v7-fonts.json').read_text());original={l['id']:l for l in base['layers']}
    for name in ['p0300','p0307','p0310','p0372','p0427','native28-hardware']:
        for prop in ['x','y','scaleX','scaleY']:
            if prop not in by[name].get('keyframes',{}):continue
            value=at(original[name],prop,840/FPS);amend(by[name],prop,[dict(t=840/FPS,value=value,ease='linear')],840/FPS,840/FPS)
    return scene
