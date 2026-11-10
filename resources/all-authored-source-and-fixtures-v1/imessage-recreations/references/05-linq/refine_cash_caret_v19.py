"""Separate one original static Cash input caret from its bounded UI material."""
from pathlib import Path
import json,copy,importlib.util
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares
D=Path(__file__).resolve().parent;R=D.parent.parent;M=D/'measurements/composer-v19';F=M/'native';s=json.loads((D/'scene-composers-v19-refined.json').read_text());cash=next(q for q in s['layers']if q['id']=='linq-measured-v6-group-36');c=next(q for q in cash['children']if q['id']=='v10-cash-composer');im=c['children'][0];a=np.array(Image.open(im['src']).convert('RGB'));clean=np.array(Image.open(F/'source-000776.png').convert('RGB'))[125:229,172:790];ac=a.astype(float);ch=np.maximum(ac[:,:,2]-ac[:,:,0],0);mask=np.zeros(ch.shape,bool);mask[24:77,124:137]=ch[24:77,124:137]>2;out=a.copy();out[mask]=clean[mask];asset=M/'cash-ui-with-independent-caret.png';Image.fromarray(out).save(asset)
# Preserve the existing static bitmap outside the actual Cash input lifecycle.
im['src']=str(asset.resolve());im['editability']='Original bounded static composer material with its blue caret removed; one independent native glyph carries the actual blink timing. All other material pixels are preserved.'
patch=ch[24:77,124:137];alpha=np.clip(patch/226,0,1);spec=importlib.util.spec_from_file_location('trace',D.parent/'02-danieltian/trace_glyphs.py');trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace);path,stats=trace.trace_alpha(alpha)
ky=c['keyframes']['y'];ts=np.array([q['t']*30 for q in ky]);vs=np.array([q['value']for q in ky]);rows=[]
for f in range(768,827):
 cy=float(np.interp(f,ts,vs));ar=np.array(Image.open(F/f'source-{f:06d}.png').convert('RGB')).astype(float);target=np.maximum(ar[:,:,2]-ar[:,:,0],0);x0,x1=292,315;y0=max(0,int(146+cy)-7);y1=min(720,int(209+cy)+7);xx,yy=np.meshgrid(np.arange(x0,x1),np.arange(y0,y1));obs=target[yy,xx];obs[obs<5]=0
 def model(q):return map_coordinates(patch,[yy-(150+cy+q[1]),xx-(296+q[0])],order=1,mode='constant',cval=0,prefilter=False)
 def residual(q):
  m=model(q);op=float(np.clip((m*obs).sum()/max((m*m).sum(),1),0,1));return(m*op-obs).ravel()/30
 if obs.sum()<50:dx,dy,op=0.,0.,0.
 else:
  z=least_squares(residual,[0.,0.],bounds=([-5,-7],[5,7]),max_nfev=50,diff_step=[.001,.001]).x;m=model(z);op=float(np.clip((m*obs).sum()/max((m*m).sum(),1),0,1));dx,dy=map(float,z)
 rows.append(dict(frame=f,x=296+dx,y=150+dy,opacity=op))
caret={'type':'group','id':'v19-cash-independent-caret','semanticText':'Blinking input insertion caret','start':768/30,'end':827/30,'children':[{'type':'path','id':'v19-cash-caret-original-glyph','d':path,'fill':'#008fe2'}],'keyframes':{k:[{'t':q['frame']/30,'value':round(float(q[k]),6),'ease':'linear'}for q in rows]for k in ['x','y','opacity']}}
# Keep the genuine static caret's tiny codec-softened color fringe as one bounded UI detail.
rgba=np.dstack([a[24:77,124:137],mask[24:77,124:137].astype(np.uint8)*255]);caret_asset=M/'cash-original-caret-detail.png';Image.fromarray(rgba,'RGBA').save(caret_asset)
caret['children']=[{'type':'image','id':'v19-cash-caret-original-detail','src':str(caret_asset.resolve()),'width':13,'height':53,'editability':'Single original static UI caret detail with its genuine color fringe; independent native position and opacity keys.'}]
c['children'].append(caret);(D/'scene-composers-caret-v19.json').write_text(json.dumps(s,indent=2)+'\n');(M/'cash-caret-measurements.json').write_text(json.dumps({'rows':rows,'trace':stats,'sourceAsset':im['src'],'cleanBackgroundFrame':776,'cleanSourceBounds':[172,125,790,229],'changedOriginalAssetPixels':int(mask.sum()),'method':'One original caret shape; actual numeric pose and blink opacity. Only former cyan pixels in the bounded UI material are restored from one genuine pre-caret static plate. No source-frame sequence.'},indent=2)+'\n');print('caret rows',len(rows),'changed pixels',mask.sum());print(D/'scene-composers-caret-v19.json')
