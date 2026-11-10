from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json
p=Path(__file__).parent

def phone_box(file):
    image=np.array(Image.open(file).convert('RGB'));mask=np.max(image,2)<95;labeled,number=ndimage.label(mask);choices=[]
    for label,box in enumerate(ndimage.find_objects(labeled),1):
        if box is None:continue
        y,x=box;w=x.stop-x.start;h=y.stop-y.start
        if w>300 and h>700 and 1.6<h/w<2.5:
            area=int((labeled[box]==label).sum());choices.append((area,(x.start,y.start,x.stop,y.stop)))
    return max(choices)[1]
old_scale=.639453125;old_x=704.21875;old_y=-37.859375
source=phone_box(p/'measured/24.5.png');candidate=phone_box(p/'combined-v8-check/24.5.png');ratio=(source[2]-source[0])/(candidate[2]-candidate[0]);new_scale=old_scale*ratio;new_x=source[0]-(candidate[0]-old_x)*ratio;new_y=source[3]-(candidate[3]-old_y)*ratio
result={'source_box':source,'candidate_box':candidate,'candidate_camera':{'scale':old_scale,'x':old_x,'y':old_y},'suggested_camera':{'scale':new_scale,'x':new_x,'y':new_y},'note':'Read-only proposal derived from the same bezel component. No frozen scene changed; inspect after current exported patch.'}
(p/'celebration-phone-proposal.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
