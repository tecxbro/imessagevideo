"""Post-repair evaluator: key and clean stem are allowed ONLY here."""
import argparse
import json
from pathlib import Path
import numpy as np
from check_cues import decode
from score_cues import score
from build_treatments import write
from render_mix import sha256


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before',required=True,type=Path);p.add_argument('--after',required=True,type=Path)
    p.add_argument('--key',required=True,type=Path);p.add_argument('--clean-stem',required=True,type=Path)
    p.add_argument('--repair-stem',required=True,type=Path);p.add_argument('--json',required=True,type=Path)
    a=p.parse_args()
    key=json.loads(a.key.read_text())
    before=score(json.loads(a.before.read_text()),key);after=score(json.loads(a.after.read_text()),key)
    clean=decode(a.clean_stem);repair=decode(a.repair_stem)
    if clean.shape!=repair.shape:
        raise ValueError('PCM span mismatch')
    delta=repair-clean;rms=float(np.sqrt(np.mean(delta**2)));maximum=float(np.max(np.abs(delta)))
    result={'key_defects':len(key['defects']),'before_detected':before['true_positives'],
            'remaining_key_defects':after['true_positives'],'resolved_key_defects':len(after['misses']),
            'new_or_unkeyed_findings':after['false_positives'],'repair_is_bit_identical_to_clean_pcm':bool(np.array_equal(clean,repair)),
            'pcm_difference_vs_clean':{'samples':len(clean),'rms_linear':rms,'rms_dbfs':float(20*np.log10(max(rms,1e-15))),
                                      'max_absolute_linear':maximum,'max_absolute_dbfs':float(20*np.log10(max(maximum,1e-15))),
                                      'snr_db':float(20*np.log10(np.sqrt(np.mean(clean**2))/max(rms,1e-15)))},
            'clean_stem_sha256':sha256(a.clean_stem),'repair_stem_sha256':sha256(a.repair_stem),
            'key_read_by':'post-repair evaluator only; repair tool has no key input'}
    write(a.json,result);print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
