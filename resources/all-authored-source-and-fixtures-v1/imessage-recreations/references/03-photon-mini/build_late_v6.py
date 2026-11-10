from pathlib import Path
from PIL import Image
import copy,json,hashlib
p=Path(__file__).parent
scene=json.loads((p/'final-v5.scene.json').read_text())
# Correct unsafe white color-keying: original opaque avatar crops preserve eye glints
# and the white Apple logo. Editable circle extensions draw only outside their crop.
boxes={'bob':(0,0,1110,830),'laptop':(1166,0,1780,416),'robot':(1320,430,1920,1080),'alice':(400,820,1120,1080)}
source=Image.open(p/'measured/14.5.png').convert('RGB')
cluster=next(layer for layer in scene['layers'] if layer['id']=='measured-avatar-transition-v5')
for carrier in cluster['children']:
    name=carrier['id'].split('-')[-1]
    filename='avatar-'+name+'-opaque.png';source.crop(boxes[name]).save(p/'assets'/filename)
    circle=carrier['children'][0];art=carrier['children'][1];art['src']='assets/'+filename
    w,h=art['width'],art['height'];x,y=circle['x'],circle['y'];cw,ch=circle['width'],circle['height']
    clips=[]
    if y<0:clips.append(('top',{'x':x,'y':y,'width':cw,'height':-y}))
    if y+ch>h:clips.append(('bottom',{'x':x,'y':h,'width':cw,'height':y+ch-h}))
    if x<0:clips.append(('left',{'x':x,'y':0,'width':-x,'height':h}))
    if x+cw>w:clips.append(('right',{'x':w,'y':0,'width':x+cw-w,'height':h}))
    extensions=[]
    for suffix,clip in clips:
        child=copy.deepcopy(circle);child['id']='avatar-extension-circle-'+name+'-'+suffix
        extensions.append({'id':'avatar-extension-clip-'+name+'-'+suffix,'type':'group','clip':clip,'children':[child]})
    carrier['children']=extensions+[art]

# Card camera: fitted native anchors at30s,30.5s,31s; stagger each card separately.
collage=next(layer for layer in scene['layers'] if layer['type']=='group' and layer.get('start')==29.7)
collage['end']=32.5

def keys(points,ease='linear'):
    return [{'t':time,'value':value,'ease':ease} for time,value in points]
collage['keyframes']={
    'scaleX':keys([(29.7,9),(30,5),(30.5,1.085),(31,1),(32.5,1)]),
    'scaleY':keys([(29.7,9),(30,5),(30.5,1.085),(31,1),(32.5,1)]),
    'x':keys([(29.7,1000),(30,704),(30.5,33.535),(31,0),(32.5,0)]),
    'y':keys([(29.7,-50),(30,-18),(30.5,-2.8),(31,0),(32.5,0)])}
anchors305=[(-101,-188),(420,-196),(933,-201),(1447,-196),(1980,-180),(-220,208),(297,195),(808,190),(1327,188),(1826,190),(-335,593),(179,588),(684,586),(1206,578),(1710,575),(-430,984),(70,973),(563,977),(1082,976),(1590,959)]
anchors320={2:(616,88,311,222),8:(1052,149,310,222),9:(1358,-17,305,228),13:(1180,378,307,220),14:(1486,215,296,220),16:(684,937,310,222),18:(1305,605,303,220),19:(1610,440,290,220)}
anchors322={9:(1124,-93,275,204),14:(1303,40,280,203),18:(1284,411,275,194),19:(1483,172,289,201)}
for index,card in enumerate(collage['children']):
    old=copy.deepcopy(card['keyframes'])
    bx=card['x'];by=card['y']
    ax,ay=anchors305[index]
    wx=960+(ax-33.535-960)/1.085;wy=540+(ay+2.8-540)/1.085
    initial_x=bx+4*(wx-bx);initial_y=by+4*(wy-by)
    if index==7:initial_x=789;initial_y=220
    if index==12:initial_x=455.2;initial_y=586.4
    scatter_x=next(key['value'] for key in old['x'] if key['t']==31.8)
    scatter_y=next(key['value'] for key in old['y'] if key['t']==31.8)
    sx0=old['scaleX'][0]['value'];sy0=old['scaleY'][0]['value']
    sx318=next(key['value'] for key in old['scaleX'] if key['t']==31.8)
    sy318=next(key['value'] for key in old['scaleY'] if key['t']==31.8)
    xt=[(29.7,initial_x),(30,initial_x),(30.5,wx),(31,bx),(31.35,bx),(31.8,scatter_x)]
    yt=[(29.7,initial_y),(30,initial_y),(30.5,wy),(31,by),(31.35,by),(31.8,scatter_y)]
    sxt=[(29.7,sx0),(31.35,sx0),(31.8,sx318)]
    syt=[(29.7,sy0),(31.35,sy0),(31.8,sy318)]
    if index in anchors320:
        x,y,w,h=anchors320[index];xt.append((32,x));yt.append((32,y));sxt.append((32,w/390));syt.append((32,h/280))
        if index in anchors322:
            x,y,w,h=anchors322[index];xt.append((32.2,x));yt.append((32.2,y));sxt.append((32.2,w/390));syt.append((32.2,h/280))
            xt.append((32.5,x-250));yt.append((32.5,y-900));sxt.append((32.5,w/390*.8));syt.append((32.5,h/280*.8))
            fade=[(31.8,1),(32.2,1),(32.5,0)]
        else:
            xt.append((32.2,x-150));yt.append((32.2,y-450));fade=[(31.8,1),(32,1),(32.16,0)]
    else:
        xt.append((32,scatter_x-150));yt.append((32,scatter_y-300));fade=[(31.8,1),(31.95,0)]
    if index not in [7,12]:fade=[(29.7,0),(30.05,0),(30.4,1)]+fade
    card['keyframes']={'x':keys(xt),'y':keys(yt),'scaleX':keys(sxt),'scaleY':keys(syt),'opacity':keys(fade)}

# Progressive prefix words; source33.0 has only the first three words.
prefix=next(layer for layer in scene['layers'] if layer['type']=='text' and layer.get('text')=='Now your agent can send')
children=[]
for number,(value,start,end) in enumerate([('Now',32.6,32.6666666667),('Now your',32.6666666667,32.7333333333),('Now your agent',32.7333333333,33.0666666667),('Now your agent can',33.0666666667,33.1666666667),('Now your agent can send',33.1666666667,36.5)]):
    child=copy.deepcopy(prefix);child.update(id='prefix-word-phase-'+str(number),text=value,x=0,y=0,start=start,end=end);child.pop('keyframes',None);children.append(child)
prefix_group={'id':'measured-prefix-reveal-v6','type':'group','children':children,'start':32.6,'end':36.5,'keyframes':{
    'x':keys([(32.6,190),(32.8,217),(33,264),(33.1,271),(33.2,272),(33.4,270),(34,270),(34.5,240)]),
    'y':keys([(32.6,490.5),(32.8,490.5),(33,494),(33.2,493)]),
    'scaleX':keys([(32.6,1.073),(32.8,1.073),(33,1)]),'scaleY':keys([(32.6,1.129),(32.8,1.129),(33,1)])}}
scene['layers']=[prefix_group if layer['id']==prefix['id'] else layer for layer in scene['layers']]
for layer in scene['layers']:
    if layer['type']=='group' and layer.get('start')==32.8 and layer.get('end')==36.5:
        layer['start']=1000/30
# Authentic first category icon, isolated from a settled source frame.
Image.open(p/'measured/33.5.png').convert('RGB').crop((1160,506,1260,586)).save(p/'assets/agentic-apps-icon.png')
first_category=next(layer for layer in scene['layers'] if layer['type']=='group' and any(child.get('text')=='agentic apps' for child in layer.get('children',[])))
first_category['children'][0]={'id':'source-agentic-apps-icon','type':'image','src':'assets/agentic-apps-icon.png','x':0,'y':0,'width':100,'height':80}

# CTA words and URL have separate observed reveal times.
cta=next(layer for layer in scene['layers'] if layer['type']=='group' and layer.get('start')==36.5 and layer.get('end')==39.6)
black=next(child for child in cta['children'] if child['type']=='text' and child.get('text')=='Available today at')
url=next(child for child in cta['children'] if child['type']=='text' and child.get('text')=='tryphoton.ai')
parts=[]
for number,(value,start,end) in enumerate([('Available',36.5,36.6666666667),('Available today',36.6666666667,36.9666666667),('Available today at',36.9666666667,39.6)]):
    child=copy.deepcopy(black);child.update(id='cta-word-phase-'+str(number),text=value,start=start,end=end);parts.append(child)
url.update(start=37.0333333333,end=39.6,keyframes={'opacity':keys([(37.0333333333,0),(37.2,1)],'easeOut'),'x':keys([(37.0333333333,650),(37.2,643),(37.5,633)],'easeOut')})
cta['children']=parts+[url]
cta['keyframes']['x']=keys([(36.5,460),(36.8,452),(37,442),(37.5,438)])
# Preserve brand identity with the supplied logo artwork, not an approximated font.
Image.open(p/'measured/40.5.png').convert('RGB').crop((690,470,1243,602)).save(p/'assets/photon-brand-original.png')
logo=next(layer for layer in scene['layers'] if layer['type']=='group' and layer.get('start')==39.6)
logo['children']=[{'id':'photon-original-brand-art','type':'image','src':'assets/photon-brand-original.png','x':-8,'y':-9,'width':553,'height':132}]
scene['source']['notes']+=' V6 late-phase patch: measured per-card30/30.5/31/31.8/32/32.2anchors and staggered card exits; observed prefix/CTAwordreveals; authentic isolated Photonlogo. Original opaque avatar crops preserve white eye highlights and Applelogo, with editable circleextensions only outside assetbounds. Remaining fitted phases are notcertified1:1.'
file=p/'final-v6.scene.json';file.write_text(json.dumps(scene,indent=2));checksum=hashlib.sha256(file.read_bytes()).hexdigest()
(p/'final-v6-changes.json').write_text(json.dumps({'sha256':checksum,'baseline':'final-v5.scene.json','conservative_inclusive_delta_from_v5':[[430,457],[891,1259]],'conservative_inclusive_delta_from_v4':[[414,457],[891,1259]],'conservative_inclusive_delta_from_v3':[[414,800],[891,1259]],'notes':['Opaque separate avatar asset correction preserves white internal features','Measured per-card states replace common-camera assumption','Words and URL use observed separate reveal times','Brandlogo is a supplied rasterbrandasset, not fullsourceframe']},indent=2))
print(checksum)
