from pathlib import Path
import ast,json,numpy as np
from PIL import Image
from functools import lru_cache
from scipy import signal,ndimage
R=Path('/workspace/imessage-recreations');REF=R/'references/06-gallery';P=R/'verification/fidelity-review/06-intro';AS=REF/'assets/intro-review';tree=ast.parse((REF/'build-intro-review.py').read_text());names={'frame','box','energy','match','fit'};exec(compile(ast.Module(body=[q for q in tree.body if isinstance(q,ast.FunctionDef) and q.name in names],type_ignores=[]),'pure-functions','exec'),globals())
def ink(a,white=255):return np.clip((255-a.mean(2))/240,0,1).astype('float32')
s=json.loads((REF/'intro-review-elements.json').read_text());g=s['insert_before']['g-1129'][0];ns={q['id']:q for q in g['children']};n=ns['rene-intro-priya'];cb=n['sourceBounds'];tb=[704,774,1176,850];raw=ink(frame(69)[tb[1]:tb[3],tb[0]:tb[2]]);bb=box(raw>.15);A=raw[bb[1]:bb[3],bb[0]:bb[2]];tx=tb[0]+bb[0];ty=tb[1]+bb[1];q=fit(30,A,[300,760,1550,1080],1.94,spread=.055)
if q and q['score']>.85 and q['alpha']>.025:
 o=dict(frame=30,correlation=q['score'],x=q['x']+q['sx']*(cb[0]-tx),y=q['y']+q['sy']*(cb[1]-ty),scaleX=q['sx'],scaleY=q['sy'],opacity=q['alpha']);s['measurements']['priya'].insert(0,o);n['start']=1;n['keyframes']={k:[dict(t=z['frame']/30,value=z[k],ease='linear') for z in s['measurements']['priya']] for k in ['x','y','scaleX','scaleY','opacity']};print('priya30',q)
# Locate plus geometry directly, including the partially clipped lower arm at32–34.
a=frame(39);roi=[320,990,430,1080];m=a[roi[1]:roi[3],roi[0]:roi[2]].max(2)<150;bb=box(m);ref=a[roi[1]:roi[3],roi[0]:roi[2]];ys,xs=np.where(m);refWidth=bb[2]-bb[0];row=np.argmax(m.sum(1));refCenterY=roi[1]+row;refMinX=roi[0]+bb[0];obs=s['measurements']['composer'];cb=ns['rene-intro-precut-composer']['sourceBounds']
for f in range(31,54):
 a=frame(f);z=a[940:1080,250:550];m=z.max(2)<175;lab,num=ndimage.label(m);c=[]
 for j,sl in enumerate(ndimage.find_objects(lab),1):
  if sl is None:continue
  yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
  if 24<w<80 and 15<h<85 and yy.stop+940>990 and np.count_nonzero(lab[sl]==j)>80:c.append((yy.start+940,xx.start+250,j,sl))
 if not c:continue
 cy,cx,j,sl=max(c,key=lambda q:q[0]);sub=(lab[sl]==j);w=sl[1].stop-sl[1].start;sc=w/refWidth;centerY=sl[0].start+940+int(np.argmax(sub.sum(1)));alpha=min(1,float((255-z[sl].mean(2))[sub].max())/240);v=dict(frame=f,x=cx+(cb[0]-refMinX)*sc,y=centerY+(cb[1]-refCenterY)*sc,scaleX=sc,scaleY=sc,opacity=alpha,directPartialPlus=True);obs=[q for q in obs if q['frame']!=f]+[v]
obs.sort(key=lambda q:q['frame']);s['measurements']['composer']=obs;n=ns['rene-intro-precut-composer'];keys={k:[dict(t=q['frame']/30,value=q[k],ease='linear') for q in obs] for k in ['x','y','scaleX','scaleY','opacity']};glyph=dict(n);glyph['id']=n['id']+'-glyphs';glyph.pop('keyframes');glyph['x']=glyph['y']=0;glyph.pop('start',None);glyph.pop('end',None)
wrapped=dict(type='group',id=n['id'],start=obs[0]['frame']/30,end=54/30,keyframes=keys,children=[dict(type='rect',id='rene-intro-composer-field',x=170,y=16,width=1145,height=130,radius=65,fill='#ffffff',shadow=dict(x=0,y=0,blur=18,color='#eeeeee')),dict(type='circle',id='rene-intro-composer-plus-disc',x=1,y=24,width=140,height=140,fill='#ffffff',shadow=dict(x=0,y=0,blur=18,color='#eeeeee')),glyph]);g['children']=[wrapped if q['id']==n['id'] else q for q in g['children']];(REF/'intro-review-elements.json').write_text(json.dumps(s,indent=2));print('plusframes',[q['frame'] for q in obs])
