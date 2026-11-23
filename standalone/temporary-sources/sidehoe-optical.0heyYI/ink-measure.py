exec(open('/tmp/sidehoe-optical.0heyYI/measure-settle-detail.py').read().split('rows={}')[0])
dat=json.loads((D/'sofia-settle-details.json').read_text())
for f in [340,342,344,346,348,350,352,354,356,358,359]:
 print('FRAME',f)
 for i,dd in enumerate(dirs):
  a=np.asarray(Image.open(dd/f'{f:06}.png').convert('RGB'))
  r,g,b=np.moveaxis(a.astype('int16'),2,0)
  gr,cy,_,_,_,_=dat[str(f)][i]
  reply,sug=[k[0] for k in cy[:2]]
  white=(r>115)&(b>=236)&(g>=204)
  dark=(r<107)&(g<110)&(b<116)
  inks=[]
  for box,_ in gr:
   x,y,X,Y=box
   if Y-y>100:continue
   inks.append(bounds(dark,[x+13,y+7,X-9,Y-7],6,4))
  cols=[]
  for j,(x,y,X,Y) in enumerate([reply,sug]):
   mid=round((y+Y)/2)
   yranges=[(y+15,Y-15)] if j==0 else [(y+15,mid-1),(mid-1,Y-13)]
   for ya,yb in yranges:
    cols.append(bounds(white,[x+22,ya,X-21,yb],8,5))
  print(i,inks,cols)
