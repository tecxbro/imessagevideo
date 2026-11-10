"""Measured iOS presentation, native sheet fill/header, isolated3D object materials."""
from pathlib import Path
import json,copy,sys,numpy as np
from PIL import Image
from scipy import ndimage
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent;P=R/'verification/fidelity-review/03-game';A=REF/'assets/game-entry-review';A.mkdir(exist_ok=True)
BASE=R/'outputs/03-photon-mini/final-v15';scene=json.load(open(BASE/'scene.json'))
sys.path.insert(0,str(REF.parent/'02-danieltian'));from trace_glyphs import trace_alpha
records=json.load(open(P/'presentation-refined.json'))
hardware_alpha=np.asarray(Image.open(REF/'assets/phone-hardware.png').convert('RGBA'))[:,:,3].astype(float)/255
hardware_pixels=np.asarray(Image.open(REF/'assets/phone-hardware.png').convert('RGBA')).copy()
hh,ww=hardware_alpha.shape;hy_grid,hx_grid=np.mgrid[:hh,:ww]
cx=hx_grid*800/ww;cy=hy_grid*1658/hh
inner_domain=(cx>25)&(cx<775)&(cy>25)&(cy<1635)&((cx-np.clip(cx,143,657))**2+(cy-np.clip(cy,145,1515))**2<120**2)
near_hole=ndimage.distance_transform_edt(hardware_alpha>.08)<=2.1
bright=hardware_pixels[:,:,:3].min(2).astype(float)
fringe=inner_domain&near_hole&(bright>180)
factor=np.clip((220-bright)/40,0,1)
hardware_pixels[:,:,3][fringe]=(hardware_pixels[:,:,3][fringe]*factor[fringe]).round().astype('uint8')
clean_hardware=A/'genuine-hardware-inner-white-matte-cleaned.png';Image.fromarray(hardware_pixels).save(clean_hardware)
hole_l=[];hole_r=[]
for row in hardware_alpha[200:800]:
    good=np.where((row<.08)&(np.arange(len(row))>17)&(np.arange(len(row))<491))[0]
    if len(good)>100:hole_l.append(good.min());hole_r.append(good.max()+1)
hole_left=float(np.median(hole_l))*800/hardware_alpha.shape[1]
hole_right=float(np.median(hole_r))*800/hardware_alpha.shape[1]
phone=next(n for n in scene['layers']if n['id']=='p03-371')
game=next(n for n in scene['layers']if n['id']=='measured-game-v13')
canonical=next(n for n in scene['layers']if n['id']=='mini-review-chat-frame-812')
ui=[copy.deepcopy(n)for n in canonical['children']if 'hardware'not in n['id']and'body'not in n['id']and'tap-dim'not in n['id']and'island'not in n['id']]
avatar=next(n for n in ui if n['id']=='mini-review-chat-team-avatar-812')
def rename(node,prefix):
    node=copy.deepcopy(node);node['id']=prefix+node['id']
    if node.get('src')and not node['src'].startswith(('/','data:')):node['src']=str((BASE/node['src']).resolve())
    node['children']=[rename(c,prefix)for c in node.get('children',[])] if 'children'in node else node.get('children',[])
    if not node.get('children'):node.pop('children',None)
    return node

content_measurements={n['frame']:n['camera']for n in json.load(open(P/'content-camera.json'))}
actors=[];ledger=[];fit_records=[];last_q=None;last_view=None;last_content=None;last_content_view=None
for record in records:
    f=record['frame'];source=np.asarray(Image.open(REF/'montage-native'/f'{f-794:03}.png').convert('RGB')).astype(float)
    body=record['body'];sx=body['scaleX'];sy=body['scaleY'];x=body['x'];y=body['y'];left=x+28*sx;right=x+772*sx;bottom=y+1630*sy;top=record['sheetTop']
    children=[dict(id=f'game-review-black-screen-{f}',type='group',x=x,y=y,scaleX=sx,scaleY=sy,children=[dict(id=f'game-review-black-display-{f}',type='rect',x=0,y=0,width=800,height=1658,radius=150,fill='#000000')])]
    view=record['view']
    if view:
        # Trace only the actual gray view's outer contour; all internal UI
        # remains independently positioned static assets, never a screen crop.
        neutral=(source.max(2)-source.min(2)<6)&(source.mean(2)>70)&(source.mean(2)<253)
        roi=np.zeros(neutral.shape,bool);roi[round(y)+5:top,round(x):round(x+800*sx)]=True
        labels,count=ndimage.label(neutral&roi);sizes=np.bincount(labels.ravel());sizes[0]=0;index=sizes.argmax();mask=ndimage.binary_fill_holes(labels==index)
        yy,xx=np.where(mask);l=int(xx.min());r=int(xx.max()+1);t=int(yy.min());b=int(yy.max()+1)
        visible_bottom=b;full_bottom=min(1080,round(bottom));mask[b:full_bottom,l:r]=True;b=full_bottom
        local=mask[t:b,l:r];core=ndimage.binary_erosion(local,iterations=2)
        alpha=local*np.clip(source[t:b,l:r].mean(2)/max(1,np.mean(view['color'])),0,1);alpha[core]=1
        alpha[max(0,visible_bottom-t):]=local[max(0,visible_bottom-t):]
        d,stats=trace_alpha(alpha)
        view_background=dict(id=f'game-review-view-gray-{f}',type='path',x=l,y=t,d=d,fill='#fdfdfd')
        fit=record['avatar']
        if fit and fit['ncc']>.85:
            q=fit['scale']/avatar['scaleX'];dx=fit['x']-q*avatar['x'];dy=fit['y']-q*avatar['y'];last_q=dict(scale=q,x=dx,y=dy)
        elif last_q is not None:
            # Later avatar pixels are covered by the rising sheet; retain
            # measured pane geometry instead of fitting another graphic.
            ratio=(r-l)/(last_view[2]-last_view[0])
            q=last_q['scale']*ratio;dx=l+(last_q['x']-last_view[0])*ratio;dy=t+(last_q['y']-last_view[1])*ratio
            last_q=dict(scale=q,x=dx,y=dy)
        else:raise ValueError('Missing first source UI camera')
        last_view=[l,t,r,b]
        content=[rename(n,f'game-review-ui-{f}-')for n in ui]
        row_nodes=[n for n in content if any(k in n['id']for k in ['-jump-','-zoom-','-sender-','-agent-'])]
        header_nodes=[n for n in content if n not in row_nodes]
        image_group=dict(id=f'game-review-ui-presentation-{f}',type='group',x=dx,y=dy,scaleX=q,scaleY=q,children=header_nodes,clip=dict(x=(l-dx)/q,y=(t-dy)/q,width=(r-l)/q,height=2200,radius=34/q))
        if f in content_measurements:last_content=dict(content_measurements[f])
        elif last_content is not None:
            ratio=(r-l)/(last_content_view[2]-last_content_view[0]);last_content=dict(scale=last_content['scale']*ratio,x=l+(last_content['x']-last_content_view[0])*ratio,y=t+(last_content['y']-last_content_view[1])*ratio)
        last_content_view=[l,t,r,b]
        cq=last_content['scale'];cdx=last_content['x'];cdy=last_content['y']
        row_group=dict(id=f'game-review-chat-row-presentation-{f}',type='group',x=cdx,y=cdy,scaleX=cq,scaleY=cq,children=row_nodes,clip=dict(x=(l-cdx)/cq,y=(t-cdy)/cq,width=(r-l)/cq,height=2200,radius=34/cq))
        children.append(dict(id=f'game-review-whole-view-dim-{f}',type='group',opacity=view['opacity'],children=[view_background,image_group,row_group],clip=dict(x=left,y=y+30*sy,width=right-left,height=bottom-(y+30*sy),radius=115*sx)))
    # Actual empty game rows yield a native editable color field, not a frame
    # texture. Every retained pixel in this fill is a median RGB color.
    l=max(0,round(left));r=min(1920,round(right));start=max(0,top);end=min(1080,round(bottom));colors=[]
    for yy in range(start,end):
        row=source[yy,l:r];keep=(row[:,0]>165)&(row[:,0]<235)&(row[:,2]-row[:,0]>5)&(abs(row[:,0]-row[:,1])<7)
        colors.append(np.median(row[keep],axis=0)if keep.sum()>12 else [np.nan]*3)
    colors=np.asarray(colors)
    for ch in range(3):
        good=np.isfinite(colors[:,ch]);colors[:,ch]=np.interp(np.arange(len(colors)),np.where(good)[0],colors[good,ch])
    if len(colors)>25:colors[:15]=colors[20]
    rows=[]
    for offset in range(len(colors)):
        yy=start+offset;col=colors[offset];op=1.;xl=left;xr=right
        if offset<80:
            a=np.clip((source[yy,l:r,2]-source[yy,l:r,0])/max(8,col[2]-col[0]),0,1)
            a[(source[yy,l:r,0]<100)|(abs(source[yy,l:r,0]-source[yy,l:r,1])>10)]=0
            op=float(np.quantile(a,.8))
            if op<.08:continue
            xx=np.where(a>=op*.5)[0]
            if len(xx)<20:continue
            lo=int(xx.min());hi=int(xx.max());xl=l+lo;xr=l+hi+1
            if lo>0 and a[lo]>a[lo-1]:xl-=float((a[lo]-op*.5)/(a[lo]-a[lo-1]))-.5
            if hi<len(a)-1 and a[hi]>a[hi+1]:xr+=float((a[hi]-op*.5)/(a[hi]-a[hi+1]))-.5
        # The first80 rows need one-pixel contour fidelity; the remaining
        # straight sheet uses four-pixel native color bands.
        if offset>=80 and (offset-80)%4:continue
        height=1 if offset<80 else min(4,len(colors)-offset)
        rows.append(dict(id=f'game-review-fill-{f}-{offset}',type='rect',x=float(xl),y=yy,width=float(xr-xl),height=height,fill='#'+''.join(f'{round(v):02x}'for v in col),opacity=op))
    # Fit a smooth native rounded top from measured50% cap contours, keeping
    # the independently measured row-opacity/color ramp. Raw row bounds had
    # inherited source compression jitter and made a staircase.
    glass_left=x+hole_left*sx;glass_right=x+hole_right*sx
    opaque_rows=[n['y']for n in rows if n['opacity']>=.5]
    smooth_top=float(min(opaque_rows))if opaque_rows else start
    smooth_radius=60*sx
    for n in rows:n.update(x=glass_left,width=glass_right-glass_left)
    sheet=[dict(id=f'game-review-color-field-{f}',type='group',children=rows,clip=dict(x=glass_left,y=smooth_top,width=glass_right-glass_left,height=2000,radius=smooth_radius))]
    # Decompose only isolated foreground cubes, shadows, peg and pointer.
    # Source pixels never become a complete game-screen/frame sequence.
    B=np.zeros_like(source);B[start:end]=colors[:,None,:]
    region=np.zeros(source.shape[:2],bool);region[max(0,top+155):end,l:r]=True
    # Source foreground at the glass edge must not connect to the bezel.
    # Otherwise a real cropped shadow/cube becomes one enormous hardware CC
    # and gets rejected, while small rim fragments masquerade as game objects.
    yy_world,xx_world=np.mgrid[:1080,:1920]
    hx=(xx_world-x)/sx*hardware_alpha.shape[1]/800
    hy=(yy_world-y)/sy*hardware_alpha.shape[0]/1658
    hole=ndimage.map_coordinates(hardware_alpha,[hy,hx],order=1,mode='constant',cval=1)<.08
    region&=ndimage.binary_erosion(hole,iterations=3)
    region[:, :max(0,round(glass_left)+2)]=False
    region[:, min(1920,round(glass_right)-2):]=False
    gx=(xx_world-x)/sx;gy=(yy_world-y)/sy
    rounded=(gx>=28)&(gx<=772)&(gy>=30)&(gy<=1630)&((gx-np.clip(gx,143,657))**2+(gy-np.clip(gy,145,1515))**2<=115**2)
    region&=rounded
    delta=np.max(abs(source-B),axis=2);fg=region&(delta>5)
    green=fg&(source[:,:,1]>source[:,:,0]*1.13)&(source[:,:,1]>source[:,:,2]*1.15)&(source[:,:,1]>65)
    peg=fg&(source[:,:,2]-source[:,:,0]>14)&(source[:,:,0]<100)&(source[:,:,1]<115)
    neutral=fg&(source.max(2)-source.min(2)<7)
    dark=neutral&(source.mean(2)<105);light=neutral&~dark
    shadow=fg&~green&~peg&~neutral
    object_count=0
    for kind,selection in [('shadow',shadow),('dark-cube',dark),('light-cube',light),('green-cube',green),('peg',peg)]:
        merged=ndimage.binary_closing(selection,iterations=1);labels,count=ndimage.label(merged)
        for index,box in enumerate(ndimage.find_objects(labels),1):
            if box is None:continue
            yy,xx=box;mask=(labels[box]==index)&selection[box]
            if mask.sum()<24:continue
            if min(xx.stop-xx.start,yy.stop-yy.start)<3 and max(xx.stop-xx.start,yy.stop-yy.start)>20:continue
            # A broad background/color-field artifact is never admitted as
            # an object. Logical foreground components remain individually bounded.
            if xx.stop-xx.start>430 or yy.stop-yy.start>430:continue
            C=source[box];bg=B[box];a=mask.astype(float);core=ndimage.binary_erosion(mask,iterations=1)
            edge=mask&~core
            minimal=np.maximum(np.max(np.maximum(0,C-bg)/np.maximum(1,255-bg),axis=2),np.max(np.maximum(0,bg-C)/np.maximum(1,bg),axis=2))
            a[edge]=np.clip(minimal[edge],.01,1)
            rgb=np.where(a[:,:,None]>0,(C-bg*(1-a[:,:,None]))/np.maximum(.0001,a[:,:,None]),0)
            rgba=np.concatenate([np.clip(rgb,0,255),a[:,:,None]*255],axis=2).round().astype('uint8')
            file=A/f'{kind}-{f}-{index}.png';Image.fromarray(rgba).save(file)
            sheet.append(dict(id=f'game-review-{kind}-{f}-{index}',type='image',src=str(file.resolve()),x=xx.start,y=yy.start,width=xx.stop-xx.start,height=yy.stop-yy.start))
            ledger.append(dict(frame=f,kind=kind,box=[xx.start,yy.start,xx.stop,yy.stop],pixels=int(mask.sum()),source=str(file.resolve()),notice='Individual projected3D game object/shadow optical material, transparent background; not a game screen or complete frame.'))
            object_count+=1
    old_panel=next(n for n in game['children']if n['id']==f'game-frame-{f}')
    caption=next(n for n in old_panel['children']if n['id']==f'game-caption-score-{f}')
    caption=rename(caption,f'game-review-caption-{f}-');caption['semanticText']='Jump Jump; actual native source score'
    sheet.append(caption)
    # The gray grab handle was below the old dark glyph threshold and absent.
    handle_bg=np.round(B);handle_delta=source-handle_bg
    handle=(source[:,:,0]>75)&(source.mean(2)<handle_bg.mean(2)-15)&(handle_delta.max(2)-handle_delta.min(2)<20)
    roi=np.zeros(handle.shape,bool);roi[max(0,top+4):min(1080,top+22),900:1020]=True
    original_handle=handle&roi
    labels,count=ndimage.label(ndimage.binary_closing(original_handle,structure=np.ones((3,9))));choices=[]
    for index,box in enumerate(ndimage.find_objects(labels),1):
        if box is None:continue
        yy,xx=box;w=xx.stop-xx.start;h=yy.stop-yy.start
        if 30<w<95 and h<=7:choices.append((w,index,box))
    if choices:
        _,index,box=max(choices);yy,xx=box;color=np.median(source[(labels==index)&original_handle],axis=0)
        sheet.append(dict(id=f'game-review-handle-{f}',type='rect',x=xx.start,y=yy.start,width=xx.stop-xx.start,height=yy.stop-yy.start,radius=(yy.stop-yy.start)/2,fill='#'+''.join(f'{round(v):02x}'for v in color)))
    children.append(dict(id=f'game-review-display-{f}',type='group',clip=dict(x=left,y=y+30*sy,width=right-left,height=bottom-(y+30*sy),radius=115*sx),children=sheet))
    hardware=[rename(n,f'game-review-chrome-{f}-')for n in phone['children']if n['id']in ['p03-231','p03-232','p03-233','p03-234']]
    for node in hardware:
        if node['id'].endswith('p03-231'):node['src']=str(clean_hardware.resolve())
    children.append(dict(id=f'game-review-physical-overlay-{f}',type='group',x=x,y=y,scaleX=sx,scaleY=sy,children=hardware))
    actors.append(dict(id=f'game-review-frame-{f}',type='group',start=f/30,end=(f+1)/30,children=children))
    fit_records.append(dict(frame=f,body=body,view=view,presentationCamera=last_q,contentCamera=last_content,sheetTop=smooth_top,sheetRadius=smooth_radius,objects=object_count,nativeColorBands=len(rows)))
    print(f,object_count,len(rows),view['opacity']if view else None,flush=True)
updates={}
for root in [phone,game]:
    end=root.get('end',scene['duration']);updates[root['id']]=dict(keyframes=dict(end=[dict(t=812/30,value=end,ease='hold'),dict(t=813/30,value=813/30,ease='hold'),dict(t=850/30,value=end,ease='hold')]))
spec=dict(node_updates=updates,insert_before={'p03-371':actors},changed_ranges=[[813,849]],provenance=dict(base=str(BASE/'scene.json'),scope='Actual game lifecycle813–849 approved by parent. Authentic static chat actors and complete presenting-view geometry under measured iOS scale/dim; independently fitted row camera, physical camera from three complete body silhouettes. Native sheet color bands, score/title paths and grab handle. Independently bounded3D object optical assets replace jagged palette masks. Hardware inner white-matte fringe corrected only near its transparent screen aperture. No whole-source-frame/screen/video playback.',objectMaterials=ledger,fitRecords=fit_records,limitations='3D optical materials are independently editable image actors with source-projected poses, not a complete editable3D game. Regenerate poses/materials after changing the3D animation. Internal chat card/header copy remains static product UI artwork. Minor hardware/AA/color-field residuals remain.'))
(REF/'game-entry-review-elements.json').write_text(json.dumps(spec,indent=2))
(P/'build-records.json').write_text(json.dumps(fit_records,indent=2))
