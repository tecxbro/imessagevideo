"""Render visually verified v3 cues and restrained T-M8-style motion texture."""
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

BASE=Path(__file__).resolve().parents[1]
TRIAL=BASE.parent
sys.path.insert(0,str(TRIAL/'tools'))
sys.path.insert(0,str(TRIAL/'audio-recreation/scripts'))
sys.path.insert(0,str(TRIAL/'checkin/tools'))
from check_cues import PACKET_HASH_METHOD,decode,packet_hash
from render_mix import encode,loudness,sha256
from build_treatments import write
from build_scores import motion_texture
import render_ui

EXPECTED='9dc4a812480d778c4b453f1eeb8d87e19569683ea2f4d78e8015b9f2f9952d9e'
KINDS={'receive':'message_arrival','tap':'tap','send':'message_send','type char':'typing','arrival':'cart_update','backspace':'delete'}
PEAKS={'message_arrival':-18,'tap':-21,'message_send':-17,'typing':-24,'cart_update':-19,'delete':-25}


def canonical(supplied,picture_hash):
    if supplied['fps']!=30 or supplied['frames']!=720:
        raise ValueError('Expected native30fps720-frame director event list')
    events=[]
    for frame,rows in supplied['events'].items():
        for row in rows:
            if int(frame)!=row['frame'] or not 0<=row['frame']<720:
                raise ValueError('Invalid native frame')
            kind=KINDS[row['action']]
            event={'frame':row['frame'],'kind':kind,'time':row['frame']/30,
                   'sample_offset_48000':row['frame']*1600,'event_id':f'checkin-v3:{kind}:{frame}',
                   'audio':{'target_peak_dbfs':PEAKS[kind]},'director_action':row,
                   'evidence':[f'evidence/frame-{row["frame"]+d:03}.png' for d in [-1,0,1]],
                   'verification':'Native before/at/after frames visually inspected; listed impact confirmed'}
            if kind in {'typing','delete'}:
                if row.get('char','').isspace():raise ValueError('Invisible space cannot be a sound cue')
                event.update(role='human',delta_count=1)
            events.append(event)
    events.sort(key=lambda e:e['frame'])
    if len({e['frame'] for e in events})!=len(events):raise ValueError('Duplicate/shared impact must be coalesced')
    return {'id':'checkin-v3','frames':720,'fps_numerator':30,'fps_denominator':1,'sample_count':1152000,
            'sample_rate':48000,'duration':24,'picture_file_sha256':picture_hash,
            'events':events,'exclusions':[
                {'range_inclusive':[210,299],'reason':'Retimed walk; continuous motion texture only, zero UI cues'},
                {'reason':'Trailing spaces and invisible-space deletions excluded; source list already contains visible glyph changes only'},
                {'reason':'Menu/card appearances, camera reveals, locator/clock/countdown changes and end-card graphics stay silent'},
                {'frames':[186,570],'reason':'One send per action; no separate tap or backspace for composer clear'},
                {'frames':[460],'reason':'One shared semantic arrival confirmation, not one cue per phone'}]}


def main():
    if (BASE/'final.mp4').exists():raise SystemExit('Refusing to overwrite completed v3 score')
    picture=BASE/'v3-final.mp4'
    actual=sha256(picture)
    if actual!=EXPECTED:raise ValueError('Director picture whole-file SHA mismatch')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(picture)]))
    stream=probe['streams'][0]
    if (stream['width'],stream['height'],stream['r_frame_rate'],int(stream['nb_frames']))!=(1920,1080,'30/1',720):
        raise ValueError('Director picture format differs from brief')
    supplied=json.loads((BASE/'director-events.json').read_text())
    schedule=canonical(supplied,actual);write(BASE/'canonical-cues.json',schedule)
    ui,rendered=render_ui.build_ui(schedule)
    if np.max(np.abs(ui))>=10**(-1.8/20):raise ValueError('UI requires additional peak guard')
    encode(BASE/'ui.flac',ui,aac=False)
    write(BASE/'ui-render.json',{'status':'pass','no_music':True,'samples':len(ui),'rendered_events':len(rendered),
                               'common_peak_guard_gain_db':0,'events':rendered})
    ui=decode(BASE/'ui.flac')
    motion=np.zeros_like(ui);motion[336000:480000]=motion_texture(144000)
    music=np.zeros_like(ui);full=ui+motion
    for name,wave in [('music',music),('motion',motion),('full_mix',full)]:encode(BASE/f'{name}.flac',wave,aac=False)
    receipt={'picture_file_sha256':actual,'picture_file_hash_method':'SHA256 of every byte of director input MP4; container included, not decoded frames',
             'picture_packet_sha256':packet_hash(picture),'picture_packet_hash_method':PACKET_HASH_METHOD,
             'schedule_sha256':sha256(BASE/'canonical-cues.json'),'fps':30,'fps_numerator':30,'fps_denominator':1,
             'samples':1152000,'sample_rate':48000,'cues':[]}
    for ordinal,event in enumerate(schedule['events']):
        wave,c=render_ui.render_event(event,schedule,ordinal)
        path=BASE/'references'/f'cue-{ordinal:02}.npy';np.save(path,wave)
        c.update(reference='references/'+path.name,reference_sha256=sha256(path))
        receipt['cues'].append(c)
    reference=BASE/'references/motion.npy';np.save(reference,motion)
    receipt['background_reference']={'reference':'references/motion.npy','reference_sha256':sha256(reference),
        'alignment_sample':0,'role':'Independent expected procedural motion reference, generated from source/seed; not decoded from production stem'}
    write(BASE/'receipts/production.json',receipt)
    encode(BASE/'final.m4a',full,aac=True,bitrate='192k')
    subprocess.run(['ffmpeg','-v','error','-i',str(picture),'-i',str(BASE/'final.m4a'),'-map','0:v:0','-map','1:a:0',
                    '-c:v','copy','-c:a','copy','-movflags','+faststart','-movie_timescale','48000','-n',str(BASE/'final.mp4')],check=True)
    output_packet=packet_hash(BASE/'final.mp4')
    if output_packet!=receipt['picture_packet_sha256']:raise ValueError('Video packet identity changed')
    error=float(np.max(np.abs(decode(BASE/'ui.flac')+decode(BASE/'music.flac')+decode(BASE/'motion.flac')-decode(BASE/'full_mix.flac'))))
    if error>2e-6:raise ValueError('Independent stems do not add')
    write(BASE/'cue-impacts.json',[{'ordinal':c['ordinal'],'frame':c['canonical_event']['frame'],'sample':c['event_sample'],
         'clip_start_sample':c['clip_start_sample_unclipped'],'alignment_offset_samples':c['clip_alignment_offset_samples'],
         'source':c['source'],'target_peak_dbfs':c['target_peak_dbfs'],'pitch':c['pitch'],'pan':c['pan'],
         'reference_sha256':c['reference_sha256']} for c in receipt['cues']])
    library=TRIAL/'audio-recreation/library/manifest.json'
    manifest={'picture':{'file_sha256':actual,'file_hash_method':receipt['picture_file_hash_method'],
                        'packet_sha256':output_packet,'packet_hash_method':PACKET_HASH_METHOD,'decoded_frame_hash':None},
              'director_events_sha256':sha256(BASE/'director-events.json'),'frame_map_sha256':sha256(BASE/'frame-map.json'),
              'treatment':'T-M8 approach: restrained UI and procedural air/location-motion texture, adapted to native v3',
              'ui_sources':json.loads(library.read_text())['sources'],'library_manifest_sha256':sha256(library),
              'renderer_source_sha256':sha256(TRIAL/'audio-recreation/scripts/render_ui.py'),
              'ui_synthesis_source_sha256':sha256(TRIAL/'audio-recreation/synthesis/ui_synth.py'),
              'ui_procedural_rights':'Original project procedural synthesis, not claimed CC0 or proprietary Apple audio',
              'motion':{'range_frames_inclusive':[210,299],'start_sample':336000,'end_sample_exclusive':480000,
                        'seed':731904,'samples':144000,'algorithm':'Same motion_texture as T-M8, freshly generated for3s: Gaussian noise, third-order180–1800Hz bandpass, equal-power slow pan; proportional edge fades3/14s',
                        'mono_rms_target_dbfs':-43,'source_file':'../checkin/tools/build_scores.py',
                        'source_sha256':sha256(TRIAL/'checkin/tools/build_scores.py'),'reference_sha256':sha256(reference),
                        'rights':'Declared original procedural synthesis; no recording, music asset or AI generation'},
              'music_stem_silent':True,'stem_sum_max_error':error,'sample_rate':48000,'samples':len(ui),
              'stem_sha256':{name:sha256(BASE/f'{name}.flac') for name in ['ui','music','motion','full_mix']},
              'final_mp4_sha256':sha256(BASE/'final.mp4'),'final_loudness':loudness(decode(BASE/'final.mp4')),
              'build_source_sha256':sha256(Path(__file__))}
    write(BASE/'provenance.json',manifest)
    print(json.dumps({'ui_render':'pass','audible_cues':len(rendered),'samples':len(ui),'stem_sum_max_error':error,
                      'final_mp4_sha256':manifest['final_mp4_sha256'],'video_packet_sha256':output_packet,
                      'loudness':manifest['final_loudness']},indent=2))


if __name__=='__main__':main()
