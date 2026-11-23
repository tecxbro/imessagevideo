"""Measure decoded pixel identity and retain lossless, native-size evidence."""
from pathlib import Path

import numpy as np
from PIL import Image


class PixelEquality:
    def __init__(self):
        self.different_frames = []
        self.changed_pixel_observations = 0
        self.first_difference = None
        self.worst_frame = None

    def add(self, frame, peaks):
        maximum = int(peaks.max())
        count = int(np.count_nonzero(peaks)) if maximum else 0
        if count:
            self.different_frames.append(frame)
            self.changed_pixel_observations += count
            record = {"frame": frame, "changed_pixels": count, "max_channel_delta": maximum}
            if self.first_difference is None:
                ys = np.flatnonzero(peaks.any(axis=1))
                xs = np.flatnonzero(peaks.any(axis=0))
                self.first_difference = {
                    **record, "rect": [int(xs[0]), int(ys[0]), int(xs[-1] - xs[0] + 1), int(ys[-1] - ys[0] + 1)],
                }
            if self.worst_frame is None or count > self.worst_frame["changed_pixels"]:
                self.worst_frame = record
        return count, maximum


def step_error(reference, candidate, previous, crop):
    """Measure signed RGB change between adjacent decoded frames in one fixed crop."""
    a, b = reference[crop].astype(np.int16), candidate[crop].astype(np.int16)
    before_a, before_b = previous
    a -= before_a[crop]
    b -= before_b[crop]
    return float(np.abs(a - b).mean()), bool(a.any()), bool(b.any())


def write_crop(output, region_index, label, reference, candidate, peaks):
    """Write original, render and a visible mask for even one changed channel value."""
    height, width = peaks.shape
    board = Image.new("RGB", (width * 3, height))
    for index, raster in enumerate((reference, candidate)):
        board.paste(Image.fromarray(raster), (index * width, 0))
    mask = np.zeros_like(reference)
    mask[:, :, 0] = np.where(peaks, 96 + np.minimum(peaks.astype(np.uint16) * 8, 159), 0)
    board.paste(Image.fromarray(mask), (2 * width, 0))
    return save_crop(output, region_index, label, board)


def write_step(output, region_index, reference, candidate, previous, crop):
    """Write previous and current rows, with source and render at native size."""
    height, width = reference[crop].shape[:2]
    board = Image.new("RGB", (width * 2, height * 2))
    for y, row in enumerate((previous, (reference, candidate))):
        for x, raster in enumerate(row):
            board.paste(Image.fromarray(raster[crop]), (x * width, y * height))
    return save_crop(output, region_index, "step", board)


def save_crop(output, region_index, label, board):
    relative = Path("crops") / f"{region_index:02d}-{label}.png"
    destination = output / relative
    destination.parent.mkdir(exist_ok=True)
    board.save(destination)
    return relative.as_posix()
