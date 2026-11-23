from pathlib import Path
import json

root=Path(__file__).parent
before=Path('/tmp/sidehoe-follow-entry.0vQCoz')
project=root/'project'
scene_path=project/'scene.json'
scene=json.loads(scene_path.read_text())
config={}
fit=json.loads((before/'sofia-shutter-fit.json').read_text())
for f in range(355,360):
    upper,lower=[r[2][:] for r in fit[str(f)]]
    if f==356:
        upper[-1]*=.5
    if f>=357:
        upper=[0,0,0,0,0]
    config[str(f)]=dict(history=upper,composerAndKeyboard=lower)
config['355']['rail']=[(936,253),(941,205),(946,113),(951,15),(953,19),(958,48),
                          (964,85),(967,94),(971,124),(976,176),(981,229),(985,253)]
config['356']['rail']=[(933,253),(938,239),(943,179),(948,129),(951,132),(959,145),
                          (969,174),(977,175),(982,202),(986,231),(992,253)]
config['355']['leftRim']=[(0,231),(2,228),(5,231),(8,244),(10,250),(13,253)]
scene['sofiaPullbackOptics']=config
scene_path.write_text(json.dumps(scene,indent=2)+'\n')

render=project/'render.py'
code=render.read_text()
method='''    def sofia_pullback(self, im, frame, optics, x, y, scale, keyboard_y):
        plate = self.thread_plate("sofia", frame, keyboard_y)
        inside = Image.new("L", plate.size)
        ImageDraw.Draw(inside).rounded_rectangle((14,14,385,812),52,fill=255)
        plate.putalpha(inside)

        # The outgoing screen appears in two exposure planes. Leave room
        # for off-screen motion to contribute to the first visible rows.
        margin = 76
        plate = plate.resize((round(plate.width*scale),round(plate.height*scale)),
                             Image.Resampling.BICUBIC)
        stage_height = SIZE+2*margin
        rows = np.arange(plate.height) + y
        upper = np.interp(rows,[550,705],[1,0])
        for key, coverage in (("history",upper),("composerAndKeyboard",1-upper)):
            dx,dy,shutter_x,shutter_y,opacity = optics[key]
            if opacity <= 0:
                continue
            surface = layer(stage_height,stage_height)
            exposure = plate.copy()
            mask = np.asarray(exposure.getchannel("A"),dtype=np.float32)
            exposure.putalpha(Image.fromarray(np.uint8(np.rint(mask*coverage[:,None]))))
            composite(surface,exposure,x+margin+dx,y+margin+dy)
            surface = vertical_blur(surface,shutter_y,horizontal=shutter_x)
            composite(im,surface.crop((margin,margin,margin+SIZE,margin+SIZE)),0,0,opacity)

        # The right bevel catches light after the screen slips out of view.
        for key in ("rail","leftRim"):
            if key not in optics:
                continue
            stops = np.asarray(optics[key],dtype=float)
            left,right = int(stops[0,0]),int(stops[-1,0])+1
            levels = np.interp(np.arange(left,right),stops[:,0],stops[:,1])
            shade = np.broadcast_to(levels,(SIZE,right-left))
            hardware = Image.fromarray(np.uint8(np.rint(shade)))
            im.paste(hardware.convert("RGB"),(left,0))

'''
start='    def sofia(self,im,f):'
assert code.count(start)==1
code=code.replace(start,method+start)
before='''        measured = self.s.get("threadRegistration",{}).get("sofia",{}).get(str(f))
        if a>0:
'''
after='''        measured = self.s.get("threadRegistration",{}).get("sofia",{}).get(str(f))
        pullback = self.s.get("sofiaPullbackOptics",{}).get(str(f))
        if pullback:
            self.sofia_pullback(im,f,pullback,x,y,s,keyboard_y)
        elif a>0:
'''
assert code.count(before)==1
render.write_text(code.replace(before,after))
