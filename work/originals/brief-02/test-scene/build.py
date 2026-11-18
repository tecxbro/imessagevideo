#!/usr/bin/env python3
"""Brief-02 test scene: one live card mutating in place (270f @30fps).
The generality test: nothing grows — one object changes state. Layer
start/end windows do the mutation instead of opacity juggling."""
import json
from pathlib import Path

W, H, FPS, FRAMES = 1920, 1080, 30, 270
DUR = FRAMES / FPS
FF = "'Helvetica Neue', Helvetica, Arial, sans-serif"
E = "easeOut"

S = {"width": W, "height": H, "fps": FPS, "duration": DUR,
     "background": "#FFFFFF", "layers": []}

def L(id_, type_, **kw):
    d = {"id": id_, "type": type_}; d.update(kw); return d

def kf(**props):  # each point: (t, v) or (t, v, ease)
    out = {}
    for p, pts in props.items():
        out[p] = [{"t": pt[0], "value": pt[1],
                   **({"ease": pt[2]} if len(pt) > 2 else {})} for pt in pts]
    return out

def txt(id_, x, y, s, size, color="#111111", weight="400", anchor="start", extra=None, **kw):
    d = L(id_, "text", x=x, y=y, text=s, fontSize=size, fontFamily=FF,
          fontWeight=weight, fill=color, textAnchor=anchor)
    if extra: d.update(extra)
    d.update(kw); return d

# ---------- title bar ----------
S["layers"] += [
    L("bar-line", "rect", x=0, y=126, width=W, height=1, fill="#D8D8DC"),
    txt("bar-back", 36, 56, "‹ 12", 34, "#0A84FF"),
    L("bar-av", "circle", x=W//2-178, y=36, width=60, height=60, fill="#0A84FF"),
    txt("bar-av-g", W//2-193, 50, "✈", 30, "#FFFFFF"),
    txt("bar-name", W//2-106, 44, "Layover", 30, weight="700"),
    txt("bar-sub", W//2-106, 84, "watching UA 1140 · SFO→JFK", 20, "#8E8E93"),
]

# ---------- incoming delay alert ----------
S["layers"].append(L("alert", "group", x=44, y=170, keyframes=kf(
    opacity=[(0.0,0),(0.5,1)], y=[(0.0,200,E),(0.5,170,E)]), children=[
    L("alert-b", "rect", x=0, y=0, width=560, height=100, radius=34, fill="#E9E9EB"),
    txt("alert-t", 30, 20, "heads up — your 4:40 is delayed.\nI’m on it.", 28, lineHeight=38),
]))

# ---------- outgoing request ----------
S["layers"].append(L("req", "group", x=W-44, y=290, keyframes=kf(
    opacity=[(0.9,0),(1.4,1)], y=[(0.9,320,E),(1.4,290,E)]), children=[
    L("req-b", "rect", x=-520, y=0, width=520, height=54, radius=27, fill="#0A84FF"),
    txt("req-t", -490, 14, "book me whatever gets me home", 26, "#FFFFFF"),
]))

# ---------- THE LIVE CARD — mutation via start/end windows ----------
CX, CY, CW, CH = 44, 380, 620, 330
kids = [
    L("card-bg", "rect", x=0, y=0, width=CW, height=CH, radius=28,
      fill="#F7F7F9", stroke="#E3E3E8", strokeWidth=1.5),
    txt("card-head", 28, 24, "UA 1140 · SFO → JFK", 26, weight="700"),
    # clock chip: three texts swapping by start/end windows — time montage
    txt("clock-a", CW-28, 20, "2:12 PM", 22, "#8E8E93", anchor="end", start=0, end=5.0),
    txt("clock-b", CW-28, 20, "2:15 PM", 22, "#8E8E93", anchor="end", start=5.0, end=7.7),
    txt("clock-c", CW-28, 20, "2:18 PM", 22, "#8E8E93", anchor="end", start=7.7),
    L("card-sep", "rect", x=24, y=66, width=CW-48, height=1, fill="#E3E3E8"),

    # STATE A — finding, pips pulse (exists 1.6s–6.35s)
    L("stA", "group", x=28, y=92, start=0, end=6.35, children=[
        txt("stA-t", 0, 0, "finding alternates…", 26, "#555555"),
        L("p1", "circle", x=6,  y=56, width=16, height=16, fill="#C7C7CC",
          keyframes=kf(scaleX=[(2.4,1),(2.8,1.6),(3.2,1)], scaleY=[(2.4,1),(2.8,1.6),(3.2,1)], opacity=[(2.4,.5),(2.8,1),(3.2,.5)])),
        L("p2", "circle", x=36, y=56, width=16, height=16, fill="#C7C7CC",
          keyframes=kf(scaleX=[(2.8,1),(3.2,1.6),(3.6,1)], scaleY=[(2.8,1),(3.2,1.6),(3.6,1)], opacity=[(2.8,.5),(3.2,1),(3.6,.5)])),
        L("p3", "circle", x=66, y=56, width=16, height=16, fill="#C7C7CC",
          keyframes=kf(scaleX=[(3.2,1),(3.6,1.6),(4.0,1)], scaleY=[(3.2,1),(3.6,1.6),(4.0,1)], opacity=[(3.2,.5),(3.6,1),(4.0,.5)])),
    ]),

    # STATE B — three options stagger into the SAME place (6.3–8.0)
    L("stB", "group", x=28, y=86, start=6.3, end=8.0, children=[
        L("r1", "group", x=0, y=0, keyframes=kf(
            opacity=[(6.4,0),(6.55,1)], y=[(6.4,14,E),(6.55,0,E)]), children=[
            L("r1-b", "rect", x=0, y=0, width=CW-56, height=64, radius=18, fill="#FFFFFF", stroke="#E3E3E8", strokeWidth=1),
            txt("r1-t", 18, 18, "6:05 PM · direct · seat 21A", 24, "#222222"),
            txt("r1-p", CW-92, 18, "free", 22, "#34C759", anchor="end"),
        ]),
        L("r2", "group", x=0, y=76, keyframes=kf(
            opacity=[(6.48,0),(6.63,1)], y=[(6.48,90,E),(6.63,76,E)]), children=[
            L("r2-b", "rect", x=0, y=0, width=CW-56, height=64, radius=18, fill="#0A84FF"),
            txt("r2-t", 18, 18, "4:58 PM · direct · seat 14C", 24, "#FFFFFF", "600"),
            txt("r2-p", CW-92, 18, "free", 22, "#FFFFFF", anchor="end"),
        ]),
        L("r3", "group", x=0, y=152, keyframes=kf(
            opacity=[(6.56,0),(6.71,1)], y=[(6.56,166,E),(6.71,152,E)]), children=[
            L("r3-b", "rect", x=0, y=0, width=CW-56, height=64, radius=18, fill="#FFFFFF", stroke="#E3E3E8", strokeWidth=1),
            txt("r3-t", 18, 18, "5:30 PM · 1 stop ORD · 8F", 24, "#222222"),
            txt("r3-p", CW-92, 18, "+$41", 22, "#8E8E93", anchor="end"),
        ]),
        L("tap", "circle", x=260, y=76+32-40, width=80, height=80,
          fill="none", stroke="#0A84FF", strokeWidth=4,
          keyframes=kf(opacity=[(7.1,0),(7.2,.9),(7.45,0)],
                       scaleX=[(7.1,.4),(7.45,1.5)], scaleY=[(7.1,.4),(7.45,1.5)])),
    ]),

    # STATE C — holding (8.0–8.75; must NOT overlap stB which ends at 8.0)
    L("stC", "group", x=28, y=100, start=8.0, end=8.75, children=[
        txt("stC-t", 0, 0, "holding seat 14C…", 28, weight="600"),
        txt("stC-s", 0, 44, "fare locked · your credits applied", 22, "#8E8E93"),
    ]),

    # STATE D — confirmed (8.75→)
    L("stD", "group", x=28, y=96, start=8.75, children=[
        L("chk", "circle", x=4, y=4, width=44, height=44, fill="#34C759",
          keyframes=kf(opacity=[(8.85,0),(9.0,1)],
                       scaleX=[(8.85,.4),(9.0,1.15,E),(9.15,1)],
                       scaleY=[(8.85,.4),(9.0,1.15,E),(9.15,1)])),
        txt("chk-t", 14, 8, "✓", 26, "#FFFFFF", "700",
            keyframes=kf(opacity=[(9.0,0),(9.1,1)])),
        txt("stD-t", 64, 10, "confirmed — 4:58 PM, seat 14C", 28, weight="700"),
        txt("stD-s", 64, 50, "boarding pass added to Wallet", 22, "#555555"),
    ]),
]
S["layers"].append(L("card", "group", x=CX, y=CY, children=kids, keyframes=kf(
    opacity=[(1.6,0),(2.1,1)], y=[(1.6,CY+36,E),(2.1,CY,E)],
    scaleX=[(1.6,.96),(2.1,1)], scaleY=[(1.6,.96),(2.1,1)])))

# ---------- outgoing resolution ----------
S["layers"].append(L("done", "group", x=W-44, y=CY+CH+30, keyframes=kf(
    opacity=[(9.0,0),(9.3,1)], y=[(9.0,CY+CH+60,E),(9.3,CY+CH+30,E)]), children=[
    L("done-b", "rect", x=-360, y=0, width=360, height=54, radius=27, fill="#0A84FF"),
    txt("done-t", -330, 14, "we're good. land 9:20 🙌", 26, "#FFFFFF"),
]))

out = Path(__file__).parent / "test-scene.json"
out.write_text(json.dumps(S, indent=1))
print("wrote", out, f"{FRAMES}f / {DUR}s")
