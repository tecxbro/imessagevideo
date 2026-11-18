"""Rehydrate omitted references and named deliveries from committed receipts."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from check_cues import add, decode
from build_treatments import mux, write
from render_mix import encode, sha256
import render_ui

BASE=Path(__file__).resolve().parents[1]
REPO=BASE.parents[1]
sys.path.insert(0,str(BASE/'checkin/tools'))
from build_scores import motion_texture


def freeze(path,wave,expected):
    import io,hashlib
    stream=io.BytesIO();np.save(stream,wave)
    if hashlib.sha256(stream.getvalue()).hexdigest()!=expected:
        raise ValueError(f'Recreated reference differs from pinned SHA: {path}')
    if path.exists():
        if sha256(path)!=expected:
            raise ValueError(f'Existing reference differs: {path}')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(stream.getvalue())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--references-only',action='store_true')
    a=p.parse_args()
    paths=[BASE/'references/receipt.json']+sorted((BASE/'blind').glob('*/receipts/*.json'))+sorted((BASE/'checkin/blind').glob('*/receipts/*.json'))
    count=0
    for path in paths:
        r=json.loads(path.read_text());base=path.parent.parent
        checkin='checkin' in path.parts
        schedule,_=render_ui.load_schedule('checkin' if checkin else '04-poke')
        for c in r['cues']:
            wave,_=render_ui.render_event(c['canonical_event'],schedule,c['ordinal'])
            wave*=10**(c.get('treatment_gain_db',0)/20)
            wave*=10**(r.get('comparison_gain_db',0)/20)
            freeze(base/c['reference'],wave,c['reference_sha256']);count+=1
        if 'background_reference' in r:
            if checkin:
                background=np.zeros((r['samples'],2));background[336000:672000]=motion_texture(336000)
            else:
                background=decode(REPO/'resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/mixes/04-poke/music.flac')*.1
                background[[0,-1]]=0
            background*=10**(r.get('comparison_gain_db',0)/20)
            ref=r['background_reference'];freeze(base/ref['reference'],background,ref['reference_sha256'])
    if not a.references_only:
        for root in [BASE/'blind',BASE/'checkin/blind']:
            for folder in sorted(root.glob('T-*')):
                r=json.loads((folder/'receipts/production.json').read_text())
                ui=np.zeros((r['samples'],2));motion=np.zeros_like(ui);music=np.zeros_like(ui)
                for c in r['cues']:
                    add(ui,np.load(folder/c['reference'],allow_pickle=False),c['clip_start_sample_unclipped'])
                if root==BASE/'checkin/blind':
                    ui=decode(BASE/'audio-recreation/ui-mixes/checkin/no-music/ui.flac')
                elif len(r['cues'])==34:
                    ui=decode(REPO/'resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/ui-mixes/04-poke/ui.flac')
                ui[[0,-1]]=0
                if 'background_reference' in r:
                    background=np.load(folder/r['background_reference']['reference'],allow_pickle=False)
                    if root==BASE/'checkin/blind':motion=background
                    else:music=background
                full=ui+music+motion
                stems=[('ui',ui),('music',music),('full_mix',full)]
                if root==BASE/'checkin/blind':stems.append(('motion',motion))
                for name,wave in stems:
                    if not (folder/f'{name}.flac').exists():encode(folder/f'{name}.flac',wave,aac=False)
                picture=BASE/'checkin/v1-first-export.mp4' if root==BASE/'checkin/blind' else REPO/'projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/gsap.mp4'
                for mode in ['production','comparison']:
                    receipt=json.loads((folder/f'receipts/{mode}.json').read_text())
                    gain=10**(receipt.get('comparison_gain_db',0)/20)
                    if not (folder/f'{mode}.m4a').exists():encode(folder/f'{mode}.m4a',full*gain,aac=True,bitrate='192k')
                    if not (folder/f'{mode}.mp4').exists():mux(picture,folder/f'{mode}.m4a',folder/f'{mode}.mp4')
    print(f'Validated/restored {count} pinned cue references; named exports '+('not requested' if a.references_only else 'restored when missing'))


if __name__=='__main__':main()
