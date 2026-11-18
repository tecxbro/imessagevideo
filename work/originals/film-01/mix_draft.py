#!/usr/bin/env python3
"""Draft UI-only mix for film-01. Renders cues.json through the skill's
procedural ui_synth.py and writes exports/ui-draft.wav (48k stereo).
No recorded audio inputs; sound agent owns the final score/bed."""
import json, sys, wave
from pathlib import Path
import numpy as np

SKILL = Path("/Users/darshan/Documents/ChatGPT/imv-wt/creative/skill/imessage-motion-recreation")
sys.path.insert(0, str(SKILL / "references/ui-audio/audio-recreation/synthesis"))
import ui_synth

HERE = Path(__file__).parent
cues = json.loads((HERE / "cues.json").read_text())
FPS, SR = cues["fps"], cues["sample_rate"]
n_total = round(cues["frames"] / FPS * SR)
mix = np.zeros((n_total, 2), dtype=np.float64)

def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * (2**23 - 1)).astype(np.int32)
    b = pcm.astype("<i4").tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(4); w.setframerate(SR)
        w.writeframes(b)

for i, e in enumerate(cues["events"]):
    if e["kind"] == "silence_marker":
        continue
    t0 = e["frame"] / FPS
    x = ui_synth.render(e["kind"], pitch=e.get("pitch", 1.0),
                        energy=e.get("energy", 0.75), pan=e.get("pan", 0.0),
                        seed=1000 + i)
    off = int(round(t0 * SR))
    end = min(n_total, off + len(x))
    if end > off:
        mix[off:end] += x[: end - off]

# gentle master trim to -3dBFS ceiling and normalize bus
peak = np.max(np.abs(mix))
if peak > 10 ** (-3 / 20):
    mix *= (10 ** (-3 / 20)) / peak
out = HERE / "exports" / "ui-draft.wav"
write_wav(out, mix)
print("wrote", out, "seconds:", round(len(mix) / SR, 2), "peak:", round(float(np.max(np.abs(mix))), 3))
