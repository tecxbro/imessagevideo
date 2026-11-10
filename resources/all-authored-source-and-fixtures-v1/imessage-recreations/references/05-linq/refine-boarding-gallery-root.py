"""Create a measured card entrance and independent gallery camera/column tracks."""
from pathlib import Path
import json,copy,sys,subprocess,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'references/02-danieltian'));from trace_glyphs import trace_alpha
BASE=ROOT/'outputs/05-linq/final-v9';scene=json.loads((BASE/'scene.json').read_text())
oldcard=next(l for l in scene['layers'] if l['id']=='g-942');oldgallery=next(l for l in scene['layers'] if l['id']=='broad-v5-group-72')
fits=json.loads((REF/'assets/root-late/gallery-camera-columns-fit.json').read_text())
late_file=REF/'assets/root-late/gallery-late-native-poses.json'
if late_file.exists():fits=[r for r in fits if r['frame']<1227]+json.loads(late_file.read_text())
first,last=1182,1200;proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',f"select='between(n,{first},{last})'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
camera=[];reference1190=None;native_frames={}
for n in range(first,last+1):
 data=proc.stdout.read(960*720*3)
 if len(data)!=960*720*3:raise ValueError('Incomplete source card decode')
 a=np.frombuffer(data,np.uint8).reshape(720,960,3)
 native_frames[n]=a.copy()
 blue=((a[:,460:500,2].astype(float)-a[:,460:500,0])>15)&(a[:,460:500,0]<170)
 rows=np.where(blue.mean(1)>.8)[0]
 if not len(rows):continue
 top=int(rows[0]);white=(a[:,120:840,:].min(2)>230).mean(1)>.93
 body=np.where(white & (np.arange(720)>top+280))[0]
 y=float(body[0]-382) if len(body) and body[0]>300 else float(top+300)
 camera.append(dict(frame=n,y=y,blue_top=top,body_top=int(body[0]) if len(body) else None))
 if n==1190:reference1190=a.copy()
proc.stdout.close();proc.wait()
if reference1190 is None:raise ValueError('No source header')
top_offsets=[r['blue_top']-r['y'] for r in camera if r['blue_top']>0 and r['body_top'] is not None]
true_top=float(np.median(top_offsets))
for row in camera:
 if row['body_top'] is None:row['y']=row['blue_top']-true_top
parent1190=next(r['y'] for r in camera if r['frame']==1190)
def white_left(a,box):
 x0,y0,x1,y1=map(round,box);y0=max(0,y0);y1=min(720,y1)
 if y1<=y0:return None
 roi=a[y0:y1,x0:x1];mask=(roi.min(2)>200)&(roi.max(2)-roi.min(2)<30);yy,xx=np.where(mask)
 return x0+int(xx.min()) if len(xx)>12 else None
reference_dx=white_left(reference1190,(45,150+parent1190,315,315+parent1190))-59
header_base=white_left(reference1190,(55,parent1190-117,320,parent1190-50))-reference_dx
for row in camera:
 a=native_frames[row['frame']];left=white_left(a,(45,150+row['y'],315,315+row['y']))
 if left is not None:row['content_x']=left-59
 else:
  left=white_left(a,(55,row['y']-117,320,row['y']-50));row['content_x']=left-header_base if left is not None else reference_dx
card=copy.deepcopy(oldcard);card['start']=camera[0]['frame']/30;card['end']=40.;card['keyframes']={'y':[{'t':r['frame']/30,'value':r['y']} for r in camera]}
# Extend the actual panel above the 40s resting crop. The old scene began at the
# destination labels and consequently showed the entire card too early.
height=1-true_top;top=dict(id='root-boarding-header-background',type='path',x=0,y=true_top,width=960,height=height,
 d=f'M80 0 H880 Q960 0 960 80 V{height} H0 V80 Q0 0 80 0 Z',fill='url(#root-boarding-header-gradient)')
card['children']=[c for c in card['children'] if c['type']!='text']
card['children'].insert(0,top)
stops=[]
for offset in np.linspace(0,1,17):
 natural_y=true_top+offset*height;source_y=int(np.clip(round(natural_y+parent1190),0,719));color=np.median(reference1190[source_y,450:550],axis=0).astype(np.uint8)
 stops.append({'offset':float(offset),'color':'#'+''.join(f'{c:02x}' for c in color)})
gradient={'id':'root-boarding-header-gradient','type':'linear','x1':'0%','y1':'0%','x2':'0%','y2':'100%','stops':stops}
canonical=np.array(Image.open(REF/'assets/root-late-measure/frame-1200.png').convert('RGB'))
body_stops=[]
for yy in list(range(0,721,30))+[900]:
 color=np.median(canonical[min(yy,719),2:30],axis=0).astype(np.uint8)
 body_stops.append({'offset':yy/900,'color':'#'+''.join(f'{v:02x}' for v in color)})
body_gradient={'id':'root-boarding-body-gradient','type':'linear','x1':'0%','y1':'0%','x2':'0%','y2':'100%','stops':body_stops}
next(c for c in card['children'] if c['id']=='r-926')['fill']='url(#root-boarding-body-gradient)'
# The original background has horizontal color variation as well as vertical
# stops. Reconstruct only that smooth color field from masked native samples;
# no text, UI, or complete reference-frame pixels enter these generated textures.
card['children']=[c for c in card['children'] if c['id'] not in ['r-926','root-boarding-header-background']]
field_provenance=[];fields=[];field_dir=REF/'assets/root-late/boarding-fields';field_dir.mkdir(exist_ok=True)
terms=[(i,j) for i in range(4) for j in range(4-i)]
height=math_height=round(900-true_top)
grid_y,grid_x=np.mgrid[0:height,0:960];gx=(grid_x-480)/480;gy=(grid_y+true_top)/900
design=np.stack([gx**i*gy**j for i,j in terms],axis=-1)
for row in camera:
 n=row['frame']
 if n>=1200:continue
 a=native_frames[n];yy,xx=np.mgrid[0:720:5,0:960:5];pixels=a[yy,xx].astype(float)
 mask=(pixels.max(2)-pixels.min(2)>15)&(pixels.max(2)<240)&(pixels.mean(2)<205)&(pixels.mean(2)>15)&((yy-row['y'])>=true_top)
 px=(xx[mask]-480)/480;py=(yy[mask]-row['y'])/900;matrix=np.stack([px**i*py**j for i,j in terms],axis=1)
 samples=pixels[mask];coefficients=np.linalg.lstsq(matrix,samples,rcond=None)[0]
 for iteration in range(2):
  valid=np.abs(matrix@coefficients-samples).mean(1)<8
  coefficients=np.linalg.lstsq(matrix[valid],samples[valid],rcond=None)[0]
 colors=np.clip(design@coefficients,0,255).astype(np.uint8)
 # A measured rounded top belongs to the panel geometry, not its artwork.
 rgba=np.concatenate([colors,np.full((height,960,1),255,np.uint8)],axis=2)
 corner=80;cy,cx=np.mgrid[0:corner,0:corner];outside=(cx-corner)**2+(cy-corner)**2>corner**2
 rgba[:corner,:corner,3][outside]=0;rgba[:corner,-corner:,3][outside[:,::-1]]=0
 file=field_dir/f'gradient-{n}.png';Image.fromarray(rgba).save(file)
 error=float(np.abs(matrix@coefficients-pixels[mask]).mean())
 fields.append(dict(id=f'root-boarding-color-field-{n}',type='image',src=str(file),x=0,y=true_top,width=960,height=height,start=n/30,end=(n+1)/30,
  semanticText='Measured smooth boarding-card background color field only',editability='Generated polynomial color artwork; no reference UI or complete frame pixels'))
 field_provenance.append(dict(frame=n,terms=terms,coefficients=coefficients.tolist(),sampleMAE=error,samples=int(mask.sum())))
card['children']=fields+card['children']
for name,roi,color in [('Airbus 3221',(55,95,320,135),'#FFFFFF'),('On time',(770,95,935,135),'#B3FF3D')]:
 x0,y0,x1,y1=roi;rgb=reference1190[y0:y1,x0:x1].astype(float);background=reference1190[y0:y1,450:550].mean((1,2))[:,None]
 if name.startswith('Airbus'):alpha=np.clip((rgb.mean(2)-background)/(253-background),0,1)
 else:
  alpha=np.clip((rgb[:,:,1]-reference1190[y0:y1,450:550,1].mean(1)[:,None])/(255-reference1190[y0:y1,450:550,1].mean(1)[:,None]),0,1)
  pixels=rgb[(rgb[:,:,1]-rgb[:,:,0]>45)&(rgb[:,:,1]-rgb[:,:,2]>45)].astype(np.uint8)
  colors,counts=np.unique(pixels,axis=0,return_counts=True);ink=colors[counts.argmax()];color='#'+''.join(f'{v:02x}' for v in ink)
 d,stats=trace_alpha(alpha,x0-reference_dx,y0-parent1190)
 card['children'].append(dict(id='root-boarding-header-'+name.split()[0],type='path',d=d,fill=color,semanticText=name,sourceFrame=1190,sourceBounds=roi,editability='Native original glyph outlines; not live text'))
# Native glyph geometry preserves the actual display weight and aircraft shape.
upper=np.zeros((720,960),float);bg=np.median(canonical.astype(float),axis=1).mean(1)[:,None]
upper[35:330,40:940]=np.clip((canonical[35:330,40:940].mean(2)-bg[35:330])/(253-bg[35:330]),0,1)
d,stats=trace_alpha(upper)
card['children'].append(dict(id='root-boarding-upper-outlines',type='path',d=d,fill='#FFFFFF',semanticText='Atlanta, GA / Terminal B / ATL / airplane / San Francisco, CA / Terminal D / SFO',sourceFrame=1200))
for name,rois in [('black',[(65,480,900,560),(80,660,870,720)]),('gray',[(65,425,900,478),(80,610,870,657)])]:
 alpha=np.zeros((720,960),float);ink=np.array([0,0,0])
 if name=='gray':
  pixels=np.concatenate([canonical[y0:y1,x0:x1].reshape(-1,3) for x0,y0,x1,y1 in rois]);pixels=pixels[(pixels.mean(1)>70)&(pixels.mean(1)<200)]
  colors,counts=np.unique(pixels,axis=0,return_counts=True);ink=colors[counts.argmax()]
 for x0,y0,x1,y1 in rois:alpha[y0:y1,x0:x1]=np.clip((255-canonical[y0:y1,x0:x1].mean(2))/(255-ink.mean()),0,1)
 d,stats=trace_alpha(alpha)
 card['children'].append(dict(id='root-boarding-body-'+name,type='path',d=d,fill='#'+''.join(f'{v:02x}' for v in ink),semanticText='Passenger / Nikki Hanse / Gate 37 / Seat 10C / Date 2 July 2026 / Boarding 2:50pm',sourceFrame=1200,editability='Native source glyph outlines; not live text'))
foreground=[c for c in card['children'] if not c['id'].startswith('root-boarding-color-field-')]
card['children']=fields+[{'id':'root-boarding-native-content','type':'group','children':foreground,
 'keyframes':{'x':[{'t':r['frame']/30,'value':r['content_x']} for r in camera]}}]
gallery=copy.deepcopy(oldgallery);gallery['start']=40.;gallery['end']=1271/30
gallery['keyframes']={prop:[{'t':r['time'],'value':r[key]} for r in fits] for prop,key in [('scaleX','scale'),('scaleY','scale'),('x','x'),('y','y'),('opacity','opacity')]}
for child in gallery['children']:
 child['src']=str((BASE/child['src']).resolve());keys=child.get('keyframes',{}).get('y',[])
 a=next((k['value'] for k in keys if k['t']==41.5),child['y']);b=next((k['value'] for k in keys if k['t']==42),a)
 if child['id']=='broad-v5-image-70':a,b=701,685
 if child['id']=='rich-asset-17':
  extended=REF/'assets/root-late/gallery-left-chat-extended-preserving-hold.png'
  if extended.exists():child['src']=str(extended);child['height']=410
 slope=(b-a)/.5
 track=[]
 for r in fits:
  dy=r.get('left_dy',0) if child['x']<320 else r.get('right_dy',0) if child['x']>640 else 0
  value=a+(r['time']-41.5)*slope+dy
  if r.get('columnY'):
   offsets={'rich-asset-15':('center',0),'broad-v5-image-68':('center',-100),'broad-v5-image-70':('center',601),
    'rich-asset-16':('right',0),'broad-v5-image-69':('right',-76),'broad-v5-image-71':('right',612),
    'rich-asset-17':('left',0),'broad-v5-image-67':('left',-357)}
   column,offset=offsets[child['id']];value=r['columnY'][column]+offset
  track.append({'t':r['time'],'value':value})
 child.setdefault('keyframes',{})['y']=track
patch=dict(replacements={'g-942':card,'broad-v5-group-72':gallery},changed_ranges=[[1182,1271]],
 provenance=dict(cardEntrance=camera,colorFields=field_provenance,headerSourceFrame=1190,headerParentY=parent1190,galleryCamera=fits,
 note='Independent original phone artworks; common native camera and separate column drift, exact measured anchors. No full-frame/video runtime layer.'))
(REF/'root-boarding-gallery-patch.json').write_text(json.dumps(patch,indent=2));print(json.dumps({'card':camera,'header_parent':parent1190,'galleryAnchors':len(fits)}))
