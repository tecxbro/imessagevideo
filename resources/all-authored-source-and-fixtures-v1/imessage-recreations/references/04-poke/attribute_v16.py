"""Hash-bound disjoint native-region attribution of final source peaks."""
from pathlib import Path
import importlib.util,json,hashlib,sys,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;spec=importlib.util.spec_from_file_location('comparison',root/'verification/compare.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);s=json.loads((root/'outputs/04-poke/final-v16/scene.json').read_text());scene={g['id']:g for g in s['layers']};scan=json.loads((root/'verification/timeline-scans/04-poke-v16/scan.json').read_text());worst=max(scan['peaks'],key=lambda v:v['mae'])['candidate_frame'];frames=sorted({worst,758,108,575});out=root/'outputs/04-poke/qa-v16-region-attribution';out.mkdir(exist_ok=True);source=root/'references/04-poke/source.mp4';candidate=root/'outputs/04-poke/gsap.mp4';ri=c.probe(source);ci=c.probe(candidate);times=[n/s['fps']for n in frames];rf=c.batch_native_frames(source,times,ri,None,out/'decoded-source');cf=c.batch_native_frames(candidate,times,ci,None,out/'decoded-candidate');rows=[]
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
 if n==575:
  add('SharedLocation map artwork',rect([596,0,1170,488]));add('SharedLocation footer UI and bubble edge',rect([596,488,1170,648]));y=at(scene['p0255'],'y',n/s['fps']);add('Restaurant sheet heading and top controls',rect([238,y-12,1202,y+175]));add('Restaurant section, list and visible photo',rect([238,y+175,1202,1080]));add('Sheet shadow and nearby surface',rect([170,540,1270,1080]));crop=[580,455,1190,900]
 elif n==108:
  add('Header controls and material',rect([0,0,1440,200]));add('Left portrait and its caption',rect([0,200,370,760]));add('Central logo and its caption',rect([450,200,1020,760]));add('Right portrait and its caption',rect([1080,200,1440,760]));add('Other favorites area',rect([0,200,1440,760]));add('Inbox text, avatars and separators',rect([0,760,1440,1080]));crop=[0,180,1440,780]
 elif n==758:
  g=scene['p0292'];t=n/s['fps'];sc=at(g,'scaleX',t);outer=bbox(g,n,0,0,1000,2160);inner=bbox(g,n,36,36,928,2088);outer=[outer[0]-18,outer[1]-18,outer[2]+18,outer[3]+18];hardware=rounded(outer,158*sc+18)&~rounded([inner[0]+4,inner[1]+4,inner[2]-4,inner[3]-4],max(0,128*sc-4));island=bbox(g,n,358,68,284,82);hardware|=rounded([island[0]-4,island[1]-4,island[2]+4,island[3]+4],41*sc+4);add('Physical frame, side shadow and camera island',hardware);m=scene['p0300'];art=bbox(m,n,0,0,390,295);foot=bbox(m,n,0,295,390,93);add('Map artwork, including header-covered portion',rect(art));add('Map footer text and gray UI',rect(foot));screen=rounded(inner,128*sc);add('Header controls, selected preview and glass surface',screen&rect([0,0,1440,497]));add('Other conversation, composer and keyboard UI',screen);crop=[400,0,1100,500]
 else:raise ValueError(n)
 add('Remaining canvas/background',~used);x,y,z,w=crop;aa=Image.fromarray(a.astype('uint8')).crop(crop);bb=Image.fromarray(b.astype('uint8')).crop(crop);sheet=Image.new('RGB',(aa.width*2,aa.height+22),'white');sheet.paste(aa,(0,22));sheet.paste(bb,(aa.width,22));ImageDraw.Draw(sheet).text((2,2),f'Native {n}: original | PC709 V16 candidate',fill='black');sheet.save(out/f'native-{n}-pair.png');rows.append(dict(frame=n,mae=float(d.mean()),regions=regions,native_pair=f'native-{n}-pair.png'))
result=dict(scene_sha256='57ed887caf7357a79e1f18c00b06934f2eeda864e555c739f1ab8965cc1b5cd9',reference_sha256=ri['sha256'],candidate_sha256=ci['sha256'],largest_source_peak=worst,method='Exact batch-native decode of stable PC709 files. Disjoint candidate-geometry regions with boundary halos; shares sum to1. Region location is evidence, not an automatic proof of physical cause.575has no phone hardware.',frames=rows);(out/'attribution.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
