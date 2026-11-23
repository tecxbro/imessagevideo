from pathlib import Path
import json
p=Path('sidehoe-skill-trial/project')
s=json.loads((p/'scene.json').read_text())
centers=[(296,300,121),(518,300,60),(630,225,44),(720,380,90),(130,391,45),(429,481,89),(245,504,67),(573,421,46),(676,632,120),(834,510,47),(244,705,99),(454,683,65),(562,790,44)]
for cell,(x,y,r) in zip(s['cluster'],centers,strict=True):
    cell[1]=round(500+(x-468)/1.08)
    cell[2]=round(500+(y-473)/1.08)
    cell[3]=round(r/1.08)
s['tracks']['inboxY']=[([f,-1128] if f==62 else [f,-1173] if f==64 else [f,y]) for f,y in s['tracks']['inboxY']]
s['tracks']['profileCamera'][-1:]=[[311,205,226,1.42],[312,205,350,1.42]]
s['tracks']['profileArrivalLisa']=[[258,798,367,94,63],[259,557,387,100,29],[260,462,414,99,19],[261,406,433,100,14],[262,367,450,100,10],[263,337,457,100,6],[267,280,440,101,2],[271,275,428,102,0]]
s['tracks']['profileArrivalElla']=[[260,735,361,101,13],[261,678,386,101,10],[262,639,415,101,8],[263,606,438,101,5],[267,554,451,102,2],[271,550,428,102,0]]
s['tracks']['profileArrivalMaria']=[[262,911,365,101,13],[263,881,390,102,10],[264,859,413,102,8],[267,826,457,102,2],[271,825,428,102,0]]
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py';v=f.read_text()
pos=v.index('    def profiles(')
v=v[:pos]+'''    def profile_arrival(self,im,f):
        for j,(name,key,tag,fill,ink) in enumerate(self.s["profiles"]):
            track_name = f"profileArrival{name}"
            start = self.s["tracks"][track_name][0][0]
            if f < start:
                continue
            x,y,radius,blur_radius = self.track(track_name, f)
            portrait_layer = layer(360,320)
            self.avatar(portrait_layer,key,180,160,2*radius,neutral=False)
            sprite = blur(portrait_layer,blur_radius*.51)
            if f == 258:
                sprite = sprite.transpose(Image.Transpose.ROTATE_90)
                sprite = vertical_blur(sprite,140).transpose(Image.Transpose.ROTATE_270)
            composite(im,sprite,x-180,y-160)
            label_y = mix(563, 561, tween(f,263,271))
            label_alpha = tween(f,start+1,start+7)
            labels = layer(300,155)
            d = ImageDraw.Draw(labels)
            prefix = name[:max(1,round(len(name)*label_alpha))]
            text(d,150,5,prefix,40,INK,630,"center")
            chip_w = 220*(.40+.60*label_alpha)
            d.rounded_rectangle((150-chip_w/2,58,150+chip_w/2,106),24,fill=fill)
            text(d,150,68,tag,22,ink,590,"center")
            composite(im,blur(labels,blur_radius*.23),x-150,label_y,label_alpha)

'''+v[pos:]
v=v.replace('    def profiles(self,im,f):\n        xoff,yoff,zoom=self.track("profileCamera",f)','''    def profiles(self,im,f):
        if f < 271:
            self.profile_arrival(im,f)
            return
        xoff,yoff,zoom=self.track("profileCamera",f)''')
f.write_text(v)
