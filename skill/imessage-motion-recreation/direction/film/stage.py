"""Editable paper theatre and prop-table plates for The Moon Cue."""

from functools import lru_cache
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZE = (960, 540)
WIDTH, HEIGHT = SIZE
PAPER_SHADOW = (43, 26, 35)
SILHOUETTE = (20, 12, 18)


def _light_field(dark, color, center, spread, texture, seed):
    """Give a paper or fabric plate a pool of light and directional grain."""
    y, x = np.mgrid[:HEIGHT, :WIDTH]
    rng = np.random.default_rng(seed)
    cx, cy = center
    sx, sy = spread
    distance = ((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2
    light = np.exp(-0.65 * distance)
    fibers = (
        rng.normal(0, texture, size=SIZE[::-1])
        + np.sin(x * 1.71 + y * 0.034) * texture * 0.38
        + np.sin(x * 0.065 + y * 0.107) * texture * 0.55
    )
    values = (
        np.array(dark, dtype=float)
        + light[:, :, None] * (np.array(color, dtype=float) - dark)
        + fibers[:, :, None]
    )
    return Image.fromarray(np.clip(values, 0, 255).astype(np.uint8), "RGB")


def _shape_shadow(base, painter, color, blur=0.9, bounds=(0, 0, WIDTH, HEIGHT)):
    mask = Image.new("L", SIZE)
    painter(ImageDraw.Draw(mask))
    shadow = mask.filter(ImageFilter.GaussianBlur(blur)).crop(bounds)
    base.paste(color, bounds, shadow)


def _curtain(draw, edge, side):
    mirror = (lambda x: x) if side == "left" else (lambda x: WIDTH - x)
    points = [(0, 45), (edge, 52), (edge - 26, 110), (edge - 48, 181),
              (edge - 56, 260), (edge - 50, 349), (edge - 37, 474), (0, 482)]
    draw.polygon([(mirror(x), y) for x, y in points], fill=(52, 23, 33))
    for index, offset in enumerate(range(11, edge, 14)):
        if side == "right":
            offset -= 7
        curve = [(offset, 48), (offset - 7, 158), (offset - 24, 248),
                 (offset - 18, 335), (offset - 11, 459)]
        highlight = (64 + index % 4 * 4, 26 + index % 3 * 3, 39 + index % 3 * 3)
        if offset < edge - 25:
            draw.line([(mirror(x), y) for x, y in curve], fill=highlight, width=2)
            draw.line([(mirror(x - 4), y + 2) for x, y in curve], fill=(41, 18, 27), width=5)
    seam = [(mirror(x - 3), y) for x, y in points[1:-1]]
    draw.line(seam, fill=(100, 44, 44), width=2)
    draw.line([(mirror(8), 461), (mirror(edge - 38), 454)], fill=(80, 34, 37), width=2)


def _foliage(draw, *, roots, fill):
    for x, y, flip, stature in roots:
        stem = [(x, y), (x + 14 * flip, y - stature * .46), (x + 7 * flip, y - stature)]
        draw.line(stem, fill=fill, width=3)
        for level in (.23, .42, .62, .80):
            cy = y - stature * level
            cx = x + math.sin(level * math.pi) * 13 * flip
            for spread in (-1, 1):
                draw.polygon(
                    [(cx, cy), (cx + spread * 14, cy - 13),
                     (cx + spread * 23, cy - 15), (cx + spread * 15, cy - 6)],
                    fill=fill,
                )


@lru_cache(maxsize=12)
def _rabbit_pose(tilt):
    body = Image.new("L", SIZE)
    draw = ImageDraw.Draw(body)
    draw.ellipse((404, 341, 463, 374), fill=255)
    draw.polygon([(427, 356), (459, 324), (484, 343), (480, 366),
                  (500, 377), (490, 383), (424, 380)], fill=255)
    draw.polygon([(432, 370), (429, 376), (384, 369), (307, 352), (308, 349)], fill=255)
    draw.ellipse((406, 343, 426, 362), fill=255)
    head = Image.new("L", SIZE)
    draw = ImageDraw.Draw(head)
    draw.ellipse((448, 311, 494, 350), fill=255)
    draw.polygon([(479, 326), (505, 328), (512, 335), (500, 343), (480, 346)], fill=255)
    ear = [(452, 322), (442, 304), (436, 284), (440, 267), (447, 260),
           (455, 268), (460, 291), (466, 318)]
    draw.polygon(ear, fill=255)
    ear = [(466, 320), (466, 299), (474, 274), (482, 260), (491, 258),
           (494, 266), (487, 286), (479, 319)]
    draw.polygon(ear, fill=255)
    draw.ellipse((478, 321, 484, 327), fill=0)
    draw.ellipse((443, 285, 450, 293), fill=175)
    draw.ellipse((478, 281, 485, 289), fill=175)
    if tilt:
        head = head.rotate(tilt, Image.Resampling.BICUBIC, center=(466, 344))
    body.paste(255, (0, 0, WIDTH, HEIGHT), head)
    return body.filter(ImageFilter.GaussianBlur(0.70))


@lru_cache(maxsize=1)
def _stage_plate():
    plate = _light_field((13, 9, 16), (78, 36, 43), (474, 287), (426, 350), 1.25, 73)
    d = ImageDraw.Draw(plate)
    # The torn tissue and its visible frame are separate practical layers.
    d.rounded_rectangle((157, 47, 799, 467), 8, fill=(21, 11, 19))
    d.rectangle((169, 58, 786, 449), fill=(62, 32, 39))
    d.rectangle((176, 64, 780, 442), fill=(88, 49, 45))
    d.rectangle((183, 70, 772, 437), fill=(37, 22, 29))
    screen = _light_field((112, 61, 53), (252, 200, 131), (503, 263), (369, 224), 1.55, 712)
    plate.paste(screen.crop((192, 79, 765, 423)), (192, 79))
    d = ImageDraw.Draw(plate)
    rng = random.Random(81)
    for index in range(1100):
        x, y = rng.randrange(200, 756), rng.randrange(82, 421)
        if index % 5 == 0:
            start = plate.getpixel((x, y))
            ink = tuple(max(0, value - 8 - index % 10) for value in start)
            d.line((x, y, x + rng.randint(1, 5), y + rng.choice((0, 1))), fill=ink)
        elif index % 3 == 0:
            start = plate.getpixel((x, y))
            d.point((x, y), fill=tuple(min(255, value + 14) for value in start))
    d.line([(193, 97), (194, 254), (196, 350), (195, 418)], fill=(151, 92, 66), width=2)
    d.line([(752, 84), (757, 209), (754, 335), (756, 416)], fill=(180, 112, 73))
    d.line([(201, 84), (410, 82), (633, 84), (748, 83)], fill=(165, 97, 62))
    # Two hills make distance legible before the foreground puppet appears.
    d.polygon([(192, 380), (230, 369), (293, 366), (352, 357), (412, 365),
               (491, 379), (557, 377), (632, 351), (721, 346), (765, 354),
               (765, 422), (192, 422)], fill=(122, 72, 71))
    d.polygon([(192, 396), (224, 394), (279, 401), (343, 396), (403, 379),
               (473, 378), (551, 395), (591, 391), (666, 374), (716, 378),
               (765, 365), (765, 422), (192, 422)], fill=(70, 41, 50))
    _foliage(
        d, roots=[(213, 407, 1, 65), (244, 408, -1, 86), (281, 409, 1, 38),
                  (672, 404, -1, 37), (714, 411, 1, 78), (748, 406, -1, 95)],
        fill=PAPER_SHADOW,
    )
    d = ImageDraw.Draw(plate)
    d.polygon([(192, 410), (245, 414), (286, 405), (337, 412), (385, 405),
               (443, 408), (493, 401), (548, 409), (578, 407), (631, 412),
               (680, 400), (707, 402), (765, 391), (765, 423), (192, 423)],
              fill=PAPER_SHADOW)
    d.rectangle((181, 424, 776, 439), fill=(55, 27, 33))
    d.line((182, 426, 777, 426), fill=(122, 69, 53), width=2)
    d.rectangle((172, 440, 793, 449), fill=(20, 12, 19))
    d.line((172, 444, 793, 444), fill=(70, 36, 42))
    return plate


@lru_cache(maxsize=2)
def _front_plate(audience):
    face = Image.new("RGBA", SIZE)
    d = ImageDraw.Draw(face)
    _curtain(d, 185, "left")
    _curtain(d, 183, "right")
    d.polygon([(0, 0), (960, 0), (960, 48), (739, 49), (604, 59),
               (414, 58), (235, 53), (0, 56)], fill=(40, 20, 29))
    for y in (12, 19, 39):
        d.arc((-15, y - 100, 965, y + 24), 8, 172, fill=(72, 31, 40), width=2)
    d.rectangle((0, 460, WIDTH, HEIGHT), fill=(30, 17, 24))
    d.line((0, 463, WIDTH, 463), fill=(65, 33, 37), width=2)
    d.line((0, 480, WIDTH, 480), fill=(42, 22, 31))
    if audience:
        d.arc((51, 466, 216, 599), 180, 342, fill=(64, 31, 42), width=2)
        d.ellipse((85, 452, 156, 532), fill=(17, 12, 21))
        d.polygon([(42, 540), (61, 518), (102, 502), (146, 503), (197, 527),
                   (206, 540)], fill=(17, 12, 21))
        d.ellipse((756, 442, 836, 526), fill=(17, 12, 21))
        d.polygon([(713, 540), (721, 519), (767, 497), (821, 494),
                   (877, 514), (898, 540)], fill=(17, 12, 21))
        d.arc((756, 442, 836, 526), 194, 292, fill=(77, 36, 41), width=2)
        d.ellipse((378, 483, 431, 547), fill=(21, 13, 22))
        d.polygon([(344, 540), (369, 522), (403, 522), (439, 531), (459, 540)],
                  fill=(21, 13, 22))
    return face


def _crescent(radius, rotation=0):
    # Difference of offset circles described as one editable paper contour.
    outside = [(math.cos(math.radians(a)) * radius, math.sin(math.radians(a)) * radius)
               for a in range(62, 301, 3)]
    inside = [(0.48 * radius + math.cos(math.radians(a)) * 0.85 * radius,
               math.sin(math.radians(a)) * 0.85 * radius)
              for a in range(246, 113, -3)]
    sine, cosine = math.sin(rotation), math.cos(rotation)
    return [(x * cosine - y * sine, x * sine + y * cosine) for x, y in outside + inside]


def _at(points, x, y, squash=1):
    return [(x + dx, y + dy * squash) for dx, dy in points]


def stage(moon: float, audience: bool = True, rabbit_motion: float = 0) -> Image.Image:
    """Render the theatre. Moon progress starts offscreen and allows overshoot."""
    plate = _stage_plate().copy()
    plate.paste(SILHOUETTE, (0, 0, WIDTH, HEIGHT), _rabbit_pose(round(24 * rabbit_motion)))
    if moon > 0:
        x = 824 - 191 * moon
        y = 222 - 45 * moon + 3 * math.sin(9 * moon)
        shape = _at(_crescent(37, rotation=-.35 + moon * .15), x, y)

        def draw_moon(d):
            d.line((x + 8, y + 10, 774, y + 56), fill=255, width=3)
            d.polygon(shape, fill=255)

        _shape_shadow(plate, draw_moon, (55, 33, 43), blur=.88, bounds=(192, 79, 765, 423))
    plate.paste(_front_plate(audience), (0, 0), _front_plate(audience))
    return plate


def _spool(draw, x, y, radius, dark, light):
    draw.ellipse((x - radius, y - radius * .52, x + radius, y + radius * .52),
                 fill=dark, outline=light, width=2)
    for delta in (-5, 0, 5):
        draw.arc((x - radius + 3, y - radius * .44 + delta,
                  x + radius - 3, y + radius * .36 + delta), 0, 180, fill=light)
    draw.ellipse((x - 5, y - 3, x + 4, y + 3), fill=(26, 16, 23))


@lru_cache(maxsize=1)
def _table_plate():
    plate = _light_field((18, 11, 19), (124, 73, 53), (646, 267), (334, 216), 1.90, 275)
    d = ImageDraw.Draw(plate)
    rng = random.Random(17)
    for index in range(140):
        y = 10 + index * 4
        x = rng.randrange(-70, 780)
        for _ in range(5):
            length = rng.randrange(9, 92)
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                original = plate.getpixel((x, y))
                difference = rng.choice((-9, -6, 5, 7))
                ink = tuple(max(0, min(255, c + difference)) for c in original)
                d.line((x, y, x + length, y + rng.randrange(-1, 2)), fill=ink)
            x += length + rng.randrange(6, 80)
    d.line([(0, 476), (272, 457), (582, 456), (960, 475)], fill=(28, 16, 23), width=2)
    d.line([(0, 478), (273, 459), (583, 459), (960, 477)], fill=(88, 47, 40))
    # The objects left of the key light share the same elliptical tabletop perspective.
    for x, y, radius, dark, light in (
        (305, 327, 66, (46, 26, 31), (83, 48, 43)),
        (270, 260, 24, (63, 42, 36), (101, 72, 50)),
        (809, 413, 27, (58, 36, 33), (105, 67, 45)),
    ):
        d.ellipse((x - radius - 6, y - radius * .36, x + radius + 16, y + radius * .78),
                  fill=(26, 17, 24))
        _spool(d, x, y, radius, dark, light)
    d.arc((329, 332, 466, 420), 105, 294, fill=(110, 77, 56), width=2)
    d.arc((390, 393, 486, 466), 218, 351, fill=(110, 77, 56), width=2)
    d.line((826, 218, 941, 177), fill=(44, 25, 28), width=5)
    d.line((823, 218, 940, 178), fill=(152, 108, 70), width=2)
    d.line((855, 242, 933, 213), fill=(51, 26, 29), width=4)
    d.line((855, 241, 932, 212), fill=(121, 81, 55))
    d.polygon([(94, 331), (178, 356), (200, 435), (167, 457), (82, 425),
               (51, 356)], fill=(39, 24, 29))
    d.line([(52, 355), (127, 376), (195, 436)], fill=(80, 46, 41), width=2)
    d.line([(82, 425), (127, 376), (177, 356)], fill=(65, 38, 36), width=2)
    return plate


def _oval(cx, cy, rx, ry):
    return cx - rx, cy - ry, cx + rx, cy + ry


def _tin_lid(draw, opening):
    cx, cy = 652 - 114 * opening, 304 - 145 * opening
    ry = 73 - 31 * math.sin(math.pi * opening)
    draw.ellipse(_oval(cx + 5, cy + 8, 130, ry), fill=(64, 24, 30))
    draw.ellipse(_oval(cx, cy, 130, ry), fill=(123, 39, 43), outline=(181, 76, 63), width=2)
    draw.ellipse(_oval(cx, cy - 2, 123, ry - 5), fill=(154, 50, 49), outline=(208, 106, 73), width=2)
    draw.ellipse(_oval(cx, cy - 4, 114, ry - 12), fill=(146, 47, 47), outline=(103, 32, 38), width=2)
    draw.arc(_oval(cx, cy - 3, 121, ry - 6), 192, 361, fill=(229, 130, 86), width=1)
    for delta in (-28, 26):
        draw.arc(_oval(cx + delta, cy, 72, ry - 15), 196, 252, fill=(175, 65, 53), width=1)


def _glove(draw, gx, gy):
    draw.polygon(
        [(gx - 35, gy - 13), (gx - 21, gy - 28), (gx + 5, gy - 31),
         (gx + 65, gy - 6), (1040, gy + 16), (1040, 468), (gx + 25, gy + 19),
         (gx + 1, gy + 12), (gx - 26, gy + 7)],
        fill=(36, 24, 33), outline=(75, 45, 44),
    )
    draw.line([(gx - 32, gy - 11), (gx - 14, gy - 17), (gx + 15, gy - 11)],
              fill=(114, 72, 55), width=2)
    draw.line([(gx - 24, gy + 2), (gx - 9, gy - 5), (gx + 5, gy - 1)],
              fill=(83, 52, 45), width=2)
    draw.line([(gx + 99, gy + 8), (gx + 95, gy + 35)], fill=(95, 55, 46), width=2)


def prop_table(opening: float, lift: float) -> Image.Image:
    """Open the red tin and stage the extraction of the same crescent prop."""
    plate = _table_plate().copy()

    def shadows(d):
        d.ellipse(_oval(670, 331, 147, 79), fill=160)
        d.ellipse(_oval(661 - 114 * opening, 331 - 145 * opening, 119, 31 + opening * 19), fill=90)
        if lift > 0:
            d.line((677 + 63 * lift, 309 - 70 * lift, 935, 417), fill=115, width=15)

    _shape_shadow(plate, shadows, (17, 10, 18), blur=15)
    d = ImageDraw.Draw(plate)
    d.ellipse(_oval(652, 323, 126, 74), fill=(104, 31, 37), outline=(66, 24, 32), width=3)
    d.arc(_oval(652, 323, 124, 71), 1, 152, fill=(174, 58, 52), width=3)
    d.ellipse(_oval(652, 303, 126, 73), fill=(184, 71, 56), outline=(226, 119, 82), width=2)
    d.ellipse(_oval(652, 303, 117, 66), fill=(75, 37, 37), outline=(102, 46, 39), width=4)
    d.ellipse(_oval(652, 307, 108, 57), fill=(99, 59, 48))
    d.arc(_oval(652, 300, 116, 64), 200, 343, fill=(56, 32, 36), width=4)
    d.arc(_oval(652, 303, 123, 70), 10, 170, fill=(237, 137, 94), width=2)
    d.polygon([(570, 314), (700, 308), (725, 332), (696, 345), (594, 347)],
              fill=(116, 72, 53))
    d.line([(570, 314), (640, 325), (725, 332)], fill=(133, 87, 64))
    prop_x, prop_y = 638 + 104 * lift, 293 - 126 * lift
    prop = _crescent(35 + 5 * lift, rotation=-.20 - .28 * lift)
    points = _at(prop, prop_x, prop_y, squash=.67 + .33 * lift)
    end = (715 + 178 * lift, 349 + 45 * lift)
    d.line((prop_x + 3, prop_y + 3, *end), fill=(48, 26, 27), width=6)
    d.line((prop_x + 3, prop_y + 1, *end), fill=(156, 101, 66), width=2)
    d.polygon([(x + 2, y + 4) for x, y in points], fill=(106, 62, 44))
    d.polygon(points, fill=(236, 171, 97), outline=(255, 208, 138), width=1)
    d.line(points[7:37], fill=(249, 193, 118), width=2)
    reach = max(0, min(1, (opening - .70) / .30))
    if reach > 0:
        _glove(d, end[0] + 288 * (1 - reach), end[1] + 50 * (1 - reach))
    # The lid occludes the prop until it physically clears the tin.
    _tin_lid(d, opening)
    return plate
