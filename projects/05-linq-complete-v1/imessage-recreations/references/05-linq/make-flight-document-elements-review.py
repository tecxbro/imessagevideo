from pathlib import Path
import json,copy,math,numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path('/workspace/imessage-recreations');REF=R/'references/05-linq';P=R/'verification/fidelity-review/05-flight';A=REF/'assets/flight-document-review';D=json.loads((REF/'flight-document-camera-exposure-review.json').read_text());S=json.loads((R/'outputs/05-linq/final-v10/scene.json').read_text());cam={q['frame']:q for q in D['camera']};bg={q['frame']:q for q in D['background']};base=next(l for l in S['layers'] if l['id']=='broad-v5-background-45');frames=list(range(360,414))
def keys(values):return [dict(t=f/30,value=float(v),ease='linear') for f,v in values]
def absfiles(l):
 if l.get('src') and not l['src'].startswith(('/','data:','http')):l['src']=str((R/'outputs/05-linq/final-v10'/l['src']).resolve())
 for c in l.get('children',[]):absfiles(c)
def freeze(l,prefix):
 l=copy.deepcopy(l);l['id']=prefix+l['id'];l.pop('start',None);l.pop('end',None)
 for k,vs in l.pop('keyframes',{}).items():l[k]=vs[-1]['value']
 l['children']=[freeze(c,prefix) for c in l.get('children',[])] if 'children'in l else l.get('children',[])
 if not l['children']:l.pop('children',None)
 absfiles(l);return l
def img(id,src,x,y,w,h):return dict(id=id,type='image',src=str(src),x=x,y=y,width=w,height=h)
def document(prefix):
 cards=[]
 for c in D['assets']['cards']:
  cards.append(dict(id=prefix+c['name'],type='group',x=c['x']-(1 if c['name']=='basic' else 0),y=550,clip=dict(width=c['width'],height=c['height'],radius=31),children=[img(prefix+c['name']+'-ui',c['path'],0,0,c['width'],c['height'])]))
 return dict(id=prefix+'document',type='group',x=188,clip=dict(width=584,height=2000,radius=64),children=[img(prefix+'top-ui',D['assets']['top'],0,0,584,550),img(prefix+'lower-sky',D['assets']['lowerBackground'],0,550,584,588),dict(id=prefix+'late-tail',type='image',src=str(A/'flight-summary-tail-sharp.png'),x=0,y=418,width=584,height=132,start=380/30),dict(id=prefix+'fare-carousel',type='group',children=cards,keyframes={'x':keys([(f,cam[f]['panX']) for f in frames])})])
# Short entrance component color poses retain the measured source blend. These
# are bounded app-panel poses, never whole source frames; later UI is static.
poses=[];posemeta=[]
for f in range(355,360):
 y=round(cam[f]['raw_profile_fit']['y']);top=max(0,y-20);im=Image.open(P/'source'/f'{f-354:04d}.png').convert('RGB').crop((188,top,772,720));mask=Image.new('L',(584,720-top),0);dr=ImageDraw.Draw(mask);dr.rounded_rectangle((0,y-top,584,2000),radius=64,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(4 if f<357 else 2 if f==357 else 1));# Component captures already include blend; feather edge only.
 # Enlarge alpha support so baked motion softness is retained; outside component
 # is exactly transparent, while inner viewport corners include underlying chat.
 a=np.array(mask);a=np.minimum(255,a.astype('float32')*3).astype('uint8');im.putalpha(Image.fromarray(a));path=A/f'entrance-color-pose-{f}.png';im.save(path)
 poses.append(dict(id=f'flight-review-entrance-{f}',type='group',start=f/30,end=(f+1)/30,clip=dict(x=188,y=0,width=584,height=720),children=[img(f'flight-review-entrance-ui-{f}',path,188,top,584,720-top)]));posemeta.append(dict(frame=f,path=str(path),source_box=[188,top,772,720],camera_y=y,notice='Bounded app-panel color pose355–359 only; local baked linear-light transition includes the underlying blurred chat visible through UI, native camera/clip/lifetime.'))
# Measured static document and native shutter samples. Fully opaque viewport
# samples permit exact weighted averaging without accumulated-alpha ghosts.
N=41;sampletracks=[{'y':[],'opacity':[]} for i in range(N)];bgtracks={'blur':keys([(f,bg[f]['blur'])for f in frames]),'opacity':keys([(f,bg[f]['opacity'])for f in frames])}
for f in frames:
 q=cam[f];kind=q['kernel'];spread=q['spread']
 if not spread:offsets=np.zeros(N);weights=np.zeros(N);weights[0]=1
 else:
  offsets=np.linspace(-spread/2,spread/2,N) if kind=='box' else np.linspace(-3*spread,3*spread,N);weights=np.ones(N) if kind=='box' else np.exp(-.5*(offsets/spread)**2)
 if q.get('exposureSamples'):
  nn=q['exposureSamples'];offsets=np.zeros(N);weights=np.zeros(N)
  for j,z in enumerate(nn):offsets[j]=z['offset'];weights[j]=z['weight']
 cumsum=np.cumsum(weights)
 for i in range(N):
  sampletracks[i]['y'].append((f,q['y']+offsets[i]));sampletracks[i]['opacity'].append((f,weights[i]/cumsum[i] if cumsum[i] else 0))
samples=[]
for i in range(N):
 pre=f'flight-review-shutter-{i}-';doc=document(pre);doc['keyframes']={'y':keys(sampletracks[i]['y'])}
 children=[dict(id=pre+'white-pane',type='rect',x=188,y=0,width=584,height=720,fill='#ffffff'),dict(id=pre+'settled-chat',type='group',children=[freeze(c,pre) for c in base['children']],keyframes=copy.deepcopy(bgtracks)),doc]
 samples.append(dict(id=pre+'sample',type='group',children=children,keyframes={'opacity':keys(sampletracks[i]['opacity'])}))
color=json.loads((REF/'flight-shutter-color-review.json').read_text());samples+=color['layers']
newgroup=dict(id='flight-review-continuous-document',type='group',start=12,end=13.8,clip=dict(x=188,y=0,width=584,height=720),children=samples)
# Source352 state and accepted414+ behavior exactly retained.
blurkeys=[dict(t=352/30,value=0,ease='linear')]+keys([(f,bg[f]['blur'])for f in range(353,414)])+[dict(t=414/30,value=10,ease='linear')]
opkeys=[dict(t=352/30,value=1,ease='linear')]+keys([(f,bg[f]['opacity'])for f in range(353,414)])+[dict(t=414/30,value=1,ease='linear')]
spec=dict(changed_frame_ranges=[[353,413]],gates={'broad-v5-group-55':{'start':414/30},'rich-group-4':{'start':414/30}},background_id=base['id'],background_tracks=dict(blur=blurkeys,opacity=opkeys),insert_before={'broad-v5-group-55':poses+[newgroup]},provenance=dict(static_document=D['assets'],entrance_poses=posemeta,local_shutter_color=color['provenance'],late_summary_tail=color['late_tail'],shutter='41 native source-camera exposure samples for370–379; one static UI doc, fixed lower sky and independent fare cards. No complete source-frame/video asset.',limitations='Five355–359 bounded app color poses retain source transition color blend; native settled static product UI uses bitmap internals. Camera/clip/lifetimes/shutter/background actors editable.'))
(REF/'flight-document-review-elements.json').write_text(json.dumps(spec,indent=2));print('elements',len(json.dumps(spec)),flush=True)
