"""Independently painted surfaces for Sidehoe's measured motion tracks."""
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from artwork import composite, text


@lru_cache(maxsize=1)
def calendar_face():
    """A pinched blue face, soft light over the upper rim, and editable type."""
    height, width = 292, 256
    yy, xx = np.mgrid[:height, :width]
    y, x = yy / (height - 1), xx / (width - 1)
    outline = Image.new("L", (width, height))
    ImageDraw.Draw(outline).rounded_rectangle((0, 0, width - 1, height - 1), radius=46, fill=255)
    pinch = 0.062 * np.exp(-((y - .52) / .23) ** 2)
    source_x = (x - .5) / (1 - pinch) + .5
    core = np.asarray(outline)
    column = np.clip(np.rint(source_x * 255), 0, 255).astype(int)
    alpha = core[np.arange(height)[:, None], column].copy()
    alpha[(source_x < 0) | (source_x > 1)] = 0
    # The upper cyan exposure is a separate band from the pinched blue face.
    surface_y = np.clip(y - .032 * ((x - .5) / .5) ** 2, 0, 1)
    depth = [0, .052, .082, .126, .225, .355, .44, .57, .75, .99]
    ramp = [(210, 235, 253), (209, 243, 254), (193, 203, 251), (176, 174, 250),
            (145, 168, 251), (105, 163, 250), (86, 162, 249), (98, 172, 250),
            (91, 165, 250), (74, 151, 249)]
    rgb = np.stack([np.interp(surface_y, depth, channel) for channel in zip(*ramp)], axis=2)
    im = Image.fromarray(np.uint8(np.dstack((np.clip(rgb, 0, 255), alpha))))
    text(ImageDraw.Draw(im), 128, 80, "31", 163, "#f8fcff", 520, "center")
    return im


def lit_phone(plate, left_light, right_light, taper, *, exit_defocus=False):
    """Repaint just the two outer bevels in local handset coordinates."""
    width, height = plate.size
    y, x = np.mgrid[:height, :width]
    left = x < width / 2
    distance = np.where(left, x, width - 1 - x)
    # Hold the black inner gasket while the outer bevel catches a broad reflection.
    depth = distance / taper
    steel = np.interp(depth, [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 15, 16],
                      [46, 51, 57, 80, 119, 137, 74, 65, 50, 26, 8, 1, 22, 253])
    reflection = (4 + 6 * (1 - y / height)) * np.exp(-((depth - 4.5) / 2.4) ** 2)
    steel += reflection * np.where(left, 1, .56)
    rgb = np.stack((steel, steel, steel + 1.5), axis=2)
    base = np.array(plate)
    along_rail = np.clip((y - 59) / 24, 0, 1) * np.clip((height - 55 - y) / 24, 0, 1)
    interior = np.clip((17 - distance) / 2.0, 0, 1)
    strength = np.where(left, left_light, right_light)
    weight = strength * along_rail * interior * (base[:, :, 3] / 255)
    base[:, :, :3] = np.rint(base[:, :, :3] * (1 - weight[..., None]) + rgb * weight[..., None])
    # Leave transparent room on both sides during the strong exit blur.
    gutter = 14 if exit_defocus else 6
    far_gutter = gutter if exit_defocus else 0
    result = Image.new("RGBA", (width + gutter + far_gutter, height))
    key = ImageDraw.Draw(result)
    key.rounded_rectangle((gutter - 3, 320, gutter + 1, 379), radius=1.5,
                          fill=(70, 70, 74, round(176 * left_light)))
    key.line((gutter - 2, 324, gutter - 2, 374), fill=(139, 139, 144, round(184 * left_light)))
    result.alpha_composite(Image.fromarray(base), (gutter, 0))
    return result, gutter


def follow_pointer(canvas, x, y, width, height, softness, alpha):
    """Separate the cursor's screen-space footprint from the handset scale."""
    oversample, padding = 4, 12
    w, h = max(1, round(width * oversample)), max(1, round(height * oversample))
    p = padding * oversample
    sprite = Image.new("RGBA", (w + 2 * p, h + 2 * p))
    draw = ImageDraw.Draw(sprite)
    shape = [
        (0, .012), (.024, 0), (.98, .563), (1, .587), (.962, .609),
        (.615, .606), (.812, .952), (.797, .982), (.729, 1),
        (.638, .991), (.606, .960), (.373, .683), (.057, .790), (.008, .775),
    ]
    points = [(p + round(px * (w - 1)), p + round(py * (h - 1))) for px, py in shape]
    rim = max(2, round(w * .065))
    draw.line([*points, points[0]], fill="#ffffff", width=rim * 2, joint="curve")
    for vertex in (points[0], points[2], points[8]):
        vx, vy = vertex
        draw.ellipse((vx - rim, vy - rim, vx + rim, vy + rim), fill="#ffffff")
    draw.polygon(points, fill="#050507")
    if softness > .15:
        sprite = sprite.convert("RGBa").filter(ImageFilter.GaussianBlur(softness * oversample)).convert("RGBA")
    sprite = sprite.resize((round(sprite.width / oversample), round(sprite.height / oversample)), Image.Resampling.LANCZOS)
    composite(canvas, sprite, x - padding, y - padding, alpha)


@lru_cache(maxsize=64)
def glyph_ink(glyph, width, height, font_file):
    font = ImageFont.truetype(font_file, 96)
    image = Image.new("RGBA", (160, 160))
    ImageDraw.Draw(image).text((5, 5), glyph, font=font, embedded_color=True)
    return image.crop(image.getbbox()).resize((width, height), Image.Resampling.LANCZOS)


def calendar_emoji(draw, glyph, x, y, size, geometry, font_file):
    dx, dy, width, height = geometry
    ink = glyph_ink(glyph, max(1, round(width * size)), max(1, round(height * size)), str(Path(font_file)))
    draw._image.alpha_composite(ink, (round(x + dx * size), round(y + dy * size)))
