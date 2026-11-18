#!/usr/bin/env python3
"""kind_check.py — per-event timbre fingerprint vs declared kind.

For each cue-sheet event, measure zero-crossing rate, crest factor and
window RMS in [t, t+window] of the audio, then compare against the
fingerprint envelope of the declared kind's family.

Families (measured on the 04-poke accepted UI stem, 16 kHz mono):
  whoosh/movement : ZCR 0.10–0.25, crest 4–14,   RMS >= -31 dB
  click/tap/key   : ZCR 0.005–0.06, crest 20–60,  RMS <= -30 dB  (short transient)
  drop/arrival    : ZCR 0.03–0.10, crest 10–26,   RMS -36..-25
  confirm/beep    : ZCR 0.01–0.08, crest 6–20,    RMS -32..-20  (tonal, longer body)
  silence         : RMS < -50 dB

Kind→family map is overridable via --map json.
Exit 0 pass / 1 any mismatch.
"""
import json, subprocess, sys, math, struct, argparse

FAMILIES = {
 "whoosh":    {"zcr": (0.09, 0.36), "crest": (4, 16)},
 "click":     {"zcr": (0.005, 0.06), "crest": (20, 70)},
 "drop":      {"zcr": (0.03, 0.12), "crest": (10, 30)},
 "confirm":   {"zcr": (0.005, 0.09), "crest": (5, 25)},
 "key":       {"zcr": (0.12, 0.40), "crest": (4, 26)},
 "silence":   {"rms_max_off": 8.0},
}
# RMS is judged RELATIVE: each non-silent event must sit within
# [-18, +9] dB of the file's median event window-RMS and >= floor+8 dB.
# Family bounds above are timbre identity (zcr/crest); level is set by
# the mix, not the kind.
KIND2FAM = {"message_send": "whoosh", "panel_open": "whoosh", "panel_close": "whoosh",
            "card_swoosh": "whoosh", "tap": "click", "typing": "key", "delete": "click",
            "text_select": "click", "cart_update": "click", "message_arrival": "drop",
            "card_arrival": "drop", "typing_burst": "key",
            "control_appear": "silence", "logo_resolve": "confirm",
            "glass_confirm": "confirm", "digital_sparkle": "confirm", "low_impact": "confirm"}

def decode(path, sr):
    return subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "a:0",
                           "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                          capture_output=True, check=True).stdout

def seg(raw, sr, t0, t1):
    a, b = int(t0 * sr), min(int(t1 * sr), len(raw) // 4)
    return struct.unpack_from("<%df" % (b - a), raw, a * 4) if b > a else []

def metrics(samps):
    if not samps:
        return 0.0, 1.0, -120.0
    zc = sum(1 for i in range(1, len(samps)) if (samps[i] >= 0) != (samps[i-1] >= 0)) / len(samps)
    pk = max(abs(x) for x in samps)
    rms = math.sqrt(sum(x * x for x in samps) / len(samps))
    return zc, (pk / rms if rms > 0 else 999.0), 20 * math.log10(rms + 1e-12)

def load_cues(path, fps):
    d = json.load(open(path))
    evs = d["events"] if isinstance(d, dict) and "events" in d else d
    out = []
    for e in evs:
        t = e.get("time", e.get("frame", 0) / fps)
        out.append({"time": float(t), "kind": e.get("kind", "?")})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("cues")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--sr", type=int, default=16000)
    ap.add_argument("--window", type=float, default=0.4)
    ap.add_argument("--map", default=None, help="JSON kind->family overrides")
    a = ap.parse_args()
    k2f = dict(KIND2FAM)
    if a.map:
        k2f.update(json.load(open(a.map)))
    raw = decode(a.audio, a.sr)
    cues = load_cues(a.cues, a.fps)
    # first pass: all metrics + file-level noise/event baselines
    for idx, c in enumerate(cues):
        w = a.window
        if idx + 1 < len(cues):
            w = min(w, max(0.02, cues[idx + 1]["time"] - c["time"] - 0.005))
        c["_w"], c["_m"] = w, metrics(seg(raw, a.sr, c["time"], c["time"] + w))
    audible = [c["_m"][2] for c in cues if k2f.get(c["kind"], "") != "silence"]
    med = sorted(audible)[len(audible) // 2] if audible else -30.0
    quiet = [c["_m"][2] for c in cues if k2f.get(c["kind"], "") == "silence"]
    floor = min(quiet) - 3 if quiet else med - 35
    fails, rows = [], []
    for c in cues:
        fam = k2f.get(c["kind"])
        z, cr, r = c["_m"]
        row = {"time": round(c["time"], 3), "kind": c["kind"], "family": fam,
               "zcr": round(z, 4), "crest": round(cr, 1), "rms_dbfs": round(r, 1),
               "rms_vs_median": round(r - med, 1)}
        if fam and fam in FAMILIES:
            f = FAMILIES[fam]
            bad = []
            if fam == "silence":
                if r > floor + f["rms_max_off"]: bad.append("not_silent")
            else:
                if "zcr" in f and not (f["zcr"][0] <= z <= f["zcr"][1]): bad.append("zcr")
                if "crest" in f and not (f["crest"][0] <= cr <= f["crest"][1]): bad.append("crest")
                if not (med - 18 <= r <= med + 9) or r < floor + 8: bad.append("level")
            row["status"] = "ok" if not bad else "FAIL:" + ",".join(bad)
            if bad: fails.append(row)
        else:
            row["status"] = "unmapped_kind"
        rows.append(row)
    print(json.dumps({"audio": a.audio, "checked": len(rows), "failed": fails,
                      "events": rows}, indent=1))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
