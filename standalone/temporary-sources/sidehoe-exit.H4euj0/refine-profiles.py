from pathlib import Path
import json
root=Path(__file__).parent
p=root/'project/scene.json'
scene=json.loads(p.read_text())
for key,record in scene['profileMotionRegistration'].items():
    frame=int(key)
    for j,pose in enumerate(record['actors']):
        if not pose:
            continue
        x,y,w,h=pose['oval']
        min_width=[.265,.22,.155][j]*w
        if j==2 and frame<=270:
            pose['nameCharacters']={267:2,268:2,269:3,270:4}[frame]
        left,top,ink_width,ink_height=pose['name']
        good=ink_width>=min_width and ink_height>=h*.087 and ink_width<=w*.64
        if not good:
            width=w*[.335,.325,.45][j]
            text_y=max(top,y+h/2+h*.091)
            pose['name']=[round(z,3) for z in (x-width/2,text_y,width,max(h*.136,ink_height))]
        if j==1 and frame>=288:
            # Names and chips remain legible as the disk falls away.
            pose['veil']=max(pose['veil'],.20) if frame>=297 else pose['veil']
p.write_text(json.dumps(scene,indent=2)+'\n')
p=root/'project/render.py'
c=p.read_text()
def edit(a,b):
    global c
    assert c.count(a)==1,a
    c=c.replace(a,b)
edit('''                        head_opacity=1, right_fade=0):''',
     '''                        head_opacity=1, right_fade=0, head_wash=0, disk_wash=0):''')
edit('''        pixels[:,:,:3]=np.rint(tones[:,None,:])''',
     '''        tones=tones+(253-tones)*disk_wash
        pixels[:,:,:3]=np.rint(tones[:,None,:])''')
edit('''        composite(sprite,art,x0-left,y0-top,head_opacity)
    if right_fade:''','''        if head_wash:
            washed = Image.blend(art,Image.new("RGBA",art.size,(253,253,253,255)),head_wash)
            washed.putalpha(art.getchannel("A"))
            art=washed
        composite(sprite,art,x0-left,y0-top,head_opacity)
    if right_fade:''')
edit('''            visibility=pose.get("veil",1)
            sprite,left,top=registered_portrait(*pose["oval"],pose["tone"][0],asset,pose["head"],
                                                gradient=pose["tone"],head_opacity=visibility,
                                                right_fade=(1-visibility)*.72 if index==1 else 0)''','''            visibility=pose.get("veil",1)
            head_coverage,side_light,head_wash,disk_wash = pose.get(
                "exposure",(visibility,(1-visibility)*.72 if index==1 else 0,0,0))
            sprite,left,top=registered_portrait(*pose["oval"],pose["tone"][0],asset,pose["head"],
                                                gradient=pose["tone"],head_opacity=head_coverage,
                                                right_fade=side_light,head_wash=head_wash,
                                                disk_wash=disk_wash)''')
p.write_text(c)
