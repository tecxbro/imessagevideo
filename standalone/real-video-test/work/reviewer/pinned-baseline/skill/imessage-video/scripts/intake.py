"""Prepare reusable source evidence. Call from decide.py on new footage."""
import csv
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image, ImageChops, ImageDraw, ImageStat
from frames import inspect


def prepare(video, identity, workdir, rea_bin=None):
    video = Path(video).resolve()
    digest = identity['sha256']
    parent = Path(workdir).resolve() / 'intake'
    parent.mkdir(parents=True, exist_ok=True)
    folder = parent / digest
    with (parent / ('.'+digest+'.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not (folder/'source.json').is_file():
            with tempfile.TemporaryDirectory(dir=parent) as temporary:
                staged = Path(temporary)/'study'
                staged.mkdir()
                index = scan(video, digest, staged)
                (staged/'source.json').write_text(json.dumps(index, indent=2)+'\n')
                staged.rename(folder)
        rea = rea_bin or os.environ.get('IMESSAGE_VIDEO_REA') or shutil.which('rea-video')
        breakdown = folder/'rea'/'breakdown.json'
        if rea and not breakdown.is_file():
            with tempfile.TemporaryDirectory(dir=parent) as temporary:
                output = Path(temporary)/'rea'
                subprocess.run([str(rea), 'decompose', str(video), '-o', str(output),
                                '--lang', 'en', '--no-vlm', '--no-stems', '--no-asr'], check=True)
                if not (output/'breakdown.json').is_file():
                    raise ValueError('REA exited without producing a breakdown.')
                output.rename(folder/'rea')
    return {'source': str(folder/'source.json'), 'frames':str(folder/'frames.csv'),
            'overview':str(folder/'overview.jpg'), 'rea_breakdown':str(breakdown) if breakdown.is_file() else None,
            'next':'Open the source frames, inventory each moving layer and compare candidate recipes.'}


def scan(video, digest, staged):
    meta, pts, _ = inspect(video)
    if meta['sha256'] != digest:
        raise ValueError('Source changed between recognition and intake.')
    w,h=192,108
    samples=set(round(i*(len(pts)-1)/min(11,max(1,len(pts)-1))) for i in range(min(12,len(pts))))
    overview=Image.new('RGB',(4*w,((len(samples)+3)//4)*(h+20)), '#222222')
    draw=ImageDraw.Draw(overview)
    command=['ffmpeg','-nostdin','-v','error','-xerror','-threads','2','-i',str(video),
             '-map','0:v:0','-an','-vf',f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2',
             '-fps_mode','passthrough','-pix_fmt','rgb24','-c:v','rawvideo','-threads','1','-f','rawvideo','pipe:1']
    proc=subprocess.Popen(command,stdout=subprocess.PIPE)
    prev=None
    count=0
    try:
        with (staged/'frames.csv').open('w',newline='') as file:
            rows=csv.writer(file, lineterminator="\n")
            rows.writerow(('frame','source_pts_seconds','mean_thumbnail_change_0_to_255'))
            for index,t in enumerate(pts):
                rgb=proc.stdout.read(w*h*3)
                if len(rgb)!=w*h*3:
                    raise ValueError(f'Could not decode source frame {index}')
                im=Image.frombytes('RGB',(w,h),rgb)
                delta=sum(ImageStat.Stat(ImageChops.difference(im,prev)).mean)/3 if prev else 0
                rows.writerow([index,None if t is None else float(t),round(delta,4)])
                if index in samples:
                    x=(count%4)*w
                    y=(count//4)*(h+20)
                    overview.paste(im,(x,y))
                    draw.text((x+4,y+h+2), f'f{index}',fill='white')
                    count+=1
                prev=im
        if proc.stdout.read(1) or proc.wait()!=0:
            raise ValueError('Decoded source frame count disagrees with the source timeline.')
    finally:
        proc.stdout.close()
        if proc.poll() is None:
            proc.kill()
        proc.wait()
    overview.save(staged/'overview.jpg',quality=90)
    return {**meta,'overview_source_frames':sorted(samples),
            'scope':'All frame timestamps and low-resolution changes. Poses, bounds and review require original-resolution evidence.'}
