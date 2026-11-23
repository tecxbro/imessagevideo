"""Compare consecutive native frame differences around all three revised passages."""
from pathlib import Path
import csv
import subprocess
import sys
from tempfile import TemporaryDirectory
import numpy as np

source,old,new,out=map(Path,sys.argv[1:])
passages=(
    ('casing hold and exit',138,162,(64,755,1946,1550)),
    ('follow-up withdrawal',689,696,(170,1020,1830,2000)),
    ('closing badge entrance and join',700,718,(690,650,1310,1315)),
    ('closing badge hold into fade',762,777,(690,650,1310,1315)),
)
with TemporaryDirectory(prefix='sidehoe-motion-check-') as tmp:
    work=Path(tmp)
    output=[]
    for name,start,end,(x0,y0,x1,y1) in passages:
        width,height=x1-x0,y1-y0
        def decoded(path,f):
            ffmpeg=['ffmpeg','-nostdin','-v','error','-i',str(path),'-an',
                    '-vf',f"select=between(n\\,{start}\\,{end}),format=rgb24,crop={width}:{height}:{x0}:{y0}",
                    '-fps_mode','passthrough','-c:v','rawvideo','-f','rawvideo',str(f)]
            subprocess.run(ffmpeg,check=True)
            return np.memmap(f,mode='r',dtype=np.uint8,shape=(end-start+1,height,width,3))
        media=[decoded(path,work/f'{start}-{i}.rgb') for i,path in enumerate((source,old,new))]
        for offset in range(1,end-start+1):
            ref_step=media[0][offset].astype(np.int16)-media[0][offset-1].astype(np.int16)
            differences=[]
            for x in media[1:]:
                step=x[offset].astype(np.int16)-x[offset-1].astype(np.int16)
                differences.append(float(np.abs(ref_step-step).mean()))
            output.append([name,start+offset-1,start+offset,*[round(v,5) for v in differences]])
    with out.open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['passage','previous_frame','frame','previous_temporal_rgb_error','revised_temporal_rgb_error'])
        writer.writerows(output)
