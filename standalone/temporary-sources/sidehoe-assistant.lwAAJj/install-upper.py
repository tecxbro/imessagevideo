from pathlib import Path
import json
root=Path(__file__).parent
p=root/'project/scene.json'
s=json.loads(p.read_text())
s['assistantUpperBevel']=json.loads((root/'upper-fit.json').read_text())
p.write_text(json.dumps(s,indent=2)+'\n')

p=root/'project/render.py'
s=p.read_text()
helper='''def register_upper_bevel(stage, top, bottom, knots):
    """Align the independently painted rim and its reflection to the glass edge."""
    table = np.asarray(knots)
    left,right = max(0,int(table[0,0])-14),min(stage.width,int(table[-1,0])+15)
    cols = np.arange(left,right)
    y = np.arange(top,bottom)[:,None]
    a,b,u,v,contrast = [np.interp(cols,table[:,0],values) for values in table[:,1:].T]
    last=bottom-1
    mapped = np.where(y<a,top+(y-top)*(u-top)/(a-top),
             np.where(y<b,u+(y-a)*(v-u)/(b-a),v+(y-b)*(last-v)/(last-b)))
    mapped=np.clip(mapped-top,0,bottom-top-1)
    region=stage.crop((left,top,right,bottom))
    rgb=np.asarray(region.convert("RGB"),dtype=np.float32)
    i=np.floor(mapped).astype(int)
    fraction=(mapped-i)[...,None]
    cols_local=np.arange(right-left)
    warped=rgb[i,cols_local]*(1-fraction)+rgb[np.minimum(i+1,bottom-top-1),cols_local]*fraction
    paper=np.mean(rgb[:9],axis=0)
    rim = np.clip((y-a+14)/8,0,1)*np.clip((b+12-y)/8,0,1)
    warped+=rim[...,None]*(warped-paper)*(contrast-1)[None,:,None]
    edge = np.clip((cols-left)/14,0,1)*np.clip((right-1-cols)/14,0,1)
    result=rgb+(warped-rgb)*edge[None,:,None]
    stage.paste(Image.fromarray(np.uint8(np.rint(np.clip(result,0,255)))),(left,top))


'''
start='def assistant_intro_pin(stage, x, y, size, distortion):'
assert s.count(start)==1
s=s.replace(start,helper+start)
start='''        if optics and "flare" in optics:
            rail_flare(im,optics["flare"])
        title_y,=self.track("assistantTitleY", f)'''
replace='''        if optics and "flare" in optics:
            rail_flare(im,optics["flare"])
        upper_bevel=self.s.get("assistantUpperBevel",{}).get(str(f))
        if upper_bevel:
            register_upper_bevel(im,*upper_bevel)
        title_y,=self.track("assistantTitleY", f)'''
assert s.count(start)==1
p.write_text(s.replace(start,replace))
