"""Repair declared UI defects using delivery, receipt, and findings, never a key."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from check_cues import SR, add, decode, packet_hash
from build_treatments import mux, write
from render_mix import encode, sha256


def patch_regions(audio, expected, intervals, fade=240):
    if audio.shape != expected.shape:
        raise ValueError('PCM spans differ')
    intervals=sorted((max(0,int(lo)),min(len(audio),int(hi))) for lo,hi in intervals if hi>lo)
    merged=[]
    for lo,hi in intervals:
        if merged and lo<=merged[-1][1]:
            merged[-1][1]=max(merged[-1][1],hi)
        else:
            merged.append([lo,hi])
    output=audio.copy()
    for lo,hi in merged:
        weight=np.ones(hi-lo)
        edge=min(fade,len(weight)//2)
        if edge:
            ramp=np.sin(np.linspace(0,np.pi/2,edge))**2
            weight[:edge]=ramp;weight[-edge:]=ramp[::-1]
        output[lo:hi]=audio[lo:hi]*(1-weight[:,None])+expected[lo:hi]*weight[:,None]
    return output,merged


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mp4',type=Path)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--findings',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    outputs=[args.output,args.output.with_suffix('.flac'),args.output.with_suffix('.m4a'),args.output.with_suffix('.repair.json')]
    if any(p.exists() for p in outputs):
        parser.error('Refusing to overwrite repair products')
    receipt=json.loads(args.receipt.read_text());findings=json.loads(args.findings.read_text())
    packet=packet_hash(args.mp4)
    if packet!=receipt['picture_packet_sha256'] or not findings['picture_match'] or findings['picture_packet_sha256']!=packet:
        raise ValueError('Picture/findings identity mismatch')
    if receipt.get('background_reference'):
        raise ValueError('UI-only repair requires a receipt without continuous background')
    audio=decode(args.mp4)
    if len(audio)!=receipt['samples']:
        raise ValueError('Decoded span differs from receipt')
    expected=np.zeros_like(audio);waves={};cues={}
    for c in receipt['cues']:
        path=args.receipt.parent.parent/c['reference']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=c['reference_sha256']:
            raise ValueError('Cue reference hash mismatch')
        wave=np.load(path,allow_pickle=False)
        waves[c['ordinal']]=wave;cues[c['ordinal']]=c
        add(expected,wave,c['clip_start_sample_unclipped'])
    regions=[];actions=[];padding=960
    for row in findings['cues']:
        if not row['flags']:
            continue
        c=cues[row['ordinal']];start=c['clip_start_sample_unclipped'];length=len(waves[row['ordinal']])
        regions.append((start-padding,start+length+padding))
        if 'missing' not in row['flags']:
            actual=start+row['offset_samples']
            regions.append((actual-padding,actual+length+padding))
        actions.append({'ordinal':row['ordinal'],'flags':row['flags'],'scheduled_start':start,
                        'observed_offset_samples':row['offset_samples'],
                        'action':'Replace scheduled and confidently observed regions with all expected overlapping references; do not erase a low-confidence missing-cue candidate elsewhere'})
    residual=audio-expected;block=240
    padded=np.pad(residual,((0,(-len(residual))%block),(0,0)))
    rms=np.sqrt(np.mean(padded.reshape(-1,block,2)**2,axis=(1,2)))
    active=np.flatnonzero(rms>.003)
    groups=np.split(active,np.flatnonzero(np.diff(active)>10)+1) if len(active) else []
    for extra in findings['extras']:
        matched=[g for g in groups if g[0]*block-4800<=extra['sample']<=(g[-1]+1)*block+4800]
        if not matched:
            raise ValueError('Extra finding cannot be located in decoded residual')
        group=min(matched,key=lambda g:abs(g[0]*block-extra['sample']))
        interval=(int(group[0]*block-padding),int((group[-1]+1)*block+padding))
        regions.append(interval);actions.append({'extra_sample':extra['sample'],'residual_region':interval,'action':'Remove transient by restoring expected PCM over detected residual extent'})
    repaired,merged=patch_regions(audio,expected,regions)
    encode(outputs[1],repaired,aac=False)
    encode(outputs[2],repaired,aac=True,bitrate='192k')
    mux(args.mp4,outputs[2],args.output)
    write(outputs[3],{'input_mp4_sha256':sha256(args.mp4),'receipt_sha256':sha256(args.receipt),
                     'findings_sha256':sha256(args.findings),'key_read':False,'clean_stem_read':False,
                     'actions':actions,'replaced_regions_samples':merged,'crossfade_samples':240,
                     'outside_regions_policy':'Preserve original decoded AAC PCM; no whole-track replacement',
                     'reference_policy':'All scheduled reference cues are included inside repaired regions to preserve overlaps',
                     'picture_packet_sha256':packet,'output_picture_packet_sha256':packet_hash(args.output),
                     'repair_flac_sha256':sha256(outputs[1]),'output_mp4_sha256':sha256(args.output),
                     'build_source_sha256':sha256(Path(__file__))})
    print(f'Repaired {len(actions)} findings in {len(merged)} regions; video packets unchanged; no key or clean stem read')


if __name__=='__main__':
    main()
