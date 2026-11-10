"""Native separate food-instance poses measured at source24.5/25/26/26.5.
Runs against the un-frozen v10 candidate; raster files are single original emoji.
"""
from pathlib import Path
import copy,json,hashlib
p=Path(__file__).parent;f=p/'final-v10.scene.json';s=json.loads(f.read_text())
food={x['id']:x for x in s['layers'] if x['id'].startswith('authentic-food-')}
# x,y,width,height at each checkpoint; off-stage entries preserve hidden instances.
poses={
'pizza-left':[(555,300,78,90),(264,546,128,141),(280,677,108,117)],
'pizza-top':[(1495,177,73,84),(969,9,112,142),(1300,-230,70,85)],
'pizza-header':[(980,1027,95,116),(701,142,52,64),(174,374,96,103)],
'pizza-tiny-right':[(943,1019,48,59),(1184,308,48,57),(1295,494,43,51)],
'pizza-card':[(1600,1070,70,82),(-7,817,75,93),(-150,1200,60,73)],
'ramen':[(1868,720,130,124),(1312,374,90,85),(1340,352,81,76)]}
for name,states in poses.items():
 x=food['authentic-food-'+name]
 for key,index in [('x',0),('y',1)]:x['keyframes'][key]=[k for k in x['keyframes'][key] if k['t']<=24.5]+[{'t':t,'value':a[index],'ease':'linear'} for t,a in zip([25,26,26.5],states)]
 for key,index,base in [('scaleX',2,x['width']),('scaleY',3,x['height'])]:x['keyframes'][key]=[k for k in x['keyframes'][key] if k['t']<=24.5]+[{'t':t,'value':a[index]/base,'ease':'linear'} for t,a in zip([25,26,26.5],states)]
 x['keyframes']['rotation']=[{'t':24.333333333333332,'value':0}]
 x['keyframes']['opacity']=[{'t':24.333333333333332,'value':1},{'t':26.6,'value':1},{'t':26.7,'value':0,'ease':'linear'}]
def extra(name,file,w,h,states):
 x={'id':'food-tail-extra-'+name,'type':'image','src':'assets/'+file,'width':w,'height':h,'start':24.5,'end':26.7,'keyframes':{}}
 for key,index,base in [('x',0,1),('y',1,1),('scaleX',2,w),('scaleY',3,h)]:x['keyframes'][key]=[{'t':t,'value':a[index]/base,'ease':'linear'} for t,a in zip([24.5,25,26,26.5],states)]
 x['keyframes']['opacity']=[{'t':24.5,'value':0},{'t':25,'value':1,'ease':'linear'},{'t':26.6,'value':1},{'t':26.7,'value':0,'ease':'linear'}]
 s['layers'].append(x)
extra('pizza-edge','apple-pizza.png',106,117,[(-160,90,106,117),(-140,110,106,117),(-68,126,106,117),(-200,200,106,117)])
extra('ramen-low-right','apple-ramen.png',152,145,[(1600,1150,60,57),(1650,1050,90,86),(1546,950,94,87),(1774,929,120,114)])
extra('ramen-low-phone','apple-ramen.png',152,145,[(1100,1100,40,38),(1200,1100,45,43),(786,855,45,48),(1824,172,97,90)])
extra('ramen-bottom','apple-ramen.png',152,145,[(600,1200,40,38),(600,1200,50,48),(660,1047,69,70),(900,1200,70,67)])
orders={
'p03-220':[(542,493,82,40),(666,710,64,30),(663,283,52,25)],
'p03-224':[(389,637,84,41),(448,949,98,48),(440,1010,94,48)],
'p03-228':[(1061,960,169,90),(1205,-25,126,64),(619,90,93,45)]}
for name,states in orders.items():
 x=next(x for x in s['layers'] if x['id']==name);rect=next(c for c in x['children'] if c['type']=='rect')
 for key,index in [('x',0),('y',1)]:x['keyframes'][key]=[{'t':24.333333333333332,'value':x[key]},{'t':24.5,'value':x[key]}]+[{'t':t,'value':a[index],'ease':'linear'} for t,a in zip([25,26,26.5],states)]
 for key,index,base in [('scaleX',2,rect['width']),('scaleY',3,rect['height'])]:x['keyframes'][key]=[{'t':24.5,'value':1}]+[{'t':t,'value':a[index]/base,'ease':'linear'} for t,a in zip([25,26,26.5],states)]
 x['end']=26.7
base=next(x for x in s['layers'] if x['id']=='p03-220')
for name,states in [('top-order',[(305,16,119,58),(568,-15,64,30),(1400,378,36,22)]),('right-order',[(1247,268,74,35),(2100,300,74,35),(1558,235,79,37)])]:
 x=copy.deepcopy(base);x['id']='food-tail-'+name;x['start']=24.5;x['end']=26.7
 for c in x['children']:c['id']+='-'+name
 for key,index,denominator in [('x',0,1),('y',1,1),('scaleX',2,64),('scaleY',3,30)]:x['keyframes'][key]=[{'t':24.5,'value':states[0][index]/denominator}]+[{'t':t,'value':a[index]/denominator,'ease':'linear'} for t,a in zip([25,26,26.5],states)]
 x['keyframes']['opacity']=[{'t':24.5,'value':0},{'t':24.8,'value':1,'ease':'linear'},{'t':26.6,'value':1},{'t':26.7,'value':0,'ease':'linear'}]
 s['layers'].append(x)
g=next(x for x in s['layers'] if x['id']=='p03-204')
scrim=next(x for x in g['children'] if x['id']=='celebration-phone-ui-scrim')
scrim['keyframes']={'opacity':[{'t':24.333333333333332,'value':12/253},{'t':24.5,'value':12/253},{'t':24.7,'value':0,'ease':'linear'}]}
next(x for x in g['children'] if x['id']=='p03-112')['blur']=8
s['source']['notes']+=' V10 tail: independent floating artwork/bubble instances fitted to native25/26/26.5 positions while24.5 anchors remain unchanged. Intermediate3Dorbits are approximated by observed2D projections.'
f.write_text(json.dumps(s,indent=2));sha=hashlib.sha256(f.read_bytes()).hexdigest();proof=json.loads((p/'final-v10-changes.json').read_text());proof['sha256']=sha;proof['floating_tail_measured_times']=[24.5,25,26,26.5];proof['floating_tail_limitation']='Observed2D projections atanchors; intermediate3Dorbits fitted, not certified frameexact.'
(p/'final-v10-changes.json').write_text(json.dumps(proof,indent=2));print(sha)
