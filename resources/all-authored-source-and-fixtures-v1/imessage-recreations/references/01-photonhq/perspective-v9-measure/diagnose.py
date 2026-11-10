"""Read-only per-card pose/material attribution for held V7 native PNGs."""
from pathlib import Path
import json,sys,numpy as np,cv2
from PIL import Image
root=Path('/workspace/imessage-recreations');p=root/'references/01-photonhq';out=p/'perspective-v9-measure';sys.path.insert(0,str(root/'engines'));from render_pillow import state
scenePath=root/'outputs/01-photonhq/final-v7/scene.json';scene=json.load(open(scenePath));cv2.setNumThreads(1);records=[]
for f in (256,307):
 src=np.array(Image.open(p/'early-walls-v7-measure'/f'frame-{f-(248 if f<282 else 263):03}.png').convert('RGB'));native=np.array(Image.open(root/f'outputs/01-photonhq/cache/motion-canvas/{f:06}.png').convert('RGB'));delta=np.abs(src.astype(float)-native.astype(float)).mean(2);cards=[]
 for n in scene['layers']:
  st=state(n,f/30)
  if not n['id'].startswith('early-wall-native-v7-') or n['type']!='image' or not(st.get('start',0)<=f/30<st.get('end',scene['duration']) and st['opacity']>0):continue
  x,y,sx,sy=st['x'],st['y'],st['scaleX'],st['scaleY'];w,h=st['width'],st['height'];x0,y0,x1,y1=max(0,int(x)),max(0,int(y)),min(1920,int(np.ceil(x+w*sx))),min(1080,int(np.ceil(y+h*sy)))
  if x1<=x0 or y1<=y0:continue
  art=Image.open(scenePath.parent/n['src']).convert('RGBA');bg=Image.new('RGBA',art.size,(253,253,253,255));bg.alpha_composite(art);a=np.array(bg.convert('RGB').resize((w,h)),dtype='uint8');X,Y=np.meshgrid(np.arange(w,dtype='float32'),np.arange(h,dtype='float32'));mx=x+X*sx;my=y+Y*sy;valid=(mx>2)&(mx<1917)&(my>2)&(my<1077);b=cv2.remap(src,mx.astype('float32'),my.astype('float32'),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(253,253,253));row={'id':n['id'],'nativeBox':[x,y,x+w*sx,y+h*sy],'pixelArea':(x1-x0)*(y1-y0),'globalErrorContribution':float(delta[y0:y1,x0:x1].sum()/delta.size),'beforeLocalMae':float(np.abs(a.astype(float)-b.astype(float))[valid].mean())};mask=valid.astype('uint8')*255
  for typ,label in ((cv2.MOTION_AFFINE,'affine'),(cv2.MOTION_HOMOGRAPHY,'projective')):
   warp=np.eye(3,dtype='float32') if typ==cv2.MOTION_HOMOGRAPHY else np.eye(2,3,dtype='float32')
   try:
    score,W=cv2.findTransformECC(cv2.cvtColor(a,cv2.COLOR_RGB2GRAY).astype('float32')/255,cv2.cvtColor(b,cv2.COLOR_RGB2GRAY).astype('float32')/255,warp,typ,(cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,120,1e-6),mask,3)
    warped=cv2.warpPerspective(b,W,(w,h),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderValue=(253,253,253)) if typ==cv2.MOTION_HOMOGRAPHY else cv2.warpAffine(b,W,(w,h),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderValue=(253,253,253))
    row[label]={'ecc':float(score),'matrix':W.tolist(),'registeredMae':float(np.abs(a.astype(float)-warped.astype(float))[valid].mean())}
   except cv2.error as e:row[label]={'failed':str(e).split('\n')[0]}
  cards.append(row)
 records.append({'frame':f,'cards':sorted(cards,key=lambda q:q['globalErrorContribution'],reverse=True)});(out/'pose-material-attribution.json').write_text(json.dumps(records,indent=2)+'\n');print('frame',f,'cards',len(cards),flush=True)
print('complete')
