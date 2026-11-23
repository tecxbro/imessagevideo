#!/usr/bin/env python3
"""Mux only new validated audio onto the existing silent GSAP pictures."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];AUDIO=ROOT/'audio-recreation'
MAIN=Path('/workspace/sites/message-motion/dist');MEDIA=Path('/workspace/sites/message-motion-originals/dist')
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def packets(path,kind):
 return subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(path),'-map','0:'+kind+':0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def probe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_packets','-show_entries','stream=codec_name,codec_type,width,height,nb_read_packets,time_base,duration_ts,duration,sample_rate,channels:format=duration','-of','json',str(path)]))
def link_atomic(source,target):
 target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_suffix(target.suffix+'.tmp');temp.unlink(missing_ok=True);temp.hardlink_to(source);os.replace(temp,target)
def render(ident):
 folder=AUDIO/'mixes'/ident;report=json.loads((folder/'mix-report.json').read_text())
 if report['validation']['status']!='pass' or report['source_samples_reused'] is not False:raise ValueError('Unaccepted mix: '+ident)
 if any(i['kind']!='new_AI_music_text_only' or not i['path'].startswith('audio-recreation/ai/') for i in report['audio_inputs']):raise ValueError('Unexpected music source')
 for name in ['full_mix.m4a','music.m4a','sfx.m4a']:
  if sha(folder/name)!=report['exports'][name]['sha256']:raise ValueError('Changed accepted audio '+name)
 video=ROOT/'outputs'/ident/'gsap.mp4';sound=folder/'full_mix.m4a';out=AUDIO/'previews'/(ident+'-recreated.mp4');sidecar=out.with_suffix('.json');out.parent.mkdir(exist_ok=True)
 old=json.loads(sidecar.read_text()) if sidecar.exists() else {}
 if not(out.exists() and old.get('video_sha256')==sha(video) and old.get('audio_sha256')==sha(sound) and old.get('output_sha256')==sha(out)):
  temp=out.with_suffix('.tmp.mp4');sidecar.unlink(missing_ok=True)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(video),'-i',str(sound),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-movie_timescale','48000','-y',str(temp)],check=True)
  if packets(video,'v')!=packets(temp,'v'):raise ValueError('Picture packets changed')
  if packets(sound,'a')!=packets(temp,'a'):raise ValueError('AAC packets changed')
  p=probe(temp);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
  if int(v['nb_read_packets'])!=report['picture']['frames']:raise ValueError('Wrong frame count')
  duration=report['picture']['sample_count']/48000
  if abs(float(p['format']['duration'])-duration)>.001:raise ValueError('Duration drift')
  os.replace(temp,out)
  data={'id':ident,'audio_kind':'newly produced instrumental plus original procedural sound effects','source_audio_reused':False,'video_sha256':sha(video),'audio_sha256':sha(sound),'output_sha256':sha(out),'picture_packets_sha256':packets(out,'v'),'audio_packets_sha256':packets(out,'a'),'picture_packets_unchanged':True,'aac_packets_unchanged':True,'picture_frames':report['picture']['frames'],'duration':duration,'probe':p,'mix_report_sha256':sha(folder/'mix-report.json'),'music_request_ids':[i['provenance']['request_id'] for i in report['audio_inputs']]}
  temp=sidecar.with_suffix('.json.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');os.replace(temp,sidecar)
 link_atomic(out,MEDIA/'audio-previews'/ident/'recreated.mp4')
 for source,dest in [('full_mix.m4a','mix.m4a'),('music.m4a','music.m4a'),('sfx.m4a','sfx.m4a')]:link_atomic(folder/source,MAIN/'audio-new'/ident/dest)
 return json.loads(sidecar.read_text())
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--id',nargs='*');parser.add_argument('--ready',action='store_true');args=parser.parse_args()
 all_ids=[v['id'] for v in json.loads((MAIN/'videos.json').read_text())];ids=args.id or all_ids
 if args.ready:ids=[i for i in ids if (AUDIO/'mixes'/i/'mix-report.json').exists()]
 else:
  missing=[i for i in ids if not(AUDIO/'mixes'/i/'mix-report.json').exists()]
  if missing:raise ValueError('Unfinished audio mixes: '+', '.join(missing))
 records=[render(i) for i in ids]
 (AUDIO/'verification/preview-packages.json').write_text(json.dumps({'records':records,'completed':len(records),'total':6,'complete':len(records)==6},indent=2)+'\n')
 print(json.dumps({'packaged':len(records),'ids':ids,'picture_and_audio_packets_unchanged':True}))
if __name__=='__main__':main()
