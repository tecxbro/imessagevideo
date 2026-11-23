from pathlib import Path
import json
p=Path('sidehoe-skill-trial/project')
s=json.loads((p/'scene.json').read_text())
t=s['tracks']
t['identityY']=[[102,482],[105,498],[106,496],[109,482],[114,464],[119,461],[128,494],[130,519],[131,535],[132,558],[133,594]]
t['identitySize']=[[102,314],[105,283],[106,273],[109,251],[114,248],[119,247],[128,239],[130,239],[131,239],[132,240],[133,231]]
t['closingY']=[[696,528],[698,545],[700,522],[703,506],[708,497],[714,488],[716,474],[724,444],[732,439],[765,438],[777,438]]
t['closingSize']=[[696,185],[698,205],[700,229],[703,241],[708,246],[714,241],[716,231],[724,211],[732,209],[765,209],[777,209]]
s['followContact']['tipFromLowerRight']=[
 [-8,84,35],[-5,46,17],[-4,31,9],[-3,19,5],[-2,0,1],[-1,-9,-3],
 [0,-13,-6],[1,-15,-9],[3,-19,-11],[7,-25,-18],[10,-25,-18],[15,-24,-17],[21,-24,-14]]
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py';v=f.read_text()
v=v.replace('        s=mix(284,249,tween(f,103,114))','        s, = self.track("identitySize", f)')
v=v.replace('        stamp(im,badge(round(mix(70,128,up(f,105,113))/4)*4),500,y,s,a)','''        amount = 6*tween(f,129,133)
        stamp(im,blur(badge(round(mix(70,128,up(f,105,113))/4)*4),amount),500,y,s,a)''')
v=v.replace('        gentle_characters(im,self.c["brand"],500,y+s*.62,77,650,f,self.at("identity.name"),.75,True)','''        text_plate = layer()
        gentle_characters(text_plate,self.c["brand"],500,y+s*.63,77,650,f,self.at("identity.name")-1,.60,True)
        composite(im,blur(text_plate,amount),0,0)''')
v=v.replace('            shift = {135: 5, 136: 7, 137: 3}[f]\n            body = apply_fringe(body, shift, shift*.63)','''            shift = {135: 4, 136: 5, 137: 2}[f]
            curved = lens_ripple(body, {135: 8, 136: 13, 137: 6}[f])
            body = apply_fringe(curved, shift, shift*.55)''')
at=v.index('def panel_wipe(')
v=v[:at]+'''def lens_ripple(image, amplitude):
    """Local top-edge refraction, tapering independently down the phone face."""
    w,h = image.size
    strip_height = 240
    def displacement(x):
        local = (x-w*.49)/(w*.34)
        return amplitude*np.exp(-local*local)*np.sin((x-w*.50)*.104)
    mesh = []
    for x in range(0,w,12):
        right = min(w,x+12)
        dy_left,dy_right = displacement(x),displacement(right)
        mesh.append(((x,0,right,strip_height),
                     (x,dy_left,x,strip_height,right,strip_height,right,dy_right)))
    mesh.append(((0,strip_height,w,h),(0,strip_height,0,h,w,h,w,strip_height)))
    return image.transform(image.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)


'''+v[at:]
f.write_text(v)
f=p/'artwork.py';v=f.read_text()
a=v.index('    for x,y,angle,col in [(',v.index('def badge'))
b=v.index('    return im',a)
v=v[:a]+'''    for x,y,angle,col in [(92,121,18,"#e4aec2"),(163,121,-18,"#f1b7ca"),(127,108,2,"#eccb9a")]:
        card=rounded_gradient(54,76,col,"#dba1bc",6)
        d=ImageDraw.Draw(card)
        oval(d,27,19,7,7,"#4a3a40")
        d.rounded_rectangle((10,30,44,43),5,fill="#4a3a40")
        d.rounded_rectangle((12,50,42,54),2,fill="#886379")
        d.rounded_rectangle((17,60,37,63),1,fill="#886379")
        card=card.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
        composite(im,card,x-card.width/2,y-card.height/2)
    d=ImageDraw.Draw(im)
    heart(d,128,160,59,"#63405b")
    heart(d,128,159,51,"#f5a7d6")
'''+v[b:]
f.write_text(v)
