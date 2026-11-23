from pathlib import Path
import json

root=Path(__file__).parent
project=root/'title-project'
p=project/'scene.json'
s=json.loads(p.read_text())
scans=json.loads((root/'glyph-fit-all.json').read_text())
lines=[]
for j,caption in enumerate(s['copy']['personal']):
    words=caption.split()
    frames={}
    for frame,values in scans.items():
        fitted=values[j]
        assert len(fitted)==sum(map(len,words)), (frame,caption)
        if any(not row for row in fitted):
            continue
        frames[frame]=[q[2:8] for q in fitted]
    lines.append(dict(caption=caption,frames=frames))
s['personalGlyphRegistration']=lines
p.write_text(json.dumps(s,indent=2)+'\n')

p=project/'render.py'
code=p.read_text()
before='''                if layout and layout[0][0]<=f<=layout[-1][0] and len(layout[0])==1+7*len(words):
                    controls = interpolate(layout,f)
                    for pos,word in enumerate(words):'''
after='''                glyphs = self.s.get("personalGlyphRegistration")
                lettering = glyphs[index] if glyphs else None
                letter_poses = lettering["frames"].get(str(f)) if lettering and caption==lettering["caption"] else None
                if letter_poses:
                    controls = interpolate(layout,f)
                    drawn = iter(letter_poses)
                    for pos,word in enumerate(words):
                        weight = controls[pos*7+4]
                        for char in word:
                            gx,gy,gw,gh,focus,opacity = next(drawn)
                            fit_ink(title,char,(gx,gy,gw,gh),weight,min(1,opacity),focus,
                                    family=messages_font,ink=color,fractional=True)
                elif layout and layout[0][0]<=f<=layout[-1][0] and len(layout[0])==1+7*len(words):
                    controls = interpolate(layout,f)
                    for pos,word in enumerate(words):'''
assert code.count(before)==1
p.write_text(code.replace(before,after))
