"""Replace remaining generic edge-logo shapes with authentic visible source artwork."""
from pathlib import Path
from PIL import Image
import json,copy,hashlib
p=Path(__file__).parent;im=Image.open(p/'native/39.0.png').convert('RGBA');fps=30000/1001;provenance=[]
s=json.loads((p/'scene-v4-refined.json').read_text());grid=[l for l in s['layers'] if l.get('start')==37.8 and l.get('end')==40.6];zoom=240/224;t39,t40=1169/fps,1199/fps
# Every visible part at rest/zoom is overlaid directly from that instance's own artwork crop.
cases=[(6,'spiral','brand-spiral-auth-composite.png',(0,292,155,517),(70,0),(8,-1)),(17,'spiral','brand-spiral-auth-composite.png',(1286,564,1440,789),(0,0),(-1,-1)),(12,'outlook','brand-outlook-auth-composite.png',(0,564,155,789),(78,0),(0,-1)),(23,'outlook','brand-outlook-auth-composite.png',(1286,836,1440,1061),(0,0),(-1,-1)),(18,'netlify',None,(0,836,155,1061),(78,0),(0,-1)),(5,'strava',None,(1285,21,1440,246),(0,0),(-2,-1))]
modified=[]
for i,name,whole,box,local,shift in cases:
 g=grid[i];oldkids=g['children'];file=p/'assets'/f'grid-{name}-{i}-visible.png';crop=im.crop(box);crop.save(file)
 if whole:g['children']=[{'id':g['id']+'-auth-base','type':'image','src':'assets/'+whole,'x':0,'y':0,'width':225,'height':225}]
 g['children'].append({'id':g['id']+'-auth-visible','type':'image','src':'assets/'+file.name,'x':local[0],'y':local[1],'width':crop.width,'height':crop.height})
 for prop,delta in [('x',shift[0]),('y',shift[1])]:
  for key in g['keyframes'][prop]:
   if key['t']>=t39-1e-8:
    scale=1+(key['t']-t39)/(t40-t39)*(zoom-1);key['value']+=delta*scale
 modified.append(g['id']);provenance.append({'asset':'assets/'+file.name,'source_frame':1169,'presentation_time':1169/fps,'source_crop':box,'local_placement':local,'parent_grid_index':i,'rest_pose_shift':shift,'purpose':'Authentic pixels for this visible static brand tile instance; no full reference frame/video layer. Outside known pixels, existing or reconstructed static fallback remains during the brief entry.','sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
s['source']['notes']+=' V5 artwork repair: generic spiral/Outlook geometry replaced by complementary authentic static logo crops; exact per-instance visible parts overlaid forspiral,Outlook,Netlify,Strava. Unknown offscreen entry pixels retain declared fallback; no full reference frames used.'
out=p/'scene-v5-artwork.json';out.write_text(json.dumps(s,indent=2));(p/'assets/grid-visible-provenance.json').write_text(json.dumps(provenance,indent=2))
report={'scene':out.name,'scene_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent':'scene-v4-refined.json','parent_sha256':hashlib.sha256((p/'scene-v4-refined.json').read_bytes()).hexdigest(),'delta_from_v4_inclusive':[[1133,1216]],'cli_ranges_from_v4':'1133:1216','changed_frames':84,'modified_grid_groups':modified,'artwork_provenance':'assets/grid-visible-provenance.json','status':'Prepared immutable artwork correction. Known visible pixels are authentic crops; unseen entry portions retain declared static fallback. Not1:1 certified.'};(p/'final-v5-scene.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
