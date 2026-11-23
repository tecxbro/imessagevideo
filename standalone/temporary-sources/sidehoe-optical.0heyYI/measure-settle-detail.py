exec(open('/tmp/sidehoe-optical.0heyYI/measure-settle.py').read().split('for f in [340')[0])
import json
def bounds(mask,box,row_min=1,col_min=1):
 x,y,X,Y=box
 m=mask[y:Y,x:X]
 rs=np.flatnonzero(m.sum(axis=1)>=row_min); cs=np.flatnonzero(m.sum(axis=0)>=col_min)
 if len(rs)*len(cs)==0:return []
 return [int(x+cs[0]),int(y+rs[0]),int(x+cs[-1]+1),int(y+rs[-1]+1)]
def palette(a,x,y):
 return [int(c) for c in np.median(a[y-2:y+3,x-2:x+3],axis=(0,1))]
rows={}
for f in range(338,360):
 rows[f]=[]
 for dd in dirs:
  a=np.asarray(Image.open(dd/f'{f:06}.png').convert('RGB'))
  r,g,b=np.moveaxis(a.astype('int16'),2,0)
  colors=r,g,b
  gr=comp(a,gray,(40 if f>345 else 80, max(14,100-(f-346)*8) if f<346 else 12,800,365),(120,29))
  cy=comp(a,cyan,(366,275,950,659),(140,25))
  cy.sort(key=lambda v:v[0][1])
  words=[]
  for (x,y,X,Y),_ in cy[:2]:
   words.append(bounds((r>125)&(b>248),[x+12,y+9,X-17,Y-8],8,3))
  chips=[]
  for m in ((r>=187)&(r<220)&(np.abs(r-g)<6)&(np.abs(r-b)<9),
            ((r-g)>13)&(b>232)|(b-g>17)&(g>186)&(g<240)&(r>130)&(b>230)):
   y=max(584,cy[-1][0][3]-3) if cy else 600
   chips.append(bounds(m,[575,y,880,min(693,y+73)],13,7))
  neutral=(r<227)&(r>85)&(abs(r-b)<22)&(abs(r-g)<9)
  lab=[]
  if len(cy)>1:
   x,y,X,Y=cy[1][0]
   lab=bounds(neutral,[x+4,y-37,min(x+290,730),y-1],5,4)
  neutral_dark=(r<158)&(r>=65)&(abs(r-g)<12)&(abs(r-b)<12)
  today=bounds(neutral_dark,[430,235,550,356],6,4)
  printkind=[gr,cy,words,chips,lab,today]
  rows[f].append(printkind)
 if f%2==0 or f in [349,353,355,359]:
  print(f)
  for k in rows[f]: print(k)
(D/'sofia-settle-details.json').write_text(json.dumps(rows,indent=2))
