from pathlib import Path
import json,numpy as np,shutil
D=Path(__file__).resolve().parent;src=D/'food-refined-measurements.json';backup=D/'food-refined-unfiltered.json'
if not backup.exists():shutil.copyfile(src,backup)
s=json.loads(backup.read_text());out={};rejected=[]
def duplicate(a,b):
 A=np.array(a['corners']);B=np.array(b['corners']);la,ha=A.min(0),A.max(0);lb,hb=B.min(0),B.max(0);inter=np.maximum(0,np.minimum(ha,hb)-np.maximum(la,lb));ia=float(np.prod(inter));area=min(float(np.prod(ha-la)),float(np.prod(hb-lb)));distance=np.linalg.norm(np.array(a['center'])-b['center']);return ia/max(1,area)>.5 and distance<.6*max(*(ha-la),*(hb-lb)) and a['inliers']<b['inliers']*.6 and a['fitMAE']>b['fitMAE']+5
for ns,models in s.items():
 keep=[]
 for m in sorted(models,key=lambda q:(-q['inliers'],q['fitMAE'])):
  old=next((q for q in keep if q['kind']==m['kind'] and duplicate(m,q)),None)
  if old:rejected.append(dict(frame=int(ns),rejected=m,retained=old))
  else:keep.append(m)
 out[ns]=keep
src.write_text(json.dumps(out,indent=2));(D/'rejected-weak-nested-fits.json').write_text(json.dumps(rejected,indent=2));print('Rejected weak nested duplicate fits',len(rejected))
