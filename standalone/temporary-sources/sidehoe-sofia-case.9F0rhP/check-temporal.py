"""Compare consecutive decoded frame changes through the suggestion and tile paths."""
from pathlib import Path
import csv,subprocess,sys
import numpy as np

source,old,new,out=map(Path,sys.argv[1:])
passages=(
    ('Sofia handset and push',318,343,(220,0,1780,2000)),
    ('tile overlap one',503,507,(278,498,1756,1598)),
    ('tile overlap two',513,517,(278,498,1756,1598)),
    ('tile overlap three',520,527,(278,498,1756,1598)),
)
scores=[]
for passage,start,end,(x0,y0,x1,y1) in passages:
    w,h=x1-x0,y1-y0
    size=w*h*3
    filter_spec=f'select=between(n\\,{start}\\,{end}),format=rgb24,crop={w}:{h}:{x0}:{y0}'
    streams=[subprocess.Popen(['ffmpeg','-nostdin','-v','error','-i',str(asset),'-an','-vf',
        filter_spec,'-fps_mode','passthrough','-threads:v','1','-c:v','rawvideo',
        '-f','rawvideo','pipe:1'], stdout=subprocess.PIPE) for asset in (source,old,new)]
    before=None
    try:
        for frame in range(start,end+1):
            current=[]
            for stream in streams:
                raw=stream.stdout.read(size)
                if len(raw)!=size:
                    raise RuntimeError(f'Incomplete crop for {passage} frame {frame}')
                current.append(np.frombuffer(raw,np.uint8).astype(np.int16))
            if before:
                expected=current[0]-before[0]
                errors=[float(np.abs(p-q-expected).mean()) for p,q in zip(current[1:],before[1:],strict=True)]
                scores.append([passage,frame-1,frame,*[round(z,6) for z in errors]])
            before=current
        for stream in streams:
            assert not stream.stdout.read(1) and stream.wait()==0
    finally:
        for stream in streams:
            if stream.poll() is None:
                stream.kill()
                stream.wait()
with out.open('w',newline='') as f:
    writer=csv.writer(f)
    writer.writerow(['passage','previous_frame','frame','previous_temporal_rgb_error','revised_temporal_rgb_error'])
    writer.writerows(scores)
