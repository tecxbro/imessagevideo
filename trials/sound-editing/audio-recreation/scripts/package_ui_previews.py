#!/usr/bin/env python3
"""Packet-preserving UI-only and quiet-music preview packaging."""
from pathlib import Path
import json,hashlib,subprocess,os,argparse
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'audio-recreation';MAIN=ROOT.parent/'sites/message-motion/dist';MEDIA=ROOT.parent/'sites/message-motion-originals/dist'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def packets(p,k):return subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(p),'-map','0:'+k+':0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def export_info(value):return value['file'] if isinstance(value.get('file'),dict) else value
def link(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);tmp=dst.with_suffix(dst.suffix+'.tmp');tmp.unlink(missing_ok=True);tmp.hardlink_to(src);os.replace(tmp,dst)
def render(ident):
 folder=A/'ui-mixes'/ident;report=json.loads((folder/'report.json').read_text());assert report['status']=='pass' and report['validation']['status']=='pass' and report['reference_film_samples_reused'] is False
 video=ROOT/'outputs'/ident/'gsap.mp4';records=[]
 for variant,name in [('ui','ui_preview.m4a'),('recreated','full_mix.m4a')]:
  audio=folder/name;assert sha(audio)==export_info(report['exports'][name])['sha256']
  out=A/'ui-previews'/(ident+'-'+variant+'.mp4');out.parent.mkdir(exist_ok=True);sidecar=out.with_suffix('.json')
  prev=json.loads(sidecar.read_text()) if sidecar.exists() else {}
  if not(out.exists() and prev.get('video_sha256')==sha(video) and prev.get('audio_sha256')==sha(audio) and prev.get('output_sha256')==sha(out)):
   tmp=out.with_suffix('.tmp.mp4');sidecar.unlink(missing_ok=True)
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(video),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-movie_timescale','48000','-y',str(tmp)],check=True)
   vp=packets(video,'v');ap=packets(audio,'a');assert vp==packets(tmp,'v') and ap==packets(tmp,'a')
   info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_packets','-show_entries','stream=codec_type,codec_name,nb_read_packets,duration_ts,time_base:format=duration','-of','json',str(tmp)]))
   v=next(x for x in info['streams'] if x['codec_type']=='video');assert int(v['nb_read_packets'])==report['picture']['frames']
   assert abs(float(info['format']['duration'])-report['samples']/48000)<.001
   os.replace(tmp,out)
   prev={'id':ident,'variant':variant,'video_sha256':sha(video),'audio_sha256':sha(audio),'output_sha256':sha(out),'video_packet_sha256':vp,'aac_packet_sha256':ap,'picture_and_aac_packets_unchanged':True,'reference_audio_reused':False,'probe':info}
  prev['ui_report_sha256']=sha(folder/'report.json');prev['visual_cues']=report['canonical_event_count'];prev['audible_cues']=report['rendered_event_count'];prev['audio_audition_boost']=variant=='ui'
  sidecar.write_text(json.dumps(prev,indent=2)+'\n');link(out,MEDIA/'audio-previews'/ident/(variant+'.mp4'));records.append(prev)
 for source,dest in [('ui.m4a','sfx.m4a'),('music.m4a','music.m4a'),('full_mix.m4a','mix.m4a')]:
  assert sha(folder/source)==export_info(report['exports'][source])['sha256'];link(folder/source,MAIN/'audio-new'/ident/dest)
 return records
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ready',action='store_true');args=p.parse_args();ids=[v['id'] for v in json.loads((MAIN/'videos.json').read_text())]
 if args.ready:ids=[i for i in ids if(A/'ui-mixes'/i/'report.json').exists()]
 records=[]
 for i in ids:records.extend(render(i))
 result={'records':records,'completed':len(records),'total':12,'complete':len(records)==12}
 (A/'verification/ui-preview-packages.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'previews':len(records),'complete':result['complete'],'unchanged_picture_and_AAC':True}))
