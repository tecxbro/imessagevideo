"""Extract only bounded white email-pane poses; leave device/backdrop native."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
P=Path(__file__).parent;B=P/'early-v13-measure';D=P/'assets/early-email-exit-v13';D.mkdir(exist_ok=True);records=[];thumbs=[]
for f in range(345,359):
 source=B/'exit-full'/f'{f-344:03d}.png';im=Image.open(source).convert('RGB');a=np.asarray(im);gray=a.mean(2);allowed=np.zeros(gray.shape,bool);allowed[:,650:1280]=True
 # Components remain separated from the device by its dark bezel. The modal
 # is the only large bright region while its independent backdrop is dimmed.
 labels,n=ndimage.label((a.min(2)>225)&allowed);sizes=np.bincount(labels.ravel());sizes[0]=0;label=int(sizes.argmax());mask=ndimage.binary_fill_holes(labels==label)
 ys,xs=np.where(mask);box=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1));assert box[2]-box[0]<800 and box[3]-box[1]<=1080
 # A one-pixel mask seam contains only the source pane, not bezel or chat.
 rgba=np.dstack([a,(mask*255).astype('uint8')]);out=Image.fromarray(rgba).crop(box);asset=D/f'frame-{f:04d}.png';out.save(asset)
 count=int(mask.sum());records.append({'source_frame':f,'source_time':f/30,'source_file':'source.mp4','bounds':list(box),'asset':str(asset.relative_to(P)),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'alpha_pixels':count,'minimum_dimension_margin_to_full_frame':min(1920-(box[2]-box[0]),1080-(box[3]-box[1])),'mask_method':'Largest bright modal-pane component within x650:1280; filled internal text holes, no dilation. Outside/bezel/backdrop remain transparent.','editability':'Original internal UI pixels and this short perspective deformation are bitmap; component position/lifetime/opacity plus native device/backdrop are independently editable.'})
 bg=Image.new('RGBA',out.size,'#d68be5');bg.alpha_composite(out);tile=Image.new('RGB',(240,300),'#ddd');bg.thumbnail((230,265));tile.paste(bg.convert('RGB'),((240-bg.width)//2,30));ImageDraw.Draw(tile).text((6,8),str(f)+' '+str(box),fill='black');thumbs.append(tile)
contact=Image.new('RGB',(240*7,300*2),'#ddd')
for i,tile in enumerate(thumbs):contact.paste(tile,((i%7)*240,(i//7)*300))
contact.save(B/'exit-texture-contact.jpg');(B/'email-exit-artwork-provenance.json').write_text(json.dumps({'records':records,'source_sha256':hashlib.sha256((P/'source.mp4').read_bytes()).hexdigest(),'authorization':'Parent explicitly authorized bounded per-pane textures for the short local perspective exit, following source01 local3Dcard precedent. Frame358 is the final tiny visible pane; source359 has none. No fullframe/video layer.'},indent=2)+'\n');print([(r['source_frame'],r['bounds'],r['alpha_pixels'])for r in records])
