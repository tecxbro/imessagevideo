#!/usr/bin/env python3
"""Cold-build a complete frozen example using its genuine shared adapters.

This convenience runner is new; canonical scene and underlying renderer code
are the accepted authored implementation, not stand-alone per-format projects.
"""
from pathlib import Path
import argparse,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
METHODS=['remotion','gsap','html','pillow','motion-canvas']
def commands(identity,method,checkpoint=None):
    state=json.loads((ROOT/'delivery-state.json').read_text());entry=state['scenes'][identity];scene=ROOT/entry['scene']
    if not scene.is_file():raise FileNotFoundError('Fetch the complete example pack first: '+str(scene))
    suffix='.png' if checkpoint is not None else '.mp4';output=ROOT/'outputs'/identity/(method+suffix);cache=ROOT/'outputs'/identity/('frames-'+method)
    if method=='pillow':cmd=[sys.executable,str(ROOT/'engines/render_pillow.py'),'--scene',str(scene),'--out',str(output),'--aa','1']
    elif method=='motion-canvas':cmd=['node',str(ROOT/'engines/render_motion_canvas.mjs'),'--scene',str(scene),'--out',str(output)]
    else:cmd=['node',str(ROOT/'engines/render.mjs'),'--method',method,'--scene',str(scene),'--out',str(output)]
    if checkpoint is not None:return [cmd+['--frame',str(checkpoint)]]
    result=[cmd+['--frames-dir',str(cache)]]
    if method=='pillow':
        overrides=json.loads((ROOT/'render-overrides.json').read_text())['pillow']['overrides'].get(identity,[])
        for item in overrides:result.append(cmd[:-1]+[str(item['antialias']),'--frames-dir',str(cache),'--ranges',','.join(f'{a}:{b}' for a,b in item['ranges'])])
    result.append([sys.executable,str(ROOT/'scripts/final_encode.py'),'--state',str(ROOT/'delivery-state.json'),'--only',identity,'--methods',method,'--report',str(ROOT/'verification/new-encoding'/f'{identity}-{method}.json')])
    mux=[sys.executable,str(ROOT/'scripts/add_reference_audio.py'),str(ROOT/'references'/identity/'source.mp4'),str(output),str(ROOT/'new-deliverables'/identity/(method+'.mp4'))]
    if identity=='06-gallery':mux+=['--segments',str(ROOT/'references/06-gallery/segments.json')]
    result.append(mux);return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--example',required=True);p.add_argument('--method',choices=METHODS+['all'],default='gsap');p.add_argument('--checkpoint',type=int);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    methods=METHODS if a.method=='all' else [a.method]
    for method in methods:
        for cmd in commands(a.example,method,a.checkpoint):
            print(json.dumps({'method':method,'argv':cmd}),flush=True)
            if not a.dry_run:subprocess.run(cmd,cwd=ROOT,check=True)
if __name__=='__main__':main()
