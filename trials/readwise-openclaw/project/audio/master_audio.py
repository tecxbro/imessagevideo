#!/usr/bin/env python3
"""Measure the reference only; master exclusively the independently authored mix."""
import argparse
import json
import math
from pathlib import Path
import re
import subprocess

def read_measurement(stderr):
    matches=re.findall(r'\{\s*"input_i"[\s\S]*?\}',stderr)
    if not matches:raise RuntimeError('FFmpeg returned no loudness measurement')
    data=json.loads(matches[-1])
    if not all(math.isfinite(float(data[k])) for k in ['input_i','input_tp']):raise ValueError('Nonfinite loudness measurement')
    return data

def measure(path,target=-16.4):
    result=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-map','0:a:0','-af',f'loudnorm=I={target}:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    return read_measurement(result.stderr)

def master(mix,out,source,first,frames=1110,fps=30):
    reference=measure(source);target=float(reference['input_i'])
    before=measure(mix,target);original=measure(first,target)
    params=f'loudnorm=I={target}:TP=-2:LRA=11:measured_I={before["input_i"]}:measured_TP={before["input_tp"]}:measured_LRA={before["input_lra"]}:measured_thresh={before["input_thresh"]}:offset={before["target_offset"]}:linear=false:print_format=json'
    end=round(1100*48000/fps);count=round(frames*48000/fps)
    result=subprocess.run(['ffmpeg','-hide_banner','-nostats','-n','-i',str(mix),'-map','0:a:0','-af',params+f',aresample=48000,atrim=end_sample={end},apad=whole_len={count}','-ar','48000','-ac','2','-c:a','pcm_f32le',str(out)],capture_output=True,text=True,check=True)
    after=measure(out,target)
    if abs(float(after['input_i'])-target)>1 or float(after['input_tp'])>-1:raise RuntimeError('PCM master missed delivery bounds')
    report={'source':reference,'first_export':original,'raw_mix':before,'mastered_pcm':after,'pass2':read_measurement(result.stderr),'target_lufs':target,'target_tp_dbtp':-2,'method':'two-pass dynamic loudnorm, reference used for measurement only'}
    out.with_suffix('.loudness.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Master: source {target:.2f} LUFS / {reference["input_tp"]} dBTP; first {original["input_i"]} LUFS / {original["input_tp"]} dBTP; PCM {after["input_i"]} LUFS / {after["input_tp"]} dBTP.')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mix',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--source',type=Path,default=Path.home()/'work/rw/source.mp4');p.add_argument('--first',type=Path,default=Path.home()/'work/rw/exports/readwise-first-export.mp4');a=p.parse_args();master(a.mix,a.out,a.source,a.first)
