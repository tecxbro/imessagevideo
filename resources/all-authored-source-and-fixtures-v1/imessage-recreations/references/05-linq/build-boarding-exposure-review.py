from pathlib import Path
from PIL import Image
import numpy as np
import json, copy

R=Path('/workspace/imessage-recreations'); REF=R/'references/05-linq'; P=R/'verification/fidelity-review/05-boarding'; BASE=R/'outputs/05-linq/final-v11'; A=REF/'assets/boarding-exposure-review';A.mkdir(exist_ok=True)
scene=json.load(open(BASE/'scene.json')); old=next(l for l in scene['layers']if l['id']=='g-942'); content=next(l for l in old['children']if l['id']=='root-boarding-native-content'); fields=[l for l in old['children']if l['id'].startswith('root-boarding-color-field-')]; fit=json.load(open(P/'exposure-fit.json')); poses={p['frame']:p for p in fit['frames']}; changed=[f for f in range(1185,1200)if f not in [1190,1195]]; count=max(len(poses[f]['samples'])for f in changed)
lin=lambda a:np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
srgb=lambda a:np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)
native=np.array(Image.open(P/'template-native/0.000.png').convert('RGB')).astype(float)/255; black=native[:,:960];white=native[:,960:];alpha=np.clip(1-(white-black).mean(2),0,1);color=np.clip(black/np.maximum(alpha[:,:,None],1e-7),0,1);color[alpha<1e-5]=0; encoded=(color*alpha[:,:,None]).astype('float32'); linear=(lin(color)*alpha[:,:,None]).astype('float32');alpha=alpha.astype('float32')

def rename(layer,prefix):
    layer=copy.deepcopy(layer)
    def walk(node):
        node['id']=prefix+node['id']
        if node.get('src')and not node['src'].startswith(('/','data:','http:')):node['src']=str((BASE/node['src']).resolve())
        for child in node.get('children',[]):walk(child)
    walk(layer)
    return layer

def track(pairs):
    return [dict(t=frame/30,value=float(value),ease='linear')for frame,value in pairs]

original_opacity=track([(f,0 if f in changed else 1)for f in range(1184,1201)])
wrapper_opacity=track([(f,1 if f in changed else 0)for f in range(1184,1201)])
samples=[]
for i in range(count):
    prefix=f'boarding-exposure-{i}-'
    child=rename(content,prefix)
    child['keyframes']={'x':[],'y':[]}
    values=[]
    for frame in range(1184,1201):
        pose=poses.get(frame)
        if frame not in changed or i>=len(pose['samples']):
            opacity=0;delta=0;x=0
        else:
            sample=pose['samples'][i];opacity=sample['weight']/sum(v['weight']for v in pose['samples'][:i+1]);delta=sample['offset'];x=pose['baseX']+pose['deltaX']
        values.append((frame,opacity));child['keyframes']['x'].append(dict(t=frame/30,value=x,ease='linear'));child['keyframes']['y'].append(dict(t=frame/30,value=delta,ease='linear'))
    samples.append(dict(id=prefix+'sample',type='group',children=[rename(field,prefix)for field in fields]+[child],keyframes={'opacity':track(values)}))

# Color-only correction for the locally inferred linear-light shutter. These
# masks are computed from native vectors + generated smooth color fields; never
# from a source motion frame or full-frame runtime screenshot.
mask_provenance=[]; masks=[]
for frame in changed:
    q=poses[frame];Y=q['baseY'];X=q['baseX']+q['deltaX'];field=next(l for l in fields if l['id']==f'root-boarding-color-field-{frame}');texture=np.array(Image.open(BASE/field['src']).convert('RGBA')).astype(float)/255
    original=np.array(Image.open(R/'outputs/05-linq/frames-gsap'/f'{frame:06d}.png').convert('RGB')).astype(float)/255
    z=np.arange(720)-Y-round(field['y']);valid=(z>=0)&(z<len(texture));v=texture[np.clip(z,0,len(texture)-1)];a=v[:,:,3:]*valid[:,None,None];background=original*(1-a)+v[:,:,:3]*a
    C=np.zeros((720,960,3),dtype='float32');L=C.copy();AL=np.zeros((720,960),dtype='float32')
    for sample in q['samples']:
        y0=Y+sample['offset']-200;x0=X;dy0=max(0,y0);dy1=min(720,y0+1400);dx0=max(0,x0);dx1=min(960,x0+960)
        if dy1<=dy0 or dx1<=dx0:continue
        source_y=slice(dy0-y0,dy1-y0);source_x=slice(dx0-x0,dx1-x0);dest_y=slice(dy0,dy1);dest_x=slice(dx0,dx1);w=sample['weight']
        C[dest_y,dest_x]+=w*encoded[source_y,source_x];L[dest_y,dest_x]+=w*linear[source_y,source_x];AL[dest_y,dest_x]+=w*alpha[source_y,source_x]
    cutoff=max(0,Y-154);C[:cutoff]=0;L[:cutoff]=0;AL[:cutoff]=0
    encoded_average=np.clip(C+background*(1-AL[:,:,None]),0,1);target=np.clip(srgb(L+lin(background)*(1-AL[:,:,None])),0,1);delta=np.maximum(0,target-encoded_average);opacity=np.clip(np.max(delta/np.maximum(.005,1-encoded_average),axis=2),0,1);rgb=np.clip((target-encoded_average*(1-opacity[:,:,None]))/np.maximum(1e-7,opacity[:,:,None]),0,1);rgba=np.dstack((rgb,opacity));rgba[opacity<.001]=0
    split1=max(0,min(720,Y+350));split2=max(split1,min(720,Y+600))
    for name,y0,y1 in [('header',0,split1),('pass-panel',split1,split2),('footer',split2,720)]:
        if y1<=y0:continue
        region=rgba[y0:y1];yy,xx=np.where(region[:,:,3]>.001)
        if not len(xx):continue
        x0=int(xx.min());x1=int(xx.max())+1;top=y0+int(yy.min());bottom=y0+int(yy.max())+1;asset=A/f'linear-color-{frame}-{name}.png';Image.fromarray(np.uint8(np.clip(rgba[top:bottom,x0:x1],0,1)*255+.5)).save(asset);masks.append(dict(id=f'boarding-linear-color-{frame}-{name}',type='image',src=str(asset),x=x0,y=top-Y,width=x1-x0,height=bottom-top,start=frame/30,end=(frame+1)/30));mask_provenance.append(dict(frame=frame,component=name,path=str(asset),rect=[x0,top-Y,x1-x0,bottom-top],notice='Transparent color-only native shutter correction computed from isolated editable paths, exposure weights and polynomial color artwork; no source motion-frame pixels.'))
    print('COLOR',frame,flush=True)

wrapper=dict(id='boarding-native-exposure',type='group',start=1185/30,end=1200/30,clip=dict(x=0,y=-154,width=960,height=1600),keyframes={'opacity':wrapper_opacity},children=samples+masks)
spec=dict(changed_frame_ranges=[[1185,1189],[1191,1194],[1196,1199]],root_id='g-942',content_id='root-boarding-native-content',content_opacity=original_opacity,append_children=[wrapper],provenance=dict(controls=[1182,1183,1184,1190,1195,1200],native_sample_count=count,exposure_fit=str(P/'exposure-fit.json'),color_masks=mask_provenance,note='Only g942 native content exposure changes. Original smooth color fields, parent camera, g925/check-in/background, all held controls and all outside states preserved. Native vectors stay editable; transparent local color masks need regeneration when their motion changes. No complete source-frame/video asset.'))
(REF/'boarding-exposure-review-elements.json').write_text(json.dumps(spec,indent=2));print('ELEMENTS',count,spec['changed_frame_ranges'])
