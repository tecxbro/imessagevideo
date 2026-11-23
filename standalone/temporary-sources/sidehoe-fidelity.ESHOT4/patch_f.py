from pathlib import Path
import json
p=Path('sidehoe-skill-trial/project')
s=json.loads((p/'scene.json').read_text())
fits=json.loads(Path('/tmp/sidehoe-fidelity.ESHOT4/wash-fits.json').read_text())
s['tracks']['titleWashFields']=fits['title']
s['tracks']['closingWashFields']=fits['closing']
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py';v=f.read_text()
start=v.index('def vertical_blur(')
v=v[:start]+'''@lru_cache(maxsize=42)
def measured_wash(controls):
    """Evaluate two editable light fields over the original stage matte."""
    yy,xx = np.mgrid[0:1:240j,0:1:240j]
    tint = np.zeros((240,240,3),dtype=np.float32)
    for offset in (0,8):
        cx,cy,sx,sy,shear,r,g,b = controls[offset:offset+8]
        light = np.exp(-((xx-cx+shear*(yy-cy))/sx)**2-((yy-cy)/sy)**2)
        tint += light[:,:,None]*np.array([r,g,b])
    rgb = np.rint(np.clip(253-tint,0,255)).astype(np.uint8)
    return Image.fromarray(rgb).resize((SIZE,SIZE),Image.Resampling.BICUBIC).convert("RGBA")


'''+v[start:]
v=v.replace('        strength, = self.track("personalWash", f)\n        im.alpha_composite(wash(round(40*strength)))','        fields = tuple(self.track("titleWashFields", f))\n        im.alpha_composite(measured_wash(fields))')
v=v.replace('        strength, = self.track("closingWash", f)\n        im.alpha_composite(wash(round(40*strength), "closing"))','        fields = tuple(self.track("closingWashFields", f))\n        im.alpha_composite(measured_wash(fields))')
f.write_text(v)
