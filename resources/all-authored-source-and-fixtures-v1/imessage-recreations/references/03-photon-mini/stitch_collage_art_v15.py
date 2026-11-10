"""Measure isolated static card UI textures across separately observed app planes.
Never exports a whole reference frame; each output is one390px-wide app interior.
"""
from pathlib import Path
import sys,json,hashlib,cv2,numpy as np
from PIL import Image
p=Path(__file__).parent;sys.path.insert(0,str(p.parent.parent/'engines'));sys.path.insert(0,str(p.parent/'02-danieltian'))
from render_pillow import state
from apply_collage_cameras_v15 import valid,trusted_frames
from trace_glyphs import trace_alpha
src=(p.parent.parent/'outputs/03-photon-mini/final-v14/scene.json').resolve();s=json.load(open(src));grid=next(x for x in s['layers'] if x['id']=='measured-collage-v13');cards=grid['children'];rows=json.load(open(p/'collage-v15-measure/source-feature-tracks.json'));assets=p/'assets/collage-art-v15';assets.mkdir(exist_ok=True);cv2.setNumThreads(1)
frames={r['frame']:cv2.cvtColor(cv2.imread(str(p/'collage-native'/f'{r["frame"]-890:03}.png')),cv2.COLOR_BGR2RGB) for r in rows};X,Y=np.meshgrid(np.arange(390,dtype=np.float32)+.5,np.arange(280,dtype=np.float32)+.5);only=int(sys.argv[sys.argv.index('--only')+1]) if '--only' in sys.argv else None;meta=[];refinements=[]
if only is not None:
 refinements=[r for r in json.load(open(p/'collage-v15-measure/art-refinements-working.json')) if r['index']!=only];meta=[r for r in json.load(open(assets/'provenance.json')) if r['index']!=only]
for index,c in enumerate(cards):
 if only is not None and index!=only:continue
 allowed=trusted_frames(rows,index)
 base=state(c,31);art=c['children'][1];height=art.get('clip',{}).get('height',206);last=next(x for x in reversed(art['children']) if x['type']=='image');fallback=Image.open(src.parent/last['src']).convert('RGB').resize((390,height),Image.Resampling.LANCZOS);canvas=np.full((280,390,3),230,dtype='uint8');canvas[:height]=np.array(fallback);quality=np.full((280,390),np.inf);coverage=np.zeros((280,390),bool);observations=[]
 for row in sorted(rows,key=lambda r:abs(r['frame']-930)):
  q=row['cards'][index]
  if row['frame'] not in allowed:continue
  f=row['frame'];A=np.array(q['affine']);mx=(A[0,0]*(base['x']+X*base['scaleX'])+A[0,1]*(base['y']+Y*base['scaleY'])+A[0,2]-.5).astype('float32');my=(A[1,0]*(base['x']+X*base['scaleX'])+A[1,1]*(base['y']+Y*base['scaleY'])+A[1,2]-.5).astype('float32');visible=(mx>=3)&(mx<1916)&(my>=3)&(my<1076);score=abs(f-930)+q.get('affineRms',0)*.01;take=visible&(score<quality)
  if not take.any():continue
  sample=cv2.remap(frames[f],mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(253,253,253));canvas[take]=sample[take];quality[take]=score;coverage|=take;corners=np.array([[mx[0,0],my[0,0]],[mx[0,-1],my[0,-1]],[mx[-1,-1],my[-1,-1]],[mx[-1,0],my[-1,0]]]);observations.append({'source_frame':f,'source_component_quad':corners.tolist(),'native_pixels_sampled':int(take.sum()),'feature_inliers':q['inliers'],'feature_rms':q['affineRms']})
 file=assets/f'{index:02d}-static-app-interior.png';Image.fromarray(canvas[:height]).save(file);body=assets/f'{index:02d}-measurement-body.png';Image.fromarray(canvas).save(body)
 sem=[x.get('text') or x.get('semanticText') for x in c['children'][2:4]];paths=[]
 # Keep incompletely observed text semantic/live rather than inventing hidden glyphs.
 for line,(top,bottom,gray,fill) in enumerate([(210,247,0,'#000000'),(247,279,170,'#aaaaaa')]):
  band=canvas[top:bottom].astype(float);known=coverage[top:bottom];bg=float(np.percentile(band.mean(2)[known],70)) if known.any() else 230;alpha=np.clip((bg-band.mean(2))/(bg-gray),0,1);alpha[:,0:8]=0;alpha[:,383:]=0
  # Require complete band coverage for source-native outlines; otherwise preserve existing text.
  if known[:,8:383].mean()<.995:continue
  d,stats=trace_alpha(alpha);paths.append({'id':f'collage-v15-semantic-footer-{index}-{line}','type':'path','d':d,'x':0,'y':top,'fill':fill,'semanticText':sem[line],'provenance':{'kind':'Bounded source-native glyph outlines from separately tracked static app footer','sourceFrames':[o['source_frame'] for o in observations],'provenanceFile':'assets/collage-art-v15/provenance.json','bitmapInternalText':False,'stats':stats}})
 row={'index':index,'src':str(file.resolve()),'height':height,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'observedArtCoverage':float(coverage[:height].mean()),'footerPaths':paths,'kind':'Static original single app UI interior; internal text bitmap; native card camera/container/footer separate','observations':observations};refinements.append(row);meta.append({k:v for k,v in row.items() if k!='footerPaths'});print(index,round(row['observedArtCoverage'],3),'paths',len(paths),flush=True)
refinements.sort(key=lambda q:q['index']);meta.sort(key=lambda q:q['index'])
(p/'collage-v15-measure/art-refinements-working.json').write_text(json.dumps(refinements,indent=2));(assets/'provenance.json').write_text(json.dumps(meta,indent=2));print('complete')
