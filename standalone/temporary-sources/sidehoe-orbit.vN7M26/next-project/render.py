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
from artwork import curve_polygon, compact_inbox_head, rounded_gradient, sprite_portrait, stamp, text
from casing import paint_exit_casing, paint_speaker_slot
from treatments import calendar_emoji, calendar_face, follow_aperture, follow_pointer, glyph_ink, lit_phone, paint_camera_island, paint_message_surface


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


def register_bevel(stage, top, bottom, knots, falloff=32):
    """Align the independently painted rim and its reflection to the glass edge."""
    table = np.asarray(knots)
    left,right = max(0,int(table[0,0])-falloff),min(stage.width,int(table[-1,0])+falloff+1)
    cols = np.arange(left,right)
    y = np.arange(top,bottom)[:,None]
    a,b,u,v,contrast = [np.interp(cols,table[:,0],values) for values in table[:,1:].T]
    last=bottom-1
    mapped = np.where(y<a,top+(y-top)*(u-top)/(a-top),
             np.where(y<b,u+(y-a)*(v-u)/(b-a),v+(y-b)*(last-v)/(last-b)))
    mapped=np.clip(mapped-top,0,bottom-top-1)
    region=stage.crop((left,top,right,bottom))
    rgb=np.asarray(region.convert("RGB"),dtype=np.float32)
    i=np.floor(mapped).astype(int)
    fraction=(mapped-i)[...,None]
    cols_local=np.arange(right-left)
    warped=rgb[i,cols_local]*(1-fraction)+rgb[np.minimum(i+1,bottom-top-1),cols_local]*fraction
    paper=np.mean(rgb[:9],axis=0)
    rim = np.clip((y-a+14)/8,0,1)*np.clip((b+12-y)/8,0,1)
    warped+=rim[...,None]*(warped-paper)*(contrast-1)[None,:,None]
    edge = np.clip((cols-left)/falloff,0,1)*np.clip((right-1-cols)/falloff,0,1)
    result=rgb+(warped-rgb)*edge[None,:,None]
    stage.paste(Image.fromarray(np.uint8(np.rint(np.clip(result,0,255)))),(left,top))


def register_handset_edge(picture, knots, falloff):
    """Adjust the position and depth of a narrow casing cross-section."""
    samples = np.asarray(knots)
    height, width = picture.shape[:2]
    blend = 22
    left = max(0, int(samples[0, 0]) - blend)
    right = min(width, int(samples[-1, 0]) + blend + 1)
    top = max(0, int(samples[:, 1].min()) - falloff - 1)
    bottom = min(height, int(samples[:, 1].max()) + falloff + 2)
    columns = np.arange(left, right)
    rows = np.arange(top, bottom)[:, None]
    center, offset, taper = [np.interp(columns, samples[:, 0], values)
                              for values in samples[:, 1:].T]
    depth = rows - center
    normal_weight = np.clip((falloff - np.abs(depth)) / 11, 0, 1)
    span_weight = (np.clip((columns - left) / blend, 0, 1)
                   * np.clip((right - 1 - columns) / blend, 0, 1))
    sample_y = np.clip(rows + (offset + taper * depth) * normal_weight * span_weight,
                       0, height - 1)
    upper = sample_y.astype(int)
    lower = np.minimum(upper + 1, height - 1)
    amount = (sample_y - upper)[..., None]
    warped = picture[upper, columns] * (1 - amount) + picture[lower, columns] * amount
    picture[top:bottom, left:right] = np.rint(warped).astype(np.uint8)


def assistant_intro_pin(stage, x, y, size, distortion, *, motif_scale=1,
                        fringe=(3.2,2.3), ripple_offset=.37, lift=0):
    """Render the first pin through the same moving glass as the casing."""
    pad = 24
    diameter = round(size)
    pin = layer(diameter+2*pad,diameter+2*pad)
    center = pin.width/2
    mark=badge(128,motif_scale=motif_scale)
    if lift:
        material=np.asarray(mark).copy()
        level=material[:,:,:3].mean(axis=2)
        gain=np.clip((119-level)/64,0,1)*lift
        material[:,:,:3]=np.uint8(np.clip(np.rint(material[:,:,:3]+gain[:,:,None]),0,255))
        mark=Image.fromarray(material)
    stamp(pin,mark,center,center,diameter)
    mesh = []
    for top in range(0,pin.height,4):
        bottom = min(top+4,pin.height)
        delta = []
        for row in (top,bottom):
            t = (row-center)/diameter
            alpha = math.exp(-((t+ripple_offset)/.19)**2)
            delta.append(distortion*alpha*(math.sin(t*30)+.39*math.cos(t*44)))
        mesh.append(((0,top,pin.width,bottom),
                     (delta[0],top,delta[1],bottom,pin.width+delta[1],bottom,
                      pin.width+delta[0],top)))
    pin = pin.transform(pin.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
    if any(fringe):
        pin = apply_fringe(pin,*fringe)
    composite(stage,pin,x-center,y-center)


def screen_matte(source):
    """Estimate the glass tint under the glyph from the two clear side margins."""
    data=np.asarray(source,dtype=np.float32)
    band=min(6,source.width//5)
    left=np.median(data[:,:band],axis=1)
    right=np.median(data[:,-band:],axis=1)
    rows=np.arange(source.height)
    x=np.linspace(0,1,source.width)[None,:,None]
    low=np.maximum(rows-2,0)
    high=np.minimum(rows+2,source.height-1)
    left=(left[low]+2*left+left[high])*.25
    right=(right[low]+2*right+right[high])*.25
    return left[:,None,:]*(1-x)+right[:,None,:]*x


def refract_control(source, settings, *, matte=None):
    """Refract an editable glyph in its own screen-space exposure window."""
    dx,dy,sx,sy,slope,horizontal_split,vertical_split,contrast,focus,*shutter=settings
    w,h=source.size
    neutral=253
    exposed=source
    if shutter:
        # Transform the glyph's color difference so shutter streaks follow ink.
        if matte is None:
            matte=screen_matte(source)
        neutral=128
        delta=neutral+(np.asarray(source,dtype=np.float32)-matte)*.5
        exposed=Image.fromarray(np.uint8(np.clip(np.rint(delta),0,255)))
    center_x,center_y=w*.5,h*.5
    matrix=(1/sx,slope,center_x*(1-1/sx)-slope*center_y+dx,
            0,1/sy,center_y*(1-1/sy)+dy)
    panel=exposed.transform(exposed.size,Image.Transform.AFFINE,matrix,Image.Resampling.BICUBIC,
                           fillcolor=(neutral,)*3)
    if horizontal_split or vertical_split:
        if shutter:
            red,green,blue=panel.split()
            red=red.transform(red.size,Image.Transform.AFFINE,
                              (1,0,-horizontal_split,0,1,vertical_split),
                              Image.Resampling.BICUBIC,fillcolor=neutral)
            blue=blue.transform(blue.size,Image.Transform.AFFINE,
                                (1,0,horizontal_split,0,1,-vertical_split),
                                Image.Resampling.BICUBIC,fillcolor=neutral)
            panel=Image.merge("RGB",(red,green,blue))
        else:
            panel=apply_fringe(panel.convert("RGBA"),horizontal_split,vertical_split).convert("RGB")
    if focus>.25:
        panel=panel.filter(ImageFilter.GaussianBlur(focus))
    if shutter:
        gap, overlap = shutter
        early, late = [panel.transform(panel.size,Image.Transform.AFFINE,(1,0,0,0,1,side*gap),
                                       Image.Resampling.BICUBIC,fillcolor=(neutral,)*3)
                       for side in (-1,1)]
        panel=Image.blend(panel,Image.blend(early,late,.5),overlap)
        pixels=matte+(np.asarray(panel,dtype=np.float32)-neutral)*(2*contrast)
        panel=Image.fromarray(np.uint8(np.clip(np.rint(pixels),0,255)))
    elif contrast!=1:
        pixels=np.asarray(panel,dtype=float)
        pixels=253-(253-pixels)*contrast
        panel=Image.fromarray(np.uint8(np.clip(np.rint(pixels),0,255)))
    yy,xx=np.mgrid[:h,:w]
    edge=np.minimum(np.minimum(xx,w-xx-1),np.minimum(yy,h-yy-1))
    if shutter:
        edge=np.clip(edge/max(15,2*gap+3),0,1)
        edge=edge*edge*(3-2*edge)
    else:
        edge=np.clip(edge/8,0,1)
    coverage=np.uint8(np.rint(edge*255))
    return Image.composite(panel,source,Image.fromarray(coverage))


def caustic_lobes(columns, rows, geometry):
    cx,cy,rx,ry,spread=geometry
    x,y=(columns-cx)/rx,(rows-cy)/ry
    angle=np.arctan2(y,x)
    radial=np.exp(-((np.hypot(x,y)-1)/spread)**2)
    directions=np.linspace(0,math.tau,8,endpoint=False)
    light=np.exp(3.8*(np.cos(angle[...,None]-directions)-1))
    return radial[...,None]*light


def paint_control_caustics(stage, settings):
    """Add the colored light cast by the glass around the moving controls."""
    for box,geometry,colors in settings:
        left,top,right,bottom=box
        rows,columns=np.mgrid[top:bottom,left:right]
        samples=caustic_lobes(columns,rows,geometry)
        rgb=np.asarray(stage.crop(box).convert("RGB"),dtype=float)+samples@np.asarray(colors)
        stage.paste(Image.fromarray(np.uint8(np.clip(np.rint(rgb),0,255))),(left,top))


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


@lru_cache(maxsize=140)
def title_heart_silhouette(color, contours):
    """Draw two independently shaped Bézier lobes and the pointed lower edge."""
    notch_x,notch_y,left_crown,right_crown,flank=contours
    mask=Image.new("L",(300,300))
    draw=ImageDraw.Draw(mask)
    notch=(149+notch_x,64+notch_y)
    curve_polygon(draw,notch,(
        ((110,-4+left_crown),(7,5+left_crown),(3,97)),
        ((-3-flank,169),(84,237),(143,293)),
        ((147,297),(153,297),(157,292)),
        ((216,239),(305+flank,166),(296,96)),
        ((290,8+right_crown),(192,right_crown),notch),
    ),255)
    ink=Image.new("RGBA",mask.size,color)
    ink.putalpha(mask)
    return ink.resize((180,180),Image.Resampling.LANCZOS)


def title_heart(canvas, pose, contour=None):
    x,y,width,height,angle,alpha,shear,focus,*pigment = pose
    if alpha<=0:
        return
    color = tuple(pigment) if pigment else (247,143,253)
    mark = title_heart_silhouette(color,tuple(contour)) if contour else curved_heart(180,180,color)
    span = math.ceil(math.hypot(width*(1+abs(shear)),height)/2+4*focus+3)
    left,top=math.floor(x-span),math.floor(y-span)
    angle=math.radians(angle)
    cosine,sine = math.cos(angle),math.sin(angle)
    vx,vy = sine/height,cosine/height
    ux,uy = cosine/width-shear*vx,-sine/width-shear*vy
    matrix = (ux,uy,.5+ux*(left-x)+uy*(top-y),
              vx,vy,.5+vx*(left-x)+vy*(top-y))
    image = mark.transform((2*span+2,2*span+2),Image.Transform.AFFINE,
                           tuple(180*v for v in matrix),Image.Resampling.BICUBIC)
    composite(canvas,blur(image,focus),left,top,alpha)


def paint_settled_bevels(stage, bands):
    """Apply separate stage-space light profiles to the straight sections of the case."""
    rendered=np.asarray(stage).copy()
    for axis,start,span,ink,screen,inner,buttons in bands:
        image=rendered if axis=="side" else rendered.transpose(1,0,2)
        first,solid_start,solid_end,last=span
        stop=start+len(ink)
        profile=np.asarray(ink,dtype=float)
        line=np.arange(first,last)
        opacity=np.interp(line,(first,solid_start,solid_end,last),(0,1,1,0))
        paint=np.broadcast_to(profile,(last-first,len(ink),3)).copy()
        screen_weight=np.asarray(screen,dtype=float)
        if axis=="side":
            # Mix toward the nearby screen tone without extending individual glyph strokes.
            paper=image[first:last,inner-3:inner+4,:3]
            glass_color=np.clip(np.percentile(paper,80,axis=1),210,253)
            paint -= (253-glass_color[:,None])*screen_weight[None,:,None]
        for top,bottom,spread,values in buttons:
            a=np.interp(line,(top-spread,top+spread,bottom-spread,bottom+spread),(0,1,1,0))
            paint+=a[:,None,None]*np.asarray(values)[None,:,:]
        crop=image[first:last,start:stop,:3]
        coverage=opacity[:,None,None]*(1-screen_weight[None,:,None]**2)
        crop[:]=np.uint8(np.clip(np.rint(crop*(1-coverage)+paint*coverage),0,255))
    stage.paste(Image.fromarray(rendered),(0,0))


def warp_handset(stage, settings):
    """Evaluate the measured camera deformation before drawing the independent cursor."""
    xs,ys,offsets=settings
    mesh=[]
    for j,(top,bottom) in enumerate(zip(ys,ys[1:])):
        for i,(left,right) in enumerate(zip(xs,xs[1:])):
            source=[]
            for x,y,col,row in ((left,top,i,j),(left,bottom,i,j+1),
                                (right,bottom,i+1,j+1),(right,top,i+1,j)):
                dx,dy=offsets[row][col]
                source.extend((x+dx,y+dy))
            mesh.append(((left,top,right,bottom),tuple(source)))
    warped=stage.transform(stage.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC,
                           fillcolor=(253,253,253,255))
    stage.paste(warped,(0,0))


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


def measured_badge_outline(size, offset, outline):
    """Evaluate coverage of the rounded case with independent corner radii."""
    cx,cy,width,height,rx,ry,feather=outline
    xx=np.arange(size[0])+offset[0]+.5
    yy=np.arange(size[1])+offset[1]+.5
    sx=np.maximum(abs(xx-cx)-(width/2-rx),0)/rx
    sy=np.maximum(abs(yy-cy)-(height/2-ry),0)/ry
    length=np.hypot(sx[None,:],sy[:,None])
    slope=np.hypot(sx[None,:]/rx,sy[:,None]/ry)/np.maximum(length,1e-5)
    distance=(length-1)/(slope+1e-6)
    alpha=np.clip(.5-distance/feather,0,1)
    return Image.fromarray(np.uint8(np.rint(255*alpha)))


def fitted_badge(im, box, corner, radius=0, opacity=1, shine=0, *, reveal=1,
                 closing_finish=None, motif_fit=0, raster_width=256, outline=None, part_poses=()):
    x,y,w,h=box
    mark=badge(corner,reveal,closing_finish,raster_width=raster_width,outer_mask=outline is None,part_poses=part_poses)
    if motif_fit:
        adjusted=badge(corner,reveal,closing_finish,refined=True,raster_width=raster_width,outer_mask=outline is None,part_poses=part_poses)
        mark=Image.blend(mark,adjusted,motif_fit)
    if shine:
        highlight=Image.new("RGBA",mark.size,(175,165,252,round(shine)))
        mixed=Image.alpha_composite(mark,highlight)
        mixed.putalpha(mark.getchannel("A"))
        mark=mixed
    left,top=x-w/2,y-h/2
    if closing_finish is not None:
        pad=max(4,math.ceil(radius*4))
        x0,y0=math.floor(left)-pad,math.floor(top)-pad
        xs,ys=mark.width/w,mark.height/h
        width,height=math.ceil(left+w)-x0+pad,math.ceil(top+h)-y0+pad
        transform=xs,0,(x0-left)*xs,0,ys,(y0-top)*ys
        fill=(51,51,51,255) if outline else None
        mark=mark.transform((width,height),Image.Transform.AFFINE,transform,Image.Resampling.BICUBIC,fillcolor=fill)
        left,top=x0,y0
    else:
        mark=mark.resize((max(1,round(w)),max(1,round(h))),Image.Resampling.LANCZOS)
    mark=blur(mark,radius)
    if outline:
        mark.putalpha(measured_badge_outline(mark.size,(left,top),outline))
    composite(im,mark,left,top,opacity)


def fit_ink(im, caption, bbox, weight, opacity=1, blur_radius=0, *,
            family=font, ink=(20,20,20), character_opacity=None, fractional=False,
            glyph=pictogram):
    x,y,w,h=bbox
    if opacity<=0 or w<=0 or h<=0:
        return
    face = family(190 if fractional else 160, weight)
    full_box = None
    if family is font and character_opacity is None:
        plane=layer(1050,140)
        text(ImageDraw.Draw(plane),10,12,caption,80,(*ink,255),weight,glyph=glyph)
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


def registered_message_ink(stage, caption, spec):
    """Keep text live while moving its baseline with the bubble."""
    left,top,width,height=spec["box"]
    weight,focus,color=spec["weight"],spec["blur"],tuple(spec["color"])
    slope=spec.get("slope",0)
    if not slope:
        fit_ink(stage,caption,spec["box"],weight,blur_radius=focus,
                family=messages_font,ink=color,fractional=True)
        return
    pad=math.ceil(abs(slope)*width/2+4*focus+7)
    x0,y0=math.floor(left)-pad,math.floor(top)-pad
    ink=layer(math.ceil(left+width)-x0+pad,math.ceil(top+height)-y0+pad)
    fit_ink(ink,caption,(left-x0,top-y0,width,height),weight,blur_radius=focus,
            family=messages_font,ink=color,fractional=True)
    midpoint=left-x0+width/2
    transform=(1,0,0,-slope,1,slope*midpoint)
    tilted=ink.transform(ink.size,Image.Transform.AFFINE,transform,Image.Resampling.BICUBIC)
    composite(stage,tilted,x0,y0)


def exposed_key_ink(im, letter, geometry):
    """Draw one live keyboard glyph with its own shear and exposure vector."""
    cx,cy,width,height,shear_x,shear_y,trail_x,trail_y,focus,coverage=geometry
    pad=math.ceil(max(width,height)*.92+max(abs(trail_x),abs(trail_y))+6)
    left,top=math.floor(cx)-pad,math.floor(cy)-pad
    local_x,local_y=cx-left,cy-top
    plate=layer(2*pad+2,2*pad+2)
    fit_ink(plate,letter,(local_x-width/2,local_y-height/2,width,height),435,
            family=messages_font,ink=(29,29,31),fractional=True)
    if shear_x or shear_y:
        transform=(1,shear_x,-shear_x*local_y,shear_y,1,-shear_y*local_x)
        plate=plate.transform(plate.size,Image.Transform.AFFINE,transform,Image.Resampling.BICUBIC)
    if trail_x or trail_y:
        plate=vertical_blur(plate,trail_y,horizontal=trail_x)
    composite(im,blur(plate,focus),left,top,coverage)


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


def entrance_casing(plate, left_width, right_width, floor_width):
    width,height=plate.size
    y,x=np.mgrid[:height,:width]
    radius=65
    edge_x=np.abs(x-(width-1)/2)-(width/2-radius-1)
    edge_y=np.abs(y-(height-1)/2)-(height/2-radius-1)
    depth=radius-np.hypot(np.maximum(edge_x,0),np.maximum(edge_y,0))
    depth-=np.minimum(np.maximum(edge_x,edge_y),0)
    side=np.where(x<width/2,left_width,right_width)
    vertical=np.clip((edge_y-edge_x+16)/32,0,1)
    floor=vertical*(y>height/2)
    ceiling=vertical-floor
    bevel=side*(1-vertical)+floor_width*floor+14*ceiling
    along=np.clip(depth/bevel,0,1)
    shade=np.interp(along,[0,.10,.20,.31,.48,.64,.81,.92,1],
                    [119,85,99,79,49,19,5,38,252])
    bottom_shade=np.interp(along,[0,.10,.21,.42,.62,.80,.94,1],
                           [135,66,51,21,13,7,52,248])
    shade=shade*(1-floor)+bottom_shade*floor
    material=np.asarray(plate).copy()
    coverage=(depth>=-.5)&(depth<bevel)
    material[coverage,:3]=np.stack((shade,shade,np.minimum(255,shade+2)),axis=2)[coverage]
    material[:,:,3]=np.rint(np.clip(depth+.5,0,1)*255)
    return Image.fromarray(material)


def exposed_entry_plate(plate, x, y, x_scale, y_scale, soft_x, soft_y):
    """Map the independently drawn screen and case into the entry shutter."""
    width=max(1,round(plate.width*x_scale))
    height=max(1,round(plate.height*y_scale))
    pad_x,pad_y=math.ceil(4*soft_x)+4,math.ceil(4*soft_y)+4
    exposed=layer(width+2*pad_x,height+2*pad_y)
    scaled=plate.resize((width,height),Image.Resampling.BICUBIC)
    exposed.alpha_composite(scaled,(pad_x,pad_y))
    return blur(exposed,(soft_x,soft_y)),x-pad_x,y-pad_y


def status(d,w,y,label,island=False,*,island_bounds=None):
    if label:
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
        left,top,right,bottom = island_bounds or (w/2-58,y-20,w/2+58,y+14)
        mid=(top+bottom)/2
        d.rounded_rectangle((left,top,right,bottom),(bottom-top)/2,fill="#09090a")
        d.rounded_rectangle((left+6,mid-10,right-50,mid+10),10,fill="#141415")
        oval(d,right-17,mid,8,8,"#14131b")
        oval(d,right-17,mid,3.3,3.3,"#292b41")


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


@lru_cache(maxsize=16)
def open_portrait(key):
    """Load the original transparent head shared by the editable portrait poses."""
    path=Path(__file__).parent/"assets"/"portraits"/f"{key}.png"
    with Image.open(path) as image:
        return image.convert("RGBA")


def registered_portrait(center_x, center_y, width, height, color, actor, head, *, gradient=None,
                        head_opacity=1, right_fade=0, head_wash=0, disk_wash=0):
    """Draw the disk and transparent head on independent measured planes."""
    left,top=math.floor(center_x-width/2)-2,math.floor(center_y-height/2)-2
    right,bottom=math.ceil(center_x+width/2)+2,math.ceil(center_y+height/2)+2
    rows,columns=np.mgrid[top:bottom,left:right]+.5
    radius=np.hypot((columns-center_x)/(width/2),(rows-center_y)/(height/2))
    opacity=np.clip((1-radius)*min(width,height)/2+.5,0,1)
    mask=Image.fromarray(np.uint8(np.rint(opacity*255)))
    if gradient:
        stops=np.linspace(center_y-height/2,center_y+height/2,len(gradient))
        pixels=np.full((mask.height,mask.width,4),255,dtype=np.uint8)
        tones=np.array([np.interp(rows[:,0],stops,values) for values in zip(*gradient)]).T
        tones=tones+(253-tones)*disk_wash
        pixels[:,:,:3]=np.rint(tones[:,None,:])
        sprite=Image.fromarray(pixels)
    else:
        sprite=Image.new("RGBA",mask.size,tuple(color)+(255,))
    if actor:
        if head:
            x0,y0,x1,y1 = head
        else:
            # The original sprite proportions keep the start of the entrance continuous.
            x0,y0,x1,y1=(center_x-width*.31,center_y-height*.363,
                         center_x+width*.31,center_y+height*.399)
        art=open_portrait(actor).resize((max(1,round(x1-x0)),max(1,round(y1-y0))),
                                       Image.Resampling.LANCZOS)
        if head_wash:
            washed = Image.blend(art,Image.new("RGBA",art.size,(253,253,253,255)),head_wash)
            washed.putalpha(art.getchannel("A"))
            art=washed
        composite(sprite,art,x0-left,y0-top,head_opacity)
    if right_fade:
        darkness = np.clip((columns-center_x)/(width*.52)+.15,0,1)
        mask = Image.fromarray(np.uint8(np.rint(opacity*(1-right_fade*darkness)*255)))
    sprite.putalpha(mask)
    return sprite,left,top


def cluster_surround(contours):
    """Shade the connected shell inward from its editable outer paths."""
    scale=2
    field=np.zeros((SIZE//scale,SIZE//scale),dtype=float)
    for contour in contours:
        controls=np.asarray(contour,dtype=float)
        x0,y0=np.maximum(0,np.floor(controls.min(axis=0)/scale).astype(int)-5)
        x1,y1=np.minimum(SIZE//scale,np.ceil(controls.max(axis=0)/scale).astype(int)+5)
        px,py=controls.T/scale
        local=(x1-x0,y1-y0)
        silhouette=Image.new("L",local)
        ImageDraw.Draw(silhouette).polygon(list(zip(px-x0,py-y0)),fill=255)
        yy,xx=np.mgrid[y0:y1,x0:x1]+.5
        distances=np.full(xx.shape,np.inf)
        for start,end in zip(controls,np.roll(controls,-1,axis=0),strict=True):
            dx,dy=(end-start)/scale
            u,v=xx-start[0]/scale,yy-start[1]/scale
            denom=dx*dx+dy*dy
            if denom:
                part=np.clip((u*dx+v*dy)/denom,0,1)
                np.minimum(distances,(u-part*dx)**2+(v-part*dy)**2,out=distances)
        signed=np.sqrt(distances)*scale*np.where(np.asarray(silhouette),1,-1)
        fade=np.interp(signed,[-8,-2,0,3,7,14,22,33,48,70,96],
                             [0,.06,.36,.73,1,.93,.72,.48,.28,.11,0])
        np.maximum(field[y0:y1,x0:x1],fade,out=field[y0:y1,x0:x1])
    tinted=Image.new("RGBA",(SIZE,SIZE),(236,231,251))
    matte=Image.fromarray(np.uint8(np.rint(field*255))).resize(tinted.size,Image.Resampling.BICUBIC)
    tinted.putalpha(matte)
    return tinted


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

    def avatar(self,im,key,x,y,diam,opacity=1,bg="",neutral=False,*,lit=False,head_pose=(),focus=0,disk_lights=()):
        spec = self.s["avatars"][key]
        lights = (bg,bg,1) if lit and bg else ()
        if lit and not bg:
            lights = tuple(disk_lights or self.s.get("pinLighting", {}).get(key, ()))
        asset = (sprite_portrait(key,spec[0],bg,not neutral,lights,head_pose) if self.s.get("portraitSprites")
                 else portrait(tuple(spec),bg,neutral))
        stamp(im,blur(asset,focus),x,y,diam,opacity)

    def inbox_intro_chrome(self, stage, chrome, poses):
        parts = ((60,157,260,257),(538,158,805,263),(43,267,226,391),
                 (293,271,527,387),(624,266,779,393))
        for section, pose in zip(parts,poses,strict=True):
            if pose is None:
                continue
            x,y,w,h,opacity,soft_x,soft_y,angle = pose
            patch=chrome.crop(section)
            pixels=np.asarray(patch,dtype=np.int16)
            ink=(pixels[:,:,3]>=166)&(pixels[:,:,:3].mean(2)<161)
            iy,ix=np.where(ink)
            if not len(ix):
                continue
            l,t,r,b=ix.min(),iy.min(),ix.max()+1,iy.max()+1
            sx,sy=w/(r-l),h/(b-t)
            patch=patch.resize((max(1,round(patch.width*sx)),max(1,round(patch.height*sy))),
                               Image.Resampling.BICUBIC)
            left,top=x-l*sx,y-t*sy
            if angle:
                w0,h0=patch.size
                patch=patch.rotate(angle,Image.Resampling.BICUBIC,expand=True)
                left-=(patch.width-w0)/2
                top-=(patch.height-h0)/2
            composite(stage,blur(patch,(soft_x,soft_y)),left,top,opacity)

    def inbox_scroll_rows(self, stage, frame, rows, home, *, focus=None, offset=(0,0)):
        surface = layer()
        d = ImageDraw.Draw(surface)
        emoji_font = os.environ.get("SIDEHOE_EMOJI_FONT", "/System/Library/Fonts/Apple Color Emoji.ttc")

        def draw_emoji(draw, name, x, y, size):
            icon = {"wink": "😉", "sushi": "🍣"}.get(name)
            if icon and Path(emoji_font).is_file():
                calendar_emoji(draw,icon,x,y,size,(-.54,-.51,1.08,1.02),emoji_font)
            else:
                pictogram(draw,name,x,y,size)

        for index, dot, avatar, name, quote, time, divider, opacity, backdrop in rows:
            if opacity:
                person, preview, stamp_text, key = self.s["inboxRows"][index]
                x, y, width, height = dot
                d.ellipse((x, y, x+width, y+height), fill=(22,169,232,round(255*opacity)))
                compact = self.s.get("inboxCompactPortraits",{}).get(str(index))
                if compact:
                    pose, color = compact
                    x,y,diam = avatar
                    oval(d,x,y,diam/2,diam/2,(*color,round(255*opacity)))
                    stamp(surface,compact_inbox_head(pose),x,y,diam,opacity)
                else:
                    self.avatar(surface,key,*avatar,opacity=opacity,bg=backdrop,lit=bool(backdrop))
                fit_ink(surface,person,name,630,opacity,.16,family=messages_font,
                        ink=(18,18,19),fractional=True)
                preview_font = font if "{" in preview else messages_font
                fit_ink(surface,preview,quote,395,opacity,.19,family=preview_font,
                        ink=(130,129,134),fractional=True,glyph=draw_emoji)
                fit_ink(surface,stamp_text,time,405,opacity*.85,.21,family=messages_font,
                        ink=(153,149,157),fractional=True)
                left, top, width, height = time
                right = left+width+14
                d.line((right,top+4,right+7,top+11,right,top+18),
                       fill=(192,190,199,round(215*opacity)),width=2)
            d.line((283,divider,820,divider),fill=(235,234,239,186),width=1)
        if home:
            bounds, tone = home
            d.rounded_rectangle(bounds,radius=4,fill=tuple(tone))
        blur_y, = self.track("inboxScrollSmear",frame)
        composite(stage,blur(surface,focus or (.38,max(.12,blur_y*.26))),*offset)

    def inbox(self,im,f):
        intro = self.s.get("inboxIntroRegistration",{}).get(str(f))
        scrolling = self.s.get("inboxScrollRegistration",{}).get(str(f))
        held = scrolling["chrome"] if scrolling else self.s.get("inboxHeldRegistration",{}).get(str(f))
        measured_rows = held.get("measuredRows") if held else None
        i=layer(820,2500)
        chrome=layer(820,630)
        d=ImageDraw.Draw(chrome)
        clock = held.get("clockInk") if held else None
        status_box = held.get("statusInk") if held else None
        if status_box:
            symbols = layer(815,310)
            status(ImageDraw.Draw(symbols),815,214,None)
            tight = symbols.crop(symbols.getbbox())
            left,top,width,height = status_box
            composite(chrome,tight.resize((round(width),round(height)),Image.Resampling.LANCZOS),
                      left,top)
        else:
            status(d,815,214,None if clock else self.c["status"])
        if clock:
            fit_ink(chrome,self.c["status"],clock,555,.99,.18,
                    family=messages_font,ink=(12,12,13),fractional=True)
        floating_control(chrome, 77, 292, 109, 68, 30)
        d.text((131,312),self.c["edit"],font=messages_font(32,630),fill="#090909",anchor="mt")
        heading=held.get("headingInk") if held else None
        if heading:
            fit_ink(chrome,self.c["inbox"],heading,630,.98,.16,
                    family=messages_font,ink=(13,13,14),fractional=True)
        else:
            d.text((410,306),self.c["inbox"],font=messages_font(35,620),fill="#090909",anchor="mt")
        floating_control(chrome, 666, 292, 68, 68, 34)
        for width,y in [(38,318),(28,327),(16,336)]:
            d.rounded_rectangle((696-width/2,y,696+width/2,y+3),2,fill=INK)

        if intro:
            self.inbox_intro_chrome(im,chrome,intro["chrome"])
        elif f<10:
            alpha,softness,rise=self.track("inboxIntroHeader",f)
            composite(i,vertical_blur(blur(chrome,softness),softness*1.8),0,rise,alpha)
        else:
            composite(i,chrome,0,held["chromeY"] if held else 0)
        d=ImageDraw.Draw(i)
        for j,((label,key),x) in enumerate(zip(self.s["inboxPins"],[169,411,651])):
            if f<10:
                continue
            p=tween(f,0 if j==1 else 1,5 if j==1 else 8)
            dx,dy,size = held["pins"][j] if held else (0,0,1)
            profile = held.get("pinHeadPoses", ((),(),()))[j] if held else ()
            focus = held.get("pinSoftness",0) if held else 0
            lighting = held.get("pinDiskLighting", ((),(),()))[j] if held else ()
            self.avatar(i,key,x+dx,473+68*(1-p)+dy,162*(.78+.22*p)*size,
                        (.58+.42*p if f<10 else .25+.75*p) if j==1 else p,lit=True,
                        head_pose=tuple(profile),focus=tuple(focus) if isinstance(focus,list) else focus,
                        disk_lights=tuple(lighting))
            if p>.38:
                name = held.get("pinLabels",[None]*3)[j] if held else None
                if name:
                    fit_ink(i,label,name,495,1,.16,family=messages_font,ink=(47,47,49),
                            fractional=True)
                else:
                    text(d,x+dx,571+dy,label,26,"#353535",510,"center")
        p=tween(f,2.5,8) if f<10 else tween(f,4,11)
        tag=None
        if p>0:
            tag=layer(255,80)
            tagd=ImageDraw.Draw(tag)
            tagd.rounded_rectangle((3,4,252,70),21,fill=(253,253,253,224),outline="#f1f1f3",width=2)
            tagd.polygon([(186,63),(211,63),(204,77)],fill="#fdfdff")
            note_ink = held.get("noteInk") if held else None
            message, marker, suffix = self.c["pinNote"].rpartition(" {broken}")
            if note_ink and marker and not suffix and "{" not in message:
                fit_ink(tag,message,note_ink["text"],470,1,.29,family=messages_font,
                        ink=(32,32,34),fractional=True)
                x, y, w, h = note_ink["heart"]
                emoji_font = os.environ.get("SIDEHOE_EMOJI_FONT", "/System/Library/Fonts/Apple Color Emoji.ttc")
                calendar_emoji(tagd,"💔",x,y,1,(0,0,w,h),emoji_font)
            else:
                text(tagd,124,22,self.c["pinNote"],25,INK,545,"center",
                     glyph=lambda *args: self.source_glyph(f,*args))
            if f>=10:
                dx,dy,_ = held["pins"][1] if held else (0,0,1)
                left,top=285+dx,359+(1-p)*22+dy*.67
                note = held.get("noteAppearance") if held else None
                if note:
                    shift_x, shift_y, coverage, focus = note
                    left += shift_x
                    top += shift_y
                    padding = math.ceil(4*focus)
                    depth = layer(255+2*padding, 80+2*padding)
                    ImageDraw.Draw(depth).rounded_rectangle(
                        (padding+3,padding+6,padding+252,padding+78),21,
                        fill=(68,68,73,round(255*coverage)))
                    composite(i,blur(depth,focus),left-padding,top-padding,p)
                composite(i,tag,left,top,p)

        rows=layer(820,2240)
        rd=ImageDraw.Draw(rows)
        standard_rows = [] if scrolling or intro or measured_rows else self.s["inboxRows"]
        for j,(name,quote,time,key) in enumerate(standard_rows):
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
            if scrolling:
                row_exposure = scrolling.get("rowExposure")
                focus, offset = (tuple(row_exposure[:2]),row_exposure[2:]) if row_exposure else (None,(0,0))
                self.inbox_scroll_rows(im,f,scrolling["rows"],scrolling["home"],focus=focus,offset=offset)
            else:
                composite(im,blur(row_layer,amount),500-410*row_scale,row_y,1,row_scale)
            if f<=59:
                chrome_y,chrome_scale=self.track("inboxChromePose",f)
                header=i.crop((0,0,820,620))
                chrome_exposure = scrolling.get("chromeExposure") if scrolling else None
                shift_x,shift_y = 0,0
                if chrome_exposure:
                    soft_x,soft_y,shift_x,shift_y = chrome_exposure
                    header = blur(header,(soft_x,soft_y))
                elif streak > 2:
                    header = header.convert("RGBa").filter(
                        ImageFilter.GaussianBlur((.38,streak*.23))).convert("RGBA")
                composite(im,header,500-410*chrome_scale+shift_x,chrome_y+shift_y,1,chrome_scale)
        elif intro:
            self.inbox_scroll_rows(im,f,intro["rows"],None,focus=tuple(intro["rowFocus"]))
        elif held:
            composite(im,blur(i,amount),500-410*scale,y,1,scale)
            if measured_rows:
                focus = tuple(held.get("measuredRowFocus", (.35,.32)))
                self.inbox_scroll_rows(im,f,measured_rows,None,focus=focus)
            else:
                row_left,row_top,row_scale = held["rows"]
                composite(im,rows,row_left,row_top,1,row_scale)
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
                measured_focus = intro.get("pinFocus") if intro else None
                focus = tuple(measured_focus[j]) if measured_focus and measured_focus[j] else max(0,5-f*1.10)
                composite(im,blur(avatar_layer,focus),x-112,cy-108)
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
        screen = self.s.get("assistantScreenRegistration",{}).get(str(f),{})
        island = self.s.get("assistantIslandRegistration", {}).get(str(f))
        if island is None:
            ix,iy,iw,ih = self.track("assistantIslandBox",f)
            d.rounded_rectangle((ix,iy,ix+iw,iy+ih),ih/2,fill="#0a0a0c")
            d.rounded_rectangle((ix+13,iy+.19*ih,ix+.56*iw,iy+.80*ih),ih*.305,fill="#131315")
            oval(d,ix+.859*iw,iy+ih/2,16,16,"#161720")
            oval(d,ix+.859*iw,iy+ih/2,7,7,"#252b42")
        if "time" in screen:
            fit_ink(beneath,self.c["status"],screen["time"],540,
                    family=messages_font,ink=(20,20,21),fractional=True)
        else:
            text(d,103,86,self.c["status"],34,INK,630)
        if "cellular" in screen:
            left,top,width,height = screen["cellular"]
            for i,part in enumerate((.43,.61,.79,1)):
                x=left+i*width*.268
                d.rounded_rectangle((x,top+height*(1-part),x+width*.19,top+height),
                                    width*.046,fill="#252527")
        else:
            for i,height in enumerate((7,12,17,21)):
                d.rounded_rectangle((604+11*i,116-height,612+11*i,116),3,fill=INK)
        if "wifi" in screen:
            left,top,width,height = screen["wifi"]
            center = left+width*.5
            for extent,lift,depth in ((1,0,1.49),(.69,.31,.89),(.36,.62,.40)):
                radius=width*extent*.61
                d.arc((center-radius,top+height*lift,center+radius,top+height*(lift+depth)),
                      218,322,fill="#202021",width=max(1,round(width*.128)))
            oval(d,center,top+height*.916,width*.097,height*.082,"#202021")
        else:
            d.arc((667,90,707,118),208,332,fill=INK,width=5)
            d.arc((674,99,700,118),208,332,fill=INK,width=4)
            oval(d,687,114,4,4,INK)
        if "battery" in screen:
            left,top,width,height = screen["battery"]
            d.rounded_rectangle((left,top,left+width*.885,top+height),
                                height*.24,fill="#262628")
            d.rounded_rectangle((left+width*.958,top+height*.32,left+width,top+height*.68),
                                width*.028,fill="#303031")
        else:
            d.rounded_rectangle((727,93,774,115),6,fill=INK)
            d.rectangle((776,100,781,108),fill=INK)
        floating_control(beneath, 85, 181, 113, 71, 32)
        floating_control(beneath, 720, 181, 70, 70, 35)
        for half,y_line in ((19,208),(14,218),(8,228)):
            d.rounded_rectangle((755-half,y_line,755+half,y_line+4),2,fill="#535258")
        if "edit" in screen:
            fit_ink(beneath,self.c["edit"],screen["edit"],585,
                    family=messages_font,ink=(24,24,26),fractional=True)
        else:
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
        elif "heading" in screen:
            fit_ink(beneath,self.c["inbox"],screen["heading"],596,
                    family=messages_font,ink=(18,18,20),fractional=True)
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
        pins=screen.get("pins",[(left,py+side_lift,side_diam),(right,py+side_lift,side_diam)])
        head_poses = screen.get("headPoses", ((),()))
        disk_lighting = screen.get("pinDiskLighting", ((),()))
        for (x,cy,disk),k,n,face,lighting in zip(
                pins,("marie","darla"),("Marie","Darla"),head_poses,disk_lighting,strict=True):
            self.avatar(beneath,k,x,cy,disk,pin_alpha,lit=True,head_pose=tuple(face),
                        disk_lights=lighting)
            if f>=135:
                ld.text((x,name_y),n,font=messages_font(29,490),fill="#333333",anchor="mt")
        badge_pose = screen.get("badgePose")
        pin_calibration = screen.get("badgeCalibration")
        if pin_calibration:
            pose,motif_scale,fringe,phase,lift = pin_calibration
            assistant_intro_pin(beneath,*pose,motif_scale=motif_scale,fringe=fringe,
                                ripple_offset=phase,lift=lift)
        elif badge_pose:
            x, y, diameter, artwork = badge_pose
            mark = badge(128)
            if artwork:
                mark = Image.blend(mark, badge(128,refined=True), artwork)
            stamp(beneath,mark,x,y,diameter)
        elif optics and "pin" in optics:
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
            row = layer(900, 125)
            drow = ImageDraw.Draw(row)
            adjustment = self.s.get("assistantRowRegistration", {}).get(str(f), {})
            def pose(key):
                dx, dy, coverage = adjustment.get(key, (0, 0, 1))
                return dx, dy, coverage
            dx, dy, coverage = pose("avatar")
            self.avatar(row, "danielle", 122+dx, 63+dy, 66, coverage)
            for key, point, caption, weight, size, color, anchor in (
                ("name", (184, 0), self.c.get("assistantRowName", "Natalie"),
                 660, 34, (23, 23, 26), "lt"),
                ("preview", (184, 42), self.c.get("assistantRowPreview", "Do u wanna go out tmrw?"),
                 420, 29, (141, 139, 141), "lt"),
                ("time", (800, 2), "1:50 AM", 430, 27, (153, 148, 153), "rt"),
            ):
                dx, dy, coverage = pose(key)
                drow.text((point[0]+dx, point[1]+dy), caption,
                          font=messages_font(size, weight), fill=(*color, round(255*coverage)),
                          anchor=anchor)
            dx, dy, coverage = pose("chevron")
            drow.line((821+dx, 5+dy, 830+dx, 14+dy, 821+dx, 23+dy),
                      fill=(215, 211, 220, round(255*coverage)), width=3)
            composite(beneath, row, 0, row_y, row_alpha)
        basis = self.s["tracks"].get("assistantBodyFocus")
        if basis:
            spread, = interpolate(basis,f)
        else:
            spread=7*(1-tween(f,134,141))+4.8*tween(f,155,161)
        body = blur(beneath,spread)
        if f==134:
            exposure = optics.get("exposure",12) if optics else 17
            body = vertical_blur(body,exposure)
        if 135 <= f <= 137:
            gutter = 28
            padded = layer(body.width,body.height+gutter)
            padded.alpha_composite(body,(0,gutter))
            curved = lens_ripple(padded,self.s["measuredRimDisplacement"][str(f)])
            shift,breadth = {135:(4.3,.20),136:(4.9,.40),137:(1.8,.39)}[f]
            if optics and "lensFringe" in optics:
                shift,breadth = optics["lensFringe"]
            body = rim_fringe(curved,shift*.54,shift*.64,gutter+9,breadth)
            y -= gutter
        if optics and "rails" in optics:
            body = register_lens_rails(body,optics["rails"])
        composite(im,body.resize((round(width),body.height),Image.Resampling.BICUBIC),x,y)
        veil = self.s.get("assistantVeilRegistration", {}).get(str(f))
        if veil:
            controls = tuple(map(tuple, veil["color"]))
            response = tuple(veil["response"])
        else:
            pose = self.track("assistantLighting",f)
            controls = tuple(tuple(pose[i:i+8]) for i in range(0,len(pose),8))
            response = tuple(self.track("assistantWashResponse",f))
        im.alpha_composite(handset_veil(controls,response))
        prism = self.s.get("assistantPrism",{}).get(str(f))
        if prism:
            spectral_rim(im,prism)
        refracted_light = self.s.get("assistantRailRefraction", {}).get(str(f))
        if refracted_light is None and optics and "flare" in optics:
            rail_flare(im,optics["flare"])
        upper_bevel=self.s.get("assistantUpperBevel",{}).get(str(f))
        if upper_bevel:
            register_bevel(im,*upper_bevel)
        side_bevels=self.s.get("assistantSideBevels",{}).get(str(f))
        if side_bevels:
            cross_section = im.transpose(Image.Transpose.TRANSPOSE)
            if "left" in side_bevels:
                register_bevel(cross_section,*side_bevels["left"])
            if "right" in side_bevels:
                cross_section = cross_section.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                register_bevel(cross_section,*side_bevels["right"])
                cross_section = cross_section.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            im.paste(cross_section.transpose(Image.Transpose.TRANSPOSE),(0,0))
        finish = screen.get("islandShade")
        if finish and island is None:
            left,top,right,bottom,pigment,softness = finish
            margin = math.ceil(softness*3)+2
            box = (left-margin,top-margin,right+margin,bottom+margin)
            area = im.crop(box)
            mask = Image.new("L",area.size)
            ImageDraw.Draw(mask).rounded_rectangle(
                (margin,margin,margin+right-left,margin+bottom-top),
                radius=(bottom-top)/2,fill=255,
            )
            coverage = np.asarray(mask.filter(ImageFilter.GaussianBlur(softness)),dtype=float)/255
            rgba = np.array(area)
            adjusted = rgba[:,:,:3]-coverage[...,None]*np.asarray(pigment)
            rgba[:,:,:3] = np.uint8(np.clip(np.rint(adjusted),0,255))
            im.paste(Image.fromarray(rgba),box[:2])
        rim_registration = self.s.get("assistantRimRegistration", {}).get(str(f))
        if rim_registration:
            rgba = np.array(im)
            rails = rgba.transpose(1, 0, 2)
            lanes = {"top": rgba, "left": rails, "right": rails[::-1]}
            for side, width, knots in rim_registration:
                register_handset_edge(lanes[side], knots, width)
            im.paste(Image.fromarray(rgba), (0, 0))
        if refracted_light:
            rail_flare(im, refracted_light)
        crown_light = self.s.get("assistantCrownLight", {}).get(str(f))
        if crown_light:
            spectral_rim(im, crown_light)
        if island:
            paint_camera_island(im, island)
        exit_casing = self.s.get("assistantExitCasing",{}).get(str(f))
        if exit_casing:
            glass_limit=self.s.get("assistantCasingGlass",{}).get(str(f))
            paint_exit_casing(im,exit_casing,glass_limit)
        speaker_slot = self.s.get("assistantSpeakerSlot",{}).get(str(f))
        if speaker_slot:
            paint_speaker_slot(im,speaker_slot)
        screen_refraction = self.s.get("assistantScreenRefraction",{}).get(str(f),{})
        for bounds,settings in screen_refraction.values():
            region=im.crop(bounds).convert("RGB")
            im.paste(refract_control(region,settings),tuple(bounds[:2]))
        caustics = self.s.get("assistantControlCaustics",{}).get(str(f))
        if caustics:
            paint_control_caustics(im,caustics)
        title_y,=self.track("assistantTitleY", f)
        captions = self.s.get("assistantCaptionOptics",{}).get(str(f))
        reveal = self.s.get("assistantCaptionReveal", {}).get(str(f))
        for j,line in enumerate(self.c["assistant"]):
            if reveal and reveal[j]:
                revealed_caption(im,line,reveal[j])
                continue
            if captions:
                left,top,width,height,weight,opacity,sx,sy = captions[j]
                fit_ink(im,line,(left,top,width,height),weight,opacity,(sx,sy),
                        family=messages_font,ink=(8,8,8),fractional=True)
                continue
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
                glyphs = self.s.get("personalGlyphRegistration")
                lettering = glyphs[index] if glyphs else None
                letter_poses = lettering["frames"].get(str(f)) if lettering and caption==lettering["caption"] else None
                if letter_poses:
                    controls = interpolate(layout,f)
                    drawn = iter(letter_poses)
                    for pos,word in enumerate(words):
                        weight = controls[pos*7+4]
                        for char in word:
                            gx,gy,gw,gh,focus,opacity,*stroke = next(drawn)
                            glyph_weight = stroke[0] if stroke else weight
                            fit_ink(title,char,(gx,gy,gw,gh),glyph_weight,min(1,opacity),focus,
                                    family=messages_font,ink=color,fractional=True)
                elif layout and layout[0][0]<=f<=layout[-1][0] and len(layout[0])==1+7*len(words):
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
        poses = self.s.get("titleHeartOptics",{}).get(str(f))
        if poses:
            contours=self.s.get("titleHeartContours",{}).get(str(f),{})
            for index,pose in enumerate(poses):
                title_heart(hearts, pose, contours.get(str(index)))
        else:
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

    def registered_cluster(self, im, frame, samples):
        plate = cluster_surround(self.s["clusterShellContours"][str(frame)])
        for entry,pose,pigment in zip(self.s["cluster"],samples,self.s["clusterDiskColors"],strict=True):
            x,y,width,height,opacity,head = pose
            if opacity<=0:
                continue
            sprite,left,top = registered_portrait(x,y,width,height,pigment,entry[0],head)
            composite(plate,sprite,left,top,opacity)
        softness,=self.track("clusterEarlyBlur",frame)
        smear,=self.track("clusterEarlySmear",frame)
        softness+=3.6*tween(frame,250,253)
        composite(im,vertical_blur(blur(plate,softness),smear),0,0)

    def cluster_entrance(self,im,f):
        registration = self.s.get("clusterDiskContours",{}).get(str(f))
        if registration:
            self.registered_cluster(im,f,registration)
            return
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

    def registered_profiles(self, im, frame, actors, optics=None):
        plate=layer()
        typeface=os.environ.get("SIDEHOE_EMOJI_FONT","/System/Library/Fonts/Apple Color Emoji.ttc")
        emojis={"{boot}":"🥾","{heart}":"💃","{art}":"🖼️"}
        ink_colors=((38,180,44),(142,14,191),(219,144,39))
        for index,(content,pose) in enumerate(zip(self.s["profiles"],actors,strict=True)):
            if pose is None:
                continue
            label,actor,tag,_,_ = content
            asset="lisa-wink" if actor=="lisa" and pose.get("wink",True) else actor
            visibility=pose.get("veil",1)
            head_coverage,side_light,head_wash,disk_wash = pose.get(
                "exposure",(visibility,(1-visibility)*.72 if index==1 else 0,0,0))
            sprite,left,top=registered_portrait(*pose["oval"],pose["tone"][0],asset,pose["head"],
                                                gradient=pose["tone"],head_opacity=head_coverage,
                                                right_fade=side_light,head_wash=head_wash,
                                                disk_wash=disk_wash)
            focus = pose.get("headFocus",0)
            composite(plate,blur(sprite,tuple(focus) if isinstance(focus,list) else focus),
                      left,top,visibility if index==2 and optics else 1)
            label = label[:pose["nameCharacters"]] if "nameCharacters" in pose else label
            if label:
                fit_ink(plate,label,pose["name"],548,opacity=pose.get("nameOpacity",visibility),
                        blur_radius=pose.get("nameFocus",.40),
                        family=messages_font,ink=(3,3,3),fractional=True)
            if not pose.get("chip"):
                continue
            x0,y0,x1,y1=pose["chip"]
            ImageDraw.Draw(plate).rounded_rectangle((x0,y0,x1-1,y1-1),(y1-y0)*.46,
                                                     fill=tuple(pose["chipColor"]))
            outline = pose.get("outline",0)
            if outline:
                rim = layer()
                ImageDraw.Draw(rim).rounded_rectangle((x0,y0,x1-1,y1-1),(y1-y0)*.46,
                                                       outline=(108,240,117,round(outline*245)),
                                                       width=3)
                composite(plate,rim,0,0)
            marker,space,caption=tag.partition(" ")
            if marker in emojis and space:
                if pose.get("glyph"):
                    x,y,w,h=pose["glyph"]
                    glyph=glyph_ink(emojis[marker],round(w),round(h),typeface)
                    composite(plate,blur(glyph,pose.get("chipFocus",0)),x,y,visibility)
                tag=caption
            if "tagCharacters" in pose:
                tag=tag[:pose["tagCharacters"]]
            if tag:
                fit_ink(plate,tag,pose["text"],437,opacity=pose.get("tagOpacity",visibility),
                        blur_radius=pose.get("chipFocus",.35),family=messages_font,
                        ink=ink_colors[index],fractional=True)
        blur_after=tuple(optics) if optics else .5+1.7*tween(frame,283,286)
        composite(im,blur(plate,blur_after),0,0)

    def profiles(self,im,f):
        motion = self.s.get("profileMotionRegistration",{}).get(str(f))
        if motion:
            self.registered_profiles(im,f,motion["actors"],motion["focus"])
            return
        registration = self.s.get("profileRegistrations",{}).get(str(f))
        if registration:
            self.registered_profiles(im,f,registration)
            return
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

    def keyboard(self,im,y,*,home_indicator=True,geometry=None,appearance=None):
        d=ImageDraw.Draw(im)
        tray=tuple(appearance["tray"]) if appearance else "#d7d8de"
        key="#fdfdfd"
        utility="#c8cdd2"
        rows = [(17,y+9,37.1,32,40),(35.5,y+60.3,37.1,32,40),(72.5,y+111.6,37.1,32,40)]
        bottom, utility_height = y+162, 40
        baseline_home = (134,802,266,808)
        if geometry:
            y, rows, bottom, utility_height, baseline_home = geometry
        d.rectangle((10,y,389,817),fill=tray)
        for index,((start,top,pitch,width,height),letters) in enumerate(
                zip(rows,("QWERTYUIOP","ASDFGHJKL","ZXCVBNM"))):
            measured = appearance["rows"][index] if appearance else None
            for column,label in enumerate(letters):
                pose = measured[column] if measured else None
                if pose:
                    (x,y1,right,bottom_edge),ink_box = pose
                    d.rounded_rectangle((x,y1+1.5,right,bottom_edge+2),5.2,fill="#babdc1")
                    d.rounded_rectangle((x,y1,right,bottom_edge),5.2,fill=key)
                    fit_ink(im,label,ink_box,420,1,.16,family=messages_font,
                            ink=(28,28,29),fractional=True)
                else:
                    x=start+column*pitch
                    d.rounded_rectangle((x,top+2,x+width,top+height+3),5.5,fill="#babdc1")
                    d.rounded_rectangle((x,top,x+width,top+height),5.5,fill=key)
                    text(d,x+width/2,top+12,label,20,"#202020",460 if geometry else 500,"center")
        top = rows[2][1] if geometry else y+112
        for x0,x1,label,color in ((17,59,"shift",key),(338,382,"delete",utility)):
            d.rounded_rectangle((x0,top+2,x1,top+43),5.5,fill="#babdc1")
            d.rounded_rectangle((x0,top,x1,top+40),5.5,fill=color)
            keyboard_glyph(d,label,(x0+x1)/2,top+20)
        for a,b,n,col in [(17,106,"123",utility),(110,292,"space",key),(297,382,"Label",utility)]:
            d.rounded_rectangle((a,bottom+2,b,bottom+utility_height+2),5,fill="#babdc1")
            d.rounded_rectangle((a,bottom,b,bottom+utility_height),5,fill=col)
            text(d,(a+b)/2,bottom+12,n,15,INK,500,"center")
        icon_y=clamp(y+247,749,780)
        keyboard_glyph(d,"emoji",53,icon_y)
        microphone(d,348,icon_y,23,"#667076")
        if home_indicator and baseline_home:
            d.rounded_rectangle(baseline_home,3,fill="#202020")

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

    def follow_history(self, im, registration):
        name, outgoing, *incoming = self.c["follow"][:4]
        l,t,r,b = registration["badge"]
        badge_width, badge_height = round(r-l),round(b-t)
        mark=badge(128).resize((badge_width,badge_height),Image.Resampling.LANCZOS)
        composite(im,mark,l,t)
        fit_ink(im,name,registration["name"],480,.94,.22,family=messages_font,ink=(44,44,45))

        (left,top,right,bottom),stops = registration["blue"]
        height=bottom-top
        swatch=layer(im.width,im.height)
        self.bubble(swatch,left,top,right-left-6,height,[],True,True,radius=height*.43)
        rows=np.linspace(top,bottom,len(stops)+2)[1:-1]
        pigments=np.stack([np.interp(np.arange(im.height),rows,c) for c in np.asarray(stops).T],axis=1)
        panel=Image.fromarray(np.uint8(np.rint(pigments))[:,None]).resize(im.size)
        panel.putalpha(swatch.getchannel("A"))
        im.alpha_composite(panel)
        words=[outgoing] if isinstance(outgoing,str) else outgoing
        for i,line in enumerate(words):
            width=min(right-left-34,max(12,len(line)*8))
            appearances = registration.get("blueInkAppearance", ())
            if len(appearances) == len(words):
                look = appearances[i]
                fit_ink(im,line,look["box"],look["weight"],1,look["blur"],
                        family=messages_font,ink=tuple(look["color"]),fractional=True)
            else:
                fit_ink(im,line,(left+14,top+height*.205+i*height*.31,width,height*.24),420,
                        .84,.38,family=messages_font,ink=(253,253,253))
        for index,(caption,(bounds,line_boxes)) in enumerate(zip(incoming,registration["bubbles"])):
            l,t,r,b=bounds
            height=b-t
            captions=[caption] if isinstance(caption,str) else caption
            has_ink_boxes=len(captions)==len(line_boxes)
            fill=(239,239,242) if index==0 else (232,232,235)
            self.bubble(im,l+height*.14,t,r-l-height*.14,height,
                        [] if has_ink_boxes else captions,paint=fill,radius=height*.35)
            if has_ink_boxes:
                ink=(86,86,88) if index==0 else (39,39,41)
                for j,(line,box) in enumerate(zip(captions,line_boxes,strict=True)):
                    look = registration.get("inkAppearance", {}).get(f"{index}:{j}")
                    if look:
                        fit_ink(im,line,look["box"],look["weight"],1,look["blur"],
                                family=messages_font,ink=tuple(look["color"]),fractional=True)
                    else:
                        fit_ink(im,line,box,420 if index==0 else 475,1,.36,
                                family=messages_font,ink=ink)
        fit_ink(im,self.c["today"],registration["today"],420,.94,.28,
                family=messages_font,ink=(111,111,112))

    def thread_plate(self, which, f, keyboard_y, *, history_offset=0, heading_height=None,
                     measured=False, home_indicator=True, follow_registration=None,
                     push_header=None):
        im=layer(400,827)
        radius = follow_registration.get("caseRadius", 65) if follow_registration else 65
        phone_shell(im,400,827,radius)
        # Header is inset within the shell, with an original tinted utility bar.
        d=ImageDraw.Draw(im)
        header_bottom=137 if which=="sofia" else 147
        if heading_height is not None:
            header_bottom=heading_height
        if follow_registration:
            header_bottom=round(follow_registration["headerEnd"])
        if push_header:
            header_bottom = push_header[0]
        d.rounded_rectangle((10,9,389,header_bottom),56,fill="#f0f0f3")
        d.rectangle((10,94,389,header_bottom),fill="#f0f0f3")
        d.line((10,header_bottom,389,header_bottom),fill="#dfdfe1",width=1)
        if follow_registration:
            status(d,400,follow_registration["idY"],self.c["chatStatus"],True,
                   island_bounds=follow_registration["island"])
        else:
            status_y = push_header[1] if push_header else 41
            status(d,400,status_y,self.c["chatStatus"],True)
        header_delta = (follow_registration["badge"][1]+follow_registration["badge"][3])/2-100 if follow_registration else 0
        if push_header:
            header_delta = push_header[2]-100
        d.line((43,82+header_delta,33,92+header_delta,43,102+header_delta),fill="#498af3",width=3)
        d.rounded_rectangle((342,84+header_delta,358,100+header_delta),3,outline="#498af3",width=2)
        d.polygon([(359,92+header_delta),(367,85+header_delta),(367,99+header_delta)],outline="#498af3")
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
        elif follow_registration:
            self.follow_history(im,follow_registration)
        else:
            c=self.c["follow"]
            avatar_y = push_header[2] if push_header else 100
            stamp(im,badge(85),200,avatar_y,45 if push_header else 38)
            text(d,200,avatar_y+26,c[0]+"  ›",11,INK,560,"center")
            if not measured:
                upper_shift,=self.track("followMessageLift",f)
                lower_shift,=self.track("followLowerLift",f)
                middle_shift=(upper_shift+lower_shift)/2
                self.bubble(im,140,173+upper_shift,222,48,c[1],True,True)
                self.bubble(im,42,232+middle_shift,260,48,c[2])
                text(d,200,307+middle_shift,self.c["today"],13,MUTED,500,"center")
                self.bubble(im,47,356+lower_shift,276,67,c[3])
        if not measured:
            if follow_registration:
                composer_geometry = follow_registration.get("composer")
                if composer_geometry:
                    self.staged_composer(im,composer_geometry)
                else:
                    self.composer(im,follow_registration["composerY"],settled=True)
            else:
                self.composer(im,keyboard_y-41,settled=which=="sofia" and 340<=f<=355)
            geometry=follow_registration["layout"] if follow_registration else None
            keyboard_style = follow_registration.get("keyboardAppearance") if follow_registration else None
            self.keyboard(im,keyboard_y,home_indicator=home_indicator,geometry=geometry,appearance=keyboard_style)
        # The white screen and keyboard share the same curved bottom mask.
        mask=Image.new("L",im.size)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,399,826),radius,fill=255)
        im.putalpha(mask)
        im.alpha_composite(rim_only(400,827,radius))
        return im

    def staged_composer(self, surface, geometry):
        left,top,right,bottom = geometry["outline"]
        cx,cy,radius = geometry["plus"]
        mx,my,unit = geometry["microphone"]
        # Draw the glass outline and controls together at subpixel precision.
        x0,y0 = math.floor(cx-radius)-3,math.floor(top)-3
        w,h = math.ceil(right)-x0+4,math.ceil(bottom)-y0+4
        scale = 3
        chrome = layer(w*scale,h*scale)
        draw = ImageDraw.Draw(chrome)
        def box(x,y,x1,y1):
            return ((x-x0)*scale,(y-y0)*scale,(x1-x0)*scale,(y1-y0)*scale)
        draw.rounded_rectangle(box(left,top,right,bottom),(bottom-top)*scale/2,
                               outline=(192,192,192),width=round(geometry.get("stroke",2.15)*scale))
        draw.ellipse(box(cx-radius,cy-radius,cx+radius,cy+radius),fill=(232,233,235))
        extent=radius*.40
        for line in ((cx-extent,cy,cx+extent,cy),(cx,cy-extent,cx,cy+extent)):
            draw.line(box(*line),fill=(130,136,140),width=round(radius*.09*scale))
        ink=(172,181,184)
        draw.rounded_rectangle(box(mx-4*unit,my-10*unit,mx+4*unit,my+8*unit),
                               radius=4*unit*scale,fill=ink)
        draw.arc(box(mx-10*unit,my-5*unit,mx+10*unit,my+13*unit),0,180,
                 fill=ink,width=round(2.1*unit*scale))
        draw.line(box(mx,my+13*unit,mx,my+16*unit),fill=ink,width=round(2.1*unit*scale))
        draw.line(box(mx-6*unit,my+16*unit,mx+6*unit,my+16*unit),fill=ink,
                  width=round(2.1*unit*scale))
        composite(surface,chrome.resize((w,h),Image.Resampling.LANCZOS),x0,y0)
        fit_ink(surface,self.c["keyboardPrompt"],geometry["text"],370,1,.3,
                family=messages_font,ink=(182,182,182),fractional=True)

    def staged_thread(self, im, which, registration, frame, *, handset_mask=None):
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
            gradient = registration.get("blueGradient")
            if gradient:
                stops = np.asarray(gradient)
                top, bottom = max(0, math.floor(y0)-3), min(SIZE, math.ceil(y1)+4)
                start, end = max(0, math.floor(x0)-3), min(SIZE, math.ceil(x1)+20)
                rows = np.arange(top,bottom)
                colors = np.stack([np.interp(rows,stops[:,0],c) for c in stops[:,1:].T],axis=1)
                plate = Image.fromarray(np.uint8(np.rint(colors))[:,None]).resize((end-start,bottom-top))
                mask = upper.getchannel("A").crop((start,top,end,bottom))
                plate.putalpha(mask)
                upper.paste(plate,(start,top))
            words=copy[1] if isinstance(copy[1],list) else [copy[1]]
            for i,line in enumerate(words):
                bx = x0+18 if follow else x0+h*.43
                by = y0+h*(.20+.37*i) if follow else y0+h*.33
                width=min(x1-bx-15,len(line)*h*(.250 if follow else .193))
                ink_box = registration.get("blueInk") if len(words)==1 else None
                appearances = registration.get("blueInkAppearance", ())
                if len(appearances) == len(words):
                    appearance = appearances[i]
                    fit_ink(upper,line,appearance["box"],appearance["weight"],1,
                            appearance["blur"],family=messages_font,
                            ink=tuple(appearance["color"]),fractional=True)
                else:
                    fit_ink(upper,line,ink_box or (bx,by,width,h*(.24 if follow else .32)),
                            420,.86,.6,family=messages_font,ink=(254,254,254))
            if follow and not gradient:
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
            if "bubbleFill" in registration:
                background = tuple(registration["bubbleFill"][i])
            words=copy[i+2]
            if isinstance(words,str):
                words=[words]
            fit=len(words)==len(lines)
            self.bubble(surface,left+tail,top,right-left-tail-1,height-1,[] if fit else words,
                        text_size=height*.43,paint=background,
                        radius=registration["corners"][i])
            appearances = registration.get("inkAppearance", {})
            for j,(word,ink) in enumerate(zip(words,lines) if fit else ()):
                appearance = appearances.get(f"{i}:{j}")
                if appearance:
                    registered_message_ink(surface,word,appearance)
                else:
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
            hardware = registration.get("railHardware")
            if hardware:
                rows_in_stage = np.arange(SIZE)
                for first,last,feather,shade in hardware[index]:
                    strength = np.interp(rows_in_stage,
                        (first-feather,first+feather,last-feather,last+feather),(0,1,1,0))
                    rgb += strength[:,None,None]*np.asarray(shade)[None,:,None]
            upper_limit = registration.get("railStart",0)
            rail = Image.fromarray(np.uint8(np.clip(np.rint(rgb[upper_limit:]),0,255)))
            ramp = registration.get("railBlend")
            span = registration.get("railSpan")
            if span:
                fade = np.interp(np.arange(upper_limit,SIZE),span,(0,255,255,0)).astype(np.uint8)
                mask = Image.fromarray(np.broadcast_to(fade[:,None],(rail.height,rail.width)))
                im.paste(rail,(start,upper_limit),mask)
            elif ramp:
                fade = np.interp(np.arange(upper_limit,SIZE),ramp,(0,255)).astype(np.uint8)
                mask = Image.fromarray(np.broadcast_to(fade[:,None],(rail.height,rail.width)))
                im.paste(rail,(start,upper_limit),mask)
            else:
                im.paste(rail,(start,upper_limit))
        zoom=(r-l)/376
        d=ImageDraw.Draw(surface)
        d.rectangle((l,top,r-1,SIZE),fill=tuple(tray))
        composer = registration.get("composer")
        if composer:
            self.staged_composer(surface,composer)
        else:
            composer_y=top-41*zoom
            prompt=layer(400,45)
            self.composer(prompt,3,settled=True)
            composite(surface,prompt,l-10*zoom,composer_y-3*zoom,1,zoom)
        d=ImageDraw.Draw(surface)
        key_poses = registration.get("keyPoses", ())
        key_ink=registration.get("keyInkRegistration",())
        exposed_keys=[]
        for row_index,((x,y,pitch,w,h,_),letters) in enumerate(
                zip(rows,("QWERTYUIOP","ASDFGHJKL","ZXCVBNM"))):
            poses = key_poses[row_index] if row_index < len(key_poses) else None
            ink_row=key_ink[row_index] if row_index<len(key_ink) else ()
            for j,letter in enumerate(letters):
                exposed=ink_row[j] if j<len(ink_row) else None
                if exposed:
                    exposed_keys.append((letter,exposed))
                if poses and poses[j]:
                    (kx,ky,end_x,end_y),ink_box = poses[j]
                    radius=(end_x-kx)*.111
                    d.rounded_rectangle((kx,ky+1,end_x,end_y+2),radius,fill="#b9bcc3")
                    d.rounded_rectangle((kx,ky,end_x,end_y),radius,fill="#fdfdfd")
                    if exposed is None:
                        fit_ink(surface,letter,ink_box,435,1,.15,
                                family=messages_font,ink=(30,30,30),fractional=True)
                else:
                    key_x = x+j*pitch
                    d.rounded_rectangle((key_x,y+1,key_x+w,y+h+2),w*.114,fill="#b9bcc3")
                    d.rounded_rectangle((key_x,y,key_x+w,y+h-1),w*.112,fill="#fdfdfd")
                    if exposed is None:
                        d.text((key_x+w/2,y+h*.29),letter,font=messages_font(h*.57,420),
                               fill="#1f1f1f",anchor="mt")
            if letters=="ZXCVBNM":
                for key_x,key_w,name,tone in ((l+4,1.20*w,"shift","#fafafa"),
                                               (r-1.22*w-6,1.22*w,"delete","#c4cbd1")):
                    d.rounded_rectangle((key_x,y,key_x+key_w,y+h-1),w*.105,fill=tone)
                    glyph=layer(36,36)
                    keyboard_glyph(ImageDraw.Draw(glyph),name,18,18)
                    composite(surface,glyph,key_x+key_w/2-18*zoom,y+h/2-18*zoom,1,zoom)
        bottom,utility_height=registration.get("utilityRow",(top+161*zoom,40*zoom))
        if bottom<SIZE:
            for start,end,caption,background in ((17,106,"123","#c8cdd2"),
                                                  (110,292,"space","#fdfdfd"),
                                                  (297,382,"Label","#c8cdd2")):
                x1,x2 = l+(start-10)*zoom,l+(end-10)*zoom
                d.rounded_rectangle((x1,bottom,x2,bottom+utility_height),5.2*zoom,fill=background)
                d.text(((x1+x2)/2,bottom+12*zoom),caption,font=messages_font(15*zoom,425),
                       fill=INK,anchor="mt")
        footer = registration.get("keyboardFooter")
        if footer:
            icon_y,home_indicator = footer
            glyph = layer(40,40)
            keyboard_glyph(ImageDraw.Draw(glyph),"emoji",20,20)
            composite(surface,glyph,l+48*zoom-20*zoom,icon_y-20*zoom,1,zoom*.74)
            microphone(d,r-39*zoom,icon_y,21*zoom,"#667076")
            if home_indicator:
                d.rounded_rectangle(home_indicator,4,fill="#252526")
        if follow:
            softness=.78+1.7*tween(frame,688,694)+max(0, (672-frame)*.48)
        else:
            softness=1.14+.29*min(1,abs(frame-348)/5)
            if frame>=352:
                softness = 1.25+1.1*(frame-352)
        if "focus" in registration:
            sweep_x,sweep_y,softness=registration["focus"]
            surface=vertical_blur(surface,sweep_y,horizontal=sweep_x)
        exposure = blur(surface,(softness*.85,softness))
        for letter,geometry in exposed_keys:
            exposed_key_ink(exposure,letter,geometry)
        if handset_mask is not None:
            exposure.putalpha(ImageChops.multiply(exposure.getchannel("A"),handset_mask))
        composite(im,exposure,0,0)

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

    def sofia_entrance_plate(self, f, keyboard_y, history, heading, opacity, home_indicator):
        body=self.thread_plate("sofia",f,keyboard_y,history_offset=history,heading_height=heading,
                               home_indicator=home_indicator)
        reply=layer(body.width,body.height)
        self.bubble(reply,227,366,132,32,self.c["sofia"][4],True,paint="#13c4fa")
        composite(body,reply,0,0,opacity)
        return body

    def render_home_indicator(self, im, frame, track):
        cx,cy,width,height,focus,saturation=interpolate(track,frame)
        margin=math.ceil(4*focus)+4
        h=math.ceil(height)
        line=layer(round(width)+4,h+2*margin)
        box=(2,margin,round(width)+1,margin+h-1)
        ImageDraw.Draw(line).rounded_rectangle(box,height/2,fill="#060606")
        composite(im,blur(line,(.8,focus)),cx-line.width/2,cy-line.height/2,
                  min(1,saturation/215))

    def sofia_pullback(self, im, frame, optics, x, y, scale, keyboard_y):
        plate = self.thread_plate("sofia", frame, keyboard_y)
        inside = Image.new("L", plate.size)
        ImageDraw.Draw(inside).rounded_rectangle((14,14,385,812),52,fill=255)
        plate.putalpha(inside)

        # The outgoing screen appears in two exposure planes. Leave room
        # for off-screen motion to contribute to the first visible rows.
        margin = 76
        plate = plate.resize((round(plate.width*scale),round(plate.height*scale)),
                             Image.Resampling.BICUBIC)
        stage_height = SIZE+2*margin
        rows = np.arange(plate.height) + y
        upper = np.interp(rows,[550,705],[1,0])
        for key, coverage in (("history",upper),("composerAndKeyboard",1-upper)):
            dx,dy,shutter_x,shutter_y,opacity,focus = optics[key]
            if opacity <= 0:
                continue
            surface = layer(stage_height,stage_height)
            exposure = plate.copy()
            mask = np.asarray(exposure.getchannel("A"),dtype=np.float32)
            exposure.putalpha(Image.fromarray(np.uint8(np.rint(mask*coverage[:,None]))))
            composite(surface,exposure,x+margin+dx,y+margin+dy)
            surface = blur(vertical_blur(surface,shutter_y,horizontal=shutter_x),focus)
            composite(im,surface.crop((margin,margin,margin+SIZE,margin+SIZE)),0,0,opacity)

        # The right bevel catches light after the screen slips out of view.
        for key in ("rail","leftRim"):
            if key not in optics:
                continue
            stops = np.asarray(optics[key],dtype=float)
            left,right = int(stops[0,0]),int(stops[-1,0])+1
            levels = np.interp(np.arange(left,right),stops[:,0],stops[:,1])
            shade = np.broadcast_to(levels,(SIZE,right-left))
            hardware = Image.fromarray(np.uint8(np.rint(shade)))
            im.paste(hardware.convert("RGB"),(left,0))

    def sofia(self,im,f):
        x,y,s=self.track("sofiaMeasuredCamera",f)
        keyboard_y,=self.track("sofiaKeyboardY",f)
        a, rail = self.track("sofiaRelease",f)
        onset=self.at("sofia.suggestion")
        registration = self.s["tracks"].get("sofiaPlateRegistration")
        history, heading, sweep_x, sweep_y = 0, None, 0, 0
        if registration and registration[0][0]<=f<=registration[-1][0]:
            history, heading, sweep_x, sweep_y=interpolate(registration,f)
        home_track = self.s["tracks"].get("sofiaHomeIndicator")
        registered_home = home_track and home_track[0][0]<=f<=home_track[-1][0]
        optics = self.s.get("sofiaEarlyOptics",{}).get(str(f))
        measured = self.s.get("threadRegistration",{}).get("sofia",{}).get(str(f))
        if optics and not measured:
            dx,dy,sx,sy,soft_x,soft_y,opacity,*bevel = optics
            body=self.sofia_entrance_plate(f,keyboard_y,history,heading,opacity,not registered_home)
            body=entrance_casing(body,*bevel)
            exposed,x0,y0=exposed_entry_plate(body,x+dx,y+dy,s*sx,s*sy,soft_x,soft_y)
            composite(im,exposed,x0,y0,a)
            if registered_home:
                self.render_home_indicator(im,f,home_track)
            return
        pullback = self.s.get("sofiaPullbackOptics",{}).get(str(f))
        if pullback:
            self.sofia_pullback(im,f,pullback,x,y,s,keyboard_y)
        elif measured and "casing" in measured:
            case_x,case_y,scale,heading,trail,focus = measured["casing"]
            plate=self.thread_plate("sofia",f,keyboard_y,heading_height=heading,measured=True)
            aspect = measured.get("casingAspect", 1)
            width,height=round(plate.width*scale),round(plate.height*scale*aspect)
            glass=Image.new("L",plate.size)
            ImageDraw.Draw(glass).rounded_rectangle((13,12,386,812),radius=50,fill=255)
            handset=Image.new("L",(SIZE,SIZE))
            handset.paste(glass.resize((width,height),Image.Resampling.BICUBIC),
                          (round(case_x),round(case_y)))
            self.expose_phone(im,plate,case_x,case_y,scale,trail,focus,a,vertical_scale=aspect)
            self.staged_thread(im,"sofia",measured,f,handset_mask=handset)
        elif a>0:
            plate=self.thread_plate("sofia",f,keyboard_y,history_offset=history,
                                    heading_height=heading,measured=bool(measured),
                                    home_indicator=not registered_home)
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
        if registered_home:
            self.render_home_indicator(im,f,home_track)
        if f<onset and measured and "earlierReply" in measured:
            reply=layer()
            (left,top,right,bottom),ink=measured["earlierReply"]
            height=bottom-top
            caption=self.c["sofia"][4]
            editable=isinstance(caption,str)
            self.bubble(reply,left,top,right-left-5,height,[] if editable else caption,
                        True,text_size=height*.44,paint="#13c4fa")
            if editable:
                fit_ink(reply,caption,ink,410,blur_radius=.25,family=messages_font,
                        ink=(251,254,255))
            horizontal,vertical,focus=measured["focus"]
            reply=vertical_blur(reply,vertical,horizontal=horizontal)
            composite(im,blur(reply,focus),0,0)
        elif f<onset:
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
                lettering = self.s["tracks"]["sendControlInk"]
                ink_boxes = interpolate(lettering,f)
                palettes = (("#c9c9c9","#c9c9c9"),("#ecaafa","#afe2fc"))
                for index,(label,gradient) in enumerate(zip(c[7:9],palettes,strict=True)):
                    x0,y0,w,h = boxes[index*4:index*4+4]
                    face = rounded_gradient(round(w),round(h),*gradient,round(h*.23),"x")
                    fit_ink(face,label,ink_boxes[index*4:index*4+4],
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
            surfaces = self.s.get("sofiaSuggestionRegistration",{}).get(str(f),{})
            reply_pose = self.track("sofiaEarlierReplyBounds",f)
            left,top,width,height=self.track("sofiaSuggestedBounds",f)
            if settled and surfaces.get("messages"):
                for pose, colors in surfaces["messages"]:
                    paint_message_surface(incoming,pose,colors)
            else:
                x0,y0,w0,h0 = reply_pose
                self.bubble(incoming,x0,y0,w0-6,h0,[] if settled else c[4],True,
                            text_size=h0*.53,paint="#13c4fa")
                self.bubble(incoming,left,top,width-6,height,[] if settled else c[6],True,
                            text_size=height*.315,text_inset=height*.30,paint="#0fc4f9")
            if settled:
                ink_boxes = interpolate(settle, f)
                captions = [c[4], *c[6], c[5]]
                for index, caption in enumerate(captions):
                    measured_ink = surfaces.get("ink", {}).get(str(index))
                    if measured_ink:
                        registered_message_ink(incoming,caption,measured_ink)
                    else:
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
                        control = surfaces.get("controls", {}).get(str(index))
                        if control:
                            shape, gradient, ink = control
                            paint_message_surface(incoming,shape,gradient)
                            fit_ink(incoming,label,ink["box"],ink["weight"],
                                    blur_radius=ink["blur"],family=messages_font,
                                    ink=tuple(ink["color"]),fractional=True)
                        else:
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
            focus = surfaces.get("focus", 1.5*launch+3.5*detach)
            composite(im,blur(incoming,focus),0,0,.92+.08*(1-launch))
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
        departure = self.s.get("calendarDeparture", {}).get(str(f))
        if departure:
            left,y0,h,right,day_x,day_y = departure["camera"]
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
            spans = departure["gridSegments"].get(str(j), ((left,right),)) if departure else ((left,right),)
            rule = tuple(departure["line"]) if departure else "#d5d2dc"
            for start,end in spans:
                d.line((start,y,end,y),fill=rule,width=2)
            if not departure or j in departure["ticks"]:
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
            if departure:
                top,bottom = departure["bars"][index]
                if "appointmentPaint" in departure:
                    fill, opacity = departure["appointmentPaint"][index]
                else:
                    fill, opacity = ("#d4f0fc","#e0cffb")[index],255
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
        if departure:
            if departure["cursor"]:
                tip_x,tip_y,angle,scale,opacity,sx,sy = departure["cursor"]
                cursor(cal,tip_x,tip_y,angle,opacity,scale,softness=(sx,sy))
            for bounds in departure["removed"]:
                d.rectangle(bounds,fill=(0,0,0,0))
            composite(im,blur(cal,tuple(departure["focus"])),0,0)
            return
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
        arrival = self.s.get("orbitArrivalExposure",{}).get(str(f),{})
        registrations=self.s.get("orbitActorFit",{}).get(str(f),{})
        for _,depth,name,x,y,size,alpha in sorted(nodes):
            ox=app_icon(name)
            softness=1.7+(1-depth)*2.9+4*(1-tween(f,478,486))
            if name in arrival:
                x,y,size,alpha,softness = arrival[name]
            vertical = 84*tween(f,616,621)
            if name == "blue":
                dy, coverage, blend, smear, height_ratio = self.track("calendarTileTreatment", f)
                y += dy
                alpha *= coverage
                if blend:
                    finish = self.s["tracks"].get("calendarTileFinish")
                    strength = interpolate(finish,f)[0] if finish else 0
                    details = self.s.get("calendarTileProfiles", {}).get(str(f))
                    detail, defocus = details if details else (0, 1)
                    softness *= defocus
                    ink_pose = self.s.get("calendarNumeralRegistration", {}).get(str(f))
                    finish_lift = self.s.get("calendarFinishExposure", {}).get(str(f), 0)
                    face = calendar_face(round(strength,3), detail, tuple(ink_pose) if ink_pose else None,
                                         finish_lift)
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
            pose=registrations.get(name)
            y_scale=1
            if pose:
                dx,dy,wide,high,focus,coverage=pose
                x+=dx
                y+=dy
                size*=wide
                y_scale=high/wide
                softness*=focus
                alpha=min(1,alpha*coverage)
            # Let the softened silhouette extend beyond the asset's square.
            pad=math.ceil(softness*3)
            pad_y=pad+math.ceil(vertical/2)
            exposed=layer(ox.width+2*pad,ox.height+2*pad_y)
            exposed.alpha_composite(ox,(pad,pad_y))
            exposed=vertical_blur(blur(exposed,softness),vertical)
            frame_scale=size/ox.width
            if y_scale!=1:
                exposed=exposed.resize((exposed.width,max(1,round(exposed.height*y_scale))),
                                       Image.Resampling.BICUBIC)
            composite(im,exposed,x-(128+pad)*frame_scale,y-(128+pad_y)*frame_scale*y_scale,alpha,frame_scale)

    def staged_follow_controls(self, im, controls, frame, opacities):
        # Response chips share the screen exposure. The pointer remains above the glass.
        for index,(spec,opacity) in enumerate(zip(controls,opacities,strict=True)):
            if not spec or opacity<=0:
                continue
            left,top,right,bottom = spec["box"]
            w,h = right-left+1,bottom-top+1
            a,b = ("#%02x%02x%02x" % tuple(rgb) for rgb in spec["gradient"])
            pad = 4
            chip = layer(w+2*pad,h+2*pad)
            chip.alpha_composite(rounded_gradient(w,h,a,b,h*.235,"x"),(pad,pad))
            label = self.c["follow"][4+index]
            words,marker,emoji_name = label.rpartition(" {")
            if marker and words and emoji_name.endswith("}") and "{" not in words:
                x,y,width,height = spec["label"]
                fit_ink(chip,words,(x-left+pad,y-top+pad,width,height),415,1,.36,
                        family=messages_font,ink=(spec["ink"],)*3,fractional=True)
                d=ImageDraw.Draw(chip)
                x,y,width,height = spec["emoji"]
                name=emoji_name[:-1]
                asset=self.s["finish"]["glyphs"].get(name)
                if asset:
                    font_file = os.environ.get("SIDEHOE_EMOJI_FONT", "/System/Library/Fonts/Apple Color Emoji.ttc")
                    calendar_emoji(d,asset["unicode"],x-left+pad,y-top+pad,1,(0,0,width,height),font_file)
                else:
                    self.source_glyph(frame,d,name,x-left+pad+width/2,y-top+pad+height/2,width)
            else:
                text(ImageDraw.Draw(chip),pad+w/2,pad+h*.23,label,h*.61,INK,410,"center",
                     glyph=lambda *args:self.source_glyph(frame,*args))
            composite(im,blur(chip,spec.get("focus",.62)),left-pad,top-pad,opacity)

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
        follow_registration=self.s.get("followSettledRegistration",{}).get(str(f))
        if follow_registration and "camera" in follow_registration:
            x,y,s,aspect = follow_registration["camera"]
        push_camera = measured.get("pushCamera") if measured else None
        case_offset = 0
        if push_camera:
            camera_y,push_header = push_camera
            case_offset = camera_y-y
            y = camera_y
        else:
            push_header = None
        plate=self.thread_plate("follow",f,keyboard_y,measured=bool(measured),
                               follow_registration=follow_registration,push_header=push_header)
        handset_mask = None
        if push_camera:
            handset_mask=Image.new("L",(SIZE,SIZE))
            width,height=round(plate.width*s),round(plate.height*s*aspect)
            handset_mask.paste(plate.getchannel("A").resize((width,height),Image.Resampling.BICUBIC),
                               (round(x),round(y)))
        if follow_registration and follow_registration["coverage"]<1:
            plate=Image.blend(self.thread_plate("follow",f,keyboard_y),plate,
                              follow_registration["coverage"])
        no_frame=self.at("follow.no")
        yes_frame=self.at("follow.yes")
        a=mix(.79,1,tween(f,no_frame,653)) if f>=no_frame else 0
        b=mix(.72,1,tween(f,yes_frame,654)) if f>=yes_frame else 0
        tapped=tween(f,self.at("follow.yes-feedback")-1,690)
        chip_shift,=self.track("followChipOffset",f)
        chip_shift -= case_offset/s
        def face(draw, name, x, y, size):
            x_shift = 2.4 if name == "tongue" else 0
            self.source_glyph(f, draw, name, x+x_shift, y-2.6, size*.97)
        no_x,no_y,no_w,no_h = 45,433+chip_shift,72,29
        release = measured if measured and "header" in measured else None
        hold_controls = measured.get("holdControls") if measured else None
        reveal_controls = follow_registration.get("controls") if follow_registration else None
        if measured and measured["no"]:
            lx,ty,rx,by=measured["no"]
            no_x,no_y=(lx-x)/s,(ty-y)/s
            no_w,no_h=min(75,round((rx-lx)/s)),round((by-ty)/s)
        if not release and not hold_controls and not reveal_controls:
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
        if not release and not hold_controls and not reveal_controls:
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
        optical = follow_registration.get("preContactExposure") if follow_registration else None
        if optical:
            trail, softness_x, softness_y = optical
            softness = (softness_x, softness_y)
        entry = self.s.get("followEntryOptics",{}).get(str(f))
        if entry:
            aspect,casing_trail,casing_focus,screen_trail,screen_focus = entry
            casing = layer(plate.width,plate.height)
            phone_shell(casing,plate.width,plate.height,65)
            glass = Image.new("L",plate.size)
            ImageDraw.Draw(glass).rounded_rectangle((12,10,387,814),radius=54,fill=255)
            plate.putalpha(ImageChops.multiply(plate.getchannel("A"),glass))
            self.expose_phone(im,casing,exposure_x,y,s,casing_trail,
                              casing_focus,vertical_scale=aspect)
            self.expose_phone(im,plate,exposure_x,y,s,screen_trail,
                              screen_focus,vertical_scale=aspect)
        else:
            self.expose_phone(im,plate,exposure_x,y,s,trail*(1-.32*tween(f,625,630)),
                              softness,vertical_scale=aspect)
        bevel_lighting = follow_registration.get("bevelLighting") if follow_registration else None
        if bevel_lighting:
            paint_settled_bevels(im,bevel_lighting)
        if reveal_controls:
            self.staged_follow_controls(im,reveal_controls,f,(f>=no_frame,f>=yes_frame))
        if release:
            bottom,cx,cy,w,h,focus = release["header"]
            header=layer()
            rail_left,rail_right = release["rails"]
            ImageDraw.Draw(header).rectangle((rail_left,0,rail_right,bottom),fill="#f0f0f2")
            if f==695:
                d=ImageDraw.Draw(header)
                d.line((271,43,260,52,271,61),fill="#559cf5",width=4)
                d.rounded_rectangle((727,45,742,59),3,outline="#6fa1f0",width=2)
                d.polygon([(743,51),(751,45),(751,58)],outline="#6fa1f0")
            title = release.get("headerInk", (487,80,35,11,510) if f == 695 else None)
            if title:
                fit_ink(header,self.c["follow"][0],title[:4],title[4],
                        family=messages_font,ink=(41,41,42),fractional=True)
            badge_trail = release.get("headerBadgeTrail")
            if badge_trail:
                mark=layer()
                fitted_badge(mark,(cx,cy,w,h),128,opacity=1)
                length,shift=badge_trail
                trail=vertical_blur(mark,length)
                composite(header,trail,0,shift)
            else:
                fitted_badge(header,(cx,cy,w,h),128,opacity=1)
            composite(im,blur(header,focus),0,0)
        if measured:
            self.staged_thread(im,"follow",measured,f,handset_mask=handset_mask)
            if hold_controls:
                self.staged_follow_controls(im,hold_controls,f,(a,b))
            if release:
                controls=layer()
                for j,(cx,cy,w,h) in enumerate(release["controls"]):
                    self.chip(controls,cx,cy,w,h,self.c["follow"][j+4],bool(j),1,
                              1 if j==0 else .87,tapped,
                              glyph=face,follow_style=True)
                composite(im,blur(controls,release["controlFocus"]),0,0)
            if tapped and not hold_controls:
                center_x=x+(left+width*.77)*s
                center_y=y+(top+height*.50)*s
                fx,fy=max(0,round(center_x-80)),max(0,round(center_y-75))
                yf,xf=np.mgrid[fy:fy+151,fx:fx+161]
                alpha=np.exp(-((xf-center_x)/48)**2-((yf-center_y)/47)**2)*tapped
                light=Image.new("RGBA",(161,151),(250,233,255))
                light.putalpha(Image.fromarray(np.uint8(np.rint(alpha*63))))
                composite(im,light,fx,fy,release["controlLight"] if release else 1)

        camera_warp = self.s.get("followCameraWarp",{}).get(str(f))
        if camera_warp:
            warp_handset(im,camera_warp)
        # The measured cursor departs on its own track as the handset withdraws.
        optics = self.s.get("followPointerOptics",{}).get(str(f))
        if optics:
            x,y,w,h,soft_x,soft_y,opacity,lean = optics
            follow_pointer(im,x,y,w,h,soft_x,opacity,lean=lean,
                           vertical_softness=soft_y,rounded=True,
                           contour=self.s.get("followPointerContour",{}).get(str(f)))
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
        focus = max(.36 if finish else 0,5*(1-tween(f,696,704)))
        optics = self.s["tracks"].get("closingBadgeOptics")
        if optics and optics[0][0]<=f<=optics[-1][0]:
            dx,dy,sx,sy,radius = interpolate(optics,f)
            x,y,w,h = box
            box = x+dx,y+dy,w*sx,h*sy
            focus = math.hypot(focus,radius)
        motif_track = self.s["tracks"].get("closingMotifFit")
        motif_fit = interpolate(motif_track,f)[0] if motif_track else 0
        raster_width = self.s.get("closingBadgeRasterWidth", {}).get(str(f), 256)
        artwork=self.s.get("closingBadgeArtwork",{}).get(str(f))
        if artwork:
            artwork=tuple(tuple(part) for part in artwork)
        fitted_badge(im,box,corner,focus,1,shine,closing_finish=finish,motif_fit=motif_fit,
                     raster_width=raster_width,
                     outline=self.s.get("closingBadgeOutline",{}).get(str(f)),
                     part_poses=artwork or ())
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
                appearance = self.s.get("closingInkAppearance", {}).get(word_id)
                if appearance:
                    box = tuple(origin+offset for origin,offset in
                                zip((x,y,w,h),appearance["offset"],strict=True))
                    focus = math.hypot(appearance["blur"],2.3*(1-opacity))
                    fit_ink(im,word,box,appearance["weight"],opacity,focus,
                            family=messages_font,ink=(4,4,4),fractional=True)
                else:
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
        departing = self.s.get("calendarDeparture",{}).get(str(f))
        foreground = departing.get("tileOcclusion") if departing else None
        if 397<=f<482:
            if foreground:
                remaining = layer()
                self.calendar(remaining,f)
                composite(im,remaining,0,0)
            else:
                self.calendar(im,f)
        if 478<=f<622:
            self.apps(im,f)
            if foreground:
                left,top,right,bottom,coverage = foreground
                composite(im,remaining.crop((left,top,right,bottom)),left,top,coverage)
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
