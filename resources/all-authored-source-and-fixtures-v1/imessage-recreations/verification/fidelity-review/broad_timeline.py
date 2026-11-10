#!/usr/bin/env python3
"""Aligned 1fps source/recreation review, using mapped retained PNGs or ready MP4s."""
from pathlib import Path
import argparse, json, subprocess, shutil, hashlib, html
from fractions import Fraction
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def probe(path):
 p=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(path)],capture_output=True,text=True,check=True)
 return json.loads(p.stdout)['streams'][0]

@lru_cache(maxsize=12)
def reference_pool(path_string):
 path=Path(path_string);digest=hashlib.sha256(path.read_bytes()).hexdigest()
 pool=HERE/'reference-native-cache'/path.parent.name/digest[:16];pool.mkdir(parents=True,exist_ok=True)
 (pool/'provenance.json').write_text(json.dumps({'source':str(path),'source_sha256':digest,'frame_index_semantics':'Original zero-based decoded source frame number. Native RGB PNG, no resize.'},indent=2))
 return pool

def bootstrap_reference_pool():
 for report_path in HERE.glob('broad-*/*/report.json'):
  data=json.loads(report_path.read_text())
  if not data.get('reference') or not data.get('samples'):continue
  source=Path(data['reference'])
  if source.name!='source.mp4':continue
  pool=reference_pool(str(source))
  for sample in data['samples']:
   source_png=report_path.parent.parent/sample['reference'];target=pool/f'{sample["reference_frame"]:06d}.png'
   if source_png.exists() and not target.exists():shutil.copy2(source_png,target)

def extract(path,indices,dest,use_reference_cache=True):
 dest.mkdir(parents=True,exist_ok=True)
 if path.name=='source.mp4' and use_reference_cache:
  pool=reference_pool(str(path));missing=[n for n in indices if not (pool/f'{n:06d}.png').exists()]
  if missing:
   fresh=extract(path,missing,dest/'fresh-source-decode',False)
   for n,p in zip(missing,fresh):shutil.copy2(p,pool/f'{n:06d}.png')
  files=[]
  for i,n in enumerate(indices,1):
   p=dest/f'{i:04d}.png';shutil.copy2(pool/f'{n:06d}.png',p);files.append(p)
  return files
 expr='+'.join(f'eq(n\\,{n})' for n in indices)
 subprocess.run(['ffmpeg','-v','error','-y','-threads','1','-i',str(path),'-vf','select='+expr,'-vsync','0','-frames:v',str(len(indices)),'-threads','1',str(dest/'%04d.png')],check=True)
 files=[dest/f'{i:04d}.png' for i in range(1,len(indices)+1)]
 if not all(p.exists() for p in files):raise RuntimeError(f'{path}: a requested decoded frame is missing')
 return files

def measure(a,b):
 a=np.asarray(a,dtype=np.int16);b=np.asarray(b,dtype=np.int16)
 diff=np.abs(a-b)
 border=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
 bg=np.median(border,axis=0)
 mask=np.maximum(np.max(np.abs(a-bg),axis=2),np.max(np.abs(b-bg),axis=2))>12
 return {'global_mae':float(diff.mean()),'foreground_mae':float(diff[mask].mean()) if mask.any() else 0,
         'changed_pixel_percent':float((diff.max(2)>8).mean()*100),'foreground_coverage_percent':float(mask.mean()*100)},diff

def source_index(identifier,n,fps):
 if identifier=='06-gallery':
  return n if n<1049 else n+181
 return n

def choose_cache():
 mapping=json.loads((ROOT/'outputs/retained-frames/mapping.json').read_text())['mapping'];chosen={}
 for directory,(identifier,method,scene) in mapping.items():
  if 'INCOMPLETE' in scene:continue
  if identifier not in chosen or method=='remotion':chosen[identifier]={'directory':directory,'method':method,'scene':scene}
 return chosen

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['cache','encoded'],default='cache');ap.add_argument('--ids',nargs='*');ap.add_argument('--method',choices=['remotion','gsap','html']);ap.add_argument('--index-only',action='store_true');args=ap.parse_args()
 mode=args.mode;dest=HERE/('broad-'+mode);dest.mkdir(exist_ok=True)
 bootstrap_reference_pool();choices={} if args.index_only else choose_cache();rows=[]
 for identifier,choice in sorted(choices.items()):
  if args.ids and identifier not in args.ids:continue
  ref=ROOT/'references'/identifier/'source.mp4';info=probe(ref);fps=float(Fraction(info['r_frame_rate']))
  outdir=dest/identifier;outdir.mkdir(exist_ok=True);candidate_dir=outdir/'candidate';candidate_dir.mkdir(exist_ok=True)
  if mode=='cache':
   cache=ROOT/'outputs/retained-frames'/choice['directory'];available={int(p.stem):p for p in cache.glob('*.png') if p.stem.isdecimal()}
   if not available:continue
   maxn=max(available);frames=[round(t*fps) for t in range(int(maxn/fps)+1) if round(t*fps) in available]
   for n in frames:shutil.copy2(available[n],candidate_dir/f'{n:06d}.png')
   candidate_path=str(cache);metadata={'state':'partial iteration cache','scene':choice['scene'],'method':choice['method'],'cache_directory':choice['directory'],'available_max_frame':maxn}
  else:
   complete=[]
   for method in ([args.method] if args.method else ['remotion','gsap','html']):
    path=ROOT/'outputs'/identifier/(method+'.mp4');side=Path(str(path)+'.render.json')
    if path.exists() and side.exists():complete.append((path,side,method))
   if not complete:continue
   path,side,method=complete[0];data=json.loads(side.read_text());original_path=path
   payload=path.read_bytes();candidate_sha256=hashlib.sha256(payload).hexdigest()
   snapshot=outdir/f'encoded-input-{method}-{candidate_sha256[:12]}.mp4'
   if not snapshot.exists():snapshot.write_bytes(payload)
   path=snapshot
   try:candidate_info=probe(path)
   except (subprocess.CalledProcessError,KeyError,IndexError,ValueError) as exc:
    error=exc.stderr if isinstance(exc,subprocess.CalledProcessError) else str(exc)
    incomplete=snapshot.with_suffix('.mp4.incomplete')
    snapshot.rename(incomplete)
    (outdir/'readiness.json').write_text(json.dumps({'state':'deferred','reason':'Sidecar existed but copied video was not a complete probeable MP4. Do not treat this as a fidelity result.','original_candidate':str(original_path),'copied_input':str(incomplete),'candidate_sha256':candidate_sha256,'probe_error':error},indent=2))
    print(json.dumps({'id':identifier,'state':'deferred','reason':'incomplete MP4 despite existing sidecar'}),flush=True)
    continue
   duration=float(candidate_info['duration']);frames=[round(t*fps) for t in range(int(duration)+1) if round(t*fps)<int(candidate_info.get('nb_frames',duration*fps))]
   temp=outdir/'candidate-extract';files=extract(path,frames,temp)
   for n,p in zip(frames,files):shutil.copy2(p,candidate_dir/f'{n:06d}.png')
   candidate_path=str(path);metadata={'state':'completed encoded render','method':method,'render_metadata':data,'probe':candidate_info,'original_candidate':str(original_path),'candidate_sha256':candidate_sha256}
  ref_indices=[source_index(identifier,n,fps) for n in frames]
  refs=extract(ref,ref_indices,outdir/'reference');samples=[];panels=[]
  for n,rn,refpath in zip(frames,ref_indices,refs):
   candidate=candidate_dir/f'{n:06d}.png';a=Image.open(refpath).convert('RGB');b=Image.open(candidate).convert('RGB')
   if a.size!=b.size:raise ValueError(f'{identifier} wrong dimensions{a.size}/{b.size}')
   metrics,diff=measure(a,b);thumbs=[]
   for pic in [a,b,Image.fromarray(np.clip(diff*4,0,255).astype('uint8'))]:
    pic.thumbnail((400,300));thumbs.append(pic)
   width=400;height=max(p.height for p in thumbs)+28
   panel=Image.new('RGB',(1200,height),'#edf0f5');draw=ImageDraw.Draw(panel);draw.text((8,8),f'{identifier} source{rn/fps:.3f}s -> output{n/fps:.3f}s MAE{metrics["global_mae"]:.2f}',fill='black')
   for i,pic in enumerate(thumbs):panel.paste(pic,(i*width,28))
   pair=outdir/f'{n:06d}-triptych.jpg';panel.save(pair);panels.append(panel)
   samples.append({'output_frame':n,'reference_frame':rn,'output_time':n/fps,'reference_time':rn/fps,'reference':str(refpath.relative_to(dest)),'candidate':str(candidate.relative_to(dest)),'triptych':str(pair.relative_to(dest)),'metrics':metrics})
  for start in range(0,len(panels),8):
   batch=panels[start:start+8];sheet=Image.new('RGB',(1200,sum(p.height for p in batch)),'white');y=0
   for p in batch:sheet.paste(p,(0,y));y+=p.height
   sheet.save(outdir/f'contact-{start//8+1}.jpg')
  report={'id':identifier,'mode':mode,'candidate':candidate_path,'reference':str(ref),'metadata':metadata,'scope':'1fps exact native frame samples, not every-frame verification. Cache mode snapshots are partial iteration states, not final rendered outputs. Metrics include no SSIM; foreground is border-median union threshold12, no dilation.','samples':samples}
  (outdir/'report.json').write_text(json.dumps(report,indent=2));rows.append(report)
  (outdir/'readiness.json').write_text(json.dumps({'state':'reviewed','mode':mode,'samples':len(samples),'candidate':candidate_path},indent=2))
  print(json.dumps({'id':identifier,'samples':len(samples),'last_output_time':samples[-1]['output_time'],'state':metadata['state'],'largest_mae':sorted([{'t':s['output_time'],'mae':s['metrics']['global_mae']} for s in samples],key=lambda x:x['mae'],reverse=True)[:5]}),flush=True)
 current_ids={r['id'] for r in rows}
 for previous in dest.glob('*/report.json'):
  data=json.loads(previous.read_text())
  if data.get('id') not in current_ids:rows.append(data)
 rows.sort(key=lambda r:r['id'])
 sections=[]
 for readiness in dest.glob('*/readiness.json'):
  state=json.loads(readiness.read_text())
  if state.get('state')=='deferred':sections.append('<h2>'+readiness.parent.name+' — deferred</h2><p>'+html.escape(state['reason'])+'</p>')
 for report in rows:
  sections.append('<h2>'+report['id']+'</h2><p>'+html.escape(report['metadata']['state'])+' · '+html.escape(str(report['metadata'].get('scene',report['metadata'].get('method',''))))+'</p>')
  for s in report['samples']:
   sections.append(f'<article><p>Source{s["reference_time"]:.3f}s → output{s["output_time"]:.3f}s · MAE{s["metrics"]["global_mae"]:.3f} · foregroundMAE{s["metrics"]["foreground_mae"]:.3f}</p><a href="{s["reference"]}">Native reference</a> · <a href="{s["candidate"]}">Native candidate</a><img loading="lazy" src="{s["triptych"]}"></article>')
 page='<!doctype html><meta charset="utf-8"><title>Broader timeline QA</title><style>body{max-width:1450px;margin:auto;padding:24px;font:15px system-ui;background:#f3f5f8}article{background:white;padding:16px;margin:20px 0;border-radius:10px}img{width:100%}p{line-height:1.6}</style><h1>Broader timeline QA: '+mode+'</h1><p>Aligned native samples at1fps. Left reference, middle candidate, right absolute difference amplified4×. Partial caches are iteration evidence, not completion or full timeline fidelity claims.</p>'+''.join(sections)
 (dest/'index.html').write_text(page);(dest/'coverage.json').write_text(json.dumps({'mode':mode,'reports':[{'id':r['id'],'samples':len(r['samples']),'first':r['samples'][0]['output_time'],'last':r['samples'][-1]['output_time'],'metadata':r['metadata']} for r in rows]},indent=2))

if __name__=='__main__':main()
