from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,json,copy,hashlib
p=Path(__file__).parent
scene=json.loads((p/'final-v6.scene.json').read_text())
source=Image.open(p/'measured/24.5.png').convert('RGB')

def foreground(box,filename,ramen=False):
    image=source.crop(box).convert('RGBA');array=np.array(image)
    rgb=array[:,:,:3].astype('int16');spread=rgb.max(2)-rgb.min(2)
    background=(spread<12)&(rgb.min(2)>235)
    if ramen:background=spread<12
    seed=np.zeros(background.shape,dtype=bool);seed[0]=background[0];seed[-1]=background[-1];seed[:,0]|=background[:,0];seed[:,-1]|=background[:,-1]
    removed=ndimage.binary_propagation(seed,mask=background)
    alpha=np.where(removed,0,255).astype('uint8')
    if ramen:
        # Preserve the white bowl, which shares the backdrop color but is bounded
        # by its real gray/red outline; remove connected monochrome phone pixels.
        mask=Image.new('L',image.size);draw=ImageDraw.Draw(mask)
        points=[]
        def curve(a,b,c,d):
            for t in np.linspace(0,1,40):
                u=1-t;points.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0],u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1]))
        curve((4,76),(4,45),(148,45),(148,76))
        curve((148,76),(144,115),(120,138),(77,138))
        curve((77,138),(35,138),(10,116),(4,76))
        draw.polygon(points,fill=255)
        alpha=np.maximum(alpha,np.array(mask))
    array[:,:,3]=alpha;Image.fromarray(array).save(p/'assets'/filename)
    return {'file':'assets/'+filename,'source_time':24.5,'source_box':list(box),'matte':'Connected boundary background removal; internal white features preserved.'}
assets=[foreground((385,155,491,272),'apple-pizza.png'),foreground((1080,240,1232,385),'apple-ramen.png',True)]
# Replace native fallback emoji with actual separate source artwork and measured poses.
emoji=[layer for layer in scene['layers'] if layer['type']=='text' and layer.get('start')==23.4 and layer.get('end')==26.7 and layer.get('text') in ['🍕','🍜','🥗']]
for layer in emoji:
    scene['layers'].remove(layer)
foodposes=[('pizza-left','apple-pizza.png',385,155,106,117,-20,30),('pizza-top','apple-pizza.png',700,-50,106,117,-8,22),('pizza-header','apple-pizza.png',790,26,120,147,-10,32),('pizza-tiny-right','apple-pizza.png',1251,110,13,15,5,38),('pizza-card','apple-pizza.png',864,575,29,38,0,20),('ramen','apple-ramen.png',1080,240,152,145,0,0)]
for name,file,x,y,w,h,r0,r1 in foodposes:
    scene['layers'].append({'id':'authentic-food-'+name,'type':'image','src':'assets/'+file,'x':x,'y':y,'width':w,'height':h,'start':23.4,'end':26.7,'keyframes':{
        'x':[{'t':23.4,'value':x-80},{'t':24.5,'value':x,'ease':'easeOut'},{'t':26.7,'value':x+120,'ease':'easeIn'}],
        'y':[{'t':23.4,'value':y-500},{'t':24.5,'value':y,'ease':'easeOut'},{'t':26.7,'value':y+600,'ease':'easeIn'}],
        'rotation':[{'t':23.4,'value':r0},{'t':24.5,'value':0,'ease':'easeOut'},{'t':26.7,'value':r1,'ease':'easeIn'}]}})
# Fit the three different scale states of the tiny Order! bubbles at24.5s.
orders=[layer for layer in scene['layers'] if layer['type']=='group' and any(child.get('text')=='Order!' for child in layer.get('children',[]))]
for layer,(x,y,w,h,size,pad) in zip(orders,[(520,360,64,30,16,10),(570,575,95,44,23,15),(1080,793,126,64,30,20)]):
    oldy=layer['y'];layer['x']=x;layer['y']=y
    for key in layer.get('keyframes',{}).get('y',[]):key['value']+=y-oldy
    for child in layer['children']:
        if child['type']=='rect':child.update(width=w,height=h,radius=h/2)
        if child['type']=='path':child['d']=f'M12 {h-10} Q13 {h+2} 6 {h+6} Q24 {h+1} 29 {h-10} Z'
        if child['type']=='text':child.update(fontFamily='Recreation Text UI',fontSize=size,lineHeight=size*1.2,x=pad,y=h*.13)
# Source phone UI is RGB241 behind the floating artwork, versus its RGB253 stage.
lunch=next(layer for layer in scene['layers'] if layer['id']=='p03-204')
lunch['children'].append({'id':'celebration-phone-ui-scrim','type':'rect','x':29,'y':25,'width':742,'height':1608,'radius':120,'fill':'#000000','opacity':12/253,'start':23.45,'end':26.7})
scene['source']['notes']+=' V7 celebration patch: authentic isolated Applepizza/ramenart fromsource24.5s, distinct measuredOrderbubblebounds, and RGB241screen-onlyscrim. These are separate rasterassets/nativebubbles; nofullsourceframe. Food trajectories between measuredanchors remainfitted.'
file=p/'final-v7.scene.json';file.write_text(json.dumps(scene,indent=2));checksum=hashlib.sha256(file.read_bytes()).hexdigest()
(p/'final-v7-assets.json').write_text(json.dumps({'sha256':checksum,'assets':assets,'measured_order_bubbles':[[520,360,64,30],[570,575,95,44],[1080,793,126,64]],'phone_blank_rgb':241,'delta_from_v6_inclusive_frames':[702,800],'all_patches_from_v3':[[414,800],[891,1259]],'all_patches_from_v4':[[414,457],[702,800],[891,1259]]},indent=2))
print(checksum)
