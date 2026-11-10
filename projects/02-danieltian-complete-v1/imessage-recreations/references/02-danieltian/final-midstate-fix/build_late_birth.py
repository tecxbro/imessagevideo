from pathlib import Path
import sys,json,copy,numpy as np
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
from scipy import ndimage
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from trace_glyphs import trace_alpha
R=Path(__file__).resolve().parent
extra=json.loads((R/'birth-extra-source/mapping.json').read_text())
def source(frame):
    path=Path(extra[str(frame)])if str(frame)in extra else R/'source-native'/f'source-{frame:04d}.png'
    return np.asarray(Image.open(path).convert('RGB')).astype(float)
def component(image):
    part=image[400:1080,1200:1800]
    mask=(part[:,:,2]-part[:,:,0]>18)&(part[:,:,1]-part[:,:,0]>8)
    labels,count=ndimage.label(mask)
    sizes=np.bincount(labels.ravel());sizes[0]=0
    if sizes.max()<10:return None
    yy,xx=np.nonzero(labels==sizes.argmax())
    return[int(xx.min()+1200),int(yy.min()+400),int(xx.max()+1201),int(yy.max()+401)]
reference=source(919)
left,top,right,bottom=component(reference)
width,height=right-left,bottom-top
crop=reference[top:bottom,left:right]
outer=(crop[:,:,2]-crop[:,:,0]>18)&(crop[:,:,1]-crop[:,:,0]>8)
outer=ndimage.binary_fill_holes(outer)
core=ndimage.binary_erosion(outer,iterations=3)
colors=np.zeros((height,3))
for row in range(height):
    if core[row].any():colors[row]=np.median(crop[row][core[row]],axis=0)
    else:colors[row]=np.nan
for channel in range(3):
    good=np.isfinite(colors[:,channel]);colors[:,channel]=np.interp(np.arange(height),np.nonzero(good)[0],colors[good,channel])
alpha=np.clip((253-crop[:,:,0])/np.maximum(1,253-colors[:,0,None]),0,1)
alpha[~outer]=0
alpha[core]=1
path,trace=trace_alpha(alpha,threshold=.5)
# Fit a smooth, editable source blue gradient rather than storing coded texture/noise.
y=np.arange(5,82)
coefficients=np.array([np.polyfit(y,colors[y,channel],1)for channel in range(3)])
def color_at(value):
    rgb=np.clip(coefficients[:,0]*value+coefficients[:,1],0,255).round().astype(int)
    return'#'+''.join(f'{v:02x}'for v in rgb)
gradient={'id':'late-birth-source-blue','type':'linear','x1':'0%','y1':'0%','x2':'0%','y2':'100%','stops':[{'offset':'0%','color':color_at(0)},{'offset':f'{92/height*100:.6f}%','color':color_at(92)},{'offset':'100%','color':color_at(92)}]}
# Source dot interiors separate clearly from the smooth row gradient.
difference=np.linalg.norm(crop-colors[:,None,:],axis=2)
mask=(difference>14)&core
mask[:24]=False;mask[72:]=False;mask[:,:25]=False;mask[:,155:]=False
mask=ndimage.binary_closing(mask,iterations=1)
labels,count=ndimage.label(mask)
objects=[]
for label,box in enumerate(ndimage.find_objects(labels),1):
    if box is None:continue
    yy,xx=box
    area=int((labels[box]==label).sum())
    if area>40:objects.append({'bounds':[xx.start,yy.start,xx.stop,yy.stop],'area':area,'center':[(xx.start+xx.stop)/2,(yy.start+yy.stop)/2]})
dots=[]
for target in[52,88,124]:
    dot=min(objects,key=lambda item:abs(item['center'][0]-target))
    assert abs(dot['center'][0]-target)<10
    dots.append(dot)
frames=[]
for frame in range(894,913):
    box=component(source(frame))
    if frame<901:assert box is None
    if not(901<=frame<=911):continue
    assert box
    l,t,r,b=box
    sx=(r-l)/width;sy=(b-t)/height
    children=[{'id':f'late-birth-body-{frame}','type':'path','d':path,'fill':'url(#late-birth-source-blue)','semanticText':'Outgoing typing bubble','sourceFrame':919,'editability':'Measured native vector bubble/tail silhouette with smooth editable blue gradient; no bitmap/frame playback.'}]
    image=source(frame)
    for index,dot in enumerate(dots):
        x0,y0,x1,y1=dot['bounds'];cx=l+dot['center'][0]*sx;cy=t+dot['center'][1]*sy;radius=max(.6,min((x1-x0)*sx,(y1-y0)*sy)*.24)
        yy,xx=np.mgrid[max(0,int(cy-radius)):min(1080,int(cy+radius+1)),max(0,int(cx-radius)):min(1920,int(cx+radius+1))]
        pixels=image[yy,xx][(xx-cx)**2+(yy-cy)**2<=radius**2]
        if not len(pixels):pixels=image[int(round(cy)),int(round(cx))][None,:]
        rgb=np.median(pixels,axis=0).round().astype(int)
        children.append({'id':f'late-birth-dot-{frame}-{index}','type':'circle','x':x0,'y':y0,'width':x1-x0,'height':y1-y0,'fill':'#'+''.join(f'{v:02x}'for v in rgb)})
    frames.append({'id':f'late-birth-native-pose-{frame}','type':'group','x':l,'y':t,'scaleX':sx,'scaleY':sy,'start':frame/30,'end':(frame+1)/30,'sourceFrame':frame,'sourceBounds':box,'children':children})
spec={'base':'outputs/02-danieltian/final-v15/scene.json','changedFrames':list(range(901,912)),'gradient':gradient,'layer':{'id':'late-birth-outgoing-typing-901-911','type':'group','start':901/30,'end':912/30,'children':frames},'measurement':{'canonicalSourceFrame':919,'canonicalSourceBounds':[left,top,right,bottom],'canonicalTrace':trace,'canonicalDotBounds':dots,'trueBirthFrame':901,'absentNativeControls':[894,895,896,897,898,899,900],'firstExistingRootNativeFrame':912,'method':'One bounded semantic native vector silhouette + native smooth blue gradient and three independently colored circles. Every native entrance pose measured from original source; no complete-frame image/video actor.'}}
(R/'late-birth-elements-candidate.json').write_text(json.dumps(spec,separators=(',',':')))
print(json.dumps(spec['measurement'],indent=2));print('gradient',gradient)
