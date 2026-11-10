from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess,json,time,hashlib
R=Path('verification/encode-range');base='scale=in_range=full:out_color_matrix=bt709:';flags='flags=bicubic+accurate_rnd+full_chroma_int+full_chroma_inp';z='format=gbrp,zscale=matrixin=gbr:matrix=709:rangein=full:primariesin=709:primaries=709:transferin=709:transfer=709:dither=none:'
profiles=[dict(id='current-tv',filter='scale=out_color_matrix=bt709',range='tv',crf=16),dict(id='explicit-tv',filter=base+'out_range=tv',range='tv',crf=16),dict(id='accurate-tv',filter=base+'out_range=tv:'+flags,range='tv',crf=16),dict(id='full-pc',filter=base+'out_range=full',range='pc',crf=16),dict(id='accurate-full-pc',filter=base+'out_range=full:'+flags,range='pc',crf=16),dict(id='zscale-tv',filter=z+'range=limited,format=yuv420p',range='tv',crf=16),dict(id='zscale-pc',filter=z+'range=full,format=yuv420p',range='pc',crf=16),dict(id='lossless-tv-control',filter=base+'out_range=tv',range='tv',crf=0,control=True),dict(id='lossless-pc-control',filter=base+'out_range=full',range='pc',crf=0,control=True)]
(R/'profiles.json').write_text(json.dumps(profiles,indent=2))
def job(p):
 out=R/(p['id']+'.mp4');cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-threads','1','-filter_threads','1','-framerate','30','-i',str(R/'sequence/%06d.png'),'-frames:v','24','-c:v','libx264','-threads','2','-vf',p['filter'],'-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range',p['range'],'-crf',str(p['crf']),'-pix_fmt','yuv420p','-movflags','+faststart',str(out)];start=time.monotonic()
 with (R/(p['id']+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 report={**p,'command':cmd,'returncode':r.returncode,'seconds':time.monotonic()-start,'path':str(out)}
 if r.returncode==0:
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=codec_name,profile,pix_fmt,width,height,r_frame_rate,avg_frame_rate,color_range,color_space,color_transfer,color_primaries,nb_read_frames,duration','-of','json',str(out)]));report.update(bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),ffprobe=probe['streams'][0]);D=R/'ffmpeg-decoded'/p['id'];D.mkdir(parents=True,exist_ok=True)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-i',str(out),'-vf','select=eq(n\\,2)+eq(n\\,8)+eq(n\\,14)+eq(n\\,20)','-fps_mode','passthrough','-pix_fmt','rgb24',str(D/'%02d.png')],check=True)
 print(p['id'],r.returncode,round(report['seconds'],3),flush=True);return report
results=[]
with ThreadPoolExecutor(max_workers=2) as pool:
 for f in as_completed([pool.submit(job,p) for p in profiles]):results.append(f.result());(R/'encode-results.json').write_text(json.dumps(results,indent=2))
if any(x['returncode'] for x in results):raise SystemExit('A profile failed; inspect its log before any retry')
