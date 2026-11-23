from pathlib import Path
import json
p=Path('sidehoe-skill-trial/project')
s=json.loads((p/'scene.json').read_text())
t=s['tracks']
s['palette']['paper']='#fdfdfd'
t['inboxY'][7:11]=[[59,-758],[62,-1083],[66,-1230],[69,-1290],[72,-1321]]
t['assistantY']=[[134,265],[135,309],[136,341],[137,360],[140,398],[145,429],[154,464],[159,518],[161,574]]
t['assistantTitleY']=[[135,117],[139,180],[145,210],[154,239],[159,294],[161,430]]
t['personalTitleY']=[[162,464],[168,454],[180,460],[187,442],[195,416],[201,388],[205,350],[209,282],[212,200]]
t['calendarRight']=[[397,862],[405,871],[415,875],[420,877],[427,885],[431,896],[435,916],[442,932],[452,940],[460,940],[470,931],[478,910]]
t['calendarDay']=[[405,652,388],[408,686,312],[410,702,282],[412,712,262],[415,724,244],[420,734,234],[427,746,228],[431,756,220],[435,770,206],[442,780,194],[452,784,190],[460,784,190],[470,778,196],[473,776,198]]
t['personalWash']=[[162,1],[182,.94],[195,.90],[201,.82],[209,.76],[212,.74]]
t['closingWash']=[[712,0],[715,.10],[724,.37],[732,.67],[752,1.12],[765,1],[777,1]]
t['sendGroup']=[[353,0,-532,2.37],[355,0,-570,2.42],[360,-43,-696,2.61],[371,-44,-699,2.62],[385,-53,-697,2.67],[391,-55,-710,2.76],[396,-62,-721,2.81],[402,-70,-1020,2.85]]
t['sendCursor']=[[381,816,1021,0],[382,819,929,0],[384,823,866,0],[386,829,830,0],[388,839,784,0],[389,841,764,0],[391,843,733,0],[393,846,707,0],[394,850,688,0],[396,856,657,0],[402,869,359,0]]
t['profileCamera']=[[258,0,0,1],[275,10,14,1],[284,10,14,1],[289,160,4,1.23],[293,179,3,1.32],[303,195,17,1.39],[308,214,61,1.42],[312,205,403,1.42]]
s['clusterWipe']=[[254,0,324,67,71],[254,134,548,60,88],[254,516,585,73,61],[255,118,210,58,31],[255,0,491,122,56],[255,260,700,89,71],[255,683,392,58,71],[256,77,236,140,67],[256,349,227,156,104],[256,239,487,265,89],[256,563,487,84,126],[256,694,666,139,81],[257,124,320,590,67],[257,0,533,430,81],[257,427,381,496,123],[257,231,634,552,114]]
s['calendarWipe']=[[475,160,379,56,95],[475,300,379,169,30],[475,485,479,94,105],[475,674,379,111,30],[475,833,375,91,25],[476,231,409,130,78],[476,441,492,161,91],[476,711,484,121,93],[476,102,562,72,73],[477,232,488,125,167],[477,493,455,162,177],[477,843,482,139,99]]
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py'
v=f.read_text().replace('Image, ImageDraw, ImageFilter','Image, ImageChops, ImageDraw, ImageFilter').replace('BASE = "#fafafa"','BASE = "#fdfdfd"')
a=v.index('@lru_cache(maxsize=84)')
b=v.index('def gentle_characters',a)
v=v[:a]+'''@lru_cache(maxsize=84)
def wash(strength, variant="pink"):
    yy, xx = np.mgrid[0:1:240j, 0:1:240j]
    if variant == "apps":
        field = np.exp(-((xx-.47-.125*(yy-.50))/.269)**2-((yy-.50)/.25)**2)
        tint = field[:, :, None] * np.array([33.5, 57.7, .9])
    else:
        cx, cy, sx, sy, shear = (1.80, .97, 1.46, .455, 1.74) if variant == "closing" else (1.70, 1.03, 1.48, .42, 1.46)
        field = np.exp(-((xx-cx+shear*(yy-cy))/sx)**2-((yy-cy)/sy)**2)
        color = [28.7, 156.5, 18.2] if variant == "closing" else [26, 177, 14]
        tint = field[:, :, None] * np.array(color)
    data = np.uint8(np.clip(253-tint*(strength/40), 0, 255))
    return Image.fromarray(data).resize((SIZE, SIZE), Image.Resampling.BICUBIC).convert("RGBA")


def apply_fringe(image, x_offset, y_offset):
    r, g, b, alpha = image.split()
    def shift(channel, dx, dy):
        return channel.transform(channel.size, Image.Transform.AFFINE, (1, 0, dx, 0, 1, dy),
                                 Image.Resampling.BICUBIC)
    return Image.merge("RGBA", (shift(r, -x_offset, y_offset), g, shift(b, x_offset, -y_offset), alpha))


def panel_wipe(im, masks, frame):
    d = ImageDraw.Draw(im)
    for onset, x, y, width, height in masks:
        if frame >= onset:
            d.rectangle((x, y, x+width, y+height), fill=(0, 0, 0, 0))


'''+v[b:]
a=v.index('def phone_shell(');b=v.index('def status',a)
v=v[:a]+'''@lru_cache(maxsize=8)
def shell_material(w, h, radius):
    yy, xx = np.mgrid[:h, :w]
    edge_x = np.abs(xx-(w-1)/2)-(w/2-radius-1)
    edge_y = np.abs(yy-(h-1)/2)-(h/2-radius-1)
    distance = np.hypot(np.maximum(edge_x,0), np.maximum(edge_y,0))
    distance += np.minimum(np.maximum(edge_x,edge_y),0)-radius
    bevel = max(9, round(w*.027))
    inset = -distance
    peak = np.exp(-((inset-bevel*.23)/max(1.3,bevel*.16))**2)
    light = (23 + peak*(32+73*np.exp(-yy/(h*.21)))
             + 33*np.exp(-((xx-w*.15)/(w*.12))**2)*np.exp(-yy/(h*.17)))
    glass = np.clip((inset-bevel+.5)*1.1,0,1)
    rgb = light*(1-glass)+253*glass
    alpha = np.clip(inset+.5,0,1)*255
    pixels = np.stack((rgb,rgb,np.minimum(rgb+2,253),alpha),axis=2).astype(np.uint8)
    return Image.fromarray(pixels)


def phone_shell(im, w, h, radius):
    im.alpha_composite(shell_material(w, h, radius))


'''+v[b:]
v=v.replace('color=tuple(round(mix(250,v,a)) for v in color)','color=tuple(round(mix(253,v,a)) for v in color)')
v=v.replace('5*max(0,1-abs(f-57)/6)','11*max(0,1-abs(f-57)/9)')
v=v.replace('        composite(im,blur(beneath,3*(1-tween(f,134,139))+4*tween(f,158,161)),50,y)\n        amount=round(34*tween(f,138,162))\n        if amount:\n            im.alpha_composite(Image.blend(im,wash(amount),.44))','''        # Add the first inbox row inside the handset's measured bottom crop.
        self.avatar(beneath,"danielle",126,567,64,tween(f,136,141))
        text(d,179,534,"Natalie",32,INK,620)
        text(d,179,581,"See you soon!",25,MUTED)
        text(d,814,535,"1:50 AM",22,MUTED,500,"right")
        body = blur(beneath,3.8*(1-tween(f,134,139))+4*tween(f,158,161))
        if 135 <= f <= 137:
            shift = {135: 5, 136: 7, 137: 3}[f]
            body = apply_fringe(body, shift, shift*.63)
        composite(im,body,50,y)
        amount = round(37*tween(f,135,155))
        if amount:
            from PIL import ImageChops
            overlay = wash(amount).convert("RGB")
            im.paste(ImageChops.multiply(im.convert("RGB"), overlay))''')
v=v.replace('        for j,line in enumerate(self.c["assistant"]):\n            gentle_characters(im,line,500,215+j*64+max(0,y-441)*.65,57,640,f,135+j*3,.31)','''        title_y, = self.track("assistantTitleY", f)
        for j,line in enumerate(self.c["assistant"]):
            gentle_characters(im,line,500,title_y+j*64,60,640,f,135+j*3,.31)''')
v=v.replace('im.alpha_composite(wash(round(36+4*tween(f,start,210))))\n        y=455-530*tween(f,202,214)\n        gentle_characters(im,self.c["personal"][0],500,y,56,630,f,start,.27)',
'''strength, = self.track("personalWash", f)
        im.alpha_composite(wash(round(40*strength)))
        y, = self.track("personalTitleY", f)
        gentle_characters(im,self.c["personal"][0],500,y,65,660,f,start,.17)''')
v=v.replace('500,y+60,77,760,f,onset,.48,True','500,y+57,94,765,f,onset,.38,True')
v=v.replace('[(217,90,22),(243,122,16),(270,143,14),(722,117,16),(763,78,17),(771,124,23),(736,147,11)]','[(238,96,24),(253,118,29),(223,78,19),(746,100,22),(767,75,19),(767,124,24),(743,138,19)]').replace('1-tween(f,194+i*.5,211)','1-tween(f,201+i*.5,212)')
a=v.index('        if f>=self.at("profiles.mosaic"):');b=v.index('    def profiles(',a)
v=v[:a]+'''        grow = .86+.28*tween(f,222,251)
        scale_y = 492-500*grow
        if f >= self.at("profiles.mosaic"):
            stage = layer()
            composite(stage,content,500-500*grow-29*(f-253),scale_y,1,grow)
            panel_wipe(stage,self.s["clusterWipe"],f)
            composite(im,blur(stage,1+1.8*(f-254)),0,0,1-.13*(f-254))
        else:
            composite(im,blur(content,5*(1-tween(f,213,221))),500-500*grow,scale_y,1,grow)

'''+v[b:]
v=v.replace('tween(f,287,302)*j*.48','tween(f,287,300)*j*.70')
v=v.replace('        right=1000-left*.42\n        first=left+20\n        last=right-31','''        right, = self.track("calendarRight", f)
        day_x, day_y = self.track("calendarDay", f)
        step = (right-left)/6.3
        first = day_x-5*step''').replace('            x=mix(first,last,j/6)','            x=first+j*step').replace('oval(d,x,y0-h*.60,h*.335,h*.335,"#ef3046")','oval(d,day_x,day_y,h*.335,h*.335,"#ef3046")').replace('text(d,x,y0-h*.74,str(num),h*.33,dark,555,"center")','text(d,x,(day_y-h*.15) if num==21 else y0-h*.74,str(num),h*.33,dark,555,"center")')
a=v.index('        if f>=self.at("calendar.mosaic"):');b=v.index('    def apps(',a)
v=v[:a]+'''        if f>=self.at("calendar.mosaic"):
            panel_wipe(cal,self.s["calendarWipe"],f)
        composite(im,blur(cal,4.5*(1-tween(f,398,410))+2*tween(f,472,479)),
                  0,0,tween(f,397,405)*(1-tween(f,477,482)))

'''+v[b:]
v=v.replace('cursor(im,x,y,r,1-tween(f,397,403),.89)','cursor(im,x,y,r,1-tween(f,397,403),1.23)')
v=v.replace('strength=round(48*tween(f,709,764))\n        im.alpha_composite(wash(strength))','strength, = self.track("closingWash", f)\n        im.alpha_composite(wash(round(40*strength), "closing"))')
v=v.replace('587+j*56+17*(1-p)','590+j*57+17*(1-p)')
v=v.replace('        elif f<258:', '        elif f<258:') 
v=v.replace('        if 397<=f<480:\n            self.calendar(im,f)\n        if 478<=f<622:\n            self.apps(im,f)\n            if f<480:\n                self.calendar(im,f)','        if 478<=f<622:\n            self.apps(im,f)\n        if 397<=f<482:\n            self.calendar(im,f)')
v=v.replace('            from PIL import ImageChops\n','')
f.write_text(v)
