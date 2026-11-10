"""Recover an editable grouped status pill and glyphs from the clean native rest."""
from pathlib import Path
import sys,json,importlib.util
import numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
P=Path(__file__).resolve().parent
image=np.array(Image.open(P/'early-entry-v17-source/005.png').convert('RGB')).astype(float)
left,top,right,bottom=600,380,930,485
rgb=image[top:bottom,left:right]
gray=rgb.mean(2)
mask=np.uint8((gray>150)&(gray<225)&(np.ptp(rgb,axis=2)<6))
number,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
index=1+np.argmax(stats[1:,cv2.CC_STAT_AREA])
contours,_=cv2.findContours(np.uint8(labels==index),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
filled=np.zeros(mask.shape,'uint8')
cv2.drawContours(filled,contours,-1,1,cv2.FILLED)
yy,xx=np.where(filled>0)
bbox=[int(xx.min()+left),int(yy.min()+top),int(xx.max()+1+left),int(yy.max()+1+top)]
background=np.median(rgb[(filled>0)&(gray>150)],axis=0)
foreground=float(np.percentile(gray[(filled>0)&(gray<100)],5))
alpha=np.clip((background.mean()-gray)/(background.mean()-foreground),0,1)*filled
spec=importlib.util.spec_from_file_location('trace',P.parent/'02-danieltian/trace_glyphs.py')
tracer=importlib.util.module_from_spec(spec);spec.loader.exec_module(tracer)
path,metadata=tracer.trace_alpha(alpha,x0=left,y0=top,threshold=.5)
file=P/'early-entry-v17-measurements.json';data=json.loads(file.read_text())
dim=.07936507936507942
data['native_working_reference']=dict(source_frame=215,bbox=bbox,source_background_rgb=background.tolist(),native_background_rgb=np.rint(background/(1-dim)).astype(int).tolist(),source_foreground=foreground,native_foreground=int(round(foreground/(1-dim))),path=path,metadata=metadata,notice='Native grouped incoming status pill has no tail once the following Mail card is present. The former static skin retained an obsolete tail and source motion blur. Native rounded material and semantic original glyph outlines replace only the six independently observed entry poses.')
file.write_text(json.dumps(data,indent=2)+'\n')
print('native working reference',bbox)
