#!/usr/bin/env python3
"""Author simple concert ticket option cards for the t3 shot plan."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).resolve().parent
W, H = 592, 394  # 2x the 296x197 rail slot (3:2)

def font(size, bold=False):
    for name in ("Helvetica-Bold.ttf" if bold else "Helvetica.ttf",
                 "Arial Bold.ttf" if bold else "Arial.ttf"):
        p = Path("/System/Library/Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    p = Path("/System/Library/Fonts/Helvetica.ttc")
    return ImageFont.truetype(str(p), size)

def rounded(draw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)

def card(fname, tier, seat, price, band, accent):
    im = Image.new("RGB", (W, H), "#101418")
    d = ImageDraw.Draw(im)
    # card body
    rounded(d, (10, 10, W - 10, H - 10), 26, "#f7f4ee")
    # colored header band
    d.rounded_rectangle((10, 10, W - 10, 118), radius=26, fill=band)
    d.rectangle((10, 70, W - 10, 118), fill=band)
    d.text((36, 34), "THE NEON PINES", font=font(30, True), fill="#ffffff")
    d.text((36, 72), "FRI · JUN 12 · 8 PM", font=font(22), fill="#e8e8e8")
    # tier block
    d.text((36, 148), tier, font=font(52, True), fill="#1b1f24")
    d.text((36, 216), seat, font=font(28), fill="#4a5058")
    # price chip
    rounded(d, (W - 196, 150, W - 36, 214), 18, accent)
    tw = d.textlength(price, font=font(40, True))
    d.text((W - 196 + (160 - tw) / 2, 158), price, font=font(40, True), fill="#ffffff")
    # perforation + stub
    for y in range(240, H - 30, 18):
        d.line((96, y, 96, y + 9), fill="#c9c4b8", width=3)
    d.line((36, 300, W - 36, 300), fill="#d8d3c8", width=2)
    d.text((36, 322), "ADMIT ONE", font=font(24, True), fill="#6b7280")
    # barcode-ish stub
    x = W - 200
    for i, wbar in enumerate((6, 3, 9, 3, 5, 3, 7, 3, 4, 8, 3, 5)):
        d.rectangle((x, 312, x + wbar, 366), fill="#22262c")
        x += wbar + 4
    im.save(OUT / fname)
    print(OUT / fname)

card("ticket-ga-floor.png", "GA FLOOR", "Standing · all ages", "$89", "#274b8f", "#3f6fd1")
card("ticket-lower-bowl.png", "LOWER BOWL", "Sec 112 · Row F", "$129", "#5b2d8e", "#8a4fd1")
card("ticket-balcony.png", "BALCONY", "Sec 304 · Row C", "$64", "#0f6e6a", "#23a39d")
card("ticket-vip-pit.png", "VIP PIT", "Early entry + poster", "$249", "#8e3a17", "#d16a3f")
