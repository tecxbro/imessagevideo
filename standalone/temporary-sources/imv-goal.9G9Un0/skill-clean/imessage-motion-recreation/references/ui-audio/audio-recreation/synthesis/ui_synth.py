"""Original, deterministic 48 kHz UI sound synthesis. No recorded audio inputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import subprocess
import wave
from pathlib import Path

import numpy as np
import scipy
from scipy import signal

SAMPLE_RATE = 48_000
PEAK_CEILING = 10 ** (-3 / 20)
EFFECTS = {
    "bubble_pop": {"duration": .18, "description": "Soft descending resonant bubble; message arrival."},
    "touch_click": {"duration": .035, "description": "Dry, quiet fingertip click; a small UI selection."},
    "key_tap": {"duration": .065, "description": "Short wooden/mechanical tap; sparse typing accents."},
    "air_whoosh": {"duration": .28, "description": "Airy quick pass; small object or type movement."},
    "card_swoosh": {"duration": .62, "description": "Rounder, longer air/body pass; a card or camera move."},
    "glass_confirm": {"duration": .72, "description": "Warm inharmonic glass bloom; confirmation or completion."},
    "low_impact": {"duration": .28, "description": "Muted low thump; a restrained landing or emphasis."},
    "digital_sparkle": {"duration": .48, "description": "Small staggered digital glints; a bright reveal."},
}
ALIASES = {"pop": "bubble_pop", "plop": "bubble_pop", "click": "touch_click",
           "key": "key_tap", "whoosh": "air_whoosh", "swoosh": "card_swoosh",
           "bell": "glass_confirm", "confirm": "glass_confirm", "impact": "low_impact",
           "sparkle": "digital_sparkle"}


def _band(x: np.ndarray, low: float, high: float) -> np.ndarray:
    low, high = max(20., low), min(SAMPLE_RATE * .46, high)
    if high <= low:
        high = min(SAMPLE_RATE * .46, low * 1.3)
    sos = signal.butter(2, [low, high], btype="bandpass", fs=SAMPLE_RATE, output="sos")
    y = signal.sosfilt(sos, x)
    rms = np.sqrt(np.mean(y * y))
    return y / max(rms, 1e-12)


def _tone(frequency: np.ndarray | float, n: int, phase: float = 0.) -> np.ndarray:
    f = np.broadcast_to(frequency, (n,)).astype(np.float64)
    f = np.clip(f, 20., SAMPLE_RATE * .44)
    return np.sin(phase + np.cumsum(f) * (2 * np.pi / SAMPLE_RATE))


def _hit(t: np.ndarray, attack: float, decay: float) -> np.ndarray:
    return -np.expm1(-t / max(attack, 1 / SAMPLE_RATE)) * np.exp(-t / decay)


def _delay(x: np.ndarray, seconds: float) -> np.ndarray:
    offset = max(0, round(seconds * SAMPLE_RATE))
    return np.pad(x, (offset, 0))[:len(x)]


def _stereo(mono: np.ndarray, side: np.ndarray | None = None) -> np.ndarray:
    if side is None:
        return np.column_stack([mono, mono])
    return np.column_stack([mono + side, mono - side])


def render(effect: str, *, pitch: float = 1., duration: float | None = None,
           energy: float = .75, pan: float = 0., seed: int = 0) -> np.ndarray:
    """Return float32 samples [frames, 2], 48 kHz.

    pitch is a frequency multiplier (1=neutral; 2=one octave up). Energy 0..1
    controls articulation/brightness and final peak; pan -1..1 is left..right.
    Stereo files are peak-normalized to -3 dBFS * energy. No samples are read.
    """
    effect = ALIASES.get(effect, effect)
    if effect not in EFFECTS:
        raise ValueError(f"Unknown effect {effect!r}; choose {', '.join(EFFECTS)}")
    duration = EFFECTS[effect]["duration"] if duration is None else duration
    if not all(math.isfinite(v) for v in [pitch, duration, energy, pan]):
        raise ValueError("Parameters must be finite")
    if not .25 <= pitch <= 4 or not .01 <= duration <= 4:
        raise ValueError("pitch must be .25..4; duration must be .01..4 seconds")
    if not 0 <= energy <= 1 or not -1 <= pan <= 1:
        raise ValueError("energy must be 0..1; pan must be -1..1")
    rng = np.random.default_rng(seed)
    n = round(duration * SAMPLE_RATE)
    if energy == 0:
        return np.zeros((n, 2), dtype=np.float32)
    t = np.arange(n, dtype=np.float64) / SAMPLE_RATE
    u = np.arange(n, dtype=np.float64) / max(1, n - 1)
    length = duration / EFFECTS[effect]["duration"]
    jitter = rng.uniform(.985, 1.015)
    p = pitch * jitter
    noise = rng.standard_normal(n)

    if effect == "bubble_pop":
        f = p * (235 + 570 * np.exp(-t / (.021 * length)))
        body = _tone(f, n) * _hit(t, .0007 * length, .035 * length)
        overtone = .18 * _tone(f * 1.93, n) * _hit(t, .0004 * length, .013 * length)
        air = .035 * _band(noise, 900 * pitch, 4600 * pitch) * _hit(t, .00025, .008 * length)
        x = _stereo(body + overtone + air)
    elif effect == "touch_click":
        tick = _band(noise, 1600 * pitch, 7000 * pitch)
        env = _hit(t, .00012 * length, .0034 * length)
        body = .15 * _tone(p * (2200 - 550 * u), n) * _hit(t, .00012, .0028 * length)
        x = _stereo(.65 * tick * env + body)
    elif effect == "key_tap":
        wood = _tone(610 * p, n, rng.uniform(0, .4)) + .25 * _tone(1390 * p, n)
        body = wood * _hit(t, .00035 * length, .0105 * length)
        top = .13 * _band(noise, 1200 * pitch, 5200 * pitch) * _hit(t, .0001, .0048 * length)
        bounce = .085 * _delay(_band(rng.standard_normal(n), 650, 2700), .007 * length)
        bounce *= _hit(np.maximum(t - .007 * length, 0), .0002, .004 * length)
        x = _stereo(body + top + bounce)
    elif effect in ["air_whoosh", "card_swoosh"]:
        low = _band(noise, 100 * pitch, 1900 * pitch)
        high = _band(rng.standard_normal(n), 1100 * pitch, (6500 + 2500 * energy) * pitch)
        shape = np.sin(np.pi * u) ** (1.5 if effect == "air_whoosh" else 2.1)
        mix = .28 + .5 * u
        air = ((1 - mix) * low + mix * high) * shape
        # A tiny moving cavity adds weight without an identifiable pitched melody.
        cavity = .08 * _tone(p * (140 + 420 * u ** 1.4), n) * shape
        if effect == "card_swoosh":
            air *= .75 + .25 * np.sin(np.pi * u)
            cavity += .09 * _tone(p * (100 + 120 * u), n) * shape
        side = .18 * _band(rng.standard_normal(n), 700, 6200) * shape
        side = _delay(side, .0013)
        x = _stereo(air + cavity, side)
    elif effect == "glass_confirm":
        mono = np.zeros(n)
        for ratio, level, decay in [(1, 1, .22), (2.73, .25, .12), (4.91, .085, .075), (7.38, .026, .05)]:
            if 760 * p * ratio >= SAMPLE_RATE * .44:
                continue
            f = 760 * p * ratio * (1 - .0015 * u)
            mono += level * _tone(f, n) * _hit(t, .0017 * length, decay * length)
        air = .015 * _band(noise, 2200, 8500) * _hit(t, .0004, .012 * length)
        side = .12 * (_delay(mono, .0017) - _delay(mono, .0031))
        x = _stereo(mono + air, side)
    elif effect == "low_impact":
        f = p * (44 + 61 * np.exp(-t / (.025 * length)))
        mono = _tone(f, n) * _hit(t, .0016 * length, .055 * length)
        mono += .2 * _tone(154 * p, n) * _hit(t, .001, .027 * length)
        mono += .055 * _band(noise, 80, 700) * _hit(t, .0005, .014 * length)
        x = _stereo(mono)
    else:  # digital_sparkle: original small, staggered modal grains.
        x = np.zeros((n, 2))
        for i, ratio in enumerate([1., 1.414, 1.899, 2.303, 1.63]):
            start = duration * (i * .115 + rng.uniform(0, .014))
            local = np.maximum(t - start, 0)
            frequency = 1700 * p * ratio
            grain = _tone(frequency, n, rng.uniform(0, 2 * np.pi))
            grain *= _hit(local, .0008 * length, (.035 + .012 * rng.random()) * length)
            grain[t < start] = 0
            grain_pan = (-.42 if i % 2 == 0 else .42)
            angle = (grain_pan + 1) * np.pi / 4
            x += grain[:, None] * np.array([np.cos(angle), np.sin(angle)])

    # Finish after all filtering/delays: remove DC with a zero-ended window.
    # Articulation belongs to each design's envelope. A shared 12 ms fade-in
    # softened dry taps, so only de-click the first half millisecond here.
    attack_edge = max(4, min(round(.0005 * SAMPLE_RATE), n // 10))
    release_edge = max(8, min(round(.012 * SAMPLE_RATE), n // 5))
    fade = np.ones(n)
    fade[:attack_edge] *= np.sin(np.linspace(0, np.pi / 2, attack_edge)) ** 2
    fade[-release_edge:] *= np.sin(np.linspace(np.pi / 2, 0, release_edge)) ** 2
    x *= fade[:, None]
    x -= fade[:, None] * (np.sum(x, axis=0) / np.sum(fade))[None, :]
    angle = (pan + 1) * np.pi / 4
    gains = np.array([np.cos(angle), np.sin(angle)])
    gains[np.abs(gains) < 1e-15] = 0
    x *= gains
    peak = np.max(np.abs(x))
    if peak > 0:
        x *= (PEAK_CEILING * energy) / peak
    x[[0, -1], :] = 0
    return x.astype(np.float32)


def analyze(samples: np.ndarray) -> dict:
    x = np.asarray(samples)
    if x.ndim != 2 or x.shape[1] != 2 or len(x) == 0 or not np.isfinite(x).all():
        raise ValueError("Expected nonempty finite stereo samples")
    peak = float(np.max(np.abs(x)))
    return {"frames": len(x), "sample_rate": SAMPLE_RATE, "channels": 2,
            "duration": len(x) / SAMPLE_RATE, "peak": peak,
            "peak_dbfs": 20 * math.log10(peak) if peak else None,
            "rms": float(np.sqrt(np.mean(x.astype(np.float64) ** 2))),
            "dc": np.mean(x, axis=0).tolist(), "finite": True,
            "endpoints_zero": bool(np.all(x[[0, -1]] == 0)), "clipped": bool(peak >= 1)}


def write_wav(path: str | Path, samples: np.ndarray) -> Path:
    """Write standard 48 kHz stereo signed PCM24 without silently clipping."""
    analysis = analyze(samples)
    if analysis["clipped"]:
        raise ValueError("Refusing to write clipped samples")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.rint(np.asarray(samples, dtype=np.float64) * (2 ** 23 - 1)).astype(np.int32).reshape(-1)
    packed = np.column_stack([(pcm >> shift) & 255 for shift in [0, 8, 16]]).astype(np.uint8).tobytes()
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(3)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(packed)
    return path


def write_bank(directory: str | Path, *, seed: int = 20261109, audition: bool = True) -> dict:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    rows, sequence = [], [np.zeros((round(.25 * SAMPLE_RATE), 2), dtype=np.float32)]
    position = .25
    for i, (name, spec) in enumerate(EFFECTS.items()):
        parameters = {"pitch": 1., "duration": spec["duration"], "energy": .75, "pan": 0., "seed": seed + i}
        samples = render(name, **parameters)
        file = write_wav(directory / (name + ".wav"), samples)
        rows.append({"effect": name, "file": file.name, "description": spec["description"],
                     "parameters": parameters, "analysis": analyze(samples),
                     "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                     "audition_start": position})
        sequence.extend([samples, np.zeros((round(.42 * SAMPLE_RATE), 2), dtype=np.float32)])
        position += len(samples) / SAMPLE_RATE + .42
    manifest = {"format_version": 1, "sample_rate": SAMPLE_RATE, "channels": 2, "encoding": "PCM24 WAV",
                "provenance": {"source": "Original procedural oscillators, modal tones and seeded filtered noise",
                               "reference_audio_used": False, "recorded_samples_used": False,
                               "paid_generation_used": False, "external_audio_inputs": [],
                               "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                "toolchain": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
                "normalization": "Joint stereo peak -3 dBFS times energy; defaults peak approximately -5.50 dBFS",
                "assets": rows}
    if audition:
        wav = write_wav(directory / "audition.wav", np.concatenate(sequence))
        mp3 = directory / "audition.mp3"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-threads", "1", "-i", str(wav),
                        "-map_metadata", "-1", "-c:a", "libmp3lame", "-q:a", "2", "-threads", "1", str(mp3)], check=True)
        manifest["audition"] = {"file": mp3.name, "duration": position, "order": list(EFFECTS),
                                "sha256": hashlib.sha256(mp3.read_bytes()).hexdigest()}
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    with (directory / "index.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["effect", "file", "duration", "audition_start", "peak_dbfs", "seed"])
        for row in rows:
            writer.writerow([row["effect"], row["file"], row["analysis"]["duration"], row["audition_start"], row["analysis"]["peak_dbfs"], row["parameters"]["seed"]])
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    bank = sub.add_parser("bank")
    bank.add_argument("--out", type=Path, default=Path(__file__).parent / "bank")
    bank.add_argument("--seed", type=int, default=20261109)
    bank.add_argument("--no-audition", action="store_true")
    one = sub.add_parser("render")
    one.add_argument("effect", choices=list(EFFECTS) + list(ALIASES))
    one.add_argument("output", type=Path)
    one.add_argument("--pitch", type=float, default=1., help="Frequency ratio;2=octave up")
    one.add_argument("--semitones", type=float, help="Alternative pitch in semitones")
    one.add_argument("--duration", type=float)
    one.add_argument("--energy", type=float, default=.75)
    one.add_argument("--pan", type=float, default=0.)
    one.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.command == "list":
        print(json.dumps(EFFECTS, indent=2))
    elif args.command == "bank":
        manifest = write_bank(args.out, seed=args.seed, audition=not args.no_audition)
        print(json.dumps({"directory": str(args.out), "assets": len(manifest["assets"]), "audition": manifest.get("audition")}, indent=2))
    else:
        pitch = 2 ** (args.semitones / 12) if args.semitones is not None else args.pitch
        samples = render(args.effect, pitch=pitch, duration=args.duration, energy=args.energy, pan=args.pan, seed=args.seed)
        write_wav(args.output, samples)
        print(json.dumps({"file": str(args.output), **analyze(samples)}, indent=2))


if __name__ == "__main__":
    main()
