from pathlib import Path
import subprocess
import csv
import json
import sys
import numpy as np
from PIL import Image, ImageDraw

base=Path('sidehoe-skill-trial/repair')
output=base/'reviewer-audit'
reference=Path('/Users/darshan/Downloads/sidehoe.mp4')
candidate=base/'exports/sidehoe.mp4'
sys.path.insert(0,'sidehoe-recreation/tools')
from check_follow_contact import components

proofs=[
 ('02-inbox-hold',22,(295,365,1690,1595)),
 ('03-inbox-scroll',56,(270,0,1680,1580)),
 ('07-portrait-cluster',242,(90,320,1760,1800)),
 ('11-suggestion-controls',352,(0,150,2000,1930)),
 ('12-isolated-suggestion',394,(660,475,1890,1480)),
 ('13-calendar-entry',420,(260,480,1770,1250)),
 ('14-violet-drag',435,(145,240,1880,1050)),
 ('15-cyan-drag',460,(140,260,1880,1250)),
 ('18-app-exit',616,(390,935,1610,1800)),
 ('20-follow-approach',673,(520,975,1220,1360)),
 ('21-yes-withdrawal',693,(160,100,1820,1900)),
 ('23-closing-copy',765,(410,625,1580,1850)),
 ('24-closing-fade',771,(500,650,1500,1800)),
]
sofia=list(range(319,336))
follow_shell=list(range(635,650))
follow=list(range(670,696))
send=list(range(385,398))
frames=sorted(set([f for _,f,_ in proofs]+sofia+follow_shell+follow+send))

def find_pointer(tile, x0, y0, min_area):
    rgb=tile.max(2)
    options=[]
    for shape in components(rgb<70):
        ymin,xmin=shape.min(0); ymax,xmax=shape.max(0)
        w=xmax-xmin+1; h=ymax-ymin+1
        if len(shape)>min_area and 16<w<155 and 23<h<205 and 0<xmin and xmax<tile.shape[1]-1 and 0<ymin and ymax<tile.shape[0]-1:
            options.append(shape)
    if not options:
        return None
    points=max(options,key=len)
    y,x=points.mean(0)+[y0,x0]
    ty,tx=points[np.argmin(points[:,0]+.35*points[:,1])]+[y0,x0]
    return (round(float(x),2),round(float(y),2),int(tx),int(ty),int(len(points)),
            int(np.ptp(points[:,1])+1),int(np.ptp(points[:,0])+1))

def decode(movie):
    expression='select='+ '+'.join(f'eq(n\\,{f})' for f in frames)
    command=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-xerror','-threads','2','-noautorotate',
            '-apply_cropping','codec','-i',str(movie),'-map','0:V:0','-an','-sn','-dn','-filter_threads','2',
            '-vf',expression,'-frames:v',str(len(frames)),'-fps_mode','passthrough',
            '-c:v','rawvideo','-threads:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
    details={}; track={'sofia-rim':{},'follow-rim':{},'follow-pointer':{},'send-pointer':{}}
    validation={}
    with subprocess.Popen(command,stdout=subprocess.PIPE) as process:
        for f in frames:
            raw=process.stdout.read(2000*2000*3)
            if len(raw)!=2000*2000*3:
                raise RuntimeError(f'{movie} returned an incomplete frame at index {f}')
            full=np.frombuffer(raw,dtype=np.uint8).reshape(2000,2000,3)
            if f in (22,394,435,675,693):
                validation[f]=full.copy()
            for label,n,(x0,y0,x1,y1) in proofs:
                if f==n:
                    details[label]=full[y0:y1,x0:x1].copy()
            if f in sofia or f in follow_shell:
                y0,y1=(280,1340) if f in sofia else (320,1380)
                profile=(full[y0:y1].max(2)<95).mean(0)
                left=np.flatnonzero(profile[280:890]>.55)+280
                right=np.flatnonzero(profile[1100:1730]>.55)+1100
                if left.size and right.size:
                    l,r=int(left[0]),int(right[-1])
                    track['sofia-rim' if f in sofia else 'follow-rim'][f]=(l,r,(l+r)/2,r-l+1)
            if f in follow:
                x0,y0,x1,y1=860,1040,1335,1480
                point=find_pointer(full[y0:y1,x0:x1],x0,y0,150)
                if point is not None:
                    track['follow-pointer'][f]=point
            if f in send:
                x0,y0,x1,y1=1435,1230,1960,1935
                point=find_pointer(full[y0:y1,x0:x1],x0,y0,175)
                if point is not None:
                    track['send-pointer'][f]=point
        if process.wait()!=0:
            raise RuntimeError(f'{movie} decoder failed')
    return details,track,validation

src=decode(reference)
rep=decode(candidate)
with (output/'exact/frames.csv').open() as file:
    strict={int(r['frame']):r for r in csv.DictReader(file)}
for f,a in src[2].items():
    assert int(np.count_nonzero((a!=rep[2][f]).any(2)))==int(strict[f]['exact_changed_pixels'])

grids=output/'previous-pass-crops'
grids.mkdir(exist_ok=False)
rows=[]
for label,frame,(x0,y0,x1,y1) in proofs:
    a=src[0][label]; b=rep[0][label]
    p=(np.maximum(a,b)-np.minimum(a,b)).max(2)
    mask=np.zeros_like(a)
    mask[:,:,0]=np.where(p>=30,255,0)
    mask[:,:,1]=np.where(p>=30,70,0)
    width,height=x1-x0,y1-y0
    canvas=Image.new('RGB',(width*3,height+35),'#f4f4f5')
    draw=ImageDraw.Draw(canvas)
    for j,(name,im) in enumerate(zip(('Original','Recreation','RGB channel delta ≥30'),(a,b,mask))):
        canvas.paste(Image.fromarray(im),(j*width,35))
        draw.text((j*width+10,7),f'f{frame}  {name}',font_size=18,fill='#17171c')
    canvas.save(grids/f'{label}.png')
    rows.append((label,frame,(x0,y0,x1,y1),int(p.size),int((p>0).sum()),int((p>=30).sum())))
with (output/'previous-pass-crops.csv').open('w',newline='') as file:
    writer=csv.writer(file)
    writer.writerow(['shot','frame','native_crop_xyxy','pixels','changed_pixels','pixels_with_rgb_delta_30_or_more'])
    writer.writerows(rows)
for name,first in src[1].items():
    second=rep[1][name]
    is_rim=name.endswith('rim')
    fields=['left','right','center_x','width'] if is_rim else ['center_x','center_y','tip_x','tip_y','dark_area','width','height']
    with (output/(name+'.csv')).open('w',newline='') as file:
        writer=csv.writer(file)
        writer.writerow(['frame',*[label+'_'+field for label in ('source','recreation') for field in fields]])
        for f in sorted(first.keys()|second.keys()):
            writer.writerow([f,*first.get(f,['']*len(fields)),*second.get(f,['']*len(fields))])
    print(name,'measured',len(first),len(second))
