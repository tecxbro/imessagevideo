#!/usr/bin/env python3
"""cue_check.py — correlate expected cue times (from a cue sheet) with
measured attacks in an actual (possibly encoded) audio file.

Two checks:
  1. PRESENCE — for every expected event, the max window-peak inside
     [t - pre, t + post] must exceed floor + min_rise_db. Reports measured
     attack offset vs expected time.
  2. UNEXPECTED — any onset-like rise (same detector logic as onsets.py,
     finer hop) not within `post` of an expected event is listed.

Cue sheet formats accepted:
  - canonical JSON (list under "events" with "frame"/"time"/"kind")
  - plain JSON list of {t} or numbers
  - CSV with a "time" or "frame" column (frames need --fps)

Exit 0 = pass, 1 = failures, 2 = usage.
"""
import json, math, struct, subprocess, sys, argparse, csv

def decode(path, sr):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "a:0",
                        "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return p.stdout

def windows(raw, sr, win_s=0.01, hop_s=0.005):
    w = max(1, int(sr * win_s)); h = max(1, int(sr * hop_s))
    n = len(raw) // 4
    out = []
    i = 0
    while i + w <= n:
        seg = struct.unpack_from("<%df" % w, raw, i * 4)
        s = 0.0; pk = 0.0
        for x in seg:
            s += x * x
            if abs(x) > pk: pk = abs(x)
        out.append((i / sr, 20 * math.log10(math.sqrt(s / w) + 1e-12),
                    20 * math.log10(pk + 1e-12)))
        i += h
    return out

def load_cues(path, fps):
    if path.endswith(".csv"):
        cues = []
        with open(path) as f:
            r = csv.DictReader(f)
            for row in r:
                if "time" in row and row["time"]:
                    cues.append({"time": float(row["time"]),
                                 "kind": row.get("kind", "?")})
                elif "frame" in row and row["frame"]:
                    cues.append({"time": int(row["frame"]) / fps,
                                 "kind": row.get("kind", "?")})
        return cues
    d = json.load(open(path))
    evs = d["events"] if isinstance(d, dict) and "events" in d else d
    cues = []
    for e in evs:
        if isinstance(e, (int, float)):
            cues.append({"time": float(e), "kind": "?"})
        elif "time" in e:
            cues.append({"time": float(e["time"]),
                         "kind": e.get("kind", "?"),
                         "event_id": e.get("event_id")})
    return cues

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("cues")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--sr", type=int, default=16000)
    ap.add_argument("--pre", type=float, default=0.06)
    ap.add_argument("--post", type=float, default=0.16)
    ap.add_argument("--min-rise-db", type=float, default=10.0)
    ap.add_argument("--max-offset", type=float, default=0.120,
                    help="max allowed |measured-expected| attack offset, s")
    args = ap.parse_args()

    raw = decode(args.audio, args.sr)
    w = windows(raw, args.sr)
    cues = sorted(load_cues(args.cues, args.fps), key=lambda c: c["time"])

    levels = sorted(x[1] for x in w)
    floor = levels[max(0, int(len(levels) * 0.10) - 1)]
    thr = floor + args.min_rise_db

    res = []
    fails = []
    for c in cues:
        t0, t1 = c["time"] - args.pre, c["time"] + args.post
        cand = [x for x in w if t0 <= x[0] <= t1]
        if not cand:
            res.append({**c, "status": "no_window"})
            fails.append(c)
            continue
        best = max(cand, key=lambda x: x[1])
        # attack = first window within 6 dB of that local max
        atk = next(x for x in cand if x[1] >= best[1] - 6.0)
        off = atk[0] - c["time"]
        ok = best[1] >= thr and abs(off) <= args.max_offset
        r = {**c, "status": "ok" if ok else "FAIL",
             "meas_attack": round(atk[0], 4), "offset_ms": round(off * 1000, 1),
             "peak_dbfs": round(best[1], 1),
             "rise_db": round(best[1] - floor, 1)}
        res.append(r)
        if not ok:
            fails.append(r)

    # unexpected onsets
    extra = []
    i = 0
    while i < len(w):
        if w[i][1] >= thr:
            j = i
            while j < len(w) and w[j][1] >= thr:
                j += 1
            t = w[i][0]
            near = any(abs(t - c["time"]) <= args.post for c in cues)
            if not near:
                extra.append({"t": round(t, 3),
                              "peak_dbfs": round(max(x[1] for x in w[i:j]), 1)})
            i = j
        i += 1

    out = {"audio": args.audio, "cues_file": args.cues,
           "floor_dbfs": round(floor, 1), "threshold_dbfs": round(thr, 1),
           "expected": len(cues), "passed": len(cues) - len(fails),
           "failed": [f if isinstance(f, dict) else f for f in fails],
           "unexpected_onsets": extra, "events": res}
    print(json.dumps(out, indent=1))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
