from pathlib import Path
import json

root=Path(__file__).parent
project=root/'title-project'
p=project/'scene.json'
scene=json.loads(p.read_text())
tracks=json.loads((root/'title-hearts-fit.json').read_text())
assert all(len(poses)==len(scene["tracks"]["personalHearts"]) for poses in tracks.values())
scene['titleHeartOptics']=tracks
p.write_text(json.dumps(scene,indent=2)+'\n')

p=project/'render.py'
code=p.read_text()
before='''def panel_wipe(im, masks, frame):'''
after='''def title_heart(canvas, pose):
    x,y,width,height,angle,alpha,shear,focus = pose
    if alpha<=0:
        return
    mark = curved_heart(180,180,(247,143,253))
    span = math.ceil(math.hypot(width*(1+abs(shear)),height)/2+4*focus+3)
    left,top=math.floor(x-span),math.floor(y-span)
    angle=math.radians(angle)
    cosine,sine = math.cos(angle),math.sin(angle)
    vx,vy = sine/height,cosine/height
    ux,uy = cosine/width-shear*vx,-sine/width-shear*vy
    matrix = (ux,uy,.5+ux*(left-x)+uy*(top-y),
              vx,vy,.5+vx*(left-x)+vy*(top-y))
    image = mark.transform((2*span+2,2*span+2),Image.Transform.AFFINE,
                           tuple(180*v for v in matrix),Image.Resampling.BICUBIC)
    composite(canvas,blur(image,focus),left,top,alpha)


def panel_wipe(im, masks, frame):'''
assert code.count(before)==1
code=code.replace(before,after)
before='''        for heart_track in self.s["tracks"]["personalHearts"]:
            x, cy, width, height, angle, alpha = interpolate(heart_track, f)
            if alpha <= 0:
                continue
            mark = curved_heart(round(width*2), round(height*2), (247, 143, 253))
            mark = mark.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
            composite(hearts, mark, x-mark.width/4, cy-mark.height/4, alpha, .5)'''
after='''        poses = self.s.get("titleHeartOptics",{}).get(str(f))
        if poses:
            for pose in poses:
                title_heart(hearts, pose)
        else:
            for heart_track in self.s["tracks"]["personalHearts"]:
                x, cy, width, height, angle, alpha = interpolate(heart_track, f)
                if alpha <= 0:
                    continue
                mark = curved_heart(round(width*2), round(height*2), (247, 143, 253))
                mark = mark.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
                composite(hearts, mark, x-mark.width/4, cy-mark.height/4, alpha, .5)'''
assert code.count(before)==1
p.write_text(code.replace(before,after))
