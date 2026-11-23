from pathlib import Path
import json
import numpy as np
from PIL import Image
from phones import load

# Estimates at overview poses seed a local color search. Values are stage units.
rough = {
 "dark": [[478,510,496,178],[483,593,506,168],[487,632,485,176],[496,656,492,166],
          [511,684,494,172],[530,689,514,166],[536,593,605,228],[550,442,612,231],
          [558,358,557,198],[567,334,499,176],[574,350,466,145],[586,465,398,100],
          [597,485,401,106],[612,506,455,104],[616,506,528,109],[619,506,644,109],
          [620,506,718,109],[621,506,824,109]],
 "rings": [[478,500,499,184],[480,522,465,180],[482,523,428,150],[487,477,411,111],
           [496,472,395,108],[511,494,386,107],[530,511,379,109],[536,650,444,146],
           [550,666,540,198],[558,632,610,204],[567,506,618,224],[574,412,598,208],
           [586,331,526,180],[597,311,532,174],[612,308,573,189],[616,308,644,187],
           [619,308,756,187],[620,308,827,187],[621,308,935,188]],
}

def estimate(key,f):
    a=np.array(rough[key])
    return tuple(np.interp(f,a[:,0],a[:,i]) for i in (1,2,3))

def pose(key,f):
    cx,cy,sz=estimate(key,f)
    rgb=load('source',f)
    l,t=max(0,round((cx-sz*.43)/2)),max(0,round((cy-sz*.46)/2))
    r,b=min(500,round((cx+sz*.43)/2)),min(500,round((cy+sz*.46)/2))
    if r<=l or b<=t:return [f,cx,cy,sz]
    red,g,blue=rgb[t:b,l:r].transpose(2,0,1)
    if key=='dark':
        mask=(np.maximum(np.maximum(red,g),blue)<126)
    else:
        mask=(blue>137)&(blue-g>27)&(red>87)&(red-g>30)&(blue-red>-31)
    y,x=np.where(mask)
    if len(x)<18:return [f,cx,cy,sz]
    mx0,mx1=np.quantile(x,[.015,.985]);my0,my1=np.quantile(y,[.03,.97])
    dy=2*(my1-my0)
    mvx=mx1+mx0+2*l
    mvy=my1+my0+2*t
    if key=='rings':
        # Magenta is the right loop and occupies the right half of the tile.
        mvx-=sz*.125
        scale=(dy*2.27+sz*.35)/1.35
    else:
        scale=(dy*1.35+sz*.46)/1.46
    if abs(mvx-cx)>55 or abs(mvy-cy)>58 or not .52*sz<scale<1.45*sz:
        return [f,cx,cy,sz]
    return [f,mvx,mvy,scale]

def glow(f,tracks):
    # Fit a pair of soft color fields from unobstructed background pixels.
    rgb=load('source',f)
    ij=np.arange(5,500,10)
    rows,columns=np.meshgrid(ij,ij,indexing='ij')
    mask=np.ones(rows.shape,bool)
    for track in tracks:
        a=np.array(track)
        x,y,s=[np.interp(f,a[:,0],a[:,i]) for i in (1,2,3)]
        mask &= (np.abs(columns*2-x) > s*.74) | (np.abs(rows*2-y) > s*.74)
    color=rgb[rows,columns]
    mask &= color.min(2)>205
    y,x=rows[mask]/500,columns[mask]/500
    target=np.clip(253-color[mask],0,128)
    fall=0 if f<613 else min(.54,max(0,(f-613)**2/130))
    seeds=np.array([[.36,.34+fall,.27,.28,0],[.63,.63+fall,.21,.24,0]])
    def solve(a):
        basis=np.array([np.exp(-((x-cx+shear*(y-cy))/sx)**2-((y-cy)/sy)**2)
                        for cx,cy,sx,sy,shear in a]).T
        gains=np.maximum(np.linalg.lstsq(basis,target,rcond=None)[0],0)
        gains=np.minimum(gains,155)
        loss=((basis@gains-target)**2).mean()
        return loss,gains
    best,gains=solve(seeds)
    for step in (.065,.035,.018):
        for _ in range(6):
            for j in range(2):
                for k in range(4):
                    for sign in (1,-1):
                        trial=seeds.copy()
                        trial[j,k]+=step*sign
                        if trial[j,2:4].min()<.105:continue
                        loss,new=solve(trial)
                        if loss<best:seeds,best,gains=trial,loss,new
    return [f,*np.round(np.hstack((seeds,gains)).ravel(),4).tolist()]

if __name__=='__main__':
    p=Path('sidehoe-skill-trial/repair/project/scene.json')
    d=json.loads(p.read_text())
    tracks=d['tracks']
    for key in rough:
        tracks[key+'MeasuredOrbit']=[[int(a[0]),*(round(float(b),3) for b in a[1:])]
                                     for a in (pose(key,f) for f in range(478,622))]
    tracks['measuredOrbitGlow']=[glow(f,[tracks[k] for k in ('redOrbit','blueOrbit','darkMeasuredOrbit','ringsMeasuredOrbit')])
                                for f in [477,478,480,487,501,518,530,543,556,567,579,586,601,612,615,617,619,620,621,622]]
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
