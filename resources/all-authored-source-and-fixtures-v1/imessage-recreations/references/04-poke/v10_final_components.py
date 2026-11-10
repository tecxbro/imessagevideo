"""Native type, separate intro header camera and measured early map entry."""
import json,numpy as np
from PIL import Image
from v8_utils import at,track,flat

def apply(scene,p):
    by={l['id']:l for l in scene['layers']};lookup={l['id']:l for l in flat(scene['layers'])};fps=scene['fps']
    for r in json.loads((p/'measurements-v8/connected-type-fit-v10.json').read_text())['measurements']:
        for prop in['x','y','scaleX','scaleY']:lookup[r['id']][prop]=r[prop]
    ledger=json.loads((p/'measurements-v8/intro-header-v10-parent.json').read_text());ref=ledger['reference_native_ink_bbox'];poses=[]
    for r in ledger['records']:
        if not r.get('title'):continue
        b=r['title']['bbox'];scale=(b[2]-b[0])/(ref[2]-ref[0]);poses.append(dict(time=r['time'],x=b[0]-ref[0]*scale,y=b[3]-ref[3]*scale,scaleX=scale,scaleY=scale))
    header=by['v8-inbox-header'];header['start']=poses[0]['time']
    for prop in['x','y','scaleX','scaleY']:track(header,prop,poses)
    # Old pre109opacity sampled only AAedges, missing the now-solid glyph core.
    ui=by['v8-inbox-rows'];old=json.loads((p/'measurements-v8/intro-ui-fit.json').read_text())['measurements'];poses=[]
    for r in old:
        if r['frame']<98 or not r.get('name_ink_bbox'):continue
        b=r['name_ink_bbox'];a=np.array(Image.open(p/f"measurements-v8/decoded/{r['frame']:06}.png").convert('RGB'));c=a[b[1]:b[3],b[0]:b[2]].astype(float);gray=c.mean(2);opacity=float(np.clip(1-np.percentile(gray,10)/255,0,1));pose=dict(time=r['time'],opacity=opacity,**{prop:at(ui,prop,r['time'])for prop in['x','y','scaleX','scaleY']})
        if r['frame']<=108 and b[2]-b[0]>300:
            scale=(b[2]-b[0])/253;pose.update(x=b[0]-455*scale,y=b[1]-688*scale,scaleX=scale,scaleY=scale)
        poses.append(pose)
    for prop in['x','y','scaleX','scaleY','opacity']:track(ui,prop,poses)
    # Distinct orangePOI marks the map's own entry camera, not the footer's
    # threshold bounds. Its729partial circle is bottom-occluded by the composer.
    ledger=json.loads((p/'measurements-v8/map-entry-v10-parent.json').read_text());poses=[dict(time=728/fps,x=460,y=884,scaleX=1,scaleY=1),dict(time=729/fps,x=460,y=732,scaleX=1,scaleY=1)]
    for r in ledger['records']:
        if r.get('source_main'):
            t=r['source_main']['raw_asset_transform'];poses.append(dict(time=r['time'],**t))
    g=by['p0300'];g['start']=728/fps
    for prop in['x','y','scaleX','scaleY']:track(g,prop,poses)
    scene['gradients'].append(dict(id='small-header-glass-v10',type='linear',x1='0%',y1='0%',x2='0%',y2='100%',stops=[dict(offset='0%',color='#ffffff',opacity=1),dict(offset='65%',color='#ffffff',opacity=.75),dict(offset='100%',color='#ffffff',opacity=0)]))
    by['p0298']['children'].insert(0,dict(id='v10-small-header-glass',type='rect',x=-24,y=0,width=920,height=227,fill='url(#small-header-glass-v10)'))
    return scene
