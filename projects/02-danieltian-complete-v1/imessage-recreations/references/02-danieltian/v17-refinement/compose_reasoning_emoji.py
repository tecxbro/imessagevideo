from pathlib import Path
import json,copy,re
import numpy as np
R=Path(__file__).resolve().parent
spec=json.loads((R/'reasoning-neutral-compact.json').read_text());root=spec['replacement'];fits=json.loads((R/'emoji-fit-candidate.json').read_text())
for row in root['children']:
    for child in row.get('children',[]):
        if child.get('id','').startswith('early-reason-emoji-full-')and child['id']!='early-reason-emoji-full-3-0':
            child['opacity']=0
            child.get('keyframes',{}).pop('opacity',None)
mag=json.loads((R.parent/'v11-boundary-refinement.json').read_text())['replacements']['group-1007']['children']
mag={int(n['id'].split('-')[-1]):n for n in mag if n['id'].startswith('peak-native-magnifier-')}
def circle(frame):
    paths=[]
    for loop in re.findall(r'M([^Z]+)Z',mag[frame]['d']):
        a=np.array(list(map(float,re.findall(r'-?\d+(?:\.\d+)?',loop)))).reshape(-1,2)
        paths.append(a)
    if frame>=364:
        loops=[a for a in paths if np.ptp(a[:,0])>20 and np.ptp(a[:,1])>20]
        if len(loops)>=2:
            a=min(loops,key=lambda a:np.ptp(a[:,0])*np.ptp(a[:,1]));low=a.min(0);high=a.max(0)
            return ((low+high)/2,(high-low).mean()/2)
    a=np.concatenate(paths);a=a[(a[:,0]>2)&(a[:,0]<1918)&(a[:,1]>2)&(a[:,1]<1078)]
    radius=np.linalg.norm(a-[957.5,537.5],axis=1);a=a[radius<np.quantile(radius,.4)]
    x,y=a.T;cx,cy,c=np.linalg.lstsq(np.stack([2*x,2*y,np.ones(len(x))],1),x*x+y*y,rcond=None)[0]
    return(np.array([cx,cy]),float(np.sqrt(c+cx*cx+cy*cy)))
allposes={name:{p['frame']:copy.deepcopy(p)for p in data['poses']}for name,data in fits.items()}
# Occluded portions are not object dimensions: derive continuation from the fully visible pin camera.
pin=allposes['pin'];anchor=pin[360]
for name,poses in allposes.items():
    for f in range(min(poses),max(poses)+1):
        if f not in poses:
            prior=max(i for i in poses if i<f);following=min(i for i in poses if i>f);prev=poses[prior];nxt=poses[following];mix=(f-prior)/(following-prior)
            poses[f]={key:prev[key]+(nxt[key]-prev[key])*mix if isinstance(prev[key],(int,float)) else prev[key]for key in prev};poses[f]['frame']=f
    for f in range(361,373):
        if f not in pin:continue
        if (name=='food'and f>=363)or(name in ['heads','car']and f>=364)or(name=='heart'and f>=367):
            base=poses[360];p=pin[f];sx=p['width']/anchor['width'];sy=p['height']/anchor['height']
            new=copy.deepcopy(base);new.update(frame=f,x=p['x']+(base['x']-anchor['x'])*sx,y=p['y']+(base['y']-anchor['y'])*sy,width=base['width']*sx,height=base['height']*sy,opacity=base['opacity']*p['opacity']/anchor['opacity'],blur=p['blur']);poses[f]=new
    for f,pose in sorted(poses.items()):
        image={'id':f'reason-emoji-native-{name}-{f}-art','type':'image','src':fits[name]['art']['file'],**{k:pose[k]for k in['x','y','width','height','opacity','blur']},'semanticText':name,'sourceFrame':fits[name]['art']['frame'],'editability':'Authentic static Apple emoji artwork on measured independent native camera/blur/alpha.'}
        group={'id':f'reason-emoji-native-{name}-{f}','type':'group','start':f/30,'end':(f+1)/30,'children':[image]}
        if f>=361:
            center,radius=circle(f);group['clip']={'x':float(center[0]-radius),'y':float(center[1]-radius),'width':float(2*radius),'height':float(2*radius),'radius':float(radius)}
        root['children'].append(group)
spec['emojiMeasurements']=allposes
(R/'reasoning-combined-candidate.json').write_text(json.dumps(spec,separators=(',',':')))
print('wrote',len(root['children']),'children',flush=True)
