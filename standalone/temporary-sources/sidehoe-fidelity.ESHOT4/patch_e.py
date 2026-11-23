from pathlib import Path
import json
p=Path('sidehoe-skill-trial/project')
s=json.loads((p/'scene.json').read_text())
t=s['tracks']
t['sendCursor']=[a for a in t['sendCursor'] if a!=[393,843,649,0]]+[[402,860,454,0]]
t['assistantY']=[[134,266],[135,307],[136,333],[137,356],[140,394],[145,420],[154,456],[159,517],[161,566]]
t['assistantTitleY']=[[135,117],[139,177],[145,211],[154,239],[159,294],[161,430]]
t['personalTitleY'][-2:]=[[209,279],[212,245]]
t['clusterPose'][0]=[213,-22,164,.92]
s['profileStartingFrames']=[257,259,261]
# Move the glossy foreground separately from the tint painted onto it.
t['assistantWash']=[[134,0],[136,.09],[140,.24],[145,.62],[154,1],[159,.96],[161,.91]]
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py';v=f.read_text()
v=v.replace('    return im.filter(ImageFilter.GaussianBlur(radius)) if radius > .25 else im','''    if radius <= .25:
        return im
    return im.convert("RGBa").filter(ImageFilter.GaussianBlur(radius)).convert("RGBA")''')
v=v.replace('        color = [28.7, 156.5, 18.2] if variant == "closing" else [26, 177, 14]\n        tint = field[:, :, None] * np.array(color)','''        color = [28.7, 156.5, 18.2] if variant == "closing" else [20, 135, 10]
        tint = field[:, :, None] * np.array(color)
        if variant == "pink":
            edge = np.exp(-((xx-1.0)/.23)**2-((yy-.96)/.25)**2)
            tint += edge[:,:,None]*np.array([7,34,5])''')
v=v.replace('    mixed = image\n    count = min(13, max(3, round(length/5)))','    image = image.convert("RGBa")\n    mixed = image\n    count = min(13, max(3, round(length/5)))').replace('    return mixed\n','    return mixed.convert("RGBA")\n')
v=v.replace('    bevel = max(9, round(w*.027))','    bevel = max(10, round(w*.032))')
v=v.replace('    d=ImageDraw.Draw(im,"RGBA")\n    face=font(size,weight)','''    d=ImageDraw.Draw(im,"RGBA")
    if f >= onset+spacing*(len(label)-1)+7:
        text(d,x,y,label,size,(21,21,21),weight,"center")
        return
    face=font(size,weight)''')
v=v.replace('    def avatar(self,im,key,x,y,diam,opacity=1,bg="",neutral=False):','    def avatar(self,im,key,x,y,diam,opacity=1,bg="",neutral=False):')
v=v.replace('        amount = round(37*tween(f,135,155))','        tint, = self.track("assistantWash", f)\n        amount = round(42*tint)')
v=v.replace('f,134+j*2,.27','f,134+j*4,.20')
v=v.replace('        gentle_characters(im,self.c["personal"][0],500,y,65,660,f,start-2,.17)','''        title = layer()
        gentle_characters(title,self.c["personal"][0],500,y,65,660,f,start-2,.17)''')
v=v.replace('        gentle_characters(im,self.c["personal"][1],500,y+57,94,765,f,onset,.38,True)\n        d=ImageDraw.Draw(im)','''        gentle_characters(title,self.c["personal"][1],500,y+57,94,765,f,onset,.38,True)
        d=ImageDraw.Draw(title)''')
v=v.replace('    def cluster(self,im,f):','''        composite(im,vertical_blur(title,30*tween(f,205,212)),0,0)

    def cluster(self,im,f):''')
v=v.replace('            onset=self.at("profiles.directory")+j*2-1','            onset=self.s["profileStartingFrames"][j]')
v=v.replace('4*(1-p)+3*max(0,1-abs(f-287)/3)+5*tween(f,308,312)','9*(1-p)+6*max(0,1-abs(f-287)/3)+5*tween(f,308,312)')
v=v.replace('        d.rounded_rectangle((317,49,583,117),40,fill="#191a20")','        d.rounded_rectangle((317,52,583,120),40,fill="#0c0d10")')
f.write_text(v)
