from pathlib import Path
from hashlib import file_digest
import json, subprocess
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

out=Path('sidehoe-skill-trial/finish/focus')
out.mkdir(exist_ok=False)
base=Path('/tmp/imv-goal.9G9Un0/sidehoe-glyph-final-export/sidehoe.mp4')
target=Path('sidehoe-skill-trial/finish/sidehoe.mp4')
source=Path('/Users/darshan/Downloads/sidehoe.mp4')
paths=(source,base,target)

def decode(path, first, last, xyxy):
    x0,y0,x1,y1=xyxy
    w,h=x1-x0,y1-y0
    graph=rf'select=between(n\,{first}\,{last}),format=rgb24,crop={w}:{h}:{x0}:{y0}:exact=1'
    output=subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(path),'-an','-filter_threads','1',
                           '-vf',graph,'-fps_mode','passthrough','-threads','1','-f','rawvideo','-'],
                          capture_output=True,check=True).stdout
    return np.frombuffer(output,np.uint8).reshape(last-first+1,h,w,3)

def sheet(tag, images, frame_first, index_start=0, count=8):
    rows,cols=len(images),count
    preview=(146,182)
    w,h=preview
    image=Image.new('RGB',(w*cols,(h+16)*rows),'#15212a')
    d=ImageDraw.Draw(image)
    for row,(name,frames) in enumerate(zip(('Source','Prior','Revised'),images)):
        for col,i in enumerate(range(index_start,index_start+count)):
            if i>=len(frames): continue
            frame=Image.fromarray(frames[i]); frame.thumbnail(preview)
            x,y=col*w,row*(h+16)
            image.paste(frame,(x,y+16));d.text((x+2,y+2),f'{name} {frame_first+i}',fill='white')
    image.save(out/f'{tag}.png')

def stats(image, expected):
    # Localize the independently drawn black core in its contact neighborhood.
    ex,ey=expected
    x0,y0=max(0,round(ex)-35),max(0,round(ey)-45)
    ex2,ey2=min(image.shape[1],round(ex)+170),min(image.shape[0],round(ey)+210)
    data=image[y0:ey2,x0:ex2].mean(2)
    cutoff=170 if active_frame==695 else 105
    regions,_=ndimage.label(data<cutoff,structure=np.ones((3,3)))
    choices=[]
    for tag,bounds in enumerate(ndimage.find_objects(regions),1):
        if bounds is None: continue
        yy,xx=bounds
        mask=regions[yy,xx]==tag
        if mask.sum()<75 or np.ptp(xx.indices(data.shape[1])[:2])<10: continue
        j,i=np.where(mask)
        level=yy.start+y0
        x=xx.start+x0+float(np.median(i[j==0]))
        dist=((ex-x)**2+(ey-level)**2)**.5
        if dist<48 and yy.stop-yy.start>14:
            choices.append((dist,[round(x+830,1),int(level+975),int(mask.sum())]))
    return min(choices,default=(0,None))[1]

result={'tile':[],'cursor':[]}
tile_roi=(742,1110,1245,2000)
frames=[decode(path,612,623,tile_roi) for path in paths]
for n,(a,b,c) in enumerate(zip(*frames),612):
    rows=[]
    for im in (a,b,c):
        r,g,blue=im.astype(np.int16).transpose(2,0,1)
        mask=(blue-r>48)&(g-r>20)&(blue-g>12)&(r<190)
        rows.append(int(mask.sum()))
    result['tile'].append({'frame':n,'blue_pixels':rows})
sheet('tile-612-617',frames,612,count=6)
sheet('tile-618-623',frames,612,index_start=6,count=6)
cursor_roi=(830,975,1143,1315)
plates=[decode(path,670,695,cursor_roi) for path in paths]
scene=json.loads(Path('sidehoe-skill-trial/finish/project/scene.json').read_text())
for active_frame,*fields in scene['tracks']['followPointerStage']:
    i=active_frame-670
    expected=2*fields[0]-830,2*fields[1]-975
    result['cursor'].append({'frame':active_frame,'dark_tip_and_area':[stats(frames[i],expected) for frames in plates]})
for start in (0,7,14,21):
    sheet(f'cursor-{670+start}',plates,670,index_start=start,count=min(7,26-start))
result['order']=['source','prior','revised']
for path in paths:
    with path.open('rb') as f: result[path.name if path==source else ('prior_sha256' if path==base else 'candidate_sha256')]=file_digest(f,'sha256').hexdigest()
(out/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')
print('f621 blue pixels',result['tile'][-3])
for i in [2,5,13,22,23,24,25]: print(result['cursor'][i])
