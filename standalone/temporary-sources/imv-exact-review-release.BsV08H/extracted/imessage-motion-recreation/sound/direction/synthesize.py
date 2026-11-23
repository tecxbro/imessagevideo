#!/usr/bin/env python3
"""Make the original Foley, atmosphere and music for The Moon Cue."""
from pathlib import Path
import argparse

import numpy as np
from scipy import signal
from scipy.io.wavfile import write

RATE = 48_000


def time(seconds):
    return np.arange(round(seconds * RATE)) / RATE


def noise(length, seed, low, high):
    generator = np.random.default_rng(seed)
    coefficients = signal.butter(2, (low, high), fs=RATE, btype="bandpass", output="sos")
    return signal.sosfilt(coefficients, generator.standard_normal(length))


def envelope(t, center, attack, decay):
    delta = t - center
    return np.exp(np.minimum(delta, 0) / attack - np.maximum(delta, 0) / decay)


def taper(t, rise, fall):
    return np.clip(t / rise, 0, 1) * np.clip((t[-1] - t) / fall, 0, 1)


def resonances(t, center, partials):
    delta = np.maximum(0, t - center)
    return sum(level * np.sin(2 * np.pi * frequency * delta)
               * envelope(t, center, .0012, decay)
               for frequency, level, decay in partials)


def spatial(t, audio, seed, width=.08):
    side = width * np.roll(audio, round(RATE * .0034))
    side += width * .22 * noise(len(audio), seed, 350, 4800) * np.abs(audio)
    return np.column_stack((audio + side, audio - side)) * taper(t, .003, .016)[:, None]


def interface(seconds, seed, center, pitches):
    t = time(seconds)
    click = noise(len(t), seed, 500, 7800) * envelope(t, center, .002, .009)
    bloom = resonances(t, center, pitches)
    return spatial(t, .36 * click + bloom, seed + 1)


def foley(seconds, seed, high, partials, *, center=.065):
    t = time(seconds)
    fibers = noise(len(t), seed, 175, high)
    movement = .23 * fibers * envelope(t, center - .024, .012, .014)
    impact = .55 * fibers * envelope(t, center, .003, .029)
    tail = .24 * fibers * envelope(t, center + .052, .011, .031)
    return spatial(t, movement + impact + tail + resonances(t, center, partials), seed + 1)


def room(seconds, seed, rise, fall, settle=False):
    t = time(seconds)
    low = noise(len(t), seed, 38, 240) * .12
    breath = noise(len(t), seed + 10, 240, 1200) * .033
    ventilation = .011 * np.sin(2 * np.pi * 53.4 * t) + .007 * np.sin(2 * np.pi * 107.1 * t)
    body = low + breath + ventilation
    if settle:
        body += .10 * noise(len(t), seed + 19, 120, 2600) * envelope(t, .29, .056, .18)
        body += .065 * noise(len(t), seed + 27, 400, 3500) * envelope(t, .54, .037, .16)
    return spatial(t, body, seed + 1, .32) * taper(t, rise, fall)[:, None]


def score(seconds, seed, notes, attack, center, decay):
    t = time(seconds)
    sound = np.zeros(len(t))
    for i, frequency in enumerate(notes):
        start = center + i * .021
        phase = 2 * np.pi * (frequency * t + .014 * np.sin(2 * np.pi * (.17 + i * .04) * t))
        felt = np.sin(phase) + .25 * np.sin(2 * phase + i) + .08 * np.sin(3 * phase)
        sound += felt * envelope(t, start, attack, decay) / len(notes)
    texture = noise(len(t), seed, 220, 2100) * envelope(t, center, attack, decay) * .03
    return spatial(t, .25 * sound + texture, seed + 1, .22) * taper(t, .05, .21)[:, None]


def synthesize(folder):
    folder.mkdir(parents=True, exist_ok=True)
    assets = {
        "seated-opening": room(2.5, 100, .08, .62),
        "seated-wait": room(1.75, 120, .44, .35),
        "seated-return": room(1.3, 140, .46, .45),
        "audience-release": room(1.12, 160, .09, .38, settle=True),
        "send": interface(.19, 200, .032, [(330, .15, .027), (743, .13, .022), (1577, .07, .017)]),
        "reply": interface(.31, 220, .038, [(439, .10, .062), (676, .13, .062), (1141, .055, .032)]),
        "tin": foley(.50, 300, 6800, [(747, .17, .095), (1329, .14, .052),
                                       (2217, .10, .042), (3612, .04, .027)]),
        "paper": foley(.32, 320, 4700, [(217, .045, .026), (370, .019, .015)]),
        "puppet": foley(.27, 340, 3150, [(179, .032, .063), (317, .023, .036)]),
        "tension": score(1.60, 400, [131.0, 155.56, 184.99], .25, .80, .29),
        "release": score(2.25, 420, [130.81, 164.81, 196.0, 261.63], .10, .25, .68),
    }
    for name, audio in assets.items():
        write(folder / f"{name}.wav", RATE, audio.astype(np.float32))


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("folder", type=Path)
    synthesize(cli.parse_args().folder)
