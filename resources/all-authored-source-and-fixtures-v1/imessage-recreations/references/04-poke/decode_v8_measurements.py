"""Decode exact native source-frame intervals selected by the every-frame audit."""
from pathlib import Path
import json,subprocess
p=Path(__file__).parent;out=p/'measurements-v8/decoded';out.mkdir(parents=True,exist_ok=True)
ranges=[(98,131),(250,264),(435,492),(575,596),(660,669),(695,829),(1125,1218)]
frames=sorted(set(n for a,b in ranges for n in range(a,b+1)))
if all((out/f'{n:06}.png').exists()for n in frames):print('Exact native intervals already complete');raise SystemExit(0)
temp=p/'measurements-v8/decode-temporary';temp.mkdir(exist_ok=True)
expression="select='"+'+'.join(f'between(n,{a},{b})'for a,b in ranges)+"'"
command=['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-i',str(p/'source.mp4'),'-vf',expression,'-fps_mode','passthrough','-frames:v',str(len(frames)),'-threads','1',str(temp/'%06d.png')]
subprocess.run(command,check=True);files=sorted(temp.glob('*.png'))
if len(files)!=len(frames):raise RuntimeError(f'Expected{len(frames)}frames, decoded{len(files)}')
for n,file in zip(frames,files):file.replace(out/f'{n:06}.png')
temp.rmdir();(p/'measurements-v8/decode-ledger.json').write_text(json.dumps({'source':'source.mp4','source_timebase':'1/3000000','frame_pts_stride':100100,'cadence':'30000/1001','ranges_inclusive':ranges,'frames':frames,'selection':expression,'command':command,'count':len(frames)},indent=2));print('Decoded',len(frames),'exact native frames')
