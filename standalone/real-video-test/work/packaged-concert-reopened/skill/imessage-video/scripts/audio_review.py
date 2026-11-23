"""Compare audio coverage and audible cues on the presented movie timeline."""
import json
import subprocess
from fractions import Fraction

import numpy as np

RATE = 48000
BLOCK = 960
CLOCK_TOLERANCE = Fraction(1, 50)
ENVELOPE_LIMIT = 0.22
SPECTRUM_LIMIT = 0.8


def streams(path):
    probe = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
        "stream=channels,start_time,duration", "-of", "json", str(path),
    ])
    return json.loads(probe).get("streams", [])


def pcm(path, index, channels, duration):
    raw = subprocess.check_output([
        "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(path),
        "-map", f"0:a:{index}", "-ar", str(RATE), "-f", "f32le", "pipe:1",
    ])
    samples = np.frombuffer(raw, "<f4").reshape(-1, channels)
    # Ignore codec padding past the end of the presented stream.
    return samples[:round(duration * RATE)].astype(np.float64)


def compare(source, output):
    left, right = streams(source), streams(output)
    result = {"source_stream_count": len(left), "output_stream_count": len(right),
              "tracks": [], "failures": [], "clock_tolerance_ms": float(CLOCK_TOLERANCE * 1000),
              "max_allowed_envelope_error": ENVELOPE_LIMIT,
              "min_allowed_spectrum_similarity": SPECTRUM_LIMIT}
    failures = result["failures"]
    if len(left) != len(right):
        failures.append("different audio stream counts")
    for index, (a, b) in enumerate(zip(left, right)):
        try:
            a_start, b_start = (Fraction(s["start_time"]) for s in (a, b))
            a_duration, b_duration = (Fraction(s["duration"]) for s in (a, b))
        except (ValueError, KeyError, ZeroDivisionError):
            failures.append(f"audio track {index}: missing presented start or duration")
            continue
        if min(a_duration, b_duration) <= 0 or a["channels"] != b["channels"]:
            failures.append(f"audio track {index}: invalid duration or different channel count")
            continue
        start_error = abs(a_start - b_start)
        end_error = abs(a_start + a_duration - b_start - b_duration)
        if max(start_error, end_error) > CLOCK_TOLERANCE:
            failures.append(f"audio track {index}: start or ending differs by more than 20 ms")
        channels = a["channels"]
        samples = [pcm(path, index, channels, duration)
                   for path, duration in ((source, a_duration), (output, b_duration))]
        if any(len(x) + BLOCK < round(duration * RATE)
               for x, duration in zip(samples, (a_duration, b_duration))):
            failures.append(f"audio track {index}: decoded samples end before the presented track")
        if any(len(x) == 0 or not np.isfinite(x).all() for x in samples):
            failures.append(f"audio track {index}: missing or invalid decoded samples")
            continue
        # Align both tracks to the earlier presented origin before measuring cue timing.
        origin = min(a_start, b_start)
        offsets = [round((t - origin) * RATE) for t in (a_start, b_start)]
        length = max(i + len(x) for i, x in zip(offsets, samples))
        blocks = [np.pad(x, ((i, -length % BLOCK + length - i - len(x)), (0, 0))).reshape(-1, BLOCK, channels)
                  for x, i in zip(samples, offsets)]
        rms = [np.sqrt(np.mean(x ** 2, axis=1)) for x in blocks]
        peak = max(float(x.max()) for x in rms)
        envelope_error = float(np.max(np.abs(rms[0] - rms[1])) / max(peak, 1e-6))
        audible = np.maximum(*rms) > max(0.08 * peak, 1e-5)
        spectra = [np.abs(np.fft.rfft(x * np.hanning(BLOCK)[None, :, None], axis=1)) for x in blocks]
        norm = np.linalg.norm(spectra[0], axis=1) * np.linalg.norm(spectra[1], axis=1)
        cosine = np.sum(spectra[0] * spectra[1], axis=1) / np.maximum(norm, 1e-12)
        similarity = float(np.mean(cosine[audible])) if np.any(audible) else None
        if envelope_error > ENVELOPE_LIMIT:
            failures.append(f"audio track {index}: cue timing or level differs")
        if similarity is not None and similarity < SPECTRUM_LIMIT:
            failures.append(f"audio track {index}: audible spectrum differs")
        result["tracks"].append({
            "index": index, "channels": channels, "start_error_ms": float(start_error * 1000),
            "end_error_ms": float(end_error * 1000), "decoded_samples": [len(x) for x in samples],
            "compared_windows": len(rms[0]), "audible_channel_windows": int(audible.sum()),
            "max_envelope_error": envelope_error, "mean_spectrum_similarity": similarity,
        })
    result["limits_passed"] = not failures
    return result
