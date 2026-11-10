from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,copy
REF=Path(__file__).resolve().parent
ROOT=REF.parents[1]
def apply_alpha(scene):
 s=copy.deepcopy(scene);n=next(n for n in s['layers'] if n['id']=='early-wall-native-v7-sms-000');n['src']=str((REF/'assets/v10-alpha/sms-000-restored.png').resolve());n['alphaRestoration']='Original RGB retained;1268 genuine row-interior glyph pixels restored to opaque alpha. Native camera/lifecycle unchanged.';return s
if __name__=='__main__':
 base=ROOT/'outputs/01-photonhq/final-v9/scene.json';s=json.load(open(base));node=next(n for n in s['layers'] if n['id']=='early-wall-native-v7-sms-000');old=base.parent/node['src'];a=np.array(Image.open(old).convert('RGBA'));b=a.copy()
 for row in range(a.shape[0]):
  xs=np.where(a[row,:,3]>200)[0]
  if len(xs)>1:
   inner=np.arange(xs[0],xs[-1]+1);b[row,inner[a[row,inner,3]<200],3]=255
 assert np.array_equal(a[:,:,:3],b[:,:,:3]);count=int(np.sum(a[:,:,3]!=b[:,:,3]));assert count==1268,count
 out=REF/'assets/v10-alpha/sms-000-restored.png';out.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(b).save(out)
 def normalize(n):
  if n.get('src') and not n['src'].startswith(('/','data:','http:','https:')):n['src']=str((base.parent/n['src']).resolve())
  for c in n.get('children',[]):normalize(c)
 for n in s['layers']:normalize(n)
 for f in s.get('fonts',[]):f['src']=str((base.parent/f['src']).resolve())
 fixed=apply_alpha(s);fixed['source']['notes']+=' V10 restores1268 genuine dark glyph alpha pixels on one existing gray SMS bitmap during260–272; original RGB, geometry, typography material and all native cameras are retained. No new reference texture or whole-frame layer.'
 candidate=ROOT/'outputs/01-photonhq/root-alpha-v10-candidate.json';candidate.write_text(json.dumps(fixed,indent=2)+'\n');meta=dict(originalAsset=str(old),originalSHA256=hashlib.sha256(old.read_bytes()).hexdigest(),restoredAsset=str(out),restoredSHA256=hashlib.sha256(out.read_bytes()).hexdigest(),changedAlphaPixels=count,RGBBytesUnchanged=True,scope=[[260,272]],candidate=str(candidate));(REF/'v10-alpha-measure/provenance.json').write_text(json.dumps(meta,indent=2));print(candidate)
