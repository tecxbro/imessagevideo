"""Correct exact127 outgoing menu /128 blank /129 blurred Games entrance.
Separate semantic element assets; preserves all accepted Games130+.
"""
from pathlib import Path
import json,hashlib,sys,numpy as np
from PIL import Image
sys.path.insert(0,'/workspace/imessage-recreations/references/02-danieltian')
from trace_glyphs import trace_alpha
R=Path('/workspace/imessage-recreations');REF=R/'references/05-linq';SRC=REF/'assets/root-handoffs-measure';AS=REF/'assets/menu-games-handoff-review';AS.mkdir(exist_ok=True);ledger=[]
def frame(f):return np.array(Image.open(SRC/f'frame-{f}.png').convert('RGB')).astype(float)
def art(f,b,id,semantic):
 a=frame(f)[b[1]:b[3],b[0]:b[2]];al=(255-a.min(2))/255;al[al<2/255]=0;rgb=np.where(al[:,:,None]>0,(a-255*(1-al[:,:,None]))/np.maximum(1e-5,al[:,:,None]),0);rgba=np.concatenate((np.clip(rgb,0,255),al[:,:,None]*255),2).round().astype('uint8');p=AS/(id+'.png');Image.fromarray(rgba).save(p);n=dict(type='image',id=id,src=str(p),x=b[0],y=b[1],width=b[2]-b[0],height=b[3]-b[1],sourceFrame=f,sourceBounds=b,semanticText=semantic,editability='Independently bounded original semantic UI pose; native geometry/lifetime, bitmap internal artwork.');ledger.append(dict(id=id,sourceFrame=f,sourceBounds=b,asset=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sourceSHA256=hashlib.sha256((SRC/f'frame-{f}.png').read_bytes()).hexdigest(),notice=n['editability']));return n
# Faded outgoing app menu: native label/watch contours plus isolated original icons.
menu=[dict(type='rect',id='handoff-menu-white-card',x=108,y=-600,width=736,height=1270,radius=95,fill='#ffffff',opacity=.8,shadow=dict(x=0,y=0,blur=12,color='#eeeeee'))]
for name,b in [('Polls',[310,0,730,80]),('Store',[310,130,730,250]),('GamePigeon',[310,280,790,410]),('Threadsby',[310,440,780,555]),('Star Flights',[310,590,790,685]),('Threadsby watch icon',[205,450,275,525])]:
 a=frame(127)[b[1]:b[3],b[0]:b[2]];al=(255-a.mean(2))/255;al[a.max(2)-a.min(2)>12]=0;pk=float(al.max());mask=al>pk*.5;y,x=np.where(mask);bb=[b[0]+int(x.min())-2,b[1]+int(y.min())-2,b[0]+int(x.max())+3,b[1]+int(y.max())+3];bb=[max(0,bb[0]),max(0,bb[1]),min(960,bb[2]),min(720,bb[3])];a=frame(127)[bb[1]:bb[3],bb[0]:bb[2]];al=(255-a.mean(2))/255;al[a.max(2)-a.min(2)>12]=0;d,stats=trace_alpha(np.clip(al/max(.001,pk),0,1),bb[0],bb[1]);id='handoff-menu-'+name.lower().replace(' ','-');menu.append(dict(type='path',id=id,d=d,fill='#000000',opacity=pk,semanticText=name,sourceFrame=127,sourceBounds=bb,editability='Native editable semantic contour, measured faded source opacity.'));ledger.append(dict(id=id,sourceFrame=127,sourceBounds=bb,opacity=pk,**stats))
for name,b in [('Polls',[178,0,299,75]),('Store',[178,125,299,237]),('GamePigeon',[176,294,304,391]),('Star Flights',[176,599,304,674])]:menu.append(art(127,b,'handoff-menu-icon-'+name.lower().replace(' ','-'),name+' icon'))
menuGroup=dict(type='group',id='handoff-outgoing-menu-127',start=127/30,end=128/30,children=menu)
# The first Games pose is before the accepted root helper starts. Motion-blurred
# card/footer fields share pixels; non-overlapping semantic partitions avoid duplicate ink.
games=[]
for name,b in [('drawer handle',[430,50,532,96]),('Games avatar',[376,91,445,170]),('Games heading',[445,91,586,170])]:games.append(art(129,b,'handoff-games-'+name.replace(' ','-'),name))
for i,(name,b) in enumerate([('8 BALL',[130,170,358,475]),('CHESS',[367,170,595,475]),('FOUR IN A ROW',[603,170,832,475]),('WORD GAMES',[130,475,358,720]),('CRAZY 8',[367,475,595,720]),('CUP PONG',[603,475,832,720])]):games.append(art(129,b,f'handoff-games-card-{i}-129',name+' preview / footer'))
gamesGroup=dict(type='group',id='handoff-games-entry-129',start=129/30,end=130/30,children=games)
spec=dict(gates={'g-119':{'end':127/30},'g-138':{'start':129/30}},insert_before={'g-138':[menuGroup]},prepend_children={'g-138':[gamesGroup]},changed_frame_ranges=[[127,129]],assets=ledger,cause='Old menu stayed active128–129 while source128 is white and129 already shows motion-blurred Games; Games root began130, one frame late. Native127 outgoing menu fade/geometry was also different from its generic held model.',notice='Independent semantic menu labels/icons and Games cards/header/handle, not a complete frame/video playback. Accepted root Games130+ and all earlier126- states are preserved. Neutral card shadow and contour AA are approximate.');(REF/'menu-games-handoff-review-elements.json').write_text(json.dumps(spec,indent=2));(REF/'menu-games-handoff-review-provenance.json').write_text(json.dumps(dict(assets=ledger,notice=spec['notice']),indent=2));print('menu elements',len(menu),'games elements',len(games))
