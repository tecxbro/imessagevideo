"""Separate web delivery master: measured static gain and oversampled peak limiting."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE.parent/'tools'))
from build_treatments import mux,write
from check_cues import decode,packet_hash
from render_mix import encode,loudness,sha256

LIMIT_DB=-2.0
LIMIT=f'alimiter=limit={10**(LIMIT_DB/20):.12f}:attack=5:release=50:level=false:latency=true'


def filter_pcm(wave,filters,rate=48000,output_rate=48000):
    if wave.ndim!=2 or wave.shape[1]!=2 or not len(wave) or not np.isfinite(wave).all():
        raise ValueError('Expected nonempty finite stereo PCM')
    data=subprocess.check_output(['ffmpeg','-v','error','-f','f64le','-ar',str(rate),'-ac','2','-i','-',
        '-af',filters,'-ar',str(output_rate),'-ac','2','-f','f64le','-'],input=wave.astype('<f8').tobytes())
    return np.frombuffer(data,'<f8').reshape(-1,2).copy()


def master(wave,gain_db):
    return filter_pcm(wave,f'aresample=192000,volume={gain_db:.10f}dB,{LIMIT},aresample=48000')[:len(wave)]


def main():
    folder=BASE/'delivery'
    if (folder/'master.mp4').exists():raise SystemExit('Refusing to overwrite delivery master')
    (folder/'references').mkdir(parents=True,exist_ok=True)
    inputs={str(p.relative_to(BASE)):sha256(p) for p in [BASE/'final.mp4',*[BASE/f'{s}.flac' for s in ['ui','music','motion','full_mix']]]}
    source=decode(BASE/'full_mix.flac');first=loudness(source)
    if first['silent']:raise ValueError('Cannot master silence to an integrated target')
    gain=-16-first['integrated_lufs'];passes=[]
    for _ in range(15):
        output=master(source,gain)
        measured=loudness(output)
        passes.append({'linear_gain_db':gain,'limited_pcm_loudnorm':measured})
        print(json.dumps(passes[-1]),flush=True)
        error=-16-measured['integrated_lufs']
        if abs(error)<=.08:break
        gain+=error
    else:raise ValueError('Static gain plus limiter did not reach target')
    encode(folder/'master.flac',output,aac=False)
    encode(folder/'master.m4a',output,aac=True,bitrate='192k')
    mux(BASE/'v3-final.mp4',folder/'master.m4a',folder/'master.mp4')
    final=loudness(decode(folder/'master.mp4'))
    if abs(final['integrated_lufs']+16)>.3 or final['true_peak_dbtp']> -1:
        raise ValueError(f'Encoded master outside delivery specification: {final}')
    oversampled=filter_pcm(source,f'aresample=192000,volume={gain:.10f}dB',output_rate=192000)
    limited=filter_pcm(oversampled,LIMIT,rate=192000,output_rate=192000)
    if len(oversampled)!=len(limited):raise ValueError('Limiter latency compensation changed span')
    mask=np.abs(oversampled)>1e-4
    reduction=-20*np.log10(np.clip(np.abs(limited[mask]/oversampled[mask]),1e-10,1))
    receipt=copy.deepcopy(json.loads((BASE/'receipts/production.json').read_text()))
    transform={'linear_gain_db':gain,'limiter_filter':LIMIT,'oversampling_hz':192000,
               'reference_policy':'Each independently pinned production cue transformed through the same delivery chain, padded with100ms silence at each edge; not sampled from the master or stems',
               'limiter_interaction_limit':'Per-cue templates do not model nonlinear interactions with neighboring cues; original checker thresholds retained'}
    receipt['delivery_transform']=transform
    for c in receipt['cues']:
        path=BASE/c['reference']
        if sha256(path)!=c['reference_sha256']:raise ValueError('Production cue reference hash mismatch')
        wave=np.load(path,allow_pickle=False)
        reference=master(np.pad(wave,((4800,4800),(0,0))),gain)[4800:4800+len(wave)]
        target=folder/'references'/Path(c['reference']).name;np.save(target,reference)
        c.update(reference='references/'+target.name,reference_sha256=sha256(target))
    ref=receipt['background_reference'];path=BASE/ref['reference']
    if sha256(path)!=ref['reference_sha256']:raise ValueError('Production motion reference hash mismatch')
    target=folder/'references/motion.npy';np.save(target,master(np.load(path,allow_pickle=False),gain))
    ref.update(reference='references/motion.npy',reference_sha256=sha256(target))
    write(folder/'receipts/master.json',receipt)
    if any(sha256(BASE/name)!=value for name,value in inputs.items()):raise ValueError('Production input changed')
    report={'input_hashes_unchanged':inputs,'source_pcm_loudnorm':first,'target_lufs':-16,'passes':passes,
        'delivery_transform':transform,'limiter_gain_reduction_db':{'maximum':float(np.max(reduction)),
            'active_sample_p99':float(np.percentile(reduction,99)),
            'method':'192kHz linked limiter output/input amplitude ratio on pre-limiter samples above1e-4, with latency compensation; before downsampling'},
        'final_mp4_loudnorm':final,'final_mp4_sha256':sha256(folder/'master.mp4'),
        'video_packet_sha256':packet_hash(folder/'master.mp4'),'samples':len(output),
        'ffmpeg_version':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],
        'recipe_sha256':sha256(Path(__file__))}
    write(folder/'measurements.json',report)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
