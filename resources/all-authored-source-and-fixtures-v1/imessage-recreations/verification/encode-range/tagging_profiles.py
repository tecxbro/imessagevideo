from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess,json,hashlib,time
R=Path('verification/encode-range');scale='scale=in_range=full:out_range=full:out_color_matrix=bt709';setfull='setparams=range=full:color_primaries=bt709:color_trc=bt709:colorspace=bt709';profiles=[dict(id='full-pc-tagged-remux',remux=True,filter='no pixel conversion; h264_metadata P=1 T=1 M=1 full_range=1',range='pc',crf=16),dict(id='full-pc-setparams',filter=scale+','+setfull,range='pc',crf=16),dict(id='accurate-full-pc-setparams',filter=scale+':flags=bicubic+accurate_rnd+full_chroma_int+full_chroma_inp,'+setfull,range='pc',crf=16),dict(id='current-tv-setparams',filter='scale=in_range=full:out_range=tv:out_color_matrix=bt709,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',range='tv',crf=16),dict(id='full-pc-srgb-setparams',filter=scale+',setparams=range=full:color_primaries=bt709:color_trc=iec61966-2-1:colorspace=bt709',range='pc',crf=16)]
(R/'profiles-tagging.json').write_text(json.dumps(profiles,indent=2))
def job(p):
 out=R/(p['id']+'.mp4');cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-threads','1','-filter_threads','1']
 if p.get('remux'):cmd+=['-i',str(R/'full-pc.mp4'),'-map','0:v:0','-c:v','copy','-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=1']
 else:cmd+=['-framerate','30','-i',str(R/'sequence/%06d.png'),'-frames:v','24','-c:v','libx264','-threads','2','-vf',p['filter'],'-crf',str(p['crf']),'-pix_fmt','yuv420p']
 cmd+=['-colorspace','bt709','-color_primaries','bt709','-color_trc','iec61966-2-1' if 'srgb' in p['id'] else 'bt709','-color_range',p['range'],'-movflags','+faststart',str(out)];t=time.monotonic()
 with (R/(p['id']+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 row={**p,'command':cmd,'seconds':time.monotonic()-t,'returncode':r.returncode,'path':str(out)}
 if r.returncode==0:
  row.update(bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),ffprobe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=codec_name,profile,pix_fmt,width,height,r_frame_rate,avg_frame_rate,color_range,color_space,color_transfer,color_primaries,nb_read_frames,duration','-of','json',str(out)]))['streams'][0]);D=R/'ffmpeg-decoded'/p['id'];D.mkdir(parents=True,exist_ok=True);subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-filter_threads','1','-i',str(out),'-vf','select=eq(n\\,2)+eq(n\\,8)+eq(n\\,14)+eq(n\\,20)','-fps_mode','passthrough','-pix_fmt','rgb24',str(D/'%02d.png')],check=True)
 print(p['id'],r.returncode,round(row['seconds'],3),flush=True);return row
results=[]
with ThreadPoolExecutor(max_workers=2) as pool:
 for f in as_completed([pool.submit(job,p) for p in profiles]):results.append(f.result());(R/'encode-results-tagging.json').write_text(json.dumps(results,indent=2))
if any(q['returncode'] for q in results):raise SystemExit('A tagging profile failed; diagnose its log before retry')
# Metadata isolation: the remux must retain every decoded YUV sample unchanged.
hashes={}
for id in ['full-pc','full-pc-tagged-remux','full-pc-setparams']:
 hashes[id]=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-filter_threads','1','-i',str(R/(id+'.mp4')),'-pix_fmt','yuvj420p','-f','hash','-hash','sha256','-']).decode().strip()
proof=dict(decodedYUVSHA256=hashes,noReencodeRemuxYUVIdentical=hashes['full-pc']==hashes['full-pc-tagged-remux'],setparamsYUVIdentical=hashes['full-pc']==hashes['full-pc-setparams']);(R/'tagging-isolation-proof.json').write_text(json.dumps(proof,indent=2));print(proof)
