from pathlib import Path
import json
r=Path('/workspace/imessage-recreations');d=r/'references/05-linq';s=json.loads((d/'scene.json').read_text());seq=0

def ident(a):
 global seq;seq+=1;return f'linq-measured-v6-{a}-{seq}'
def rect(x,y,w,h,fill,r=0,**kw):return dict(type='rect',id=ident('rect'),x=x,y=y,width=w,height=h,fill=fill,radius=r,**kw)
def text(t,x,y,z,fill='#ffffff',**kw):return dict(type='text',id=ident('text'),text=t,x=x,y=y,fontSize=z,fontFamily='SF Pro Display',fontWeight=400,lineHeight=z*1.18,fill=fill,**kw)
def circle(x,y,w,fill,**kw):return dict(type='circle',id=ident('circle'),x=x,y=y,width=w,height=w,fill=fill,**kw)
def tr(*p):return [{'t':t,'value':v,'ease':'linear'} for t,v in p]
def group(ch,**kw):return dict(type='group',id=ident('group'),children=ch,**kw)
# Data-driven chess brackets from native source every3frames.
for g in s['layers']:
 if g.get('start')==6.97:
  ch=g['children'];white=next(q for q in ch if 'white-pawn-sprite' in q.get('src',''));black=next(q for q in ch if 'black-pawn-sprite' in q.get('src',''));glow=next(q for q in ch if q.get('fill')=='#5ca8ff')
  white['keyframes']['y']=tr((6.97,510),(7.5,510),(7.6,433));black['keyframes']['y']=tr((6.97,125),(8.1,125),(8.2,279));glow['keyframes']['opacity']=tr((7.12,0),(7.2,.3),(7.7,.3),(7.9,0));g['children']=[ch[0],glow,white,black]
 if g.get('start')==28.83:
  q=g['children'][1];q['keyframes']['x']=tr((28.83,188),(29.2,188),(29.5,417));q['keyframes']['y']=tr((28.83,136),(29.2,136),(29.5,365))
 if g.get('start') in [30.25,30.1] and any('winning-label' in q.get('src','') for q in g.get('children',[])):
  g.update(start=30.1,originX=479,originY=360);g['keyframes']={'opacity':tr((30.1,0),(30.2,1)),'scaleX':tr((30.1,.25),(30.25,1.05),(30.3,1)),'scaleY':tr((30.1,.25),(30.25,1.05),(30.3,1))}
 if g.get('start')==30.2 and len(g.get('children',[]))>50:
  g['start']=30.3
  for q in g['children']:
   for a in q.get('keyframes',{}).values():
    for k in a:
     if k['t']==30.2:k['t']=30.3
 if g.get('start')==35.63 and g['children'][-1].get('id')!='restaurant-fixed-photo-clip-v6':
  inner=g['children'][-1];inner.pop('clip',None);g['children'][-1]={'id':'restaurant-fixed-photo-clip-v6','type':'group','clip':{'x':190,'y':303,'width':584,'height':333},'children':[inner]}
# A blur backdrop must be behind all sheets, never over the active seats.
bg=[g for g in s['layers'] if g.get('blur')==10 and g.get('start')==11.8666667];s['layers']=bg+[g for g in s['layers'] if g not in bg and g.get('start')!=25.33]
# Native AppleCash panel follows measured26s/26.8s/27s vertical anchors and rolls its amount.
ch=[circle(180,138,78,'#ffffff'),rect(273,138,509,81,'#ffffff',41),rect(206,173,30,4,'#555555',2),rect(219,160,4,30,'#555555',2),text('iMessage',303,155,32,'#bcbcbc'),rect(303,155,2,40,'#59b8f5'),rect(728,160,16,25,'none',8,stroke='#bcbcbc',strokeWidth=3),dict(type='path',id=ident('microphone'),d='M 722 177 Q 722 190 736 190 Q 750 190 750 177 M 736 190 L 736 198 M 729 198 L 743 198',fill='none',stroke='#bcbcbc',strokeWidth=3),rect(185,235,590,461,'#111111',75),rect(454,242,54,6,'#555555',3),circle(279,365,68,'#222222',stroke='#333333',strokeWidth=1),rect(298,396,30,5,'#ffffff',2),circle(615,359,80,'#737373',stroke='#aaaaaa',strokeWidth=1),rect(636,395,39,6,'#ffffff',3),rect(652,378,6,40,'#ffffff',3)]
# The fixed prefix and decimals share a clipped roller for the changing ones digit.
roller=group([text(v,0,i*100,76,shadow={'x':0,'y':2,'blur':0,'color':'#777777'}) for i,v in enumerate('890123456')],keyframes={'y':tr(*[(25.6+i*.1,-100*i) for i in range(9)])})
ones=group([roller],x=126.55,clip={'width':47,'height':90})
amount=group([text('$15',0,0,76,end=25.8),text('$16',0,0,76,start=25.8),ones,text('.89',173.45,0,76,shadow={'x':0,'y':2,'blur':0,'color':'#777777'})],x=352,y=344,scaleX=.91,clip={'width':283,'height':90});ch.append(amount)
ch +=[text('Show Keypad',480,494,20,'#777777',textAnchor='middle'),rect(231,585,235,72,'#252525',36,stroke='#777777',strokeWidth=1),rect(494,585,235,72,'#252525',36,stroke='#777777',strokeWidth=1),text('Request',348,604,28,textAnchor='middle'),text('Send',612,604,28,textAnchor='middle')]
s['layers'].append(group(ch,start=25.33,end=27.67,keyframes={'y':tr((25.33,600),(25.7,200),(26,96),(26.8,0),(27,-2))}))
s['source']['notes']+=' Finalv6 corrects fixed clipping order and native source-bracket chess timing; payment amount rolls through162.89at26s and settles166.89, panel rises through source26/26.8/27cameraanchors with native circularcontrols. Both pictures and motion remain independently authored.'
(d/'scene.json').write_text(json.dumps(s,indent=2));print('Linq final measurement pass written')
