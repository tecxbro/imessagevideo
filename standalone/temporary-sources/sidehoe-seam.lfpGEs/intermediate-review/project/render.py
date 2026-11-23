"""Frame-indexed original vector stage. Render input is scene.json and its local font."""
import argparse
from bisect import bisect_right
from functools import lru_cache
import json
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from artwork import app_icon, badge, composite, curved_heart, font, heart, messages_font, oval, pictogram, portrait
from artwork import rounded_gradient, sprite_portrait, stamp, text
from treatments import calendar_emoji, calendar_face, follow_aperture, follow_pointer, lit_phone


SIZE = 1000
BASE = "#fdfdfd"
INK = "#17171d"
MUTED = "#77747e"


def clamp(x, y=0, z=1):
    return min(z, max(x, y))


def up(f, a, b):
    return clamp((f-a)/(b-a))


def ease(p):
    return p*p*(3-2*p)


def tween(f,a,b):
    return ease(up(f,a,b))


def mix(a,b,p):
    return a+(b-a)*p


def interpolate(track, f):
    frames=[k[0] for k in track]
    at=bisect_right(frames,f)
    if at==0:
        return track[0][1:]
    if at==len(track):
        return track[-1][1:]
    a,b=track[at-1:at+1]
    return [mix(x,y,up(f,a[0],b[0])) for x,y in zip(a[1:],b[1:])]


def layer(w=SIZE,h=SIZE):
    return Image.new("RGBA",(w,h))


def blur(im,radius):
    spread = max(radius) if isinstance(radius,tuple) else radius
    if spread <= .25:
        return im
    return im.convert("RGBa").filter(ImageFilter.GaussianBlur(radius)).convert("RGBA")


def floating_control(im, x, y, w, h, radius):
    pad = 24
    shadow = layer(w+2*pad,h+2*pad)
    ImageDraw.Draw(shadow).rounded_rectangle((pad,pad+3,pad+w,pad+h+5),radius,fill=(102,95,114,39))
    composite(im,blur(shadow,9),x-pad,y-pad)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x,y,x+w,y+h),radius,fill="#f8f8fa",outline="#fdfdfd",width=2)


@lru_cache(maxsize=84)
def wash(strength, variant="pink"):
    yy, xx = np.mgrid[0:1:240j, 0:1:240j]
    if variant == "apps":
        field = np.exp(-((xx-.47-.125*(yy-.50))/.269)**2-((yy-.50)/.25)**2)
        tint = field[:, :, None] * np.array([33.5, 57.7, .9])
    else:
        cx, cy, sx, sy, shear = (1.80, .97, 1.46, .455, 1.74) if variant == "closing" else (1.70, 1.03, 1.48, .42, 1.46)
        field = np.exp(-((xx-cx+shear*(yy-cy))/sx)**2-((yy-cy)/sy)**2)
        color = [28.7, 156.5, 18.2] if variant == "closing" else [20, 135, 10]
        tint = field[:, :, None] * np.array(color)
        if variant == "pink":
            edge = np.exp(-((xx-1.0)/.23)**2-((yy-.96)/.25)**2)
            tint += edge[:,:,None]*np.array([7,34,5])
    data = np.uint8(np.clip(253-tint*(strength/40), 0, 255))
    return Image.fromarray(data).resize((SIZE, SIZE), Image.Resampling.BICUBIC).convert("RGBA")


@lru_cache(maxsize=42)
def measured_wash(controls):
    """Evaluate two editable light fields over the original stage matte."""
    yy,xx = np.mgrid[0:1:240j,0:1:240j]
    tint = np.zeros((240,240,3),dtype=np.float32)
    for offset in (0,8):
        cx,cy,sx,sy,shear,r,g,b = controls[offset:offset+8]
        light = np.exp(-((xx-cx+shear*(yy-cy))/sx)**2-((yy-cy)/sy)**2)
        tint += light[:,:,None]*np.array([r,g,b])
    rgb = np.rint(np.clip(253-tint,0,255)).astype(np.uint8)
    return Image.fromarray(rgb).resize((SIZE,SIZE),Image.Resampling.BICUBIC).convert("RGBA")


@lru_cache(maxsize=28)
def handset_veil(controls, response=(1,1)):
    yy,xx=np.mgrid[0:1:200j,0:1:200j]
    tint = np.zeros((200,200,3))
    coverage = np.zeros(xx.shape)
    for (cx,cy,sx,sy,shear,r,g,b),gain in zip(controls,response,strict=True):
        field = np.exp(-((xx-cx+shear*(yy-cy))/sx)**2-((yy-cy)/sy)**2)
        tint += field[...,None]*[r,g,b]
        coverage += field*g*gain/175
    # Match the paper tint separately from the light reflected in dark artwork.
    alpha = np.clip(coverage, 0, .94)
    pigment = 253 - tint/np.maximum(alpha[...,None], 1/255)
    rgba = np.dstack((np.clip(pigment,0,255),alpha*255))
    return Image.fromarray(np.uint8(np.rint(rgba))).resize((SIZE,SIZE),Image.Resampling.BICUBIC)



def spectral_rim(stage, controls):
    left,right = controls[0][0],controls[-1][0]+1
    top = max(0,math.floor(min(row[1] for row in controls))-19)
    bottom = min(stage.height,math.ceil(max(row[1] for row in controls))+62)
    columns = np.arange(left,right)
    offsets = np.array(controls,dtype=float)
    y = np.arange(top,bottom)[:,None]-np.interp(columns,offsets[:,0],offsets[:,1])
    samples = np.array([np.interp(columns,offsets[:,0],values) for values in offsets[:,2:].T])
    samples = samples.reshape(6,3,-1).transpose(0,2,1)
    tint = np.zeros((bottom-top,right-left,3))
    for (offset,width),band in zip(((-3,4),(5,5.1),(12,5.2),(21,7.2),(30,6.5),(43,5.7)),samples):
        tint += np.exp(-((y-offset)/width)**2)[...,None]*band
    box = (left,top,right,bottom)
    rgb = np.asarray(stage.crop(box).convert("RGB"),dtype=float)
    lit = Image.fromarray(np.uint8(np.rint(np.clip(rgb+tint,0,255))))
    stage.paste(lit,box)

def vertical_blur(image, length, *, horizontal=0):
    if max(abs(horizontal), length) < 2:
        return image
    image = image.convert("RGBa")
    mixed = image
    count = min(13, max(3, round(max(abs(horizontal), length)/5)))
    if horizontal:
        count = max(count, math.ceil(math.hypot(horizontal,length)))
    ys = np.linspace(-length/2, length/2, count)
    xs = np.linspace(-horizontal/2, horizontal/2, count)
    for i, (dx, dy) in enumerate(zip(xs, ys), 2):
        shifted = image.transform(image.size, Image.Transform.AFFINE, (1, 0, dx, 0, 1, dy),
                                  Image.Resampling.BILINEAR)
        mixed = Image.blend(mixed, shifted, 1/i)
    return mixed.convert("RGBA")


def apply_fringe(image, x_offset, y_offset):
    r, g, b, alpha = image.split()
    def shift(channel, dx, dy):
        return channel.transform(channel.size, Image.Transform.AFFINE, (1, 0, dx, 0, 1, dy),
                                 Image.Resampling.BICUBIC)
    return Image.merge("RGBA", (shift(r, -x_offset, y_offset), g, shift(b, x_offset, -y_offset), alpha))


def rim_fringe(image, x_offset, y_offset, height_center, breadth):
    """Confine aberration to the lens edge and the lower reflections."""
    width,height=image.size
    yy,xx=np.mgrid[:height,:width]
    top=np.exp(-((yy-height_center)/43)**2-((xx-width*.5)/(width*breadth))**2)
    bottom=np.exp(-((yy-660)/140)**2)
    corners=np.exp(-((xx-width*.06)/60)**2)+np.exp(-((xx-width*.94)/60)**2)
    mask=np.rint(np.clip(top+bottom*corners,0,1)*255).astype(np.uint8)
    aberrated=apply_fringe(image,x_offset,y_offset)
    return Image.composite(aberrated,image,Image.fromarray(mask))


def lens_ripple(image, displacement_samples):
    """Local top-edge refraction, tapering independently down the phone face."""
    w,h = image.size
    strip_height = 220
    samples=[(0,0),*displacement_samples,(w,0)]
    px,py=zip(*samples)
    def displacement(x):
        return -np.interp(x,px,py)*1.15
    mesh = []
    for x in range(0,w,12):
        right = min(w,x+12)
        dy_left,dy_right = displacement(x),displacement(right)
        mesh.append(((x,0,right,strip_height),
                     (x,dy_left,x,strip_height,right,strip_height,right,dy_right)))
    mesh.append(((0,strip_height,w,h),(0,strip_height,0,h,w,h,w,strip_height)))
    return image.transform(image.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)


def register_lens_rails(body, knots):
    """Register each editable casing rail between the outside and glass contours."""
    width, height = body.size
    controls = np.asarray(knots)
    rows = np.arange(height)
    values = np.array([np.interp(rows,controls[:,0],column)
                       for column in controls[:,1:].T]).T
    data = np.asarray(body.convert("RGBa"))
    result = data.copy()
    for side, (left,right) in enumerate(((0,166),(width-166,width))):
        columns = np.arange(left,right)
        warp = values[:,side*4:(side+1)*4]
        for y,(a,b,c,d) in enumerate(warp):
            source_x = np.interp(columns,(left,a,b,right),(left,c,d,right))
            ix = source_x.astype(int)
            fraction = (source_x-ix)[:,None]
            result[y,left:right] = np.rint(
                data[y,ix]*(1-fraction)+data[y,np.minimum(ix+1,width-1)]*fraction)
    return Image.fromarray(result,mode="RGBa").convert("RGBA")


def assistant_intro_pin(stage, x, y, size, distortion):
    """Render the first pin through the same moving glass as the casing."""
    pad = 24
    diameter = round(size)
    pin = layer(diameter+2*pad,diameter+2*pad)
    center = pin.width/2
    stamp(pin,badge(128),center,center,diameter)
    mesh = []
    for top in range(0,pin.height,4):
        bottom = min(top+4,pin.height)
        delta = []
        for row in (top,bottom):
            t = (row-center)/diameter
            alpha = math.exp(-((t+.37)/.19)**2)
            delta.append(distortion*alpha*(math.sin(t*30)+.39*math.cos(t*44)))
        mesh.append(((0,top,pin.width,bottom),
                     (delta[0],top,delta[1],bottom,pin.width+delta[1],bottom,
                      pin.width+delta[0],top)))
    pin = pin.transform(pin.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
    pin = apply_fringe(pin,3.2,2.3)
    composite(stage,pin,x-center,y-center)


def rail_flare(stage, controls):
    """Cast the exit-side prism color along the lower rails."""
    y,x = np.mgrid[880:SIZE,0:SIZE]
    rgb = np.asarray(stage.crop((0,880,SIZE,SIZE)).convert("RGB"),dtype=float)
    for cx,cy,rx,ry,angle,red,green,blue in controls:
        light = np.exp(-((x-cx-(y-cy)*angle)/rx)**2-((y-cy)/ry)**2)
        rgb += light[...,None]*[red,green,blue]
    stage.paste(Image.fromarray(np.uint8(np.clip(np.rint(rgb),0,255))),(0,880))


def exposed_appointment(left, right, pose, opacity, border):
    """Draw a calendar bar with separate leading and trailing shutter widths."""
    top,bottom,leading,trailing,red,green,blue = pose
    x0,x1 = math.floor(left)-4,math.ceil(right)+4
    y0 = max(0,math.floor(top-5*leading))
    y1 = min(SIZE,math.ceil(bottom+5*trailing))
    x = np.arange(x0,x1)+.5
    y = np.arange(y0,y1)+.5

    def edge_samples(coords, position, spread):
        z = (coords-position)/(spread*math.sqrt(2))
        return .5+.5*np.fromiter(map(math.erf,z),dtype=float,count=len(z))

    across = np.clip(edge_samples(x,left,1)-edge_samples(x,right,1),0,1)
    shutter = np.clip(edge_samples(y,top,leading)-edge_samples(y,bottom,trailing),0,1)
    bar = np.empty((len(y),len(x),4),dtype=np.uint8)
    bar[:,:,:3] = np.rint([red,green,blue])
    bar[:,:,3] = np.rint(opacity*shutter[:,None]*across[None,:])
    result = Image.fromarray(bar)
    accent = np.empty_like(bar)
    accent[:,:,:3] = border
    line = np.clip(edge_samples(x,left,1)-edge_samples(x,left+5,1),0,1)
    accent[:,:,3] = np.rint(255*shutter[:,None]*line[None,:])
    result.alpha_composite(Image.fromarray(accent))
    return result,x0,y0


def panel_wipe(im, masks, frame):
    d = ImageDraw.Draw(im)
    for onset, x, y, width, height in masks:
        if frame >= onset:
            d.rectangle((x, y, x+width, y+height), fill=(0, 0, 0, 0))


def gentle_characters(im, label, x, y, size, weight, f, onset, spacing, tinted=False):
    d=ImageDraw.Draw(im,"RGBA")
    if f >= onset+spacing*(len(label)-1)+7:
        text(d,x,y,label,size,(21,21,21),weight,"center")
        return
    face=font(size,weight)
    left=x-face.getlength(label)/2
    accents=[(211,128,222),(163,139,237),(104,207,217),(224,189,107)]
    for i,glyph in enumerate(label):
        a=up(f,onset+spacing*i,onset+spacing*i+4)
        after=up(f,onset+spacing*i+2,onset+spacing*i+7)
        if a:
            base=accents[i%len(accents)] if tinted else (143,141,151)
            color=tuple(round(mix(v,21,after)) for v in base)
            c=tuple(round(mix(250,v,a)) for v in color)
            text(d,left+face.getlength(label[:i]),y+(1-ease(a))*size*.19,glyph,size,c,weight)


def fitted_badge(im, box, corner, radius=0, opacity=1, shine=0, *, reveal=1, closing_finish=None):
    x,y,w,h=box
    mark=badge(corner,reveal,closing_finish)
    if shine:
        highlight=Image.new("RGBA",mark.size,(175,165,252,round(shine)))
        mixed=Image.alpha_composite(mark,highlight)
        mixed.putalpha(mark.getchannel("A"))
        mark=mixed
    left,top=x-w/2,y-h/2
    if closing_finish is not None:
        x0,y0=math.floor(left)-4,math.floor(top)-4
        xs,ys=mark.width/w,mark.height/h
        width,height=math.ceil(left+w)-x0+4,math.ceil(top+h)-y0+4
        transform=xs,0,(x0-left)*xs,0,ys,(y0-top)*ys
        mark=mark.transform((width,height),Image.Transform.AFFINE,transform,Image.Resampling.BICUBIC)
        left,top=x0,y0
    else:
        mark=mark.resize((max(1,round(w)),max(1,round(h))),Image.Resampling.LANCZOS)
    composite(im,blur(mark,radius),left,top,opacity)


def fit_ink(im, caption, bbox, weight, opacity=1, blur_radius=0, *,
            family=font, ink=(20,20,20), character_opacity=None, fractional=False):
    x,y,w,h=bbox
    if opacity<=0 or w<=0 or h<=0:
        return
    face = family(190 if fractional else 160, weight)
    full_box = None
    if family is font and character_opacity is None:
        plane=layer(1050,140)
        text(ImageDraw.Draw(plane),10,12,caption,80,(*ink,255),weight)
    elif character_opacity is None:
        plane = layer(round(face.getlength(caption))+25, 245 if fractional else 210)
        draw = ImageDraw.Draw(plane)
        draw.text((10, 5), caption, font=face, fill=(*ink, 255), anchor="lt")
    else:
        plane = layer(round(face.getlength(caption))+25, 210)
        draw = ImageDraw.Draw(plane)
        for index, character in enumerate(caption):
            x_char = 10 + face.getlength(caption[:index])
            draw.text((x_char, 5), character, font=face,
                      fill=(*ink, round(255*character_opacity[index])), anchor="la")
        # Fit to the full line so entering characters retain their final positions.
        full_box = draw.textbbox((10, 5), caption, font=face, anchor="la")
    box=plane.getbbox()
    if box is None:
        return
    if full_box is not None:
        box = full_box
    cropped=plane.crop(box)
    if fractional:
        column,row=math.floor(x)-2,math.floor(y)-2
        xs,ys=cropped.width/w,cropped.height/h
        shift=(xs,0,(column-x)*xs,0,ys,(row-y)*ys)
        extent=(math.ceil(x+w)-column+2,math.ceil(y+h)-row+2)
        ink=cropped.transform(extent,Image.Transform.AFFINE,shift,Image.Resampling.BICUBIC)
        x,y=column,row
    else:
        ink=cropped.resize((max(1,round(w)),max(1,round(h))),Image.Resampling.BICUBIC)
    padding = max(8,math.ceil(3*max(blur_radius))) if isinstance(blur_radius,tuple) else 8
    patch=layer(ink.width+2*padding,ink.height+2*padding)
    patch.alpha_composite(ink,(padding,padding))
    composite(im,blur(patch,blur_radius),x-padding,y-padding,opacity)


@lru_cache(maxsize=20)
def reveal_caption_mask(caption):
    face = messages_font(160,615)
    ink = Image.new("L",(round(face.getlength(caption))+28,210))
    ImageDraw.Draw(ink).text((5,5),caption,font=face,fill=255,anchor="lt")
    bounds = ink.getbbox()
    return ink.crop(bounds).resize((600,120),Image.Resampling.BICUBIC) if bounds else None


def revealed_caption(im, caption, settings):
    x,y,width,height,opacity,shear,reveal,soft_edge,softness = settings
    ink = reveal_caption_mask(caption)
    if ink is None:
        return
    ink = ink.filter(ImageFilter.GaussianBlur(softness*2))
    fade = np.clip((reveal - np.linspace(0,1,ink.width))/soft_edge+.5,0,1)
    alpha = np.asarray(ink)*fade[None,:]**2*(3-2*fade[None,:])*opacity
    alpha = Image.fromarray(np.uint8(np.rint(alpha)))
    # Warp the authored letters in a transparent padded patch so the feather
    # follows the source's line reveal and the baseline leans as it moves.
    padding = 12
    x0 = math.floor(x)-padding
    y0 = math.floor(y+min(0,shear))-padding
    dx,dy = x0-x,y0-y
    sx,sy = 599/width,119/height
    patch = alpha.transform((math.ceil(width)+2*padding, math.ceil(height+abs(shear))+2*padding),
                            Image.Transform.AFFINE,(sx,0,sx*dx,-sy*shear/width,sy,
                                                    sy*(dy-shear*dx/width)),
                            Image.Resampling.BICUBIC)
    shadow = Image.new("RGBA",patch.size,(0,0,0,0))
    shadow.putalpha(patch)
    composite(im,shadow,x0,y0)

def cursor(im,x,y,r=0, opacity=1, size=1, softness=(0,0)):
    pad=72 if r else 0
    glyph=layer(68+2*pad,72+2*pad)
    d=ImageDraw.Draw(glyph)
    points=[(11,9),(51,43),(31,42),(43,65),(34,70),(22,48),(12,59)]
    d.polygon([(px+pad,py+pad) for px,py in points],fill="#15141b",outline="#ffffff",width=3)
    pivot_x,pivot_y=11+pad,9+pad
    if r:
        glyph=glyph.rotate(-r,resample=Image.Resampling.BICUBIC,center=(pivot_x,pivot_y))
    if any(softness):
        radius=tuple(value/size for value in softness)
        glyph=glyph.convert("RGBa").filter(ImageFilter.GaussianBlur(radius)).convert("RGBA")
    composite(im,glyph,x-pivot_x*size,y-pivot_y*size,opacity,size)


@lru_cache(maxsize=8)
def shell_material(w, h, radius, bevel_fraction=.032, top_exposure=False):
    yy, xx = np.mgrid[:h, :w]
    edge_x = np.abs(xx-(w-1)/2)-(w/2-radius-1)
    edge_y = np.abs(yy-(h-1)/2)-(h/2-radius-1)
    distance = np.hypot(np.maximum(edge_x,0), np.maximum(edge_y,0))
    distance += np.minimum(np.maximum(edge_x,edge_y),0)-radius
    bevel = max(10, round(w*bevel_fraction))
    inset = -distance
    peak = np.exp(-((inset-bevel*.23)/max(1.3,bevel*.16))**2)
    light = (23 + peak*(32+73*np.exp(-yy/(h*.21)))
             + 33*np.exp(-((xx-w*.15)/(w*.12))**2)*np.exp(-yy/(h*.17)))
    if top_exposure:
        profile = [64,68,79,112,150,145,62,24,32,48,10,5,5,3,0,0,2]
        depth = [0,1,3,5,7,9,11,13,15,17,19,21,23,25,29,32,35]
        light = np.interp(inset*35/bevel,depth,profile)
    glass = np.clip((inset-bevel+.5)*1.1,0,1)
    rgb = light*(1-glass)+253*glass
    alpha = np.clip(inset+.5,0,1)*255
    pixels = np.stack((rgb,rgb,np.minimum(rgb+2,253),alpha),axis=2).astype(np.uint8)
    return Image.fromarray(pixels)


def phone_shell(im, w, h, radius, bevel_fraction=.032):
    im.alpha_composite(shell_material(w,h,radius,bevel_fraction))


@lru_cache(maxsize=4)
def rim_only(w,h,radius):
    outer = shell_material(w,h,radius).copy()
    alpha = outer.getchannel("A")
    bevel = max(10, round(w*.032))
    ImageDraw.Draw(alpha).rounded_rectangle((bevel,bevel,w-bevel-1,h-bevel-1),radius-bevel,fill=0)
    outer.putalpha(alpha)
    return outer


def status(d,w,y,label,island=False):
    text(d,41 if island else 92,y if island else y-18,label,16 if island else 35,INK,630)
    size=.41 if island else 1
    x=w-(98 if island else 250)
    top=y-18 if not island else y
    ink="#272729"
    for i,h in enumerate((10,16,21,27)):
        left=x+i*12*size
        d.rounded_rectangle((left,top+(27-h)*size,left+6.5*size,top+26*size),
                            2.7*size,fill=ink)
    center=x+78*size
    baseline=top+28*size
    for radius,thickness in ((29,5.4),(20,5)):
        radius*=size
        d.arc((center-radius,baseline-radius,center+radius,baseline+radius),
              227,313,fill=ink,width=max(1,round(thickness*size)))
    dot=10*size
    d.pieslice((center-dot,baseline-dot,center+dot,baseline+dot),226,314,fill=ink)
    x+=117*size
    d.rounded_rectangle((x,top+3*size,x+45*size,top+22*size),5*size,fill=ink)
    d.pieslice((x+46*size,top+9*size,x+57*size,top+18*size),270,90,fill=ink)
    if island:
        d.rounded_rectangle((w/2-58,y-20,w/2+58,y+14),17,fill="#09090a")
        d.rounded_rectangle((w/2-52,y-13,w/2+8,y+7),10,fill="#141415")
        oval(d,w/2+41,y-3,8,8,"#14131b")
        oval(d,w/2+41,y-3,3.3,3.3,"#292b41")


def microphone(d,x,y,size,color):
    width=max(1,round(size*.105))
    d.rounded_rectangle((x-size*.22,y-size*.55,x+size*.22,y+size*.10),
                        size*.20,outline=color,width=width)
    d.arc((x-size*.36,y-size*.37,x+size*.36,y+size*.29),0,180,fill=color,width=width)
    d.line((x,y+size*.30,x,y+size*.49),fill=color,width=width)
    d.line((x-size*.19,y+size*.49,x+size*.19,y+size*.49),fill=color,width=width)


def keyboard_glyph(d,key,x,y):
    ink="#596067"
    if key=="shift":
        d.polygon([(x-9,y+1),(x,y-9),(x+9,y+1),(x+5,y+1),
                   (x+5,y+8),(x-5,y+8),(x-5,y+1)],fill="#111111")
    elif key=="delete":
        d.polygon([(x-11,y),(x-5,y-7),(x+10,y-7),(x+10,y+7),(x-5,y+7)],
                  outline=ink,width=2)
        d.line((x-2,y-3,x+5,y+3),fill=ink,width=2)
        d.line((x-2,y+3,x+5,y-3),fill=ink,width=2)
    elif key=="emoji":
        d.ellipse((x-12,y-12,x+12,y+12),outline=ink,width=2)
        for eye in (x-4,x+4):
            oval(d,eye,y-3,1.4,2.2,ink)
        d.arc((x-7,y-3,x+7,y+8),4,176,fill=ink,width=2)


class Film:
    def __init__(self, scene):
        self.s=scene
        self.c=scene["copy"]
        self.palette=scene["palette"]
        self.events={e["id"]:e["frame"] for e in scene["timeline"]["events"]}

    def at(self,event):
        return self.events[event]

    def track(self,key,f):
        return interpolate(self.s["tracks"][key], f)

    def source_glyph(self, frame, draw, name, x, y, size):
        glyphs = self.s["finish"]["glyphs"]
        if name not in glyphs:
            return pictogram(draw, name, x, y, size)
        glyph = glyphs[name]
        geometry = interpolate(glyph["ink"], frame)
        font_file = os.environ.get("SIDEHOE_EMOJI_FONT", "/System/Library/Fonts/Apple Color Emoji.ttc")
        return calendar_emoji(draw, glyph["unicode"], x, y, size, geometry, font_file)

    def avatar(self,im,key,x,y,diam,opacity=1,bg="",neutral=False,*,lit=False):
        spec = self.s["avatars"][key]
        lights = (bg,bg,1) if lit and bg else ()
        if lit and not bg:
            lights = tuple(self.s.get("pinLighting", {}).get(key, ()))
        asset = (sprite_portrait(key,spec[0],bg,not neutral,lights) if self.s.get("portraitSprites")
                 else portrait(tuple(spec),bg,neutral))
        stamp(im,asset,x,y,diam,opacity)

    def inbox(self,im,f):
        i=layer(820,2500)
        chrome=layer(820,630)
        d=ImageDraw.Draw(chrome)
        status(d,815,214,self.c["status"])
        floating_control(chrome, 77, 292, 109, 68, 30)
        d.text((131,312),self.c["edit"],font=messages_font(32,630),fill="#090909",anchor="mt")
        d.text((410,306),self.c["inbox"],font=messages_font(35,620),fill="#090909",anchor="mt")
        floating_control(chrome, 666, 292, 68, 68, 34)
        for width,y in [(38,318),(28,327),(16,336)]:
            d.rounded_rectangle((696-width/2,y,696+width/2,y+3),2,fill=INK)

        if f<10:
            alpha,softness,rise=self.track("inboxIntroHeader",f)
            composite(i,vertical_blur(blur(chrome,softness),softness*1.8),0,rise,alpha)
        else:
            composite(i,chrome,0,0)
        d=ImageDraw.Draw(i)
        for j,((label,key),x) in enumerate(zip(self.s["inboxPins"],[169,411,651])):
            if f<10:
                continue
            p=tween(f,0 if j==1 else 1,5 if j==1 else 8)
            self.avatar(i,key,x,473+68*(1-p),162*(.78+.22*p),
                        (.58+.42*p if f<10 else .25+.75*p) if j==1 else p,lit=True)
            if p>.38:
                text(d,x,571,label,26,"#353535",510,"center")
        p=tween(f,2.5,8) if f<10 else tween(f,4,11)
        tag=None
        if p>0:
            tag=layer(255,80)
            tagd=ImageDraw.Draw(tag)
            tagd.rounded_rectangle((3,4,252,70),21,fill=(253,253,253,224),outline="#f1f1f3",width=2)
            tagd.polygon([(186,63),(211,63),(204,77)],fill="#fdfdff")
            text(tagd,124,22,self.c["pinNote"],25,INK,545,"center",
                 glyph=lambda *args: self.source_glyph(f,*args))
            if f>=10:
                composite(i,tag,285,359+(1-p)*22,p)

        rows=layer(820,2240)
        rd=ImageDraw.Draw(rows)
        for j,(name,quote,time,key) in enumerate(self.s["inboxRows"]):
            y=696+j*171
            backdrop = self.s.get("inboxRowColors",{}).get(name,"")
            alpha = 1-tween(f,49,54) if j==0 else 1
            if alpha:
                row = layer(820,138)
                drow = ImageDraw.Draw(row)
                oval(drow,80,56,8,8,"#19abdf")
                self.avatar(row,key,140,55,69,bg=backdrop,lit=bool(backdrop))
                text(drow,191,11,name,29,INK,630)
                text(drow,191,52,quote,26,MUTED)
                text(drow,690,14,time,23,"#98959f",400,"right")
                drow.line((717,16,726,25,717,34),fill="#bdbac5",width=2)
                composite(rows,row,0,y,alpha)
            rd.line((193,y+137,740,y+137),fill="#ecebf1",width=1)
        y,=self.track("inboxY",f)
        scale,=self.track("inboxScale",f)
        amount=3*(1-up(f,0,6))+1.3*up(f,98,101)
        if f>=42:
            row_y,row_scale=self.track("inboxIdentifiedRowPose",f)
            row_layer=layer(820,2290)
            row_layer.alpha_composite(rows)
            ImageDraw.Draw(row_layer).rounded_rectangle((231,2260,590,2270),6,fill="#777580")
            streak,=self.track("inboxScrollSmear",f)
            if streak > 2:
                row_layer = row_layer.convert("RGBa").filter(
                    ImageFilter.GaussianBlur((.45,streak*.32))).convert("RGBA")
            composite(im,blur(row_layer,amount),500-410*row_scale,row_y,1,row_scale)
            if f<=59:
                chrome_y,chrome_scale=self.track("inboxChromePose",f)
                header=i.crop((0,0,820,620))
                if streak > 2:
                    header = header.convert("RGBa").filter(
                        ImageFilter.GaussianBlur((.38,streak*.23))).convert("RGBA")
                composite(im,header,500-410*chrome_scale,chrome_y,1,chrome_scale)
        else:
            d.rounded_rectangle((231,2260,590,2270),6,fill="#777580")
            composite(i,rows,0,0,tween(f,-.5,9) if f<10 else 1)
            composite(im,blur(i,amount),500-410*scale,y,1,scale)
        if f<10:
            for j,(label,key) in enumerate(self.s["inboxPins"]):
                pin=self.s["tracks"][f"inboxIntroPin{j}"]
                if f<pin[0][0]:
                    continue
                x,cy,diam,opacity=interpolate(pin,f)
                avatar_layer=layer(225,234)
                self.avatar(avatar_layer,key,112,108,diam,opacity,lit=True)
                if f>=3:
                    text(ImageDraw.Draw(avatar_layer),112,109+diam/2+15,label,25,INK,530,"center")
                composite(im,blur(avatar_layer,max(0,5-f*1.10)),x-112,cy-108)
            if tag is not None:
                _, center_y, _, _ = self.track("inboxIntroPin1",f)
                composite(im,blur(tag,5*(1-p)),387,center_y-115,p,.91)

    def identity(self,im,f):
        cx,cy,w,h=self.track("identityMeasuredBox",f)
        a=up(f,101.7,104.4)
        amount=max(3.2*(1-tween(f,102,105)),1.4+2.7*tween(f,105,109)*(1-tween(f,110,118)),6*tween(f,129,133))
        corner=round(mix(87,128,up(f,105,113))/4)*4
        fitted_badge(im,(cx,cy,w,h),corner,amount,a,reveal=round(tween(f,105,110),3))
        text_plate=layer()
        gentle_characters(text_plate,self.c["brand"],cx,cy+h*.64,77,650,f,
                          self.at("identity.name")-1,.68,True)
        exposure=max(amount,5*(1-tween(f,106,110)))
        composite(im,vertical_blur(blur(text_plate,exposure),exposure),0,0)

    def assistant(self,im,f):
        optics = self.s.get("assistantEntranceOptics",{}).get(str(f))
        height = 1030 if f==134 and optics else 830
        beneath=layer(900,height)
        bevel, = self.track("assistantBevelDepth",f)
        beneath.alpha_composite(shell_material(900,height,163,bevel/900,True))
        d=ImageDraw.Draw(beneath)
        d.rounded_rectangle((354,12,537,19),3,fill="#171719",outline="#535355")
        d.line((689,4,703,4),fill="#727278",width=2)
        ix,iy,iw,ih = self.track("assistantIslandBox",f)
        d.rounded_rectangle((ix,iy,ix+iw,iy+ih),ih/2,fill="#0a0a0c")
        d.rounded_rectangle((ix+13,iy+.19*ih,ix+.56*iw,iy+.80*ih),ih*.305,fill="#131315")
        oval(d,ix+.859*iw,iy+ih/2,16,16,"#161720")
        oval(d,ix+.859*iw,iy+ih/2,7,7,"#252b42")
        text(d,103,86,self.c["status"],34,INK,630)
        for i, height in enumerate((7, 12, 17, 21)):
            d.rounded_rectangle((604+11*i,116-height,612+11*i,116),3,fill=INK)
        d.arc((667,90,707,118),208,332,fill=INK,width=5)
        d.arc((674,99,700,118),208,332,fill=INK,width=4)
        oval(d,687,114,4,4,INK)
        d.rounded_rectangle((727,93,774,115),6,fill=INK)
        d.rectangle((776,100,781,108),fill=INK)
        floating_control(beneath, 85, 181, 113, 71, 32)
        floating_control(beneath, 720, 181, 70, 70, 35)
        for half,y_line in ((19,208),(14,218),(8,228)):
            d.rounded_rectangle((755-half,y_line,755+half,y_line+4),2,fill="#535258")
        text(d,143,208,self.c["edit"],33,INK,640,"center")
        if optics and "inbox" in optics:
            left,top,width,ink_height = optics["inbox"]
            title = layer()
            fit_ink(title,self.c["inbox"],(left,top,width,ink_height),700,
                    1,1,family=messages_font,ink=(27,27,28))
            # A short refraction passes over the title as the handset comes into focus.
            pad = 24
            box=(left-pad,top-pad,left+width+pad,top+ink_height+pad)
            raster=title.crop(box)
            mesh=[]
            for i in range(0,raster.width,5):
                j=min(i+5,raster.width)
                dy1,dy2=(8*math.sin((x-pad)/7.3)*math.exp(-((x-pad-width*.48)/(width*.5))**2)
                         for x in (i,j))
                mesh.append(((i,0,j,raster.height),
                            (i,dy1,i,raster.height+dy1,j,raster.height+dy2,j,dy2)))
            visible = raster.transform(raster.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
            composite(beneath,visible,box[0],box[1])
        else:
            text(d,450,207,self.c["inbox"],36,INK,650,"center")
        px,py,diam = self.track("assistantPinPose",f)
        name_y=py+diam/2+11
        pin_control = self.s["tracks"].get("assistantPinControls")
        if pin_control:
            left,right,side_diam,side_lift,pin_alpha,label_alpha = interpolate(pin_control,f)
        else:
            left,right,side_diam,side_lift,pin_alpha,label_alpha = 184,719,diam*.887,0,tween(f,134,138),1
        labels=layer(900,830)
        ld=ImageDraw.Draw(labels)
        for x,k,n in [(left,"marie","Marie"),(right,"darla","Darla")]:
            self.avatar(beneath,k,x,py+side_lift,side_diam,pin_alpha,lit=True)
            if f>=135:
                ld.text((x,name_y),n,font=messages_font(29,490),fill="#333333",anchor="mt")
        if optics and "pin" in optics:
            assistant_intro_pin(beneath,*optics["pin"])
        else:
            stamp(beneath,badge(128),px,py,diam)
        ld.text((px-14,name_y+4),self.c["brand"],font=messages_font(29,490),fill="#333333",anchor="mt")
        ld.regular_polygon((px+56,name_y+16,13),10,rotation=15,fill="#7e7587")
        ld.line((px+51,name_y+16,px+55,name_y+20,px+62,name_y+11),fill="#f8f6fa",width=2)
        composite(beneath,labels,0,0,label_alpha)
        x,y,width=self.track("assistantMeasuredPosition",f)
        # The handset and the first message row travel independently at the cut.
        row_y,row_alpha = self.track("assistantRowPose",f)
        if row_alpha:
            row = layer(900,125)
            rd = ImageDraw.Draw(row)
            self.avatar(row,"danielle",122,63,66)
            rd.text((184,0),self.c.get("assistantRowName","Natalie"),font=messages_font(34,660),
                    fill="#17171a",anchor="lt")
            rd.text((184,42),self.c.get("assistantRowPreview","Do u wanna go out tmrw?"),
                    font=messages_font(29,420),fill="#8d8b8d",anchor="lt")
            rd.text((800,2),"1:50 AM",font=messages_font(27,430),fill="#999499",anchor="rt")
            rd.line((821,5,830,14,821,23),fill="#d7d3dc",width=3)
            composite(beneath,row,0,row_y,row_alpha)
        basis = self.s["tracks"].get("assistantBodyFocus")
        if basis:
            spread, = interpolate(basis,f)
        else:
            spread=7*(1-tween(f,134,141))+4.8*tween(f,155,161)
        body = blur(beneath,spread)
        if f==134:
            body = vertical_blur(body,12 if optics else 17)
        if 135 <= f <= 137:
            gutter = 28
            padded = layer(body.width,body.height+gutter)
            padded.alpha_composite(body,(0,gutter))
            curved = lens_ripple(padded,self.s["measuredRimDisplacement"][str(f)])
            shift,breadth = {135:(4.3,.20),136:(4.9,.40),137:(1.8,.39)}[f]
            body = rim_fringe(curved,shift*.54,shift*.64,gutter+9,breadth)
            y -= gutter
        if optics and "rails" in optics:
            body = register_lens_rails(body,optics["rails"])
        composite(im,body.resize((round(width),body.height),Image.Resampling.BICUBIC),x,y)
        pose = self.track("assistantLighting",f)
        controls = tuple(tuple(pose[i:i+8]) for i in range(0,len(pose),8))
        response = tuple(self.track("assistantWashResponse",f))
        im.alpha_composite(handset_veil(controls,response))
        prism = self.s.get("assistantPrism",{}).get(str(f))
        if prism:
            spectral_rim(im,prism)
        if optics and "flare" in optics:
            rail_flare(im,optics["flare"])
        title_y,=self.track("assistantTitleY", f)
        for j,line in enumerate(self.c["assistant"]):
            lettering = self.s["tracks"].get(f"assistantLettering{j+1}")
            if lettering and f<lettering[0][0]:
                continue
            if lettering and f<=lettering[-1][0]:
                revealed_caption(im,line,interpolate(lettering,f))
                continue
            first=141 if j==0 else 142
            if first<=f<=160:
                fit_ink(im,line,self.track(f"assistantLine{j+1}",f),620,
                        1,2*tween(f,158,161),family=messages_font,ink=(8,8,8))
            elif f<first:
                title=layer()
                gentle_characters(title,line,500,title_y+j*75,60,640,f,134+j*4,.20)
                composite(im,blur(title,2.5*(1-tween(f,138,142))),0,0)

    def personal(self,im,f):
        start=self.at("personal.line-one")
        prefix_age=f-start
        fields = tuple(self.track("titleWashFields", f))
        im.alpha_composite(measured_wash(fields))
        title = layer()
        paths = self.s["tracks"].get("personalLettering")
        registered = paths and paths[0][0][0]<=f<=paths[0][-1][0]
        if registered:
            word_paths = self.s["tracks"].get("personalWordRegistration")
            for index,(caption,weight,path) in enumerate(zip(self.c["personal"],(620,700),paths,strict=True)):
                x,y,w,h,opacity,soft_x,soft_y,r,g,b = interpolate(path,f)
                color = round(r),round(g),round(b)
                words=caption.split()
                layout=word_paths[index] if word_paths else None
                if layout and layout[0][0]<=f<=layout[-1][0] and len(layout[0])==1+7*len(words):
                    controls = interpolate(layout,f)
                    for pos,word in enumerate(words):
                        wx,wy,ww,wh,stroke,focus,coverage=controls[pos*7:(pos+1)*7]
                        fit_ink(title,word,(wx,wy,ww,wh),stroke,min(1,coverage),focus,
                                family=messages_font,ink=color,fractional=True)
                else:
                    fit_ink(title,caption,(x,y,w,h),weight,min(1,opacity),(soft_x,soft_y),
                            family=messages_font,ink=color)
        else:
            line1=self.c["personal"][0]
            x,top,w,h=self.track("personalLine1",f)
            if prefix_age<0:
                pass
            elif prefix_age<5 and line1:
                sizes=(3,7,10,14,17)
                visible=min(len(line1),sizes[prefix_age])
                face=messages_font(80,620)
                scale=face.getlength(line1[:visible])/face.getlength(line1)
                fit_ink(title,line1[:visible],(x,top,w*scale,h),620,
                        mix(.48,.86,tween(f,162,168)),2*(1-tween(f,162,168)),
                        family=messages_font,ink=(0,0,0))
            else:
                fit_ink(title,line1,(x,top,w,h),620,mix(.82,1,tween(f,167,176)),
                        family=messages_font,ink=(0,0,0))
            onset=self.at("personal.line-two")
            if f>=onset:
                caption=self.c["personal"][1]
                hints=(179,178,178,182,183,177,181,183,180,182,181,177,177)
                alpha=None
                if f<186:
                    alpha=[tween(f,hints[min(index,len(hints)-1)]-1,185)
                           for index in range(len(caption))]
                ink=tuple(round(value*(1-tween(f,183,195))) for value in (108, 72, 110))
                fit_ink(title,caption,self.track("personalLine2",f),700,
                        family=messages_font,ink=ink,character_opacity=alpha)
        hearts = layer() if registered else title
        for heart_track in self.s["tracks"]["personalHearts"]:
            x, cy, width, height, angle, alpha = interpolate(heart_track, f)
            if alpha <= 0:
                continue
            mark = curved_heart(round(width*2), round(height*2), (247, 143, 253))
            mark = mark.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
            composite(hearts, mark, x-mark.width/4, cy-mark.height/4, alpha, .5)

        rise=tween(f,205,212)
        if rise:
            hearts=blur(hearts,(1.4*rise,6.5*rise))
        if registered:
            composite(im,title,0,0)
        composite(im,hearts,0,0)
        if f==212:
            self.cluster_entrance(im,f)

    def cluster_entrance(self,im,f):
        layer_image=layer()
        d=ImageDraw.Draw(layer_image)
        samples=[]
        poses="clusterEntrance" if f<=226 else "clusterVisibleDisks"
        for entry,keys in zip(self.s["cluster"],self.s["tracks"][poses]):
            if f<keys[0][0]:
                continue
            actor,_,_,_,_,color=entry
            x,y,size,opacity=interpolate(keys,f)
            samples.append((actor,x,y,size,opacity,color))
        if f>=214:
            silhouette=Image.new("L",layer_image.size)
            edge=ImageDraw.Draw(silhouette)
            for _,x,y,size,opacity,_ in samples:
                oval(edge,x,y,size*.61,size*.61,round(opacity*245))
            silhouette=silhouette.filter(ImageFilter.GaussianBlur(15)).point(
                lambda a:max(0,min(255,round((a-54)*8))))
            surround=Image.new("RGBA",layer_image.size,(236,232,251))
            surround.putalpha(silhouette)
            layer_image.alpha_composite(surround)
        for actor,x,y,size,opacity,color in samples:
            if actor:
                self.avatar(layer_image,actor,x,y,size,opacity,color)
            else:
                from PIL import ImageColor
                oval(d,x,y,size/2,size/2,(*ImageColor.getrgb(color),round(opacity*255)))
        softness,=self.track("clusterEarlyBlur",f)
        smear,=self.track("clusterEarlySmear",f)
        softness+=3.6*tween(f,250,253)
        composite(im,vertical_blur(blur(layer_image,softness),smear),0,0)

    def cluster(self,im,f):
        if f<=253:
            self.cluster_entrance(im,f)
            return
        wipe = self.s.get("clusterRegisteredWipe",{}).get(str(f))
        if wipe:
            base=layer()
            self.cluster_entrance(base,253)
            dx,dy,sx,sy=wipe["pose"]
            stage=base.transform((SIZE,SIZE),Image.Transform.AFFINE,
                                 (1/sx,0,500-(500+dx)/sx,0,1/sy,500-(500+dy)/sy),
                                 Image.Resampling.BICUBIC)
            smear=10+15*(f-254)
            stage=vertical_blur(stage,0,horizontal=smear)
            survivors=wipe.get("survivors")
            mask=Image.new("L",stage.size,0 if survivors else 255)
            draw=ImageDraw.Draw(mask)
            for box in survivors or wipe["masks"]:
                draw.rectangle(box,fill=255 if survivors else 0)
            stage.putalpha(ImageChops.multiply(stage.getchannel("A"),mask))
            composite(im,blur(stage,.40),0,0)
            return
        content=layer()
        d=ImageDraw.Draw(content)
        for k,x,y,r,on,col in self.s["cluster"]:
            a=tween(f,on,on+6)
            if a:
                cx=500+(x-500)*a
                cy=515+(y-515)*a+155*(1-a)
                oval(d,cx,cy,(r+27)*a,(r+27)*a,"#ece8f9")
        for k,x,y,r,on,col in self.s["cluster"]:
            a=tween(f,on,on+6)
            if a<=0:
                continue
            cx=500+(x-500)*a
            cy=515+(y-515)*a+155*(1-a)
            if k:
                self.avatar(content,k,cx,cy,2*r*a,a,col)
            else:
                oval(d,cx,cy,r*a,r*a,col)
        x,y,grow = self.track("clusterPose", f)
        if f >= self.at("profiles.mosaic"):
            stage = layer()
            composite(stage,content,500-500*grow+x,492-500*grow+y,1,grow)
            trail = f-254
            islands=self.s["clusterWipeSurvivors"].get(str(f))
            if islands:
                observed=Image.new("L",stage.size)
                mask=ImageDraw.Draw(observed)
                for rectangle in islands:
                    mask.rectangle(rectangle,fill=255)
                stage.putalpha(ImageChops.multiply(stage.getchannel("A"),observed))
            else:
                panel_wipe(stage,self.s["clusterWipe"],f)
            if 1<=trail<=3:
                stage=stage.transpose(Image.Transpose.ROTATE_90)
                stage=vertical_blur(stage,10+trail*12).transpose(Image.Transpose.ROTATE_270)
            composite(im,blur(stage,1+min(trail,3)*.7),0,0,max(0,.98-.048*trail))
        else:
            composite(im,blur(content,11*(1-tween(f,213,222))),500-500*grow+x,492-500*grow+y,1,grow)

    def profile_arrival(self,im,f):
        for j,(name,key,tag,fill,ink) in enumerate(self.s["profiles"]):
            track_name = f"profileArrival{name}"
            start = self.s["tracks"][track_name][0][0]
            if f < start:
                continue
            x,y,radius,blur_radius = self.track(track_name, f)
            portrait_layer = layer(360,320)
            self.avatar(portrait_layer,key,180,160,2*radius,neutral=False)
            sprite = blur(portrait_layer,blur_radius*.51)
            if f == 258:
                sprite=sprite.resize((680,320),Image.Resampling.BICUBIC)
                sprite=sprite.transpose(Image.Transpose.ROTATE_90)
                sprite=vertical_blur(sprite,145).transpose(Image.Transpose.ROTATE_270)
                composite(im,sprite,x-340,y-160)
                continue
            composite(im,sprite,x-180,y-160)
            label_y = mix(563, 561, tween(f,263,271))
            label_alpha = tween(f,start+1,start+7)
            labels = layer(300,155)
            d = ImageDraw.Draw(labels)
            prefix = name[:max(1,round(len(name)*label_alpha))]
            text(d,150,5,prefix,40,INK,630,"center")
            chip_w = 220*(.40+.60*label_alpha)
            d.rounded_rectangle((150-chip_w/2,58,150+chip_w/2,106),24,fill=fill)
            text(d,150,68,tag,22,ink,590,"center")
            composite(im,blur(labels,blur_radius*.23),x-150,label_y,label_alpha)

    def profiles(self,im,f):
        if f < 271:
            self.profile_arrival(im,f)
            return
        xoff,yoff,zoom=self.track("profileCamera",f)
        for j,(name,key,tag,fill,ink) in enumerate(self.s["profiles"]):
            onset=self.s["profileStartingFrames"][j]
            p=tween(f,onset,onset+4)
            opacity=p*(1-tween(f,287,300)*j*.70)
            if j==2:
                opacity*=1-tween(f,286,290)
            if opacity<=0:
                continue
            tile=layer(300,370)
            d=ImageDraw.Draw(tile)
            if j==0:
                expression,=self.track("lisaExpression",f)
                self.avatar(tile,key,150,124,204,neutral=True)
                self.avatar(tile,key,150,124,204,expression,neutral=False)
            else:
                self.avatar(tile,key,150,124,204,neutral=True)
            labels = layer(300,370)
            label_draw = ImageDraw.Draw(labels)
            text(label_draw,150,257,name,40,INK,630,"center")
            label_draw.rounded_rectangle((40,309,260,357),24,fill=fill)
            text(label_draw,150,319,tag,22,ink,590,"center")
            composite(tile,labels,0,0,tween(f,onset+3,onset+8))
            local=f-self.at("profiles.lisa-focus")
            if j==0 and f>=288:
                pulse,=self.track("lisaOutline",f)
                if pulse:
                    color=(97,233,112,round(255*pulse))
                    d.rounded_rectangle((39,308,261,358),24,outline=color,width=2)
            if j==1 and f>=287:
                veil,=self.track("ellaRevealVeil",f)
                field=np.clip(np.linspace(.45,1.8,300)*veil,0,.98)
                mask=Image.fromarray(np.tile(np.uint8((1-field)*255),(370,1)))
                tile.putalpha(ImageChops.multiply(tile.getchannel("A"),mask))
                opacity=max(opacity,.91)
            x=265+j*275
            x=500+(x-500)*zoom+xoff+126*(1-p)
            y=414+yoff-90*(1-p)
            if f>=282 and j in (0,1):
                measured_x,y,diam=self.track("lisaProfileBounds",f)
                zoom=diam/204
                x=measured_x if j==0 else self.track("ellaProfileX",f)[0]
            composite(im,blur(tile,9*(1-p)+6*max(0,1-abs(f-287)/3)+5*tween(f,308,312)),
                      x-150*zoom,y-124*zoom,opacity,zoom)

    def bubble(self,im,x,y,w,h,lines,out=False,pale=False,text_size=14.3,text_inset=None,*,
               paint=None,radius=None):
        d=ImageDraw.Draw(im)
        fill="#13c8ee" if out else "#e7e7ea"
        if pale:
            fill="#daf5fd"
        if paint is not None:
            fill=paint
        ink="#f4fdff" if out else self.palette["ink"]
        r=min(h*.5,text_size*1.35) if radius is None else radius
        d.rounded_rectangle((x,y,x+w,y+h),r,fill=fill)
        edge=x+w if out else x
        direction=1 if out else -1
        # Follow the curve from the sidewall through the root to the tail tip.
        tail=min(h*.34,22)
        bottom=y+h
        contour=[(-max(tail,r*.72),-r*1.15),(-tail*.05,-r*.83),(-tail*.02,-tail*.56),
                 (tail*.12,-tail*.31),(tail*.32,-tail*.11),(tail*.61,tail*.02),
                 (tail*.34,0),(tail*.06,-tail*.065),(-tail*.23,-tail*.23),(-max(tail,r*.80),-tail*.08)]
        d.polygon([(edge+direction*u,bottom+v) for u,v in contour],fill=fill)
        if isinstance(lines,str):
            lines=[lines]
        if not lines:
            return
        size=min(text_size,(w-18)/max(1,max(len(t) for t in lines)) * 1.92)
        font_h=size*1.22
        start=y+(h-font_h*len(lines))*.5+1.5
        inset=max(11,size*.33) if text_inset is None else text_inset
        for j,line in enumerate(lines):
            text(d,x+inset,start+j*font_h,line,size,ink,480)

    def chip(self,im,x,y,w,h,label,active=False,scale=1, opacity=1,pressed=0, *,
             glyph=pictogram, follow_style=False, send_style=False):
        if opacity<=0:
            return
        a,b=self.palette["control_a"],self.palette["control_b"]
        if follow_style:
            a, b = "#d9f0ff", "#efd1f7"
        elif send_style:
            a, b = "#f0c9fa", "#d3effd"
        elif pressed:
            a="#e8ecf4"
            b="#f2e3f5"
        asset=rounded_gradient(w,h,a if active else self.palette["negative"],
                              b if active else "#d2d3db",round(h*.25),"x")
        d=ImageDraw.Draw(asset)
        if follow_style:
            tone = round(mix(28,90, .79 + .21*pressed)) if active else 31
            text(d,w/2,round(h*.26),label,h*.65,(tone,tone,tone),405,"center",glyph=glyph)
        else:
            text(d,w/2,round(h*.18),label,h*.60,INK,510,"center",glyph=glyph)
        composite(im,asset,x+(w*(1-scale))/2,y+h*(1-scale)/2,opacity,scale)

    def keyboard(self,im,y):
        d=ImageDraw.Draw(im)
        tray="#d7d8de"
        key="#fdfdfd"
        utility="#c8cdd2"
        d.rectangle((10,y,389,817),fill=tray)
        for row,start,letters in ((0,17,"QWERTYUIOP"),(1,35.5,"ASDFGHJKL"),(2,72.5,"ZXCVBNM")):
            top=y+9+row*51.3
            for column,label in enumerate(letters):
                x=start+column*37.1
                d.rounded_rectangle((x,top+2,x+32,top+43),5.5,fill="#babdc1")
                d.rounded_rectangle((x,top,x+32,top+40),5.5,fill=key)
                text(d,x+16,top+12,label,20,"#202020",500,"center")
        top=y+112
        for x0,x1,label,color in ((17,59,"shift",key),(338,382,"delete",utility)):
            d.rounded_rectangle((x0,top+2,x1,top+43),5.5,fill="#babdc1")
            d.rounded_rectangle((x0,top,x1,top+40),5.5,fill=color)
            keyboard_glyph(d,label,(x0+x1)/2,top+20)
        top=y+162
        for a,b,n,col in [(17,106,"123",utility),(110,292,"space",key),(297,382,"Label",utility)]:
            d.rounded_rectangle((a,top+2,b,top+42),5,fill="#babdc1")
            d.rounded_rectangle((a,top,b,top+40),5,fill=col)
            text(d,(a+b)/2,top+12,n,15,INK,500,"center")
        icon_y=clamp(y+247,749,780)
        keyboard_glyph(d,"emoji",53,icon_y)
        microphone(d,348,icon_y,23,"#667076")
        d.rounded_rectangle((134,802,266,808),3,fill="#202020")

    def composer(self,im,y,*,settled=False):
        d=ImageDraw.Draw(im)
        oval(d,44,y+15,15,15,"#eeedf2")
        d.line((37,y+15,51,y+15),fill="#95969b",width=2)
        d.line((44,y+8,44,y+22),fill="#95969b",width=2)
        if settled:
            d.rounded_rectangle((70,y-1,373,y+33),17,outline="#bebebe",width=1)
            text(d,82,y+8,self.c["keyboardPrompt"],14.5,"#b9b9b9")
            x, cy = 353, y+15
            ink = "#aeb4b6"
            d.rounded_rectangle((x-2,cy-8,x+2,cy+2),2,fill=ink)
            d.arc((x-5,cy-6,x+5,cy+5),0,180,fill=ink,width=1)
            d.line((x,cy+5,x,cy+8),fill=ink,width=1)
            d.line((x-3,cy+8,x+3,cy+8),fill=ink,width=1)
        else:
            d.rounded_rectangle((70,y-1,373,y+32),17,outline="#d5d3dd",width=1)
            text(d,82,y+7,self.c["keyboardPrompt"],15,"#a6a2af")
            microphone(d,353,y+15,16,"#8b9297")

    def thread_plate(self, which, f, keyboard_y, *, history_offset=0, heading_height=None,
                     measured=False):
        im=layer(400,827)
        phone_shell(im,400,827,65)
        # Header is inset within the shell, with an original tinted utility bar.
        d=ImageDraw.Draw(im)
        header_bottom=137 if which=="sofia" else 147
        if heading_height is not None:
            header_bottom=heading_height
        d.rounded_rectangle((10,9,389,header_bottom),56,fill="#f0f0f3")
        d.rectangle((10,94,389,header_bottom),fill="#f0f0f3")
        d.line((10,header_bottom,389,header_bottom),fill="#dfdfe1",width=1)
        status(d,400,41,self.c["chatStatus"],True)
        d.line((43,82,33,92,43,102),fill="#498af3",width=3)
        d.rounded_rectangle((342,84,358,100),3,outline="#498af3",width=2)
        d.polygon([(359,92),(367,85),(367,99)],outline="#498af3")
        if which=="sofia":
            c=self.c["sofia"]
            push=tween(f,331,341)
            self.avatar(im,"danielle",200,94,46)
            text(d,200,120,c[0]+"  ›",11,INK,500,"center")
            if not measured:
                self.bubble(im,141,178+13*push+history_offset,217,34,c[1],True,paint="#14c5fa")
                settle = self.s["tracks"].get("sofiaHistorySettle")
                if settle and settle[0][0] <= f <= settle[-1][0]:
                    left_shift, lift, today_lift, fade = interpolate(settle, f)
                    for top, width, height, copy, ink_width in (
                        (239+12*push, 178, 33, c[2], 148),
                        (276+13*push, 270, 34, c[3], 239),
                    ):
                        left = 43+left_shift
                        top += history_offset+lift
                        use_fitted_ink = isinstance(copy,str)
                        self.bubble(im,left,top,width-left_shift,height,
                                    [] if use_fitted_ink else copy,paint="#e8e8eb")
                        if use_fitted_ink:
                            fit_ink(im,copy,(left+12.5,top+10.8,ink_width,10.25),410,
                                    .95, .12, family=messages_font,ink=(32,32,34))
                    fit_ink(im,self.c["today"],(185,329+18*push+history_offset+today_lift,30,9),
                            410,fade,.12,family=messages_font,ink=(127,127,127))
                else:
                    self.bubble(im,43,239+12*push+history_offset,178,33,c[2])
                    self.bubble(im,43,276+13*push+history_offset,270,34,c[3])
                    text(d,200,329+18*push+history_offset,self.c["today"],13,MUTED,475,"center")
        else:
            c=self.c["follow"]
            stamp(im,badge(85),200,100,38)
            text(d,200,126,c[0]+"  ›",11,INK,560,"center")
            if not measured:
                upper_shift,=self.track("followMessageLift",f)
                lower_shift,=self.track("followLowerLift",f)
                middle_shift=(upper_shift+lower_shift)/2
                self.bubble(im,140,173+upper_shift,222,48,c[1],True,True)
                self.bubble(im,42,232+middle_shift,260,48,c[2])
                text(d,200,307+middle_shift,self.c["today"],13,MUTED,500,"center")
                self.bubble(im,47,356+lower_shift,276,67,c[3])
        if not measured:
            self.composer(im,keyboard_y-41,settled=which=="sofia" and 340<=f<=355)
            self.keyboard(im,keyboard_y)
        # The white screen and keyboard share the same curved bottom mask.
        mask=Image.new("L",im.size)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,399,826),65,fill=255)
        im.putalpha(mask)
        im.alpha_composite(rim_only(400,827,65))
        return im

    def staged_thread(self, im, which, registration, frame):
        """Paint bodies and keyboard on the measured screen plane."""
        surface = layer()
        copy = self.c[which]
        follow = which=="follow"
        if registration["blue"]:
            x0,y0,x1,y1 = registration["blue"]
            h = y1-y0
            upper = layer()
            measured_color = registration.get("bluePaint")
            paint = tuple(measured_color) if measured_color else ("#ccf3fc" if follow else "#14c5fa")
            self.bubble(upper,x0,y0,x1-x0-5,h,[],True,follow,text_size=h*.35,paint=paint)
            words=copy[1] if isinstance(copy[1],list) else [copy[1]]
            for i,line in enumerate(words):
                bx = x0+18 if follow else x0+h*.43
                by = y0+h*(.20+.37*i) if follow else y0+h*.33
                width=min(x1-bx-15,len(line)*h*(.250 if follow else .193))
                ink_box = registration.get("blueInk") if len(words)==1 else None
                fit_ink(upper,line,ink_box or (bx,by,width,h*(.24 if follow else .32)),
                        420,.86,.6,family=messages_font,ink=(254,254,254))
            if follow:
                # The incoming light rolls off the pale outgoing message vertically.
                alpha=np.asarray(upper.getchannel("A"),dtype=float)
                lighting=np.interp(np.arange(SIZE),(y0,y0+h*.40,y1),(.08,.29,.89))
                upper.putalpha(Image.fromarray(np.uint8(np.rint(alpha*lighting[:,None]))))
            composite(surface,upper,0,0)
        for i,(bounds,lines) in enumerate(registration["items"]):
            left,top,right,bottom = bounds
            height = bottom-top
            tail = height*.13
            background = "#eeeef0" if follow and i==0 else "#e8e8eb"
            words=copy[i+2]
            if isinstance(words,str):
                words=[words]
            fit=len(words)==len(lines)
            self.bubble(surface,left+tail,top,right-left-tail-1,height-1,[] if fit else words,
                        text_size=height*.43,paint=background,
                        radius=registration["corners"][i])
            for word,ink in zip(words,lines) if fit else ():
                color = (113,113,115) if follow and i==0 else (34,34,35)
                weight = 440 if follow and i else 410
                fit_ink(surface,word,ink,weight,1,.25,family=messages_font,ink=color)
        if registration["today"]:
            fit_ink(surface,self.c["today"],registration["today"],400,1,.2,
                    family=messages_font,ink=(126,126,126))

        l,r = registration["rails"]
        top,tray,rows = registration["keys"]
        for index,(start,end,values) in enumerate(registration["edgeRamps"]):
            columns=np.arange(start,end+1)
            luma=np.interp(columns,np.linspace(start,end,len(values)),values)
            inside=(columns>=l-1) if index==0 else (columns<=r+1)
            screen=np.clip((luma-138)/115,0,1)*inside
            rgb=np.broadcast_to(luma[None,:,None],(SIZE,end-start+1,3)).copy()
            rgb[top:]-=screen[None,:,None]*(253-np.asarray(tray))
            upper_limit = registration.get("railStart",0)
            rail = Image.fromarray(np.uint8(np.clip(np.rint(rgb[upper_limit:]),0,255)))
            im.paste(rail,(start,upper_limit))
        zoom=(r-l)/376
        d=ImageDraw.Draw(surface)
        d.rectangle((l,top,r-1,SIZE),fill=tuple(tray))
        composer_y=top-41*zoom
        prompt=layer(400,45)
        self.composer(prompt,3,settled=True)
        composite(surface,prompt,l-10*zoom,composer_y-3*zoom,1,zoom)
        d=ImageDraw.Draw(surface)
        for (x,y,pitch,w,h,_), letters in zip(rows,("QWERTYUIOP","ASDFGHJKL","ZXCVBNM")):
            for j,letter in enumerate(letters):
                key_x = x+j*pitch
                d.rounded_rectangle((key_x,y+1,key_x+w,y+h+2),w*.114,fill="#b9bcc3")
                d.rounded_rectangle((key_x,y,key_x+w,y+h-1),w*.112,fill="#fdfdfd")
                d.text((key_x+w/2,y+h*.29),letter,font=messages_font(h*.57,420),
                       fill="#1f1f1f",anchor="mt")
            if letters=="ZXCVBNM":
                for key_x,key_w,name,tone in ((l+4,1.20*w,"shift","#fafafa"),
                                               (r-1.22*w-6,1.22*w,"delete","#c4cbd1")):
                    d.rounded_rectangle((key_x,y,key_x+key_w,y+h-1),w*.105,fill=tone)
                    glyph=layer(36,36)
                    keyboard_glyph(ImageDraw.Draw(glyph),name,18,18)
                    composite(surface,glyph,key_x+key_w/2-18*zoom,y+h/2-18*zoom,1,zoom)
        bottom=top+161*zoom
        if bottom<SIZE:
            for start,end,caption,background in ((17,106,"123","#c8cdd2"),
                                                  (110,292,"space","#fdfdfd"),
                                                  (297,382,"Label","#c8cdd2")):
                x1,x2 = l+(start-10)*zoom,l+(end-10)*zoom
                d.rounded_rectangle((x1,bottom,x2,bottom+40*zoom),5.2*zoom,fill=background)
                d.text(((x1+x2)/2,bottom+12*zoom),caption,font=messages_font(15*zoom,425),
                       fill=INK,anchor="mt")
        if follow:
            softness=.78+1.7*tween(frame,688,694)+max(0, (672-frame)*.48)
        else:
            softness=1.14+.29*min(1,abs(frame-348)/5)
            if frame>=352:
                softness = 1.25+1.1*(frame-352)
        if "focus" in registration:
            sweep_x,sweep_y,softness=registration["focus"]
            surface=vertical_blur(surface,sweep_y,horizontal=sweep_x)
        composite(im,blur(surface,(softness*.85,softness)),0,0)

    def expose_phone(self, im, plate, x, y, scale, smear, radius, alpha=1, *,
                     vertical_scale=1):
        if vertical_scale != 1:
            plate = plate.resize((plate.width,round(plate.height*vertical_scale)),
                                 Image.Resampling.BICUBIC)
        if smear > 1:
            pad = math.ceil(smear/2)+4
            padded = layer(plate.width, plate.height+2*pad)
            padded.alpha_composite(plate,(0,pad))
            plate = vertical_blur(padded,smear)
            y -= pad*scale
        composite(im,blur(plate,radius),x,y,alpha,scale)

    def sofia(self,im,f):
        x,y,s=self.track("sofiaMeasuredCamera",f)
        keyboard_y,=self.track("sofiaKeyboardY",f)
        a, rail = self.track("sofiaRelease",f)
        onset=self.at("sofia.suggestion")
        registration = self.s["tracks"].get("sofiaPlateRegistration")
        history, heading, sweep_x, sweep_y = 0, None, 0, 0
        if registration and registration[0][0]<=f<=registration[-1][0]:
            history, heading, sweep_x, sweep_y=interpolate(registration,f)
        measured = self.s.get("threadRegistration",{}).get("sofia",{}).get(str(f))
        if a>0:
            plate=self.thread_plate("sofia",f,keyboard_y,history_offset=history,
                                    heading_height=heading,measured=bool(measured))
            entrance=5.5*(1-tween(f,313,318))+.45
            push=2.3*max(0,1-abs(f-337)/5)+3*max(0,1-abs(f-354)/4)
            trail, = self.track("sofiaExposure",f)
            if sweep_x or sweep_y:
                plate=vertical_blur(plate,sweep_y,horizontal=sweep_x)
                push *= .4
            if f>=352:
                inside = Image.new("L",plate.size)
                ImageDraw.Draw(inside).rounded_rectangle((14,14,385,812),52,fill=255)
                if f>=356:
                    upper = 1-tween(f,355,357)
                    fade = np.interp(np.arange(plate.height),[0,495,563,827],[upper,upper,1,1])
                    inside = Image.fromarray(np.uint8(np.asarray(inside)*fade[:,None]))
                plate.putalpha(inside)
            bezels = self.s["tracks"].get("sofiaBezelControls")
            if bezels and bezels[0][0] <= f <= bezels[-1][0]:
                width, coverage, lo1, hi1, lo2, hi2, lo3, hi3, lo4, hi4 = interpolate(bezels,f)
                switches = layer()
                d = ImageDraw.Draw(switches)
                for lo,hi in ((lo1,hi1),(lo2,hi2),(lo3,hi3)):
                    d.rounded_rectangle((x-width,lo,x+4,hi),2.4,fill=(52,52,52,247))
                    d.line((x-width+1.4,lo+4,x-width+1.4,hi-4),fill=(122,122,122,243),width=2)
                right = x+400*s
                d.rounded_rectangle((right-4,lo4,right+width,hi4),2.8,fill=(49,49,49,251))
                d.line((right+width-1.2,lo4+4,right+width-1.2,hi4-4),fill=(111,111,111,245),width=2)
                composite(im,blur(switches,.75+push),0,0,coverage)
                push *= 1-.44*tween(f,351,354)
            self.expose_phone(im,plate,x,y,s,trail*(1-.30*tween(f,315,319)),entrance+push,a)
            if f>=352 and rail:
                self.expose_phone(im,rim_only(400,827,65),x,y,s,0,.72,rail)
            if measured:
                self.staged_thread(im,"sofia",measured,f)
        if f<onset:
            reply=layer(410,545)
            self.bubble(reply,227,366,132,32,self.c["sofia"][4],True,paint="#13c4fa")
            trail = 85*(1-tween(f,313,319))
            composite(im,vertical_blur(blur(reply,2.0*max(0,1-abs(f-337)/6)),trail),x,y,1,s)
        elif f>=360:
            detached = layer()
            c = self.c["sofia"]
            rbox=self.track("sendReplyBox",f)
            sbox=self.track("sendSuggestionBox",f)
            left,top,right,bottom=sbox
            text(ImageDraw.Draw(detached),left+12,top-28,c[5],27,MUTED,520)
            lettering=self.s["tracks"].get("sendDepartureInk")
            specs=interpolate(lettering,f) if lettering else None
            for i,(bounds,content,paint,size) in enumerate((
                (rbox,c[4],"#13c4fa",54),(sbox,c[6],"#0fc4f9",46),
            )):
                x0,y0,x1,y1=bounds
                w,h=x1-x0,y1-y0
                lines=content if isinstance(content,list) else [content]
                fit=specs and len(lines)==i+1
                self.bubble(detached,x0,y0,w-8,h,[] if fit else content,True,
                            text_size=size,paint=paint)
                if fit:
                    for j,line in enumerate(lines):
                        k=(0 if i==0 else 1+j)*4
                        dx,dy,width,height=specs[k:k+4]
                        fit_ink(detached,line,(x0+dx*w,y0+dy*h,width*w,height*h),
                                400,1,.33,family=messages_font,ink=(245,253,254))
            chip_track = self.s["tracks"].get("sendHandoffControls")
            if chip_track and chip_track[0][0]<=f<=chip_track[-1][0]:
                boxes = interpolate(chip_track,f)
                palettes = (("#c9c9c9","#c9c9c9"),("#ecaafa","#afe2fc"))
                for index,(label,gradient) in enumerate(zip(c[7:9],palettes,strict=True)):
                    x0,y0,w,h = boxes[index*4:index*4+4]
                    face = rounded_gradient(round(w),round(h),*gradient,round(h*.23),"x")
                    ink_width=w*(.54 if index==0 else .75)
                    fit_ink(face,label,((w-ink_width)/2,h*.29,ink_width,h*.41),
                            480,1,.4,family=messages_font,ink=(34,34,34))
                    composite(detached,face,x0,y0)
            else:
                self.chip(detached, right-318, bottom+5, 123, 64, c[7])
                self.chip(detached, right-177, bottom+5, 160, 66, c[8], True,send_style=True)
            envelope = (self.track("sendOutgoingOpacity",f)[0]
                        if f>=399 and "sendOutgoingOpacity" in self.s["tracks"] else 1)
            exit_exposure=self.s["tracks"].get("sendExitExposure")
            if exit_exposure and exit_exposure[0][0]<=f<=exit_exposure[-1][0]:
                sx,sy=interpolate(exit_exposure,f)
                detached=detached.convert("RGBa").filter(
                    ImageFilter.GaussianBlur((sx,sy))).convert("RGBA")
            else:
                detached=blur(detached,4*tween(f,396,403))
            composite(im,detached,0,0,envelope)
        if onset<=f<360:
            c=self.c["sofia"]
            incoming=layer()
            settle = self.s["tracks"].get("sofiaSuggestionInk")
            two_lines = isinstance(c[6], list) and len(c[6]) == 2
            settled = (settle and settle[0][0] <= f <= settle[-1][0]
                       and isinstance(c[4], str) and two_lines)
            left,top,width,height=self.track("sofiaEarlierReplyBounds",f)
            self.bubble(incoming,left,top,width-6,height,[] if settled else c[4],True,
                        text_size=height*.53,paint="#13c4fa")
            left,top,width,height=self.track("sofiaSuggestedBounds",f)
            self.bubble(incoming,left,top,width-6,height,[] if settled else c[6],True,
                        text_size=height*.315,text_inset=height*.30,paint="#0fc4f9")
            if settled:
                ink_boxes = interpolate(settle, f)
                captions = [c[4], *c[6], c[5]]
                for index, caption in enumerate(captions):
                    fit_ink(incoming,caption,ink_boxes[index*4:index*4+4],400,
                            blur_radius=.48,family=messages_font,
                            ink=(145,145,145) if index==3 else (244,253,255))
            else:
                label=height*.20
                label_opacity=tween(f,336,341)
                text(ImageDraw.Draw(incoming),left+15,top-label*.99,c[5],label,
                     (103,102,106,round(255*label_opacity)),520)
            launch=1-tween(f,336,340)
            detach=max(0,1-abs(f-355)/3)
            if f>=self.at("sofia.no"):
                controls = self.s["tracks"].get("sofiaSettledControls")
                if controls and controls[0][0] <= f <= controls[-1][0]:
                    boxes = interpolate(controls, f)
                    for index, label in enumerate(c[7:9]):
                        if index==1 and f<self.at("sofia.send-control"):
                            continue
                        bx,by,bw,bh = boxes[index*4:index*4+4]
                        paint = ("#e6b4fb","#afdff9") if index else ("#c9c9c9","#c9c9c9")
                        face = rounded_gradient(round(bw),round(bh),*paint,round(bh*.26),"x")
                        label_width=bw*(.70 if index else .45)
                        fit_ink(face,label,((bw-label_width)/2,bh*.26,label_width,bh*.48),410,
                                blur_radius=.4,family=messages_font,ink=(31,31,31))
                        composite(incoming,face,bx,by)
                else:
                    right,cap_y,cap_h=self.track("sofiaSendMeasurement",f)
                    no_width=round(1.88*cap_h)
                    send_width=round(2.58*cap_h)
                    no_alpha=mix(.65,1,tween(f,341,347))
                    self.chip(incoming,right-send_width-no_width-15,cap_y+3,no_width,
                              round(cap_h*.95),c[7],False,opacity=no_alpha)
                    if f>=self.at("sofia.send-control"):
                        self.chip(incoming,right-send_width,cap_y,send_width,round(cap_h),c[8],True,send_style=True)
            if sweep_x or sweep_y:
                incoming=vertical_blur(incoming,sweep_y*s*.69,horizontal=sweep_x*s*.69)
            composite(im,blur(incoming,1.5*launch+3.5*detach),0,0,.92+.08*(1-launch))
        if f>=381:
            tip = self.s["tracks"].get("sendPointerStage")
            if tip and tip[0][0]<=f<=tip[-1][0]:
                x,y,w,h,soft_x,soft_y,alpha,lean=interpolate(tip,f)
                follow_pointer(im,x,y,w,h,soft_x,alpha,lean=lean,vertical_softness=soft_y)
            else:
                x,y,r=self.track("sendCursor",f)
                cursor(im,x,y,r,1-tween(f,397,403),1.53)

    def calendar(self,im,f):
        cal=layer()
        d=ImageDraw.Draw(cal)
        left,y0,h=self.track("calendarCamera",f)
        right, = self.track("calendarRight", f)
        day_x, day_y = self.track("calendarDay", f)
        date_keys=self.s["tracks"].get("calendarDateExposure")
        date=None
        if date_keys and date_keys[0][0]<=f<=date_keys[-1][0]:
            date=interpolate(date_keys,f)
            day_x,day_y=date[:2]
        step = (right-left)/6.3
        first = day_x-5*step
        heading=layer() if date else cal
        title=ImageDraw.Draw(heading)
        day_top=day_y-h*.16 if date else y0-h*.74
        week_top=day_y-h*.72 if date else y0-h*1.30
        for j,(dow,num) in enumerate(zip("SMTWTFS",[16,17,18,19,20,21,23])):
            x=first+j*step
            dark=INK if 0<j<6 else "#9894a5"
            if num==21 and date is None:
                oval(title,day_x,day_y,h*.335,h*.335,"#ef3046")
                dark="#fff"
            text(title,x,week_top,dow,h*.17,INK,635,"center")
            if num!=21 or date is None:
                text(title,x,(day_y-h*.15) if num==21 else day_top,str(num),h*.33,dark,555,"center")
        grid = self.s["tracks"].get("calendarGridRegistration")
        if grid and grid[0][0]<=f<=grid[-1][0]:
            grid_y,grid_step,ink_tone = interpolate(grid,f)
            tick_ink = tuple(round(ink_tone+v) for v in (0,-2,4))
        else:
            grid_y,grid_step,tick_ink = y0,h,"#8a8796"
        tick_controls = self.s.get("calendarHandoff",{}).get(str(f))
        ticks = layer() if tick_controls else cal
        tick_draw = ImageDraw.Draw(ticks)
        if tick_controls:
            tick_right, tick_shift, tick_focus, tick_trail, strength, bar_left, bar_right, bar_shift = tick_controls
        else:
            tick_right, tick_shift = left-8, 0
            bar_left, bar_right, bar_shift = left, right, 0
        for j in range(8):
            y=grid_y+grid_step*j
            d.line((left,y,right,y),fill="#d5d2dc",width=2)
            text(tick_draw,tick_right,y-8+tick_shift,f"{j or 12}AM",h*.195,tick_ink,535,"right")
        calendar_exposure=self.s["tracks"].get("calendarAppointmentExposure")
        exposure=None
        if calendar_exposure and calendar_exposure[0][0]<=f<=calendar_exposure[-1][0]:
            exposure=interpolate(calendar_exposure,f)
        appointments=(
            ("calendarLisa",self.c["calendar"][0],1.50,"#35b8e0","#8bd9f5","#246d87"),
            ("calendarMarie",self.c["calendar"][1],1.01,"#9a37df","#b68af1","#6826a3")
        )
        calendar_labels=layer() if exposure else cal
        calendar_blocks=layer() if exposure else cal
        shutter = self.s.get("calendarBarShutter",{}).get(str(f))
        a, = self.track("calendarArrivalOpacity",f)
        typed=ImageDraw.Draw(calendar_labels)
        for index,(track,name,dur,edge,fill,ink) in enumerate(appointments):
            top=y0+h*self.track(track,f)[0]
            bottom=top+h*dur
            opacity=92
            if exposure:
                top,height,opacity=exposure[index*3:index*3+3]
                top += bar_shift
                bottom=top+height
                if index==0:
                    fill="#8bd9fc"
            from PIL import ImageColor
            if shutter:
                pose = shutter[index*7:index*7+7]
                lx,rx = 194,874
                bar,start_x,start_y = exposed_appointment(lx,rx,pose,opacity*a,ImageColor.getrgb(edge))
                composite(calendar_blocks,bar,start_x,start_y)
                top = pose[0]
            else:
                lx=bar_left
                bar=layer(round(bar_right-bar_left),max(1,round(bottom-top)))
                bd=ImageDraw.Draw(bar)
                rgb=ImageColor.getrgb(fill)
                bd.rounded_rectangle((0,0,bar.width-1,bar.height-1),8,fill=(*rgb,round(opacity)))
                bd.rounded_rectangle((0,0,5,bar.height-1),3,fill=edge)
                composite(calendar_blocks,bar,bar_left,top)
            text(typed,lx+13,top+(h*.32 if track=="calendarMarie" else h*.10),name,h*.234,ink,620,
                 glyph=lambda *args: self.source_glyph(f, *args))
        fitted=self.s["tracks"]["calendarMeasuredCursor"]
        if fitted[0][0]<=f<=fitted[-1][0]:
            x,y,r,size=interpolate(fitted,f)
        else:
            x,y,r=self.track("calendarCursor",f)
            size=.98
        eye=tween(f,398,402)
        entry_cursor=self.s["tracks"].get("calendarCursorVisibility")
        if entry_cursor and entry_cursor[0][0]<=f<=entry_cursor[-1][0]:
            eye,=interpolate(entry_cursor,f)
        measured_entry = self.s["tracks"].get("calendarEntryPointer")
        separate_pointer = measured_entry and measured_entry[0][0]<=f<=measured_entry[-1][0]
        if not separate_pointer:
            cursor(cal,x,y,r,eye,size)
        if f>=self.at("calendar.mosaic"):
            panel_wipe(cal,self.s["calendarWipe"],f)
        smear, = self.track("calendarArrivalSmear",f)
        if smear:
            # The long trail sits around a shorter core exposure during entry.
            short = vertical_blur(cal,smear*.49).convert("RGBa")
            trail = vertical_blur(cal,smear).convert("RGBa")
            cal = Image.blend(short,trail,.42).convert("RGBA")
        mosaic=tween(f,476,479)
        composite(im,blur(cal,4.5*(1-tween(f,398,410))+4*mosaic),
                  0,0,a*(1-.95*mosaic)*(1-tween(f,479,482)))
        if tick_controls:
            ticks = vertical_blur(ticks,tick_trail).convert("RGBa")
            ticks = ticks.filter(ImageFilter.GaussianBlur((tick_focus,1.4))).convert("RGBA")
            composite(im,ticks,0,0,strength)
        if exposure:
            label_blur=exposure[-1]
            if shutter:
                composite(im,calendar_blocks,0,0)
            else:
                blocks=calendar_blocks.convert("RGBa").filter(
                    ImageFilter.GaussianBlur((max(.55,label_blur*.10),label_blur))).convert("RGBA")
                composite(im,blocks,0,0,a)
            calendar_labels=vertical_blur(calendar_labels,label_blur*2.25)
            composite(im,blur(calendar_labels, max(.3, label_blur*.13)),0,0,a)
        if separate_pointer:
            tip_x,tip_y,angle,scale,opacity,spread_x,spread_y = interpolate(measured_entry,f)
            cursor(im,tip_x,tip_y,angle,opacity,scale,softness=(spread_x,spread_y))
        if date:
            cx,cy,rx,ry,opacity,soft_x,soft_y,_=date
            stamp_size=182
            mark=layer(stamp_size,stamp_size)
            mid=stamp_size/2
            oval(ImageDraw.Draw(mark),mid,mid,rx,ry,"#ed2f38")
            heading=heading.convert("RGBa").filter(
                ImageFilter.GaussianBlur((soft_x*.59,soft_y*.86))).convert("RGBA")
            composite(im,heading,0,0,date[-1]*a)
            mark=mark.convert("RGBa").filter(
                ImageFilter.GaussianBlur((soft_x,soft_y))).convert("RGBA")
            composite(im,mark,cx-mid,cy-mid,opacity)
            ink=layer(stamp_size,stamp_size)
            text(ImageDraw.Draw(ink),mid,mid-h*.15,"21",h*.33,"#fff",555,"center")
            ink=ink.convert("RGBa").filter(
                ImageFilter.GaussianBlur((soft_x*.7,soft_y*.67))).convert("RGBA")
            composite(im,ink,cx-mid,cy-mid,opacity*date[-1])

    def apps(self,im,f):
        phase,=self.track("orbitPhase",f)
        fade=1-tween(f,619,623)
        nodes=[]
        entrances={"rings":478,"red":479,"blue":479,"dark":481}
        lead = ("rings" if f<=478 else "red" if f<=533 else "dark" if f<=555
                else "rings" if f<=575 else "blue")
        for name,k in (("red",0),("dark",.25),("rings",.50),("blue",.75)):
            onset=entrances[name]
            if f<onset:
                continue
            depth=math.cos((k-phase)*math.tau)
            path=f"{name}Orbit" if name in ("red","blue") else f"{name}MeasuredOrbit"
            x,y,size=self.track(path,f)
            alpha=mix(.68,1,tween(f,onset,onset+2))*fade
            nodes.append((name==lead,depth,name,x,y,size,alpha))
        for _,depth,name,x,y,size,alpha in sorted(nodes):
            ox=app_icon(name)
            softness=1.7+(1-depth)*2.9+4*(1-tween(f,478,486))
            vertical = 84*tween(f,616,621)
            if name == "blue":
                dy, coverage, blend, smear, height_ratio = self.track("calendarTileTreatment", f)
                y += dy
                alpha *= coverage
                if blend:
                    finish = self.s["tracks"].get("calendarTileFinish")
                    strength = interpolate(finish,f)[0] if finish else 0
                    face = calendar_face(round(strength,3))
                    face_height = round(ox.height * height_ratio)
                    face = face.resize((face.width, face_height), Image.Resampling.BICUBIC)
                    height_gain = face.height - ox.height
                    previous = layer(face.width, face.height)
                    previous.alpha_composite(ox, (0, height_gain))
                    ox = Image.blend(previous.convert("RGBa"), face.convert("RGBa"), blend).convert("RGBA")
                    y -= height_gain * size / ox.width
                vertical *= smear
                shutter = self.s["tracks"].get("calendarTileShutter")
                if shutter and shutter[0][0] <= f <= shutter[-1][0]:
                    advance, = interpolate(shutter,f)
                    vertical=max(vertical,advance)
            if name=="rings" and f==478:
                trim=rounded_gradient(256,256,"#eb86c9","#ffdbec",42,"x")
                composite(trim,ox,9,9,1,.93)
                ox=trim
            # Let the softened silhouette extend beyond the asset's square.
            pad=math.ceil(softness*3)
            pad_y=pad+math.ceil(vertical/2)
            exposed=layer(ox.width+2*pad,ox.height+2*pad_y)
            exposed.alpha_composite(ox,(pad,pad_y))
            exposed=vertical_blur(blur(exposed,softness),vertical)
            frame_scale=size/ox.width
            composite(im,exposed,x-(128+pad)*frame_scale,y-(128+pad_y)*frame_scale,alpha,frame_scale)

    def follow(self,im,f):
        x,y,s=self.track("followMeasuredCamera",f)
        contact=self.s["followContact"]
        if f<=659:
            keyboard_y,=self.track("followKeyboardY",f)
        else:
            keyboard_shift,=self.track("followKeyboardOffset",f)
            keyboard_y=543+keyboard_shift
        registration = self.s["tracks"].get("followBodyRegistration")
        aspect = 1
        registered = registration and registration[0][0]<=f<registration[-1][0]
        if registered:
            x,y,s,aspect,keyboard_y = interpolate(registration,f)
        measured = self.s.get("threadRegistration",{}).get("follow",{}).get(str(f))
        plate=self.thread_plate("follow",f,keyboard_y,measured=bool(measured))
        no_frame=self.at("follow.no")
        yes_frame=self.at("follow.yes")
        a=mix(.79,1,tween(f,no_frame,653)) if f>=no_frame else 0
        b=mix(.72,1,tween(f,yes_frame,654)) if f>=yes_frame else 0
        tapped=tween(f,self.at("follow.yes-feedback")-1,690)
        chip_shift,=self.track("followChipOffset",f)
        def face(draw, name, x, y, size):
            x_shift = 2.4 if name == "tongue" else 0
            self.source_glyph(f, draw, name, x+x_shift, y-2.6, size*.97)
        no_x,no_y,no_w,no_h = 45,433+chip_shift,72,29
        if measured and measured["no"]:
            lx,ty,rx,by=measured["no"]
            no_x,no_y=(lx-x)/s,(ty-y)/s
            no_w,no_h=min(75,round((rx-lx)/s)),round((by-ty)/s)
        self.chip(plate,no_x,no_y,no_w,no_h,self.c["follow"][4],False,.58+.42*a,a,
                  glyph=face,follow_style=True)
        left,top,width,height=contact["yesRect"]
        top+=chip_shift
        shift, height_scale = self.track("followYesRegistration", f)
        dx, dy, dw, dh = self.track("followYesInkBounds", f)
        left += dx
        top += shift + dy
        width = max(1, round(width + dw))
        height = max(1, round(height * height_scale + dh))
        self.chip(plate,left,top,width,height,self.c["follow"][5],True,.58+.42*b,b,tapped,
                  glyph=face,follow_style=True)
        trail, = self.track("followExposure",f)
        softness=.38+4.6*(1-tween(f,624,630))+2.2*max(0,1-abs(f-665)/7)+3*tween(f,690,696)
        left_light, right_light, taper, extra_defocus = self.track("handsetRailLight", f)
        exposure_x = x
        aperture=self.s["tracks"].get("followRailAperture")
        if aperture and aperture[0][0]<=f<=aperture[-1][0]:
            plate=follow_aperture(plate,*interpolate(aperture,f),keyboard_y)
        elif left_light or right_light:
            plate, gutter = lit_phone(plate,left_light,right_light,taper,
                                      exit_defocus=extra_defocus>0, registered=registered)
            exposure_x -= gutter * s
        softness += extra_defocus
        self.expose_phone(im,plate,exposure_x,y,s,trail*(1-.32*tween(f,625,630)),
                          softness,vertical_scale=aspect)
        if measured:
            self.staged_thread(im,"follow",measured,f)
            if tapped:
                center_x=x+(left+width*.77)*s
                center_y=y+(top+height*.50)*s
                fx,fy=max(0,round(center_x-80)),max(0,round(center_y-75))
                yf,xf=np.mgrid[fy:fy+151,fx:fx+161]
                alpha=np.exp(-((xf-center_x)/48)**2-((yf-center_y)/47)**2)*tapped
                light=Image.new("RGBA",(161,151),(250,233,255))
                light.putalpha(Image.fromarray(np.uint8(np.rint(alpha*63))))
                composite(im,light,fx,fy)

        # The measured cursor departs on its own track as the handset withdraws.
        optics = self.s.get("followPointerOptics",{}).get(str(f))
        if optics:
            x,y,w,h,soft_x,soft_y,opacity,lean = optics
            follow_pointer(im,x,y,w,h,soft_x,opacity,lean=lean,
                           vertical_softness=soft_y,rounded=True)
            return
        tip_track = self.s["tracks"]["followPointerStage"]
        if tip_track[0][0] <= f <= tip_track[-1][0]:
            lean, = self.track("followPointerLean", f)
            follow_pointer(im, *interpolate(tip_track, f), lean=lean)
            return
        if "followLeadIn" in self.s["tracks"]:
            lead = self.s["tracks"]["followLeadIn"]
            if lead[0][0] <= f <= lead[-1][0]:
                cx,cy,angle,size,soft_x,soft_y,alpha=interpolate(lead,f)
                cursor(im,cx,cy,angle,alpha,size,(soft_x,soft_y))
            return

        # Earlier approach retains its local control until the measured track begins.
        cx,cy,r=self.track("followCursor",f)
        pointer=self.s["tracks"]["isolatedFollowPointer"]
        if pointer and pointer[0][0]<=f<=pointer[-1][0]:
            cx,cy=interpolate(pointer,f)
        local=f-self.at("follow.yes-contact")
        measured=local+contact["measuredContactFrame"]
        approach=self.s["tracks"]["followApproachPointer"]
        on_approach=approach[0][0]<=measured<=approach[-1][0]
        if on_approach:
            cx,cy=interpolate(approach,measured)
        attached=0 if on_approach else tween(local,-8,-2)
        if attached>0:
            dx,dy=interpolate(contact["tipFromLowerRight"],local)
            target_x=x+(left+width+dx)*s
            target_y=y+(top+height+dy)*s
            cx=mix(cx,target_x,attached)
            cy=mix(cy,target_y,attached)
        angle=mix(18,r,tween(f,654,662))
        opacity=tween(f,624,626)*(1-.26*max(0,1-abs(measured-667)/5))
        cursor(im,cx,cy,angle,opacity,s*.59)

    def end(self,im,f):
        fields = tuple(self.track("closingWashFields", f))
        im.alpha_composite(measured_wash(fields))
        shine,=self.track("badgeClosingHighlights",f)
        finish = self.s["tracks"].get("closingBadgeFinish")
        finish = tuple(interpolate(finish,f)) if finish and f>=finish[0][0] else None
        contour = self.s["tracks"].get("closingBadgeShape")
        if contour and f>=contour[0][0]:
            pose = interpolate(contour,f)
            box, corner = pose[:4],pose[-1]
        else:
            box,corner=self.track("closingMeasuredBox",f),52
        fitted_badge(im,box,corner,max(.36 if finish else 0,5*(1-tween(f,696,704))),
                     1,shine,closing_finish=finish)
        captions = self.c["ending"]
        caption_ids = (("the","most","personal"),("imessage","assistant","yet"))
        for words, ids, weight in zip(captions,caption_ids,(515,690),strict=True):
            for word, word_id in zip(words,ids):
                if f<self.at(f"ending.{word_id}"):
                    continue
                track = self.s["tracks"][f"closingInk-{word_id}"]
                x,y,w,h,opacity = interpolate(track,f)
                if f<track[0][0]:
                    opacity *= .65
                fit_ink(im,word,(x,y,w,h),weight,opacity,2.3*(1-opacity))
        fade,=self.track("endingFade",f)
        if fade<1:
            return Image.blend(Image.new("RGBA",im.size,"black"),im,fade)
        return im

    def frame(self,f):
        im=Image.new("RGBA",(SIZE,SIZE),self.palette["paper"])
        if f<102:
            self.inbox(im,f)
        elif f<134:
            self.identity(im,f)
        elif f<162:
            self.assistant(im,f)
        elif f<213:
            self.personal(im,f)
        elif f<313:
            if f < 259:
                self.cluster(im,f)
            if f >= 258:
                self.profiles(im,f)
        elif f<403:
            self.sofia(im,f)
        if 478<=f<622:
            im.alpha_composite(measured_wash(tuple(self.track("measuredOrbitGlow",f))))
        if 397<=f<482:
            self.calendar(im,f)
        if 478<=f<622:
            self.apps(im,f)
        if 624<=f<696:
            self.follow(im,f)
        elif f>=696:
            im=self.end(im,f)
        return im.convert("RGB")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene",type=Path,default=Path(__file__).with_name("scene.json"))
    parser.add_argument("--cache",type=Path,required=True)
    parser.add_argument("--frames",help="Inclusive frame span, e.g. 397:479. By default render all frames.")
    args=parser.parse_args()
    scene=json.loads(args.scene.read_text())
    count=scene["timeline"]["picture"]["frameCount"]
    start,end=(map(int,args.frames.split(":")) if args.frames else (0,count-1))
    if not 0<=start<=end<count:
        parser.error(f"frame span must be inside 0:{count-1}")
    film=Film(scene)
    args.cache.mkdir(exist_ok=True,parents=True)
    for f in range(start,end+1):
        film.frame(f).save(args.cache/f"{f:06d}.png",compress_level=1)
    print(f"Rendered {end-start+1} pictures from {start} to {end}")


if __name__=="__main__":
    main()
