from pathlib import Path
import json
from PIL import Image
import numpy as np
r=Path(__file__).parent
p=r/'project/render.py'
s=p.read_text()
a=s.index('    width, height = body.size\n',s.index('def register_lens_rails'))
b=s.index('\n\ndef assistant_intro_pin',a)
s=s[:a]+'''    width, height = body.size
    controls = np.asarray(knots)
    rows = np.arange(height)
    values = np.array([np.interp(rows,controls[:,0],column)
                       for column in controls[:,1:].T]).T
    data = np.asarray(body.convert("RGBa"))
    result = data.copy()
    for side, (left,right) in enumerate(((0,166),(width-166,width))):
        columns = np.arange(left,right)
        warp = values[:,side*4:(side+1)*4]
        for y,(a,b,c,d) in enumerate(warp):
            source_x = np.interp(columns,(left,a,b,right),(left,c,d,right))
            ix = source_x.astype(int)
            fraction = (source_x-ix)[:,None]
            result[y,left:right] = np.rint(
                data[y,ix]*(1-fraction)+data[y,np.minimum(ix+1,width-1)]*fraction)
    return Image.fromarray(result,mode="RGBa").convert("RGBA")
'''+s[b:]
s=s.replace('left,top,width,height = optics["inbox"]','left,top,width,ink_height = optics["inbox"]').replace('(left,top,width,height),700','(left,top,width,ink_height),700')
s=s.replace('''            lens_raster = [[0,0],[left,0],[left+30,8],[left+57,-8],
                           [left+82,7],[left+106,-5],[left+width,0]]
            composite(beneath,lens_ripple(title,lens_raster),0,0)''','''            # A short refraction passes over the title as the handset comes into focus.
            pad = 24
            box=(left-pad,top-pad,left+width+pad,top+ink_height+pad)
            raster=title.crop(box)
            mesh=[]
            for i in range(0,raster.width,5):
                j=min(i+5,raster.width)
                dy1,dy2=(8*math.sin((x-pad)/7.3)*math.exp(-((x-pad-width*.48)/(width*.5))**2)
                         for x in (i,j))
                mesh.append(((i,0,j,raster.height),
                            (i,dy1,i,raster.height+dy1,j,raster.height+dy2,j,dy2)))
            visible = raster.transform(raster.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
            composite(beneath,visible,box[0],box[1])''')
p.write_text(s)
p=r/'project/scene.json'
config=json.loads(p.read_text())
rows=config['tracks']['assistantRowPose']
rows.append([138,581.5,.97])
rows.sort()
config['assistantEntranceOptics']['134']['inbox']=[361,191,177,39]
p.write_text(json.dumps(config,indent=2)+'\n')
