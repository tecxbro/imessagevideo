from pathlib import Path
import json
p=Path('sidehoe-skill-trial/project')
s=json.loads((p/'scene.json').read_text())
t=s['tracks']
t['sendReplyBox']=[[360,512,314,882,402],[371,504,300,894,394],[382,504,292,910,388],[386,504,286,918,384],[389,504,276,922,376],[391,504,270,926,370],[393,504,258,926,358],[394,504,252,926,352],[396,508,234,926,332],[402,514,64,944,171]]
t['sendSuggestionBox']=[[360,376,450,886,590],[371,360,442,898,590],[382,352,440,914,592],[386,348,436,922,592],[389,348,430,926,588],[391,348,422,930,580],[393,348,412,930,572],[394,348,406,930,566],[396,348,390,930,548],[402,350,237,946,386]]
t['sendCursor']=[[381,775,982,1],[382,784,918,1],[384,816,837,2],[386,832,774,0],[389,840,707,0],[391,840,675,0],[393,843,649,0],[394,845,637,0],[396,852,619,0],[402,860,454,0]]
t['calendarCursor']=[[402,998,478,-91],[405,891,453,-86],[408,820,441,-90],[411,745,438,-95],[415,575,547,-49],[420,514,536,-4],[427,510,534,-4],[431,514,518,-4],[435,520,458,-4],[437,520,450,-4],[442,494,474,-4],[452,476,510,-4],[457,460,620,-59],[460,463,633,-60],[470,406,636,-62],[478,90,680,-34]]
s['palette']['cyan']='#02bae7'
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py'
v=f.read_text()
v=v.replace('                     Image.Resampling.BICUBIC)','                     Image.Resampling.BICUBIC)')
v=v.replace('        status(d,900,92,self.c["status"],True)\n','')
v=v.replace('d.rounded_rectangle((83,90,125,114),7,fill=BASE)\n        ','')
v=v.replace('        d.rounded_rectangle((759,83,886,112),10,fill=BASE)\n        text(d,749,89,"▴  ◔  ▰",29,INK,600)','''        for i, height in enumerate((6, 10, 14, 19)):
            d.rounded_rectangle((755+8*i,107-height,760+8*i,107),2,fill=INK)
        d.arc((789,88,822,111),206,332,fill=INK,width=4)
        oval(d,806,105,2,2,INK)
        d.rounded_rectangle((826,91,857,105),4,fill=INK)''')
v=v.replace('        for j,line in enumerate(self.c["assistant"]):\n            gentle_characters(im,line,500,title_y+j*64,60,640,f,135+j*3,.31)','''        if f < 161:
            title = layer()
            for j,line in enumerate(self.c["assistant"]):
                gentle_characters(title,line,500,title_y+j*64,60,640,f,134+j*2,.27)
            if f < 157:
                im.paste(title.convert("RGB"), mask=title.point(lambda x: x).getchannel("A")) if False else None
            # The title is rendered after optical treatment and leaves independently.
            if f >= 157:
                title = Image.blend(Image.new("RGBA",title.size,BASE),title,1-tween(f,157,161))
                composite(im,title,0,0,0)
            for j, line in enumerate(self.c["assistant"]):
                if f < 157:
                    gentle_characters(im,line,500,title_y+j*64,60,640,f,134+j*2,.27)
                else:
                    strip = layer()
                    gentle_characters(strip,line,500,title_y+j*64,60,640,f,134+j*2,.27)
                    composite(im,strip,0,0,1-tween(f,157,161))''')
a=v.index('        if f < 161:'); b=v.index('    def personal(',a)
v=v[:a]+'''        title = layer()
        for j, line in enumerate(self.c["assistant"]):
            gentle_characters(title,line,500,title_y+j*64,60,640,f,134+j*2,.27)
        composite(im,title,0,0,1-tween(f,157,161))

'''+v[b:]
v=v.replace('gentle_characters(im,self.c["personal"][0],500,y,65,660,f,start,.17)','gentle_characters(im,self.c["personal"][0],500,y,65,660,f,start-2,.17)')
v=v.replace('(1-tween(f,201+i*.5,212))','(1-tween(f,194+i*.5,208))')
v=v.replace('            composite(im,blur(stage,1+1.8*(f-254)),0,0,1-.13*(f-254))','''            trail = f-254
            if trail:
                stage = blur(stage, 1+trail*1.3)
            composite(im,stage,0,0,1-.26*trail)''')
v=v.replace('            onset=self.at("profiles.directory")+j*2\n            p=tween(f,onset,onset+8)','            onset=self.at("profiles.directory")+j*2-1\n            p=tween(f,onset,onset+4)')
v=v.replace('            x=500+(x-500)*zoom+xoff+85*(1-p)','            x=500+(x-500)*zoom+xoff+126*(1-p)')
v=v.replace('            y=414+yoff-75*(1-p)','            y=414+yoff-90*(1-p)')
v=v.replace('    def bubble(self,im,x,y,w,h,lines,out=False,pale=False):','    def bubble(self,im,x,y,w,h,lines,out=False,pale=False,text_size=14.3):').replace('r=min(h*.43,18)','r=min(h*.43, text_size*1.24)').replace('size=min(14.3,','size=min(text_size,')
a=v.index('        if f<353:',v.index('    def sofia'));b=v.index('        if f>=381:',a)
v=v[:a]+'''        if f < 353:
            composite(im,blur(g,2.0*max(0,1-abs(f-337)/6)),x,y,1,s)
        elif f < 360:
            dx,y,s=self.track("sendGroup",f)
            x=500-200*s+dx
            composite(im,blur(g,1.8*max(0,1-abs(f-355)/6)),x,y,1,s)
        else:
            detached = layer()
            c = self.c["sofia"]
            left, top, right, bottom = self.track("sendReplyBox", f)
            self.bubble(detached,left,top,right-left-8,bottom-top,c[4],True,text_size=54)
            left, top, right, bottom = self.track("sendSuggestionBox", f)
            text(ImageDraw.Draw(detached),left+12,top-28,c[5],27,MUTED,520)
            self.bubble(detached,left,top,right-left-8,bottom-top,c[6],True,text_size=46)
            self.chip(detached, right-318, bottom+5, 123, 64, c[7])
            self.chip(detached, right-177, bottom+5, 158, 64, c[8], True)
            composite(im,blur(detached,4*tween(f,396,403)),0,0,1-tween(f,399,403))
'''+v[b:]
v=v.replace('cursor(im,x,y,r,1-tween(f,397,403),1.23)','cursor(im,x,y,r,1-tween(f,397,403),1.53)')
v=v.replace('d.polygon([(11,9),(52,35),(34,38),(44,58),(34,63),(24,43),(13,55)]','d.polygon([(11,9),(51,43),(31,42),(43,65),(34,70),(22,48),(12,59)]')
v=v.replace('cursor(cal,x,y,r,tween(f,402,405),.88)','cursor(cal,x,y,r,tween(f,402,405),.98)')
f.write_text(v)
f=p/'artwork.py'
v=f.read_text().replace('from PIL import Image, ImageDraw, ImageFont','from PIL import Image, ImageDraw, ImageFont, ImageColor')
a=v.index('@lru_cache(maxsize=90)')
v=v[:a]+'''@lru_cache(maxsize=64)
def material(color, width, height, highlight):
    """Shade an independently authored ellipsoid and round its silhouette."""
    yy, xx = np.mgrid[-1:1:complex(height), -1:1:complex(width)]
    radius = np.sqrt(xx*xx + yy*yy)
    normal_z = np.sqrt(np.maximum(0, 1-radius*radius))
    key = np.clip(-.31*xx-.39*yy+.86*normal_z, 0, 1)
    gloss = np.maximum(0, normal_z-.36*xx-.44*yy)**7
    base = np.array(ImageColor.getrgb(color),float)
    rgb = base[None,None,:]*(.54+.60*key[:,:,None])+highlight*gloss[:,:,None]
    opacity = np.clip((1-radius)*min(width,height)/2+.5,0,1)*255
    return Image.fromarray(np.dstack((np.clip(rgb,0,255),opacity)).astype(np.uint8))


'''+v[a:]
v=v.replace('    d.ellipse((56,27,204,214 if style in {"long","braids"} else 188),fill=hair)','    composite(im, material(hair, 153, 193 if style in {"long","braids"} else 166, 35), 51, 24)')
v=v.replace('d.rounded_rectangle((53,168,207,271),36,fill=clothes)','composite(im, material(clothes, 174, 106, 10), 41, 164)')
v=v.replace('d.rounded_rectangle((81,51,176,174),radius=44,fill=skin)\n    d.arc((81,53,176,173),9,157,fill=blush,width=2)\n    oval(d,100,138,12,6,blush)\n    oval(d,156,138,12,6,blush)','''composite(im, material(skin, 115, 130, 22), 70, 49)
    for x in (89, 149):
        spot = material(blush, 20, 12, 0)
        composite(im,spot,x,131,.40)''')
v=v.replace('d.pieslice((75,31,185,110),180,360,fill=hair)','composite(im,material(hair,119,60,27),70,31)')
v=v.replace('oval(d,x,117,11,6,"#fff8ef")\n            oval(d,x+1,117,5,6,"#372d34")','oval(d,x,116,12,8,"#fff3e9")\n            composite(im,material("#554439",13,16,9),x-5,109)')
v=v.replace('d.line((126,120,123,133,130,135),fill=blush,width=3,joint="curve")','composite(im,material(skin,15,20,19),120,119)')
f.write_text(v)
