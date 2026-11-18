"""Contrast raw single-template measurement with overlap-aware fixed references."""
import json
from pathlib import Path
import numpy as np
from check_cues import add, decode
from build_treatments import write
from render_mix import sha256

BASE=Path(__file__).resolve().parents[1]


def measurement(segment,wave):
    dot=np.sum(segment*wave)
    gain=dot/np.sum(wave**2)
    return {'correlation':float(dot/np.sqrt(np.sum(segment**2)*np.sum(wave**2))),
            'gain_delta_db':float(20*np.log10(max(gain,1e-10)))}


def main():
    folder=BASE/'blind/T-V5'
    results=[]
    for mode in ['production','comparison']:
        receipt=json.loads((folder/f'receipts/{mode}.json').read_text())
        audio=decode(folder/f'{mode}.mp4')
        expected=np.zeros_like(audio)
        waves=[np.load(folder/c['reference'],allow_pickle=False) for c in receipt['cues']]
        for cue,wave in zip(receipt['cues'],waves):
            add(expected,wave,cue['clip_start_sample_unclipped'])
        first=receipt['cues'][0];wave=waves[0];start=first['clip_start_sample_unclipped'];end=start+len(wave)
        neighbors=expected.copy();add(neighbors,wave,start,-1)
        isolated=audio-neighbors
        raw=measurement(audio[start:end],wave)
        separated=measurement(isolated[start:end],wave)
        prior=json.loads((folder/f'{mode}.check.json').read_text())
        level_deltas=[c['level_delta_db'] for c in prior['cues']]
        ref_rms_db=[float(20*np.log10(np.sqrt(np.mean(w**2)))) for w in waves]
        results.append({'mode':mode,'delivery_sha256':sha256(folder/f'{mode}.mp4'),
                        'receipt_sha256':sha256(folder/f'receipts/{mode}.json'),
                        'frame':109,'fps_numerator':30000,'fps_denominator':1001,
                        'expected_impact_sample':first['event_sample'],'expected_impact_seconds':first['event_sample']/48000,
                        'template_start_sample':start,'template_end_exclusive':end,
                        'overlapping_cues':[{'ordinal':c['ordinal'],'frame':c['canonical_event']['frame'],
                                             'clip_start_sample':c['clip_start_sample_unclipped'],'clip_samples':len(w)}
                                            for c,w in zip(receipt['cues'][1:],waves[1:])
                                            if c['clip_start_sample_unclipped']<end and c['clip_start_sample_unclipped']+len(w)>start],
                        'raw_single_template_at_scheduled_start':raw,
                        'after_subtracting_FIXED_expected_neighbors_no_gain_or_time_fitting':separated,
                        'previous_checker_opening':prior['cues'][0],
                        'all_checker_level_deltas_db':[min(level_deltas),max(level_deltas)],
                        'checker_gain_span_db':max(level_deltas)-min(level_deltas),
                        'expected_reference_rms_span_db':max(ref_rms_db)-min(ref_rms_db),
                        'all_expected_mix_vs_decoded_correlation':float(np.sum(audio*expected)/np.sqrt(np.sum(audio**2)*np.sum(expected**2))),
                        'threshold_changed':False})
    write(BASE/'results/T-V5-opening-investigation.json',results)
    print(json.dumps(results,indent=2))


if __name__=='__main__':
    main()
