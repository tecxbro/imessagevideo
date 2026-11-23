from pathlib import Path
import numpy as np,subprocess,sys
base=Path(__file__).parent
orig='/Users/darshan/Downloads/sidehoe.mp4'
published='sidehoe-skill-trial/detail-review/candidate/sidehoe.mp4'
probe=sys.argv[1] if len(sys.argv)>1 else str(base/'seam-probe.mp4')
def run(path,ss):
 args=['ffmpeg','-hide_banner','-v','error','-threads','4','-ss',str(ss),'-i',path,
       '-vf','scale=64:36:flags=area,format=gray','-frames:v','31','-f','rawvideo','-']
 samples=np.frombuffer(subprocess.check_output(args),dtype=np.uint8).reshape(-1,36,64).astype(float)
 return np.r_[0,np.abs(np.diff(samples,axis=0)).mean(axis=(1,2))]
reference,prior,revised=[run(v,start) for v,start in [(orig,15.52),(published,15.52),(probe,0 if len(sys.argv)==1 else 15.52)]]
for name,v in [('source',reference),('prior',prior),('revised',revised)]:
 local=sorted([*v[(401-388)-12:401-388],*v[402-388:414-388]])
 d=v[401-388]
 print(name,'change',round(d,4),'median',round(local[12],4),'ratio',round(d/local[12],4),
       'fourfold margin',round(d-4*local[12],4),
       'middle frames',sorted([(round(v[i],4),i+388) for i in range(1,26) if i!=401-388])[10:15])
