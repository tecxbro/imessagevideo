"""Seed six Check In interventions in decoded production-MP4 audio."""
import argparse
import json
from pathlib import Path
import numpy as np
from check_cues import SR,add,decode,packet_hash
from build_treatments import mux,write
from render_mix import encode,sha256


def intervene(audio,receipt,base,seed):
    rng=np.random.default_rng(seed);output=audio.copy();defects=[]
    cues=receipt['cues'];by_frame={c['canonical_event']['frame']:c for c in cues}
    if 186 not in by_frame or 445 not in by_frame:
        raise ValueError('Required Check In send186 and key445 are absent')
    selected=rng.choice([c['ordinal'] for c in cues if c['canonical_event']['frame']>445],3,replace=False)
    by_ordinal={c['ordinal']:c for c in cues}
    plan=[(by_frame[445],'late',1),(by_frame[186],'late',3),
          (by_ordinal[int(selected[0])],'early',-2),
          (by_ordinal[int(selected[1])],'attenuated',0),
          (by_ordinal[int(selected[2])],'dropped',0)]
    for cue,kind,frames in plan:
        path=base/cue['reference']
        if sha256(path)!=cue['reference_sha256']:raise ValueError('Reference hash mismatch')
        wave=np.load(path,allow_pickle=False);start=cue['clip_start_sample_unclipped']
        delta=round(frames*SR/receipt['fps']);add(output,wave,start,-1)
        if kind in {'late','early'}:add(output,wave,start+delta)
        elif kind=='attenuated':add(output,wave,start,10**(-12/20))
        defects.append({'ordinal':cue['ordinal'],'frame':cue['canonical_event']['frame'],'kind':kind,
                        'expected_sample':cue['event_sample'],'offset_samples':delta,'offset_frames':frames})
    tap=next(c for c in cues if c['canonical_event']['kind']=='tap')
    wave=np.load(base/tap['reference'],allow_pickle=False);sample=round(10.25*SR)
    add(output,wave,sample)
    defects.append({'ordinal':None,'kind':'extra','sample':sample})
    return output,defects


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mp4',type=Path);p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--key',type=Path,required=True)
    p.add_argument('--seed',type=int,default=420186)
    a=p.parse_args()
    if any(f.exists() for f in [a.output,a.output.with_suffix('.flac'),a.output.with_suffix('.m4a'),a.key]):
        p.error('Refusing to overwrite intervention outputs/key')
    r=json.loads(a.receipt.read_text())
    if packet_hash(a.mp4)!=r['picture_packet_sha256']:raise ValueError('Picture mismatch')
    audio=decode(a.mp4)
    if len(audio)!=r['samples']:raise ValueError('Audio span mismatch')
    damaged,defects=intervene(audio,r,a.receipt.parent.parent,a.seed)
    encode(a.output.with_suffix('.flac'),damaged,aac=False)
    encode(a.output.with_suffix('.m4a'),damaged,aac=True,bitrate='192k')
    mux(a.mp4,a.output.with_suffix('.m4a'),a.output)
    write(a.key,{'seed':a.seed,'source_mp4_sha256':sha256(a.mp4),'source':'decoded production MP4; continuous motion preserved',
                 'defects':defects});a.key.chmod(0o600)
    print(f'Wrote {a.output}; six interventions; original video packets preserved')


if __name__=='__main__':main()
