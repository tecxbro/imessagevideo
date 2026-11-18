"""Score a completed blind review; this is the only reader of intervention keys."""
import argparse
import json
from pathlib import Path


def score(review, key):
    rows = {c['ordinal']: c for c in review['cues']}
    expected = set(); hits = []; misses = []; errors = []
    for defect in key['defects']:
        ordinal = defect['ordinal']
        if ordinal is None:
            found = any(abs(e['sample']-defect['sample']) < 4800 for e in review['extras'])
        else:
            expected.add(ordinal); row = rows[ordinal]
            wanted = {'late': 'late', 'early': 'early', 'dropped': 'missing',
                      'attenuated': 'damaged', 'lowpassed': 'damaged'}[defect['kind']]
            found = wanted in row['flags']
            if found and defect['kind'] in {'late', 'early'}:
                errors.append(row['offset_samples'] - defect['offset_samples'])
        (hits if found else misses).append({'ordinal': ordinal, 'kind': defect['kind']})
    false = [{'ordinal': c['ordinal'], 'flags': c['flags']} for c in review['cues'] if c['flags'] and c['ordinal'] not in expected]
    false += [e for e in review['extras'] if not any(d['kind']=='extra' and abs(e['sample']-d['sample']) < 4800 for d in key['defects'])]
    return {'true_positives': len(hits), 'misses': misses, 'false_positives': false,
            'detected': hits, 'timing_errors_samples': errors,
            'maximum_absolute_timing_error_ms': max(map(abs, errors), default=0)/48}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('review', type=Path); p.add_argument('key', type=Path); p.add_argument('--json', type=Path, required=True)
    a = p.parse_args(); result = score(json.loads(a.review.read_text()), json.loads(a.key.read_text()))
    a.json.write_text(json.dumps(result, indent=2)+'\n'); print(json.dumps(result, indent=2))
