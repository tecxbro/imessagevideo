"""Recover authentic tile artwork from complementary visible source crops."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
p=Path(__file__).parent;im=Image.open(p/'native/39.0.png').convert('RGB');a=p/'assets';rows=[]
def combine(name,leftbox,rightbox,offset):
 left=im.crop(leftbox);right=im.crop(rightbox);ar=np.asarray(left).astype(float);br=np.asarray(right).astype(float);overlap=left.width-offset
 error=float(np.mean(np.abs(ar[:,offset:]-br[:,:overlap])))
 out=Image.new('RGBA',(225,225),(255,255,255,0));out.paste(left,(0,0));cut=offset+overlap//2
 out.paste(right.crop((max(0,cut-offset),0,right.width,right.height)),(cut,0));mask=Image.new('L',(225,225),0);ImageDraw.Draw(mask).rounded_rectangle((0,0,224,224),radius=54,fill=255);out.putalpha(mask);file=a/f'brand-{name}-auth-composite.png';out.save(file)
 rows.append({'asset':str(file.relative_to(p)),'source_time':39,'source_frame':1169,'left_crop':leftbox,'right_crop':rightbox,'right_paste_x':offset,'overlap_mae_rgb':error,'purpose':'Complementary visible halves of the SAME static logo, stitched in overlap; no complete video frame used.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
combine('spiral',(1286,564,1440,789),(0,292,155,517),70)
combine('outlook',(1286,836,1440,1061),(0,564,147,789),78)
def partial(name,box,paste):
 crop=im.crop(box);out=Image.new('RGBA',(225,225),(0,0,0,0));out.paste(crop,paste);file=a/f'brand-{name}-auth-partial.png';out.save(file);rows.append({'asset':str(file.relative_to(p)),'source_time':39,'source_frame':1169,'source_crop':box,'paste':paste,'purpose':'Authentic visible pixels only; transparent unknown columns preserve underlying native fallback during entry. Rest/zoom visible portion uses source artwork.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
partial('netlify',(0,836,147,1061),(78,0));partial('strava',(1285,21,1440,246),(0,0))
(a/'grid-artwork-provenance.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
preview=Image.new('RGB',(900,250),'#ddd')
for i,row in enumerate(rows):preview.paste(Image.open(p/row['asset']),(i*225,15),Image.open(p/row['asset']))
preview.save(a/'grid-artwork-preview.png')
