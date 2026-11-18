#!/usr/bin/env python3
"""film-01 'Offload' — single-timeline scene generator.
1920x1080 @ 30fps -> scenes/film-01.json for scripts/engines/render.mjs --method html.
All artwork hand-authored vectors/text. Real glyph metrics via fontTools/HelveticaNeue.ttc.
Keyframe values are ABSOLUTE (they replace the attr), so positioned groups get
keyframes written against their final slot coordinates."""
import json, sys, math, random
from pathlib import Path
from fontTools.ttLib import TTCollection

_coll = TTCollection("/System/Library/Fonts/HelveticaNeue.ttc")
_FONTS = {"regular": _coll.fonts[0], "bold": _coll.fonts[1], "medium": _coll.fonts[10]}
_cmaps = {k: f.getBestCmap() for k, f in _FONTS.items()}
_hmtx = {k: f["hmtx"] for k, f in _FONTS.items()}
_upm = {k: f["head"].unitsPerEm for k, f in _FONTS.items()}
_EMOJI = set("😬😅🙌📸🚲☕👀🙄✨🔥💸🤝👍🎉🏷")

def text_w(text, size, weight="regular"):
    cmap, hmtx, upm = _cmaps[weight], _hmtx[weight], _upm[weight]
    w = 0.0
    for ch in text:
        if ch in _EMOJI or ord(ch) > 0xFFFF:
            w += size * 1.05; continue
        g = cmap.get(ord(ch))
        w += hmtx[g][0] if g else upm * 0.5
    return w * size / upm

def wrap_text(text, size, maxw, weight="regular"):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if text_w(trial, size, weight) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur); cur = word
    if cur: lines.append(cur)
    return lines

W, H, FPS = 1920, 1080, 30
FONT = "'Helvetica Neue', Helvetica, Arial, 'Apple Color Emoji', sans-serif"
BLUE = "#0A84FF"; GRAY_B = "#E9E9EB"; INK = "#111111"; SUB = "#8E8E93"
CARD_LINE = "#DCDCE1"; GREEN = "#30D158"; ORANGE = "#FF7A1A"; RED = "#E5484D"
NAVY = "#1F2A44"
WEIGHTS = {"regular": "400", "medium": "500", "bold": "700"}
OUT_X, IN_X, GAP = 1900, 96, 14

def kf(f, v, ease=None):
    d = {"t": round(f / FPS, 5), "value": v}
    if ease: d["ease"] = ease
    return d
def kf2(pairs):
    return {p: [kf(*t) for t in ks] for p, ks in pairs.items()}
def base(d, start=None, end=None):
    if start is not None: d["start"] = round(start / FPS, 5)
    if end is not None: d["end"] = round(end / FPS, 5)
    return d

def T(id, text, x, y, size, fill=INK, weight="regular", anchor="start", kfs=None,
      ls=None, lh=None, start=None, end=None):
    d = {"id": id, "type": "text", "text": text, "x": x, "y": y, "fontSize": size,
         "fontFamily": FONT, "fontWeight": WEIGHTS[weight], "fill": fill, "textAnchor": anchor}
    if ls is not None: d["letterSpacing"] = ls
    if lh is not None: d["lineHeight"] = lh
    if kfs: d["keyframes"] = kfs
    return base(d, start, end)
def R(id, x, y, w, h, fill, radius=0, kfs=None, stroke=None, sw=1, shadow=None,
      start=None, end=None, rot=None, ox=None, oy=None, opacity=None):
    d = {"id": id, "type": "rect", "x": x, "y": y, "width": w, "height": h, "fill": fill}
    if radius: d["radius"] = radius
    if kfs: d["keyframes"] = kfs
    if stroke: d["stroke"] = stroke; d["strokeWidth"] = sw
    if shadow: d["shadow"] = shadow
    if rot is not None: d["rotation"] = rot
    if ox is not None: d["originX"] = ox; d["originY"] = oy
    if opacity is not None: d["opacity"] = opacity
    return base(d, start, end)
def C(id, cx, cy, r, fill, kfs=None, stroke=None, sw=1, start=None, end=None, opacity=None):
    d = {"id": id, "type": "circle", "x": cx - r, "y": cy - r, "width": 2 * r, "height": 2 * r, "fill": fill}
    if kfs: d["keyframes"] = kfs
    if stroke: d["stroke"] = stroke; d["strokeWidth"] = sw
    if opacity is not None: d["opacity"] = opacity
    return base(d, start, end)
def P(id, d_path, fill, kfs=None, stroke=None, sw=1, x=0, y=0, start=None, end=None,
      rot=None, ox=None, oy=None, sx=None, sy=None, opacity=None, rule=None):
    d = {"id": id, "type": "path", "d": d_path, "fill": fill, "x": x, "y": y}
    if kfs: d["keyframes"] = kfs
    if stroke: d["stroke"] = stroke; d["strokeWidth"] = sw
    if rot is not None: d["rotation"] = rot
    if ox is not None: d["originX"] = ox; d["originY"] = oy
    if sx is not None: d["scaleX"] = sx
    if sy is not None: d["scaleY"] = sy
    if opacity is not None: d["opacity"] = opacity
    if rule: d["fillRule"] = rule
    return base(d, start, end)
def G(id, x, y, children, kfs=None, start=None, end=None, ox=None, oy=None,
      rot=None, opacity=None):
    d = {"id": id, "type": "group", "x": x, "y": y, "children": children}
    if kfs: d["keyframes"] = kfs
    if ox is not None: d["originX"] = ox; d["originY"] = oy
    if rot is not None: d["rotation"] = rot
    if opacity is not None: d["opacity"] = opacity
    return base(d, start, end)

BODY_FS, LH, PADX, PADY, RAD = 34, 40, 24, 17, 30
MAX_TXT_W = 560

def tail_path(w, h, side):
    if side == "out":
        return f"M {w-16} {h-18} Q {w-3} {h+1} {w+7} {h-2} Q {w-3} {h-6} {w-2} {h-20} Z"
    return f"M 16 {h-18} Q 3 {h+1} -7 {h-2} Q 3 {h-6} 2 {h-20} Z"

def bubble_kids(idp, text, side, x0=0, size=BODY_FS, maxw=MAX_TXT_W):
    lines = wrap_text(text, size, maxw)
    tw = max(text_w(l, size) for l in lines)
    w, h = tw + 2 * PADX, len(lines) * LH + 2 * PADY
    if side == "out":
        kids = [R(f"{idp}-body", x0, 0, w, h, "url(#blueg)", radius=RAD),
                P(f"{idp}-tail", tail_path(w, h, "out"), BLUE, x=x0),
                T(f"{idp}-t", "\n".join(lines), x0 + PADX, PADY + 6, size, fill="#FFF", lh=LH)]
    else:
        kids = [R(f"{idp}-body", x0, 0, w, h, GRAY_B, radius=RAD),
                P(f"{idp}-tail", tail_path(w, h, "in"), GRAY_B, x=x0),
                T(f"{idp}-t", "\n".join(lines), x0 + PADX, PADY + 6, size, fill=INK, lh=LH)]
    return kids, w, h

def arrive_at(idp, x, y, kids, f_in, rise=26, dur=9, s0=0.55, ox=None, oy=None):
    """Absolute-position arrival: pops in from below at its slot (x,y)."""
    ox = 0 if ox is None else ox
    oy = 60 if oy is None else oy
    return G(idp, x, y, kids, ox=ox, oy=oy, kfs=kf2({
        "y": [(f_in, y + rise, "easeOut"), (f_in + dur, y)],
        "scaleX": [(f_in, s0, "easeOut"), (f_in + dur, 1)],
        "scaleY": [(f_in, s0, "easeOut"), (f_in + dur, 1)],
        "opacity": [(f_in, 0), (f_in + max(4, dur - 3), 1)]}))

def typing_dots(idp, x, y, f_a, f_b):
    kids = [R(f"{idp}-b", 0, 0, 92, 52, GRAY_B, radius=26),
            P(f"{idp}-tail", tail_path(92, 52, "in"), GRAY_B)]
    for i in range(3):
        ph = i * 3
        kids.append(C(f"{idp}-d{i}", 24 + i * 22, 26, 7, "#8E8E93", kfs=kf2({
            "opacity": [(f_a, .25), (f_a + ph + 3, 1), (f_a + ph + 10, .25), (f_b, .25)]})))
    return G(idp, x, y, kids, start=f_a, end=f_b + 3, kfs=kf2({
        "opacity": [(f_a, 0), (f_a + 5, 1), (f_b - 3, 1), (f_b, 0)]}))

def avatar_layers(idp, cx, cy, r, initial, color):
    return [C(f"{idp}-c", cx, cy, r, color),
            T(f"{idp}-i", initial, cx, cy - r * 0.62, r * 1.15, fill="#FFF", weight="medium", anchor="middle")]

TAG_D = ("M 14 6 L 54 6 Q 62 6 66 14 L 92 62 Q 96 70 90 76 L 70 96 "
         "Q 64 102 56 96 L 8 48 Q 0 40 6 32 L 8 16 Q 9 6 14 6 Z "
         "M 24 26 A 10 10 0 1 0 44 26 A 10 10 0 1 0 24 26 Z")

def tag_layer(idp, x, y, s, color, kfs=None, rot=None, ox=None, oy=None, start=None, end=None):
    d = {"id": idp, "type": "path", "d": TAG_D, "fill": color, "x": x, "y": y,
         "scaleX": s, "scaleY": s, "fillRule": "evenodd"}
    if kfs: d["keyframes"] = kfs
    if rot is not None: d["rotation"] = rot
    if ox is not None: d["originX"] = ox; d["originY"] = oy
    return base(d, start, end)

def offload_avatar(idp, cx, cy, r):
    return [C(f"{idp}-c", cx, cy, r, ORANGE),
            tag_layer(f"{idp}-t", cx - r * 0.62, cy - r * 0.62, r * 1.24 / 100, "#FFF")]

def bike_kids(idp, w, h):
    kids = [R(f"{idp}-bg", 0, 0, w, h, "url(#skyg)", radius=20),
            R(f"{idp}-gr", 0, h * 0.80, w, h * 0.20, "#D8DCE7", radius=20)]
    cx1, cx2, cy, wr = w * 0.24, w * 0.76, h * 0.68, h * 0.17
    fx, fy = w * 0.46, h * 0.62
    sx, sy = w * 0.30, h * 0.38
    hx, hy = w * 0.72, h * 0.40
    kids += [
        C(f"{idp}-w1", cx1, cy, wr, "none", stroke=NAVY, sw=10),
        C(f"{idp}-w2", cx2, cy, wr, "none", stroke=NAVY, sw=10),
        P(f"{idp}-frame", f"M {cx1} {cy} L {sx} {sy} L {hx} {hy} L {cx2} {cy} "
          f"M {sx} {sy} L {fx} {fy} L {cx1} {cy} M {fx} {fy} L {hx} {hy} M {fx} {fy} L {cx2} {cy}",
          "none", stroke=NAVY, sw=11),
        P(f"{idp}-seat", f"M {sx-24} {sy-10} L {sx+28} {sy-10}", "none", stroke=ORANGE, sw=11),
        P(f"{idp}-bars", f"M {hx} {hy} L {hx+30} {hy-32} M {hx+30} {hy-32} L {hx+56} {hy-16}", "none", stroke=ORANGE, sw=11),
        C(f"{idp}-bb", fx, fy, wr * 0.26, "none", stroke=NAVY, sw=8),
        P(f"{idp}-crank", f"M {fx} {fy} L {fx-20} {fy+28} M {fx} {fy} L {fx+20} {fy-28}", "none", stroke=NAVY, sw=8)]
    return kids

def header(name, av_initial, av_color, subtitle):
    kids = [R("hd-line", 0, 118, W, 1.5, "#E8E8ED"),
            P("hd-back", "M 96 40 L 66 66 L 96 92", "none", stroke=BLUE, sw=7),
            T("hd-backn", "482", 108, 44, 32, fill=BLUE)]
    if av_initial is None:
        kids += offload_avatar("hd-av", 910, 60, 33)
    else:
        kids += avatar_layers("hd-av", 910, 60, 33, av_initial, av_color)
    kids += [T("hd-name", name, 962, 38, 36, weight="medium", anchor="middle"),
             T("hd-sub", subtitle, 962, 80, 24, fill=SUB, anchor="middle")]
    return kids

def composer():
    return [R("cp-line", 0, 992, W, 1.5, "#E8E8ED"),
            C("cp-plus", 52, 1040, 27, GRAY_B),
            T("cp-plus-t", "+", 52, 1025, 46, fill="#7C7C80", anchor="middle", weight="medium"),
            R("cp-field", 96, 1008, 1720, 66, "#FFF", radius=33, stroke="#C7C7CC", sw=1.5)]

# ---------- timeline (frames) ----------
f = dict(type0=6, typeN=42, send=54,
         dots1a=60, dots1b=78, card=80, listed=140,
         offer1=210, offer2=228, dots2a=252, dots2b=266, ican=270,
         pusha=296, pushb=318,
         nina1=326, agent1=374,
         ndots_a=436, ndots_b=448, nina2=452,
         agent2=500,
         ndots2a=540, ndots2b=552, nina3=556,
         popa=588, popb=608,
         deal=614, press=658, convert=670,
         sold=698, label=724, cash=752,
         outa=800, outb=832, enda=808)
DUR_F = 890

L = []
# ===== ENDCARD =====
end_kids = [
    tag_layer("end-tag", 800, 160, 1.0, ORANGE, rot=-10, ox=50, oy=50,
              kfs=kf2({"y": [(f["enda"], 100, "easeOut"), (f["enda"] + 10, 160)],
                       "opacity": [(f["enda"], 0), (f["enda"] + 6, 1)]})),
    T("end-wm", "offload", 960, 330, 128, weight="bold", anchor="middle", ls=-2,
      kfs=kf2({"opacity": [(f["enda"], 0), (f["enda"] + 10, 1)],
               "y": [(f["enda"], 370, "easeOut"), (f["enda"] + 12, 330)]})),
    T("end-p1", "Text it a photo.", 960, 520, 62, weight="medium", anchor="middle",
      kfs=kf2({"opacity": [(f["enda"] + 10, 0), (f["enda"] + 20, 1)]})),
    T("end-p2", "It handles the haggling.", 960, 600, 62, weight="medium", anchor="middle", fill="#3A3A3C",
      kfs=kf2({"opacity": [(f["enda"] + 18, 0), (f["enda"] + 28, 1)]})),
    R("end-pill", 795, 686, 330, 74, "#F0F0F2", radius=37, ox=960, oy=723,
      kfs=kf2({"opacity": [(f["enda"] + 30, 0), (f["enda"] + 40, 1)],
               "scaleX": [(f["enda"] + 30, .8, "easeOut"), (f["enda"] + 40, 1)],
               "scaleY": [(f["enda"] + 30, .8, "easeOut"), (f["enda"] + 40, 1)]})),
    T("end-url", "offload.chat", 960, 709, 34, fill="#3A3A3C", weight="medium", anchor="middle",
      kfs=kf2({"opacity": [(f["enda"] + 30, 0), (f["enda"] + 40, 1)]})),
]
L.append(G("endcard", 0, 0, end_kids))

# ===== WORLD =====
world = {"id": "world", "type": "group", "x": 0, "y": 0, "children": [],
         "keyframes": kf2({"x": [(f["pusha"], 0, "easeInOut"), (f["pushb"], -W),
                                 (f["popa"], -W, "easeInOut"), (f["popb"], 0)]})}

# ---------- THREAD A ----------
threadA = {"id": "threadA", "type": "group", "x": 0, "y": 0, "children": []}
threadA["children"] += header("Offload", None, ORANGE, "your selling agent")
threadA["children"] += composer()
typed = "sell this for me?"
chars = len(typed)
for i in range(1, chars + 1):
    fr = f["type0"] + round((i - 1) * (f["typeN"] - f["type0"]) / chars)
    fr_end = f["type0"] + round(i * (f["typeN"] - f["type0"]) / chars)
    if i == chars: fr_end = f["send"]
    threadA["children"].append(T(f"cp-ty{i:02d}", typed[:i], 128, 1026, 30, start=fr, end=fr_end))
threadA["children"] += [
    R("cp-sendbg", 1752, 1016, 50, 50, "url(#blueg)", radius=25,
      start=f["type0"], end=f["send"] + 2, ox=1777, oy=1041,
      kfs=kf2({"scaleX": [(f["type0"], .4, "easeOut"), (f["type0"] + 8, 1)],
               "scaleY": [(f["type0"], .4, "easeOut"), (f["type0"] + 8, 1)]})),
    P("cp-sendarr", "M 0 -14 L 0 12 M -9 -5 L 0 -14 L 9 -5", "none", stroke="#FFF", sw=5,
      x=1777, y=1041, start=f["type0"], end=f["send"] + 2)]

stackA = {"id": "stackA", "type": "group", "x": 0, "y": 0, "children": [], "keyframes": {}}
clipA = {"id": "clipA", "type": "group", "x": 0, "y": 0,
         "clip": {"x": 0, "y": 122, "width": W, "height": 866}, "children": [stackA]}
cur = 0.0
bottoms = {}          # name -> content-bottom (local stack coords)
anchors = []          # (frame, bottom) scroll targets

def record(name, h, anchor_at=None):
    global cur
    bottoms[name] = cur + h
    cur += h + GAP
    if anchor_at is not None:
        anchors.append((anchor_at, bottoms[name]))

# 0 intro agent bubble (present at f0)
k, w0, h0 = bubble_kids("b-intro", "send a photo of what you want to sell 📸", "in", x0=IN_X)
stackA["children"].append(G("intro", 0, cur, offload_avatar("av0", 30, h0 - 26, 17) + k))
record("intro", h0)

# 1 user photo + text at send
phk = [R("ph-back", 12, -10, 392, 254, "#D7DAE4", radius=22, rot=-4, ox=200, oy=120)] + bike_kids("ph", 400, 250)
stackA["children"].append(G("photo", OUT_X - 400, cur, phk, ox=400, oy=250, kfs=kf2({
    "y": [(f["send"], cur + 40, "easeOut"), (f["send"] + 9, cur)],
    "scaleX": [(f["send"], .7, "easeOut"), (f["send"] + 9, 1)],
    "scaleY": [(f["send"], .7, "easeOut"), (f["send"] + 9, 1)],
    "opacity": [(f["send"], 0), (f["send"] + 5, 1)]})))
record("photo", 250, None)

k, w1, h1 = bubble_kids("b-req", typed, "out")
stackA["children"].append(G("req", OUT_X - w1, cur, k, ox=w1, oy=h1, kfs=kf2({
    "y": [(f["send"], cur + 34, "easeOut"), (f["send"] + 9, cur)],
    "scaleX": [(f["send"], .55, "easeOut"), (f["send"] + 9, 1)],
    "scaleY": [(f["send"], .55, "easeOut"), (f["send"] + 9, 1)],
    "opacity": [(f["send"], 0), (f["send"] + 5, 1)]})))
record("req", h1, f["send"])  # single scroll anchor lands photo+text together

# 2 dots -> listing card
stackA["children"].append(typing_dots("dotsA", IN_X, cur, f["dots1a"], f["dots1b"]))
lc_w, lc_h = 660, 430
bk = bike_kids("lc-img", lc_w - 28, 210)
for ch in bk:  # offset into card
    ch["x"] = ch.get("x", 0) + 14; ch["y"] = ch.get("y", 0) + 14
lc_kids = [
    R("lc-card", 0, 0, lc_w, lc_h, "#FFF", radius=26, stroke=CARD_LINE, sw=1.5,
      shadow={"x": 0, "y": 10, "blur": 28, "color": "rgba(0,0,0,0.14)"}),
    *bk,
    T("lc-title", "Fuji Feather · 2023", 28, 244, 40, weight="medium"),
    T("lc-sub", "Like new · Mission District", 28, 292, 28, fill=SUB),
    R("lc-price", 28, 336, 130, 62, "url(#blueg)", radius=31),
    T("lc-pricet", "$140", 93, 352, 36, fill="#FFF", weight="medium", anchor="middle"),
    R("lc-btn", 178, 336, 454, 62, "#F5F5F7", radius=31, stroke=CARD_LINE, sw=1.5),
    T("lc-btnt", "Listed on Marketplace ✓", 405, 352, 30, anchor="middle", weight="medium"),
    T("lc-status", "Listed · just now · offers will land here", 28, 408, 24, fill=SUB,
      kfs=kf2({"opacity": [(f["listed"], 0), (f["listed"] + 10, 1)]})),
]
stackA["children"].append(G("listing", IN_X, cur, lc_kids, ox=0, oy=50, kfs=kf2({
    "y": [(f["card"], cur + 34), (f["card"] + 7, cur - 7, "easeOut"), (f["card"] + 12, cur)],
    "scaleX": [(f["card"], .22), (f["card"] + 7, 1.05, "easeOut"), (f["card"] + 12, 1)],
    "scaleY": [(f["card"], .22), (f["card"] + 7, 1.05, "easeOut"), (f["card"] + 12, 1)],
    "opacity": [(f["card"], 0), (f["card"] + 4, 1)]})))
record("listing", lc_h + 6, f["card"])

# 3 offer chips
for oid, price, name, at in [("o1", "$40", "· Nina “for tonight?”", f["offer1"]),
                             ("o2", "$60", "· Marcus", f["offer2"])]:
    cw, chh = 330, 88
    kids = [R(f"{oid}-c", 0, 0, cw, chh, "#FFF", radius=22, stroke=CARD_LINE, sw=1.5,
              shadow={"x": 0, "y": 4, "blur": 14, "color": "rgba(0,0,0,0.10)"}),
            T(f"{oid}-p", price, 24, 26, 36, weight="bold"),
            T(f"{oid}-n", name, 24 + text_w(price, 36, "bold") + 12, 33, 26, fill=SUB)]
    stackA["children"].append(arrive_at(oid, IN_X, cur, kids, at, rise=24, dur=8, ox=0, oy=50))
    record(oid, chh, at)

# 4 agent line
stackA["children"].append(typing_dots("dotsB", IN_X, cur, f["dots2a"], f["dots2b"]))
k, w2, h2 = bubble_kids("b-ican", "I can work with this.", "in", x0=IN_X)
stackA["children"].append(G("ican", 0, cur, offload_avatar("av1", 30, h2 - 26, 17) + k,
    ox=IN_X, oy=h2, kfs=kf2({
    "y": [(f["ican"], cur + 26, "easeOut"), (f["ican"] + 8, cur)],
    "scaleX": [(f["ican"], .55, "easeOut"), (f["ican"] + 8, 1)],
    "scaleY": [(f["ican"], .55, "easeOut"), (f["ican"] + 8, 1)],
    "opacity": [(f["ican"], 0), (f["ican"] + 5, 1)]})))
record("ican", h2, f["ican"])

# 5 deal card
dc_w, dc_h = 640, 330
dc_kids = [
    R("dc-c", 0, 0, dc_w, dc_h, "#FFF", radius=26, stroke=CARD_LINE, sw=1.5,
      shadow={"x": 0, "y": 10, "blur": 28, "color": "rgba(0,0,0,0.14)"}),
    T("dc-h", "OFFER — NINA", 28, 28, 24, fill=SUB, weight="medium", ls=3),
    T("dc-p", "$110", 28, 66, 76, weight="bold"),
    T("dc-s", "she picks up tonight, cash", 28, 156, 30),
    T("dc-u", "you made a sale.", 28, 196, 26, fill=SUB),
    R("dc-take", 28, 240, 288, 66, "url(#blueg)", radius=33,
      kfs=kf2({"opacity": [(f["convert"] + 4, 1), (f["convert"] + 12, .35)]})),
    T("dc-taket", "Take it", 172, 258, 32, fill="#FFF", weight="medium", anchor="middle",
      kfs=kf2({"opacity": [(f["convert"] + 4, 1), (f["convert"] + 12, .35)]})),
    R("dc-keep", 332, 240, 280, 66, "#F5F5F7", radius=33, stroke=CARD_LINE, sw=1.5,
      kfs=kf2({"opacity": [(f["convert"] + 4, 1), (f["convert"] + 12, .35)]})),
    T("dc-keept", "Keep haggling", 472, 258, 30, anchor="middle",
      kfs=kf2({"opacity": [(f["convert"] + 4, 1), (f["convert"] + 12, .35)]})),
    # press overlay: darkens only the Take-it pill
    R("dc-press", 28, 240, 288, 66, "#000", radius=33, opacity=0,
      kfs=kf2({"opacity": [(f["press"], 0), (f["press"] + 2, .22),
                           (f["press"] + 8, .22), (f["press"] + 12, 0)]})),
    # SOLD stamp lands on THIS card (callback object)
    {"id": "sold", "type": "group", "x": 478, "y": 118, "rotation": -9,
     "originX": 0, "originY": 0, "children": [
        R("sold-box", -150, -46, 300, 92, "none", radius=14, stroke=RED, sw=8),
        T("sold-t", "SOLD", 0, -30, 56, fill=RED, weight="bold", anchor="middle", ls=8)],
     "keyframes": kf2({
        "scaleX": [(f["sold"], 2.2), (f["sold"] + 4, .94, "easeOut"), (f["sold"] + 7, 1)],
        "scaleY": [(f["sold"], 2.2), (f["sold"] + 4, .94, "easeOut"), (f["sold"] + 7, 1)],
        "opacity": [(f["sold"], 0), (f["sold"] + 2, 1)]})},
]
stackA["children"].append(G("deal", IN_X, cur, dc_kids, ox=0, oy=50, kfs=kf2({
    "y": [(f["deal"], cur + 34), (f["deal"] + 7, cur - 6, "easeOut"), (f["deal"] + 12, cur)],
    "scaleX": [(f["deal"], .3), (f["deal"] + 7, 1.03, "easeOut"), (f["deal"] + 12, 1)],
    "scaleY": [(f["deal"], .3), (f["deal"] + 7, 1.03, "easeOut"), (f["deal"] + 12, 1)],
    "opacity": [(f["deal"], 0), (f["deal"] + 5, 1)]})))
record("deal", dc_h, f["deal"])

# 6 outgoing "take the $110"
k, w3, h3 = bubble_kids("b-take", "take the $110 🙌", "out")
stackA["children"].append(G("take", OUT_X - w3, cur, k, ox=w3, oy=h3, kfs=kf2({
    "y": [(f["convert"], cur + 26, "easeOut"), (f["convert"] + 8, cur)],
    "scaleX": [(f["convert"], .55, "easeOut"), (f["convert"] + 8, 1)],
    "scaleY": [(f["convert"], .55, "easeOut"), (f["convert"] + 8, 1)],
    "opacity": [(f["convert"], 0), (f["convert"] + 5, 1)]})))
record("take", h3, f["convert"])

# 7 shipping label
sc_w, sc_h = 560, 300
sc_kids = [
    R("sc-c", 0, 0, sc_w, sc_h, "#FFF", radius=22, stroke=CARD_LINE, sw=1.5,
      shadow={"x": 0, "y": 6, "blur": 18, "color": "rgba(0,0,0,0.12)"}),
    T("sc-h", "SHIPPING LABEL", 28, 26, 24, fill=SUB, weight="medium", ls=2),
    T("sc-to", "Nina K. · San Francisco", 28, 66, 32, weight="medium"),
    T("sc-fw", "Prepaid · drop off anytime", 28, 108, 24, fill=SUB)]
bx = 28
for i, bw in enumerate([4, 2, 6, 3, 8, 2, 4, 5, 2, 7, 3, 4, 2, 6, 4, 3, 2, 5, 7, 2, 4, 3, 6, 2, 4, 5, 3, 2, 6, 4]):
    sc_kids.append(R(f"sc-bb{i}", bx, 150, bw * 2, 70, "#111111")); bx += bw * 2 + 5
rnd = random.Random(7)
for gy in range(6):
    for gx in range(6):
        corner = (gx < 2 and gy < 2) or (gx > 3 and gy < 2) or (gx < 2 and gy > 3)
        if rnd.random() < .45 or corner:
            sc_kids.append(R(f"sc-q{gy}{gx}", 420 + gx * 16, 150 + gy * 16, 10, 10, "#111111"))
stackA["children"].append(G("ship", IN_X, cur, sc_kids, ox=0, oy=40, kfs=kf2({
    "x": [(f["label"], IN_X - 80, "easeOut"), (f["label"] + 10, IN_X)],
    "opacity": [(f["label"], 0), (f["label"] + 6, 1)]})))
record("ship", sc_h, f["label"])

# 8 cash pill
cp_w, cp_h = 430, 74
cp_kids = [R("cash-p", 0, 0, cp_w, cp_h, GREEN, radius=37),
           T("cash-t", "$110 sent to you ✓", cp_w / 2, 19, 32, fill="#FFF", weight="medium", anchor="middle")]
stackA["children"].append(G("cash", IN_X, cur, cp_kids, ox=0, oy=40, kfs=kf2({
    "scaleX": [(f["cash"], .5, "easeOut"), (f["cash"] + 9, 1)],
    "scaleY": [(f["cash"], .5, "easeOut"), (f["cash"] + 9, 1)],
    "y": [(f["cash"], cur + 24, "easeOut"), (f["cash"] + 9, cur)],
    "opacity": [(f["cash"], 0), (f["cash"] + 6, 1)]})))
record("cash", cp_h, f["cash"])

# ---- stack scroll ----
ANCHOR = 950
sk = [(0, ANCHOR - bottoms["intro"], "linear")]
y_prev = ANCHOR - bottoms["intro"]
for at, bottom in anchors:
    target = ANCHOR - bottom
    if abs(target - y_prev) < 1:
        continue
    sk.append((at + 2, y_prev, "linear"))
    sk.append((at + 12, target, "easeInOut"))
    y_prev = target
stackA["keyframes"] = kf2({"y": sk})
threadA["children"].append(clipA)
threadA["keyframes"] = kf2({"opacity": [(f["outa"], 1), (f["outb"], 0)],
                            "y": [(f["outa"], 0, "easeInOut"), (f["outb"], -160)]})
world["children"].append(threadA)

# ---------- THREAD B ----------
threadB = {"id": "threadB", "type": "group", "x": W, "y": 0, "children": []}
threadB["children"] += header("Nina K.", "N", "#5E5CE6", "buyer · Marketplace")
threadB["children"] += composer()
threadB["children"].append(G("neg-pill", 0, 140, [
    R("negp-b", 700, 0, 520, 54, "#F0F0F2", radius=27),
    T("negp-t", "🤝 offload is negotiating for you", 960, 15, 26, fill="#3A3A3C",
      anchor="middle", weight="medium")],
    kfs=kf2({"opacity": [(f["pushb"], 0), (f["pushb"] + 10, 1)]})))

stackB = {"id": "stackB", "type": "group", "x": 0, "y": 0, "children": []}
clipB = {"id": "clipB", "type": "group", "x": 0, "y": 0,
         "clip": {"x": 0, "y": 122, "width": W, "height": 866}, "children": [stackB]}
cyB = 214
seqB = [
    ("n1", "$80 is my max 😬", "in", f["nina1"], True),
    ("a1", "$140 was fair at noon. I'll do $120 tonight.", "out", f["agent1"], False),
    ("nd1", None, "in", (f["ndots_a"], f["ndots_b"]), True),
    ("n2", "$100 cash tonight?", "in", f["nina2"], True),
    ("a2", "$110 tonight. In or out?", "out", f["agent2"], False),
    ("nd2", None, "in", (f["ndots2a"], f["ndots2b"]), True),
    ("n3", "fine. 110.", "in", f["nina3"], True),
]
for sid, text, side, at, is_in in seqB:
    if text is None:
        stackB["children"].append(typing_dots(sid, IN_X, cyB, at[0], at[1]))
        continue  # dots do NOT consume a row; next bubble takes this slot
    k, w, h = bubble_kids(sid, text, side, x0=IN_X if is_in else 0)
    x = 0 if is_in else OUT_X - w
    kids = (avatar_layers(f"{sid}-av", 30, h - 24, 16, "N", "#5E5CE6") + k) if is_in else k
    stackB["children"].append(
        G(sid, x, cyB, kids, ox=0 if is_in else w, oy=h, kfs=kf2({
            "y": [(at, cyB + 26, "easeOut"), (at + 8, cyB)],
            "scaleX": [(at, .55, "easeOut"), (at + 8, 1)],
            "scaleY": [(at, .55, "easeOut"), (at + 8, 1)],
            "opacity": [(at, 0), (at + 5, 1)]})))
    cyB += h + GAP
threadB["children"].append(clipB)
threadB["keyframes"] = kf2({"opacity": [(f["outa"], 1), (f["outb"], 0)],
                            "y": [(f["outa"], 0, "easeInOut"), (f["outb"], -160)]})
world["children"].append(threadB)

L.append(world)

scene = {
    "width": W, "height": H, "fps": FPS, "duration": DUR_F / FPS,
    "background": "#FFFFFF",
    "title": "Offload — text it a photo, it handles the haggling",
    "gradients": [
        {"id": "blueg", "type": "linear", "x1": "0%", "y1": "0%", "x2": "0%", "y2": "100%",
         "stops": [{"offset": "0%", "color": "#3AA0FF"}, {"offset": "100%", "color": "#0A84FF"}]},
        {"id": "skyg", "type": "linear", "x1": "0%", "y1": "0%", "x2": "0%", "y2": "100%",
         "stops": [{"offset": "0%", "color": "#EEF1F7"}, {"offset": "100%", "color": "#DFE3ED"}]}],
    "layers": L,
    "source": {"notes": "Original direction. Authored timing/layout; motif phases informed by motion-catalog entries (anchored card arrival, typing->reply, choice->outgoing). Assets: hand-authored vectors; Helvetica Neue measured via fontTools."},
}
out = Path(__file__).parent / "scenes" / "film-01.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(scene, indent=1))
print("wrote", out, "| layers:", len(L), "| stackA items:", len(stackA["children"]),
      "| stackB items:", len(stackB["children"]), "| dur:", DUR_F / FPS, "s")
