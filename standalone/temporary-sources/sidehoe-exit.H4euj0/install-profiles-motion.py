from pathlib import Path
import json

root=Path(__file__).parent
project=root/'project'
scene_path=project/'scene.json'
scene=json.loads(scene_path.read_text())
actors=json.loads((root/'new-profiles.json').read_text())
focus={267:(1.32,1.18),268:(1.13,1.06),269:(.87,.86),270:(.72,.73),
       287:(10.2,3.7),288:(3.5,2.65),289:(2.20,2.12),290:(1.34,1.33),
       306:(1.16,1.24),307:(1.60,1.84),308:(2.05,2.48),
       309:(2.4,3.25),310:(2.85,4.18),311:(3.45,6.2),312:(4.25,9.)}
for frame,poses in actors.items():
    f=int(frame)
    if f>=287 and poses[0]:
        chosen=poses[0]
        if f<289:
            chosen["wink"]=False
        else:
            chosen["wink"]=True
    scene.setdefault('profileMotionRegistration',{})[frame]=dict(actors=poses,focus=focus.get(f,(.63,.71)))
scene_path.write_text(json.dumps(scene,indent=2)+'\n')

path=project/'render.py'
code=path.read_text()
def edit(before,after):
    global code
    assert code.count(before)==1,before
    code=code.replace(before,after)
edit('''def registered_portrait(center_x, center_y, width, height, color, actor, head, *, gradient=None):''',
     '''def registered_portrait(center_x, center_y, width, height, color, actor, head, *, gradient=None,
                        head_opacity=1, right_fade=0):''')
edit('''        composite(sprite,art,x0-left,y0-top)
    sprite.putalpha(mask)
    return sprite,left,top''','''        composite(sprite,art,x0-left,y0-top,head_opacity)
    if right_fade:
        darkness = np.clip((columns-center_x)/(width*.52)+.15,0,1)
        mask = Image.fromarray(np.uint8(np.rint(opacity*(1-right_fade*darkness)*255)))
    sprite.putalpha(mask)
    return sprite,left,top''')
edit('''    def registered_profiles(self, im, frame, actors):''',
     '''    def registered_profiles(self, im, frame, actors, optics=None):''')
edit('''            label,actor,tag,_,_ = content
            asset="lisa-wink" if actor=="lisa" else actor
            sprite,left,top=registered_portrait(*pose["oval"],pose["tone"][0],asset,pose["head"],
                                                gradient=pose["tone"])
            composite(plate,sprite,left,top)
            fit_ink(plate,label,pose["name"],548,blur_radius=.40,
                    family=messages_font,ink=(3,3,3),fractional=True)''','''            if pose is None:
                continue
            label,actor,tag,_,_ = content
            asset="lisa-wink" if actor=="lisa" and pose.get("wink",True) else actor
            visibility=pose.get("veil",1)
            sprite,left,top=registered_portrait(*pose["oval"],pose["tone"][0],asset,pose["head"],
                                                gradient=pose["tone"],head_opacity=visibility,
                                                right_fade=(1-visibility)*.72 if index==1 else 0)
            composite(plate,sprite,left,top,visibility if index==2 and optics else 1)
            label = label[:pose["nameCharacters"]] if "nameCharacters" in pose else label
            fit_ink(plate,label,pose["name"],548,opacity=visibility,blur_radius=.40,
                    family=messages_font,ink=(3,3,3),fractional=True)''')
edit('''            ImageDraw.Draw(plate).rounded_rectangle((x0,y0,x1-1,y1-1),(y1-y0)*.46,
                                                     fill=tuple(pose["chipColor"]))
            marker,space,caption=tag.partition(" ")''','''            ImageDraw.Draw(plate).rounded_rectangle((x0,y0,x1-1,y1-1),(y1-y0)*.46,
                                                     fill=tuple(pose["chipColor"]))
            outline = pose.get("outline",0)
            if outline:
                rim = layer()
                ImageDraw.Draw(rim).rounded_rectangle((x0,y0,x1-1,y1-1),(y1-y0)*.46,
                                                       outline=(108,240,117,round(outline*245)),
                                                       width=3)
                composite(plate,rim,0,0)
            marker,space,caption=tag.partition(" ")''')
edit('''                composite(plate,glyph,x,y)
                tag=caption
            fit_ink(plate,tag,pose["text"],437,blur_radius=.35,family=messages_font,
                    ink=ink_colors[index],fractional=True)
        blur_after=.5+1.7*tween(frame,283,286)
        composite(im,blur(plate,blur_after),0,0)

    def profiles(self,im,f):
        registration = self.s.get("profileRegistrations",{}).get(str(f))''','''                composite(plate,glyph,x,y,visibility)
                tag=caption
            fit_ink(plate,tag,pose["text"],437,opacity=visibility,blur_radius=.35,family=messages_font,
                    ink=ink_colors[index],fractional=True)
        blur_after=tuple(optics) if optics else .5+1.7*tween(frame,283,286)
        composite(im,blur(plate,blur_after),0,0)

    def profiles(self,im,f):
        motion = self.s.get("profileMotionRegistration",{}).get(str(f))
        if motion:
            self.registered_profiles(im,f,motion["actors"],motion["focus"])
            return
        registration = self.s.get("profileRegistrations",{}).get(str(f))''')
path.write_text(code)
