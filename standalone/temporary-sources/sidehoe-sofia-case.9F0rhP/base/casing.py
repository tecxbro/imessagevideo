"""Editable fit of the curved handset shell and its cross-section lighting."""
import numpy as np
from PIL import Image


def shoulder_distance(columns, rows, outline):
    """Approximate inward normal distance to a rounded rectangle open at its foot."""
    center, top, width, radius_x, radius_y = outline
    x = np.abs(columns - center) - (width / 2 - radius_x)
    y = top + radius_y - rows
    u = np.maximum(x / radius_x, 0)
    v = np.maximum(y / radius_y, 0)
    length = np.hypot(u, v)
    slope = np.hypot(u / radius_x, v / radius_y) / np.maximum(length, 1e-6)
    inside = np.minimum(radius_x - x, radius_y - y)
    return np.where(length > 1e-6, (1 - length) / np.maximum(slope, 1e-6), inside)


def casing_coordinates(columns, rows, outer, glass):
    outside = shoulder_distance(columns, rows, outer)
    inside = shoulder_distance(columns, rows, glass)
    depth = outside / np.maximum(5, outside - inside)
    center, top, width, radius_x, radius_y = outer
    lateral = (columns - center) / (width / 2)
    along = np.clip(lateral, -1, 1)
    return depth, along


def paint_exit_casing(stage, settings, glass_limit=None):
    """Replace the casing in a narrow band and retain the live glass content."""
    outer, glass, depth_stops, light_stops, lighting, span = settings
    top, solid_end, bottom = span
    y, x = np.ogrid[top:bottom, :stage.width]
    depth, along = casing_coordinates(x + .5, y + .5, outer, glass)
    patch = np.array(stage.crop((0, top, stage.width, bottom)))
    colors = np.asarray(lighting)
    right = np.clip(np.searchsorted(light_stops, along, side='right'), 1, len(light_stops)-1)
    left = right - 1
    anchors = np.asarray(light_stops)
    ratio = (along - anchors[left]) / (anchors[right] - anchors[left])
    material = np.zeros((*depth.shape, 3), dtype=float)
    for i in range(len(light_stops)):
        weight = np.where(left == i, 1-ratio, 0) + np.where(right == i, ratio, 0)
        for channel in range(3):
            ramp = np.interp(depth, depth_stops, colors[i, :, channel])
            material[:, :, channel] += ramp * weight
    inner=1.77
    if glass_limit is not None:
        # Preserve the clear central glass above the camera island.
        cutoff, half_width, softness=glass_limit
        window=np.clip((half_width-abs(along))/softness,0,1)
        inner=1.77-(1.77-cutoff)*window
    edge = np.clip((depth+.88)/.54, 0, 1) * np.clip((inner-depth)/.49, 0, 1)
    coverage = edge * np.clip((bottom-y)/(bottom-solid_end), 0, 1)
    rgb = patch[:, :, :3]
    rgb[:] = np.uint8(np.clip(np.rint(rgb + (material-rgb)*coverage[..., None]), 0, 255))
    stage.paste(Image.fromarray(patch), (0, top))


def speaker_slot_basis(columns, rows, geometry):
    """Two light lobes describe the machined slot and its illuminated edge."""
    center_x, center_y, half_width, half_height, feather = geometry
    x = np.abs(columns-center_x)
    y = rows-center_y
    rounded_tip = np.maximum(x-half_width+10,0)/10
    across = np.clip((half_width-x-feather*rounded_tip**2)/feather,0,1)
    across = across*across*(3-2*across)
    interior = np.exp(-((y+half_height*.49)/(half_height*.91))**2)
    highlight = np.exp(-((y-half_height*.68)/(half_height*.59))**2)
    return np.stack(np.broadcast_arrays(across*interior,across*highlight),axis=-1)


def paint_speaker_slot(stage, settings):
    """Apply editable slot shading on top of the polished handset casing."""
    bounds, geometry, colors = settings
    left,top,right,bottom = bounds
    x = np.arange(left,right)[None,:]+.5
    y = np.arange(top,bottom)[:,None]+.5
    rgb = np.array(stage.crop(bounds),dtype=np.float32)
    rgb[:,:,:3] += speaker_slot_basis(x,y,geometry) @ np.asarray(colors)
    stage.paste(Image.fromarray(np.uint8(np.clip(np.rint(rgb),0,255))),(left,top))
