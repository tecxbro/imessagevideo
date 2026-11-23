from measure import *
for f in [636,643,649,655,659]:
 print(f)
 for base in [SRC,PRE]:
    q=np.array(Image.open(base/f'{f:06d}.png').convert('RGB'),dtype=np.int16)
    g=q.mean(2)
    p=measure(q,f)
    x,y,s,asp,ky=camera(f); sy=s*asp
    print(base.name)
    for n in ('gray1','gray2'):
        l,t,r,b=p[n]
        print(n,'fill',np.median(q[t+9:b-9,r-16:r-6],axis=(0,1)).astype(int),'ink',round(float(np.percentile(g[t+5:b-5,l+18:r-28],6))))
    badge_range=range(max(1,int(y+120*sy)), min(999,int(y+172*sy)))
    edge=next((j for j in badge_range if np.median(q[j,round(x+30*s):round(x+100*s),0])>249),0)
    print('headerEnd',edge,'head',[float(np.median(q[j,round(x+30*s):round(x+100*s),0])) for j in range(edge-3,edge+3)] if edge else None)
    print('tray',np.median(q[int(p['keys'][0][1])-5:int(p['keys'][0][1])-2,375:625],axis=(0,1)).astype(int))
    a=max(0,int(p['keys'][0][1])+round(196*sy)); b=min(1000,a+110)
    xs,xe=round(x+120*s),round(x+280*s)
    arr=g[a:b,xs:xe]
    dark=(arr<70).sum(1)>(xe-xs)*.7
    print('footer',[(j,int((arr[j-a]<70).sum())) for j in range(a,b) if dark[j-a]])
