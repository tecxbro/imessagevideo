"""Hash-bound disjoint native-region attribution of final source peaks."""
from pathlib import Path
import importlib.util,json,hashlib,sys,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from v8_utils import at
from scipy import ndimage
p=Path(__file__).parent;root=p.parent.parent;spec=importlib.util.spec_from_file_location('comparison',root/'verification/compare.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);s=json.loads((root/'outputs/04-poke/final-v19/scene.json').read_text());scene={g['id']:g for g in s['layers']};scan=json.loads((root/'verification/timeline-scans/04-poke-v19/scan.json').read_text());worst=max(scan['peaks'],key=lambda v:v['mae'])['candidate_frame'];frames=sorted({worst,758,108,575,1173,165});out=root/'outputs/04-poke/qa-v19-region-attribution';out.mkdir(exist_ok=True);source=root/'references/04-poke/source.mp4';candidate=root/'outputs/04-poke/gsap.mp4';ri=c.probe(source);ci=c.probe(candidate);times=[n/s['fps']for n in frames];rf=c.batch_native_frames(source,times,ri,None,out/'decoded-source');cf=c.batch_native_frames(candidate,times,ci,None,out/'decoded-candidate');rows=[]
def rect(box):
 im=Image.new('L',(1440,1080),0);ImageDraw.Draw(im).rectangle(tuple(box),fill=255);return np.array(im)>0

def bbox(g,n,x,y,w,h):
 t=n/s['fps'];sx,sy=[at(g,k,t)for k in['scaleX','scaleY']];gx,gy=[at(g,k,t)for k in['x','y']];ox,oy=[at(g,k,t)for k in['originX','originY']];return[gx+ox+(x-ox)*sx,gy+oy+(y-oy)*sy,gx+ox+(x+w-ox)*sx,gy+oy+(y+h-oy)*sy]
def rounded(box,r):
 im=Image.new('L',(1440,1080),0);ImageDraw.Draw(im).rounded_rectangle(tuple(box),radius=r,fill=255);return np.array(im)>0
for n in frames:
 a=np.array(Image.open(rf[n]).convert('RGB')).astype(np.int16);b=np.array(Image.open(cf[n]).convert('RGB')).astype(np.int16);d=abs(a-b).mean(2);used=np.zeros(d.shape,bool);regions=[]
 def add(name,m):
  nonlocal_dummy=None
  m=m&~used;used[:]|=m;regions.append(dict(name=name,pixels=int(m.sum()),mae=float(d[m].mean())if m.any() else 0,absolute_error_share=float(d[m].sum()/d.sum()),whole_frame_mae_contribution=float(d[m].sum()/d.size)))
 if n==165:
  letters=((a.max(2)<180)|(b.max(2)<180))&rect([150,460,1290,625]);letters=ndimage.binary_dilation(letters,iterations=3);add('Sarah sentence and underline ink edge bands',letters);add('Gray incoming pill, tail and camera displacement',rect([100,400,1340,710]));crop=[100,400,1340,710]
 elif n==575:
  add('SharedLocation map artwork',rect([596,0,1170,488]));add('SharedLocation footer UI and bubble edge',rect([596,488,1170,648]));y=at(scene['p0255'],'y',n/s['fps']);add('Restaurant sheet heading and top controls',rect([238,y-12,1202,y+175]));add('Restaurant section, list and visible photo',rect([238,y+175,1202,1080]));add('Sheet shadow and nearby surface',rect([170,540,1270,1080]));crop=[580,455,1190,900]
 elif n==108:
  add('Header controls and material',rect([0,0,1440,200]));add('Left portrait and its caption',rect([0,200,370,760]));add('Central logo and its caption',rect([450,200,1020,760]));add('Right portrait and its caption',rect([1080,200,1440,760]));add('Other favorites area',rect([0,200,1440,760]));add('Inbox text, avatars and separators',rect([0,760,1440,1080]));crop=[0,180,1440,780]
 elif 710<=n<800:
  g=scene['p0292'];t=n/s['fps'];sc=at(g,'scaleX',t);outer=bbox(g,n,0,0,1000,2160);inner=bbox(g,n,36,36,928,2088);outer=[outer[0]-18,outer[1]-18,outer[2]+18,outer[3]+18];hardware=rounded(outer,158*sc+18)&~rounded([inner[0]+4,inner[1]+4,inner[2]-4,inner[3]-4],max(0,128*sc-4));island=bbox(g,n,358,68,284,82);hardware|=rounded([island[0]-4,island[1]-4,island[2]+4,island[3]+4],41*sc+4);add('Physical frame, side shadow and camera island',hardware);m=scene['p0300'];art=bbox(m,n,0,0,390,295);foot=bbox(m,n,0,295,390,93);add('Map artwork, including header-covered portion',rect(art));add('Map footer text and gray UI',rect(foot));screen=rounded(inner,128*sc);add('Header controls, selected preview and glass surface',screen&rect([0,0,1440,497]));add('Other conversation, composer and keyboard UI',screen);crop=[400,0,1100,500]
 elif n==1173:
  tile=np.zeros(d.shape,bool);borders=np.zeros(d.shape,bool)
  for g in s['layers']:
   if g.get('start')!=39.005633333333336 or not g.get('children'):continue
   if g['children'][0]['type']!='image':continue
   t=n/s['fps'];gx,gy,scale=[at(g,k,t)for k in ['x','y','scaleX']];box=[gx,gy,gx+225*scale,gy+225*scale];r=54*scale;inside=rounded(box,r);outside=rounded([box[0]-8,box[1]-8,box[2]+8,box[3]+8],r+8);inner=rounded([box[0]+8,box[1]+8,box[2]-8,box[3]-8],r-8);tile|=inside;borders|=outside&~inner
  add('Outer tile boundaries and nearby cast edges',borders)
  sharp=np.zeros(d.shape,bool)
  for im in [a,b]:
   sharp[:,1:]|=(abs(im[:,1:]-im[:,:-1]).max(2)>12);sharp[1:]|=(abs(im[1:]-im[:-1]).max(2)>12)
  sharp=ndimage.binary_dilation(sharp,iterations=2);add('Brand glyph/artwork edge bands inside tiles',sharp&tile);add('Flat/interior tile artwork away from those edges',tile);crop=[160,0,1120,1080]
 else:raise ValueError(n)
 add('Remaining canvas/background',~used);x,y,z,w=crop;aa=Image.fromarray(a.astype('uint8')).crop(crop);bb=Image.fromarray(b.astype('uint8')).crop(crop);sheet=Image.new('RGB',(aa.width*2,aa.height+22),'white');sheet.paste(aa,(0,22));sheet.paste(bb,(aa.width,22));ImageDraw.Draw(sheet).text((2,2),f'Native {n}: original | PC709 V19 candidate',fill='black');sheet.save(out/f'native-{n}-pair.png');rows.append(dict(frame=n,mae=float(d.mean()),regions=regions,native_pair=f'native-{n}-pair.png'))
result=dict(scene_sha256='bf46102ecdc578cdadac244ba85dec7e5ab19fe07b80277a2fdcdb4c2b191df1',reference_sha256=ri['sha256'],candidate_sha256=ci['sha256'],largest_source_peak=worst,method='Exact batch-native decode of stable PC709 files. Disjoint candidate-geometry regions with boundary halos; shares sum to1. Region location is evidence, not an automatic proof of physical cause.575and1173have no phone hardware. Grid regions separate tile-boundary halos, brand-ink edge bands and flat interior; location is not a sole cause claim.',frames=rows);(out/'attribution.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
