#!/usr/bin/env python3
"""Independent 48 kHz stereo sound design; never reads the reference film."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
from scipy.io import wavfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
KIT=ROOT/'resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation'
RATE=48000

def music_bed(count, settings):
    rng=np.random.default_rng(settings['seed']);out=np.zeros((count,2),dtype=np.float64)
    if not count:return out
    beat=60/settings['bpm'];roots=[45,41,48,43]
    for i,start in enumerate(np.arange(0,count/RATE,beat/2)):
        root=roots[(i//16)%len(roots)]
        midi=root+[12,19,24,27,31,24,19,15][i%8]
        frequency=440*2**((midi-69)/12)
        n=min(round(RATE*beat*.95),count-round(start*RATE));t=np.arange(n)/RATE
        phase=rng.uniform(0,2*np.pi)
        signal=(np.sin(2*np.pi*frequency*t+phase)+.2*np.sin(4*np.pi*frequency*t+phase))
        signal*=np.minimum(t/.015,1)*np.exp(-t*6)
        pan=rng.uniform(-.45,.45);a=round(start*RATE)
        out[a:a+n,0]+=signal*np.sqrt((1-pan)/2)
        out[a:a+n,1]+=signal*np.sqrt((1+pan)/2)
    for i,start in enumerate(np.arange(0,count/RATE,beat)):
        a=round(start*RATE);n=min(round(.23*RATE),count-a);t=np.arange(n)/RATE
        kick=np.sin(2*np.pi*(48*t+7*(1-np.exp(-t*24))))*np.exp(-t*22)*np.minimum(t/.004,1)
        out[a:a+n]+=kick[:,None]*.28
    peak=float(abs(out).max())
    if peak:out*=10**(settings['gain_db']/20)/peak
    return out

def decode(path):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar',str(RATE),'-ac','2','pipe:1'])
    return np.frombuffer(raw,dtype='<f4').reshape(-1,2).astype(np.float64)

def build(schedule):
    if schedule['sample_rate']!=RATE or schedule['fps_denominator']!=1:
        raise ValueError('Expected 48 kHz and integer frame cadence')
    frames=schedule['frames'];fps=schedule['fps_numerator']
    if frames<1 or fps<=0:raise ValueError('Positive frame span and rate required')
    count=round(frames*RATE/fps)
    end=round(schedule['music_end_frame']*RATE/fps)
    if not 0<=end<=count:raise ValueError('Audio end is outside the film')
    for event in schedule['events']:
        if not isinstance(event['frame'],int) or not 0<=event['frame']<frames:raise ValueError('Cue outside film')
    sys.path.insert(0,str(KIT/'scripts'))
    spec=importlib.util.spec_from_file_location('shared_render_ui',KIT/'scripts/render_ui.py')
    shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
    stock=dict(schedule,events=[e for e in schedule['events'] if 'bank' not in e])
    ui,receipts=shared.build_ui(stock)
    for event in schedule['events']:
        if 'bank' not in event:continue
        path=KIT/'synthesis/bank'/f"{event['bank']}.wav"
        clip=decode(path);peak=float(abs(clip).max())
        if not peak:raise ValueError(f'Empty procedural bank effect: {path}')
        clip*=10**(event['peak_dbfs']/20)/peak
        a=round(event['frame']*RATE/fps);n=min(len(clip),count-a)
        ui[a:a+n]+=clip[:n]
        receipts.append({'canonical_event':event,'source':'original procedural synthesis bank','path':str(path.relative_to(ROOT))})
    bed=np.zeros_like(ui);bed[:end]=music_bed(end,schedule['music'])
    mix=ui+bed;peak=float(abs(mix).max());gain=min(1,10**(-9/20)/peak) if peak else 1
    mix*=gain;mix[end:]=0;ui[end:]=0
    if not np.isfinite(mix).all():raise ValueError('Nonfinite mix')
    return mix,ui,bed,{'sample_rate':RATE,'samples':count,'channels':2,'master_gain':gain,'sample_peak_dbfs':20*np.log10(float(abs(mix).max())) if peak else None,'music':schedule['music'],'provenance':schedule['provenance'],'receipts':receipts}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--cues',type=Path,default=HERE/'cues.json');args=parser.parse_args()
    mix,ui,bed,report=build(json.loads(args.cues.read_text()))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    for name,data in [(args.out,mix),(args.out.with_name('ui-only.wav'),ui),(args.out.with_name('music-only.wav'),bed)]:wavfile.write(name,RATE,data.astype(np.float32))
    args.out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Audio: {report['samples']} samples, 48000 Hz stereo; sample peak {report['sample_peak_dbfs']:.2f} dBFS; {len(report['receipts'])} cues; original music seed {report['music']['seed']}.")

if __name__=='__main__':main()
