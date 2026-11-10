from pathlib import Path
from PIL import Image
import numpy as np,json
REF=Path(__file__).resolve().parent;ROOT=REF.parents[1];spec=json.loads((REF/'root-backplane-patch-v4.json').read_text());ex=json.loads((REF/'root-backplane-food-exclusions-v4.json').read_text());checks=[]
for l in spec['layers']:
 if not l['id'].startswith('root-backplane-ui-ink-'):continue
 n=int(l['id'].split('-')[-1]);alpha=np.array(Image.open(l['src']).convert('RGBA'))[:,:,3]
 for bx0,by0,bx1,by1 in ex['bounds'].get(str(n),[]):
  m=ex['margin'];x0=max(0,bx0-m-l['x']);x1=min(l['width'],bx1+m-l['x']);y0=max(0,by0-m-l['y']);y1=min(l['height'],by1+m-l['y']);ok=x1<=x0 or y1<=y0 or not alpha[y0:y1,x0:x1].any();checks.append({'frame':n,'rect':True,'excluded':bool(ok)})
 if n==733:
  mask=np.array(Image.open(ex['shapeMasks'][0]['file']).convert('L'))>0;mx0,my0,mx1,my1=ex['shapeMasks'][0]['bounds'];xa=max(l['x'],mx0);xb=min(l['x']+l['width'],mx1);ya=max(l['y'],my0);yb=min(l['y']+l['height'],my1);sub=alpha[ya-l['y']:yb-l['y'],xa-l['x']:xb-l['x']];inside=mask[ya-my0:yb-my0,xa-mx0:xb-mx0];assert not sub[inside].any();checks.append({'frame':733,'shape':True,'excluded':True})
  source=np.array(Image.open(REF/'assets/root-backplane-measure/frame-733.png').convert('RGB'));region=source[740:750,1056:1152].mean(2);yy,xx=np.unravel_index(region.argmin(),region.shape);px,py=1056+int(xx),740+int(yy);preserved=int(alpha[py-l['y'],px-l['x']]);checks.append({'protectedUI':True,'position':[px,py],'sourceGray':float(region[yy,xx]),'newInkAlpha':preserved});assert preserved>0
assert all(q.get('excluded',True) for q in checks);(ROOT/'outputs/03-photon-mini/root-backplane-v4-food-mask-proof.json').write_text(json.dumps(checks,indent=2));print(checks)
