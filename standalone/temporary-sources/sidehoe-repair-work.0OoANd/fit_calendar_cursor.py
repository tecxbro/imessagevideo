from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
sys.path[:0]=['sidehoe-skill-trial/repair/project','sidehoe-recreation/tools']
from phones import load
from render import cursor
from check_follow_contact import components

templates=[]
for angle in range(-180,180,6):
    for size in (.77,.87,.98,1.08,1.16):
        tile=Image.new('RGBA',(192,192),(253,253,253,255))
        cursor(tile,96,96,angle,1,size)
        color=np.array(tile.convert('RGB').resize((96,96),Image.Resampling.LANCZOS))
        pts=np.argwhere(color.max(2)<102)
        lo=pts.min(0)
        templates.append((angle,size,lo,pts.max(0)-lo,pts-lo))
p=Path('sidehoe-skill-trial/repair/project/scene.json')
scene=json.loads(p.read_text()); t=scene['tracks']
xseed=[[399,987],[403,914],[405,897],[409,828],[411,746],[413,654],
       [415,594],[417,559],[421,529],[429,526]]
yseed=[[399,891],[403,556],[405,459],[408,389],[410,386],[412,479],
       [414,540],[418,550],[427,550],[429,543]]
keys=[]
aseed=[[399,-76],[403,-65],[405,-72],[408,-96],[411,-126],[414,-78],[418,-36],[429,-20]]
for f in range(399,430):
    x,y=[np.interp(f,*zip(*a)) for a in (xseed,yseed)]
    a=load('source',f).max(2)<102
    x0,x1=max(0,round((x-64)/2)),min(500,round((x+66)/2))
    y0,y1=max(0,round((y-75)/2)),min(500,round((y+75)/2))
    groups=[]
    for points in components(a[y0:y1,x0:x1]):
        lo=points.min(0)
        extent=points.max(0)-lo
        if len(points)>=17 and 4<=extent[0]<36 and 4<=extent[1]<36:
            dist=np.hypot(*((points.mean(0)+[y0,x0])*2-[y,x]))
            groups.append((dist-len(points)*.028,points))
    if not groups:
        continue
    _,pts=min(groups,key=lambda g:g[0])
    lo,hi=pts.min(0),pts.max(0)
    target=np.zeros((100,100),dtype=bool)
    target[pts[:,0]-lo[0]+20,pts[:,1]-lo[1]+20]=True
    best=None
    for theta,size,tmin,tspan,shape in templates:
        q=np.rint((hi-lo-tspan)/2).astype(int)
        for m in (-2,0,2):
            for n in (-2,0,2):
                offset=q+[m,n]
                tx=shape+offset+20
                correct=target[tx[:,0],tx[:,1]].sum()
                overlap=correct/(len(shape)+len(pts)-correct)
                angle_error=abs(theta-np.interp(f,*zip(*aseed)))
                score=overlap-angle_error*.0026
                if best is None or score>best[0]:
                    uv=(lo+offset-tmin+[y0,x0]+[48,48])*2
                    best=(score,int(uv[1]),int(uv[0]),theta,size)
    score,x1,y1,angle,size=best
    if score>=.35:
        keys.append([f,x1,y1,angle,size])
    print(f,tuple(round(float(n),2) for n in best))
t['calendarMeasuredCursor']=keys
p.write_text(json.dumps(scene,indent=2,ensure_ascii=False)+'\n')
