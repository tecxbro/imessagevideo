"""Source-backed delivery gate. Requires FFmpeg with the ebur128 filter."""
import argparse
import json
import math
import re
import subprocess


def measure(path):
    result = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path),
                             '-map', '0:a:0', '-af', 'ebur128=peak=true',
                             '-f', 'null', '-'], capture_output=True, text=True, check=True)
    summary = result.stderr.rsplit('Summary:', 1)[-1]
    integrated = re.search(r'I:\s*([-+\w.]+) LUFS', summary)
    peak = re.search(r'Peak:\s*([-+\w.]+) dBFS', summary)
    if not integrated or not peak:
        raise ValueError('FFmpeg did not report ebur128 integrated loudness and true peak')
    return {'integrated_lufs': float(integrated[1]), 'true_peak_dbtp': float(peak[1])}


def evaluate(source, export, tolerance=1., ceiling=-1.):
    delta = export['integrated_lufs'] - source['integrated_lufs']
    passed = (all(math.isfinite(v) for m in [source, export] for v in m.values())
              and abs(delta) <= tolerance and export['true_peak_dbtp'] <= ceiling)
    return delta, passed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('export')
    args = parser.parse_args()
    try:
        source, export = measure(args.source), measure(args.export)
        delta, passed = evaluate(source, export)
    except (subprocess.CalledProcessError, ValueError) as error:
        parser.exit(2, f'Loudness measurement failed: {error}\n')
    for label, measurement in [('source', source), ('export', export)]:
        print(f"{label}: {measurement['integrated_lufs']:.1f} LUFS, {measurement['true_peak_dbtp']:.1f} dBTP")
    print(f"{'PASS' if passed else 'FAIL'}: delta={delta:+.1f} LU (limit ±1.0); export true peak <= -1.0 dBTP required")
    return int(not passed)


if __name__ == '__main__':
    raise SystemExit(main())
