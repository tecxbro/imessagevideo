from pathlib import Path
from PIL import Image
import json
root=Path('/workspace/imessage-recreations');d=root/'references/05-linq';scene=json.loads((d/'scene.json').read_text());prov=json.loads((d/'assets/asset-provenance.json').read_text())
idx=0
def crop(t,box,name):
 image=Image.open(d/f'keyframes/{t}.png').convert('RGBA').crop(box);name=f'assets/{name}.png';image.save(d/name);prov.append({'path':name,'frame':t,'box':box,'kind':'static rich-app internal artwork; internal text bitmap; outer transform/layout editable'});return name

def image(src,x,y,w,h):
 global idx;idx+=1;return {'id':f'rich-asset-{idx}','type':'image','src':src,'x':x,'y':y,'width':w,'height':h}
def group(ch,a,b,x=0,y=0,keys=None):
 global idx;idx+=1;return {'id':f'rich-group-{idx}','type':'group','children':ch,'x':x,'y':y,'start':a,'end':b,**({'keyframes':keys} if keys else {})}
def track(*pairs):return [{'t':t,'value':v,'ease':'easeOut'} for t,v in pairs]
chess=crop('008.20',(152,0,810,720),'chess-app-board')
fare=crop('013.30',(188,0,770,720),'flight-fare-panel')
seat=crop('015.10',(188,0,770,720),'flight-seat-panel')
game=crop('029.00',(236,0,724,720),'chess-app-full')
four=crop('033.00',(152,0,638,720),'four-in-row-app')
food=crop('035.20',(192,0,776,720),'foodash-order-panel')
restaurant=crop('037.00',(190,0,774,720),'restaurant-app-panel')
# Each bounded internal panel is independently animated. Native surrounding scene remains separate.
replacements={
 6.97:group([image(chess,152,0,658,720)],6.97,8.57,keys={'scaleX':track((6.97,.85),(7.5,1)),'scaleY':track((6.97,.85),(7.5,1)),'originX':track((6.97,480)),'originY':track((6.97,360))}),
 12.07:group([image(fare,188,0,582,720)],12.07,13.9,keys={'y':track((12.07,100),(12.4,0)),'opacity':track((12.07,0),(12.25,1))}),
 13.9:group([image(seat,188,0,582,720)],13.9,15.63,keys={'opacity':track((13.9,0),(14.05,1))}),
 28.83:group([image(game,236,0,488,720)],28.83,31.37,keys={'y':track((28.83,90),(29.05,0))}),
 31.37:group([image(four,0,0,486,720)],31.37,33.17,x=152,keys={'x':track((31.37,236),(33,152))}),
 33.17:group([image(food,192,0,584,720)],33.17,35.63,keys={'y':track((33.17,60),(33.4,0))}),
 35.63:group([image(restaurant,190,0,584,720)],35.63,38.13,keys={'y':track((35.63,55),(35.9,0))})}
new=[]
for l in scene['layers']:
 a=l.get('start');
 if a in replacements:
  # At6.97 one native chessgroup; atother times one rich-app group.
  new.append(replacements.pop(a));continue
 if a==7.2:continue # native pawn-glow overlay mismatched bitmap state; no false geometry
 if a==40.63:continue # replace generic phonegallery with individual measured assets below
 new.append(l)
# Native confetti and native YOU WON title remain independent of the static chess-app panel.
phone_boarding=crop('041.50',(345,100,617,656),'gallery-phone-boarding')
phone_music=crop('041.50',(662,51,931,606),'gallery-phone-music')
phone_chat=crop('041.50',(30,332,301,720),'gallery-phone-chat-part')
phone_order=crop('041.50',(30,0,301,276),'gallery-phone-order-part')
# gallery elements at the reference41.5sec camera settle; coordinated drift approximates measured grid motion.
gallery=group([image(phone_boarding,345,100,272,556),image(phone_music,662,51,269,555),image(phone_chat,30,332,271,388),image(phone_order,30,0,271,276)],40.63,42.27,keys={'y':track((40.63,90),(41.5,0),(42.27,-100))})
# Insert before titlecards, preserving zorder.
new.append(gallery);scene['layers']=new
scene['source']['notes']+=' Finalv4 uses declared static rich-app panels and individual phone-gallery artwork for internal app detail; those internal pixels/text are not editable. Outer scene, bubbles, title typesetting, geometry and motion are native. Full temporal motion remains approximate.'
(d/'scene.json').write_text(json.dumps(scene,indent=2));(d/'assets/asset-provenance.json').write_text(json.dumps(prov,indent=2))
# Rene v4 = v3 geometry/optimizedfonts; nofullframe/screensubstitution.
r=root/'references/06-gallery';ss=json.loads((r/'scene.json').read_text());ss['source']['notes']+=' Finalv4 uses measured header/status-camera corrections and optimized used-glyph font subsets; physical bezel crop only, screen remains native.';(r/'scene.json').write_text(json.dumps(ss,indent=2))
print('Finalv4 Linq richapp panel crops',len(prov))
