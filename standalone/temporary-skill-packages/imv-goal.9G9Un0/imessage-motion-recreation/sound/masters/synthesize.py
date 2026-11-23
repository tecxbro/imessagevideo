"""Generate the original sounds for the Poke picture treatment comparison."""
from pathlib import Path
import sys
import wave

import numpy as np


RATE = 48000


def times(seconds):
    return np.arange(round(seconds * RATE), dtype=np.float64) / RATE


def burst(t, center, spread):
    return np.exp(-0.5 * ((t - center) / spread) ** 2)


def voice(t, frequency, fall=0):
    return np.sin(2 * np.pi * (frequency * t - fall * t * t / 2))


def modal(t, impact, tones):
    elapsed = np.maximum(t - impact, 0)
    rise = np.minimum(elapsed / 0.002, 1)
    return sum(
        weight * voice(elapsed, frequency, bend) * rise * np.exp(-elapsed / decay)
        for frequency, weight, bend, decay in tones
    )


def band_noise(t, rng, low, high):
    samples = rng.uniform(-1, 1, len(t))
    spectrum = np.fft.rfft(samples)
    frequency = np.fft.rfftfreq(len(t), 1 / RATE)
    # Smooth rolloffs keep the short, close texture free of filter ringing.
    envelope = (1 - np.exp(-(frequency / low) ** 4)) * np.exp(-(frequency / high) ** 4)
    return np.fft.irfft(spectrum * envelope, n=len(t))


def open_sheet(rng):
    t = times(0.23)
    air = band_noise(t, rng, 300, 2600) * burst(t, 0.062, 0.024)
    wood = modal(t, 0.065, [(262, 0.7, 680, 0.042), (701, 0.16, 350, 0.029)])
    return np.column_stack((wood + 0.65 * air, wood + 0.5 * air))


def select_place(rng):
    t = times(0.095)
    touch = band_noise(t, rng, 420, 5100) * burst(t, 0.009, 0.002)
    body = modal(t, 0.007, [(330, 0.65, 1650, 0.014), (1013, 0.22, 1900, 0.008)])
    return np.column_stack((body + 0.55 * touch, body + 0.55 * touch))


def send_card(rng):
    t = times(0.255)
    air = band_noise(t, rng, 600, 2900) * burst(t, 0.025, 0.011)
    body = modal(
        t, 0.028, [(392, 0.50, 1150, 0.037), (932, 0.18, 560, 0.031)]
    )
    body += modal(t, 0.062, [(294, 0.30, 393, 0.042)])
    return np.column_stack((body + 0.36 * air, body + 0.48 * air))


def room_glow(rng):
    t = times(3.4)
    amplitude = np.interp(t, [0, 0.28, 0.9, 1.6, 2.45, 3.4], [0, 0.08, 0.9, 1, 0.5, 0])
    swell = amplitude * amplitude
    common = (0.65 * voice(t, 146.8) + 0.29 * voice(t, 220.0)) * swell
    noise = band_noise(t, rng, 270, 1600) * 0.13 * swell
    left = common + noise + 0.19 * voice(t, 329.7) * swell
    right = common + noise + 0.19 * voice(t, 330.0) * swell
    return np.column_stack((left, right))


def write_wave(path, audio):
    fade = np.linspace(0, 1, round(RATE * 0.003))[:, None]
    audio[:len(fade)] *= fade
    audio[-len(fade):] *= fade[::-1]
    samples = np.rint(0.70 / np.abs(audio).max() * audio * 32767).astype("<i2")
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(samples.tobytes())


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 synthesize.py OUTPUT_DIR")
    folder = Path(sys.argv[1])
    folder.mkdir(parents=True, exist_ok=True)
    recipes = {
        "open-sheet": open_sheet,
        "select-place": select_place,
        "send-card": send_card,
        "room-glow": room_glow,
    }
    for seed, (name, recipe) in enumerate(recipes.items(), start=60871):
        write_wave(folder / f"{name}.wav", recipe(np.random.default_rng(seed)))


if __name__ == "__main__":
    main()
