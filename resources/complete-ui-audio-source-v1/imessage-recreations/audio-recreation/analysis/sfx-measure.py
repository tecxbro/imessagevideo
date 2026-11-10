"""Read-only reference-audio measurements; no reference waveform is saved.

All generated files belong to the sfx-* namespace. This is candidate detection,
not perceptual source separation or a claim that detected attacks are UI sounds.
"""
from pathlib import Path
import hashlib, json, subprocess
import numpy as np
from scipy import signal, ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'audio-recreation/analysis'
IDS = ['01-photonhq','02-danieltian','03-photon-mini','04-poke','05-linq','06-gallery']
SR, HOP, NFFT = 24000, 120, 1024

def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],text=True))

def mapped(t, k):
    if k != '06-gallery': return t
    if 1049/30 <= t < 41: return None
    return t if t < 1049/30 else t-181/30

def measure(k):
    src=ROOT/'references'/k/'source.mp4'; vis=ROOT/'outputs'/k/'gsap.mp4'
    meta=probe(src); vm=probe(vis)
    vd=next(x for x in vm['streams'] if x['codec_type']=='video')
    source_vd=next(x for x in meta['streams'] if x['codec_type']=='video')
    audio=next(x for x in meta['streams'] if x['codec_type']=='audio')
    raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(src),'-vn','-ac','2','-ar',str(SR),'-f','f32le','pipe:1'])
    stereo=np.frombuffer(raw,np.float32).reshape(-1,2); y=stereo.mean(axis=1)
    f,t,Z=signal.stft(y,SR,nperseg=NFFT,noverlap=NFFT-HOP,boundary='zeros')
    a=np.abs(Z).astype(np.float32)
    power=a*a
    # Median masks are only attribution aids. No separated audio is synthesized.
    hm=ndimage.median_filter(a,size=(1,41)); pm=ndimage.median_filter(a,size=(17,1))
    percussive=pm*pm/(hm*hm+pm*pm+1e-15)
    hp_ratio=(power*percussive).sum(axis=0)/(power.sum(axis=0)+1e-15)
    bands=[(0,180),(180,1200),(1200,5000),(5000,12001)]
    bp=np.stack([power[(f>=lo)&(f<hi)].sum(axis=0) for lo,hi in bands])
    norm=a/(np.median(a,axis=1,keepdims=True)+0.00003)
    log=np.log1p(norm)
    flux=np.maximum(np.diff(log,axis=1,prepend=log[:,:1]),0)
    novelty=flux.mean(axis=0)
    # Robust local background avoids calling all loud musical passages cues.
    bg=ndimage.median_filter(novelty,size=101)
    diff=np.maximum(novelty-bg,0)
    scale=np.percentile(diff[diff>0],75) if np.any(diff>0) else 1
    score=diff/max(float(scale),1e-8)
    peaks,props=signal.find_peaks(score,distance=18,prominence=.55,height=.9)
    if len(peaks)>180:
        peaks=np.sort(peaks[np.argsort(score[peaks])[-180:]])
    env=np.sqrt(power.sum(axis=0))
    # Beat periodicity is a likelihood aid, not a measured music tempo claim.
    act=np.maximum(novelty-np.median(novelty),0)
    ac=signal.fftconvolve(act,act[::-1],mode='full')[len(act)-1:]
    lo,hi=int(.285*SR/HOP),int(1.5*SR/HOP)
    acpeaks,_=signal.find_peaks(ac[lo:hi]); lags=acpeaks+lo
    ranked=sorted(lags,key=lambda n:ac[n],reverse=True)[:8]
    periods=[{'period_s':round(float(n*HOP/SR),4),'bpm':round(float(60/(n*HOP/SR)),2),'relative_autocorrelation':round(float(ac[n]/max(ac[0],1e-10)),4)} for n in ranked]
    main=ranked[0]*HOP/SR if ranked else .5
    # Best alignment of recurring acoustic attacks to a single periodic grid.
    phase_candidates=np.arange(0,main,HOP/SR)
    pts=t[peaks]; wt=score[peaks]
    support=[]
    for phase in phase_candidates:
        d=np.abs((pts-phase+main/2)%main-main/2)
        support.append(float((wt*np.exp(-(d/.032)**2)).sum()))
    phase=float(phase_candidates[int(np.argmax(support))]) if support else 0
    candidates=[]
    for p in peaks:
        ts=float(t[p]); ot=mapped(ts,k)
        j0=max(0,p-3); j1=min(len(t),p+20)
        energy=bp[:,j0:j1].sum(axis=1); shares=energy/(energy.sum()+1e-15)
        local=env[max(0,p-40):min(len(t),p+80)]
        floor=float(np.percentile(local,25)); peak=float(env[p:min(p+10,len(t))].max())
        threshold=floor+.3*(peak-floor)
        end=min(p+140,len(t)-1)
        for j in range(p+4,min(p+140,len(t)-3)):
            if np.all(env[j:j+3]<threshold):end=j;break
        dbeat=abs((ts-phase+main/2)%main-main/2)
        centroid=float((f[:,None]*power[:,j0:j1]).sum()/(power[:,j0:j1].sum()+1e-15))
        flat=float(np.exp(np.mean(np.log(a[:,j0:j1]+1e-10)))/(np.mean(a[:,j0:j1])+1e-10))
        candidates.append({'source_time':round(ts,4),'output_time':round(ot,4) if ot is not None else None,'onset_score':round(float(score[p]),3),'strength_relative':round(float(min(score[p]/max(np.percentile(score[peaks],95),1e-8),1)),3),'duration_estimate':round(float((end-p)*HOP/SR),3),'band_energy_fraction':dict(zip(['low_0_180','low_mid_180_1200','mid_1200_5000','high_5000_12000'],np.round(shares,4).tolist())),'centroid_hz':round(centroid,1),'spectral_flatness':round(flat,4),'percussive_mask_fraction':round(float(hp_ratio[j0:j1].mean()),3),'distance_to_recurring_attack_grid_s':round(float(dbeat),4),'excluded_live_action':ot is None})
    r={'reference':k,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_audio':{key:audio.get(key) for key in ['codec_name','sample_rate','channels','start_time','duration']},'source_video_duration':float(source_vd['duration']),'output_video_duration':float(vd['duration']),'measurement':{'sample_rate':SR,'hop_s':HOP/SR,'window_s':NFFT/SR,'waveform_saved':False,'auditioned':False,'listening_limitation':'No local audition/listening endpoint was available; these are signal measurements correlated with visual scene context.','timing_uncertainty_s':.03,'duration_limit':'Estimated decay includes overlapping music; not an isolated SFX tail.','beat_grid':{'period_s':round(main,4),'phase_s':round(phase,4),'alternatives':periods},'rms_dbfs':round(float(20*np.log10(np.sqrt(np.mean(y*y))+1e-10)),2),'peak_dbfs':round(float(20*np.log10(np.max(np.abs(stereo))+1e-10)),2),'stereo_correlation':round(float(np.corrcoef(stereo.T)[0,1]),4)},'onset_candidates':candidates}
    (OUT/f'sfx-{k}-measurements.json').write_text(json.dumps(r,indent=2)+'\n')
    fig,ax=plt.subplots(3,1,figsize=(15,6),sharex=True)
    ax[0].plot(t,20*np.log10(env+1e-8),lw=.6);ax[0].set_ylabel('STFT RMS dB')
    for i,label in enumerate(['<180Hz','180–1200Hz','1.2–5kHz','>5kHz']):ax[1].plot(t,bp[i]/(bp.sum(axis=0)+1e-15),lw=.6,label=label)
    ax[1].legend(ncol=4,fontsize=8);ax[1].set_ylabel('Energy share')
    ax[2].plot(t,score,lw=.6);ax[2].scatter(t[peaks],score[peaks],s=9,c='r');ax[2].set_ylabel('Attack score');ax[2].set_xlabel('Source seconds')
    if k=='06-gallery':
        for axy in ax:axy.axvspan(1049/30,41,color='gray',alpha=.25)
    fig.suptitle(k+' — analysis only; red marks are attacks, not certified UI cues');fig.tight_layout();fig.savefig(OUT/f'sfx-{k}-overview.png',dpi=100);plt.close(fig)
    print(k,'candidates',len(candidates),'grid',round(main,3),'RMS',r['measurement']['rms_dbfs'],flush=True)

if __name__=='__main__':
    for key in IDS:measure(key)
