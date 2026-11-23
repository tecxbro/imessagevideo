from pathlib import Path
p=Path('sidehoe-skill-trial/repair/project')
f=p/'render.py';v=f.read_text()
a=v.index('    def apps(');b=v.index('    def follow(',a)
v=v[:a]+'''    def apps(self,im,f):
        phase,=self.track("orbitPhase",f)
        fade=1-tween(f,619,623)
        nodes=[]
        entrances={"rings":478,"red":479,"blue":479,"dark":481}
        lead = ("rings" if f<=478 else "red" if f<=533 else "dark" if f<=555
                else "rings" if f<=575 else "blue")
        for name,k in (("red",0),("dark",.25),("rings",.50),("blue",.75)):
            onset=entrances[name]
            if f<onset:
                continue
            depth=math.cos((k-phase)*math.tau)
            path=f"{name}Orbit" if name in ("red","blue") else f"{name}MeasuredOrbit"
            x,y,size=self.track(path,f)
            alpha=mix(.68,1,tween(f,onset,onset+2))*fade
            nodes.append((name==lead,depth,name,x,y,size,alpha))
        for _,depth,name,x,y,size,alpha in sorted(nodes):
            ox=app_icon(name)
            softness=(1-depth)*1.4+4*(1-tween(f,478,483))
            ox=blur(ox,softness)
            if f>=617:
                pad=64
                exposed=layer(ox.width,ox.height+2*pad)
                exposed.alpha_composite(ox,(0,pad))
                ox=vertical_blur(exposed,125*tween(f,616,621))
                frame_scale=size/ox.width
                composite(im,ox,x-size/2,y-(128+pad)*frame_scale,alpha,frame_scale)
            else:
                stamp(im,ox,x,y,size,alpha)

'''+v[b:]
v=v.replace('''        if 478<=f<622:
            self.apps(im,f)
        if 397<=f<482:
            self.calendar(im,f)''','''        if 478<=f<622:
            im.alpha_composite(measured_wash(tuple(self.track("measuredOrbitGlow",f))))
        if 397<=f<482:
            self.calendar(im,f)
        if 478<=f<622:
            self.apps(im,f)''')
f.write_text(v)
f=p/'artwork.py';v=f.read_text()
a=v.index('        d.polygon([(122,49)')
b=v.index('    elif key=="blue":',a)
v=v[:a]+'''        # Editable flame silhouette in local tile coordinates.
        points=[(123,47),(145,69),(163,92),(178,115),(181,137),(179,156),
                (172,172),(153,188),(134,196),(112,197),(94,190),(81,177),
                (74,163),(72,149),(75,131),(84,111),(96,96),(104,124),
                (113,117),(122,107),(128,94),(129,77)]
        d.polygon([(128+(x-128)*1.39,127+(y-127)*1.24) for x,y in points],fill="#fffefe")

'''+v[b:]
a=v.index('        for box in [(64,55',v.index('def app_icon'))
b=v.index('    return im',a)
v=v[:a]+'''        for box in [(56,42,89,217),(151,42,184,217),(78,111,180,145)]:
            d.rounded_rectangle(box,radius=9,fill="#202023")
        d.arc((133,67,225,140),1,82,fill="#212125",width=24)
    else:
        for cx,col in [(93,"#20abc8"),(158,"#a32cb5")]:
            oval(d,cx,127,51,54,None,outline=col,width=11)
'''+v[b:]
f.write_text(v)
