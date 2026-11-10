#!/usr/bin/env python3
"""Portable UI-audio mux for any of the five accepted picture formats."""
from pathlib import Path
import argparse,hashlib,json,subprocess,os
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--example',required=True);p.add_argument('--method',choices=['remotion','gsap','html','pillow','motion-canvas'],default='gsap');p.add_argument('--mode',choices=['ui','music'],default='ui');p.add_argument('--video',type=Path);p.add_argument('--audio-dir',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
 video=a.video or ROOT/'deliverables'/a.example/(a.method+'.mp4');folder=a.audio_dir or ROOT/'audio-recreation/ui-mixes'/a.example;audio=folder/('ui_preview.m4a' if a.mode=='ui' else 'full_mix.m4a')
 output=a.out or ROOT/'new-ui-deliverables'/a.example/(a.method+'-'+a.mode+'.mp4')
 for f in [video,audio]:
  if not f.is_file():raise FileNotFoundError('Materialize the complete visual/audio pack first: '+str(f))
 if output.exists():raise FileExistsError('Keep existing artifacts immutable; choose a new --out: '+str(output))
 output.parent.mkdir(parents=True,exist_ok=True);temp=output.with_name(output.stem+'.muxing.mp4')
 try:subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-i',str(video),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-movie_timescale','48000',str(temp)],check=True);os.replace(temp,output)
 finally:temp.unlink(missing_ok=True)
 record={'video':str(video),'audio':str(audio),'out':str(output),'method':a.method,'mode':a.mode,'video_reencoded':False,'reference_audio_mapped':False,'ui_only_is_labelled_listening_boost':a.mode=='ui','sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest()};output.with_suffix('.provenance.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
if __name__=='__main__':main()
