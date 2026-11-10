#!/usr/bin/env python3
"""Attach declared reference audio to a finished recreation without encoding video."""
import argparse,hashlib,json,subprocess
from pathlib import Path

def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))['streams']
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',required=True);p.add_argument('--candidate',required=True);p.add_argument('--out',required=True);p.add_argument('--segments',help='Existing source/output alignment JSON');a=p.parse_args();reference=Path(a.reference).resolve();candidate=Path(a.candidate).resolve();out=Path(a.out).resolve()
 if out in (reference,candidate):raise ValueError('Use a separate output so the native render/source remain intact')
 native=next(s for s in probe(candidate) if s['codec_type']=='video');audio=next((s for s in probe(reference) if s['codec_type']=='audio'),None)
 if not audio:raise ValueError('Reference has no audio stream')
 duration=float(native['duration']);out.parent.mkdir(parents=True,exist_ok=True);cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-i',str(candidate),'-threads','1','-i',str(reference)];segments=None
 if a.segments:
  segments=json.loads(Path(a.segments).read_text());parts=[];labels=[]
  for i,seg in enumerate(segments):
   start=float(seg['reference_start']);length=float(seg['duration']);parts.append(f'[1:a:0]atrim=start={start:.9f}:duration={length:.9f},asetpts=PTS-STARTPTS[a{i}]');labels.append(f'[a{i}]')
  parts.append(''.join(labels)+f'concat=n={len(segments)}:v=0:a=1[audio]');cmd+=['-filter_complex_threads','1','-filter_complex',';'.join(parts),'-map','0:v:0','-map','[audio]','-c:a','aac','-b:a','192k'];treatment='Reference audio trimmed/concatenated to declared graphic segments and AAC encoded'
 else:cmd+=['-map','0:v:0','-map','1:a:0','-c:a','copy'];treatment='Original reference audio stream copied and trimmed to native video duration'
 cmd+=['-c:v','copy','-threads','2','-t',f'{duration:.9f}','-movflags','+faststart',str(out)];subprocess.run(cmd,check=True);streams=probe(out);video=next(s for s in streams if s['codec_type']=='video')
 for key in ('width','height','nb_frames'):
  if str(video.get(key))!=str(native.get(key)):raise RuntimeError(f'Unexpected video change: {key}')
 meta={'reference':str(reference),'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'candidate':str(candidate),'output':str(out),'audio_treatment':treatment,'video_treatment':'Video bitstream copied; no video encoding','segments':segments,'duration':video.get('duration'),'video_frames':video.get('nb_frames'),'reference_audio_codec':audio['codec_name'],'output_audio_codec':next(s['codec_name'] for s in streams if s['codec_type']=='audio')};Path(str(out)+'.audio.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
if __name__=='__main__':main()
