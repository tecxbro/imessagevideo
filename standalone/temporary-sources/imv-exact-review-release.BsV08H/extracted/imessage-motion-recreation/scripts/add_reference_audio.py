#!/usr/bin/env python3
"""Mux a reconstruction with the supplied reference soundtrack, using explicit cuts."""
import argparse, json, subprocess, hashlib, os
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('reference',type=Path)
    p.add_argument('candidate',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('--segments',type=Path)
    a=p.parse_args()
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=duration,nb_frames,avg_frame_rate','-of','json',str(a.candidate)]))['streams'][0]
    duration=float(info['duration'])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    temporary=a.output.with_name(a.output.stem+f'.muxing-{os.getpid()}'+a.output.suffix)
    sidecar=a.output.with_suffix('.audio.json')
    sidecar.unlink(missing_ok=True)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-filter_complex_threads','1','-i',str(a.candidate),'-threads','1','-i',str(a.reference)]
    if a.segments:
        segments=json.loads(a.segments.read_text())
        tracks=[]
        labels=[]
        for i,s in enumerate(segments):
            start=float(s['reference_start']); end=start+float(s['duration'])
            tracks.append(f'[1:a:0]atrim=start={start:.12f}:end={end:.12f},asetpts=PTS-STARTPTS[a{i}]')
            labels.append(f'[a{i}]')
        tracks.append(''.join(labels)+f'concat=n={len(segments)}:v=0:a=1[soundtrack]')
        cmd+=['-filter_complex',';'.join(tracks),'-map','0:v:0','-map','[soundtrack]']
    else:
        cmd+=['-map','0:v:0','-map','1:a:0']
    # All six acquired soundtracks are AAC. Preserve their packets when no cut is
    # required; the trimmed Rene soundtrack must be encoded after concatenation.
    cmd+=['-c:v','copy','-c:a','aac' if a.segments else 'copy']
    if a.segments:cmd+=['-b:a','192k']
    cmd+=['-t',str(duration),'-movflags','+faststart',str(temporary)]
    subprocess.run(cmd,check=True)
    temporary.replace(a.output)
    render_meta=Path(str(a.candidate)+'.render.json')
    provenance=json.loads(render_meta.read_text()) if render_meta.exists() else {}
    record={'video':str(a.candidate),
        'picture_sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),
        'sceneSHA256':provenance.get('sceneSHA256',provenance.get('sceneSha256')),
        'method':provenance.get('method'),
        'reference_soundtrack':str(a.reference),'duration':duration,
        'segments':str(a.segments) if a.segments else None,
        'audio_encoding':'AAC encode after explicit cuts' if a.segments else 'Original AAC packet copy',
        'note':'Independent reconstructed picture; audio reused from the user-supplied reference.'}
    pending=sidecar.with_name(sidecar.name+'.tmp')
    pending.write_text(json.dumps(record,indent=2));pending.replace(sidecar)
    print(a.output)

if __name__=='__main__':main()
