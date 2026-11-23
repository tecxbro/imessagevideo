import csv,subprocess,sys
import numpy as np
w=500
p=subprocess.Popen(['ffmpeg','-v','error','-i','/Users/darshan/Downloads/sidehoe.mp4','-vf',f'scale={w}:{w}','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
def bounds(mask,x0=0,y0=0):
    y,x=np.where(mask)
    return [int(4*(v+o)) for v,o in ((x.min(),x0),(y.min(),y0),(x.max()+1,x0),(y.max()+1,y0))] if len(x) else []
def masks(reg,which):
    r,g,b=reg.astype('int16').transpose(2,0,1)
    return {'cyan':(b-r>110)&(g-r>94)&(r<65),
    'dark':(r<55)&(g<55)&(b<55),
    'red':(r>170)&(r-g>110)&(r-b>80),
    'purple':(b-r>40)&(r-g>50)&(r<130),
    'cal':(b-r>100)&(g-r>80)&(r<90)}[which]
def find(arr,kind,box):
    x,y,xx,yy=[i//4 for i in box]
    return bounds(masks(arr[y:yy,x:xx],kind),x,y)
rows=[]
for f in range(778):
    a=np.frombuffer(p.stdout.read(w*w*3),np.uint8).reshape(w,w,3)
    row={'frame':f,'pts':f*2400,'seconds':f/25}
    if 400<=f<=477:
        row['cal_date']=find(a,'red',(1150,100,1750,1950))
        row['cal_cyan_edge']=find(a,'cal',(220,560,600,1420))
        row['cal_purple_edge']=find(a,'purple',(220,560,600,1380))
    if 336<=f<=402:
        row['sofia_cyan']=find(a,'cyan',(600,455,1900,1550))
    if f in {18,80,103,105,113,124,134,140,147,159,215,224,251,261,275,290,300,312,322,327,335,339,349,355,360,380,390,395,500,530,540,555,565,580,590,610,624,632,645,659,665,670,675,684,693,696,705,713,725,741,755,765,766,767,768,769,770,771,772,773,774,775,776,777} or 660<=f<=696:
        row['dark_edges']=find(a,'dark',(0,0,2000,2000))
    if f>=755:
        row['mean_rgb_luma']=round(a.mean(),3)
        row['top_left_rgb']=a[40,40].tolist()
        row['bottom_right_rgb']=a[455,455].tolist()
    rows.append(row)
p.wait()
keys=list(dict.fromkeys(k for r in rows for k in r))
out=csv.DictWriter(open(sys.argv[1],'w'),keys)
out.writeheader()
out.writerows(rows)
