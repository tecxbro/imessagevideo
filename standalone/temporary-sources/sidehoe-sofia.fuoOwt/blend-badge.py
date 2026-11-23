from pathlib import Path
p=Path(__file__).parent/'project'
f=p/'artwork.py'
s=f.read_text()
s=s.replace('def badge(roundness, reveal=1, closing_finish=None):','def badge(roundness, reveal=1, closing_finish=None, refined=False):',1)
s=s.replace('''    ink = "#333333" if closing else "#333131"''','''    ink = "#333333" if refined else "#333131"''',1)
old='''    if closing:
        rear = Image.new("L", face.size)
        curve_polygon(ImageDraw.Draw(rear), (104, 198),('''
new='''    if closing:
        rear_pigments = ((False, (250,228,186), (247,173,219)),
                         (True, (251,217,187), (245,166,227)))
    if refined:
        rear = Image.new("L", face.size)
        curve_polygon(ImageDraw.Draw(rear), (104, 198),('''
assert old in s
s=s.replace(old,new,1)
s=s.replace('''        if closing:
            oval(d,cx+(.2 if right else .65),213.4,16.5,16.9,ink)
        else:''','''        if refined:
            oval(d,cx+(.2 if right else .65),213.4,16.5,16.9,ink)
        elif closing:
            oval(d,cx+(1 if right else 1.5),214,16.3,16.4,ink)
        else:''',1)
s=s.replace('''(cx-side*(17 if closing else 16),234 if closing else 235),(cx+side*22,229 if closing else 230)''','''(cx-side*(17 if refined else 16),234 if refined else 235),(cx+side*22,229 if refined else 230)''',1)
s=s.replace('''            transform=(.996,0,1.2,0,1.002,-.45) if right else (1.003,0,-.77,0,1.003,-.45)
            scaled''','''            transform = (1.003,0,-.77,0,1.005,-.45)
            if refined:
                transform = (.996,0,1.2,0,1.002,-.45) if right else (1.003,0,-.77,0,1.003,-.45)
            scaled''',1)
s=s.replace('''        pigment += (np.exp(-((rows-87)/75)**2))[...,None]*[1.1,2.4,3.2]''','''        if refined:
            pigment += np.exp(-((rows-87)/75)**2)[...,None]*[1.1,2.4,3.2]''',1)
s=s.replace('''        oval(d,80.0,49.2,21.65,22.7,ink)''','''        if refined:
            oval(d,80.0,49.2,21.65,22.7,ink)
        else:
            oval(d,80.5,49.5,20.9,21.25,ink)''',1)
s=s.replace('''        for width,row,height in ((109,116,8),(69,135.5,9)):''','''        bars = ((109,116,8),(69,135.5,9)) if refined else ((108,116,8),(69,135,8))
        for width,row,height in bars:''',1)
s=s.replace('''    if closing:
        composite(motif,curved_heart(136,118,(51,51,51)),187,280)''','''    if refined:
        composite(motif,curved_heart(136,118,(51,51,51)),187,280)''',1)
s=s.replace('''    heart_width,heart_height = (121,118) if closing else (124,114)''','''    heart_width = 121 if refined else 124
    heart_height = 118 if closing else 114''',1)
s=s.replace('''    pigment_base = [249,163,216] if closing else [249,163,223]''','''    pigment_base = [249,161,221] if closing else [249,163,223]
    if refined:
        pigment_base = [249,163,216]''',1)
s=s.replace('''    pink+=lower[...,None]*([2,34,35] if closing else [3,35,22])
    if closing:
        edges''','''    lower_glow = [2,35,26] if closing else [3,35,22]
    if refined:
        lower_glow = [2,34,35]
    pink+=lower[...,None]*lower_glow
    if refined:
        edges''',1)
s=s.replace('''    composite(motif,pigment,195 if closing else 193,288)''','''    composite(motif,pigment,(195 if refined else 194) if closing else 193,288)''',1)
f.write_text(s)
f=p/'render.py'
s=f.read_text()
s=s.replace('''def fitted_badge(im, box, corner, radius=0, opacity=1, shine=0, *, reveal=1, closing_finish=None):
    x,y,w,h=box
    mark=badge(corner,reveal,closing_finish)''','''def fitted_badge(im, box, corner, radius=0, opacity=1, shine=0, *, reveal=1,
                 closing_finish=None, motif_fit=0):
    x,y,w,h=box
    mark=badge(corner,reveal,closing_finish)
    if motif_fit:
        adjusted=badge(corner,reveal,closing_finish,refined=True)
        mark=Image.blend(mark,adjusted,motif_fit)''',1)
s=s.replace('''        fitted_badge(im,box,corner,focus,1,shine,closing_finish=finish)''','''        motif_track = self.s["tracks"].get("closingMotifFit")
        motif_fit = interpolate(motif_track,f)[0] if motif_track else 0
        fitted_badge(im,box,corner,focus,1,shine,closing_finish=finish,motif_fit=motif_fit)''',1)
f.write_text(s)
