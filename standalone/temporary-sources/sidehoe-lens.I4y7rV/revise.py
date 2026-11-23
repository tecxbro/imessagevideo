from pathlib import Path
import json
from PIL import Image
import numpy as np
root = Path(__file__).parent
render = root/'project/render.py'
text = render.read_text()
where = 'def panel_wipe(im, masks, frame):'
addition = '''def register_lens_rails(body, knots):
    """Register each editable casing rail between the outside and glass contours."""
    width, height = body.size
    controls = np.asarray(knots)
    mesh = []
    for top in range(0, height, 12):
        bottom = min(height, top+12)
        upper, lower = [np.array([np.interp(y, controls[:,0], column)
                                  for column in controls[:,1:].T]).reshape(2,4)
                        for y in (top,bottom)]
        for side, edges in enumerate(((0,166),(width-166,width))):
            start, end = edges
            u, v = upper[side], lower[side]
            target = (start,round((u[0]+v[0])/2),round((u[1]+v[1])/2),end)
            source_upper = (start,u[2],u[3],end)
            source_lower = (start,v[2],v[3],end)
            for i,(left,right) in enumerate(zip(target,target[1:])):
                mesh.append(((left,top,right,bottom),
                             (source_upper[i],top,source_lower[i],bottom,
                              source_lower[i+1],bottom,source_upper[i+1],top)))
        mesh.append(((166,top,width-166,bottom),
                     (166,top,166,bottom,width-166,bottom,width-166,top)))
    return body.transform(body.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)


def assistant_intro_pin(stage, x, y, size, distortion):
    """Render the first pin through the same moving glass as the casing."""
    pad = 24
    diameter = round(size)
    pin = layer(diameter+2*pad,diameter+2*pad)
    center = pin.width/2
    stamp(pin,badge(128),center,center,diameter)
    mesh = []
    for top in range(0,pin.height,4):
        bottom = min(top+4,pin.height)
        delta = []
        for row in (top,bottom):
            t = (row-center)/diameter
            alpha = math.exp(-((t+.37)/.19)**2)
            delta.append(distortion*alpha*(math.sin(t*30)+.39*math.cos(t*44)))
        mesh.append(((0,top,pin.width,bottom),
                     (delta[0],top,delta[1],bottom,pin.width+delta[1],bottom,
                      pin.width+delta[0],top)))
    pin = pin.transform(pin.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
    pin = apply_fringe(pin,3.2,2.3)
    composite(stage,pin,x-center,y-center)


def rail_flare(stage, controls):
    """Cast the exit-side prism color along the lower rails."""
    y,x = np.mgrid[880:SIZE,0:SIZE]
    rgb = np.asarray(stage.crop((0,880,SIZE,SIZE)).convert("RGB"),dtype=float)
    for cx,cy,rx,ry,angle,red,green,blue in controls:
        light = np.exp(-((x-cx-(y-cy)*angle)/rx)**2-((y-cy)/ry)**2)
        rgb += light[...,None]*[red,green,blue]
    stage.paste(Image.fromarray(np.uint8(np.clip(np.rint(rgb),0,255))),(0,880))


'''
text = text.replace(where,addition+where,1)
text = text.replace('''        beneath=layer(900,830)
        bevel, = self.track("assistantBevelDepth",f)
        beneath.alpha_composite(shell_material(900,830,163,bevel/900,True))''','''        optics = self.s.get("assistantEntranceOptics",{}).get(str(f))
        height = 1030 if f==134 and optics else 830
        beneath=layer(900,height)
        bevel, = self.track("assistantBevelDepth",f)
        beneath.alpha_composite(shell_material(900,height,163,bevel/900,True))''',1)
text = text.replace('''        text(d,450,207,self.c["inbox"],36,INK,650,"center")''','''        if optics and "inbox" in optics:
            left,top,width,height = optics["inbox"]
            title = layer()
            fit_ink(title,self.c["inbox"],(left,top,width,height),700,
                    1,1,family=messages_font,ink=(27,27,28))
            lens_raster = [[0,0],[left,0],[left+30,8],[left+57,-8],
                           [left+82,7],[left+106,-5],[left+width,0]]
            composite(beneath,lens_ripple(title,lens_raster),0,0)
        else:
            text(d,450,207,self.c["inbox"],36,INK,650,"center")''',1)
text = text.replace('''        stamp(beneath,badge(128),px,py,diam)
        ld.text''','''        if optics and "pin" in optics:
            assistant_intro_pin(beneath,*optics["pin"])
        else:
            stamp(beneath,badge(128),px,py,diam)
        ld.text''',1)
text = text.replace('''        if f==134:
            body=vertical_blur(body,17)''','''        if f==134:
            body = vertical_blur(body,12 if optics else 17)''',1)
text = text.replace('''        composite(im,body.resize((round(width),body.height),Image.Resampling.BICUBIC),x,y)
        pose = self.track("assistantLighting",f)''','''        if optics and "rails" in optics:
            body = register_lens_rails(body,optics["rails"])
        composite(im,body.resize((round(width),body.height),Image.Resampling.BICUBIC),x,y)
        pose = self.track("assistantLighting",f)''',1)
text = text.replace('''        if prism:
            spectral_rim(im,prism)
        title_y''','''        if prism:
            spectral_rim(im,prism)
        if optics and "flare" in optics:
            rail_flare(im,optics["flare"])
        title_y''',1)
render.write_text(text)
scene = root/'project/scene.json'
config = json.loads(scene.read_text())
config['assistantEntranceOptics'] = {
    '134':{'pin':[449,403,254,4.5],'inbox':[366,195,176,39]},
    '135':{},
    '136':{},
    '137':{},
}
for key, rows in {
    'assistantIslandBox':{134:[315,61,276,96],135:[314,53,273,87],136:[313,59,273,84],137:[314,62,274,82]},
    'assistantBodyFocus':{134:[5],135:[4.2],136:[3.6],137:[3.4]},
    'assistantPinControls':{134:[183,718,203,0,0,.31],135:[183,718,183,-2,.34,.37],136:[183,719,186,-1,.76,.58]},
    'assistantRowPose':{135:[576,.37],136:[567,.82],137:[573,.94]}
}.items():
    for i,row in enumerate(config['tracks'][key]):
        if row[0] in rows:
            config['tracks'][key][i] = [row[0],*rows[row[0]]]
scene.write_text(json.dumps(config,indent=2)+'\n')
