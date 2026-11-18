#!/usr/bin/env python3
"""film1_score.py — build a cue sheet for creative's film-01 from its
shot-plan sound_events + the visible-action inventory of the delivered mp4.

Inputs: shot-plan.json (creative), picture mp4 path.
Output: cue-sheet JSON for stem_build.py (all frames = delivered picture).

Kind→asset routing (all provenance-clean):
  typing                  -> CC0 single-key recordings (rotated), -13 dB, attack
  message_send            -> procedural air_whoosh, -10 dB, onset
  message_arrival         -> kenney_drop_001 (CC0), -14 dB, attack
  card_arrival            -> kenney_drop_002 (CC0, distinct from msgs), -14 dB
  tap                     -> kenney_click_001 (CC0), -14 dB, attack
  card_swoosh             -> procedural card_swoosh, -11 dB, onset
  low_impact              -> procedural low_impact, -10 dB, onset
  glass_confirm           -> procedural glass_confirm, -15 dB, onset
  digital_sparkle         -> procedural digital_sparkle, -16 dB, onset
"""
import json, sys, argparse

AR = "resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation"
P, S = AR + "/library/prepared", AR + "/synthesis/bank"
KEYS = ["key_001", "key_011", "key_023", "key_029"]

ROUTES = {
 "typing":          (P, "key_ROT", -13.0, "attack"),
 "message_send":    (S, "air_whoosh", -10.0, "onset"),
 "message_arrival": (P, "kenney_drop_001", -14.0, "attack"),
 "card_arrival":    (P, "kenney_drop_002", -14.0, "attack"),
 "tap":             (P, "kenney_click_001", -14.0, "attack"),
 "card_swoosh":     (S, "card_swoosh", -11.0, "onset"),
 "low_impact":      (S, "low_impact", -10.0, "onset"),
 "glass_confirm":   (S, "glass_confirm", -15.0, "onset"),
 "digital_sparkle": (S, "digital_sparkle", -16.0, "onset"),
}

def build(plan_path, picture_path, sha, out_path, extra_events=None):
    plan = json.load(open(plan_path))
    ev, ki = [], 0
    for sh in plan["shots"]:
        for se in sh.get("sound_events", []):
            k, f = se["kind"], se.get("frame")
            if f is None:
                continue  # e.g. typing w/o fixed frame — fill from picture evidence
            base, name, g, al = ROUTES[k]
            fn = KEYS[ki % len(KEYS)] + ".wav" if name == "key_ROT" else name + ".wav"
            if name == "key_ROT": ki += 1
            ev.append({"frame": f, "kind": k, "asset": f"{base}/{fn}",
                       "gain_db": g, "align": al, "pan": 0.0})
    if extra_events:
        ev += extra_events
    sheet = {"schema": "sound-agent-cue-sheet/1",
             "picture": {"file": picture_path, "sha256": sha,
                         "fps": str(plan.get("fps", 30)), "frames": plan["shots"][-1]["end_frame_exclusive"]},
             "basis": "creative shot-plan declared sound_events; assets/routing by sound agent",
             "events": sorted(ev, key=lambda e: e["frame"])}
    json.dump(sheet, open(out_path, "w"), indent=1)
    print(f"{len(ev)} events -> {out_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("picture"); ap.add_argument("sha"); ap.add_argument("out")
    a = ap.parse_args()
    build(a.plan, a.picture, a.sha, a.out)
