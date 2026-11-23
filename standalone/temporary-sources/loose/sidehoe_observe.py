import io, subprocess, sys
from PIL import Image,ImageDraw
ref='/Users/darshan/Downloads/sidehoe.mp4'
step,w,cols,rows=map(int,sys.argv[1:])
dest='sidehoe-recreation/evidence'
proc=subprocess.Popen(['ffmpeg','-v','error','-i',ref,'-vf',f'scale={w}:{w}', '-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
batch=cols*rows
for n in range(778):
    data=proc.stdout.read(w*w*3)
    if len(data)!=w*w*3: raise RuntimeError(n)
    if n%step: continue
    i=n//step%batch
    if i==0:
        sheet=Image.new('RGB',(cols*w,rows*(w+21)), '#ddd')
        draw=ImageDraw.Draw(sheet)
    x,y=i%cols*w,i//cols*(w+21)
    sheet.paste(Image.frombytes('RGB',(w,w),data),(x,y))
    draw.text((x+5,y+w+3),f'{n:03}   {n/25:05.2f} s',fill='#111')
    if i==batch-1 or n+step>=778: sheet.save(f'{dest}/source-grid-{n//step//batch:02d}.jpg',quality=92)
proc.wait()
