#!/usr/bin/env python3
"""Onset/envelope analysis for short UI-sound verification.

Pure stdlib + ffmpeg decode. Emits JSON:
  - sample_rate, duration, noise_floor_dbfs (median window RMS of quietest decile)
  - windows: optional per-window RMS dB series (with --dump-envelope)
  - onsets: list of {t, rel_db, peak_dbfs} where rel_db = rise over local floor

Onset rule: a window is an onset when its RMS exceeds
  max(noise_floor + rise_min_db, absolute_min_dbfs) AND rises at least
  rise_min_db over the max of the previous `back` windows' median.
Grouping: consecutive above-threshold windows merge; onset t = first window
whose RMS is within `attack_drop_db` of the group peak (approx attack point).

Designed for near-silent beds (UI stems); on loud music beds use --abs-min
to ignore constant program material.
"""
import json, math, struct, subprocess, sys, tempfile, os, argparse

def decode(path, sr=16000):
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-map", "a:0", "-ac", "1",
         "-ar", str(sr), "-f", "f32le", "-"],
        capture_output=True, check=True)
    return sr, p.stdout

def envelope(raw, sr, win_ms=10.0, hop_ms=10.0):
    w = max(1, int(sr * win_ms / 1000.0))
    h = max(1, int(sr * hop_ms / 1000.0))
    n = len(raw) // 4
    out = []
    i = 0
    while i + w <= n:
        seg = struct.unpack_from("<%df" % w, raw, i * 4)
        s = 0.0
        pk = 0.0
        for x in seg:
            s += x * x
            if abs(x) > pk:
                pk = abs(x)
        rms = math.sqrt(s / w) if w else 0.0
        db = 20.0 * math.log10(rms + 1e-12)
        pdb = 20.0 * math.log10(pk + 1e-12)
        out.append((i / sr, db, pdb))
        i += h
    return out

def detect(env, rise_min_db=9.0, abs_min_dbfs=-60.0, floor_pct=10,
           back=6, merge_gap=0.06, attack_drop_db=6.0, max_len=2.0):
    if not env:
        return [], -120.0
    levels = sorted(e[1] for e in env)
    floor = levels[max(0, int(len(levels) * floor_pct / 100) - 1)]
    thresh = max(floor + rise_min_db, abs_min_dbfs)
    onsets = []
    i = 0
    while i < len(env):
        t, db, pdb = env[i]
        if db >= thresh:
            # local floor = median of previous `back` windows below thresh
            j0 = max(0, i - back)
            prev = sorted(env[j][1] for j in range(j0, i))
            local_floor = prev[len(prev)//2] if prev else floor
            if db - local_floor >= rise_min_db or db >= abs_min_dbfs + 30:
                # grow group
                g0 = i
                gpk, gt = db, t
                j = i
                last_above = i
                while j < len(env) and (env[j][1] >= thresh or
                                        (j - last_above) * 0.01 <= merge_gap) and \
                        env[j][0] - env[g0][0] <= max_len:
                    if env[j][1] >= thresh:
                        last_above = j
                        if env[j][1] > gpk:
                            gpk, gt = env[j][1], env[j][0]
                    j += 1
                # attack point: first window in group within attack_drop of peak
                at = env[g0][0]
                for k in range(g0, last_above + 1):
                    if env[k][1] >= gpk - attack_drop_db:
                        at = env[k][0]
                        break
                onsets.append({"t": round(at, 4),
                               "group_peak_dbfs": round(gpk, 2),
                               "rel_db": round(gpk - local_floor, 2),
                               "end_t": round(env[last_above][0] + 0.01, 4)})
                i = last_above + 1
                continue
        i += 1
    return onsets, floor

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--sr", type=int, default=16000)
    ap.add_argument("--win", type=float, default=10.0)
    ap.add_argument("--rise", type=float, default=9.0, help="min dB rise over local floor")
    ap.add_argument("--abs-min", type=float, default=-60.0, help="absolute min RMS dBFS")
    ap.add_argument("--dump-envelope", action="store_true")
    args = ap.parse_args()
    sr, raw = decode(args.file, args.sr)
    env = envelope(raw, sr, args.win, args.win)
    onsets, floor = detect(env, rise_min_db=args.rise, abs_min_dbfs=args.abs_min)
    out = {"file": args.file, "sr": sr,
           "duration_s": round(len(raw) / 4 / sr, 4),
           "noise_floor_dbfs": round(floor, 2),
           "onset_count": len(onsets), "onsets": onsets}
    if args.dump_envelope:
        out["envelope"] = [[round(t, 3), round(db, 1)] for t, db, _ in env]
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
