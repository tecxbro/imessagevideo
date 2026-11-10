"""Diagnostic native layered reconstruction at486 only; not a full-film scene."""
from pathlib import Path
import sys,json,copy,importlib.util,math
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2,numpy as np
from PIL import Image
from scipy import ndimage
R=Path(__file__).resolve().parent;P=R.parent.parent.parent/'outputs/02-danieltian/final-v13';AS=R/'assets';AS.mkdir(exist_ok=True);spec=importlib.util.spec_from_file_location('trace',R.parent/'trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace);scene=json.loads((P/'scene.json').read_text());src=np.asarray(Image.open(R/'source-native/000486.png').convert('RGB')).astype(float);gray=src.mean(2);BG=253.;caps=json.loads((R/'caps-affine-probe.json').read_text());field=json.loads((R/'field-affine-probe.json').read_text())['486'];atlas=Image.open(R/'local-template-check/16.200.png').convert('RGB')
def absolute(n):
 if n.get('src') and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((P/n['src']).resolve())
 for c in n.get('children',[]):absolute(c)
for n in scene['layers']:absolute(n)
for f in scene.get('fonts',[]):
 if not f['src'].startswith(('/','data:','http:','https:')):f['src']=str((P/f['src']).resolve())
def affine_group(id,M,W,H,children,opacity=1):
 M=np.array(M);U,s,V=np.linalg.svd(M[:,:2])
 if np.linalg.det(U)<0:U[:,1]*=-1;s[1]*=-1
 if np.linalg.det(V)<0:V[1,:]*=-1;s[1]*=-1
 center=M@np.array([W/2,H/2,1]);return dict(id=id,type='group',x=float(center[0]),y=float(center[1]),rotation=math.degrees(math.atan2(U[1,0],U[0,0])),scaleX=float(s[0]),scaleY=float(s[1]),opacity=opacity,children=[dict(id=id+'-inner',type='group',rotation=math.degrees(math.atan2(V[1,0],V[0,0])),children=children)])
def paths(alpha,x,y,id,levels=5):
 peak=float(np.max(alpha));out=[]
 if peak<.003:return out
 steps=np.linspace(.1,.9,levels) if levels>1 else[.5];previous=0.
 for j,t in enumerate(steps):
  d,stats=trace.trace_alpha(alpha,x,y,threshold=float(t*peak));level=min(1,peak*(j+1)/levels);opacity=(level-previous)/(1-previous) if previous<1 else 0;previous=level
  if d:out.append(dict(id=id+'-'+str(j),type='path',d=d,fill='#000000',opacity=float(opacity)))
 return out
# Retire original field/capsule graphs only in this single-frame diagnostic.
for n in scene['layers']:
 if n['id'].startswith('pb-number-'):n['end']=436/30
 if n['id'] in [c['id'] for c in caps]:n['end']=n['start']
new=[]
for q in field:
 if q['opacity']<=.001:continue
 W,H=q['width'],q['height'];id='v14-probe-'+q['id'];node=affine_group(id,q['matrix'],W,H,[dict(id=id+'-art',type='image',src=q['asset'],x=-W/2,y=-H/2,width=W,height=H)],q['opacity']);node.update(start=486/30,end=487/30);new.append(node)
# Isolate each genuine rounded container ring, separately from its moving content.
neutral=src.max(2)-src.min(2)<14;m=neutral&(gray>185)&(gray<247);lab,num=ndimage.label(m);rings=[]
for k,bb in enumerate(ndimage.find_objects(lab),1):
 if bb is None:continue
 yy,xx=bb;w,h=xx.stop-xx.start,yy.stop-yy.start
 if 450<w<800 and 30<h<180:rings.append(dict(label=k,bbox=[xx.start,yy.start,xx.stop,yy.stop]))
print('Native ring candidates',[q['bbox'] for q in rings],flush=True);details=[]
def findImage(n,fragment):
 if n.get('type')=='image' and fragment in n['id']:return n
 for c in n.get('children',[]):
  a=findImage(c,fragment)
  if a:return a
for j,q in enumerate(caps):
 id=q['id'];M=np.array(q['bodyLocalMatrix']);W,H=q['nativeLocalSize'];center=M@np.array([W/2,H/2,1]);ring=min(rings,key=lambda a:np.linalg.norm(np.array([(a['bbox'][0]+a['bbox'][2])/2,(a['bbox'][1]+a['bbox'][3])/2])-center));l,t,r,b=ring['bbox'];bw,bh=r-l,b-t;group=dict(id='v14-probe-card-'+id,type='group',start=486/30,end=487/30,children=[]);children=group['children'];children.append(dict(id=id+'-v14-native-backdrop',type='rect',x=l+1,y=t+1,width=bw-2,height=bh-2,radius=(bh-2)/2,fill='#FDFDFD'))
 rawmask=ndimage.binary_dilation(lab==ring['label'],iterations=2);alpha=np.clip((BG-gray)/BG,0,1)*rawmask;children+=paths(alpha[t-3:b+3,l-3:r+3],l-3,t-3,id+'-v14-native-ring',5)
 # Source projected semantic label remains native contours, rather than italic font substitution.
 L,T,RR,B=l+105,t+5,r-100,b-5;ar=src[T:B,L:RR];a=np.clip((BG-ar.mean(2))/BG,0,1)*(ar.max(2)-ar.min(2)<18);a[ndimage.binary_dilation(rawmask,iterations=3)[T:B,L:RR]]=0;peak=float(a.max());children+=paths(a,L,T,id+'-v14-semantic-label',1 if peak>.95 else 5)
 # Preserve actual plus projection independently of the content's tilt.
 L,T,RR,B=r-100,max(t,int((t+b)/2-38)),r-25,min(b,int((t+b)/2+38));ar=src[T:B,L:RR];a=np.clip((BG-ar.mean(2))/BG,0,1)*(ar.max(2)-ar.min(2)<18);a[ndimage.binary_dilation(rawmask,iterations=3)[T:B,L:RR]]=0;children+=paths(a,L,T,id+'-v14-plus-projection',5)
 body=np.asarray(atlas.crop((j*640+16,20,j*640+16+W,20+H))).copy()
 if id=='pb-uber-eats':
  original=next(n for n in scene['layers'] if n['id']==id);clean=findImage(original,'uber-settled')
  if clean:body=np.asarray(Image.open(clean['src']).convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
 rr,gg,bb=body[:,:,0],body[:,:,1],body[:,:,2];zone=np.zeros((H,W),bool);zone[:,:112]=True
 if 'lyft' in id:mask=zone&(rr>150)&(gg<130)&(bb>130)
 elif 'airbnb' in id:mask=zone&(rr>150)&(gg<150)&(bb>60)&(bb<180)
 elif 'resy' in id:mask=zone&(rr>150)&(gg<130)&(bb<110)
 else:mask=zone&(body.max(2)<95)
 labels,count=ndimage.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0;mask=labels==int(np.argmax(sizes));mask=ndimage.binary_fill_holes(mask);mask=ndimage.binary_dilation(mask,iterations=2);yy,xx=np.nonzero(mask);cl,ct,cr,cb=max(0,int(xx.min())-1),max(0,int(yy.min())-1),min(W,int(xx.max())+2),min(H,int(yy.max())+2);pixels=np.dstack([body[ct:cb,cl:cr],np.uint8(mask[ct:cb,cl:cr])*255]);asset=AS/(id+'-original-logo.png');Image.fromarray(pixels).save(asset);logo=affine_group(id+'-v14-original-logo',M,W,H,[dict(id=id+'-v14-original-logo-art',type='image',src=str(asset.resolve()),x=cl-W/2,y=ct-H/2,width=cr-cl,height=cb-ct)]);children.append(logo);new.append(group);details.append(dict(id=id,ringBox=ring['bbox'],labelPeak=peak,logoCrop=[cl,ct,cr,cb],camera=M.tolist()))
scene['layers']+=new;scene['source']['notes']+=' Diagnostic single-frame486 probe only: separately native borders, semantic label/plus contours, original logo art under measured affine camera, and measured original field image poses. Not valid for a full-film export.';(R/'frame486-layered-prototype.scene.json').write_text(json.dumps(scene,indent=2));(R/'frame486-layered-details.json').write_text(json.dumps(details,indent=2));print('Built layered native486 probe',details,flush=True)
