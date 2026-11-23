#!/usr/bin/env python3
"""Pick one renderer to try, or select the best verified pilot for one reference."""
import argparse
import json
import math
from pathlib import Path
import sys

ENGINES = ('pillow', 'svg', 'hyperframes', 'gsap', 'remotion', 'html', 'motion-canvas')
PILOTS = {
    'raster': ('pillow', 'A native-pixel image or mask track is the hardest requirement.'),
    'dom': ('hyperframes', 'The hard shot needs editable type, browser layout, masks or a product interface.'),
    'timeline': ('gsap', 'The hard shot depends on coordinated easing across several layers.'),
    'react': ('remotion', 'The source components and state already live in React.'),
    'vector': ('motion-canvas', 'The critical requirement is animated vector geometry.'),
}

def nominate(material='dom', existing=None, required=None):
    if required:
        engine, reason = required, 'The user specifically selected this implementation.'
    elif existing:
        engine, reason = existing, 'The saved editable project already has an implementation for this shot.'
    else:
        engine, reason = PILOTS[material]
    return dict(engine=engine, basis='short-pilot-needed', reason=reason,
                next='Render the hardest passage at source geometry and timing. Inspect its moving subject and fixed anchors. '
                     'Try another engine only if this one misses a requirement.')

def select(pilots, required=None):
    """Use only comparable, frame-verified and reviewed proofs; keep ties in input order."""
    candidates, rejected = [], []
    comparison = None
    seen = set()
    for item in pilots:
        engine, filename = item['engine'], item['report']
        if engine not in ENGINES or engine in seen:
            raise ValueError(f'Unknown or duplicate renderer: {engine}')
        seen.add(engine)
        if required and engine != required:
            continue
        report = json.loads(Path(filename).read_text())
        metrics = report['metrics']
        source = report['inputs']['source']
        identity = (source['sha256'], json.dumps(report.get('roi_xyxy',{}), sort_keys=True),
                    json.dumps(report['thresholds'], sort_keys=True))
        if comparison is None:
            comparison = identity
        elif comparison != identity:
            raise ValueError('All pilots must use the same source passage, same regions and same tolerances.')
        if not (report.get('structure_within_tolerance',report.get('structure_match')) and report.get('limits_passed') is True
                and report['thresholds']['max_mae'] is not None and metrics
                and report.get('compared_frames') == source['frame_count']
                and item.get('visual_review') == 'pass' and str(item.get('observation','')).strip()):
            rejected.append(engine)
            continue
        scores = [x['max_frame_mae'] for x in metrics.values()]
        if not all(math.isfinite(score) and score >= 0 for score in scores):
            raise ValueError('Invalid frame comparison metric.')
        candidates.append(((max(scores), metrics['full']['mean_frame_mae']), engine, str(filename), item['observation']))
    if not candidates:
        return dict(engine=None, basis='no-passing-pilot', rejected=rejected, next='Revise the shot or test one different renderer.')
    score, engine, report, observation = min(candidates, key=lambda row: row[0])
    return dict(engine=engine, basis='reviewed-pilot', worst_frame_or_region_mae=score[0],
                mean_frame_mae=score[1], report=report, observation=observation, rejected=rejected)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--material', choices=PILOTS, default='dom')
    ap.add_argument('--existing', choices=ENGINES)
    ap.add_argument('--required', choices=ENGINES)
    ap.add_argument('--pilots', type=Path, help='JSON array of engine, report path, visual_review, observation.')
    a=ap.parse_args()
    try:
        if a.pilots:
            rows=json.loads(a.pilots.read_text())
            for row in rows:
                row['report']=str((a.pilots.parent/row['report']).resolve())
            result=select(rows, a.required)
        else:
            result=nominate(a.material,a.existing,a.required)
        print(json.dumps(result,indent=2))
        return 0 if result.get('engine') else 1
    except (KeyError, TypeError, OSError, ValueError) as exc:
        ap.exit(2,f'{exc}\n')

if __name__ == '__main__':
    sys.exit(main())
