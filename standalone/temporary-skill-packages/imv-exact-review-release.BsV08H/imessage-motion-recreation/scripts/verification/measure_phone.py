#!/usr/bin/env python3
"""Find candidate phone-bezel boxes; proposals require native-frame visual checks."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from scipy import ndimage

def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--fps',type=float,default=2);p.add_argument('--start',type=float,default=0)
    p.add_argument('--duration',type=float,required=True);a=p.parse_args()
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(a.source)]))['streams'][0]
    w,h=meta['width'],meta['height']
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-ss',str(a.start),'-i',str(a.source),'-t',str(a.duration),'-vf',f'fps={a.fps}', '-f','rawvideo','-pix_fmt','rgb24','pipe:1']
    proc=subprocess.Popen(cmd,stdout=subprocess.PIPE);rows=[];i=0
    while True:
        raw=proc.stdout.read(w*h*3)
        if len(raw)!=w*h*3:break
        im=np.frombuffer(raw,dtype=np.uint8).reshape(h,w,3)
        mask=np.max(im,axis=2)<95
        labeled,n=ndimage.label(mask)
        candidates=[]
        for label,box in enumerate(ndimage.find_objects(labeled),1):
            if box is None:continue
            ys,xs=box;bw=xs.stop-xs.start;bh=ys.stop-ys.start
            if bw<80 or bh<250 or not 1.3<bh/bw<2.9:continue
            ink=int(np.count_nonzero(labeled[box]==label));area=bw*bh
            if ink<1000 or ink/area<.02:continue
            center=abs((xs.start+bw/2)-w/2)/w
            candidates.append({'bbox':[xs.start,ys.start,bw,bh],'connected_dark_pixels':ink,
                'score':area*(1-center),'cropped':xs.start==0 or ys.start==0 or xs.stop==w or ys.stop==h})
        candidates.sort(key=lambda x:x['score'],reverse=True)
        rows.append({'t':a.start+(i+.5)/a.fps,'sampling_note':'FFmpeg fps bin center, not a frame-exact animation key',
            'candidates':candidates[:3]});i+=1
    if proc.wait():raise RuntimeError('FFmpeg decode failed')
    result={'source':str(a.source),'native_dimensions':[w,h],
        'notice':'Connected-component proposals only. Dark UI cards, cropped phones, and title text can confuse detection. Verify original native frame before using.', 'samples':rows}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2));print({'samples':i,'with_candidates':sum(bool(r['candidates']) for r in rows),'out':str(a.out)})

if __name__=='__main__':main()
