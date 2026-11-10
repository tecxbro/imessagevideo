"""Frame837 spatial chromatic pulse: native empty-background fields and block masks."""
from pathlib import Path
import json,copy,numpy as np
from PIL import Image
from scipy import ndimage
R=Path('/workspace/imessage-recreations');REF=Path(__file__).parent;P=R/'verification/fidelity-review/03-game';A=REF/'assets/game-tinted-frame-review';A.mkdir(exist_ok=True)
FROZEN=R/'outputs/03-photon-mini/game-entry-review-07';spec=json.load(open(FROZEN/'game-entry-review-elements.json'));f=837
root=next(n for n in spec['insert_before']['p03-371']if n['id']==f'game-review-frame-{f}')
source=np.asarray(Image.open(REF/'montage-native'/f'{f-794:03}.png').convert('RGB')).astype(float)
record=next(q for q in spec['provenance']['fitRecords']if q['frame']==f);body=record['body'];x=body['x'];y=body['y'];sx=body['scaleX'];sy=body['scaleY']
display=next(n for n in root['children']if n['id']==f'game-review-display-{f}');field=display['children'][0];base_rows=field['children'];B=np.zeros_like(source)
for row in base_rows:
    c=row['fill'];B[row['y']:row['y']+row['height']]=[int(c[i:i+2],16)for i in[1,3,5]]
def rgbhex(color):return '#'+''.join(f'{int(np.clip(round(v),0,255)):02x}'for v in color)

# Sample only blank stage pixels outside the complete phone, then interpolate
# hidden cells. These native flat-color tiles contain no source UI/scene image.
step=32;ny=(1080+step-1)//step;nx=(1920+step-1)//step;stage=np.full((ny,nx,3),np.nan)
for iy in range(ny):
    for ix in range(nx):
        l=ix*step;r=min(1920,l+step);t=iy*step;b=min(1080,t+step)
        if r<=700 or l>=1220:stage[iy,ix]=np.median(source[t:b,l:r],axis=(0,1))
for iy in range(ny):
    valid=np.isfinite(stage[iy,:,0]);
    for ch in range(3):stage[iy,:,ch]=np.interp(np.arange(nx),np.where(valid)[0],stage[iy,valid,ch])
stage_nodes=[]
for iy in range(ny):
    for ix in range(nx):stage_nodes.append(dict(id=f'game-tint-stage-{iy}-{ix}',type='rect',x=ix*step,y=iy*step,width=min(step,1920-ix*step),height=min(step,1080-iy*step),fill=rgbhex(stage[iy,ix])))
root['children'].insert(0,dict(id='game-tint-stage-837',type='group',children=stage_nodes))

# Within the sheet, measure only empty high-value background; objects/fonts
# and shadows are excluded. Reconstruct a coarse color field, not a screen.
l=round(field['clip']['x']);r=round(l+field['clip']['width']);t=round(record['sheetTop']+20);b=min(1080,round(y+1630*sy));gx=(r-l+step-1)//step;gy=(b-t+step-1)//step
sheet=np.full((gy,gx,3),np.nan)
for iy in range(gy):
    for ix in range(gx):
        xa=l+ix*step;xb=min(r,xa+step);ya=t+iy*step;yb=min(b,ya+step);C=source[ya:yb,xa:xb]
        keep=C.min(2)>170
        if keep.sum()>20:sheet[iy,ix]=np.median(C[keep],axis=0)
missing=~np.isfinite(sheet[:,:,0]);_,nearest=ndimage.distance_transform_edt(missing,return_indices=True);sheet[missing]=sheet[nearest[0][missing],nearest[1][missing]]
for iy in range(gy):
    for ix in range(gx):
        xa=l+ix*step;xb=min(r,xa+step);ya=t+iy*step;yb=min(b,ya+step);color=sheet[iy,ix]
        field['children'].append(dict(id=f'game-tint-sheet-{iy}-{ix}',type='rect',x=xa,y=ya,width=xb-xa,height=yb-ya,fill=rgbhex(color)))
        B[ya:yb,xa:xb]=np.round(color)

# The warm pulse invalidated the neutral-RGB face classifier, leaving holes.
# Use stronger contrast to the measured clean background and retain logical
# connected block/shadow clusters; the pointer glow is a separate small actor.
keep_nodes=[]
for node in display['children'][1:]:
    if node.get('type')!='image':keep_nodes.append(node);continue
    if 1000<node.get('x',0)<1060 and 760<node.get('y',0)<840:keep_nodes.append(node)
alpha_raw=np.asarray(Image.open(REF/'assets/phone-hardware.png').convert('RGBA'))[:,:,3].astype(float)/255
yy,xx=np.mgrid[:1080,:1920];cx=(xx-x)/sx;cy=(yy-y)/sy;ah=ndimage.map_coordinates(alpha_raw,[cy*alpha_raw.shape[0]/1658,cx*alpha_raw.shape[1]/800],order=1,mode='constant',cval=1)
glass=ndimage.binary_erosion(ah<.08,iterations=3)&(cx>=28)&(cx<=772)&(cy>=30)&(cy<=1630)&((cx-np.clip(cx,143,657))**2+(cy-np.clip(cy,145,1515))**2<=115**2)
region=glass&(yy>=record['sheetTop']+150)&(yy<b)&(xx>=l+2)&(xx<r-2)
fg=region&(np.max(abs(source-B),axis=2)>15)
# Preserve the existing accurate pointer/glow material without duplicating it.
fg[760:840,1000:1060]=False
labels,count=ndimage.label(ndimage.binary_closing(fg,iterations=1));materials=[];objects=[]
for index,box in enumerate(ndimage.find_objects(labels),1):
    if box is None:continue
    ys,xs=box;mask=(labels[box]==index)&fg[box]
    if mask.sum()<24:continue
    if xs.stop-xs.start>430 or ys.stop-ys.start>430:continue
    C=source[box];bg=B[box];a=mask.astype(float);core=ndimage.binary_erosion(mask,iterations=1);edge=mask&~core
    minimum=np.maximum(np.max(np.maximum(0,C-bg)/np.maximum(1,255-bg),axis=2),np.max(np.maximum(0,bg-C)/np.maximum(1,bg),axis=2));a[edge]=np.clip(minimum[edge],.01,1)
    color=np.where(a[:,:,None]>0,(C-bg*(1-a[:,:,None]))/np.maximum(.0001,a[:,:,None]),0);rgba=np.concatenate([np.clip(color,0,255),a[:,:,None]*255],axis=2).round().astype('uint8');file=A/f'block-cluster-837-{index}.png';Image.fromarray(rgba).save(file)
    objects.append(dict(id=f'game-tint-block-cluster-{index}',type='image',src=str(file.resolve()),x=xs.start,y=ys.start,width=xs.stop-xs.start,height=ys.stop-ys.start));materials.append(dict(box=[xs.start,ys.start,xs.stop,ys.stop],pixels=int(mask.sum()),source=str(file.resolve())))
display['children']=[field]+objects+keep_nodes

# The exposed gray presenting-view cap also needs a continuous native shape:
# source chromatic noise had punched holes in the old neutral-color mask.
view_group=next(n for n in root['children']if n['id']==f'game-review-whole-view-dim-{f}')
view=record['view'];vl,vt,vr,vb=view['box'];sample=source[vt+8:min(vb,vt+24),max(vl+50,850):min(vr-50,1070)];color=np.median(sample,axis=(0,1));opacity=float(color.max()/253);view_group['opacity']=opacity
view_group['children'][0]=dict(id=f'game-review-view-gray-{f}',type='rect',x=vl,y=vt,width=vr-vl,height=b-vt,radius=35,fill=rgbhex(color/max(opacity,.001)))
spec['provenance']['tintedFrame837']=dict(cause='One-frame spatial chromatic pulse breaks neutral object/background masks. Native color fields use only blank stage/empty-sheet samples; hidden cells interpolate. Cube/shadow clusters use clean-background contrast; pointer retained. No full-frame/screen bitmap or source video playback.',stageTileSize=step,stageSampleExcludes=[700,1220],sheetBackgroundExcludes='R/G/B below170, fonts and objects',materials=materials,changedOnlyFrame=837)
(REF/'game-entry-review-elements-v8.json').write_text(json.dumps(spec,indent=2));(P/'tinted-frame-measurements.json').write_text(json.dumps(spec['provenance']['tintedFrame837'],indent=2));print('logical blocks',len(objects))
