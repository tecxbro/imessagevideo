#!/usr/bin/env python3
"""Validate frozen scene revisions and prepare the final reference-audio videos."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
METHODS=('remotion','gsap','html','pillow','motion-canvas')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def picture_packets(path):
    return subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(path),
        '-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--state',type=Path,default=ROOT/'delivery-state.json')
    p.add_argument('--mux',action='store_true')
    p.add_argument('--only',nargs='*')
    p.add_argument('--report',type=Path,default=ROOT/'verification/delivery-validation.json')
    a=p.parse_args()
    state=json.loads(a.state.read_text());records=[];errors=[]
    for identity,entry in state['scenes'].items():
        if a.only and identity not in a.only:continue
        scene_path=ROOT/entry['scene'];scene=json.loads(scene_path.read_text())
        expected_hash=sha(scene_path)
        expected_frames=round(scene['duration']*scene['fps'])
        for method in METHODS:
            video=ROOT/'outputs'/identity/(method+'.mp4')
            metadata=Path(str(video)+'.render.json')
            label=identity+'/'+method
            if not video.exists() or not metadata.exists():
                errors.append(label+': missing completed picture/metadata');continue
            meta=json.loads(metadata.read_text())
            actual_hash=meta.get('sceneSHA256',meta.get('sceneSha256'))
            if actual_hash!=expected_hash:
                errors.append(label+': stale scene hash');continue
            if meta.get('knownIssues'):
                errors.append(label+': renderer reports known issues');continue
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
                '-show_entries','stream=width,height,nb_frames,r_frame_rate,duration,color_range,color_space,color_transfer,color_primaries','-of','json',str(video)]))['streams'][0]
            issues=[]
            if (probe['width'],probe['height'])!=(scene['width'],scene['height']):issues.append('dimensions')
            if int(probe.get('nb_frames',-1))!=expected_frames:issues.append('frame count')
            numerator,denominator=map(int,probe['r_frame_rate'].split('/'))
            if abs(numerator/denominator-scene['fps'])>1e-8:issues.append('cadence')
            if abs(float(probe['duration'])-expected_frames/scene['fps'])>1/scene['fps']/4:issues.append('duration')
            if state.get('encoding_profile'):
                encoding=meta.get('encoding',{})
                if encoding.get('profile')!=state['encoding_profile'] or encoding.get('pictureSHA256')!=sha(video):issues.append('encoding provenance')
                for key,wanted in [('color_range','pc'),('color_space','bt709'),('color_transfer','bt709'),('color_primaries','bt709')]:
                    if probe.get(key)!=wanted:issues.append(key)
            if issues:
                errors.append(label+': wrong '+', '.join(issues));continue
            record={'reference':identity,'method':method,'scene':entry['scene'],
                'sceneSHA256':expected_hash,'picture':str(video.relative_to(ROOT)),
                'pictureSHA256':sha(video),'probe':probe}
            if a.mux:
                output=ROOT/'deliverables'/identity/(method+'.mp4')
                sidecar=output.with_suffix('.audio.json')
                current=json.loads(sidecar.read_text()) if sidecar.exists() else {}
                if not output.exists() or current.get('picture_sha256')!=record['pictureSHA256']:
                    command=[sys.executable,str(ROOT/'scripts/add_reference_audio.py'),
                        str(ROOT/'references'/identity/'source.mp4'),str(video),str(output)]
                    segments=ROOT/'references'/identity/'segments.json'
                    if identity=='06-gallery':command+=['--segments',str(segments)]
                    subprocess.run(command,check=True)
                output_probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(output)]))['streams']
                pictures=[s for s in output_probe if s['codec_type']=='video']
                soundtracks=[s for s in output_probe if s['codec_type']=='audio']
                if len(pictures)!=1 or len(soundtracks)!=1 or soundtracks[0]['codec_name']!='aac':
                    errors.append(label+': unexpected muxed streams');continue
                muxed=pictures[0]
                if int(muxed.get('nb_frames',-1))!=expected_frames or muxed['r_frame_rate']!=probe['r_frame_rate']:
                    errors.append(label+': mux changed picture cadence or count');continue
                if any(muxed.get(key)!=probe.get(key) for key in ['width','height','color_range','color_space','color_transfer','color_primaries']):
                    errors.append(label+': mux changed picture dimensions or color tags');continue
                original_packets=picture_packets(video)
                if original_packets!=picture_packets(output):
                    errors.append(label+': mux changed H.264 picture packets');continue
                record['with_reference_audio']=str(output.relative_to(ROOT))
                record['muxedSHA256']=sha(output)
                record['picturePacketsUnchanged']=True
                record['picturePacketSHA256']=original_packets
                record['audioProbe']={key:soundtracks[0].get(key) for key in ['codec_name','sample_rate','channels','duration','nb_frames']}
            records.append(record)
    result={'validated':len(records),'expected':len(a.only or state['scenes'])*len(METHODS),
        'errors':errors,'videos':records}
    destination=a.report
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=destination.with_name(destination.name+f'.tmp-{os.getpid()}')
    temporary.write_text(json.dumps(result,indent=2));temporary.replace(destination)
    print(json.dumps({'validated':result['validated'],'expected':result['expected'],'errors':errors},indent=2))
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())
