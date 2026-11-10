"""Verified hardware bitmap mask and independent source120 UI corrections."""
import json,copy
import numpy as np
from PIL import Image,ImageDraw
from v8_utils import at,track,flat
from scipy import ndimage
FPS=30000/1001

def apply(scene,p):
    by={l['id']:l for l in scene['layers']};raw=json.loads((p/'measurements-v8/intro-ui-fit.json').read_text())['measurements']
    # Repair only the diagnosed native label/ROI ambiguity at37..42.
    for r in raw:
        n=r['frame']
        if n not in range(37,43):continue
        a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB'))
        lo=650 if n<40 else 900
        roi=a[lo:1080,:1000];mask=(roi.max(2)-roi.min(2)<10)&(roi.min(2)>150)&(roi.max(2)<235)
        linked=ndimage.binary_dilation(mask,structure=np.ones((1,35),bool));labels,_=ndimage.label(linked);choices=[]
        for i,sl in enumerate(ndimage.find_objects(labels),1):
            if sl is None:continue
            yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
            if ((n<40 and w>300 and 100<xx.start<500)or(n>=40 and w>150 and xx.start<200))and h>15:
                actual=mask&(labels==i);ys,xs=np.where(actual)
                choices.append([int(xs.min()),int(ys.min()+lo),int(xs.max()+1),int(ys.max()+1+lo)])
        if choices:
            b=min(choices,key=lambda b:b[1]);r['name_ink_bbox']=b;r['ui_scale_ratio']=(b[3]-b[1])/30 if n<40 else 73/30
    # Faint Poke caption was mistaken for contact text at40. Require contact ink
    # to begin on the left; freeze minimum label height through clipped first row.
    rows=[]
    for r in raw:
        b=r.get('name_ink_bbox')
        if not b or (r['frame']<109 and b[0]>500):continue
        rows.append(r)
    ui=by['v8-inbox-rows'];ui['keyframes']={}
    for prop in ['x','y','scaleX','scaleY','opacity']:
        poses=[]
        for r in rows:
            b=r['name_ink_bbox'];scale=(b[2]-b[0])/253 if r['frame']>=109 else r['ui_scale_ratio'];poses.append(dict(time=r['time'],x=b[0]-455*scale,y=b[1]-688*scale,scaleX=scale,scaleY=scale,opacity=r['ui_opacity']))
        track(ui,prop,poses)
    name=next(l for l in ui['children']if l['id']=='v8-Nikki')
    name.update(x=451.9146341463415,y=678.6896551724138,scaleX=253/246,scaleY=30/29)
    ui['children'].extend([dict(id='v8-Angie',type='text',text='Angie',x=451,y=1078,fontFamily='SF Pro Display',fontSize=40,fontWeight=600,fill='#000000'),dict(id='v8-AngieTime',type='text',text='12:03 AM',x=914,y=1080,fontFamily='SF Pro Display',fontSize=34,fill='#858585')])
    # Genuine photographed hardware only. Screen interior is transparent, so all
    # inbox type, Memoji, layout and controls remain separate editable elements.
    source=Image.open(p/'measurements-v8/decoded/000120.png').convert('RGBA');mask=Image.new('L',source.size,255);draw=ImageDraw.Draw(mask);draw.rounded_rectangle((285,123,1153,2200),radius=132,fill=0)
    # Interior rectangle drawn beyond source bottom avoids a false bottom curve.
    source.putalpha(mask);source.crop((243,88,1197,1080)).save(p/'assets/intro-hardware-native4.png')
    source=Image.open(p/'measurements-v8/decoded/000120.png').convert('RGBA');source.crop((585,153,856,233)).save(p/'assets/intro-island-native4.png')
    phone=next(l for l in scene['layers']if l['id']=='v8-v8-intro-physical')
    physical=[]
    for r in raw:
        b=r.get('physical_bbox');island=r.get('island_bbox')
        if not b:continue
        s=(b[2]-b[0])/974;y=b[1]-10*s if b[1]>0 else island[3]-150*s if island else 0
        physical.append(dict(time=r['time'],x=b[0]-13*s,y=y,scaleX=s,scaleY=s))
    ref=next(r for r in physical if abs(r['time']-120/FPS)<1e-5)
    poses=[]
    for r in physical:
        scale=r['scaleX']/ref['scaleX'];poses.append(dict(time=r['time'],x=r['x']-ref['x']*scale,y=r['y']-ref['y']*scale,scaleX=scale,scaleY=scale))
    phone['keyframes']={}
    for prop in ['x','y','scaleX','scaleY']:track(phone,prop,poses)
    phone['children']=[dict(id='v8-intro-screen',type='rect',x=257,y=101,width=923,height=2100,radius=145,fill='#ffffff'),
        dict(id='v8-native-intro-ring',type='image',src='assets/intro-hardware-native4.png',x=243,y=88,width=954,height=992),
        dict(id='v8-native-intro-island',type='image',src='assets/intro-island-native4.png',x=585,y=153,width=271,height=80),
        dict(id='v8-intro-clock',type='text',text='9:41',x=415,y=182,fontFamily='SF Pro Display',fontSize=38,fontWeight=600,fill='#000000'),
        *[dict(id='v8-statusbar'+str(i),type='rect',x=906+11*i,y=206-6*i,width=8,height=12+6*i,radius=2.5,fill='#000000')for i in range(4)],
        dict(id='v8-wifi1',type='path',d='M964 201 Q980 187 996 201',fill='none',stroke='#000000',strokeWidth=5),
        dict(id='v8-wifi2',type='path',d='M970 209 Q980 200 990 209',fill='none',stroke='#000000',strokeWidth=5),
        dict(id='v8-wifi3',type='path',d='M977 215 L980 218 L983 215 Z',fill='#000000'),
        dict(id='v8-battery-outline',type='rect',x=1015,y=192,width=50,height=26,radius=6,fill='none',stroke='#999999',strokeWidth=2),
        dict(id='v8-battery-inner',type='rect',x=1019,y=196,width=42,height=18,radius=3,fill='#000000'),
        dict(id='v8-battery-cap',type='rect',x=1067,y=199,width=3,height=11,radius=2,fill='#999999')]
    # Correct chromatic-shadow bias in held circular portraits, bounded to113+.
    for identifier,dx,dy,factor in [('p0007',-1,-5,.95),('p0010',-7.5,-3,.96)]:
        l=by[identifier]
        for prop in ['x','y','scaleX','scaleY']:
            for k in l['keyframes'][prop]:
                weight=max(0,min(1,(k['t']*FPS-109)/11))
                if prop=='x':k['value']+=dx*weight
                elif prop=='y':k['value']+=dy if k['t']*FPS>=108.999 else 0
                else:k['value']*=(.97 if identifier=='p0007'else .975)+(factor-(.97 if identifier=='p0007'else .975))*weight
    # Caption + unread blue dot are editable components, measured at120.
    logo=by['p0014'];poses=[];badge=[];dots=[]
    times=[k['t']for k in logo['keyframes']['x']]
    for t in times:
        s=at(logo,'scaleX',t)/.3987341772151899;x=at(logo,'x',t);y=at(logo,'y',t)
        poses.append(dict(time=t,x=x,y=y+(584-485.1012658227848)*s,fontSize=32*s))
        badge.append(dict(time=t,x=x+(760-720.5)*s,y=y+(590-485.1012658227848)*s,scaleX=.44*s,scaleY=.44*s))
        dots.append(dict(time=t,x=x+(653-720.5)*s,y=y+(594-485.1012658227848)*s,scaleX=s,scaleY=s))
    for prop in ['x','y','fontSize']:track(by['p0015'],prop,poses)
    for prop in ['x','y','scaleX','scaleY']:track(by['p0016'],prop,badge)
    dot=dict(id='v8-poke-unread',type='circle',start=109/FPS,end=142/FPS,width=19,height=19,fill='#009df0')
    for prop in ['x','y','scaleX','scaleY']:track(dot,prop,dots)
    scene['layers'].append(dot)
    # The frosted preview background springs independently from its typing text.
    popup=by['p0058'];body=dict(id='v8-preview-material',type='group',start=109/FPS,end=142/FPS,originX=153.5,originY=56,children=popup['children'][:2])
    popup['children']=popup['children'][2:]
    poses=[dict(time=n/FPS,x=x,y=y,scaleX=sc,scaleY=sc,rotation=rotation)for n,x,y,sc,rotation in[(109,610,350,.92,-7),(113,568,366,1,-2.5),(120,568,370,1,0),(125,568,370,1,0),(131,580,380,.92,0),(141,605,392,.82,0)]]
    for prop in ['x','y','scaleX','scaleY','rotation']:track(body,prop,poses)
    scene['layers'].insert(scene['layers'].index(popup),body)
    (p/'assets/intro-hardware-v8-provenance.json').write_text(json.dumps({'source_frame':120,'assets':[{'asset':'assets/intro-hardware-native4.png','crop':[243,88,1197,1080],'screen_interior':'transparent measured rounded screen opening; authentic bezel/buttons only'},{'asset':'assets/intro-island-native4.png','crop':[585,153,856,233],'purpose':'authentic optical island camera hardware only'}]},indent=2))
    return scene
