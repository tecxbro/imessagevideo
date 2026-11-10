"""Replace the empty/mispositioned Linq brand with bounded native traced paths."""
import importlib.util,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('trace_glyphs',ROOT.parent/'02-danieltian/trace_glyphs.py')
tracer=importlib.util.module_from_spec(spec);spec.loader.exec_module(tracer)
s=json.loads((ROOT/'scene.json').read_text())
source=Image.open(ROOT/'keyframes/046.50.png').convert('RGB')
parts=[];provenance=[a for a in json.loads((ROOT/'assets/asset-provenance.json').read_text()) if a.get('path') not in ['assets/linq-mark.png','assets/linq-wordmark-original.png']]
for label,box,name in [('mark',(408,323,466,394),'linq-mark.png'),('wordmark',(479,337,553,385),'linq-wordmark-original.png')]:
 crop=np.asarray(source.crop(box)).astype(float);alpha=1-crop.mean(axis=2)/255
 assert alpha.max()>.99 and np.count_nonzero(alpha>.5)>500
 rgba=np.zeros((*alpha.shape,4),np.uint8);rgba[:,:,3]=np.round(alpha*255).astype(np.uint8)
 Image.fromarray(rgba).save(ROOT/'assets'/name)
 assert Image.open(ROOT/'assets'/name).getbbox() is not None
 d,stats=tracer.trace_alpha(alpha,box[0],box[1])
 parts.append({'type':'path','id':'linq-closing-native-'+label,'d':d,'fill':'#000000'})
 provenance.append({'path':'assets/'+name,'timestamp':46.5,'box':list(box),'kind':'bounded original brand alpha, traced to editable native paths; raster not used by final scene','trace':stats})
base=(255-np.asarray(source).astype(float))[310:405,395:565]
den=np.sum(base*base)
cmd=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss',str(1373/30),'-i',str(ROOT/'source.mp4'),'-t',str(85/30),'-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1']
p=subprocess.Popen(cmd,stdout=subprocess.PIPE);opacity=[];measurements=[]
for f in range(1373,1458):
 b=p.stdout.read(960*720*3)
 if len(b)!=960*720*3:raise RuntimeError('Incomplete closing decode')
 a=np.frombuffer(b,np.uint8).reshape(720,960,3).astype(float)
 value=float(np.clip(np.sum(base*(255-a[310:405,395:565]))/den,0,1))
 if f<1418:value=1.0
 opacity.append({'t':f/30,'value':value,'ease':'linear'})
 measurements.append({'frame':f,'opacity':value})
p.wait()
assert p.returncode==0
for layer in s['layers']:
 if layer.get('id')=='g-1069':layer['end']=1373/30
 if layer.get('id')=='g-1072':
  layer.update(children=parts,start=1373/30,end=1458/30,keyframes={'opacity':opacity})
(ROOT/'scene.json').write_text(json.dumps(s,indent=2)+'\n')
(ROOT/'assets/asset-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
(ROOT/'assets/closing-brand-opacity-track.json').write_text(json.dumps(measurements,indent=2)+'\n')
print('Rest bounds mark409,325–464,392; word481,339–551,383. Native traced paths:',len(parts))
