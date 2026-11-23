from pathlib import Path
import json
p=Path('sidehoe-skill-trial/project')
s=json.loads((p/'scene.json').read_text())
t=s['tracks']
t['redOrbit']=[[478,525,553,202],[483,525,573,226],[487,526,588,228],[496,521,606,228],[509,511,617,230],[530,487,623,230],[536,337,561,218],[545,319,499,174],[550,337,463,146],[558,431,405,102],[567,494,396,96],[574,544,400,96],[580,636,440,124],[586,665,475,150],[594,681,491,170],[602,687,509,182],[612,690,569,186],[616,691,638,184],[619,691,754,182],[620,691,827,182],[621,691,930,182]]
t['blueOrbit']=[[478,403,529,137],[483,374,526,170],[487,355,525,168],[496,341,523,164],[509,323,516,158],[530,317,502,150],[536,410,411,96],[545,499,399,86],[550,551,407,86],[558,649,463,114],[567,666,503,136],[574,663,539,158],[580,597,603,178],[586,541,622,186],[594,514,634,200],[602,503,649,206],[612,499,709,206],[616,499,781,206],[619,500,897,204],[621,499,1014,204]]
t['clusterPose']=[[213,-32,159,.76],[216,-31,53,.85],[218,-12,12,.88],[222,-10,0,.90],[226,-12,0,.92],[242,-32,-19,1.08],[249,-54,-25,1.11],[253,-82,-30,1.13],[254,-108,-29,1.14],[255,-121,-27,1.14],[256,-157,-30,1.14],[257,-188,-30,1.14],[258,-223,-26,1.14]]
for node in s['cluster']:
    node[4]-=3
s['clusterWipe']=[[254,0,329,66,76],[254,128,471,104,65],[254,468,335,103,56],[254,54,616,84,98],[255,9,213,80,27],[255,110,473,104,94],[255,234,655,92,59],[255,569,340,93,157],[256,52,310,140,75],[256,312,304,144,104],[256,205,505,272,95],[256,461,475,144,146],[256,646,500,130,92],[257,121,313,620,78],[257,0,520,490,86],[257,364,381,496,138],[257,231,605,552,143]]
t['sofiaCamera'][2:5]=[[318,-33,1.0],[319,12,1],[320,33,1.0],[325,88,1.0]]
t['sofiaCamera'][0]=[313,-335,1]
t['followCamera'][0:4]=[[624,-218,1],[626,-109,1],[630,1,1],[633,40,1]]
t['inboxY']=[[0,74],[6,38],[11,32],[37,-3],[42,-30],[46,-68],[50,-139],[54,-272],[59,-791],[62,-1014],[64,-1144],[66,-1262],[69,-1407],[75,-1409],[82,-1411],[95,-1410],[101,-1235]]
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py'
v=f.read_text().replace('def apply_fringe(image, x_offset, y_offset):','''def vertical_blur(image, length):
    if length < 2:
        return image
    mixed = image
    count = min(13, max(3, round(length/5)))
    for i, offset in enumerate(np.linspace(-length/2, length/2, count), 2):
        shifted = image.transform(image.size, Image.Transform.AFFINE, (1, 0, 0, 0, 1, offset),
                                  Image.Resampling.BILINEAR)
        mixed = Image.blend(mixed, shifted, 1/i)
    return mixed


def apply_fringe(image, x_offset, y_offset):''')
v=v.replace('def status(d,w,y,label,island=False):','''@lru_cache(maxsize=4)
def rim_only(w,h,radius):
    outer = shell_material(w,h,radius).copy()
    alpha = outer.getchannel("A")
    bevel = max(9, round(w*.027))
    ImageDraw.Draw(alpha).rounded_rectangle((bevel,bevel,w-bevel-1,h-bevel-1),radius-bevel,fill=0)
    outer.putalpha(alpha)
    return outer


def status(d,w,y,label,island=False):''')
v=v.replace('amount=8*(1-up(f,0,6))+11*max(0,1-abs(f-57)/9)+2*up(f,98,101)\n        composite(im,blur(i,amount),500-410*scale,y,1,scale)','''amount=3*(1-up(f,0,6))+1.3*up(f,98,101)
        scroll_streak = 52*max(0,1-abs(f-57)/7)
        composite(im,vertical_blur(blur(i,amount),scroll_streak),500-410*scale,y,1,scale)''')
a=v.index('        grow = .86+.28');b=v.index('    def profiles',a)
v=v[:a]+'''        x,y,grow = self.track("clusterPose", f)
        if f >= self.at("profiles.mosaic"):
            stage = layer()
            composite(stage,content,500-500*grow+x,492-500*grow+y,1,grow)
            panel_wipe(stage,self.s["clusterWipe"],f)
            trail = f-254
            composite(im,blur(stage, .6+trail*2.4),0,0,max(0,1-.20*trail))
        else:
            composite(im,blur(content,11*(1-tween(f,213,222))),500-500*grow+x,492-500*grow+y,1,grow)

'''+v[b:]
v=v.replace('            self.avatar(tile,key,150,124,204,neutral=(f<self.at("profiles.lisa-focus") or f>=307))\n            text(d,150,257,name,40,INK,630,"center")\n            d.rounded_rectangle((40,309,260,357),24,fill=fill)\n            text(d,150,319,tag,22,ink,590,"center")','''            self.avatar(tile,key,150,124,204,neutral=(f<self.at("profiles.lisa-focus") or f>=307))
            labels = layer(300,370)
            label_draw = ImageDraw.Draw(labels)
            text(label_draw,150,257,name,40,INK,630,"center")
            label_draw.rounded_rectangle((40,309,260,357),24,fill=fill)
            text(label_draw,150,319,tag,22,ink,590,"center")
            composite(tile,labels,0,0,tween(f,onset+3,onset+8))''')
v=v.replace('            blur(plate,','            blur(plate,')
v=v.replace('        im.putalpha(mask)\n        return im\n\n    def suggestion_group','''        im.putalpha(mask)
        im.alpha_composite(rim_only(400,827,65))
        return im

    def suggestion_group''')
v=v.replace('            composite(im,blur(plate,entrance+push),x,y,a,s)','''            trail = 93*(1-tween(f,313,319))
            composite(im,vertical_blur(blur(plate,entrance+push),trail),x,y,a,s)''')
v=v.replace('            nodes.append((depth,name,x,y,s))','''            if name in ("red","blue"):
                x,y,s = self.track(f"{name}Orbit", f)
            nodes.append((depth,name,x,y,s))''')
v=v.replace('            ox=blur(app_icon(name),4.5*(1-(depth+1)/2)+8*tween(f,615,622))','''            ox=blur(app_icon(name),4.5*(1-(depth+1)/2))
            ox=vertical_blur(ox,85*tween(f,616,622))''')
v=v.replace('        composite(im,blur(plate,6*(1-tween(f,624,633))+2.5*max(0,1-abs(f-665)/7)+3*tween(f,690,696)),x,y,1,s)','''        exposed = blur(plate,6*(1-tween(f,624,633))+2.5*max(0,1-abs(f-665)/7)+3*tween(f,690,696))
        composite(im,vertical_blur(exposed,102*(1-tween(f,624,630))),x,y,1,s)''')
v=v.replace('        elif f<258:\n            self.cluster(im,f)\n        elif f<313:\n            self.profiles(im,f)','''        elif f<313:
            if f < 259:
                self.cluster(im,f)
            if f >= 258:
                self.profiles(im,f)''')
f.write_text(v)
f=p/'artwork.py'
v=f.read_text()
v=v.replace('d.rounded_rectangle((45,46,211,82),11,fill="#a9dbff")\n        d.line((77,38,77,68),fill="#fff",width=8)\n        d.line((177,38,177,68),fill="#fff",width=8)\n        text(d,128,94,"31",103,"#fff",620,"center")','''d.rounded_rectangle((33,32,223,68),11,fill="#6cb4ff")
        text(d,128,72,"31",144,"#fff",595,"center")''')
v=v.replace('        heart(d,126,164,58,"#ffd9e6")','')
f.write_text(v)
