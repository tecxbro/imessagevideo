"""Correct false panel fading from flat visible material, preserving pulse pixels."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
D = Path(__file__).resolve().parent
ROOT = D.parent.parent
OUT = D/'root-cash-plane-v20'

def find(layers, identity):
    for layer in layers:
        if layer['id']==identity:return layer
        result=find(layer.get('children',[]),identity)
        if result is not None:return result

def prepare():
    scene_path=ROOT/'outputs/05-linq/final-v19/scene.json'
    scene=json.loads(scene_path.read_text());panel=find(scene['layers'],'v10-cash-panel');layer=find(panel['children'],'v10-cash-panel-ui')
    rgba=np.asarray(Image.open(scene_path.parent/layer['src']).convert('RGBA'))
    gray=rgba[:,:,:3].mean(2).astype(float)
    yy,xx=np.mgrid[:rgba.shape[0],:rgba.shape[1]]
    mask=(gray<25)&(rgba[:,:,3]==255)&(xx>20)&(xx<rgba.shape[1]-20)&(yy>20)&(yy<rgba.shape[0]-20)
    mask &= ~((xx+182>=605)&(xx+182<=720)&(yy+230>=330)&(yy+230<=460))
    sy,sx=np.where(mask);sy,sx=sy[::11],sx[::11]
    ypos=panel['keyframes']['y'];alpha=panel['keyframes']['opacity'];rows=[]
    for frame in range(773,838):
        py=float(np.interp(frame/30,[k['t']for k in ypos],[k['value']for k in ypos]))
        old=float(np.interp(frame/30,[k['t']for k in alpha],[k['value']for k in alpha]))
        path=D/'measurements/composer-v19/native'/f'source-{frame:06}.png'
        if not path.exists():path=D/'measurements/native-transition'/f'{frame:06}.png'
        source=np.asarray(Image.open(path).convert('RGB')).mean(2)
        wy=sy+round(layer['y']+py);wx=sx+round(layer['x'])
        valid=(wy>=0)&(wy<720)&(wx>=0)&(wx<960)
        observed=source[wy[valid],wx[valid]];material=gray[sy[valid],sx[valid]]
        keep=observed<50
        observed,material=observed[keep],material[keep]
        if len(observed)>=100:
            bins=np.arange(256,dtype=np.int32)
            raw=np.rint(material).astype(np.int32)
            predicted=(255-bins)[None,:]+(raw[:,None]*bins[None,:])//255
            costs=np.mean(np.abs(predicted-observed[:,None]),axis=0)
            old_bin=round(old*255)
            best=int(costs.argmin())
            if costs[old_bin]<=costs[best]+1e-9:best=old_bin
            estimated=old if best==old_bin else best/255
        else:
            estimated=old
        rows.append({'frame':frame,'old':old,'value':estimated,'samples':len(observed),'sourceMedian':float(np.median(observed)) if len(observed)else None,'materialMedian':float(np.median(material)) if len(material)else None})
    OUT.mkdir(exist_ok=True)
    (OUT/'measurements.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps([row for row in rows if row['frame']in [773,774,780,820,827,828,829,830,831,832,833,834,835,836,837]],indent=2),flush=True)

def apply_cash_plane(scene):
    panel=find(scene['layers'],'v10-cash-panel')
    rows=json.loads((OUT/'measurements.json').read_text());table={row['frame']:row for row in rows}
    for key in panel['keyframes']['opacity']:
        frame=round(key['t']*30)
        if frame in table:key['value']=table[frame]['value']
    control=find(panel['children'],'root-cash-native-control-v19')
    if control is None:raise ValueError('Expected already accepted native pulse')
    for actor in control['children']:
        for name in ['fill','stroke']:
            for key in actor.get('keyframes',{}).get(name,[]):
                frame=round(key['t']*30);row=table[frame]
                color=int(key['value'][1:3],16)
                displayed=row['old']*color+(1-row['old'])*255
                old_bin=round(row['old']*255);new_bin=round(row['value']*255)
                target=255-old_bin+(color*old_bin)//255
                choices=np.arange(256,dtype=np.int32)
                predicted=255-new_bin+(choices*new_bin)//255
                errors=np.abs(predicted-target)
                candidates=choices[errors==errors.min()]
                local=int(candidates[np.abs(candidates-color).argmin()])
                key['value']='#'+f'{local:02x}'*3
    return scene

if __name__=='__main__':prepare()
