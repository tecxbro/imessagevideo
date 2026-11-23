from pathlib import Path
import json
p=Path('sidehoe-skill-trial/project')
s=json.loads((p/'scene.json').read_text())
s['portraitSprites']=True
s['tracks']['clusterPose'][0:3]=[[213,-29,149,.83],[216,-16,55,.89],[218,-7,21,.91]]
s['tracks']['personalWash']=[[162,1.20],[182,1.10],[195,.97],[201,.84],[209,.74],[212,.69]]
s['tracks']['closingWash']=[[712,0],[715,.12],[724,.49],[732,.80],[741,1.14],[752,1.13],[765,1],[777,1]]
s['tracks']['sendCursor'][7:10]=[[393,843,642,0],[394,844,630,0],[396,852,614,0]]
s['tracks']['calendarCamera'][1:4]=[[403,188,521,82],[405,190,448,87],[410,196,332,89],[420,192,287,91]]
s['tracks']['sofiaCamera'][8:13]=[[336,9,1.37],[338,-144,1.60],[339,-272,1.77],[341,-397,2.04],[345,-496,2.24]]
s['tracks']['sofiaCamera']=sorted({a[0]:a for a in s['tracks']['sofiaCamera']}.values())
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'artwork.py';v=f.read_text()
a=v.index('@lru_cache(maxsize=90)')
v=v[:a]+'''@lru_cache(maxsize=65)
def sprite_portrait(key, base_color, disk_color, wink):
    """Place a generated head on an editable disk at the chosen shot scale."""
    disk = rounded_gradient(256,256,disk_color or base_color,base_color,128)
    variant = "lisa-wink" if key == "lisa" and wink else key
    path = Path(__file__).parent / "assets" / "portraits" / f"{variant}.png"
    with Image.open(path) as img:
        head = img.convert("RGBA")
    scale = min(188/head.width,198/head.height)
    head = head.resize((round(head.width*scale),round(head.height*scale)), Image.Resampling.LANCZOS)
    composite(disk,head,(256-head.width)/2,141-head.height/2)
    disk.putalpha(rounded_gradient(256,256,base_color,base_color,128).getchannel("A"))
    return disk


'''+v[a:]
f.write_text(v)
f=p/'render.py';v=f.read_text().replace('from artwork import rounded_gradient, stamp, text','from artwork import rounded_gradient, sprite_portrait, stamp, text')
v=v.replace('        stamp(im,portrait(tuple(self.s["avatars"][key]),bg,neutral),x,y,diam,opacity)','''        spec = self.s["avatars"][key]
        asset = (sprite_portrait(key,spec[0],bg,not neutral) if self.s.get("portraitSprites")
                 else portrait(tuple(spec),bg,neutral))
        stamp(im,asset,x,y,diam,opacity)''')
v=v.replace('        font_h=size*1.26','        font_h=size*1.22')
v=v.replace('text(d,x+11,start+j*font_h,line,size,ink,480)','text(d,x+max(11,size*.33),start+j*font_h,line,size,ink,480)')
v=v.replace('        self.chip(detached, right-177, bottom+5, 158, 64, c[8], True)','        self.chip(detached, right-177, bottom+5, 160, 66, c[8], True)')
v=v.replace('        dab=0','        dab=0')
v=v.replace('        if f < 353:\n            composite(im,blur(g,2.0*max(0,1-abs(f-337)/6)),x,y,1,s)','''        if f < 353:
            trail = 85*(1-tween(f,313,319))
            composite(im,vertical_blur(blur(g,2.0*max(0,1-abs(f-337)/6)),trail),x,y,1,s)''')
f.write_text(v)
