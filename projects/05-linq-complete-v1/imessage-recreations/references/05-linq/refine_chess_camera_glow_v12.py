from pathlib import Path
import json,copy
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;F=D/'measurements/native-transition';s=json.loads((D/'scene-chess-art-tap-v12.json').read_text());board=next(q for q in s['layers'] if q['id']=='broad-v5-group-41');keys=board['keyframes']['x'];by={round(k['t']*30):k for k in keys};base=np.array(Image.open(board['children'][0]['src']).convert('RGB')).astype(float);dimrows=json.loads((D/'chess-v12-measurements.json').read_text())['dim'];dimBy={p['frame']:p['opacity'] for p in dimrows};poses=[]
# Camera is the already measured settled-grid correlation from the art helper.
poses=[dict(frame=f,x=k['value'],previous=k['value']) for f,k in sorted(by.items())]
# Glow is its own native radial emission above the dimming scrim; the source
# grows from the original cyan orb into a yellow halo after the win.
stops=[dict(offset='0%',color='#efff91',opacity=.67),dict(offset='24%',color='#efff91',opacity=.67),dict(offset='40%',color='#fffc3c',opacity=.55),dict(offset='60%',color='#ffe837',opacity=.42),dict(offset='82%',color='#ffdc2d',opacity=.13),dict(offset='100%',color='#ffdc2d',opacity=0)]
s.setdefault('gradients',[]).append(dict(id='v12-ai-victory-emission',type='radial',stops=stops));R=90.;cx=426.;cy=46.;yy,xx=np.mgrid[0:140,330:520];rr=np.hypot(xx-cx,yy-cy)/R;offset=np.array([0,.24,.4,.6,.82,1]);colors=np.array([[239,255,145],[239,255,145],[255,252,60],[255,232,55],[255,220,45],[255,220,45]],float);alphas=np.array([.67,.67,.55,.42,.13,0]);glowA=np.interp(rr,offset,alphas);glowRGB=np.stack([np.interp(rr,offset,colors[:,i]) for i in range(3)],2);track=[]
for f in range(898,947):
 source=np.array(Image.open(F/f'{f:06}.png').convert('RGB')).astype(float);x=by[f]['value'];xi=np.clip(np.rint(xx+x).astype(int),0,959);target=source[yy,xi];dim=dimBy.get(f,dimrows[-1]['opacity']);b=base[yy,np.minimum(xx,483)]*(1-dim);b[xx>=484]=255;direction=(glowRGB-b)*glowA[:,:,None];mask=(xx+x>=0)&(xx+x<960)&(rr<.98);num=np.sum((target-b)[mask]*direction[mask]);den=np.sum(direction[mask]**2);value=float(np.clip(num/max(1,den),0,1.1));track.append(dict(t=f/30,value=value,ease='linear'))
glow=dict(type='circle',id='v12-native-ai-victory-glow',x=cx-R,y=cy-R,width=2*R,height=2*R,fill='url(#v12-ai-victory-emission)',keyframes={'opacity':[dict(t=897/30,value=0)]+track});board['children'].append(glow)
# Reattach the badge to the improved app camera after its measured birth.
label=next(q for q in s['layers'] if q['id']=='broad-v5-group-43');p0=next(q for q in label['keyframes']['x'] if round(q['t']*30)==932)['value'];label['keyframes']['x']=[q for q in label['keyframes']['x'] if q['t']<933/30]+[dict(t=k['t'],value=k['value']+104,ease='linear') for k in keys if k['t']>=933/30]
(D/'chess-camera-glow-v12.json').write_text(json.dumps(dict(camera=poses,glow=track),indent=2));(D/'scene-chess-tap-glow-v12.json').write_text(json.dumps(s,indent=2)+'\n');print('camera',[(q['frame'],round(q['previous'],2),round(q['x'],2)) for q in poses if q['frame'] in [898,909,930,933,936,939]],'glow',[(round(q['t']*30),round(q['value'],3)) for q in track if round(q['t']*30) in [898,903,909,918,930,933]])
