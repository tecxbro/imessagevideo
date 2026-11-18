#!/usr/bin/env python3
"""Build, render, mix, verify, then publish one immutable complete export."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TRIAL=HERE.parent
LOG=TRIAL/'LOG.md'
ZONE=ZoneInfo('America/Los_Angeles')

def now():return datetime.now(ZONE).strftime('%H:%M PST')

def log(line):
    with LOG.open('a') as f:f.write(line+'\n')

def attempt(label,command,variable):
    start=now();tick=time.monotonic()
    log(f'- {start} → pending — {label}. Changed variable: {variable}.')
    try:
        subprocess.run([str(v) for v in command],cwd=ROOT,check=True)
    except Exception as exc:
        log(f'  - {start} → {now()} — {label} FAILED: {exc}; elapsed {time.monotonic()-tick:.2f} s.')
        raise
    elapsed=time.monotonic()-tick
    log(f'  - {start} → {now()} — {label} OK; observed failure: none; elapsed {elapsed:.2f} s.')
    return elapsed

def true_peak(path):
    result=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn','-af','loudnorm=I=-24:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    matches=re.findall(r'\{\s*"input_i"[\s\S]*?\}',result.stderr)
    if not matches:raise RuntimeError('Could not obtain encoded AAC true-peak measurement')
    report=json.loads(matches[-1]);peak=float(report['input_tp'])
    if peak>=-1:raise RuntimeError(f'Encoded AAC true peak {peak} dBTP violates headroom')
    return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path.home()/'work/rw/exports/readwise-first-export.mp4');args=parser.parse_args()
    final=args.out.expanduser().resolve();receipt=TRIAL/'exports/FIRST-EXPORT.sha256'
    if final.exists() or receipt.exists():raise FileExistsError('First export or its receipt already exists; never overwrite. Use a new export filename and receipt for later versions.')
    work=final.parent/f'build-{datetime.now(ZONE):%Y%m%d-%H%M%S}'
    work.mkdir(parents=True,exist_ok=False);stage=work/'candidate.mp4';picture=work/'picture.mp4';mix=work/'mix.wav'
    env=os.environ.copy();env.setdefault('CHROME_PATH','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');os.environ.update(env)
    started=now();tick=time.monotonic();times={}
    times['build']=attempt('Complete scene build',[sys.executable,HERE/'build_scene.py'],'S2/S3/S4 enabled; all copy/timing read from JSON')
    times['picture']=attempt('Full 1110-frame HTML picture render',['node',ROOT/'skill/imessage-motion-recreation/scripts/engines/render.mjs','--method','html','--scene',HERE/'build/scene.json','--out',picture,'--frames-dir',work/'frames'],'final checkpoint-corrected vectors; zero-area frame anchor; unchanged shared engine')
    times['audio']=attempt('Independent UI + original music render',[sys.executable,HERE/'audio/render_audio.py','--out',mix],'CC0 keys/clicks, declared original synthesis-bank send/pop, original seeded music; no source audio input')
    times['mux']=attempt('Explicit new-audio mux',['ffmpeg','-hide_banner','-loglevel','error','-n','-i',picture,'-i',mix,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','37','-movflags','+faststart',stage],'only rendered picture video and newly mixed WAV audio selected')
    peak=true_peak(stage)
    probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels,duration:format=duration,size','-of','json',stage],text=True)
    data=json.loads(probe);video=next(s for s in data['streams'] if s['codec_type']=='video');audio=next(s for s in data['streams'] if s['codec_type']=='audio')
    if len(data['streams'])!=2 or (video['width'],video['height'],video['nb_frames'],video['r_frame_rate'])!=(1920,1080,'1110','30/1') or (audio['sample_rate'],audio['channels'])!=('48000',2):raise RuntimeError('Export stream properties do not match contract')
    os.link(stage,final);stage.unlink()
    sha=subprocess.check_output(['shasum','-a','256',final],text=True)
    receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open('x') as f:f.write(sha)
    with (receipt.parent/'FIRST-EXPORT.ffprobe.json').open('x') as f:f.write(probe)
    report={'export':str(final),'sha256':sha.split()[0],'start':started,'end':now(),'wall_seconds':round(time.monotonic()-tick,2),'stages_seconds':times,'aac_analysis':peak,'work':str(work),'scene_sha256':hashlib.sha256((HERE/'build/scene.json').read_bytes()).hexdigest()}
    with (receipt.parent/'FIRST-EXPORT.report.json').open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
    log(f'- {started} → {now()} — FIRST COMPLETE EXPORT published once: {final}; SHA256 {sha.split()[0]}; encoded AAC true peak {peak["input_tp"]} dBTP; pipeline {report["wall_seconds"]} s.')
    print(sha.strip());print(probe);print(f'Encoded AAC true peak: {peak["input_tp"]} dBTP; pipeline wall time: {report["wall_seconds"]} s')

if __name__=='__main__':main()
