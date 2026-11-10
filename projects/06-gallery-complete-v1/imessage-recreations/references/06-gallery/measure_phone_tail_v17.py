from pathlib import Path
import json,subprocess,numpy as np
D=Path(__file__).resolve().parent
p=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-ss','27.6','-i',str(D/'source.mp4'),'-t',str(12/30),'-vf','crop=300:1080:800:0','-f','rawvideo','-pix_fmt','rgb24','-threads','1','pipe:1'],stdout=subprocess.PIPE);out=[]
for f in range(828,840):
 raw=p.stdout.read(300*1080*3)
 if len(raw)!=300*1080*3:raise RuntimeError('Short tail decode')
 a=np.frombuffer(raw,np.uint8).reshape(1080,300,3).astype(int);m=(np.max(a,axis=2)<100)&(np.max(a,axis=2)-np.min(a,axis=2)<12);pos=np.arange(300)[None,:];last=np.maximum.accumulate(np.where(~m,pos,-1),axis=1);runs=(pos-last).max(axis=1);yy=np.where(runs>150)[0];out.append({'frame':f,'center_top_y':int(yy.min()) if len(yy) else None})
p.wait();(D/'native-birthday-tail-v17.json').write_text(json.dumps(out,indent=2));print(out)
