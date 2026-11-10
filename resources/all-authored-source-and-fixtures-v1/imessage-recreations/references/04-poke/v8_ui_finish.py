"""Native component refinements from exact source/candidate ink and rail bounds."""
import json,copy
import numpy as np
from PIL import Image
from v8_utils import at,track,flat
FPS=30000/1001

def apply(scene,p):
    by={l['id']:l for l in scene['layers']}
    # At a clean scanline, physical screen edges are independent of chat motion.
    datafile=p/'measurements-v8/early-rail-fit.json'
    if datafile.exists():poses=json.loads(datafile.read_text())['measurements']
    else:
        poses=[]
        for n in range(264,481):
            a=np.array(Image.open(p/f'measurements-v8/decoded/{n:06}.png').convert('RGB'))[500];indices=np.where(a.max(1)<80)[0];runs=[]
            for x in indices:
                if runs and x==runs[-1][-1]+1:runs[-1].append(int(x))
                else:runs.append([int(x)])
            left=[v for v in runs if len(v)>4 and v[-1]<170];right=[v for v in runs if len(v)>4 and v[0]>1270]
            if not left or not right:continue
            lo=max(v[-1]for v in left)+1;hi=min(v[0]for v in right);s=(hi-lo)/1272
            poses.append(dict(frame=n,time=n/FPS,x=lo-92*s,scaleX=s))
        datafile.write_text(json.dumps({'method':'Exact source row500 independent left/right inner black rails; local native screen x92..1364.','measurements':poses},indent=2))
    for prop in ['x','scaleX']:track(by['p0109'],prop,poses)
    by['p0109']['end']=(poses[-1]['frame']+1)/FPS
    # Incoming text is fitted to native456 glyph spans, preserving native type.
    spot=next(c for c in by['p0146']['children']if c['type']=='text')
    spot.update(fontFamily='SF Pro Text',scaleX=.967,scaleY=1,y=30)
    where=next(c for c in by['p0155']['children']if c['type']=='text')
    where.update(scaleX=491/469,scaleY=56/57,y=29.86)
    title=next(c for c in by['p0135']['children']if c.get('text')=='Indian')
    title.update(scaleX=138/147,scaleY=40/41,y=42)
    sub=next(c for c in by['p0135']['children']if c.get('text')=='Selected option')
    sub.update(scaleX=330/338,scaleY=45/47,y=111.02)
    for c in by['p0135']['children'][:2]:c['fill']='#e6e6e6'
    # A compact early keyboard has shorter keys/pitch than the late capture.
    kb=by['p0220']
    for l in kb['children']:
        if l['type']=='rect' and l.get('fill')=='#ffffff':
            l['height']=140;l['radius']=22
        if l.get('y',0)>=345:l['y']-=16 if l['y']<537 else 32
    grad=copy.deepcopy(next(g for g in scene['gradients']if g['id']=='keyboard-native-gradient'))
    grad['id']='early-keyboard-native-gradient';grad['stops'][0]['color']='#dcdde2';grad['stops'][1]['color']='#e1e2e7'
    scene['gradients'].append(grad);kb['children'][0]['fill']='url(#early-keyboard-native-gradient)'
    # Source controls have a material fill and a shorter microphone than late28.
    comp=by['p0165'];mic=[]
    for l in list(comp['children']):
        if l['id'].endswith('p0364'):
            l['fill']='#f3f2f5';l['shadow']={'x':0,'y':18,'blur':35,'color':'#ededed'}
        if l['id'].endswith('p0363'):
            l['fill']='#f9f9f9';l['opacity']=.8
        if any(l['id'].endswith(code)for code in['p0368','p0369','p0370','p0371']):
            mic.append(l);comp['children'].remove(l)
    comp['children'].append(dict(id='v8-early-microphone',type='group',originX=1102,originY=27,scaleX=.9,scaleY=.72,children=mic))
    # Same measured frosted control material and microphone dimensions late.
    late=by['p0372'];mic=[]
    for l in list(late['children']):
        if l['id']=='p0364':l['y']=-19;l['height']=148;l['opacity']=.755;l['fill']='#f3f2f5';l['shadow']={'x':0,'y':18,'blur':35,'color':'#ededed'}
        if l['id']in['p0368','p0369','p0370','p0371']:mic.append(l);late['children'].remove(l)
    late['children'].append(dict(id='v8-late-microphone',type='group',originX=1102,originY=27,scaleX=.9,scaleY=.72,children=mic))
    return scene
