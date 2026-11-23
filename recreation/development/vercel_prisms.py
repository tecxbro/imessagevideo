#!/usr/bin/env python3
"""Author the gallery's 724-frame prism study as editable measured vector layers."""

import argparse
from fractions import Fraction
import json
from math import hypot, cos, sin, tau
from pathlib import Path


RATE = Fraction(60000, 1001)
FRAME_COUNT = 724
# Measurements at 960×540: front apex, lower left, lower right and far rim.
# Vertices are fitted to edge pixels, with occluded wire intersections inferred.
POSES = {
    0: ((310, 278), (258, 353), (363, 413), (700, 257)),
    255: ((310, 278), (258, 353), (363, 413), (700, 257)),
    269: ((313, 276), (261, 351), (365, 412), (699, 257)),
    290: ((322, 273), (271, 346), (375, 408), (693, 258)),
    312: ((340, 264), (288, 338), (392, 398), (679, 265)),
    336: ((365, 253), (313, 327), (418, 387), (654, 276)),
    354: ((391, 240), (335, 319), (444, 374), (635, 284)),
    376: ((426, 223), (361, 313), (480, 352), (613, 290)),
    398: ((454, 209), (385, 310), (511, 331), (591, 293)),
    410: ((465, 204), (397, 308), (524, 321), (579, 294)),
    424: ((474, 200), (408, 307), (534, 312), (567, 297)),
    436: ((478, 198), (415, 305), (539, 308), (557, 299)),
    448: ((480, 199), (418, 304), (542, 305), (550, 302)),
    459: ((481, 197), (418, 305), (545, 305), (545, 305)),
    470: ((480, 198), (418, 304), (542, 304), (542, 304)),
    480: ((480, 200), (419, 304), (541, 304), (541, 304)),
}


def seconds(frame):
    return frame / float(RATE)


def track(points, ease="linear"):
    return [{"t": seconds(frame), "value": value, "ease": ease} for frame, value in points]


def line(points, close=False):
    p = " L".join(f"{x:.3f} {y:.3f}" for x, y in points)
    return "M" + p + (" Z" if close else "")


def dashed(points):
    segments = []
    for a, b in zip(points, points[1:] + points[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = hypot(dx, dy)
        for start in range(0, int(length), 6):
            end = min(start + 3, length)
            segments.append(line([(a[0] + d * dx / length, a[1] + d * dy / length)
                                  for d in (start, end)]))
    return " ".join(segments)


def geometry(pose):
    origin, left, right, far = pose
    front = [(x - origin[0], y - origin[1]) for x, y in (origin, left, right)]
    delta = (far[0] - right[0], far[1] - right[1])
    back, next_front, next_back = [
        [(x + delta[0] * f, y + delta[1] * f) for x, y in front]
        for f in (0.465, 0.535, 1)
    ]
    return {
        "front-face": line(front, True),
        "front-outline": line([front[0], back[0], back[2], front[2]]),
        "front-rear-edges": line([front[1], back[1], back[0]]) + " " + line([back[1], back[2]]),
        "backend-outline": line([next_front[0], next_back[0], next_back[2], next_front[2]], True)
                           + " " + line([next_front[0], next_front[1], next_front[2]]),
        "backend-rear-edges": line([next_front[1], next_back[1], next_back[0]]) + " "
                              + line([next_back[1], next_back[2]]),
        "backend-dashes": dashed([next_front[0], next_back[0], next_back[2], next_front[2]]),
    }


def interpolate(keys, frame):
    for a, b in zip(keys, keys[1:]):
        if frame <= b:
            progress = (frame - a) / (b - a)
            return tuple(tuple(start + (stop - start) * progress for start, stop in zip(p, q))
                         for p, q in zip(POSES[a], POSES[b]))
    return POSES[keys[-1]]


def label(identity, x, y, leader, triangle, opacity):
    tx, ty = triangle
    marker = line([(tx, ty), (tx - 7.5, ty + 13), (tx + 7.5, ty + 13)], True)
    children = [
        {"type": "text", "id": f"{identity}-copy", "x": x, "y": y,
         "fontFamily": "Arial", "fontSize": 15, "fill": "#ffffff", "text": identity.upper()},
        {"type": "path", "id": f"{identity}-marker", "d": marker, "fill": "#ffffff"},
        {"type": "path", "id": f"{identity}-leader", "d": line(leader), "fill": "none",
         "stroke": "#777777", "strokeWidth": 0.8},
        {"type": "circle", "id": f"{identity}-pin", "x": leader[0][0] - 2.5,
         "y": leader[0][1] - 2.5, "width": 5, "height": 5, "fill": "#ffffff"},
    ]
    if identity == "backend":
        children[1]["keyframes"] = {"opacity": track([(0, 0), (159, 0), (168, 1)])}
        rosette = [(tx + (8 if i % 2 == 0 else 5.5) * cos(i * tau / 16),
                    ty + 7 + (8 if i % 2 == 0 else 5.5) * sin(i * tau / 16)) for i in range(16)]
        children.append({"type": "path", "id": "backend-rosette", "d": line(rosette, True),
                         "fill": "none", "stroke": "#ffffff", "strokeWidth": 2,
                         "keyframes": {"opacity": track([(0, 1), (159, 1), (168, 0)])}})
    return {"type": "group", "id": f"{identity}-annotation", "children": children,
            "keyframes": {"opacity": track(opacity)}}


def scene(first):
    keys = [0, 255, 480] if first else list(POSES)
    frames = [0, *range(255, 481)]
    states = [interpolate(keys, f) for f in frames]
    vectors = [geometry(pose) for pose in states]
    front_fade = [(0, 1), (668, 1), (674, .93), (680, .83), (686, .68), (692, .51),
                  (698, .345), (704, .20), (710, .09), (716, .024), (723, 0)]
    layers = []
    for identity, initial in vectors[0].items():
        fade = (front_fade if identity == "front-face" else
                [(0, 1), (108, 1), (147, 0)] if identity == "backend-dashes" else
                [(0, 0), (108, 0), (147, 1), (448, 1), (459, 0)] if identity == "backend-outline" else
                [(0, 1), (448, 1), (459, 0)])
        layers.append({
            "id": identity, "type": "path", "d": initial,
            "fill": "#fdfdfd" if identity == "front-face" else "none",
            "stroke": "#353535" if identity.endswith("edges") else "#c9c9c9",
            "strokeWidth": 0 if identity == "front-face" else 0.9,
            "keyframes": {"d": track(zip(frames, [v[identity] for v in vectors]), "hold"),
                          "opacity": track(fade)},
        })
    camera = {"type": "group", "id": "prism-camera", "children": layers,
              "keyframes": {axis: track((key, POSES[key][0][i]) for key in keys)
                            for i, axis in enumerate(("x", "y"))}}
    envelope = {"type": "path", "id": "shared-outline", "fill": "none", "stroke": "#cacaca",
                "strokeWidth": 1, "d": line([(236, 358), (302, 263), (657, 99), (722, 264), (363, 433)], True),
                "keyframes": {"opacity": track([(0, 0), (125, 0), (166, 1), (243, 1), (266, 0)])}}
    fade = [(0, 1), (244, 1), (255, .48), (265, 0)]
    return {"title": "Prism diagram development study", "width": 1920, "height": 1080,
            "fps": float(RATE), "duration": seconds(FRAME_COUNT), "background": "#000000",
            "layers": [{"type": "group", "id": "canvas-units", "scaleX": 2, "scaleY": 2,
                        "children": [camera, envelope,
                                     label("frontend", 385, 79, [(410.5, 258.5), (410.5, 108)], (365.5, 80), fade),
                                     label("backend", 597, 437, [(620, 273), (620, 423)], (576, 438), fade)]}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first", action="store_true", help="Render the original two-pose camera fit")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with args.out.open("x") as out:
        json.dump(scene(args.first), out, indent=2)
        out.write("\n")


if __name__ == "__main__":
    main()
