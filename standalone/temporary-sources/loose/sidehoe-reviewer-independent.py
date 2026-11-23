import csv
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw

src=Path('/Users/darshan/Downloads/sidehoe.mp4')
root=Path('sidehoe-skill-trial/repair')
dst=root/'exports/sidehoe.mp4'
out=root/'reviewer-audit'
frames_by_name={
 'bubble':(394,(660,475,1890,1480)),
 'calendar':(435,(145,236,1880,1050)),
 'calendar-emoji':(435,(310,720,845,930)),
 'app-31':(616,(742,1260,1245,1790)),
 'buttons':(675,(342,935,1080,1265)),
}
cursor_rect=(915,975,1245,1210)
cursor_frames=list(range(417,432))
keep=sorted(set([f for f,_ in frames_by_name.values()]+cursor_frames))

def read(movie):
    select='select='+ '+'.join(f'eq(n\\,{f})' for f in keep)
    tool=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-xerror','-threads','2',
          '-noautorotate','-apply_cropping','codec','-i',str(movie),'-map','0:V:0',
          '-an','-sn','-dn','-filter_threads','2','-vf',select,'-frames:v',str(len(keep)),
          '-fps_mode','passthrough','-c:v','rawvideo','-threads:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
    details={}
    pointers={}
    checks={}
    with subprocess.Popen(tool,stdout=subprocess.PIPE) as p:
        for f in keep:
            raw=p.stdout.read(2000*2000*3)
            if len(raw)!=2000*2000*3:
                raise RuntimeError(f'Missing native frame {f} in {movie}')
            full=np.frombuffer(raw,dtype=np.uint8).reshape(2000,2000,3)
            if f in (394,435,616,675):
                checks[f]=full.copy()
            for name,(sample,rect) in frames_by_name.items():
                if f==sample:
                    xl,yl,xr,yr=rect
                    details[name]=full[yl:yr,xl:xr].copy()
            if f in cursor_frames:
                xl,yl,xr,yr=cursor_rect
                tile=full[yl:yr,xl:xr].copy()
                coords=np.argwhere(tile.max(2)<80)
                if len(coords)==0:
                    continue
                low=coords.min(0); high=coords.max(0)
                pointers[f]=(coords.mean(0)+[yl,xl],int(len(coords)),high-low+1,tile)
        if p.wait()!=0:
            raise RuntimeError(f'Decoder failed for {movie}')
    return details,pointers,checks

ref=read(src); enc=read(dst)
with (out/'exact/frames.csv').open() as stream:
    all_frames=list(csv.DictReader(stream))
assert len(all_frames)==778
for f in ref[2]:
    assert int(np.count_nonzero((ref[2][f]!=enc[2][f]).any(2)))==int(all_frames[f]['exact_changed_pixels'])

def peak(a,b):
    return (np.maximum(a,b)-np.minimum(a,b)).max(2)

def triplet(reference,reconstruction):
    diff=peak(reference,reconstruction)
    highlights=np.zeros_like(reference)
    highlights[:,:,0]=np.where(diff>=30,255,0)
    highlights[:,:,1]=np.where(diff>=30,70,0)
    tiles=(Image.fromarray(reference),Image.fromarray(reconstruction),Image.fromarray(highlights))
    return tiles,diff

native=out/'native-crops'
native.mkdir()
rows={}
for key,(frame,rect) in frames_by_name.items():
    tiles,diff=triplet(ref[0][key],enc[0][key])
    width,height=tiles[0].size
    board=Image.new('RGB',(3*width,height+36),'#f4f4f5')
    draw=ImageDraw.Draw(board)
    for j,(name,tile) in enumerate(zip(('Original','Recreation','Changed by at least 30 RGB levels'),tiles)):
        board.paste(tile,(width*j,36))
        draw.text((width*j+10,9),f'f{frame}  {name}', fill='#17171c',font_size=17)
    board.save(native/f'{key}.png')
    rows[key]={'frame':frame,'crop_xyxy':rect,'pixels':int(diff.size),
               'different':int((diff>0).sum()),'at_least_30':int((diff>=30).sum()),
               'mean_abs_rgb':float((np.maximum(ref[0][key],enc[0][key])-np.minimum(ref[0][key],enc[0][key])).mean())}

with (out/'calendar-pointer.csv').open('w',newline='') as stream:
    writer=csv.writer(stream)
    writer.writerow(['frame','original_center_x','original_center_y','original_dark_pixels','original_width','original_height',
                     'candidate_center_x','candidate_center_y','candidate_dark_pixels','candidate_width','candidate_height'])
    for f in cursor_frames:
        ref_pose,enc_pose=ref[1].get(f),enc[1].get(f)
        if ref_pose is not None and enc_pose is not None:
            writer.writerow([f,*[val for xy,count,wh,_ in (ref_pose,enc_pose)
                   for val in (round(float(xy[1]),2),round(float(xy[0]),2),count,int(wh[1]),int(wh[0]))]])
chosen=[418,419,420,421,422,429,430]
w,h=330,235
board=Image.new('RGB',(2*(w+10),len(chosen)*(h+23)),'#f4f4f5'); draw=ImageDraw.Draw(board)
for i,f in enumerate(chosen):
    for j,(label,sequence) in enumerate((('Original',ref[1]),('Recreation',enc[1]))):
        tiles=sequence.get(f)
        if tiles is None:
            continue
        x,y=j*(w+10)+5,i*(h+23)
        board.paste(Image.fromarray(tiles[3]),(x,y+19))
        draw.text((x,y+1),f'f{f} {label}  |  dark pointer pixels {tiles[1]}',fill='#17171c')
board.save(native/'pointer-motion.png')

with (out/'each-second.csv').open('w',newline='') as stream:
    writer=csv.writer(stream)
    writer.writerow(['second','first_frame','last_frame','frames','identical_frames',
                     'frames_with_pixel_delta_at_least_30','mean_frame_rgb_error','worst_frame','worst_frame_rgb_error'])
    for start in range(0,len(all_frames),25):
        rows_here=all_frames[start:start+25]
        worst=max(rows_here,key=lambda row:float(row['mean_abs_rgb']))
        writer.writerow([start//25,start,rows_here[-1]['frame'],len(rows_here),
              sum(int(row['exact_changed_pixels'])==0 for row in rows_here),
              sum(int(row['pixels_above_floor'])>0 for row in rows_here),
              round(sum(float(row['mean_abs_rgb']) for row in rows_here)/len(rows_here),6),
              int(worst['frame']),round(float(worst['mean_abs_rgb']),6)])
(out/'targeted-crops.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
print('Actual frames with a pixel off by at least 30:',sum(int(row['pixels_above_floor'])>0 for row in all_frames))
