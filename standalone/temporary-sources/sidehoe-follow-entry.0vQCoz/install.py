from measure import *

scene_path = ROOT/'project/scene.json'
scene = json.loads(scene_path.read_text())
measured = json.loads((ROOT/'measured.json').read_text())
fit_path = ROOT/'casing-fit.json'
casing_fit = json.loads(fit_path.read_text()) if fit_path.exists() else {}
for key,(marks,_) in measured.items():
    f=int(key)
    q=np.asarray(Image.open(SRC/f'{f:06d}.png').convert('RGB'),dtype=np.int16)
    x,y,s,asp,ky=camera(f)
    sy=asp*s
    case=casing_fit.get(key)

    def local(rect):
        l,t,r,b=rect
        return [round(v,3) for v in ((l-x)/s,(t-y)/sy,(r-x)/s,(b-y)/sy)]

    def ink(rect):
        l,t,r,b=local(rect)
        return l,t,round(r-l,3),round(b-t,3)

    header_end=next(k for k in range(max(1,int(y+121*sy)), min(998,int(y+172*sy)))
                    if np.median(q[k,round(x+30*s):round(x+100*s),0])>249)
    tray_top=marks['keys'][0][1]
    tray_y=next(k for k in range(round(tray_top-16*sy),round(tray_top))
                if 196 < np.median(q[k,round(x+105*s):round(x+290*s),0])<229)
    board = q[round(tray_top+185*sy):,round(x+111*s):round(x+289*s)]
    board_y=round(tray_top+185*sy)
    longest=[]
    for row in (board.max(2)<78):
        take=np.flatnonzero(row)
        lengths=np.split(take,np.flatnonzero(np.diff(take)>1)+1)
        longest.append(max(lengths,key=len))
    runs=[i for i,a in enumerate(longest) if s*117<len(a)<s*148]
    home=None
    if runs:
        block=list(np.split(runs,np.flatnonzero(np.diff(runs)>1)+1))[0]
        if len(block):
            mid=int(block[len(block)//2])
            span=longest[mid]+round(x+111*s)
            home=local((span[0],block[0]+board_y,span[-1]+1,block[-1]+board_y+1))
    else:
        raise ValueError((f,'missing home bar'))
    space_search=components(q,(x+98*s,(marks['keys'][2][1]+45*sy),x+300*s,marks['keys'][2][1]+114*sy),
                            lambda a:(a.min(2)>=245)&(np.ptp(a,axis=2)<9),1000)
    assert space_search, f
    space=space_search[0][1]

    if f >= 650 and case and case[2]<case[1]:
        dx,dy,dw,dh=case[0]
        previous_x,previous_y,previous_s,previous_sy=x,y,s,sy
        x+=dx-dw/2
        y+=dy-dh/2
        s+=dw/399
        sy+=dh/826
        if home:
            l,t,r,b=home
            home=local((previous_x+l*previous_s,previous_y+t*previous_sy,
                        previous_x+r*previous_s,previous_y+b*previous_sy))
    records=dict(badge=local(marks['badge']),name=ink(marks['name']),island=local(marks['island']),
                 headerEnd=round((header_end-y)/sy-1.2,3),idY=round((marks['island'][1]-y)/sy+18,3))
    if f >= 650 and case and case[2]<case[1]:
        records['camera']=[round(a,5) for a in (x,y,s,sy/s)]
    records['coverage']={631:.50,632:.83}.get(f,1)

    records['layout']=[(tray_y-y)/sy,
        [[(l-x)/s,(t-y)/sy,p/s,w/s,h/sy] for l,t,p,w,h in marks['keys']],
        (space[1]-y)/sy,(space[3]-space[1])/sy,home]
    records['layout'][:4]=[round(v,3) if isinstance(v,(float,int)) else [[round(a,3) for a in r] for r in v] for v in records['layout'][:4]]
    records['blue']=[local(marks['blue']),marks['blueStops']]
    records['composerY']=round((marks['composer'][1]-y)/sy+1,3)
    records['today']=ink(marks['today'])
    records['bubbles']=[[local(marks[n]),[ink(k) for k in marks[n+'_ink']]] for n in ('gray1','gray2')]
    scene.setdefault('followSettledRegistration',{})[key]=records

scene_path.write_text(json.dumps(scene,indent=2)+'\n')
