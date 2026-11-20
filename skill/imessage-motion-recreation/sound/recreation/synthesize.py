"""Render four seeded diegetic accents for Train options."""
from pathlib import Path
import sys

import numpy as np

from masters.synthesize import band_noise, burst, modal, times, write_wave


def send_flick(rng):
    t = times(0.108)
    flick = burst(t, 0.013, 0.006) * band_noise(t, rng, 550, 5100)
    impact = modal(t, 0.013, [(474, 0.53, -800, 0.023), (1133, 0.19, 1350, 0.013)])
    return np.column_stack((0.78 * impact + 0.53 * flick, impact + 0.65 * flick))


def drawer_glide(rng):
    t = times(0.177)
    fabric = burst(t, 0.056, 0.019) * band_noise(t, rng, 220, 3200)
    stop = modal(t, 0.054, [(198, 0.44, 500, 0.027), (622, 0.2, 800, 0.015)])
    return np.column_stack((stop + 0.9 * fabric, stop + 0.78 * fabric))


def seat_latch(rng):
    t = times(0.068)
    click = burst(t, 0.006, 0.003) * band_noise(t, rng, 650, 5500)
    plastic = modal(t, 0.005, [(615, 0.61, 2100, 0.011), (1355, 0.12, 1400, 0.006)])
    return np.column_stack((plastic + click, 0.96 * plastic + 0.8 * click))


def receipt_resolve(rng):
    t = times(0.249)
    paper = burst(t, 0.026, 0.012) * band_noise(t, rng, 380, 4100)
    primary = modal(t, 0.029, [(381, 0.56, 60, 0.037), (771, 0.18, 560, 0.030)])
    answer = modal(t, 0.070, [(572, 0.24, 90, 0.037), (1144, 0.10, 500, 0.024)])
    return np.column_stack((primary + answer + 0.29 * paper, primary + 0.8 * answer + 0.35 * paper))


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 -m recreation.synthesize OUTPUT_DIR")
    output = Path(sys.argv[1])
    output.mkdir(parents=True, exist_ok=True)
    recipes = {
        "send-flick": send_flick,
        "drawer-glide": drawer_glide,
        "seat-latch": seat_latch,
        "receipt-resolve": receipt_resolve,
    }
    for seed, (name, recipe) in enumerate(recipes.items(), start=41249):
        write_wave(output / f"{name}.wav", recipe(np.random.default_rng(seed)))


if __name__ == "__main__":
    main()
