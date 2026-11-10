"""Exact source card positions: white top edge, blue controls and photo profile."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.fft import rfft, irfft, next_fast_len
from scipy import ndimage

p = Path(__file__).parent
decoded = p / 'measurements-v8/decoded'
fps = 30000 / 1001


def white_top(array, border):
    if border > 247:
        return None
    # Both native cards have a translucent/light-gray top material. An absolute
    # white threshold selected the content below that top material,44px too low.
    threshold = border + .5 * (255 - border)
    white = np.median(array[:, 400:1040], axis=1).min(axis=1) > threshold
    starts = np.where(np.convolve(white.astype(int), np.ones(6, int), 'valid') == 6)[0]
    return int(starts[0]) if len(starts) else None


calendar = []
previous = 222
selected_first = None
for frame in range(168, 265):
    array = np.array(Image.open(decoded / f'{frame:06}.png').convert('RGB'))
    rgb = array.astype(int)
    border = float(np.median(np.r_[array[:, :20].ravel(), array[:, -20:].ravel()]))
    blue = ((rgb[:, :, 1] - rgb[:, :, 0] > 60)
            & (rgb[:, :, 2] - rgb[:, :, 1] > 20))
    density = blue[:, 230:570].sum(axis=1).astype(float)
    top = white_top(array, border)
    row = {'frame': frame, 'time': frame / fps, 'border': border,
           'scrim_opacity': max(0, 1 - border / 255), 'blue_pixels': int(blue.sum()),
           'white_top': top}
    first_column = blue.copy()
    first_column[:, :230] = False
    first_column[:, 570:] = False
    closed = ndimage.binary_closing(first_column, structure=np.ones((3, 3)))
    labels, _ = ndimage.label(closed)
    rectangles = []
    for label, slices in enumerate(ndimage.find_objects(labels), 1):
        if slices is None:
            continue
        yy, xx = slices
        width, height = xx.stop - xx.start, yy.stop - yy.start
        if 270 < width < 340 and 75 < height < 130:
            rectangles.append({'bbox': [xx.start, yy.start, xx.stop, yy.stop],
                               'width': width, 'height': height,
                               'blue_area': int((labels[slices] == label).sum())})
    row['first_column_controls'] = rectangles
    if (top is not None and top > 1) or blue.sum() > 400:
        if top is not None and top > 1:
            shift = top
            method = 'foreground white top'
        else:
            edge = np.abs(np.diff(density, prepend=0))
            edge = np.maximum.reduce([np.roll(edge, offset) for offset in range(-3, 4)])
            candidates = []
            for shift in range(max(-720, round(previous - 250)), min(230, round(previous + 5)) + 1):
                locations = np.array([392, 494, 877, 979, 1177, 1279]) + shift
                visible = locations[(locations >= 0) & (locations < 1080)]
                score = float(edge[visible].sum()) - .3 * abs(shift - previous)
                candidates.append((score, shift))
            score, shift = max(candidates)
            row['blue_border_score'] = score
            method = 'native blue control edges'
        row['sheet_y'] = float(shift)
        row['method'] = method
        previous = shift
        if selected_first is None and np.max(density) > 280:
            # A filled button has a broad band, unlike a thin outlined rectangle.
            if np.count_nonzero(density > 250) > 45:
                selected_first = frame
    calendar.append(row)
friday_offsets = [control['bbox'][1] - row['white_top']
                  for row in calendar if row['white_top'] is not None and row['white_top'] > 1
                  for control in row['first_column_controls'] if control['width'] > 310]
friday_local_top = float(np.median(friday_offsets)) if friday_offsets else 877
for row in calendar:
    controls = [control for control in row['first_column_controls'] if control['width'] > 310]
    if (row['white_top'] is None or row['white_top'] <= 1) and controls:
        friday = min(controls, key=lambda control: control['bbox'][1])
        row['sheet_y'] = friday['bbox'][1] - friday_local_top
        row['method'] = 'native first Friday control, calibrated while the top was visible'
calendar_cut = next(row['frame'] for row in calendar
                    if row['frame'] > 250 and row['blue_pixels'] < 100 and row['border'] > 245)
(p / 'measurements-v8/calendar-fit.json').write_text(json.dumps({
    'method': 'Native white top while visible; blue button-edge pattern when the card top is clipped. Border RGB directly measures scrim. Exact original source frames.',
    'selected_first_frame': selected_first, 'cut_frame': calendar_cut,
    'friday_local_control_top': friday_local_top,
    'measurements': calendar}, indent=2))

# RGB profile retains twenty horizontal bins, so other restaurant photos do not
# match merely because their average colors are similar.
template = np.array(Image.open(p / 'assets/ettan-photo.png').convert('RGB')).astype(np.float32)
template = template.reshape(168, 21, 8, 3).mean(axis=2).reshape(168, -1)
template = 255 - template
fft_size = next_fast_len(1080 + 168 - 1)
template_fft = rfft(template, n=fft_size, axis=0)
template_energy = np.r_[0, np.cumsum((template * template).sum(axis=1), dtype=np.float64)]
restaurant = []
for frame in range(575, 670):
    strip = np.array(Image.open(p / f'measurements-v8/restaurant-strips/{frame:06}.png').convert('RGB')).astype(np.float32)
    profile = 255 - strip.reshape(1080, 21, 8, 3).mean(axis=2).reshape(1080, -1)
    source_fft = rfft(profile, n=fft_size, axis=0)
    correlation = irfft((source_fft * np.conj(template_fft)).sum(axis=1), n=fft_size)
    source_energy = np.r_[0, np.cumsum((profile * profile).sum(axis=1), dtype=np.float64)]
    ys = np.arange(-130, 1000)
    lo, hi = np.maximum(0, ys), np.minimum(1080, ys + 168)
    tlo, thi = np.maximum(0, -ys), np.minimum(168, 1080 - ys)
    valid = (hi - lo >= 30) & (thi > tlo)
    ys, lo, hi, tlo, thi = [value[valid] for value in [ys, lo, hi, tlo, thi]]
    template_norm = template_energy[thi] - template_energy[tlo]
    source_norm = source_energy[hi] - source_energy[lo]
    energy = template_norm * source_norm
    # Empty white windows have zero energy. FFT roundoff there previously yielded
    # impossible NCC>1; exclude them before normalizing instead of dividing by1.
    scores = np.where((template_norm > 1000) & (source_norm > 1000),
                      correlation[np.mod(ys, fft_size)] / np.sqrt(np.maximum(1, energy)), 0)
    index = int(scores.argmax())
    photo_y = float(ys[index])
    if 0 < index < len(scores) - 1:
        denominator = scores[index - 1] - 2 * scores[index] + scores[index + 1]
        if abs(denominator) > 1e-8:
            photo_y += float(np.clip(.5 * (scores[index - 1] - scores[index + 1]) / denominator, -.5, .5))
    row = {'frame': frame, 'time': frame / fps, 'photo_y': photo_y,
           'photo_ncc': float(scores[index])}
    full = decoded / f'{frame:06}.png'
    if full.exists():
        array = np.array(Image.open(full).convert('RGB'))
        border = float(np.median(np.r_[array[:, :20].ravel(), array[:, -20:].ravel()]))
        top = white_top(array, border)
        row.update(border=border, scrim_opacity=max(0, 1 - border / 255), white_top=top)
    if scores[index] > .8 and frame < 664:
        row.update(sheet_y=photo_y - 320, method='authentic Ettan photo profile')
    elif row.get('white_top') is not None and row['white_top'] > 0:
        row.update(sheet_y=float(row['white_top']), method='foreground white top')
    restaurant.append(row)
(p / 'measurements-v8/restaurant-fit.json').write_text(json.dumps({
    'method': 'Exact source168px restaurant strip;21 RGB column bins preserve photo identity. White top handles fast dismissals after the photo leaves frame. No source pixels become a UI layer.',
    'measurements': restaurant}, indent=2))
for rows, points in [(calendar, [180, 184, 212, 240, 259, 263, 264]),
                     (restaurant, [580, 583, 599, 613, 659, 663, 664, 665])]:
    for frame in points:
        print(next(row for row in rows if row['frame'] == frame))
