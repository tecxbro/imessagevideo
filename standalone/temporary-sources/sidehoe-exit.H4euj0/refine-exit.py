from pathlib import Path
import json

p=Path(__file__).parent/'project'
scene_file=p/'scene.json'
scene=json.loads(scene_file.read_text())
follow=scene['threadRegistration']['follow']
for f,control in {
  '694': {
     'focus':[6,-9,2.2], 'railStart':0, 'railBlend':[0,75],
     'header':[44,504,-17,47,43,3.5],
     'controls':[[246,501,122,46],[377,503,112,44]],
     'controlFocus':2.9,'controlLight':.42,
  },
  '695': {
     'focus':[3,9,1.62], 'railStart':0, 'railBlend':[16,120],
     'header':[120,504,46,47,58,2.7],
     'controls':[[291,501,100,34],[402,503,89,34]],
     'controlFocus':2.45,'controlLight':.24,
  }
}.items():
    follow[f].update(control)
scene_file.write_text(json.dumps(scene,indent=2)+'\n')

render=p/'render.py'
s=render.read_text()
def edit(before,after):
    global s
    assert s.count(before)==1,before
    s=s.replace(before,after)
edit('''            im.paste(rail,(start,upper_limit))
        zoom=(r-l)/376''','''            ramp = registration.get("railBlend")
            if ramp:
                fade = np.interp(np.arange(upper_limit,SIZE),ramp,(0,255)).astype(np.uint8)
                mask = Image.fromarray(np.broadcast_to(fade[:,None],(rail.height,rail.width)))
                im.paste(rail,(start,upper_limit),mask)
            else:
                im.paste(rail,(start,upper_limit))
        zoom=(r-l)/376''')
edit('''        if measured and measured["no"]:
            lx,ty,rx,by=measured["no"]''','''        release = measured if measured and "header" in measured else None
        if measured and measured["no"]:
            lx,ty,rx,by=measured["no"]''')
edit('''        self.chip(plate,no_x,no_y,no_w,no_h,self.c["follow"][4],False,.58+.42*a,a,
                  glyph=face,follow_style=True)''','''        if not release:
            self.chip(plate,no_x,no_y,no_w,no_h,self.c["follow"][4],False,.58+.42*a,a,
                      glyph=face,follow_style=True)''')
edit('''        self.chip(plate,left,top,width,height,self.c["follow"][5],True,.58+.42*b,b,tapped,
                  glyph=face,follow_style=True)''','''        if not release:
            self.chip(plate,left,top,width,height,self.c["follow"][5],True,.58+.42*b,b,tapped,
                      glyph=face,follow_style=True)''')
edit('''        if measured:
            self.staged_thread(im,"follow",measured,f)
            if tapped:
                center_x=x+(left+width*.77)*s''','''        if release:
            bottom,cx,cy,w,h,focus = release["header"]
            header=layer()
            rail_left,rail_right = release["rails"]
            ImageDraw.Draw(header).rectangle((rail_left,0,rail_right,bottom),fill="#f0f0f2")
            if f==695:
                d=ImageDraw.Draw(header)
                d.line((271,43,260,52,271,61),fill="#559cf5",width=4)
                d.rounded_rectangle((727,45,742,59),3,outline="#6fa1f0",width=2)
                d.polygon([(743,51),(751,45),(751,58)],outline="#6fa1f0")
                fit_ink(header,self.c["follow"][0],(487,80,35,11),510,
                        family=messages_font,ink=(41,41,42),fractional=True)
            fitted_badge(header,(cx,cy,w,h),128,opacity=1)
            composite(im,blur(header,focus),0,0)
        if measured:
            self.staged_thread(im,"follow",measured,f)
            if release:
                controls=layer()
                for j,(cx,cy,w,h) in enumerate(release["controls"]):
                    self.chip(controls,cx,cy,w,h,self.c["follow"][j+4],bool(j),1,
                              1 if j==0 else .87,tapped,
                              glyph=face,follow_style=True)
                composite(im,blur(controls,release["controlFocus"]),0,0)
            if tapped:
                center_x=x+(left+width*.77)*s''')
edit('''                light.putalpha(Image.fromarray(np.uint8(np.rint(alpha*63))))
                composite(im,light,fx,fy)''','''                light.putalpha(Image.fromarray(np.uint8(np.rint(alpha*63))))
                composite(im,light,fx,fy,release["controlLight"] if release else 1)''')
render.write_text(s)
