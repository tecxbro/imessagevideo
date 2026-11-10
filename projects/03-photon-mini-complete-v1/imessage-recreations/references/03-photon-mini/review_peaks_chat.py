"""Bounded static UI actors and independently measured chat-card birth,800–812."""
from pathlib import Path
import json,copy,sys
import numpy as np
from PIL import Image
from scipy import ndimage,signal

R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent
sys.path.insert(0,str(R/'references/02-danieltian'))
from trace_glyphs import trace_alpha
P=R/'verification/fidelity-review/03-peaks';A=REF/'assets/peaks-review-chat';A.mkdir(exist_ok=True)
BASE=R/'outputs/03-photon-mini/final-v14';scene=json.load(open(BASE/'scene.json'))
old=next(n for n in scene['layers']if n['id']=='p03-371')
measurements=json.load(open(P/'chat-measurements-initial.json'))
images={f:Image.open(P/'source-804-full'/f'{f-797:04}.png').convert('RGB')for f in range(800,813)}
arrays={f:np.asarray(im).astype(float)for f,im in images.items()}

def crop_asset(name,frame,box):
    file=A/(name+'.png');images[frame].crop(box).save(file)
    return dict(name=name,frame=frame,box=list(box),src=str(file.resolve()),width=box[2]-box[0],height=box[3]-box[1])

def node(asset,x,y,scale=1,opacity=1,identifier=None):
    return dict(id=identifier or asset['name'],type='image',src=asset['src'],x=float(x),y=float(y),width=asset['width'],height=asset['height'],scaleX=float(scale),scaleY=float(scale),opacity=float(opacity))

# Static product UI internals. None includes physical hardware or a whole screen.
controls={
 'back':(718,74,787,143),'video':(1132,74,1202,143),
 'team-avatar':(919,75,1009,155),'group-title':(866,152,1053,196),
 'date':(903,201,1035,228),'island':(878,6,1042,58),
 'composer-plus':(718,946,785,1013),'composer-entry':(786,946,1202,1013),
}
assets={name:crop_asset('mini-review-chat-'+name,804,box)for name,box in controls.items()}
# Canonical cards are complete, opaque static product states, including native
# rounded corners/footer/tail. Sender and Agent labels remain separate actors.
assets['jump']=crop_asset('mini-review-jump-card',800,(752,223,1180,541))
assets['zoom']=crop_asset('mini-review-zoom-card',812,(802,570,1127,809))
assets['robot']=crop_asset('mini-review-sender-robot',800,(677,477,741,541))
assets['agent']=crop_asset('mini-review-agent-label',800,(775,190,838,218))
card_pixels=np.asarray(Image.open(assets['jump']['src'])).astype(float)
card_mask=ndimage.binary_fill_holes(np.max(np.abs(card_pixels-253),axis=2)>8).astype('uint8')
card_outline,card_outline_stats=trace_alpha(card_mask.astype(float))

def resize_float(asset,scale):
    w=max(1,round(asset['width']*scale));h=max(1,round(asset['height']*scale))
    return np.asarray(Image.open(asset['src']).resize((w,h),Image.Resampling.LANCZOS)).astype(float)

def fit(asset,frame,guess,scale_hint,radius=12,scale_radius=.045,steps=11):
    """Normalized dark/color correlation, avoiding small-template SSE bias."""
    source=arrays[frame];best=None
    for scale in np.linspace(scale_hint*(1-scale_radius),scale_hint*(1+scale_radius),steps):
        template=resize_float(asset,scale);h,w=template.shape[:2]
        gx,gy=guess;left=max(0,int(gx-radius));top=max(0,int(gy-radius));right=min(1920,int(gx+radius+w+1));bottom=min(1080,int(gy+radius+h+1))
        if bottom-top<h or right-left<w:continue
        target=np.maximum(0,253-source[top:bottom,left:right]);delta=np.maximum(0,253-template)
        corr=sum(signal.fftconvolve(target[:,:,c],delta[::-1,::-1,c],mode='valid')for c in range(3))
        energy=sum(signal.fftconvolve(target[:,:,c]**2,np.ones((h,w)),mode='valid')for c in range(3))
        d2=float((delta*delta).sum());ncc=corr/np.sqrt(np.maximum(1e-6,energy*d2))
        yy,xx=np.unravel_index(ncc.argmax(),ncc.shape);score=float(ncc[yy,xx]);opacity=float(np.clip(corr[yy,xx]/max(d2,1),0,1))
        row=dict(x=left+int(xx),y=top+int(yy),scale=float(scale),opacity=opacity,ncc=score)
        if best is None or score>best['ncc']:best=row
    return best

ref=next(row for row in measurements if row['frame']==804)['hardware']
actors=[];records=[];provenance=[]
for row in measurements:
    frame=row['frame'];camera=row['hardware'];start=frame/30;end=(frame+1)/30
    ratio=camera['scale']/ref['scale'];dx=camera['x']-ratio*ref['x'];dy=camera['y']-ratio*ref['y']
    # Source screen is slightly warm-gray late in this pullback; sample its
    # empty lower conversation, never the off-device stage.
    screen_color=int(np.median(arrays[frame][850:900,1050:1100]))
    screen_color=int(np.clip(screen_color,249,253));screen_fill='#'+f'{screen_color:02x}'*3
    hardware=[]
    for original in old['children'][:3]:
        child=copy.deepcopy(original);child['id']=f'mini-review-chat-hardware-{frame}-'+child['id']
        if child.get('src'):child['src']=str((BASE/child['src']).resolve())
        if original['id']=='p03-230':child['fill']=screen_fill
        hardware.append(child)
    body=dict(id=f'mini-review-chat-body-{frame}',type='group',x=camera['x'],y=camera['y'],scaleX=camera['scale'],scaleY=camera['scale'],children=hardware)
    children=[body]
    for name,asset in assets.items():
        if name in ['jump','zoom','robot','agent']:continue
        box=asset['box'];children.append(node(asset,ratio*box[0]+dx,ratio*box[1]+dy,ratio,identifier=f'mini-review-chat-{name}-{frame}'))
    # Pink poster silhouette gives the independent Jump card scale/position.
    box=row['jump'];scale=(box[2]-box[0])/422
    jump=fit(assets['jump'],frame,(box[0]-2*scale,box[1]-3*scale),scale,radius=7,scale_radius=.015,steps=9)
    jump['opacity']=1
    children.append(node(assets['jump'],jump['x'],jump['y'],jump['scale'],identifier=f'mini-review-chat-jump-{frame}'))
    # Tap highlight starts805 and eases out: actual footer gray231→199, then
    # recovers to216 by812. This is a whole-card dim, not a new poster asset.
    sample=a_sample=arrays[frame]
    x1=round(jump['x']+80*jump['scale']);x2=round(jump['x']+350*jump['scale'])
    y1=round(jump['y']+288*jump['scale']);y2=round(jump['y']+296*jump['scale'])
    footer_gray=float(np.median(a_sample[y1:y2,x1:x2]))
    dim=float(np.clip(1-footer_gray/231,0,.3))
    if dim>0:
        children.append(dict(id=f'mini-review-chat-tap-dim-{frame}',type='path',d=card_outline,fill='#000000',x=jump['x'],y=jump['y'],scaleX=jump['scale'],scaleY=jump['scale'],opacity=dim))
    # First sender and Agent label are rigid phone UI; second preview has an
    # independent spring. Register all four small actors independently.
    jump0=assets['jump']['box'];ui_scale=jump['scale']
    robot0=assets['robot']['box'];agent0=assets['agent']['box']
    robot_guess=(jump['x']+(robot0[0]-jump0[0])*ui_scale,jump['y']+(robot0[1]-jump0[1])*ui_scale)
    label_guess=(jump['x']+(agent0[0]-jump0[0])*ui_scale,jump['y']+(agent0[1]-jump0[1])*ui_scale)
    robot1=fit(assets['robot'],frame,robot_guess,ui_scale,radius=8,scale_radius=.03,steps=7)
    label1=fit(assets['agent'],frame,label_guess,ui_scale,radius=8,scale_radius=.03,steps=7)
    for name,asset,pose in [('sender-one',assets['robot'],robot1),('agent-one',assets['agent'],label1)]:
        children.append(node(asset,pose['x'],pose['y'],pose['scale'],pose['opacity'],identifier=f'mini-review-chat-{name}-{frame}'))
    # Search only below the first complete bubble: the cyan sender is not a
    # Zoom poster. Source800 has no preview;801 is barely born.
    a=arrays[frame];mask=np.zeros(a.shape[:2],bool)
    bottom=int(jump['y']+assets['jump']['height']*jump['scale'])
    mask[bottom+25:940,700:1250]=True
    blue=(a[:,:,2]-a[:,:,0]>5)&(a[:,:,1]-a[:,:,0]>3)&(a[:,:,0]<240)&mask
    labels,count=ndimage.label(ndimage.binary_closing(blue,iterations=3));sizes=np.bincount(labels.ravel());sizes[0]=0
    zoom=None
    if frame==801:
        # Exact source has a first18px-wide sliver below the label; normal
        # saturated-blue segmentation cannot see that faint, tiny birth.
        zoom=fit(assets['zoom'],frame,(771,812),18/325,radius=6,scale_radius=.25,steps=17)
        children.append(node(assets['zoom'],zoom['x'],zoom['y'],zoom['scale'],zoom['opacity'],identifier=f'mini-review-chat-zoom-{frame}'))
    elif frame>=802 and len(sizes)>1 and sizes.max()>18:
        yy,xx=ndimage.find_objects(labels)[sizes.argmax()-1];width=xx.stop-xx.start
        zscale=width/320
        zoom=fit(assets['zoom'],frame,(xx.start-2*zscale,yy.start-2*zscale),zscale,radius=10,scale_radius=.035,steps=11)
        children.append(node(assets['zoom'],zoom['x'],zoom['y'],zoom['scale'],zoom['opacity'],identifier=f'mini-review-chat-zoom-{frame}'))
    # The label/sender are associated with the final conversation row; they
    # fade independently rather than scaling with the tiny preview bubble.
    label2_guess=(label1['x'],label1['y']+302*ratio)
    label2=fit(assets['agent'],frame,label2_guess,ui_scale,radius=18,scale_radius=.03,steps=7)
    # The second sender is bottom-aligned with the settling preview; unlike
    # the header, its world row gap does not contract with the phone camera.
    robot2_guess=(robot1['x'],robot1['y']+273)
    robot2=fit(assets['robot'],frame,robot2_guess,ui_scale,radius=45,scale_radius=.03,steps=7)
    if frame>=801:
        for name,asset,pose in [('sender-two',assets['robot'],robot2),('agent-two',assets['agent'],label2)]:
            children.append(node(asset,pose['x'],pose['y'],pose['scale'],pose['opacity'],identifier=f'mini-review-chat-{name}-{frame}'))
    actors.append(dict(id=f'mini-review-chat-frame-{frame}',type='group',start=start,end=end,children=children))
    records.append(dict(frame=frame,camera=camera,screenColor=screen_color,jump=jump,zoom=zoom,robot1=robot1,robot2=robot2,label1=label1,label2=label2))
    print(frame,'jump',jump,'zoom',zoom,flush=True)

# Separate optical exit poses for individual off-device food/Order graphics.
# These crops never include the phone, UI, or a complete source frame.
exit_poses=[]
for record in records:
    frame=record['frame']
    if frame>807:continue
    a=arrays[frame];camera=record['camera'];left=int(camera['x']-12);right=int(camera['x']+800*camera['scale']+12)
    delta=np.max(np.abs(a-253),axis=2);mask=delta>4;mask[:,max(0,left):min(1920,right)]=False
    mask=ndimage.binary_closing(mask,iterations=4);labels,count=ndimage.label(ndimage.binary_dilation(mask,iterations=8))
    for index,box in enumerate(ndimage.find_objects(labels),1):
        if box is None:continue
        yy,xx=box
        actual=mask[yy,xx]&(labels[yy,xx]==index)
        if actual.sum()<18:continue
        # Reject thin source compression noise and never admit a wide frame.
        if xx.stop-xx.start>500 or yy.stop-yy.start>500:continue
        rgb=np.minimum(a[yy,xx],253);alpha=np.max((253-rgb)/253,axis=2);alpha*=labels[yy,xx]==index
        alpha[alpha<3/253]=0
        color=np.where(alpha[:,:,None]>0,(rgb-253*(1-alpha[:,:,None]))/np.maximum(alpha[:,:,None],1e-6),0)
        rgba=np.concatenate([np.clip(color,0,255),alpha[:,:,None]*255],axis=2).round().astype('uint8')
        file=A/f'off-device-element-{frame}-{index}.png';Image.fromarray(rgba).save(file)
        actor=dict(id=f'mini-review-exit-element-{frame}-{index}',type='image',src=str(file.resolve()),x=xx.start,y=yy.start,width=xx.stop-xx.start,height=yy.stop-yy.start,start=frame/30,end=(frame+1)/30)
        exit_poses.append(actor);provenance.append(dict(frame=frame,box=[xx.start,yy.start,xx.stop,yy.stop],opaquePixels=int((alpha>0).sum()),purpose='Individual source food or Order glyph optical exit pose only; transparent stage excluded; phone masked out.'))

spec=dict(node_updates={'p03-371':dict(start=813/30)},insert_before={'p03-371':exit_poses+actors},changed_ranges=[[800,812]],provenance=dict(staticAssets=list(assets.values()),exitingElements=provenance,explanation='A separate spring births the Zoom preview, while phone camera, sender icons, Agent labels, and Jump card are independent actors. Static genuine product UI interiors and hardware are bounded and disclosed. Off-device food/title exit only800–807 uses short per-element source optical poses, not a whole-frame or screen sequence.',limitations='Static UI interior artwork is editable as positioned image actors, not every internal glyph. Native sampling/AA and hardware material retain small residuals.'))
(REF/'peaks-review-chat-elements.json').write_text(json.dumps(spec,indent=2))
(P/'chat-fit-records.json').write_text(json.dumps(records,indent=2))
