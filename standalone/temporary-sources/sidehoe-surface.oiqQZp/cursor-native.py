from pathlib import Path
import hashlib,json,subprocess,sys,csv
import numpy as np
from scipy.ndimage import binary_dilation,label
base=Path(sys.argv[1]).resolve()
d=base/'review'/'focus'
paths={'source':Path('/Users/darshan/Downloads/sidehoe.mp4'),
       'previous':base.parent/'motion-review'/'candidate'/'sidehoe.mp4',
       'revised':base/'candidate'/'sidehoe.mp4'}
q=json.loads((base/'comparison-checks.json').read_text())
r=next(x for x in q['regions'] if x['id']=='follow-cursor-native-hull')
frames=range(r['start'],r['end']+1)
allbox=r['rects']
left=min(b[0] for b in allbox)
top=min(b[1] for b in allbox)
right=max(b[0]+b[2] for b in allbox)
bottom=max(b[1]+b[3] for b in allbox)
left-=left%2; top-=top%2
right+=right%2; bottom+=bottom%2
w,h=right-left,bottom-top
def decode(path):
 args=['ffmpeg','-nostdin','-v','error','-ss',f'{frames.start/25:.2f}','-i',str(path),'-an',
       '-vf',f'crop={w}:{h}:{left}:{top}', '-frames:v',str(len(frames)),'-pix_fmt','rgb24','-f','rawvideo','-']
 a=np.frombuffer(subprocess.check_output(args),dtype=np.uint8).reshape(-1,h,w,3)
 if len(a)!=len(frames): raise RuntimeError(f'Unexpected count in {path}')
 return a.astype(np.int16)
images=[decode(p) for p in paths.values()]
scene=json.loads((base/'project'/'scene.json').read_text())['followPointerOptics']
def masked_hull(image,x,y):
 mean=image.mean(axis=2)
 comps,_=label((mean<150)&(np.ptp(image,axis=2)<35))
 comp=comps[round(y),round(x)]
 if not comp:
    print('No dark cursor',x,y, file=sys.stderr)
    return None
 return comps==comp
rows=[]
for off,f in enumerate(frames):
 x0,y0,ww,hh=allbox[off]
 i,j=x0-left,y0-top
 source,old,new=(z[off,j:j+hh,i:i+ww] for z in images)
 x,y,width,height,*_=scene[str(f)]
 anchor=(2*(x+width*.27)-x0,2*(y+height*.44)-y0)
 actual=masked_hull(source,*anchor)
 if actual is None: continue
 region=binary_dilation(actual,iterations=6)
 result=[]
 for image in (old,new):
    curr=masked_hull(image,*anchor)
    full_mae=float(np.mean(np.abs(image-source)))
    local_mae=float(np.mean(np.abs(image-source)[region]))
    overlap=None
    if curr is not None:
       overlap=np.count_nonzero(actual&curr)/np.count_nonzero(actual|curr)
    result.extend([round(full_mae,4),round(local_mae,4),round(overlap,4) if overlap is not None else None])
 rows.append([f,f/25,int(region.sum()),*result])
if len(rows)!=len(frames):raise RuntimeError('Incomplete cursor measurements')
with (d/'cursor-frames.csv').open('w',newline='') as out:
 writer=csv.writer(out)
 writer.writerow(['frame','seconds','mask_pixels','previous_crop_mae','previous_cursor_mae','previous_contour_iou','revised_crop_mae','revised_cursor_mae','revised_contour_iou'])
 writer.writerows(rows)
readings=np.array(rows,float)
print('Source-derived cursor mask, all 26 decoded frames')
print('Mean columns',readings[:,3:].mean(axis=0))
print('Improved masks',len(readings[readings[:,4]>readings[:,7]]))
