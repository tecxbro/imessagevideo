"""Original stereo instrumental and frame-anchored synthesized Foley."""
import argparse
from pathlib import Path
import json
import math
import wave

import numpy as np


RATE=48000


def hz(midi):
    return 440 * 2 ** ((midi-69)/12)


def sine(t,frequency):
    return np.sin(math.tau*frequency*t)


def place(stem, start, signal, pan=0):
    start=round(start)
    a=max(0,start)
    b=min(len(stem),start+len(signal))
    if a<b:
        audio=signal[a-start:b-start]
        stem[a:b,0]+=audio*math.sqrt((1-pan)*.5)
        stem[a:b,1]+=audio*math.sqrt((1+pan)*.5)


def count(seconds):
    return round(seconds*RATE)


def time(seconds):
    return np.arange(count(seconds))/RATE


def write_wav(path, samples):
    with wave.open(str(path),"wb") as file:
        file.setparams((2,2,RATE,len(samples),"NONE","not compressed"))
        file.writeframes(np.int16(np.clip(samples,-1,1)*32767).astype("<i2").tobytes())


def build(scene, output):
    output.mkdir(parents=True,exist_ok=True)
    metadata=scene["timeline"]["picture"]
    frames=metadata["frameCount"]
    per_frame=RATE*metadata["fpsDen"]/metadata["fpsNum"]
    seconds=frames*per_frame/RATE
    music=np.zeros((count(seconds),2),dtype=np.float32)
    effects=music.copy()
    beat=60/scene["score"]["bpm"]
    rng=np.random.default_rng(602)
    chords=scene["score"]["chords"]
    melody=scene["score"]["melody"]
    for i in range(math.ceil(seconds/beat)):
        chord=chords[(i//4)%len(chords)]
        t=time(.46)
        env=(1-np.exp(-t*160))*np.exp(-t*8)
        fundamental=hz(chord[0])
        bass=(sine(t,fundamental)+sine(t,2*fundamental)*.24)*env*.045
        place(music,count(i*beat),bass)
        if i%2==0:
            kick=.085*np.sin(math.tau*(46*t+4*(1-np.exp(-t*32))))*np.exp(-t*22)
            place(music,count(i*beat),kick)
        else:
            clap=(rng.normal(size=t.size)*.014+.014*sine(t,161))*np.exp(-t*36)
            place(music,count(i*beat),clap,.13)
        for step in (0,1):
            j=i*2+step
            t=time(.43)
            env=(1-np.exp(-t*150))*np.exp(-t*10.5)
            note=hz(chord[melody[j%len(melody)]]+12+(12 if j%11==6 else 0))
            lead=(sine(t,note)+.23*sine(t,note*2+1)+.15*sine(t,note*3-.5))*env
            pan=-.40 if (j//2)%2==0 else .39
            when=count((i+step*.5)*beat)
            place(music,when,lead*.034,pan)
            place(music,when+count(.156),lead*.011,-pan)
            t=time(.10)
            noise=rng.normal(size=t.size)
            hat=np.append(0,np.diff(noise))*np.exp(-t*52)*.006
            place(music,when+count(.028),hat,.42)
        if i%4==0:
            t=time(4*beat+.2)
            attack=np.clip(t/.35,0,1)
            release=np.clip((t[-1]-t)/.45,0,1)
            for j,midi in enumerate(chord[1:]):
                frequency=hz(midi)
                tone=(sine(t,frequency)+.30*sine(t,frequency*1.997)+.18*sine(t,frequency/2))
                place(music,count(i*beat),tone*attack*release*.013,(j-1)*.35)
    events={e["id"]:e for e in scene["timeline"]["events"]}
    resolved=[]
    for cue in scene["timeline"]["cues"]:
        frame=events[cue["eventId"]]["frame"]
        start=math.floor(frame*per_frame+.5)+cue["offsetSamples"]
        kind=cue["asset"]
        if kind=="tap":
            t=time(.13)
            signal=(.095*sine(t,945)+.032*sine(t,1440)+.023*rng.normal(size=t.size))*np.exp(-t*70)
        elif kind=="chime":
            t=time(.35)
            signal=.049*(sine(t,785)+.57*sine(t,1175)+.25*sine(t,1568))*np.exp(-t*10)
        else:
            t=time(.29)
            noise=np.append(0,np.diff(rng.normal(size=t.size)))
            signal=(.017*noise+.023*np.sin(math.tau*(260*t-192*t*t)))*np.sin(np.pi*t/t[-1])**3
        place(effects,start,signal, -.19 if kind=="swish" else .08)
        resolved.append({**cue,"frame":frame,"sample":start,"seconds":start/RATE,
                         "availableSamples":min(len(signal),len(music)-start)})
    t=np.arange(len(music))/RATE
    env=np.clip(t/.055,0,1)*np.clip((seconds-t)/.47,0,1)
    music *= env[:,None] * scene["score"]["gain"]
    effects *= env[:,None]
    write_wav(output/"score.wav",music)
    write_wav(output/"foley.wav",effects)
    write_wav(output/"mix.wav",music+effects)
    (output/"events.json").write_text(json.dumps({"picture":metadata,"events":scene["timeline"]["events"],
                                                "sampleRate":RATE,"cues":resolved},indent=2,
                                               ensure_ascii=False)+"\n")
    print(f"Rendered {len(resolved)} Foley cues and {seconds:.3f}s of stereo score")


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--scene",type=Path,default=Path(__file__).with_name("scene.json"))
    cli.add_argument("--out",type=Path,required=True)
    args=cli.parse_args()
    build(json.loads(args.scene.read_text()),args.out)


if __name__=="__main__":
    main()
