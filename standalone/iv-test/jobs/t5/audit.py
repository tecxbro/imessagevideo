#!/usr/bin/env python3
"""Audit every bundled seed motion: checksum, fresh-process render, preview parity, motion presence."""
import hashlib, json, subprocess, sys
from pathlib import Path

SKILL = Path("/Users/darshan/Documents/video-analysis/imessagevideo-dl/skill/imessage-video")
PY = "/Users/darshan/Documents/video-analysis/.venv/bin/python"
OUT = Path("/Users/darshan/Documents/video-analysis/iv-test/jobs/t5")
RENDERS = OUT / "renders"
RENDERS.mkdir(parents=True, exist_ok=True)

def probe(path):
    r = subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-count_frames",
                        "-show_entries","stream=width,height,avg_frame_rate,nb_read_frames",
                        "-of","json",str(path)],capture_output=True,text=True)
    if r.returncode: return None
    s = json.loads(r.stdout)["streams"][0]
    return {"w":s["width"],"h":s["height"],"fps":s["avg_frame_rate"],"frames":int(s["nb_read_frames"])}

def mae_max(a, b):
    """Per-frame max mean-abs-diff between two videos via ffmpeg rawvideo, plus motion presence."""
    import numpy as np
    def frames(p):
        info = probe(p)
        w,h = info["w"],info["h"]
        proc = subprocess.Popen(["ffmpeg","-nostdin","-v","error","-i",str(p),"-map","0:v:0",
            "-an","-vf",f"scale={w}:{h}","-pix_fmt","rgb24","-f","rawvideo","pipe:1"],stdout=subprocess.PIPE)
        buf = proc.stdout.read()
        proc.wait()
        n = len(buf)//(w*h*3)
        return np.frombuffer(buf[:n*w*h*3],dtype=np.uint8).reshape(n,h,w,3), info
    fa,ia = frames(a); fb,ib = frames(b)
    n = min(len(fa),len(fb))
    if n == 0: return {"error":"no frames"}
    d = np.abs(fa[:n].astype(np.int16)-fb[:n].astype(np.int16)).mean(axis=(1,2,3))
    # motion presence in the fresh render: max consecutive-frame diff
    md = np.abs(np.diff(fb.astype(np.int16),axis=0)).mean(axis=(1,2,3)) if len(fb)>1 else np.array([0.])
    return {"paired":n,"a_frames":len(fa),"b_frames":len(fb),"max_mae_vs_preview":float(d.max()),
            "mean_mae_vs_preview":float(d.mean()),"render_motion_max_delta":float(md.max()),
            "render_motion_mean_delta":float(md.mean())}

catalog = json.loads((SKILL/"assets/seed/catalog.json").read_text())
results = {}
for row in catalog["entries"]:
    rid = row["id"]
    rec = {"id": rid}
    try:
        pv = SKILL/"assets"/"seed"/row["preview"]
        impl = SKILL/"assets"/"seed"/row["implementation"]
        rec["preview_exists"] = pv.is_file()
        rec["impl_exists"] = impl.is_file()
        rec["sha_ok"] = pv.is_file() and hashlib.sha256(pv.read_bytes()).hexdigest() == row["sha256"]
        out = RENDERS/f"{rid}.mp4"
        r = subprocess.run([PY,"scripts/recipes.py","render",rid,"--out",str(out)],
                           cwd=SKILL, capture_output=True, text=True, timeout=600)
        rec["render_rc"] = r.returncode
        if r.returncode:
            rec["render_error"] = (r.stderr or r.stdout)[-800:]
        elif out.is_file():
            rec["render_probe"] = probe(out)
            rec["preview_probe"] = probe(pv)
            rec.update(mae_max(pv, out))
    except Exception as e:
        rec["exception"] = str(e)[:500]
    results[rid] = rec
    print(rid, "OK" if rec.get("paired") else "FAIL", json.dumps({k:v for k,v in rec.items() if k not in ("id",)}, default=str)[:300], flush=True)

(OUT/"audit-results.json").write_text(json.dumps(results,indent=1))
ok = [k for k,v in results.items() if v.get("paired") and v.get("max_mae_vs_preview",9e9)<3 and v.get("render_motion_max_delta",0)>0.05]
print("\nPASS", len(ok), "of", len(results))
print("failures:", [k for k in results if k not in ok])
