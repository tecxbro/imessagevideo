"""Read-only source/material fitting and bounded seat-grid entrance construction."""
from pathlib import Path
import json,copy,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent
P=R/'verification/fidelity-review/05-seat-entrance';A=REF/'assets/seat-entrance-review';A.mkdir(exist_ok=True)
BASE=R/'outputs/05-linq/final-v13';scene=json.load(open(BASE/'scene.json'))
grid_root=next(n for n in scene['layers']if n['id']=='v10-seat-base')
grid=np.asarray(Image.open(BASE/grid_root['children'][0]['src']).convert('RGB')).astype(float)/255
fare_root=next(n for n in scene['layers']if n['id']=='rich-group-4')
fare_node=fare_root['children'][0]['children'][1]
fare=np.asarray(Image.open(BASE/fare_node['src']).convert('RGBA')).astype(float)/255
opaque_fare_node=fare_root['children'][0]['children'][0]
opaque_fare=np.asarray(Image.open(BASE/opaque_fare_node['src']).convert('RGB').resize((fare.shape[1],fare.shape[0]),Image.Resampling.LANCZOS)).astype(float)/255
button_mask=Image.new('L',(fare.shape[1]*4,fare.shape[0]*4),0)
ImageDraw.Draw(button_mask).rounded_rectangle((-113*4,553*4,177*4,603*4),radius=25*4,fill=255)
button_alpha=np.asarray(button_mask.resize((fare.shape[1],fare.shape[0]),Image.Resampling.LANCZOS)).astype(float)/255
old_alpha=fare[:,:,3].copy();new_alpha=old_alpha+button_alpha*(1-old_alpha)
fare[:,:,:3]=(fare[:,:,:3]*old_alpha[:,:,None]+opaque_fare*button_alpha[:,:,None]*(1-old_alpha[:,:,None]))/np.maximum(.0001,new_alpha[:,:,None])
fare[:,:,3]=new_alpha
fare_file=A/'fare-repaired-clipped-button.png'
Image.fromarray(np.clip(fare*255,0,255).round().astype('uint8')).save(fare_file)
H,W=grid.shape[:2];mask=np.zeros((H,W),bool)
xs=[306,352,398,535,581,627];ys=[80,137,194,252,309,367,424,481,538,596,653,710]
for yy in ys:
    for xx in xs:
        x=xx-188;y=yy;w=31;h=42
        mask[max(0,y-3):min(H,y+h+3),max(0,x-3):min(W,x+w+3)]=True
# Letters, row numbers, and red exit outline/text are separate alpha material.
text_regions=[]
for xx in xs:text_regions.append((xx-188-3,35,xx-188+34,67,'white'))
for i,yy in enumerate(ys):text_regions.append((468-188,yy+8,494-188,min(H,yy+39),'blue'))
text_regions.extend([(278-188,472,682-188,477,'red'),(278-188,583,682-188,590,'red'),(278-188,473,302-188,586,'red'),(659-188,473,684-188,586,'red')])
for l,t,r,b,color in text_regions:mask[max(0,t):min(H,b),max(0,l):min(W,r)]=True
# Smooth cloud texture under UI only; original observed sky stays untouched.
# This is a static bounded app photograph, not a source motion-frame sequence.
sky_path=A/'seat-sky-static.png'
if sky_path.exists():
    sky=np.asarray(Image.open(sky_path).convert('RGB')).astype(float)/255
else:
    sky=grid.copy();_,nearest=ndimage.distance_transform_edt(mask,return_indices=True)
    sky[mask]=grid[nearest[0][mask],nearest[1][mask]]
    for iteration in range(1100):
        smooth=ndimage.convolve(sky,np.array([[0,1,0],[1,0,1],[0,1,0]])[:,:,None]/4,mode='nearest')
        sky[mask]=smooth[mask]
alpha=np.zeros((H,W));rgb=np.zeros_like(grid)
for yy in ys:
    for xx in xs:
        x=xx-188;y=yy;l=max(0,x-3);r=min(W,x+35);t=max(0,y-3);b=min(H,y+46)
        C=grid[t:b,l:r];B=sky[t:b,l:r]
        F=np.median(grid[min(H-1,y+7):min(H,y+34),x+4:x+7],axis=(0,1))
        D=F-B;aa=np.clip(((C-B)*D).sum(2)/np.maximum(1e-6,(D*D).sum(2)),0,1)
        core=np.zeros(aa.shape,bool)
        core[max(0,y+4-t):min(b-t,y+38-t),max(0,x+4-l):min(r-l,x+27-l)]=True
        aa[core]=1;aa[aa<.035]=0
        color=np.broadcast_to(F,C.shape).copy();color[core]=C[core]
        rgb[t:b,l:r]=color;alpha[t:b,l:r]=aa
for l,t,r,b,color in text_regions:
    l=max(0,l);r=min(W,r);t=max(0,t);b=min(H,b)
    C=grid[t:b,l:r];B=sky[t:b,l:r]
    if color=='white':F=np.array([.82,.82,.82])
    elif color=='blue':F=np.array([.09,.29,.52])
    else:F=np.array([.86,.31,.43])
    D=F-B;aa=np.clip(((C-B)*D).sum(2)/np.maximum(1e-6,(D*D).sum(2)),0,1)
    aa[aa<.035]=0
    current=alpha[t:b,l:r];use=aa>current
    rgb[t:b,l:r][use]=F;alpha[t:b,l:r]=np.maximum(current,aa)
rgba=np.concatenate([np.clip(rgb,0,1),alpha[:,:,None]],axis=2)
sky_file=A/'seat-sky-static.png';ui_file=A/'seat-ui-transparent.png'
Image.fromarray(np.clip(sky*255,0,255).round().astype('uint8')).save(sky_file)
Image.fromarray(np.clip(rgba*255,0,255).round().astype('uint8')).save(ui_file)

def linear(a):return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def srgb(a):return np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)
def translated_fare(x):
    out=np.concatenate([sky.copy(),np.ones((H,W,1))],axis=2)
    left=max(0,x);right=min(W,W+x)
    if right>left:
        src=fare[:,left-x:right-x];a=src[:,:,3,None]
        out[:,left:right,:3]=src[:,:,:3]*a+out[:,left:right,:3]*(1-a)
    return out[:,:,:3]
positions={414:-32,415:-113,416:-112,417:-223,418:-344,419:-454,420:-534,421:-534}
records=[];actors=[];ledger=[]
for frame,x in positions.items():
    source=np.asarray(Image.open(P/'source'/f'{frame:06}.png').convert('RGB')).astype(float)[:,188:770]/255
    B=translated_fare(x);best=[]
    for mode in ['rgb','linear']:
        base=linear(B)if mode=='linear'else B
        material=linear(np.clip(rgb,0,1))if mode=='linear'else np.clip(rgb,0,1)
        target=linear(source)if mode=='linear'else source
        delta=(material-base)*alpha[:,:,None]
        op=float(np.clip(((target-base)*delta).sum()/max(1e-8,(delta*delta).sum()),0,1))
        result=base+op*delta
        if mode=='linear':result=srgb(result)
        best.append(dict(mode=mode,opacity=op,mae=float(abs(source-result).mean()*255)))
    chosen=min(best,key=lambda q:q['mae']);op=chosen['opacity']
    if frame<=416:op=0.0
    # Explicit local color correction only if the source prefers linear-light
    # fading; no shared renderer feature and no source-frame pixel playback.
    correction=None
    if chosen['mode']=='linear' and op>0:
        expected=srgb(linear(B)+(linear(np.clip(rgb,0,1))-linear(B))*alpha[:,:,None]*op)
        corrected=np.where(alpha[:,:,None]*op>.0001,(expected-B*(1-alpha[:,:,None]*op))/np.maximum(.0001,alpha[:,:,None]*op),0)
        correction=A/f'seat-ui-linear-color-{frame}.png'
        Image.fromarray(np.clip(np.concatenate([corrected,alpha[:,:,None]],axis=2)*255,0,255).round().astype('uint8')).save(correction)
    ui_source=correction or ui_file
    children=[dict(id=f'seat-review-sky-{frame}',type='image',src=str(sky_file.resolve()),x=188,y=0,width=W,height=H),dict(id=f'seat-review-fares-{frame}',type='image',src=str(fare_file.resolve()),x=188+x,y=0,width=W,height=H),dict(id=f'seat-review-grid-{frame}',type='image',src=str(ui_source.resolve()),x=188,y=0,width=W,height=H,opacity=op)]
    if frame>=420:
        # By420 the grid is fully settled and the final fare sliver does not
        # overlap its seats. Retain exact original static grid material here.
        children=[dict(id=f'seat-review-settled-grid-{frame}',type='image',src=str((BASE/grid_root['children'][0]['src']).resolve()),x=188,y=0,width=W,height=H),children[1]]
    if frame!=419:
        actors.append(dict(id=f'seat-review-frame-{frame}',type='group',start=frame/30,end=(frame+1)/30,clip=dict(x=188,y=0,width=W,height=H),children=children))
    records.append(dict(frame=frame,x=x,models=best,chosen=chosen,nativeOpacity=op,preserveBaseline=frame==419))
    print(records[-1],flush=True)
gates={}
for root in [grid_root,fare_root,next(n for n in scene['layers']if n['id']=='rich-group-6')]:
    end=root.get('end',scene['duration']);gates[root['id']]=dict(keyframes=dict(end=[dict(t=413/30,value=end,ease='hold'),dict(t=414/30,value=414/30,ease='hold'),dict(t=419/30,value=end,ease='hold'),dict(t=420/30,value=420/30,ease='hold'),dict(t=422/30,value=end,ease='hold')]))
spec=dict(node_updates=gates,insert_before={'rich-group-4':actors},changed_ranges=[[414,418],[420,421]],provenance=dict(base=str(BASE/'scene.json'),sourceFrames=list(positions),sky='Static bounded cloud background with UI-only harmonic inpainting; original observed sky outside the UI masks is untouched. Unobserved fine cloud variation under seats is approximate.',grid='Static authentic seat/cross/label UI alpha separated from background; bitmap internal detail, native position/fade/lifetime. By420 use exact original opaque grid again, behind the nonoverlapping fare sliver.419 baseline retained because the first native prototype slightly regressed it. Never source full-frame/video playback.',fare='Existing accepted static transparent fare UI material; repaired its accidentally keyed-out clipped Basic blue button from the original opaque product UI. Native camera corrected independently from white card edges, not reduced-contrast glyph thresholds.',records=records,limitations='Static UI internals retain bitmap editability limits and cloud inpainting residual. Local linear-light textures are computed from static UI and native clean underlay; regenerate after geometry changes.'))
(REF/'seat-entrance-review-elements.json').write_text(json.dumps(spec,indent=2))
(P/'fit-records.json').write_text(json.dumps(records,indent=2))
