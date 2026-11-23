"""Compare the full and limited range encodes at matched frames in each passage."""
import json,sys,subprocess
from pathlib import Path
import numpy as np
files=[Path(x) for x in sys.argv[1:4]]
frames=range(0,778,13)
selector='not(mod(n\\,13))'
streams=[subprocess.Popen(['ffmpeg','-nostdin','-v','error','-i',str(path),
    '-an','-vf',f'select={selector},format=rgb24','-fps_mode','passthrough',
    '-threads:v','1','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE) for path in files]
size=2000*2000*3
rows=[]
for f in frames:
    pictures=[]
    for stream in streams:
        block=stream.stdout.read(size)
        assert len(block)==size,(f,len(block))
        pictures.append(np.frombuffer(block,np.uint8).astype(np.int16))
    rows.append([f,*[float(np.abs(pictures[0]-pic).mean()) for pic in pictures[1:]]])
for stream in streams:
    assert not stream.stdout.read(1) and stream.wait()==0
rank=np.asarray(rows)
print('average full limited',np.mean(rank[:,1:],axis=0).tolist())
print('limited range wins',sum(rank[:,2]<rank[:,1]),'of',len(rows))
Path(sys.argv[4]).write_text(json.dumps(rows,indent=2)+'\n')
