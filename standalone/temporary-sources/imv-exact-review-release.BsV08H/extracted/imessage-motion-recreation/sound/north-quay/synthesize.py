"""Generate the original North Quay effects and notes at 48 kHz."""
import argparse
from pathlib import Path

import numpy as np
from scipy.io import wavfile

RATE = 48_000


def clock(seconds, impact):
    position = np.arange(round(seconds * RATE)) / RATE
    elapsed = np.maximum(position - impact, 0)
    return position, elapsed


def taper(position, steps=0.012):
    return np.clip((position[-1] - position) / steps, 0, 1)


def stereo(left, right, position):
    return (np.column_stack((left, right)) * taper(position)[:, None]).astype(np.float32)


def tactile(seconds, impact, seed, resonances):
    position, elapsed = clock(seconds, impact)
    noise = np.random.default_rng(seed).standard_normal(len(position))
    prep = np.exp(-((position - impact + .006) / .003) ** 2) * .035 * noise
    contact = np.exp(-((position - impact) / .0015) ** 2) * .21 * noise
    ring = sum(weight * np.sin(2 * np.pi * pitch * elapsed) * np.exp(-elapsed / decay)
               for pitch, decay, weight in resonances)
    mono = prep + contact + ring * np.clip(elapsed / .003, 0, 1)
    return stereo(mono, .87 * mono + .04 * ring, position)


def bloom(seconds, impact, frequencies, decay):
    position, elapsed = clock(seconds, impact)
    shape = np.clip(elapsed / .018, 0, 1) * np.exp(-elapsed / decay)
    bend = .9 * np.expm1(-15 * elapsed)
    bass, air = (
        shape * (.16 * np.sin(2 * np.pi * (hz * elapsed + bend))
                 + .025 * np.sin(2 * np.pi * (2 * hz * elapsed + bend)))
        for hz in frequencies
    )
    return stereo(bass + air * .65, air + bass * .74, position)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=True)
    assets = {
        "paper-tick": tactile(.105, .014, 84, [(310, .019, .18), (940, .010, .09)]),
        "felt-confirm": tactile(.155, .022, 112, [(195, .035, .24), (670, .022, .11)]),
        "warm-rise": bloom(.68, .013, (196, 246.94), .18),
        "open-fifth": bloom(.27, .029, (146.83, 220), .065),
    }
    for name, audio in assets.items():
        wavfile.write(output / f"{name}.wav", RATE, audio)


if __name__ == "__main__":
    main()
