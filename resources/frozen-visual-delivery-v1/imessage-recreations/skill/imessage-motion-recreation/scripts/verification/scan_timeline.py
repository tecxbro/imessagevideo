#!/usr/bin/env python3
"""Scan every aligned native frame, then rank separated error peaks for inspection.

This is a diagnosis pass, not a perceptual perfection score. It does not replace
native SSIM/foreground comparison or visual review of the selected transitions.
"""
from pathlib import Path
import argparse,csv,json,subprocess,hashlib
import numpy as np

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=width,height,nb_frames,r_frame_rate','-of','json',str(path)]))['streams'][0]

def reader(path,select=None):
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-filter_threads','1','-i',str(path)]
    if select:cmd+=['-vf',select,'-fps_mode','passthrough']
    cmd+=['-map','0:v:0','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    return subprocess.Popen(cmd,stdout=subprocess.PIPE)

def read_exact(stream,size):
    value=bytearray()
    while len(value)<size:
        part=stream.read(size-len(value))
        if not part:break
        value.extend(part)
    return value

def main():
    p=argparse.ArgumentParser()
    p.add_argument('reference',type=Path);p.add_argument('candidate',type=Path)
    p.add_argument('--segments',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--peaks',type=int,default=24)
    a=p.parse_args();info=probe(a.candidate);reference_info=probe(a.reference)
    width,height=info['width'],info['height'];num,den=map(int,info['r_frame_rate'].split('/'));fps=num/den
    if (width,height)!=(reference_info['width'],reference_info['height']):raise ValueError('Native dimensions differ')
    count=int(info['nb_frames']);mapping=list(range(count));selection=None
    if a.segments:
        segments=json.loads(a.segments.read_text());mapping=[];pieces=[]
        for s in segments:
            first=round(s['reference_start']*fps);length=round(s['duration']*fps)
            mapping.extend(range(first,first+length));pieces.append(f'between(n,{first},{first+length-1})')
        selection="select='"+'+'.join(pieces)+"'"
    if len(mapping)!=count:raise ValueError('Source mapping frame count differs')
    source=reader(a.reference,selection);candidate=reader(a.candidate);rows=[];size=width*height*3
    try:
        for n in range(count):
            raw_source=read_exact(source.stdout,size);raw_candidate=read_exact(candidate.stdout,size)
            if len(raw_source)!=size or len(raw_candidate)!=size:raise ValueError(f'Incomplete decode at frame {n}')
            ref=np.frombuffer(raw_source,dtype=np.uint8).reshape(height,width,3)
            out=np.frombuffer(raw_candidate,dtype=np.uint8).reshape(height,width,3)
            difference=np.abs(np.subtract(ref,out,dtype=np.int16))
            rows.append({'candidate_frame':n,'reference_frame':mapping[n],
                'candidate_time':n/fps,'reference_time':mapping[n]/fps,
                'mae':float(difference.mean()),'max_channel_error':int(difference.max())})
        # Close pipes after the expected picture count, ignoring longer source tails.
    finally:
        for process in [source,candidate]:
            process.stdout.close()
            if process.poll() is None:process.terminate()
            process.wait()
    peaks=[]
    for row in sorted(rows,key=lambda r:r['mae'],reverse=True):
        if all(abs(row['candidate_frame']-old['candidate_frame'])>=round(fps*.5) for old in peaks):
            peaks.append(row)
            if len(peaks)>=a.peaks:break
    report={'reference':str(a.reference),'candidate':str(a.candidate),'dimensions':[width,height],
        'referenceSHA256':hashlib.sha256(a.reference.read_bytes()).hexdigest(),
        'candidateSHA256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),
        'fps':fps,'frames_scanned':count,'mean_native_mae':float(np.mean([r['mae'] for r in rows])),
        'maximum_native_mae':max(r['mae'] for r in rows),'peaks':peaks,
        'notice':'Every aligned native picture frame was measured. Error peaks require visual and foreground diagnosis; this is not a perfection percentage.'}
    sidecar=Path(str(a.candidate)+'.render.json')
    if sidecar.exists():
        metadata=json.loads(sidecar.read_text())
        report['sceneSHA256']=metadata.get('sceneSHA256',metadata.get('sceneSha256'))
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'scan.json').write_text(json.dumps(report,indent=2))
    with (a.out/'frames.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (a.out/'peak-segments.json').write_text(json.dumps([{'name':f"frame-{r['candidate_frame']}",
        'reference_start':r['reference_time'],'candidate_start':r['candidate_time'],'duration':1/fps}
        for r in sorted(peaks,key=lambda r:r['candidate_frame'])],indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='peaks'},indent=2))

if __name__=='__main__':main()
