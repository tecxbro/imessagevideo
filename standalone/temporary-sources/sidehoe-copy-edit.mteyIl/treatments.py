"""Independently painted surfaces for Sidehoe's measured motion tracks."""
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from artwork import composite, curve_polygon


@lru_cache(maxsize=1)
def calendar_face():
    """A pinched blue face, soft light over the upper rim, and editable type."""
    height, width = 292, 256
    yy, xx = np.mgrid[:height, :width]
    y, x = yy / (height - 1), xx / (width - 1)
    front = Image.new("L", (width, height))
    ImageDraw.Draw(front).rounded_rectangle((0, 21, width - 1, height - 5),
                                            radius=48, fill=255)
    pinch = 0.095 * np.exp(-((y - .52) / .24) ** 2)
    face_x = (x - .5) / (1 - pinch) + .5
    column = np.clip(np.rint(face_x * (width - 1)), 0, width - 1).astype(int)
    alpha = np.asarray(front)[np.arange(height)[:, None], column].copy()
    alpha[(face_x < 0) | (face_x > 1)] = 0

    surface_y = np.clip(y + .025 * ((x - .5) / .5) ** 2, 0, 1)
    depth = [.07, .09, .12, .15, .20, .27, .345, .415, .51, .57, .68, .82, .98]
    ramp = [(180, 176, 252), (179, 174, 252), (171, 174, 251), (163, 173, 251),
            (148, 170, 250), (130, 166, 250), (111, 163, 250), (94, 160, 250),
            (82, 158, 249), (89, 165, 251), (99, 173, 251), (87, 164, 250), (75, 151, 249)]
    rgb = np.stack([np.interp(surface_y, depth, channel) for channel in zip(*ramp)], axis=2)
    cheek = np.exp(-((y-.23)/.17)**2)*np.clip((np.abs(x-.5)-.31)/.14, 0, 1)
    rgb -= cheek[..., None]*[55, 10, 0]
    fold = np.exp(-((y-.555)/.032)**2)
    rgb += fold[..., None]*[3.0, 3.5, .6]

    # The glass cap has its own contour behind the rounded blue shoulder.
    cap = Image.new("RGBA", (width, height))
    ImageDraw.Draw(cap).rounded_rectangle((19, 0, width-20, 89), radius=39,
                                           fill=(209, 244, 254, 255))
    base = Image.fromarray(np.uint8(np.dstack((np.clip(rgb, 0, 255), alpha))))
    cap.alpha_composite(base)
    im = cap
    # The slanted terminals are part of the icon lettering.
    numerals = Image.new("L", (115, 103))
    draw = ImageDraw.Draw(numerals)
    curve_polygon(draw, (1, 20), (
        ((7, 2), (26, -1), (36, 0)), ((53, 1), (62, 12), (61, 25)),
        ((61, 34), (57, 42), (47, 48)), ((57, 52), (65, 61), (65, 74)),
        ((65, 95), (51, 102), (32, 102)), ((15, 102), (5, 92), (0, 79)),
        ((2, 77), (8, 75), (12, 73)), ((15, 85), (25, 91), (34, 91)),
        ((46, 91), (52, 84), (51, 73)), ((51, 58), (40, 52), (22, 53)),
        ((21, 49), (21, 45), (22, 44)), ((39, 45), (48, 37), (48, 26)),
        ((48, 17), (43, 10), (33, 10)), ((23, 10), (16, 13), (12, 25)),
        ((7, 23), (4, 22), (1, 20)),
    ), 255)
    draw.polygon([(73,23),(105,2),(114,2),(114,101),(100,101),(100,20),(81,32)], fill=255)
    mark = numerals.resize((140, 135), Image.Resampling.LANCZOS)
    im.paste("#fcfdfb", (54, 87), mark)
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


def follow_aperture(plate, left_width, right_width, unlit, keyboard_y):
    """Change the exposed bevel width during the cropped camera move."""
    values = np.array(plate)
    height,width = values.shape[:2]
    rows = np.arange(height)
    matte = np.where(rows < keyboard_y, 253, 215).astype(np.float32)
    rgb = np.stack((matte, matte+(rows>=keyboard_y), matte+7*(rows>=keyboard_y)), axis=1)
    fade = np.clip((rows-62)/30,0,1)*np.clip((height-62-rows)/28,0,1)
    for left, aperture in ((True,left_width),(False,right_width)):
        for i in range(18):
            col = i if left else width-i-1
            depth = i/aperture
            bounce = 82*np.exp(-((depth-.21)/.17)**2)
            black = np.array([unlit+bounce,unlit+bounce,unlit+bounce+2])
            coverage = np.clip(aperture+.45-i,0,1)
            shade = rgb*(1-coverage)+black*coverage
            values[:,col,:3]=np.round(values[:,col,:3]*(1-fade[:,None])+shade*fade[:,None])
    return Image.fromarray(values)


def follow_pointer(canvas, x, y, width, height, softness, alpha, lean=0, *,
                   vertical_softness=None):
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
    points = [(p + round(px * (w - 1) + lean * py * oversample),
               p + round(py * (h - 1))) for px, py in shape]
    rim = max(2, round(w * .065))
    draw.line([*points, points[0]], fill="#ffffff", width=rim * 2, joint="curve")
    for vertex in (points[0], points[2], points[8]):
        vx, vy = vertex
        draw.ellipse((vx - rim, vy - rim, vx + rim, vy + rim), fill="#ffffff")
    draw.polygon(points, fill="#050507")
    if vertical_softness is None:
        vertical_softness=softness
    if max(softness,vertical_softness) > .15:
        radius=(softness*oversample,vertical_softness*oversample)
        sprite=sprite.convert("RGBa").filter(ImageFilter.GaussianBlur(radius)).convert("RGBA")
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
