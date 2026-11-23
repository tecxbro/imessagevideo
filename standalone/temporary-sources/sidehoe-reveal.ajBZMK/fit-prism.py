from pathlib import Path
from PIL import Image
import numpy as np,json
root=Path(__file__).parent
rows={}
for f, anchors in {
 135:[(331,337),(355,328),(383,318),(405,311),(431,306),(460,303),(495,302),(526,303),(558,306),(584,313),(611,324),(648,338),(665,343)],
 136:[(234,352),(261,352),(286,349),(313,341),(342,344),(367,343),(393,334),(417,333),(444,336),(470,341),(500,341),(528,341),(557,335),(583,334),(607,336),(632,343),(661,344),(687,342),(714,350),(740,353),(764,355)],
}.items():
 p=np.array(Image.open(root/'source'/f'{f-133:03}.png'),dtype=float)
 b=np.array(Image.open(root/'light-probe'/f'{f:06}.png'),dtype=float)
 diff=p-b
 spec=[(-3,4),(5,5.1),(12,5.2),(21,7.2),(30,6.5),(43,5.7)]
 results=[]
 for i,(x,y) in enumerate(anchors):
  if i in (0,len(anchors)-1):
   results.append([x,y,*[0]*(3*len(spec))]);continue
  def basis(ym):
   return np.stack([np.exp(-((ym-y-off)/s)**2) for off,s in spec],axis=1)
  ym=np.arange(y-17,y+50)
  d=np.mean(diff[ym,x-4:x+5],axis=1)
  mat=basis(ym)
  coef=np.linalg.solve(mat.T@mat+np.eye(len(spec))*.65,mat.T@d)
  results.append([x,y,*np.round(np.clip(coef,-105,146),2).ravel().tolist()])
 rows[str(f)]=results
(root/'prism-fit.json').write_text(json.dumps(rows,indent=2))
