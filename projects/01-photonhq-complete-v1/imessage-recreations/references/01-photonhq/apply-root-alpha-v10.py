from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,copy
REF=Path(__file__).resolve().parent
ROOT=REF.parents[1]
def apply_alpha(scene):
 s=copy.deepcopy(scene);n=next(n for n in s['layers'] if n['id']=='early-wall-native-v7-sms-000');clone=copy.deepcopy(n);assert n['keyframes']['opacity'][-1]['t']==260/30;n['keyframes']['opacity'][-1]['t']=265/30;clone.update(id='root-alpha-v10-sms000-restored',src=str((REF/'assets/v10-alpha/sms-000-restored.png').resolve()),start=260/30,end=265/30,opacity=1);clone['keyframes'].pop('opacity');clone['alphaRestoration']='Original RGB retained;1268 genuine row-interior glyph pixels restored. Camera unchanged; only the five source-improving visible states.';s['layers'].insert(s['layers'].index(n)+1,clone)
 n=next(n for n in s['layers'] if n['id']=='early-wall-native-v7-sms-021');n['src']=str((REF/'assets/v10-alpha/sms-021-restored.png').resolve());n['alphaRestoration']='Original RGB retained;369 genuine row-interior glyph pixels restored. Camera/lifecycle unchanged.'
 return s
if __name__=='__main__':
 base=ROOT/'outputs/01-photonhq/final-v9/scene.json';s=json.load(open(base));repairs=[]
 for suffix,expected in [('000',1268),('021',369)]:
  node=next(n for n in s['layers'] if n['id']=='early-wall-native-v7-sms-'+suffix);old=base.parent/node['src'];a=np.array(Image.open(old).convert('RGBA'));b=a.copy()
  for row in range(a.shape[0]):
   xs=np.where(a[row,:,3]>200)[0]
   if len(xs)>1:
    inner=np.arange(xs[0],xs[-1]+1);b[row,inner[a[row,inner,3]<200],3]=255
  assert np.array_equal(a[:,:,:3],b[:,:,:3]);count=int(np.sum(a[:,:,3]!=b[:,:,3]));assert count==expected,count
  out=REF/f'assets/v10-alpha/sms-{suffix}-restored.png';out.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(b).save(out);repairs.append(dict(id=node['id'],originalAsset=str(old),originalSHA256=hashlib.sha256(old.read_bytes()).hexdigest(),restoredAsset=str(out),restoredSHA256=hashlib.sha256(out.read_bytes()).hexdigest(),changedAlphaPixels=count,RGBBytesUnchanged=True))
 def normalize(n):
  if n.get('src') and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((base.parent/n['src']).resolve())
  for c in n.get('children',[]):normalize(c)
 for n in s['layers']:normalize(n)
 for f in s.get('fonts',[]):f['src']=str((base.parent/f['src']).resolve())
 fixed=apply_alpha(s);fixed['source']['notes']+=' V10 restores1637 genuine dark glyph alpha pixels on two existing gray SMS bitmaps:000 only260–264 and021 during262–270. Original RGB, geometry and all native cameras remain unchanged. Continuous000 restoration at272 was rejected after a tiny source regression. No new reference texture or whole-frame layer.'
 candidate=ROOT/'outputs/01-photonhq/root-alpha-v10-candidate.json';candidate.write_text(json.dumps(fixed,indent=2)+'\n');meta=dict(repairs=repairs,scope=[[260,270]],candidate=str(candidate));(REF/'v10-alpha-measure/provenance.json').write_text(json.dumps(meta,indent=2));print(candidate)
