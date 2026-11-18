"""Package two independently stemmed, neutral-labelled scores on one picture."""
import copy
import json
from pathlib import Path
import secrets
import sys
import numpy as np
from scipy import signal

BASE=Path(__file__).resolve().parents[1]
TRIAL=BASE.parent
sys.path.insert(0,str(TRIAL/'tools'))
sys.path.insert(0,str(TRIAL/'audio-recreation/scripts'))
from check_cues import PACKET_HASH_METHOD, add, decode, packet_hash
from build_treatments import mux, write
from render_mix import encode, loudness, sha256
import render_ui as renderer


def motion_texture(samples,seed=731904):
    if samples <= 0:
        raise ValueError('Texture span must be positive')
    rng=np.random.default_rng(seed)
    noise=signal.sosfilt(signal.butter(3,[180,1800],btype='bandpass',fs=48000,output='sos'),rng.normal(size=samples))
    phase=np.linspace(0,1,samples)
    envelope=np.minimum(1,np.minimum(phase,1-phase)*14)
    envelope=np.sin(np.pi/2*envelope)**2*(.85+.15*np.sin(np.pi*phase))
    mono=noise*envelope
    mono*=10**(-43/20)/max(np.sqrt(np.mean(mono**2)),1e-12)
    pan=np.linspace(-.25,.25,samples)
    stereo=np.column_stack([mono*np.sqrt((1-pan)/2),mono*np.sqrt((1+pan)/2)])
    stereo[[0,-1]]=0
    return stereo


def main():
    key=BASE/'keys/treatments.json'
    if key.exists():
        raise SystemExit('Refusing to overwrite key or scores')
    picture=BASE/'v1-first-export.mp4'
    schedule,schedule_path=renderer.load_schedule('checkin')
    report_path=TRIAL/'audio-recreation/ui-mixes/checkin/no-music/report.json'
    report=json.loads(report_path.read_text())
    library_path=TRIAL/'audio-recreation/library/manifest.json'
    library=json.loads(library_path.read_text())
    ui=decode(report_path.parent/'ui.flac')
    cues=[]; reconstructed=np.zeros_like(ui)
    for ordinal,event in enumerate(schedule['events']):
        if event['kind']=='control_appear':
            continue
        wave,c=renderer.render_event(event,schedule,ordinal)
        wave*=10**(report['common_peak_guard_gain_db']/20)
        cues.append((c,wave))
        add(reconstructed,wave,c['clip_start_sample_unclipped'])
    if np.max(np.abs(ui-reconstructed)) > 2e-6:
        raise ValueError('Cue references differ from existing renderer output')
    labels=set()
    while len(labels)<2:
        labels.add('T-'+secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')+secrets.choice('23456789'))
    labels=sorted(labels);secrets.SystemRandom().shuffle(labels)
    write(key,{'assignments':dict(zip(labels,['UI only','UI plus procedural location-motion texture'])),
               'policy':'Full 24-second original picture. Texture frames210–419 inclusive. No new UI cues in gap. No music asset or AI generation.'})
    key.chmod(0o600)
    productions=[]
    for index,label in enumerate(labels):
        folder=BASE/'blind'/label;folder.mkdir()
        (folder/'references').mkdir();(folder/'receipts').mkdir()
        motion=np.zeros_like(ui)
        if index:
            motion[210*1600:420*1600]=motion_texture(210*1600)
        music=np.zeros_like(ui)
        full=ui+motion
        for name,wave in [('ui',ui),('music',music),('motion',motion),('full_mix',full)]:
            encode(folder/f'{name}.flac',wave,aac=False)
        encode(folder/'production.m4a',full,aac=True,bitrate='192k')
        mux(picture,folder/'production.m4a',folder/'production.mp4')
        receipt={'picture_packet_sha256':packet_hash(picture),'picture_packet_hash_method':PACKET_HASH_METHOD,
                 'picture_file_sha256':sha256(picture),'picture_file_hash_method':schedule['picture_file_hash_method'],
                 'schedule_sha256':sha256(schedule_path),'fps':30,'fps_numerator':30,'fps_denominator':1,
                 'samples':1152000,'sample_rate':48000,'cues':[]}
        for original,wave in cues:
            c=copy.deepcopy(original)
            ref=folder/'references'/f'cue-{c["ordinal"]:02}.npy';np.save(ref,wave)
            c['reference']='references/'+ref.name;c['reference_sha256']=sha256(ref)
            receipt['cues'].append(c)
        texture=None
        if index:
            ref=folder/'references/continuous.npy';np.save(ref,motion)
            receipt['background_reference']={'reference':'references/continuous.npy','reference_sha256':sha256(ref),
                'alignment_sample':0,'role':'Expected procedural motion waveform generated from pinned source/seed; not extracted from delivery or production stem'}
            texture={'kind':'declared procedural synthesis, nonmusical air/location-motion texture; no recorded footsteps',
                     'seed':731904,'sample_rate':48000,'range_frames_inclusive':[210,419],
                     'sample_start':336000,'sample_end_exclusive':672000,'seconds':7.,
                     'algorithm':'Seeded Gaussian noise, causal third-order Butterworth bandpass180–1800Hz; half-sine squared 0.5s edge fades, broad arch; slow equal-power pan-.25 to+.25',
                     'mono_target_rms_dbfs':-43,'actual_stereo_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(motion[336000:672000]**2)))),
                     'peak_dbfs':float(20*np.log10(np.max(np.abs(motion)))),
                     'reference_sha256':sha256(ref),'source_sha256':sha256(Path(__file__)),
                     'license':'Original procedural trial synthesis; no third-party recording or AI generation. No claim to Apple proprietary sounds.'}
        write(folder/'receipts/production.json',receipt)
        impacts=[{'ordinal':c['ordinal'],'kind':c['canonical_event']['kind'],'frame':c['canonical_event']['frame'],
                  'sample':c['event_sample'],'clip_start_sample':c['clip_start_sample_unclipped'],
                  'alignment_offset_samples':c['clip_alignment_offset_samples'],
                  'asset':c['source'].get('asset_id',c['source'].get('effect')),
                  'target_peak_dbfs':c['target_peak_dbfs'],'asset_gain_db':c['source'].get('asset_gain_db'),
                  'common_guard_gain_db':report['common_peak_guard_gain_db'],'pitch':c['pitch'],'pan':c['pan'],
                  'reference_sha256':c['reference_sha256']} for c in receipt['cues']]
        write(folder/'cue-impacts.json',{'ui_impacts':impacts,'continuous_motion':texture,
                                        'silent_states':[e for e in report['events'] if not e['rendered']]})
        summed=decode(folder/'ui.flac')+decode(folder/'music.flac')+decode(folder/'motion.flac')
        error=float(np.max(np.abs(summed-decode(folder/'full_mix.flac'))))
        if error>2e-6:
            raise ValueError('Independent stems do not add')
        manifest={'label':label,'picture':{'file_sha256':sha256(picture),'file_hash_method':schedule['picture_file_hash_method'],
                  'packet_sha256':packet_hash(picture),'packet_hash_method':PACKET_HASH_METHOD,'decoded_frame_hash':None},
                  'frames':720,'fps_numerator':30,'fps_denominator':1,'samples':1152000,'sample_rate':48000,
                  'ui_sources':library['sources'],'library_manifest_sha256':sha256(library_path),
                  'asset_receipts':[{k:c[k] for k in ['ordinal','source','target_peak_dbfs','pitch','pan']} for c in receipt['cues']],
                  'renderer_report_sha256':sha256(report_path),'renderer_source_sha256':sha256(TRIAL/'audio-recreation/scripts/render_ui.py'),
                  'synthesis_source_sha256':sha256(TRIAL/'audio-recreation/synthesis/ui_synth.py'),
                  'procedural_ui_license':'Original project synthesis; not a proprietary Apple sound or asserted CC0 asset',
                  'continuous_motion':texture,'music_input':None,'music_stem_silent':True,
                  'stem_sha256':{name:sha256(folder/f'{name}.flac') for name in ['ui','music','motion','full_mix']},
                  'stem_sum_max_error':error,'build_source_sha256':sha256(Path(__file__)),
                  'production_loudness':loudness(decode(folder/'production.mp4'))}
        productions.append((label,folder,full,receipt,manifest))
    target=min(m['production_loudness']['integrated_lufs'] for _,_,_,_,m in productions)-1
    summary=[]
    for label,folder,full,original,manifest in productions:
        receipt=copy.deepcopy(original)
        gain_db=min(0.,target-manifest['production_loudness']['integrated_lufs']);gain=10**(gain_db/20)
        encode(folder/'comparison.m4a',full*gain,aac=True,bitrate='192k')
        mux(picture,folder/'comparison.m4a',folder/'comparison.mp4')
        for c in receipt['cues']:
            source=folder/c['reference'];dest=source.with_name(source.stem+'-review.npy')
            np.save(dest,np.load(source,allow_pickle=False)*gain)
            c['reference']='references/'+dest.name;c['reference_sha256']=sha256(dest)
        if 'background_reference' in receipt:
            ref=receipt['background_reference'];source=folder/ref['reference'];dest=source.with_name('continuous-review.npy')
            np.save(dest,np.load(source,allow_pickle=False)*gain)
            ref['reference']='references/'+dest.name;ref['reference_sha256']=sha256(dest)
        receipt['comparison_gain_db']=gain_db
        write(folder/'receipts/comparison.json',receipt)
        measured=loudness(decode(folder/'comparison.mp4'))
        if measured['true_peak_dbtp']>manifest['production_loudness']['true_peak_dbtp']+.1:
            raise ValueError('Comparison raised peaks')
        manifest['comparison']={'attenuation_only':True,'gain_db':gain_db,'target_lufs':target,'measured':measured}
        manifest['export_sha256']={p.name:sha256(p) for p in folder.glob('*.mp4')}
        write(folder/'provenance.json',manifest)
        summary.append({'label':label,'production':manifest['production_loudness'],'comparison':measured,'comparison_gain_db':gain_db,
                        'cues':len(receipt['cues']),'stem_sum_max_error':manifest['stem_sum_max_error']})
    write(BASE/'blind/levels.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
