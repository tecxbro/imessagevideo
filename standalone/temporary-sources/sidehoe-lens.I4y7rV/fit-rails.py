from pathlib import Path
from PIL import Image
import json,numpy as np
from scipy.ndimage import gaussian_filter1d
root=Path(__file__).parent
p=root/'project/scene.json'
data=json.loads(p.read_text())
src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
for f,(top,left,width) in {134:(267,50,901),135:(293,44,900),136:(319,50,893),137:(334,47,896)}.items():
 a,b=[np.asarray(Image.open(d/f'{f:06}.png').convert('L'),float) for d in (src,root/'probe-v1')]
 start={134:347,135:399,136:430,137:443}[f]
 rows=[start,*range(start+20,983,28),989,999]
 knots=[]
 for y in rows:
  both=[]
  for z in [a,b]:
   shade=gaussian_filter1d(np.median(z[max(0,y-5):y+6],axis=0),1.7)
   values=[]
   for flip in (False,True):
    search=shade[::-1] if flip else shade
    low,high=30,165
    where=np.flatnonzero(search[low:high]<155)+low
    if len(where)==0:
     values=[]; break
    gaps=np.flatnonzero(np.diff(where)>1)
    if len(gaps):
     where=where[:gaps[0]+1]
    if len(where)<12:
     values=[]; break
    span=np.array([where[0],where[-1]])
    if flip:
     span=999-span[::-1]
    values.append(np.clip((span-left)*900/width,1,899))
   both.append(values)
  if all(both):
   target,previous=both
   params=np.array([(target[i][0],target[i][1],previous[i][0],previous[i][1]) for i in range(2)])
   params[0]=np.clip(params[0],2,150)
   params[1]=np.clip(params[1],749,898)
   params[:, :2]=np.clip(params[:, :2],params[:, 2:]-22,params[:, 2:]+22)
   knots.append([y-top,*np.rint(params.ravel()).astype(int).tolist()])
 if knots[0][0]>7:
  knots.insert(0,[knots[0][0]-38,12,121,12,121,779,886,779,886])
 data['assistantEntranceOptics'][str(f)]['rails']=knots
 if f in (136,137):
  intensity=1 if f==136 else .79
  data['assistantEntranceOptics'][str(f)]['flare']=[
   [i[0],i[1],i[2],i[3],i[4],*map(lambda c:round(intensity*c),i[5:])] for i in [
    [52,1000,15,32,.22,22,84,25],[67,994,12,27,-.14,4,130,43],
    [77,998,12,21,.24,154,28,-26],[92,996,11,24,-.38,90,39,76],
    [119,988,39,10,-.31,-35,-1,8],
    [947,998,13,33,-.34,27,122,35],[928,991,10,30,.17,1,115,32],
    [914,997,10,20,-.17,124,46,-43],[897,996,13,16,.42,123,69,67],
    [870,991,42,9,.25,-3,-48,-11]]]
p.write_text(json.dumps(data,indent=2)+'\n')
