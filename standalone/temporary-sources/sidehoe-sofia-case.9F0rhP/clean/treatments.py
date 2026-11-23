"""Independently painted surfaces for Sidehoe's measured motion tracks."""
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from artwork import composite, curve_polygon


@lru_cache(maxsize=12)
def calendar_face(calibrated=0, numeral_detail=0, ink_pose=None, finish_lift=0):
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
    refraction = cheek[..., None]*[55,10,0]
    if calibrated:
        revised_cheek = np.exp(-((y-.23)/.18)**2)*np.clip((np.abs(x-.5)-.33)/.15, 0, 1)
        wrap = np.exp(-((y-.38)/.098)**2)*np.clip((np.abs(x-.5)-.31)/.13, 0, 1)
        base_shade = np.interp(surface_y,[0,.28,.48,.59,.72,.83,.96,1],[0,0,-.5,-.5,-4.6,-4,0,0])
        revised = revised_cheek[...,None]*[42,6,0] - wrap[...,None]*[13,4,.1]
        revised -= base_shade[...,None]*[1,.78,.02]
        refraction += (revised-refraction)*calibrated
    rgb -= refraction
    fold = np.exp(-((y-.555)/.032)**2)
    rgb += fold[..., None]*[3-calibrated, 3.5, .6]
    if numeral_detail:
        # The fold catches light just below the cooler middle of the blue face.
        upper = np.exp(-((surface_y-.422)/.055)**2)
        middle = np.exp(-((surface_y-.535)/.031)**2)
        lower = np.exp(-((surface_y-.605)/.033)**2)
        light = upper[..., None]*[-5, 1, 0] + middle[..., None]*[1.5, 2, 0]
        light += lower[..., None]*[5.5, 4.1, -.8]
        rgb += light * min(1, numeral_detail)

    if finish_lift:
        softness = np.exp(-((surface_y-.19)/.167)**2)
        fold_lift = np.exp(-((surface_y-.57)/.088)**2)
        edge_lift = np.exp(-((surface_y-.80)/.079)**2)
        rgb += finish_lift*(softness[...,None]*[5.8,4.2,.1]
                           + fold_lift[...,None]*[4.3,4.2,.0]
                           + edge_lift[...,None]*[1.5,2,.4])

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
    if calibrated:
        # Fit the bowl stroke without expanding its optical bounds.
        three = numerals.crop((0,0,68,103))
        stroke = three.filter(ImageFilter.MaxFilter(3))
        numerals.paste(Image.blend(three,stroke,max(0, .85*calibrated-numeral_detail*.65)),(0,0))
    spine = 100-calibrated
    draw.polygon([(73,23),(105,2),(114,2),(114,101),(spine,101),(spine,20),(81,32)], fill=255)
    if numeral_detail:
        one = numerals.crop((71,0,115,103))
        profile = Image.new("L", (44,103))
        profile.paste(one.crop((0,0,43,101)).resize((42,101),Image.Resampling.LANCZOS),(2,0))
        numerals.paste(Image.blend(one,profile,min(1,numeral_detail)),(71,0))
    mark = numerals.resize((140, 135), Image.Resampling.LANCZOS)
    if ink_pose is None:
        ink_x, ink_y = 54, 87
    else:
        ink_x, ink_y, height_ratio, bold = ink_pose
        mark = mark.resize((mark.width, round(mark.height*height_ratio)), Image.Resampling.LANCZOS)
        mark = Image.blend(mark, mark.filter(ImageFilter.MaxFilter(3)), bold)
    im.paste("#fcfdfb", (ink_x, ink_y), mark)
    return im


def lit_phone(plate, left_light, right_light, taper, *, exit_defocus=False,
              registered=False):
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
    base = np.array(plate)
    if registered:
        stops = [0,1,2,3,4,5,6,8,10,12,14,15,16,17,19]
        left_face = [113,59,76,112,119,81,61,48,25,10,0,1,55,164,253]
        right_face = [119,61,81,123,121,76,61,41,22,8,0,5,70,181,253]
        steel = np.where(left, np.interp(distance,stops,left_face),
                         np.interp(distance,stops,right_face))
        steel += reflection*np.where(left,1,.75)
        matte = base[:,:,0].astype(float)
        glass = np.clip((distance-15.2)/4.3,0,1)
        steel = steel*(1-glass)+matte*glass
        interior = np.clip((20 - distance) / 2.0,0,1)
        strength = .92
    else:
        interior = np.clip((17 - distance) / 2.0,0,1)
        strength = np.where(left,left_light,right_light)
    rgb = np.stack((steel, steel, steel + 1.5), axis=2)
    along_rail = np.clip((y - 59) / 24, 0, 1) * np.clip((height - 55 - y) / 24, 0, 1)
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


def rounded_arrow(points, radii):
    """Round the editable arrow's convex corners in screen space."""
    path = []
    for index, tip in enumerate(points):
        left, right = points[index-1], points[(index+1) % len(points)]
        left, tip, right = (np.asarray(point, dtype=float) for point in (left, tip, right))
        bend = radii[index]
        entry = tip + (left-tip)*min(.49,bend/max(1,np.linalg.norm(left-tip)))
        exit = tip + (right-tip)*min(.49,bend/max(1,np.linalg.norm(right-tip)))
        for fraction in np.linspace(0,1,7):
            u=1-fraction
            path.append(tuple(u*u*entry+2*u*fraction*tip+fraction*fraction*exit))
    return path


def follow_pointer(canvas, x, y, width, height, softness, alpha, lean=0, *,
                   vertical_softness=None, rounded=False, contour=None):
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
    left, top = x-padding, y-padding
    if rounded:
        left, top = int(np.floor(left)), int(np.floor(top))
        # The triangle and stem have different radii. Keep the notch open.
        outline = [(0,0),(1,.558),(.984,.596),(.595,.601),
                   (.806,.946),(.799,.978),(.760,.997),(.688,1),
                   (.648,.979),(.362,.684),(0,.794)]
        radii = np.array([.046,.058,.023,.01,.035,.022,.018,.021,.024,.010,.12])*w
        outline = contour if contour is not None else outline
        points = [(p+(x%1)*oversample+px*w+lean*py*oversample,
                   p+(y%1)*oversample+py*h) for px,py in outline]
        points=rounded_arrow(points,radii)
        rim = max(2, round(w*.085))
        ink = "#000000"
    else:
        points = [(p + round(px * (w - 1) + lean * py * oversample),
                   p + round(py * (h - 1))) for px, py in shape]
        rim = max(2, round(w * .065))
        ink = "#050507"
    draw.line([*points, points[0]], fill="#ffffff", width=rim * 2, joint="curve")
    if rounded:
        for vx,vy in points:
            draw.ellipse((vx-rim,vy-rim,vx+rim,vy+rim),fill="#ffffff")
    else:
        for vertex in (points[0], points[2], points[8]):
            vx, vy = vertex
            draw.ellipse((vx - rim, vy - rim, vx + rim, vy + rim), fill="#ffffff")
    draw.polygon(points, fill=ink)
    if vertical_softness is None:
        vertical_softness=softness
    if max(softness,vertical_softness) > .15:
        radius=(softness*oversample,vertical_softness*oversample)
        sprite=sprite.convert("RGBa").filter(ImageFilter.GaussianBlur(radius)).convert("RGBA")
    sprite = sprite.resize((round(sprite.width / oversample), round(sprite.height / oversample)), Image.Resampling.LANCZOS)
    composite(canvas, sprite, left, top, alpha)


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


def capsule_coverage(columns, rows, shape):
    """Rasterize an editable capsule with a curved centerline and soft edge."""
    cx, cy, width, height, softness, slope, bend = shape
    across = columns - cx
    u = np.clip(across / (width / 2), -1, 1)
    y = rows - (cy + slope * u + bend * (1 - u * u))
    radius = height / 2
    distance = np.hypot(np.maximum(np.abs(across) - (width / 2 - radius), 0), y) - radius
    return .5 * (1 - np.tanh(distance * .8 / max(softness, .25)))


def camera_island_layer(columns, rows, optics):
    """Build the dark opening, separate sensor insert, and reflected lens rings."""
    coverage = capsule_coverage(columns, rows, optics["opening"])
    inset = capsule_coverage(columns, rows, optics["sensor"])
    rgb = np.asarray(optics["black"]) + inset[..., None] * (
        np.asarray(optics["sensor_color"]) - optics["black"])
    for cx, cy, rx, ry, red, green, blue in optics["reflections"]:
        tint = np.exp(-((columns - cx) / rx) ** 2 - ((rows - cy) / ry) ** 2)
        rgb += tint[..., None] * [red, green, blue]
    return coverage, np.clip(rgb, 0, 255)


def camera_edge_light(columns, rows, reflections):
    tint = np.zeros((*rows.shape,3),dtype=float)
    for cx,cy,rx,ry,*pigment in reflections:
        reflection = np.exp(-((columns-cx)/rx)**2-((rows-cy)/ry)**2)
        tint += reflection[...,None]*pigment
    return tint


def paint_camera_island(stage, optics):
    cx, cy, width, height, softness, slope, bend = optics["opening"]
    edge_reflections = optics.get("edgeReflections")
    pad = 4 * softness + abs(slope) + abs(bend) + 6
    if edge_reflections:
        pad = max(pad,54)
    left = max(0, int(cx - width / 2 - pad))
    top = max(0, int(cy - height / 2 - pad))
    right = min(stage.width, int(cx + width / 2 + pad) + 1)
    bottom = min(stage.height, int(cy + height / 2 + pad) + 1)
    rows, columns = np.mgrid[top:bottom, left:right]
    alpha, rgb = camera_island_layer(columns, rows, optics)
    if edge_reflections:
        box=(left,top,right,bottom)
        paper=np.asarray(stage.crop(box).convert("RGB"),dtype=float)
        paper += camera_edge_light(columns,rows,edge_reflections)
        stage.paste(Image.fromarray(np.uint8(np.clip(np.rint(paper),0,255))),box)
    sprite = Image.fromarray(np.uint8(np.rint(np.dstack((rgb, 255 * alpha)))))
    composite(stage, sprite, left, top)


def message_outline(size, pose, origin=(0, 0), supersample=3):
    """Draw the body and outgoing tail on the same antialiased plane."""
    width, height = size
    x, y, w, h, radius, tail_width, tail_height = pose
    left, top = origin
    z = supersample
    mask = Image.new("L", (width*z, height*z))
    draw = ImageDraw.Draw(mask)
    x, y = (x-left)*z, (y-top)*z
    w, h, radius = w*z, h*z, radius*z
    draw.rounded_rectangle((x, y, x+w, y+h), radius, fill=255)
    if tail_width and tail_height:
        edge, floor = x+w, y+h
        u, v = tail_width*z, tail_height*z
        curve_polygon(draw, (edge-u*.64,floor-v*1.55), (
            ((edge+u*.20,floor-v*1.62),(edge-u*.30,floor-v*.48),
             (edge+u,floor+v*.12)),
            ((edge+u*.24,floor+v*.10),(edge-u*.52,floor-v*.11),
             (edge-u*1.12,floor-v*.56)),
            ((edge-u*1.24,floor-v*.79),(edge-u*1.10,floor-v*1.08),
             (edge-u*.64,floor-v*1.55)),
        ), 255)
    return mask.resize(size,Image.Resampling.LANCZOS)


def paint_message_surface(stage, pose, palette):
    x, y, w, h, radius, tail_width, tail_height, *lean = pose
    slope = lean[0] if lean else 0
    lift = math.ceil(abs(slope)*(w/2+tail_width))
    left = max(0, int(x)-4)
    top = max(0, int(y)-4-lift)
    right = min(stage.width, int(x+w+tail_width)+5)
    bottom = min(stage.height, int(y+h+tail_height*.12)+5+lift)
    size = (right-left, bottom-top)
    alpha = message_outline(size, pose[:7], (left,top))
    if slope:
        midpoint=x+w/2-left
        alpha=alpha.transform(size,Image.Transform.AFFINE,(1,0,0,-slope,1,slope*midpoint),
                              Image.Resampling.BICUBIC)
    first, last = np.asarray(palette)
    values = np.clip((np.arange(left,right)+.5-x)/w,0,1)
    line = np.rint(first+values[:,None]*(last-first)).astype(np.uint8)
    rgba = Image.fromarray(np.broadcast_to(line[None,:,:],(size[1],size[0],3))).convert("RGBA")
    rgba.putalpha(alpha)
    composite(stage,rgba,left,top)
