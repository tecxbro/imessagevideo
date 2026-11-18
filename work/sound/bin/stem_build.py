#!/usr/bin/env python3
"""stem_build.py — place audio assets at frame-exact offsets into a 48kHz
stereo stem. Pure stdlib (wave/struct); assets decoded via ffmpeg to s16.

Cue sheet: JSON list of events:
  {frame, kind, asset, gain_db, pan(-1..1), align: attack|onset, silence?: true}

- attack: align the asset's dominant early peak (max |x| in first 80 ms)
  to the event sample. For clicks/keys/drops.
- onset: align first sample that exceeds -55 dBFS to the event sample.
  For whooshes/movement.
- silence: no audio placed (recorded deliberate silence).

Output: s24 WAV at --frames/--fps exact span + JSON placement report
(event_sample, written_start, aligned_offset_samples, clip_samples,
peak_dbfs) for verification against cue_check.py.
"""
import json, math, struct, subprocess, sys, wave, argparse

SR = 48000

def load_asset(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2",
                        "-ar", str(SR), "-f", "s16le", "-"],
                       capture_output=True, check=True)
    n = len(p.stdout) // 4
    d = struct.unpack("<%dh" % (n * 2), p.stdout)
    return [(d[i], d[i + 1]) for i in range(0, n * 2, 2)]

def attack_offset(samps):
    lim = min(len(samps), int(0.080 * SR))
    bi, bv = 0, 0
    for i in range(lim):
        v = max(abs(samps[i][0]), abs(samps[i][1]))
        if v > bv:
            bv, bi = v, i
    return bi

def onset_offset(samps):
    thr = int(0.0018 * 32768)  # ~-55 dBFS
    for i in range(min(len(samps), int(0.4 * SR))):
        if max(abs(samps[i][0]), abs(samps[i][1])) >= thr:
            return i
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("out_wav")
    ap.add_argument("--frames", type=int, required=True)
    ap.add_argument("--fps", default="30000/1001")
    ap.add_argument("--report", default=None)
    args = ap.parse_args()

    num, den = (float(x) for x in args.fps.split("/")) if "/" in args.fps else (float(args.fps), 1.0)
    fps = num / den
    total = int(round(args.frames * SR / fps))
    buf = [[0.0, 0.0] for _ in range(total)]

    sheet = json.load(open(args.sheet))
    evs = sheet["events"] if isinstance(sheet, dict) else sheet
    cache = {}
    report = []
    for e in evs:
        t_sample = int(round(e["frame"] * SR / fps))
        if e.get("silence"):
            report.append({"frame": e["frame"], "kind": e["kind"],
                           "status": "intentional_silence"})
            continue
        apath = e["asset"]
        if apath not in cache:
            cache[apath] = load_asset(apath)
        samps = cache[apath]
        g = 10 ** (e.get("gain_db", 0.0) / 20.0)
        pan = e.get("pan", 0.0)
        gl = g * math.cos((pan + 1) * math.pi / 4)
        gr = g * math.sin((pan + 1) * math.pi / 4)
        off = attack_offset(samps) if e.get("align", "attack") == "attack" else onset_offset(samps)
        start = t_sample - off
        w0 = max(0, start)
        w1 = min(total, start + len(samps))
        peak = 0
        for i in range(w0, w1):
            l, r = samps[i - start]
            nl = buf[i][0] + (l / 32768.0) * gl
            nr = buf[i][1] + (r / 32768.0) * gr
            buf[i] = [nl, nr]
            if abs(nl) > peak: peak = abs(nl)
            if abs(nr) > peak: peak = abs(nr)
        report.append({"frame": e["frame"], "kind": e["kind"],
                       "asset": apath.split("/")[-1],
                       "event_sample": t_sample,
                       "written_start_sample": w0,
                       "aligned_offset_samples": w0 - t_sample,
                       "clip_samples": w1 - w0,
                       "status": "placed"})

    data = bytearray()
    clip = 0
    for l, r in buf:
        for v in (l, r):
            if v > 1.0: v, clip = 1.0, clip + 1
            if v < -1.0: v, clip = -1.0, clip + 1
            data += int(v * 8388607).to_bytes(3, "little", signed=True)
    with wave.open(args.out_wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR)
        w.writeframes(bytes(data))
    pk = 20 * math.log10(max(1e-9, max(max(abs(l), abs(r)) for l, r in buf))) if buf else -120
    rep = {"out": args.out_wav, "samples": total, "fps": args.fps,
           "frames": args.frames, "peak_dbfs": round(pk, 2),
           "clipped_samples": clip, "events": report}
    if args.report:
        json.dump(rep, open(args.report, "w"), indent=1)
    print(json.dumps({k: rep[k] for k in ("out", "samples", "peak_dbfs", "clipped_samples")}))

if __name__ == "__main__":
    main()
