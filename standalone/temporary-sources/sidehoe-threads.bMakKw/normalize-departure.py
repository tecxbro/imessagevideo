from pathlib import Path
import json,sys
import numpy as np
r=Path(__file__).parent
sys.path.insert(0,str(r/'project'))
from render import interpolate
m=json.loads((r/'send-fit.json').read_text())
p=r/'project/scene.json'
s=json.loads(p.read_text());t=s['tracks']
out=[]
last=[[.155,.31,.70,.33],[.093,.16,.767,.254],[.092,.535,.745,.255]]
for f in range(360,403):
 entry=[f]
 vals=[]
 for i,k in enumerate(('sendReplyBox','sendSuggestionBox')):
  x,y,X,Y=interpolate(t[k],f);w=X-x;h=Y-y
  for j,q in enumerate(m[str(f)][i][1],0 if i==0 else 1):
   prev=last[j]
   use=(q is not None and f<=393 and .47<q[2]/w<.88
        and .19<q[3]/h<.48 and .01<(q[0]-x)/w<.22)
   if use:
    fit=[(q[0]-x)/w,(q[1]-y)/h,q[2]/w,q[3]/h]
    if j==2 and fit[1]<.48:fit=prev
    vals.append(fit)
    last[j]=fit
   else:vals.append(prev)
 entry.extend(round(z,5) for seq in vals for z in seq)
 out.append(entry)
t['sendDepartureInk']=out
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
