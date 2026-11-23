from pathlib import Path
from PIL import Image
from copy import deepcopy
import json,sys
import numpy as np
root=Path(__file__).parent
sys.path.insert(0,str(root/'project'))
from render import interpolate
original=Path('/Users/darshan/Documents/ChatGPT/imessage-video/sidehoe-skill-trial/tile-and-push-review/project/scene.json')
s=json.loads(original.read_text())
source=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
measure=json.loads((root/'measured.json').read_text())
register=s['threadRegistration']['sofia']
new={}
for f in range(329,337):
    spec,orig=measure[str(f)]
    canvas=np.asarray(Image.open(source/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    combo=canvas.mean(axis=2)
    cam=interpolate(s['tracks']['sofiaMeasuredCamera'],f)
    dx,dy,scale=cam
    rails=[spec['rails'][0]['221'][0][1]+1,spec['rails'][1]['221'][0][0]-1]
    outer=[spec['rails'][0]['240'][0][0],spec['rails'][1]['240'][0][1]]
    y=spec['top']-.1
    if f==336:
        y=-2.5
    w=(outer[1]-outer[0]-3)/400
    rail_colors=[]
    for start,end in ((outer[0]-9,rails[0]+9),(rails[1]-9,outer[1]+9)):
        luma=np.rint(np.median(combo[380:650,start:end+1],axis=0)).astype(int)
        rail_colors.append([start,end,luma.tolist()])
    top=spec['tray']-1
    tray=np.rint(np.median(canvas[top+4:top+7,470:530,:],axis=(0,1))).astype(int).tolist()
    first=spec['keys'][0]
    pitch=round((first[1][9][0]-first[1][0][0])/9,3)
    height=round(pitch*1.087,2)
    step=spec['keys'][1][0][0]-first[0][0]
    rows=[]
    for i,len_row in enumerate((10,9,7)):
        box,col=spec['keys'][i]
        if i==2 and f>=334:
            y0=first[0][0]+2*step-1
            left=first[1][0][0]+pitch*1.50
        else:
            y0=box[0]
            left=col[1 if i==2 else 0][0]
        rows.append([left-1.1,y0-1,pitch,round(pitch*.855,2),height,len_row])
    utility_top=round(rows[2][1]+step-2)
    head_end=spec['chrome'][-1][1]
    history=[]
    for i,(l,t,r,b) in enumerate(spec['received']):
        il,it,ir,ib=spec['ink'][i]
        history.append([[l-2,t-1,r+1,b+1],[[il-.5,it-1,ir-il+1,ib-it+2]]])
    if len(history)!=2:
        raise ValueError((f,spec['received']))
    diff={**new}
    blue=spec['cyan'][0]
    bw,bh=blue[2]-blue[0],blue[3]-blue[1]
    blue_ink=[blue[0]+bh*.49,blue[1]+bh*.35,bw-bh*.91,bh*.30]
    first=spec['cyan'][1]
    first_w,first_h=first[2]-first[0],first[3]-first[1]
    # The source holds the lower curve while the eye moves to the suggestion.
    earlier_reply=[first,[first[0]+first_h*.40,first[1]+first_h*.39,first_w-first_h*.69,first_h*.31]]
    roles={
      329:[0,0,.70],330:[0,0,.74],331:[0,0,.80],332:[0,0,.85],
      333:[.85,1.8,.87],334:[1.55,2.8,.98],335:[2.15,4.35,1.02],336:[3.5,5.7,1.05],
    }
    may=s['copy']['today']
    home=None
    if f<=332:
        y0=[952,966,981,995][f-329]
        home=[500-round(scale*65),y0-3,500+round(scale*65),y0+4]
    footer=None
    if utility_top+110<1040:
        footer=[utility_top+round(scale*94),home]
    sample=canvas[blue[1]+round(bh*.20):blue[1]+round(bh*.40),blue[0]+27:blue[0]+64]
    pigment=np.rint(np.median(sample,axis=(0,1))).astype(int).tolist()
    flight=spec['today']
    text_y=[450,452,452,452,452,451,447,435][f-329]
    today=[500-scale*13.5,text_y,scale*27,scale*9]
    # Hardware opacity is applied before the independently softened display plane.
    new[str(f)]=dict(rails=rails,keys=[top,tray,rows],items=history,today=today,
      blue=blue,blueInk=blue_ink,bluePaint=pigment,edgeRamps=rail_colors,
      corners=[round(18*scale,2),round(18*scale,2)],focus=roles[f],
      railSpan=[round(y+scale*42),round(y+scale*85),round(y+scale*(827-83)),round(y+scale*(827-42))],
      casing=[outer[0]+.4,y,w,round((head_end-y)/w),[0,.2,.45,.7,1.1,1.5,1.9,2.4][f-329],
              [.8,.9,1,1.1,1.3,1.5,1.8,2.1][f-329]],
      utilityRow=[utility_top,round(scale*42)],earlierReply=earlier_reply)
    if footer:
        new[str(f)]['keyboardFooter']=footer
# Reuse the same registration through the next push. Use the source's soft per-frame tint
# when the moving rows leave trails around the glyphs.
for f in (337,338,339):
    new[str(f)]=deepcopy(register[str(f)])
    new[str(f)]['focus']= {337:[6.3,10,.93],338:[5.2,8.5,.98],339:[4.1,6.9,.94]}[f]
register.update(new)
path=root/'project/scene.json'
path.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
