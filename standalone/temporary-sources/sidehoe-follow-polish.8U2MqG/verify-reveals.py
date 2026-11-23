from pathlib import Path
import csv,sys,subprocess
import numpy as np

source,candidate,out=map(Path,sys.argv[1:])
frames=(646,651)
regions={'no':(730,977,805,1074),'yes':(857,978,1032,1072)}
left,top,width,height=700,940,350,150
values=[]
def decode(path):
    output=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(path),
        '-an','-vf',f"select=between(n\\,{frames[0]}\\,{frames[1]}),crop={width}:{height}:{left}:{top},format=rgb24",
        '-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
    return np.frombuffer(output,dtype=np.uint8).reshape(frames[1]-frames[0]+1,height,width,3)
bounds={}
for name,movie in [('Source',source),('Revised',candidate)]:
    detections={}
    for f,img in enumerate(decode(movie),frames[0]):
        for action,(l,t,r,b) in regions.items():
            a=img[t-top:b-top,l-left:r-left].astype(np.int16)
            R,G,B=a.transpose(2,0,1)
            selected=((R-B>28)&(G-B>16)&(R>152)) if action=='no' else (
                (B-G>=16)&(B-R>=8)&(B>=226)&(R>167))
            count=int(np.count_nonzero(selected))
            values.append([name,f,action,count])
            if count>=15:
                detections.setdefault(action,f)
        print(values[-2:],flush=True)
    bounds[name]=detections
assert bounds=={'Source':{'no':648,'yes':650},'Revised':{'no':648,'yes':650}},bounds
with out.open('w',newline='') as h:
    writer=csv.writer(h)
    writer.writerow(['version','frame','control','detected pixels'])
    writer.writerows(values)
print(bounds)
