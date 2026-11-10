"""Separate the physical device materialization from its visible Messages UI."""
from pathlib import Path
import json,copy,subprocess,numpy as np,sys
from PIL import Image
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'references/02-danieltian'));from trace_glyphs import trace_alpha
patch=json.loads((REF/'root-lock-patch.json').read_text());device=patch['replacements']['g-1237'];photo=next(c for c in device['children'] if c['id']=='i-1214')
original=Image.open(photo['src']).convert('RGBA');extended=Image.new('RGBA',(681,1456),(255,255,255,0));extended.paste(original,(0,0));strip=original.crop((0,1060,681,1080)).resize((681,376),Image.Resampling.BILINEAR);extended.paste(strip,(0,1080));file=REF/'assets/root-lock/physical-hardware-extended.png';extended.save(file)
assert np.array_equal(np.array(extended)[:1080],np.array(original))
# Preserve the actual landlord-scene metal colors instead of the birthday
# scene's differently lit frame. Only the hardware mask becomes visible.
reference=Image.open(REF/'assets/root-lock-measure/frame-0515.png').convert('RGB');reference_crop=reference.crop((596,80,1275,1080));actual=Image.new('RGBA',(679,1451),(255,255,255,0));actual.paste(reference_crop,(0,0));actual.paste(reference_crop.crop((0,980,679,1000)).resize((679,451),Image.Resampling.BILINEAR),(0,1000));actual.putalpha(extended.getchannel('A').resize(actual.size,Image.Resampling.LANCZOS));clean=np.array(actual);clean[:,:,:3][clean[:,:,3]==0]=255;extended=Image.fromarray(clean);actual_file=REF/'assets/root-lock/landlord-hardware-reference.png';extended.save(actual_file)
photo['src']=str(file);photo['height']=1456;photo.pop('keyframes',None)
hardware_ids={'r-1213','i-1214','r-1215','c-1226'};hardware=[c for c in device['children'] if c['id'] in hardware_ids];device['children']=[c for c in device['children'] if c['id'] not in hardware_ids]
backplate=next(c for c in hardware if c['id']=='r-1213')
camera={r['frame']:r for r in patch['provenance']['camera']};records=[];header_records=[];blue_layers=[];physical_records=[];rim_layers=[]
source_boxes={r['frame']:r['grayBoxes'] for r in patch['provenance']['bubbles']};backplate_colors=[]
flat=Image.new('RGBA',extended.size,'white');flat.alpha_composite(extended);darkness=255-np.array(flat.convert('RGB'),float).mean(2);profile=darkness[200:800].mean(0);local_left=float(profile[:50].argmax())*681/extended.width;local_right=float(extended.width-50+profile[-50:].argmax())*681/extended.width;local_top=float(darkness[:40,round(200*extended.width/681):round(480*extended.width/681)].mean(1).argmax())*1456/extended.height
rim_dir=REF/'assets/root-lock/materialization';rim_dir.mkdir(exist_ok=True)
logo=next(c for c in device['children'] if c['id']=='i-1233');logo_rgba=np.array(Image.open(logo['src']).convert('RGBA').resize((round(logo['width']),round(logo['height'])),Image.Resampling.LANCZOS));mask=(logo_rgba[:,:,3]>127)&(logo_rgba[:,:,:3].max(2)<140);labels,_=ndimage.label(mask,np.ones((3,3)));pieces=[(int((labels[sl]==i+1).sum()),sl) for i,sl in enumerate(ndimage.find_objects(labels)) if sl];_,sl=max(pieces,key=lambda r:r[0]);ly,lx=sl;logo_box=(lx.start,ly.start,lx.stop,ly.stop);logo_w=lx.stop-lx.start;logo_h=ly.stop-ly.start
def blue_box(a):
 mask=(a[:,:,2]-a[:,:,0]>15)&(a[:,:,2]>200)&(a[:,:,1]>80);mask[:650]=False;mask[:,:850]=False;mask[:,1400:]=False;labels,_=ndimage.label(mask,np.ones((3,3)));candidates=[]
 for i,sl in enumerate(ndimage.find_objects(labels)):
  if sl is None:continue
  yy,xx=sl;area=int((labels[sl]==i+1).sum())
  if area>400 and xx.stop-xx.start>70 and yy.stop-yy.start>15:candidates.append((area,(xx.start,yy.start,xx.stop,yy.stop)))
 return max(candidates)[1] if candidates else None
first,last=483,554;proc=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',f"select='between(n,{first},{last})'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
for n in range(first,last+1):
 raw=proc.stdout.read(1920*1080*3)
 if len(raw)!=1920*1080*3:raise ValueError('Incomplete physical source decode')
 source=np.frombuffer(raw,np.uint8).reshape(1080,1920,3).astype(float);pose=camera[n];parent_sx,parent_sy=pose['scaleX'],pose['scaleY'];parent_x,parent_y=pose['x'],pose['y'];sx=sy=parent_sx;x=parent_x;y=parent_y;header_alpha=0.
 first_box=source_boxes[n][0];gx0=min(1860,first_box[2]+20);gx1=min(1910,first_box[2]+70);gy0=min(1030,first_box[1]+20);gy1=min(1070,first_box[1]+50);color=np.median(source[gy0:gy1,gx0:gx1],axis=(0,1)).astype(np.uint8);backplate_colors.append({'t':n/30,'value':'#'+''.join(f'{v:02x}' for v in color)})
 # The message layout and the native phone header have distinct entrance poses.
 # Use the mascot's own connected outline, preserving its scale when top-clipped.
 center=parent_x+(306+(lx.start+lx.stop)/2)*parent_sx;top=parent_y+141*parent_sy
 rx0=max(0,round(center-130*parent_sx));rx1=min(1920,round(center+130*parent_sx));ry0=max(0,round(top-180));ry1=min(1080,round(top+130*parent_sy))
 roi=source[ry0:ry1,rx0:rx1];dark=(roi.max(2)-roi.min(2)<30)&(roi.max(2)<140);labels,_=ndimage.label(dark,np.ones((3,3)));candidates=[]
 for i,slice_ in enumerate(ndimage.find_objects(labels)):
  if slice_ is None:continue
  yy,xx=slice_;w,h=xx.stop-xx.start,yy.stop-yy.start;cx=rx0+(xx.start+xx.stop)/2
  if .4*logo_w*parent_sx<w<1.6*logo_w*parent_sx and .1*logo_h*parent_sx<h<1.6*logo_h*parent_sx and abs(cx-center)<80*parent_sx:candidates.append((int((labels[slice_]==i+1).sum()),(rx0+xx.start,ry0+yy.start,rx0+xx.stop,ry0+yy.stop)))
 if candidates:
  _,box=max(candidates);bx0,by0,bx1,by1=box;header_alpha=1.
  if by0>2 and by1-by0>.65*logo_h*parent_sx:
   sx=sy=(bx1-bx0)/logo_w;y=by0-(141+ly.start)*sy;x=bx0-(306+lx.start)*sx
  else:
   x=(bx0+bx1)/2-(306+(lx.start+lx.stop)/2)*sx;y=by1-(141+ly.stop)*sy
 # The physical frame uses its own rigid camera and reveals from top to bottom.
 # A scalar opacity fitted on the middle rails hid the already-visible top arc.
 shade=255-source.mean(2);ps=.984*sx;px=x+(681*sx-681*ps)/2-3;py=y+2;confidence=0.
 y0=max(0,round(y+200*sx));y1=min(1080,round(y+600*sx))
 if y1-y0>30:
  scores=shade[y0:y1].mean(0);left=range(max(0,round(x+(local_left-40)*sx)),min(1920,round(x+(local_left+40)*sx)));right=range(max(0,round(x+(local_right-40)*sx)),min(1920,round(x+(local_right+40)*sx)))
  if len(left) and len(right):
   lp=max(left,key=lambda c:scores[c]);rp=max(right,key=lambda c:scores[c]);confidence=float(min(scores[lp],scores[rp]))
   candidate=(rp-lp)/(local_right-local_left)
   if confidence>25 and .8*sx<candidate<1.2*sx:
    ps=candidate;px=lp-local_left*ps;lo=max(0,round(y+local_top*ps-18));hi=min(1080,round(y+local_top*ps+18));xx0=max(0,round(px+200*ps));xx1=min(1920,round(px+480*ps))
    if hi>lo and xx1>xx0:
     rows=shade[:,xx0:xx1].mean(1);py=max(range(lo,hi),key=lambda j:rows[j])-local_top*ps
 image=extended.resize((round(681*ps),round(1456*ps)),Image.Resampling.BILINEAR);canvas=Image.new('RGBA',(1920,1080),'white');canvas.alpha_composite(image,(round(px),round(py)));expected=np.array(canvas.convert('RGB'),float)
 bands=[]
 for lo in range(0,1080,32):
  hi=min(1080,lo+32);delta=255-expected[lo:hi];actual=255-source[lo:hi];opacity=float(np.clip((delta*actual).sum()/max((delta*delta).sum(),1),0,1));bands.append(((lo+hi)/2,opacity))
 alpha_y=np.interp(py+np.arange(extended.height)*1456/extended.height*ps,[b[0] for b in bands],[b[1] for b in bands]);rgba=np.array(extended).copy();rgba[:,:,3]=np.uint8(np.rint(rgba[:,:,3]*alpha_y[:,None]));rgba[:,:,:3][np.array(extended)[:,:,3]==0]=255
 if rgba[:,:,3].max()>0:
  asset=rim_dir/f'rim-{n}.png';Image.fromarray(rgba).save(asset);rim_layers.append({'id':f'root-rene-rim-pose-{n}','type':'image','src':str(asset),'width':681,'height':1456,'start':n/30,'end':(n+1)/30,'semanticText':'Physical phone hardware with measured vertical materialization','sourceFrame':n,'editability':'Original hardware color, measured generated opacity mask; no visible source UI pixels'})
 physical_records.append({'frame':n,'x':(px-x)/sx,'y':(py-y)/sy,'scaleX':ps/sx,'scaleY':ps/sy,'worldPose':[px,py,ps],'profileConfidence':confidence,'opacityBands':bands})
 records.append({'frame':n,'value':float(np.mean(alpha_y))})
 header_records.append({'frame':n,'x':(x-parent_x)/parent_sx,'y':(y-parent_y)/parent_sy,'scaleX':sx/parent_sx,'scaleY':sy/parent_sy,'opacity':header_alpha,'worldPose':[x,y,sx,sy]})
 box=blue_box(source)
 if box:
  bx0,by0,bx1,by1=box;roi=source[by0:by1,bx0:bx1];mask=(roi[:,:,2]-roi[:,:,0]>15)&(roi[:,:,2]>200)&(roi[:,:,1]>80);filled=ndimage.binary_fill_holes(mask);pixels=roi[mask].astype(np.uint8);colors,counts=np.unique(pixels,axis=0,return_counts=True);bg=colors[counts.argmax()]
  body=np.clip((255-roi[:,:,0])/(255-float(bg[0])),0,1);body[filled&~mask]=1.;d,stats=trace_alpha(body)
  blue_layers.append({'id':f'root-rene-yes-body-{n}','type':'path','d':d,'x':bx0,'y':by0,'fill':'#'+''.join(f'{v:02x}' for v in bg),'start':n/30,'end':(n+1)/30,'semanticText':'Yes plz','sourceFrame':n})
  alpha_text=np.clip((roi.mean(2)-float(bg.mean()))/(255-float(bg.mean())),0,1)*filled;d,stats=trace_alpha(alpha_text)
  blue_layers.append({'id':f'root-rene-yes-glyphs-{n}','type':'path','d':d,'x':bx0,'y':by0,'fill':'#FFFFFF','start':n/30,'end':(n+1)/30,'semanticText':'Yes plz','sourceFrame':n,'editability':'Native white glyph-outline pose; not live text'})
 # The camera island itself materializes with an independently measured shade.
 ix0=max(0,round(px+170*ps));ix1=min(1920,round(px+510*ps));iy0=max(0,round(py+20*ps));iy1=min(1080,round(py+125*ps))
 if ix1>ix0 and iy1>iy0:
  roi=source[iy0:iy1,ix0:ix1];mask=(roi.max(2)-roi.min(2)<35)&(roi.min(2)<235);labels,_=ndimage.label(mask,np.ones((3,3)));candidates=[]
  for i,sl in enumerate(ndimage.find_objects(labels)):
   if sl is None:continue
   yy,xx=sl;w,h=xx.stop-xx.start,yy.stop-yy.start
   if .6*194*ps<w<1.5*194*ps and .2*55*ps<h<1.8*55*ps:candidates.append((int((labels[sl]==i+1).sum()),sl))
  if candidates:
   _,sl=max(candidates,key=lambda c:c[0]);yy,xx=sl;pixels=roi[sl];values=roi[sl][mask[sl]].astype(np.uint8);colors,counts=np.unique(values,axis=0,return_counts=True);ink=colors[counts.argmax()];alpha_island=np.clip((255-pixels.mean(2))/(255-float(ink.mean())),0,1);d,stats=trace_alpha(alpha_island)
   blue_layers.append({'id':f'root-rene-camera-island-{n}','type':'path','d':d,'x':ix0+xx.start,'y':iy0+yy.start,'fill':'#'+''.join(f'{v:02x}' for v in ink),'start':n/30,'end':(n+1)/30,'semanticText':'Measured camera island materialization','sourceFrame':n})
proc.stdout.close();proc.wait()
device['children']=[c for c in device['children'] if c['id']!='g-1208']
backplate.setdefault('keyframes',{})['fill']=backplate_colors
header_items=device['children'];physical={'id':'root-rene-physical-material','type':'group','children':[backplate]+rim_layers,'keyframes':{p:[{'t':r['frame']/30,'value':r[p]} for r in physical_records] for p in ['x','y','scaleX','scaleY']}}
header={'id':'root-rene-native-header','type':'group','children':header_items,'keyframes':{'opacity':[{'t':r['frame']/30,'value':r['opacity']} for r in header_records]}}
device['children']=[{'id':'root-rene-header-camera','type':'group','children':[physical,header],'keyframes':{p:[{'t':r['frame']/30,'value':r[p]} for r in header_records] for p in ['x','y','scaleX','scaleY']}}]
patch['replacements']['g-1197']['children'].extend(blue_layers)
patch['provenance']['physicalOpacity']=records;patch['provenance']['hardwareExtension']={'original':str(original.size),'new':[681,1456],'originalTopPixelsPreserved':True,'purpose':'Continue straight transparent hardware rails beyond the cropped original; no source UI pixels are made visible.'}
patch['provenance']['headerCamera']=header_records;patch['provenance']['blueNativePoses']=len(blue_layers)
patch['provenance']['physicalCamera']=physical_records;patch['provenance']['physicalReveal']='Measured top-to-bottom opacity bands with an independent opaque screen backplate and native island poses.'
patch['provenance']['actualHardwareReference']={'sourceFrame':515,'crop':[596,80,1275,1080],'asset':str(actual_file),'intrinsicSize':[679,1451],'declaredSize':[681,1456],'note':'Actual scene metal colors inside the original hardware-only alpha mask. The UI interior is transparent and its latent RGB was removed.'}
(REF/'root-lock-physical-patch.json').write_text(json.dumps(patch,indent=2));print(json.dumps(records[::6]))
