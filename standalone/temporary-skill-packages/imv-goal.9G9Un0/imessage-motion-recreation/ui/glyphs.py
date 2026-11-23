"""Lay out explicitly supplied color glyphs alongside editable message text."""
from math import isfinite

from .components import TextLayout, clusters, text


class GlyphText(TextLayout):
    """Match complete graphemes to independent, portable artwork and em metrics."""

    def __init__(self, specs, assets):
        if not isinstance(specs, dict):
            raise ValueError("glyphAssets must map graphemes to asset IDs and metrics")
        self.glyphs = {}
        for cluster, spec in specs.items():
            if list(clusters(cluster)) != [cluster] or not cluster.strip():
                raise ValueError(f"Glyph key must contain one grapheme: {cluster!r}")
            if not isinstance(spec, dict) or set(spec) != {"assetId", "advance", "ink"}:
                raise ValueError(f"{cluster}: provide assetId, advance and ink")
            asset = spec["assetId"]
            advance, ink = spec["advance"], spec["ink"]
            if not isinstance(asset, str) or asset not in assets:
                raise ValueError(f"{cluster}: glyph asset must name a declared local image")
            if not isinstance(ink, list) or len(ink) != 4 or not all(
                type(value) in (int, float) and isfinite(value) for value in [advance, *ink]
            ):
                raise ValueError(f"{cluster}: ink must contain four finite em metrics")
            x, y, width, height = ink
            if not (0 < advance <= 4 and -1 <= x <= 1 and -1 <= y <= 2
                    and 0 < width <= 4 and 0 < height <= 4):
                raise ValueError(f"{cluster}: glyph ink or advance is outside the supported em range")
            self.glyphs[cluster] = (assets[asset][0], advance, ink)

    def runs(self, value):
        copy = []
        for cluster in clusters(value):
            glyph = self.glyphs.get(cluster)
            if glyph is None:
                copy.append(cluster)
                continue
            if copy:
                yield "".join(copy), None
                copy.clear()
            yield cluster, glyph
        if copy:
            yield "".join(copy), None

    def width(self, value, size, weight=400):
        measure = super().width
        return sum(size * glyph[1] if glyph else measure(run, size, weight)
                   for run, glyph in self.runs(value))

    def layers(self, id, lines, x, y, size, line_height, fill, *, weight=400):
        if not any(unit in self.glyphs for line in lines for unit in clusters(line)):
            return [text(id, "\n".join(lines), x, y, size, fill=fill, lineHeight=line_height, fontWeight=weight)]
        result = []
        for row, line in enumerate(lines):
            advance = x
            top = y + row * line_height
            for index, (run, glyph) in enumerate(self.runs(line)):
                name = f"{id}.{row + 1}.{index + 1}"
                if glyph is None:
                    result.append(text(name, run, advance, top, size, fill=fill, fontWeight=weight))
                    advance += super().width(run, size, weight)
                    continue
                src, glyph_advance, (left, offset, width, height) = glyph
                result.append(dict(id=name, type="image", src=src, x=advance + size * left,
                                   y=top + size * offset, width=size * width, height=size * height))
                advance += glyph_advance * size
        return result
