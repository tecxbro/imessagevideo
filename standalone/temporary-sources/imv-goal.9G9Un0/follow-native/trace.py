import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

work=Path(__file__).parent
project=work.parent/'sidehoe-clean-project'
sys.path.insert(0,str(project))
import render

scene=json.loads((project/'scene.json').read_text())
film=render.Film(scene)
frames=range(672,698)
labels=('source','pre2000','encoded')
read=lambda label,f: np.asarray(Image.open(work/label/f'{f:06d}.png').convert('RGB'))

def trace(f, replacement=None):
    record={}
    original_cursor, original_expose=render.cursor,film.expose_phone
    def capture_cursor(im,x,y,r,opacity,size):
        record.update(cursorPivot=[round(2*x,4),round(2*y,4)],cursorAngle=r,cursorOpacity=opacity,cursorScale=size)
        isolated=render.layer()
        original_cursor(isolated,x,y,r,opacity,size)
        record['isolated']=np.asarray(isolated.getchannel('A'))
        if replacement is None:
            original_cursor(im,x,y,r,opacity,size)
        else:
            nx, ny=replacement
            original_cursor(im,nx,ny,r,opacity,size)
    def capture_expose(im,plate,x,y,scale,smear,radius,alpha=1):
        record.update(railOuter=[2*x,2*(x+plate.width*scale)],phoneTop=2*y,phoneScale=scale,phoneSmear=smear,phoneBlur=radius)
        return original_expose(im,plate,x,y,scale,smear,radius,alpha)
    try:
        render.cursor,film.expose_phone=capture_cursor,capture_expose
        frame=film.frame(f)
    finally:
        render.cursor,film.expose_phone=original_cursor,original_expose
    if 'railOuter' in record:
        x,y,s=film.track('followMeasuredCamera',f)
        shift,=film.track('followChipOffset',f)
        left,top,w,h=scene['followContact']['yesRect']
        record['yesBounds']=[2*(x+left*s),2*(y+(top+shift)*s),2*(x+(left+w)*s),2*(y+(top+shift+h)*s)]
    return frame,record

if __name__=='__main__':
    masks=work/'mask'
    masks.mkdir(exist_ok=True)
    state={}
    for f in frames:
        im, row=trace(f)
        before=Image.open(work.parent/'sidehoe-clean-frames'/f'{f:06d}.png').convert('RGB')
        assert np.array_equal(np.asarray(im),np.asarray(before)),f
        if 'isolated' in row:
            Image.fromarray(row.pop('isolated')).save(masks/f'{f:06d}.png')
        state[f]=row
    (work/'evaluated.json').write_text(json.dumps(state,indent=2)+'\n')
