from pathlib import Path
import json
p=Path('sidehoe-skill-trial/repair/project')
s=json.loads((p/'scene.json').read_text())
t=s['tracks']
# Early nodes are measured independently through the series of sharp and streaked frames.
t['clusterEntrance'] = [
 [[212,348,850,17,.51],[213,344,725,111,.79],[214,350,607,170,.90],[215,346,553,207,1],[216,347,519,237,1],[218,347,468,229,1],[220,352,433,200,1],[223,347,396,178,1],[226,351,393,181,1]],
 [[212,533,844,45,.73],[213,520,717,97,.9],[214,524,604,108,1],[215,522,553,114,1],[216,524,519,115,1],[218,522,469,106,1],[220,526,434,91,1],[223,526,399,90,1],[226,526,398,83,1]],
 [[212,616,794,56,.87],[213,615,667,77,1],[214,614,552,83,1],[215,611,501,83,1],[216,611,462,83,1],[218,615,409,71,1],[220,615,374,66,1],[223,617,335,67,1],[226,615,336,67,1]],
 [[213,682,780,18,.65],[214,683,672,86,.91],[215,683,617,122,1],[216,684,574,150,1],[218,683,530,158,1],[220,685,493,154,1],[223,685,461,131,1],[226,688,456,132,1]],
 [[214,217,684,18,.49],[215,215,627,42,.91],[216,211,592,60,1],[218,214,543,77,1],[220,213,505,80,1],[223,215,474,70,1],[226,212,468,69,1]],
 [[216,449,666,34,.76],[218,446,613,125,1],[220,453,579,171,1],[223,455,548,159,1],[226,454,542,156,1]],
 [[217,301,657,24,.56],[218,304,632,66,.92],[220,304,596,126,1],[223,304,567,127,1],[226,305,563,125,1]],
 [[215,566,649,14,.59],[216,566,613,45,.89],[218,567,568,82,1],[220,566,529,85,1],[223,572,501,75,1],[226,573,495,72,1]],
 [[218,646,740,120,1],[220,650,697,212,1],[223,649,664,230,1],[226,651,661,226,1]],
 [[216,774,685,20,.62],[218,782,635,65,1],[220,783,600,87,1],[223,783,569,79,1],[226,783,567,76,1]],
 [[219,304,778,27,.66],[220,303,757,103,1],[223,302,730,200,1],[226,303,721,200,1]],
 [[218,472,775,32,.88],[220,475,740,103,1],[223,474,708,131,1],[226,476,702,133,1]],
 [[220,558,831,44,.92],[223,562,798,89,1],[226,561,794,89,1]]
]
t['clusterEarlySmear']=[[212,37],[213,51],[214,36],[215,19],[216,11],[217,5],[218,0]]
t['clusterEarlyBlur']=[[212,7],[213,9],[214,7],[215,5],[216,4],[218,2],[220,0]]
# Pink face is revealed from the left and does not share Lisa's opacity.
t['ellaRevealVeil']=[[282,0],[286,0],[288,.42],[290,.66],[295,.84],[300,.88],[305,.99],[312,.99]]
t['lisaExpression']=[[282,0],[286,0],[289,.67],[291,1],[306,1],[308,.58],[312,0]]
t['inboxIntroHeader']=[[0,.67,10,-14],[1,.85,6,-12],[2,1,4,-4],[4,1,2,0],[9,1,0,0]]
t['inboxScrollSmear']=[[42,0],[52,6],[54,25],[55,49],[56,60],[57,68],[59,55],[61,27],[63,13],[66,0],[101,0]]
t['badgeClosingHighlights']=[[696,51],[697,42],[698,27],[699,15],[701,0],[765,0]]
t['identityMeasuredBox']=[[102,500,482,314,178],[103,500,486,296,232],[104,500,491,289,265]]+t['identityMeasuredBox']
t['closingMeasuredBox']=[[696,499,527,207,144]]+[v for v in t['closingMeasuredBox'] if v[0]!=697]
for key in ('personalLine1','personalLine2','closingLine1','closingLine2'):
    t[key]=[v for v in t[key] if 28 <= v[4] <= (60 if key.endswith('1') else 86)]
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py';v=f.read_text()
v=v.replace('from PIL import Image, ImageChops, ImageDraw, ImageFilter','from PIL import Image, ImageChops, ImageDraw, ImageFilter')
i=v.index('def cursor(')
v=v[:i]+'''def fitted_badge(im, box, corner, radius=0, opacity=1, shine=0):
    x,y,w,h=box
    mark=badge(corner)
    if shine:
        highlight=Image.new("RGBA",mark.size,(175,165,252,round(shine)))
        mixed=Image.alpha_composite(mark,highlight)
        mixed.putalpha(mark.getchannel("A"))
        mark=mixed
    mark=mark.resize((max(1,round(w)),max(1,round(h))),Image.Resampling.LANCZOS)
    composite(im,blur(mark,radius),x-w/2,y-h/2,opacity)


def fit_ink(im, caption, bbox, weight, opacity=1, blur_radius=0):
    x,y,w,h=bbox
    if opacity<=0 or w<=0 or h<=0:
        return
    plane=layer(1050,140)
    text(ImageDraw.Draw(plane),10,12,caption,80,(20,20,20,255),weight)
    box=plane.getbbox()
    if box is None:
        return
    ink=plane.crop(box).resize((max(1,round(w)),max(1,round(h))),Image.Resampling.BICUBIC)
    patch=layer(ink.width+16,ink.height+16)
    patch.alpha_composite(ink,(8,8))
    composite(im,blur(patch,blur_radius),x-8,y-8,opacity)


'''+v[i:]
v=v.replace('''        d=ImageDraw.Draw(i)
        status(d,815,214,self.c["status"])''','''        chrome=layer(820,630)
        d=ImageDraw.Draw(chrome)
        status(d,815,214,self.c["status"])''',1)
v=v.replace('''        for j,((label,key),x) in enumerate(zip(self.s["inboxPins"],[169,411,651])):''','''        if f<10:
            alpha,softness,rise=self.track("inboxIntroHeader",f)
            composite(i,vertical_blur(blur(chrome,softness),softness*1.8),0,rise,alpha)
        else:
            composite(i,chrome,0,0)
        d=ImageDraw.Draw(i)
        for j,((label,key),x) in enumerate(zip(self.s["inboxPins"],[169,411,651])):''',1)
v=v.replace('self.avatar(i,key,x,482+68*(1-p),158*(.78+.22*p),.25+.75*p if j==1 else p)','''self.avatar(i,key,x,482+68*(1-p),158*(.78+.22*p),
                        (.58+.42*p if f<10 else .25+.75*p) if j==1 else p)''',1)
v=v.replace('''        scroll_streak = 52*max(0,1-abs(f-57)/7)
        composite(im,vertical_blur(blur(i,amount),scroll_streak),500-410*scale,y,1,scale)''','''        scroll_streak=0
        if f>=42:
            measured,=self.track("inboxMeasuredScroll",f)
            y=mix(y,measured,tween(f,42,47)*.86)
            scroll_streak,=self.track("inboxScrollSmear",f)
        composite(im,vertical_blur(blur(i,amount),scroll_streak),500-410*scale,y,1,scale)''')
a=v.index('        y,=self.track("identityY",f)')
b=v.index('    def assistant',a)
v=v[:a]+'''        cx,cy,w,h=self.track("identityMeasuredBox",f)
        a=tween(f,102,105)
        amount=6*tween(f,129,133)
        corner=round(mix(87,128,up(f,105,113))/4)*4
        fitted_badge(im,(cx,cy,w,h),corner,amount,a)
        text_plate=layer()
        gentle_characters(text_plate,self.c["brand"],cx,cy+h*.64,77,650,f,
                          self.at("identity.name")-1,.68,True)
        exposure=max(amount,5*(1-tween(f,106,110)))
        composite(im,vertical_blur(blur(text_plate,exposure),exposure),0,0)

'''+v[b:]
v=v.replace('''        gentle_characters(title,self.c["personal"][0],500,y,65,660,f,start-2,.17)
        onset=self.at("personal.line-two")
        gentle_characters(title,self.c["personal"][1],500,y+57,94,765,f,onset,.38,True)''','''        if f<168:
            gentle_characters(title,self.c["personal"][0],500,y,65,660,f,start-1,.30)
        else:
            fit_ink(title,self.c["personal"][0],self.track("personalLine1",f),660,
                    mix(.72,1,tween(f,168,174)))
        onset=self.at("personal.line-two")
        if f>=188:
            fit_ink(title,self.c["personal"][1],self.track("personalLine2",f),765)
        elif f>=onset:
            line=self.c["personal"][1]
            face=font(89,765)
            left=500-face.getlength(line)/2
            hints=(179,178,178,182,183,177,181,183,180,182,181,177)
            for j,char in enumerate(line):
                ink=(72,35,76,round(255*tween(f,hints[j],188)))
                text(ImageDraw.Draw(title),left+face.getlength(line[:j]),y+56,char,89,ink,765)''')
v=v.replace('''        composite(im,vertical_blur(title,30*tween(f,205,212)),0,0)

    def cluster''','''        composite(im,vertical_blur(title,23*tween(f,205,212)),0,0)
        if f==212:
            self.cluster_entrance(im,f)

    def cluster_entrance(self,im,f):
        layer_image=layer()
        d=ImageDraw.Draw(layer_image)
        samples=[]
        for entry, keys in zip(self.s["cluster"],self.s["tracks"]["clusterEntrance"]):
            if f<keys[0][0]:
                continue
            actor,_,_,_,_,color=entry
            x,y,size,opacity=interpolate(keys,f)
            samples.append((actor,x,y,size,opacity,color))
        if f>=214:
            for _,x,y,size,opacity,_ in samples:
                oval(d,x,y,size*.61,size*.61,(236,232,251,round(opacity*232)))
        for actor,x,y,size,opacity,color in samples:
            if actor:
                self.avatar(layer_image,actor,x,y,size,opacity,color)
            else:
                from PIL import ImageColor
                oval(d,x,y,size/2,size/2,(*ImageColor.getrgb(color),round(opacity*255)))
        softness,=self.track("clusterEarlyBlur",f)
        smear,=self.track("clusterEarlySmear",f)
        composite(im,vertical_blur(blur(layer_image,softness),smear),0,0)

    def cluster''')
v=v.replace('''        content=layer()
        d=ImageDraw.Draw(content)''','''        if f<=226:
            self.cluster_entrance(im,f)
            return
        content=layer()
        d=ImageDraw.Draw(content)''',1)
v=v.replace('''            trail = f-254
            composite(im,blur(stage, .6+trail*2.4),0,0,max(0,1-.20*trail))''','''            trail = f-254
            if trail>=2:
                stage=stage.transpose(Image.Transpose.ROTATE_90)
                stage=vertical_blur(stage,(trail-1)*22).transpose(Image.Transpose.ROTATE_270)
            composite(im,blur(stage,.6+trail*.75),0,0,max(0,1-.17*trail))''')
v=v.replace('''            self.avatar(tile,key,150,124,204,neutral=(f<self.at("profiles.lisa-focus") or f>=307))''','''            if j==0:
                expression,=self.track("lisaExpression",f)
                self.avatar(tile,key,150,124,204,neutral=True)
                self.avatar(tile,key,150,124,204,expression,neutral=False)
            else:
                self.avatar(tile,key,150,124,204,neutral=True)''')
v=v.replace('''            x=265+j*275
            x=500+(x-500)*zoom+xoff+126*(1-p)''','''            if j==1 and f>=287:
                veil,=self.track("ellaRevealVeil",f)
                field=np.clip(np.linspace(.45,1.8,300)*veil,0,.98)
                mask=Image.fromarray(np.tile(np.uint8((1-field)*255),(370,1)))
                tile.putalpha(ImageChops.multiply(tile.getchannel("A"),mask))
                opacity=max(opacity,.91)
            x=265+j*275
            x=500+(x-500)*zoom+xoff+126*(1-p)''')
v=v.replace('''        y,=self.track("closingY",f)
        s,=self.track("closingSize",f)
        stamp(im,blur(badge(52),6*(1-tween(f,696,704))),500,y,s, .75+.25*tween(f,696,703))''','''        if f<766:
            shine,=self.track("badgeClosingHighlights",f)
            fitted_badge(im,self.track("closingMeasuredBox",f),52,5*(1-tween(f,696,704)),1,shine)
        else:
            y,=self.track("closingY",f)
            s,=self.track("closingSize",f)
            stamp(im,badge(52),500,y,s)''')
v=v.replace('''            face=font(size,weight)
            x=500-face.getlength(" ".join(row))/2''','''            if f<766:
                bounds=self.track(f"closingLine{j+1}",f)
                face=font(80,weight)
                width=face.getlength(" ".join(row))
                x,y,w,h=bounds
                for k,word in enumerate(row):
                    at=onset[j][k]
                    a=tween(f,at-1,at+5)
                    prefix=" ".join(row[:k])+(" " if k else "")
                    xi=x+w*face.getlength(prefix)/width
                    word_w=w*face.getlength(word)/width
                    fit_ink(im,word,(xi,y+12*(1-a),word_w,h),weight,a,4*(1-a))
                continue
            face=font(size,weight)
            x=500-face.getlength(" ".join(row))/2''')
f.write_text(v)
