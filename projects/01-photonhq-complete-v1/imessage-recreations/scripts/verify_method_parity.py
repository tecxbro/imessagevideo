#!/usr/bin/env python3
"""Compare every decoded picture frame of current methods against measured GSAP.
This is renderer coverage evidence; source fidelity requires the separate native
source scan. High parity alone cannot prove either render matches the reference.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
METHODS=('remotion','html','pillow','motion-canvas')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,default=ROOT/'delivery-state.json');p.add_argument('--only',nargs='*');p.add_argument('--out',type=Path,default=ROOT/'verification/method-parity');a=p.parse_args();state=json.loads(a.state.read_text());a.out.mkdir(parents=True,exist_ok=True);records=[];tool_hash=sha(Path(__file__))
 for identity,entry in state['scenes'].items():
  if a.only and identity not in a.only:continue
  scene=ROOT/entry['scene'];s=json.loads(scene.read_text());digest=sha(scene);count=round(s['fps']*s['duration']);reference=ROOT/'outputs'/identity/'gsap.mp4';refmeta=json.loads(Path(str(reference)+'.render.json').read_text())
  if refmeta.get('sceneSHA256',refmeta.get('sceneSha256'))!=digest:raise ValueError(identity+' GSAP scene is stale')
  for method in METHODS:
   candidate=reference.with_name(method+'.mp4');meta=json.loads(Path(str(candidate)+'.render.json').read_text())
   if meta.get('sceneSHA256',meta.get('sceneSha256'))!=digest:raise ValueError(identity+'/'+method+' scene is stale')
   folder=a.out/identity;folder.mkdir(exist_ok=True);report_path=folder/(method+'.json');reference_hash=sha(reference);candidate_hash=sha(candidate)
   if report_path.exists():
    current=json.loads(report_path.read_text())
    if current.get('toolSHA256')==tool_hash and current.get('sceneSHA256')==digest and current.get('gsapSHA256')==reference_hash and current.get('candidateSHA256')==candidate_hash and current.get('frames')==count:
     records.append(current);print(json.dumps(dict(reference=identity,method=method,frames=count,reusedCurrentHashBoundComparison=True)),flush=True);continue
   stats=folder/(method+'-ssim.txt');graph=f'[0:v]setpts=PTS-STARTPTS,format=yuv420p[a];[1:v]setpts=PTS-STARTPTS,format=yuv420p[b];[a][b]ssim=stats_file={stats.resolve()}:shortest=1'
   command=['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-filter_complex_threads','1','-i',str(reference),'-threads','1','-i',str(candidate),'-filter_complex',graph,'-an','-f','null','-'];subprocess.run(command,check=True)
   rows=[]
   for line in stats.read_text().splitlines():
    match=re.search(r'n:(\d+).*?All:([\d.]+)',line)
    if not match:raise ValueError('Unparsed SSIM row '+line)
    rows.append((int(match[1])-1,float(match[2])))
   if len(rows)!=count or [r[0] for r in rows]!=list(range(count)):raise ValueError(identity+'/'+method+' incomplete decoded comparison')
   values=np.array([r[1] for r in rows]);minimum=float(values.min());mean=float(values.mean());percentile1=float(np.percentile(values,1));reasons=[]
   if minimum<.95:reasons.append('minimum SSIM below .95')
   if mean<.985:reasons.append('mean SSIM below .985')
   if minimum<percentile1-.01:reasons.append('isolated minimum more than .01 below first percentile')
   record=dict(reference=identity,method=method,toolSHA256=tool_hash,sceneSHA256=digest,gsapSHA256=reference_hash,candidateSHA256=candidate_hash,frames=count,meanSSIM=mean,minimumSSIM=minimum,percentile1SSIM=percentile1,peaks=[dict(frame=n,time=n/s['fps'],ssim=v) for n,v in sorted(rows,key=lambda r:r[1])[:12]],requiresDiagnosis=bool(reasons),diagnosisReasons=reasons,notice='Every aligned decoded picture frame compared to GSAP. Absolute and relative outlier flags are review heuristics, not a fidelity certificate. This does not establish source fidelity; use the corresponding all-frame source scan and optical/foreground review.')
   report_path.write_text(json.dumps(record,indent=2));records.append(record);print(json.dumps({k:record[k] for k in ['reference','method','frames','meanSSIM','minimumSSIM','requiresDiagnosis']}),flush=True)
 (a.out/'report.json').write_text(json.dumps(dict(comparisons=records,completeFrameComparisons=sum(r['frames'] for r in records)),indent=2))
if __name__=='__main__':main()
