"""Deterministic, original field ambience and graphite foley for Pinch Hit."""

import numpy as np
from scipy.signal import butter, sosfilt


def band(data, low, high, rate):
    return sosfilt(butter(2, [low, high], btype="bandpass", fs=rate, output="sos"), data)


def field_bed(count, rate, fps, plan):
    t = np.arange(count) / rate
    rng = np.random.default_rng(plan["seed"])
    drift = 0.73 + 0.13 * np.sin(2 * np.pi * 0.29 * t) + 0.09 * np.sin(2 * np.pi * 0.67 * t + 1.4)
    wind = band(rng.standard_normal(count), 145, 640, rate) * drift
    air = band(rng.standard_normal(count), 640, 1760, rate)
    side = band(rng.standard_normal(count), 420, 1440, rate)
    perspective = plan.get("perspective_by_frame", [[0, 0.36], [98, 0.18], [160, 0.09],
                                                     [444, 0.10], [576, 0.04]])
    frames, values = zip(*perspective)
    closeness = np.interp(t, np.array(frames) / fps, values)
    mid = wind + air * closeness
    if "indoors_by_frame" in plan:
        frames, values = zip(*plan["indoors_by_frame"])
        indoors = np.interp(t, np.array(frames) / fps, values)
        room = band(rng.standard_normal(count), 160, 370, rate) * 0.62
        mid = mid * (1 - indoors) + room * indoors
        side *= 1 - indoors * 0.6
    stereo = np.column_stack((mid + side * 0.16, mid - side * 0.16))
    stereo /= np.max(np.abs(stereo))
    frames, levels = zip(*plan["level_dbfs_by_frame"])
    gain = 10 ** (np.interp(t, np.array(frames) / fps, levels) / 20)
    stereo *= gain[:, None]
    fade_in, fade_out = int(0.18 * rate), int(0.32 * rate)
    stereo[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    stereo[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
    return stereo


def graphite(design, rate):
    t = np.arange(round(design["duration_ms"] * rate / 1000)) / rate
    rng = np.random.default_rng(design["seed"])
    speed = np.sin(np.pi * t / design["duration_ms"] * 1000) ** 1.4
    grain = band(rng.standard_normal(len(t)), 840, 5700, rate)
    body = band(rng.standard_normal(len(t)), 260, 860, rate)
    irregularity = np.maximum(
        0.12, 0.5 + 0.25 * np.sin(2 * np.pi * 34 * t + 0.3) + 0.24 * np.sin(2 * np.pi * 49 * t)
    )
    # The motion accelerates into the mark and tapers when the tip stops.
    signal = (grain * irregularity + 0.34 * body) * speed
    return np.column_stack((signal * 1.04, signal * 0.96))
