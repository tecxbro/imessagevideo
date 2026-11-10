from pathlib import Path
import importlib.util,json,os
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('compare',ROOT/'verification/compare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);source=ROOT/'references/02-danieltian/source.mp4';frames=list(range(748,791))+list(range(802,871))+list(range(904,941));out=R/'source-native'
if out.exists():assert not any(out.iterdir())
out.mkdir(exist_ok=True)
# Three exact ranges avoid a deeply nested149-term expression in AVExpr.
m.command(['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(source),'-vf',r'select=between(n\,748\,790)+between(n\,802\,870)+between(n\,904\,940)','-fps_mode','passthrough','-frames:v',str(len(frames)),'-pix_fmt','rgb24','-c:v','png','-threads','1',str(out/'%06d.png')])
paths={f:out/f'{i+1:06d}.png'for i,f in enumerate(frames)}
assert all(p.exists()for p in paths.values())
mapping={} 
for f,p in paths.items():
 target=out/f'source-{f:04d}.png';p.rename(target);mapping[str(f)]=str(target)
baseline=R/'baseline-v14-native';baseline.mkdir(exist_ok=True)
for f in frames:
 src=ROOT/'outputs/02-danieltian/frames-gsap'/f'{f:06d}.png';dst=baseline/src.name
 if not dst.exists():os.link(src,dst)
(R/'source-map.json').write_text(json.dumps(mapping,indent=2));print('acquired native',len(frames),'source frames and preserved nativeV14 controls',flush=True)
