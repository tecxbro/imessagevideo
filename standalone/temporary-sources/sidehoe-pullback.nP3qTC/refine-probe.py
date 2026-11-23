from pathlib import Path
import json

root=Path(__file__).parent
project=root/'project'
scene_path=project/'scene.json'
scene=json.loads(scene_path.read_text())
for frame,record in json.loads((root/'shutter-focus.json').read_text()).items():
    scene['sofiaPullbackOptics'][frame].update(record)
    if frame in {'357','358','359'}:
        scene['sofiaPullbackOptics'][frame]['history']=[0]*6
fit=json.loads((root/'badge-focus.json').read_text())
# Use the identified focus change on the film clock.
scene['tracks']['closingBadgeOptics']=[
    [int(f),*data['controls']] for f,data in fit.items()
]
scene_path.write_text(json.dumps(scene,indent=2)+'\n')

p=project/'render.py'
code=p.read_text()
def edit(before,after):
    global code
    assert code.count(before)==1,before
    code=code.replace(before,after)

edit('    if closing_finish is not None:\n        x0,y0=math.floor(left)-4,math.floor(top)-4',
     '    if closing_finish is not None:\n        pad=max(4,math.ceil(radius*4))\n        x0,y0=math.floor(left)-pad,math.floor(top)-pad')
edit('        width,height=math.ceil(left+w)-x0+4,math.ceil(top+h)-y0+4',
     '        width,height=math.ceil(left+w)-x0+pad,math.ceil(top+h)-y0+pad')
edit('            dx,dy,shutter_x,shutter_y,opacity = optics[key]',
     '            dx,dy,shutter_x,shutter_y,opacity,focus = optics[key]')
edit('            surface = vertical_blur(surface,shutter_y,horizontal=shutter_x)',
     '            surface = blur(vertical_blur(surface,shutter_y,horizontal=shutter_x),focus)')
edit('''        fitted_badge(im,box,corner,max(.36 if finish else 0,5*(1-tween(f,696,704))),
                     1,shine,closing_finish=finish)''','''        focus = max(.36 if finish else 0,5*(1-tween(f,696,704)))
        optics = self.s["tracks"].get("closingBadgeOptics")
        if optics and optics[0][0]<=f<=optics[-1][0]:
            dx,dy,sx,sy,radius = interpolate(optics,f)
            x,y,w,h = box
            box = x+dx,y+dy,w*sx,h*sy
            focus = math.hypot(focus,radius)
        fitted_badge(im,box,corner,focus,1,shine,closing_finish=finish)''')
p.write_text(code)

p=project/'artwork.py'
code=p.read_text()
edit('''        rear_pigments = ((False, (252,231,183), (243,161,213)),
                         (True, (254,228,185), (244,160,216)))''','''        rear_pigments = ((False, (250,228,186), (247,173,219)),
                         (True, (251,217,187), (245,166,227)))''')
edit('''        curve_polygon(d,(cx-side*15,268),(
            ((cx-side*20,257),(cx-side*16,235),(cx+side*22,230)),
            ((cx+side*31,236),(cx+side*33,247),(cx+side*33,252)),
            ((cx+side*18,259),(cx+side*1,265),(cx-side*15,268)),
        ),ink)''','''        shoulder = 5 if closing else 0
        curve_polygon(d,(cx-side*15,268+shoulder),(
            ((cx-side*20,257+shoulder),(cx-side*16,235),(cx+side*22,230)),
            ((cx+side*31,236),(cx+side*33,247+shoulder),(cx+side*33,252+shoulder)),
            ((cx+side*18,259+shoulder),(cx+side*1,265+shoulder),(cx-side*15,268+shoulder)),
        ),ink)''')
edit('''(1.024,0,-6.14,0,1.005,-.45)''','''(1.003,0,-.77,0,1.005,-.45)''')
edit('''    start, delta = ((248,226,174),(-2,-76,32)) if closing else ((249,226,177),(-4,-74,34))
    rgb = np.array(start) + ramp[:,None,None]*np.array(delta)
    rgb = rgb + light[None,:,None]*(1-ramp[:,None,None]) * ([4,9,2] if closing else [6,12,4])
    if closing:
        cheek = np.exp(-((np.arange(195)-53)/33)**2)
        rgb -= cheek[:,None,None]*[1,2,11]
''','''    if closing:
        rows,cols = np.mgrid[0:195,0:142]
        # Warm face illumination and rose at the bottom of the card.
        stops = (0,14,31,54,77,108,136,168,194)
        colors = ((248,237,193),(248,227,178),(248,216,164),
                  (247,203,163),(247,198,176),(247,192,190),
                  (246,179,195),(244,159,198),(244,153,205))
        pigment = np.stack([np.interp(rows,stops,c) for c in zip(*colors)],axis=2)
        across = (cols-70)/70
        glow = 1-across**2
        depth = rows/194
        rgb = (pigment + across[...,None]*[-.5,-2.8,3.1] + glow[...,None]*[1.2,-1.6,-3.9]
               + (across*depth)[...,None]*[0,-5.6,-2.7] + (glow*depth)[...,None]*[.2,1.2,8.8])
    else:
        rgb = np.array([249,226,177])+ramp[:,None,None]*[-4,-74,34]
        rgb += light[None,:,None]*(1-ramp[:,None,None])*[6,12,4]
''')
edit('        oval(d,79,48.8,21.9,22,ink)','        oval(d,80.5,49.5,20.9,21.25,ink)')
edit('    heart_height = 117 if closing else 114','    heart_height = 118 if closing else 114')
edit('    pigment_base = [247,158,218] if closing else [249,163,223]',
     '    pigment_base = [249,161,221] if closing else [249,163,223]')
p.write_text(code)
