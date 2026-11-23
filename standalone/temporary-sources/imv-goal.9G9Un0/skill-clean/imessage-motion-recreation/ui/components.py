"""Editable geometry for the original film skin."""
from functools import lru_cache
from pathlib import Path
import math
import re
import subprocess
import unicodedata

from PIL import ImageFont

FONT = "DejaVu Sans"
PAPER = "#f6f0e7"
INK = "#2a2631"
PLUM = "#623864"
MUTED = "#655965"
LAVENDER = "#e8dbe8"
LINE = "#ded1d0"
GUTTER = 18
HEADER = 78
FOOTER = 14
PALETTES = {"film-paper": (PLUM, LAVENDER), "film-ink": ("#295984", "#dfdede")}


def rect(id, x, y, width, height, fill, radius=0, **extras):
    return dict(id=id, type="rect", x=x, y=y, width=width, height=height,
                fill=fill, radius=radius, **extras)


def text(id, value, x, y, size=16, **extras):
    return dict(id=id, type="text", text=value, x=x, y=y, fontSize=size,
                fontFamily=FONT, **{"fill": INK, **extras})


def group(id, x, y, children, **extras):
    return dict(id=id, type="group", x=x, y=y, children=children, **extras)


def clip(width, height, radius=0):
    return dict(x=0, y=0, width=width, height=height, radius=radius)


@lru_cache(maxsize=2)
def font_path(weight):
    style = "Bold" if weight == 700 else "Book"
    result = subprocess.check_output(
        ["fc-match", "-f", "%{family}\n%{file}", f"{FONT}:style={style}"], text=True
    )
    family, filename = result.split("\n", 1)
    if FONT not in family.split(",") or not Path(filename).is_file() or (
        weight == 700 and "Bold" not in Path(filename).stem
    ):
        raise ValueError(f"Install {FONT} regular and bold before compiling")
    return Path(filename)


@lru_cache(maxsize=32)
def font(size, weight):
    return ImageFont.truetype(str(font_path(weight)), size)


def clusters(value):
    """Keep combining marks, emoji modifiers, joined glyphs and flag pairs together."""
    cluster = ""
    regional_count = 0
    for char in value:
        code = ord(char)
        regional = 0x1F1E6 <= code <= 0x1F1FF
        joins = (
            unicodedata.category(char) in {"Mn", "Mc", "Me"} or char == "\u200d"
            or cluster.endswith("\u200d") or 0x1F3FB <= code <= 0x1F3FF
            or 0xE0020 <= code <= 0xE007F
            or (regional and regional_count % 2 == 1)
        )
        if cluster and not joins:
            yield cluster
            cluster = ""
        cluster += char
        regional_count = regional_count + 1 if regional else 0
    if cluster:
        yield cluster


class TextLayout:
    """Wrap in font coordinates before passing explicit lines to the engines."""

    def width(self, value, size, weight=400):
        # The renderer's fallback glyphs for color emoji can occupy a full em.
        return max(font(size, weight).getlength(value), sum(
            size * 1.28 if any(ord(c) >= 0x1F000 for c in unit)
            else font(size, weight).getlength(unit)
            for unit in clusters(value)
        ))

    def wrap(self, value, width, size, weight=400):
        lines = []
        for paragraph in value.replace("\r\n", "\n").replace("\r", "\n").expandtabs(4).split("\n"):
            line = ""
            for token in re.findall(r"\S+\s*|\s+", paragraph):
                if self.width(line + token.rstrip(), size, weight) <= width:
                    line += token
                    continue
                if line.strip():
                    lines.append(line.rstrip())
                line = ""
                for unit in clusters(token.lstrip()):
                    if line and self.width(line + unit.rstrip(), size, weight) > width:
                        lines.append(line.rstrip())
                        line = ""
                    line += unit
            lines.append(line.rstrip())
        return lines

    def ellipsis(self, value, width, size, weight=400):
        line = " ".join(value.split())
        if self.width(line, size, weight) <= width:
            return line
        fitted = ""
        for unit in clusters(line):
            if self.width(fitted + unit + "…", size, weight) > width:
                break
            fitted += unit
        return fitted.rstrip() + "…"


def header(width, name, service, measure):
    return group("ui.header", 0, 0, [
        rect("ui.header.paper", 0, 0, width, HEADER, PAPER),
        rect("ui.header.rule", GUTTER, HEADER - 1, width - GUTTER * 2, 1, LINE),
        rect("ui.header.badge", GUTTER, 19, 39, 39, PLUM, 10),
        text("ui.header.initial", next(clusters(name)).upper(), GUTTER + 19.5, 29, 15,
             textAnchor="middle", fill="#ffffff", fontWeight=700),
        text("ui.header.title", measure.ellipsis(name, width - 104, 19, 700), 70, 17, 19, fontWeight=700),
        text("ui.header.service", measure.ellipsis(service, width - 104, 11), 70, 43, 11, fill=MUTED),
    ])


def composer(width, copy, focused, measure):
    field_width = width - 116
    lines = measure.wrap(copy, field_width - 22, 14)
    shown = lines[-3:]
    height = 36 + (len(shown) - 1) * 17
    if len(lines) > len(shown):
        shown[0] = measure.ellipsis("… " + shown[0], field_width - 22, 14)
    signal = PLUM if focused else LINE
    return height + 20, [
        rect("ui.composer.paper", 0, 0, width, height + 20, PAPER),
        rect("ui.composer.rule", GUTTER, 0, width - GUTTER * 2, 1, LINE),
        rect("ui.composer.add", GUTTER, height - 19, 29, 29, LAVENDER, 8),
        text("ui.composer.plus", "+", GUTTER + 14.5, height - 16, 18, fill=PLUM, textAnchor="middle"),
        rect("ui.composer.field", 54, 10, field_width, height, "#fffaf4", 11,
             stroke=signal, strokeWidth=1),
        text("ui.composer.draft", "\n".join(shown) if copy else "Write a message",
             65, 19, 14, lineHeight=17, fill=INK if copy else MUTED),
        rect("ui.composer.send", width - 56, height - 19, 38, 29, PLUM if copy.strip() else LAVENDER, 8),
        text("ui.composer.send-label", "Send", width - 37, height - 11, 10,
             textAnchor="middle", fontWeight=700, fill="#ffffff" if copy.strip() else PLUM),
    ]


def bubble(id, copy, outgoing, width, measure, joined=False, size=16, color=None):
    fill = color or (PLUM if outgoing else LAVENDER)
    max_width = min(width - 2 * GUTTER, math.floor(width * .76))
    lines = measure.wrap(copy, max_width - 28, size)
    box_width = min(max_width, max(48, math.ceil(max(measure.width(line, size) for line in lines)) + 28))
    line_height = math.ceil(size * 1.32)
    height = len(lines) * line_height + 18
    elements = [rect(id + ".ink", 0, 0, box_width, height, fill, 12)]
    if not joined:
        # A small squared tab marks the end of a run in this film skin.
        elements.append(rect(id + ".tab", box_width - 8 if outgoing else 0,
                             height - 9, 8, 9, fill, 2))
    elements.append(text(id + ".copy", "\n".join(lines), 14, 9, size,
                         fill="#ffffff" if outgoing else INK, lineHeight=line_height))
    return box_width, height, elements


def typing(id, name, width, measure):
    label = measure.ellipsis(f"{name} is typing", width - 2 * GUTTER - 28, 12)
    return [
        rect(id + ".surface", 0, 0, measure.width(label, 12) + 28, 29, LAVENDER, 10),
        text(id + ".copy", label, 14, 7, 12, fill=PLUM),
    ]
