#!/usr/bin/env python3
"""Encode completed lossless picture caches with the validated RGB transport.
Capture engine identity/history stays intact; this is an explicit encode-only
stage. No scene or cached PNG is changed. Original pictures/sidecars are retained.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
PROFILE='full-range-bt709-v1'
FILTER='scale=in_range=full:out_range=full:out_color_matrix=bt709,setparams=range=full:color_primaries=bt709:color_trc=bt709:colorspace=bt709'
METHODS=('remotion','gsap','html','pillow','motion-canvas')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):
 tmp=p.with_name(p.name+f'.tmp-{os.getpid()}');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(p)
def probe(p):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate,duration,pix_fmt,color_range,color_space,color_transfer,color_primaries','-of','json',str(p)]))['streams'][0]
def inventory(folder,count):
 rows=[]
 for n in range(count):
  file=folder/f'{n:06}.png'
  if not file.is_file():raise ValueError('Incomplete lossless cache: '+str(file))
  rows.append(dict(frame=n,bytes=file.stat().st_size,sha256=sha(file)))
 return rows
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,default=ROOT/'delivery-state.json');p.add_argument('--only',nargs='*');p.add_argument('--methods',nargs='*',choices=METHODS,default=METHODS);p.add_argument('--report',type=Path,default=ROOT/'verification/final-encoding/report.json');a=p.parse_args();state=json.loads(a.state.read_text());records=[]
 for identity,entry in state['scenes'].items():
  if a.only and identity not in a.only:continue
  scene_path=ROOT/entry['scene'];scene=json.loads(scene_path.read_text());scene_hash=sha(scene_path);count=round(scene['duration']*scene['fps'])
  for method in a.methods:
   picture=ROOT/'outputs'/identity/(method+'.mp4');sidecar=Path(str(picture)+'.render.json');meta=json.loads(sidecar.read_text())
   if meta.get('sceneSHA256',meta.get('sceneSha256'))!=scene_hash:raise ValueError(identity+'/'+method+' is not the current frozen scene')
   cache=Path(meta['frameDirectory']);before=inventory(cache,count);digest=hashlib.sha256(json.dumps(before,separators=(',',':')).encode()).hexdigest()
   existing=meta.get('encoding',{})
   if existing.get('profile')==PROFILE and existing.get('cacheSHA256')==digest and existing.get('pictureSHA256')==sha(picture):
    print(identity+'/'+method+' already current',flush=True);records.append(dict(reference=identity,method=method,**existing));continue
   backup=ROOT/'outputs'/identity/'iterations'/'encoding-before-full-range';backup.mkdir(parents=True,exist_ok=True);old_hash=sha(picture);old_picture=backup/(method+'-'+old_hash[:12]+'.mp4');old_sidecar=Path(str(old_picture)+'.render.json')
   if not old_picture.exists():
    try:os.link(picture,old_picture)
    except OSError:shutil.copy2(picture,old_picture)
   if not old_sidecar.exists():shutil.copy2(sidecar,old_sidecar)
   target=picture.with_name(picture.stem+f'.encoding-full-{os.getpid()}.mp4');sidecar.unlink();started=time.monotonic()
   try:
    pix='yuv444p' if scene['width']%2 or scene['height']%2 else 'yuv420p'
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-framerate',str(scene['fps']),'-i',str(cache/'%06d.png'),'-frames:v',str(count),'-c:v','libx264','-threads','2','-vf',FILTER,'-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','pc','-crf','16','-pix_fmt',pix,'-movflags','+faststart',str(target)]
    subprocess.run(command,check=True);actual=probe(target);after=inventory(cache,count)
    if before!=after:raise ValueError('Lossless capture cache changed during encoding')
    if int(actual['nb_frames'])!=count or (actual['width'],actual['height'])!=(scene['width'],scene['height']):raise ValueError('Encoded dimensions/frame count mismatch')
    numerator,denominator=map(int,actual['r_frame_rate'].split('/'))
    if abs(numerator/denominator-scene['fps'])>1e-8:raise ValueError('Encoded cadence mismatch')
    for key,wanted in [('color_range','pc'),('color_space','bt709'),('color_transfer','bt709'),('color_primaries','bt709')]:
     if actual.get(key)!=wanted:raise ValueError('Wrong encoded '+key)
    encoded_hash=sha(target);evidence=ROOT/'verification/final-encoding'/identity;evidence.mkdir(parents=True,exist_ok=True);inventory_path=evidence/(method+'-cache.json');write(inventory_path,dict(sceneSHA256=scene_hash,cacheSHA256=digest,frames=before,unchangedAfterEncoding=True))
    record=dict(profile=PROFILE,filter=FILTER,sceneSHA256=scene_hash,cacheSHA256=digest,cacheManifest=str(inventory_path.relative_to(ROOT)),cacheUnchanged=True,pictureSHA256=encoded_hash,previousPictureSHA256=old_hash,previousPicture=str(old_picture.relative_to(ROOT)),encoderScriptSHA256=sha(Path(__file__)),probe=actual,seconds=time.monotonic()-started)
    target.replace(picture);meta.setdefault('encodingHistory',[]).append(meta.get('encoding',dict(profile='previous-renderer-encoding',pictureSHA256=old_hash)));meta['encoding']=record;write(sidecar,meta);records.append(dict(reference=identity,method=method,**record));print(json.dumps(dict(reference=identity,method=method,frames=count,profile=PROFILE,seconds=record['seconds'])),flush=True)
   except BaseException:
    target.unlink(missing_ok=True)
    if not sidecar.exists():write(sidecar,meta)
    raise
 destination=a.report;destination.parent.mkdir(parents=True,exist_ok=True);write(destination,dict(profile=PROFILE,records=records,notice='Only completed lossless caches encoded. Native frames are hashed before/after and unchanged. Capture engine fingerprints remain the actual original fingerprints. Profile validation evidence is verification/encode-range.'))
if __name__=='__main__':main()
