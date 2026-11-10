from pathlib import Path
import json,sys,numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from trace_glyphs import trace_alpha
R=Path(__file__).resolve().parent
labels={q['frame']:q for q in json.loads((R/'label-measurements.json').read_text())['rows']}
result=[]
for frame in range(812,840):
    source=np.asarray(Image.open(R/'source-native'/f'source-{frame:04d}.png').convert('RGB')).astype(float)
    bounds=labels[frame]['matchedGlyphBounds']
    left=max(480,int(bounds[0]-40))
    top=int(bounds[3]+8)
    right=min(790,left+280)
    bottom=min(1080,top+170)
    crop=source[top:bottom,left:right]
    ink=np.clip(253-crop.mean(2),0,253)
    monochrome=(crop.max(2)-crop.min(2))<12
    mask=(ink>2)&monochrome
    lab,count=ndimage.label(mask)
    sizes=np.bincount(lab.ravel())
    sizes[0]=0
    if sizes.max()<10:continue
    component=ndimage.binary_dilation(lab==sizes.argmax(),iterations=1)
    ink*=component
    if bottom==1080 and np.any(component[-1]):
        ink=np.pad(ink,((0,4),(0,0)),mode="edge")
        crop=np.pad(crop,((0,4),(0,0),(0,0)),mode="edge")
    children=[]
    levels=[1,3,5,7,9,11,13,15,17,19,21,23,28,38,48,58,68,78,88,98,108,118]
    for index,level in enumerate(levels):
        contour,meta=trace_alpha(ink,threshold=level)
        if not contour:continue
        following=levels[index+1]if index+1<len(levels)else 254
        pixels=crop[(ink>=level)&(ink<following)]
        if len(pixels):color=np.median(pixels,axis=0).round().astype(int)
        else:color=np.array([253-level]*3)
        children.append({'id':f'post-v14-typing-{frame}-shade-{index}','type':'path','d':contour,'fill':'#'+''.join(f'{int(v):02x}'for v in color),'sourceInkLevel':level})
    result.append({'id':f'post-v14-typing-native-{frame}','type':'group','x':left,'y':top,'start':frame/30,'end':(frame+1)/30,'semanticText':'Airbnb typing indicator','sourceFrame':frame,'sourceBounds':[left,top,right,bottom],'editability':'Native measured vector bubble outline, tail and three dot phases; contours editable, no bitmap source frame.','children':children})
(R/'typing-elements.json').write_text(json.dumps(result,separators=(',',':')))
print('native typing states',len(result),'paths',sum(len(n['children'])for n in result))
