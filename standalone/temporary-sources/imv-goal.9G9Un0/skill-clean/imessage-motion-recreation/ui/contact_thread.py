"""Original light contact-thread appearance for the shared synthetic Messages scene."""
import math

from .components import clip, clusters, group, rect, text

SKIN = "contact-thread"
PAPER = "#fbfcfe"
INK = "#17243a"
MUTED = "#526178"
BLUE = "#126bd4"
GRAY = "#e8edf3"
HEADER = 114
FOOTER = 22
HANDSET_MARGIN = 14
SCREEN_RADIUS = 30
TYPING_HEIGHT = 32
KEYBOARD_COLORS = {"panel": "#dce3ec", "divider": "#cbd6e4", "standard": "#ffffff",
                   "special": "#aabbd0", "label": INK, "special_label": INK}


def path(layer_id, outline, *, x=0, y=0, fill="none", **extras):
    return dict(id=layer_id, type="path", d=outline, x=x, y=y, fill=fill, **extras)


def dot(layer_id, x, y, size, color):
    return dict(id=layer_id, type="circle", x=x, y=y, width=size, height=size, fill=color)


def avatar(x, y, title, asset):
    diameter = 41
    prefix = "ui.header.avatar"
    if asset:
        src, width, height = asset
        scale = diameter / min(width, height)
        art = dict(id=prefix + ".image", type="image", src=src,
                   x=(diameter - width * scale) / 2, y=(diameter - height * scale) / 2,
                   width=width * scale, height=height * scale)
    else:
        initials = "".join(next(clusters(word)) for word in title.split()[:2]).upper()
        art = text(prefix + ".initials", initials, diameter / 2, 11, 15, fill="#203d60",
                   textAnchor="middle", fontWeight=700)
    return group(prefix, x, y, [rect(prefix + ".backing", 0, 0, diameter, diameter, "#dbe8f7"), art],
                 clip=clip(diameter, diameter, diameter / 2))


def header(width, name, service, measure, asset, status_time):
    foreground = {"stroke": INK, "strokeWidth": 1.3}
    status = group("ui.header.status", 0, 0, [
        text("ui.header.status.time", status_time, 24, 11, 11, fill=INK, fontWeight=700),
        *[rect(f"ui.header.status.signal.{i}", width - 73 + i * 4, 20 - i * 2, 2, 3 + i * 2, INK, 1)
          for i in range(4)],
        path("ui.header.status.wifi", "M0 3 Q6 -2 12 3 M2 6 Q6 2 10 6 M5 9 H7",
             x=width - 53, y=11, **foreground),
        rect("ui.header.status.battery", width - 35, 11, 16, 9, PAPER, 2, **foreground),
        rect("ui.header.status.battery.fill", width - 33, 13, 12, 5, INK, 1),
    ])
    center = width / 2
    return group("ui.header", 0, 0, [
        rect("ui.header.paper", 0, 0, width, HEADER, PAPER), status,
        path("ui.header.back", "M9 0 L2 7 L9 14", x=25, y=55, stroke=BLUE, strokeWidth=2),
        avatar(center - 20.5, 31, name, asset),
        text("ui.header.title", measure.ellipsis(name, width - 112, 15, 700), center, 76, 15,
             textAnchor="middle", fontWeight=700, fill=INK),
        text("ui.header.service", measure.ellipsis(service, width - 112, 10), center, 96, 10,
             textAnchor="middle", fill=MUTED),
        rect("ui.header.rule", 16, HEADER - 1, width - 32, 1, "#e0e6ed"),
    ])


def composer(width, copy, focused, measure):
    field_width = width - 68
    lines = measure.wrap(copy, field_width - 53, 15)
    shown = lines[-3:]
    height = 37 + (len(shown) - 1) * 18
    if len(lines) > len(shown):
        shown[0] = measure.ellipsis("… " + shown[0], field_width - 53, 15)
    y = height - 18
    sending = bool(copy.strip())
    control = [
        rect("ui.composer.send", width - 51, y - 3, 29, 23, BLUE, 11.5),
        path("ui.composer.send-arrow", "M7 12 V1 M2 6 L7 1 L12 6", x=width - 43,
             y=y + 2, stroke="#ffffff", strokeWidth=1.7),
    ] if sending else [
        rect("ui.composer.mic", width - 40, y - 1, 6, 11, MUTED, 3),
        path("ui.composer.mic-stand", "M1 6 V7 Q1 12 6 12 Q11 12 11 7 V6 M6 12 V16 M3 16 H9",
             x=width - 43, y=y - 1, stroke=MUTED, strokeWidth=1.2),
    ]
    return height + 14, [
        rect("ui.composer.paper", 0, 0, width, height + 14, PAPER),
        dot("ui.composer.add", 18, y - 5, 29, GRAY),
        path("ui.composer.plus", "M0 6 H12 M6 0 V12", x=26.5, y=y + 3.5,
             stroke=BLUE, strokeWidth=1.5),
        rect("ui.composer.field", 53, 7, field_width, height, "#ffffff", 18.5,
             stroke="#90b3e8" if focused else "#d7e0eb", strokeWidth=1),
        group("ui.composer.draft", 0, 0, measure.layers("ui.composer.draft.copy", shown if copy else ["Message"],
                                                       67, 16, 15, 18, INK if copy else MUTED)),
        group("ui.composer.control", 0, 0, control),
    ]


def tail(layer_id, box_width, box_height, outgoing, color):
    return path(layer_id, "M0 0 C5 3 9 3 13 1 C13 6 16 9 19 10 C11 11 6 6 0 5 Z",
                x=box_width - 18 if outgoing else 18, y=box_height - 6,
                scaleX=1 if outgoing else -1, fill=color)


def bubble(layer_id, copy, outgoing, width, measure, joined, size, color):
    max_width = min(width - 36, math.floor(width * .74))
    lines = measure.wrap(copy, max_width - 26, size)
    ink_width = max(measure.width(line, size) for line in lines)
    width = min(max_width, max(46, math.ceil(ink_width) + 26))
    line_height = math.ceil(size * 1.25)
    height = line_height * len(lines) + 16
    elements = [rect(layer_id + ".ink", 0, 0, width, height, color, min(17, height / 2))]
    if not joined:
        elements.append(tail(layer_id + ".tail", width, height, outgoing, color))
    elements.append(group(layer_id + ".copy", 0, 0, measure.layers(layer_id + ".copy.runs", lines,
                          13, 8, size, line_height, "#ffffff" if outgoing else INK)))
    return width, height, elements


def typing():
    return [
        rect("ui.typing.surface", 0, 0, 58, TYPING_HEIGHT, GRAY, 15),
        tail("ui.typing.tail", 58, TYPING_HEIGHT, False, GRAY),
        *[dot(f"ui.typing.dot.{index + 1}", 12 + index * 13, 12, 8, MUTED) for index in range(3)],
    ]


def typing_keys(nodes, spans, fps):
    """Each appearance has its own authored phase, with times on the picture frame grid."""
    cycle = max(3, fps)
    rise = max(1, cycle // 5)
    fall = max(2, cycle // 2)
    for dot_index, node in enumerate(nodes):
        points = {}
        for start, end in spans:
            points[start] = (12, .44, "hold")
            first = start + dot_index * max(1, round(fps * .13))
            for base in range(first, end, cycle):
                for offset, y, opacity in ((0, 12, .44), (rise, 10, 1), (fall, 12, .44)):
                    if base + offset < end:
                        points.setdefault(base + offset, (y, opacity, "linear"))
            last = end - 1
            if last > first and last not in points:
                phase = (last - first) % cycle
                strength = max(0, min(phase / rise, (fall - phase) / (fall - rise)))
                points[last] = (12 - 2 * strength, .44 + .56 * strength, "linear")
        if points:
            ordered = sorted(points.items())
            node["keyframes"] = {
                prop: [{"t": frame / fps, "value": pose[prop_index], "ease": pose[2]}
                       for frame, pose in ordered]
                for prop_index, prop in enumerate(("y", "opacity"))
            }


def handset(width, height):
    return group("ui.handset", 0, 0, [
        rect("ui.handset.rim", -9, -9, width + 18, height + 18, "#1c283c", SCREEN_RADIUS + 9,
             stroke="#9baabd", strokeWidth=1.5),
        rect("ui.handset.aperture", -2, -2, width + 4, height + 4, "#142135", SCREEN_RADIUS + 2),
        rect("ui.handset.side-key", width + 9, 113, 3, 49, "#526178", 1.5),
    ])


def footer(width, height):
    return group("ui.footer", 0, height - FOOTER, [
        rect("ui.footer.paper", 0, 0, width, FOOTER, PAPER),
        rect("ui.footer.home", width / 2 - 36, 11, 72, 4, INK, 2),
    ])
