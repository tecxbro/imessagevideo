"""Measure the gallery fade on an isolated upper-right phone-art ROI."""
from pathlib import Path
import json,subprocess,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];REF=Path(__file__).resolve().parent
scene=json.loads((ROOT/'outputs/05-linq/root-late-candidate-v6.json').read_text());group=next(l for l in scene['layers'] if l['id']=='broad-v5-group-72')
assets={c['id']:Image.open(c['src']).convert('RGBA') for c in group['children']}
def sample(keys,t):
 if t<=keys[0]['t']:return keys[0]['value']
 for a,b in zip(keys,keys[1:]):
  if t<=b['t']:return a['value']+(b['value']-a['value'])*(t-a['t'])/(b['t']-a['t'])
 return keys[-1]['value']
first,last=1258,1281;cmd=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(REF/'source.mp4'),'-vf',f"select='between(n,{first},{last})'",'-fps_mode','passthrough','-threads','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'];proc=subprocess.Popen(cmd,stdout=subprocess.PIPE);records=[]
for n in range(first,last+1):
 data=proc.stdout.read(960*720*3)
 if len(data)!=960*720*3:raise ValueError('Incomplete native fade decode')
 source=np.frombuffer(data,np.uint8).reshape(720,960,3).astype(float);canvas=Image.new('RGBA',(960,720),'white')
 for c in group['children']:
  y=sample(c['keyframes']['y'],n/30);art=assets[c['id']]
  canvas.alpha_composite(art,(round(c['x']),round(y)))
 predicted=np.array(canvas.convert('RGB'),float);roi=(slice(100,250),slice(700,900));delta=predicted[roi]-255;reference=source[roi]-255
 alpha=float(np.clip((reference*delta).sum()/max((delta*delta).sum(),1),0,1))
 if alpha>.995:alpha=1.
 records.append({'frame':n,'t':n/30,'value':alpha})
proc.stdout.close();proc.wait();(REF/'assets/root-late/gallery-opacity.json').write_text(json.dumps(records,indent=2));print(json.dumps(records))
