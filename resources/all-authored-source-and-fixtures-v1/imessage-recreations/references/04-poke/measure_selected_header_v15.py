"""Native chroma registration of selected restaurant thumbnail, with control fit."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
p=Path(__file__).parent;root=p.parent.parent;fps=30000/1001
im=Image.open(p/'assets/zareen-card-photo.png').convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);template=np.array(bg.convert('RGB').resize((71,72),Image.Resampling.LANCZOS)).astype(np.float32);tf=np.maximum(template[:,:,0]-template[:,:,2],0);rows=[]
for n in[734,737,740,743,746,749,752,755,758,760,761,762,765,769,773]:
    row=dict(frame=n,time=n/fps)
    for role,file in[('source',p/f'measurements-v8/decoded/{n:06}.png'),('control',root/f'outputs/04-poke/cache-history/v13/gsap/{n:06}.png')]:
        a=np.array(Image.open(file).convert('RGB')).astype(np.float32);x0,y0,x1,y1=620,170,810,440;f=np.maximum(a[y0:y1,x0:x1,0]-a[y0:y1,x0:x1,2],0);corr=cv2.matchTemplate(f,tf,cv2.TM_CCORR_NORMED);_,score,_,point=cv2.minMaxLoc(corr);x,y=point;patch=f[y:y+tf.shape[0],x:x+tf.shape[1]];alpha=float((patch*tf).sum()/max(1,(tf*tf).sum()));row[role]=dict(photo_x=x+x0,photo_y=y+y0,normalized_correlation=float(score),chroma_amplitude=alpha,positive_source_pixels=int((patch>3).sum()))
    rows.append(row);print(row,flush=True)
(p/'measurements-v8/selected-header-chroma-v15.json').write_text(json.dumps(dict(method='Positive red-minus-blue chroma of the genuine static photo, native71x72projection;2Dnormalized correlation. Candidate/control should recover its actual681.5,323.5photo pose when actor is visible; all results are hypotheses until this control and occlusion are inspected.',measurements=rows),indent=2))
