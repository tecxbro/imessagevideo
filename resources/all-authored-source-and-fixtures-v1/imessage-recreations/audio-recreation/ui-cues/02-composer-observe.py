#!/usr/bin/env python3
"""Observe native composer frames; OCR is evidence, not an assumed keystroke clock."""
from pathlib import Path
from io import BytesIO
import json,subprocess
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
frames=list(range(90,175));w,h=1280,275
command=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(ROOT/'references/02-danieltian/source.mp4'),'-vf',"select='between(n,90,174)',format=rgb24,crop=1280:275:260:400",'-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-']
producer=subprocess.Popen(command,stdout=subprocess.PIPE)
records=[];sheets={0:Image.new('RGB',(640*4,166*11),'#e7e7e7'),1:Image.new('RGB',(640*4,166*11),'#e7e7e7')}
for index,n in enumerate(frames):
 raw=producer.stdout.read(w*h*3)
 if len(raw)!=w*h*3:raise RuntimeError(f'Incomplete native frame{n}')
 rgb=np.frombuffer(raw,np.uint8).reshape(h,w,3)
 gray=rgb.mean(2);neutral=(rgb.max(2).astype(int)-rgb.min(2).astype(int)<18)
 ink=neutral&(gray<165)
 ocr=Image.fromarray(np.uint8(~ink)*255,'L')
 buffer=BytesIO();ocr.save(buffer,format='PNG')
 result=subprocess.run(['tesseract','stdin','stdout','--psm','6','--oem','1','-l','eng'],input=buffer.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout.decode().strip()
 labels,_=ndimage.label(ink,np.ones((3,3)))
 carets=[]
 for label,sl in enumerate(ndimage.find_objects(labels),1):
  if sl is None:continue
  yy,xx=sl
  if 1<=xx.stop-xx.start<=9 and yy.stop-yy.start>=35:
   carets.append({'bounds':[int(xx.start+260),int(yy.start+400),int(xx.stop+260),int(yy.stop+400)],'width':xx.stop-xx.start,'height':yy.stop-yy.start,'ink_pixels':int(np.count_nonzero(labels[sl]==label))})
 records.append({'frame':n,'time':n/30,'ocr_raw':result,'tall_narrow_components':carets,'ink_pixels':int(ink.sum())})
 sheetindex = 0 if index < 44 else 1;local=index if index<44 else index-44;sheet=sheets[sheetindex];x=(local%4)*640;y=(local//4)*166
 sheet.paste(Image.fromarray(rgb).resize((640,138)),(x,y));ImageDraw.Draw(sheet).text((x+8,y+142),f'{n}: {result.replace(chr(10)," / ")[:68]}',fill='black')
producer.stdout.close();assert producer.wait()==0
(OUT/'02-composer-ocr.json').write_text(json.dumps({'source':'references/02-danieltian/source.mp4','roi':[260,400,1540,675],'fps':30,'records':records,'limitations':'OCR and connected-component caret candidates require manual/prefix consistency review; no raw OCR string is automatically treated as a keystroke.'},indent=2)+'\n')
for index,sheet in sheets.items():sheet.save(OUT/f'02-composer-native-{index}.jpg',quality=91)
print(json.dumps({'frames':len(records),'nonblank_ocr':sum(bool(r['ocr_raw'])for r in records),'ocr':[(r['frame'],r['ocr_raw'])for r in records]},ensure_ascii=False))
