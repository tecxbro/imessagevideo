from pathlib import Path
import json
root=Path(__file__).parent
p=root/'project/scene.json'
s=json.loads(p.read_text())
rails=json.loads((root/'lower-sides.json').read_text())
rails['136'].pop('left',None)
s['assistantSideBevels']=rails
p.write_text(json.dumps(s,indent=2)+'\n')

p=root/'project/render.py'
s=p.read_text()
s=s.replace('def register_upper_bevel(stage, top, bottom, knots):','def register_bevel(stage, top, bottom, knots):')
before='''        if upper_bevel:
            register_upper_bevel(im,*upper_bevel)
        title_y,=self.track("assistantTitleY", f)'''
after='''        if upper_bevel:
            register_bevel(im,*upper_bevel)
        side_bevels=self.s.get("assistantSideBevels",{}).get(str(f))
        if side_bevels:
            cross_section = im.transpose(Image.Transpose.TRANSPOSE)
            if "left" in side_bevels:
                register_bevel(cross_section,*side_bevels["left"])
            if "right" in side_bevels:
                cross_section = cross_section.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                register_bevel(cross_section,*side_bevels["right"])
                cross_section = cross_section.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            im.paste(cross_section.transpose(Image.Transpose.TRANSPOSE),(0,0))
        title_y,=self.track("assistantTitleY", f)'''
assert s.count(before)==1
p.write_text(s.replace(before,after))
