"""Measured late menu camera correction; does not put food under phone camera."""
from pathlib import Path
import copy,json,hashlib
from PIL import Image
p=Path(__file__).parent
s=json.loads((p/'final-v9.scene.json').read_text())
g=next(x for x in s['layers'] if x['id']=='p03-204')
menu_rows=json.loads((p/'menu-exit-native/boxes.json').read_text())
tail_rows=json.loads((p/'celebration-tail-native/boxes.json').read_text())
# Native template dark bezel: x=15..785; y=12..1645. At the cropped
# frames height is not observable; preserve aspect and anchor measured bottom.
rows=menu_rows+tail_rows[1:]
poses=[]
for row in rows:
 t=row['t'];b=row['box']
 if t==24.6: continue # Ramen occludes one side of the connected component.
 left,top,right,bottom=b;sx=(right-left)/770
 sy=(bottom-top)/1633 if t>=24.7 else sx
 x=left-15*sx;y=bottom-1645*sy
 poses.append({'t':t,'x':x,'y':y,'scaleX':sx,'scaleY':sy,'source_box':b,'height_fit':'top+bottom' if t>=24.7 else 'cropped: aspect + bottom'})
for key in ['x','y','scaleX','scaleY']:
 old=g['keyframes'][key]
 # 22.5 keeps its previous pose; new23.4 key continuously corrects the camera.
 g['keyframes'][key]=[x for x in old if x['t']<23.4]+[{'t':x['t'],'value':x[key],'ease':'linear'} for x in poses]+[{'t':26.7,'value':old[-1]['value'],'ease':'linear'}]
menu=next(x for x in g['children'] if x['id']=='p03-203')
menu['end']=24.5;menu['originX']=400;menu['originY']=815
# Old list scroll compensated the wrong phone camera; remove that compensation.
menu_list=next(x for x in menu['children'] if x['id']=='p03-202')
menu_list['keyframes']['y']=[{'t':20.6,'value':0},{'t':22.7,'value':0},{'t':23.4,'value':0,'ease':'linear'},{'t':24,'value':14,'ease':'linear'}]
# Genuine separately declared food-photo crops; source never exposes the lower
# tomato-photo pixels, so those unobserved pixels remain transparent.
source=Image.open(p/'menu-exit-native/07.png').convert('RGBA')
source.crop((1085,707,1236,859)).save(p/'assets/food-falafel-original.png')
tomato=Image.new('RGBA',(153,153));tomato.paste(source.crop((1083,892,1236,974)),(0,0));tomato.save(p/'assets/food-tomato-original-top.png')
for row in menu_list['children']:
 if row['id']=='p03-191':row['src']='assets/food-falafel-original.png'
 if row['id']=='p03-198':row['src']='assets/food-tomato-original-top.png'
 if row['id']=='p03-190':row['text']='Falafel, cucumber, hummus,\npita'

menu['clip']={'x':29,'y':25,'width':742,'height':1608,'radius':120}
for key in ['scaleX','scaleY']:
 menu['keyframes'][key]=[{'t':20.6,'value':1},{'t':24.3,'value':1},{'t':24.4,'value':.48,'ease':'linear'},{'t':24.5,'value':.01,'ease':'linear'}]
menu['keyframes']['opacity']=[{'t':20.6,'value':1},{'t':24.3,'value':1},{'t':24.4,'value':.88,'ease':'linear'},{'t':24.5,'value':0,'ease':'linear'}]
# Correct the late avatar exits independently of the phone camera.
for avatar_id in ['p03-205','p03-207']:
 avatar=next(x for x in s['layers'] if x['id']==avatar_id);avatar['end']=23.35
 avatar['keyframes']['opacity']=[{'t':22.9,'value':1},{'t':23.35,'value':0,'ease':'linear'}]
bob=next(x for x in s['layers'] if x['id']=='p03-206');bob['end']=23.5
bob['keyframes']['x']=[k for k in bob['keyframes']['x'] if k['t']<=22.5]+[{'t':23.2,'value':1178,'ease':'linear'},{'t':23.4,'value':1180,'ease':'linear'}]
bob['keyframes']['y']=[k for k in bob['keyframes']['y'] if k['t']<=22.5]+[{'t':23.2,'value':270,'ease':'linear'},{'t':23.4,'value':245,'ease':'linear'}]
bob['keyframes']['blur']=[{'t':23.2,'value':0},{'t':23.4,'value':10,'ease':'linear'}]
bob['keyframes']['opacity']=[{'t':23.2,'value':1},{'t':23.4,'value':.6,'ease':'linear'},{'t':23.5,'value':0,'ease':'linear'}]
# Header/composer was intentionally obscured by menu until dismissal.
next(x for x in g['children'] if x['id']=='celebration-phone-ui-scrim')['start']=24.333333333333332
# Cart is a native vector icon and independently editable count bubble.
old=next(x for x in s['layers'] if x['id']=='p03-211');old['end']=23.4
cart={'id':'late-menu-cart-v10','type':'group','x':1297,'y':354,'start':23.4,'end':24.333333333333332,'children':[
 {'id':'cart-bubble-bg-v10','type':'rect','x':0,'y':0,'width':122,'height':73,'radius':36.5,'fill':'#ececec'},
 {'id':'cart-glyph-v10','type':'path','x':17,'y':18,'d':'M2 4 H10 L17 30 H38 L43 10 H13 M17 30 L18 34 H36','fill':'none','stroke':'#000000','strokeWidth':4.5},
 {'id':'cart-wheel-a-v10','type':'circle','x':29,'y':49,'width':7,'height':7,'fill':'#000000'},
 {'id':'cart-wheel-b-v10','type':'circle','x':46,'y':49,'width':7,'height':7,'fill':'#000000'},
 {'id':'cart-count-v10','type':'text','text':'3','x':73,'y':12,'fontSize':43,'fontFamily':'Recreation Text UI','fontWeight':400,'fill':'#000000'}]}
# Source count2 at23.4; count3 by23.5. The state change is explicitly bracketed.
cart['keyframes']={'x':[{'t':23.4,'value':1306},{'t':24,'value':1297,'ease':'linear'}],'y':[{'t':23.4,'value':410},{'t':24,'value':354,'ease':'linear'}]}
cart2=copy.deepcopy(cart);cart2['id']='late-menu-cart-two-v10';cart2['end']=23.466666666666665
for child in cart2['children']:child['id']+='-two'
cart2['children'][-1]['text']='2';cart['start']=23.466666666666665
s['layers'].extend([cart2,cart])
# Food and Order layers previously began before the menu actually dismissed.
# Retiming does not change their measured24.5 stage anchors.
for layer in s['layers']:
 if layer['id'].startswith('authentic-food-'):
  layer['start']=24.333333333333332
  for key,center in [('x',960-layer['width']/2),('y',400-layer['height']/2),('rotation',0)]:
   layer['keyframes'][key]=[{'t':24.333333333333332,'value':center}]+[k for k in layer['keyframes'][key] if k['t']>=24.5]
  for key in ['scaleX','scaleY']:layer['keyframes'][key]=[{'t':24.333333333333332,'value':.03},{'t':24.5,'value':1,'ease':'easeOut'}]
 if layer['id'] in ['p03-220','p03-224','p03-228']:
  layer['start']=24.333333333333332
  layer['keyframes']['opacity']=[{'t':24.333333333333332,'value':0},{'t':24.5,'value':1,'ease':'easeOut'}]
  layer['keyframes']['y']=[{'t':24.333333333333332,'value':layer['y']+20},{'t':24.5,'value':layer['y'],'ease':'easeOut'}]
s['source']['notes']+=' V10: exact native 23.4–26.6 bezel anchors correct late menu/camera; width and height fit independently when fully visible, aspect+bottom used when cropped. Menu remains through24.3, then native collapse/dissolve. Floating food stays outside phone camera; measured24.5 stage positions preserved.'
f=p/'final-v10.scene.json';f.write_text(json.dumps(s,indent=2));sha=hashlib.sha256(f.read_bytes()).hexdigest()
(p/'final-v10-changes.json').write_text(json.dumps({'sha256':sha,'baseline':'final-v9.scene.json','delta_frames_inclusive':[[618,800]],'pose_measurements':poses,'photo_assets':[{'file':'assets/food-falafel-original.png','source_time':24,'box':[1085,707,1236,859]},{'file':'assets/food-tomato-original-top.png','source_time':24,'box':[1083,892,1236,974],'partial':True}],'cropped_height_method':'Match dark bezel width and bottom; keep template aspect when top is not observable. Full visible samples >=24.7 use independent measured height. Rejected occluded24.6 bbox.','limitations':'Menu collapse/easing fitted from0.1-second anchors. Floating food24.5 positions retained; tail paths remain fitted.','proof':'No whole source frame/video layer; only native camera/menu/cart timing changed; separate floating assets retimed.'},indent=2))
print(sha)
