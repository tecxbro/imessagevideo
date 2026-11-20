"""Verify a decoded MP4 against visual anchors and source audio fingerprints."""
from fractions import Fraction
import json

import numpy as np
from scipy import signal

from media import RATE, db, decode, picture_signature, picture_track, probe, sample, sha256
from project import landmark_rows, resolved_cues, silence_ranges

MATCH_RATE = 12_000
DECIMATION = RATE // MATCH_RATE


def match_signal(audio):
    reduced = signal.resample_poly(audio, 1, DECIMATION, axis=0)
    highpass = signal.butter(2, 100, fs=MATCH_RATE, btype="highpass", output="sos")
    return signal.sosfilt(highpass, reduced, axis=0)


def rms_gaps(expected, decoded):
    """Flag substantial dropouts in ranges where the approved PCM has energy."""
    window = RATE // 50
    count = min(len(expected), len(decoded)) // window

    def rms(audio):
        return np.sqrt(np.mean(audio[:count * window].reshape(count, window, 2) ** 2, axis=(1, 2)))

    reference = rms(expected)
    actual = rms(decoded)
    silent = (reference >= 10 ** (-45 / 20)) & (actual < reference * 10 ** (-18 / 20))
    edges = np.flatnonzero(np.diff(np.r_[False, silent, False]))
    return [[round(start * window / RATE, 4), round(end * window / RATE, 4)]
            for start, end in zip(edges[::2], edges[1::2])]



def pcm_differences(expected, decoded):
    """Find 20 ms windows whose audible-band residual exceeds codec allowance."""
    window = MATCH_RATE // 50
    count = min(len(expected), len(decoded)) // window
    if not count:
        return []

    def rms(audio):
        return np.sqrt(np.mean(audio[:count * window].reshape(count, window, 2) ** 2, axis=(1, 2)))

    size = count * window
    residual = rms(expected[:size] - decoded[:size])
    ceiling = np.maximum(10 ** (-50 / 20), rms(expected) * .18)
    exceeds = residual > ceiling
    edges = np.flatnonzero(np.diff(np.r_[False, exceeds, False]))
    return [[round(start * window / MATCH_RATE, 4), round(end * window / MATCH_RATE, 4)]
            for start, end in zip(edges[::2], edges[1::2])]

def audio_timing(export):
    content = probe(export, "-select_streams", "a:0", "-show_streams", "-show_frames",
                    "-show_entries", "stream=codec_name,channels,sample_rate,start_pts,"
                    "duration_ts,time_base:frame=best_effort_timestamp,nb_samples")
    track, = content["streams"]
    clock = Fraction(track["time_base"])
    rate = int(track["sample_rate"])
    if not content.get("frames"):
        raise ValueError("export has no decoded audio frames")
    frames = [(int(frame["best_effort_timestamp"]) * clock, int(frame["nb_samples"]))
              for frame in content["frames"]]
    start = sample(frames[0][0])
    discontinuity = max((abs(sample(current[0] - previous[0]
                                    - Fraction(previous[1], rate)))
                         for previous, current in zip(frames, frames[1:])), default=0)
    duration = sample(int(track["duration_ts"]) * clock)
    return track, start, discontinuity, duration


def strongest_fingerprint(template, cue):
    if cue.fingerprint is not None:
        begin, end = (round(index / DECIMATION) for index in cue.fingerprint)
        if end > len(template):
            raise ValueError(f"{cue.id}: fingerprint extends outside the asset")
    else:
        width = min(len(template), round(0.08 * MATCH_RATE))
        energy = np.r_[0, np.cumsum(np.sum(template ** 2, axis=1))]
        begin = int(np.argmax(energy[width:] - energy[:-width]))
        end = begin + width
    segment = template[begin:end]
    channel = int(np.argmax(np.sum(segment ** 2, axis=0)))
    reference = segment[:, channel]
    energy = float(np.dot(reference, reference))
    if len(reference) < 0.012 * MATCH_RATE or energy < 1e-9:
        raise ValueError(f"{cue.id}: no usable source fingerprint")
    return begin, reference, energy, channel


def check_cue(cue, expected_impact, source, decoded, audio_start, bus_gain):
    begin, template, energy, channel = strongest_fingerprint(source, cue)
    predicted_asset = expected_impact - cue.impact - audio_start
    first = max(0, (predicted_asset - cue.search) // DECIMATION + begin)
    last = min(len(decoded) - len(template), (predicted_asset + cue.search) // DECIMATION + begin)
    measurement = {"id": cue.id, "event": cue.event, "expected_impact_sample": expected_impact,
                   "intended_offset_samples": cue.offset}
    if last < first:
        return {**measurement, "verdict": "missing"}
    interval = decoded[first:last + len(template), channel]
    dots = signal.correlate(interval, template, mode="valid", method="fft")
    prefix = np.r_[0, np.cumsum(interval ** 2)]
    strength = np.maximum(0, prefix[len(template):] - prefix[:-len(template)])
    correlation = dots / np.sqrt(np.maximum(strength * energy, 1e-20))
    fitted_gain = dots / energy
    gain_floor = 10 ** ((cue.gain_db + bus_gain - 16) / 20)
    valid = (correlation >= cue.min_correlation) & (fitted_gain >= gain_floor)
    impacts = ((np.arange(len(correlation)) + first - begin) * DECIMATION
               + audio_start + cue.impact)
    errors = impacts - expected_impact
    within = valid & (np.abs(errors) <= cue.tolerance)
    candidates = np.flatnonzero(within if np.any(within) else valid)
    if not len(candidates):
        return {**measurement, "verdict": "missing",
                "best_correlation": round(float(np.max(correlation)), 3)}
    index = candidates[np.argmax(correlation[candidates])]
    impact = int(impacts[index])
    error = int(errors[index])
    verdict = "pass" if abs(error) <= cue.tolerance else "late" if error > 0 else "early"
    return {**measurement, "verdict": verdict, "correlation": round(float(correlation[index]), 3),
            "observed_asset_alignment_sample": impact - cue.impact,
            "estimated_onset_marker_sample": impact - cue.impact + cue.onset,
            "observed_impact_marker_sample": impact, "error_ms": round(error * 1000 / RATE, 3)}


def verify(plan_path, picture, export, manifest_path):
    stream, picture_duration = picture_track(picture)
    final_stream, final_duration = picture_track(export)
    streams = probe(export, "-show_streams")["streams"]
    if sorted(track["codec_type"] for track in streams) != ["audio", "video"]:
        raise ValueError("export needs exactly one picture and one audio stream")

    failures = []
    manifest = json.loads(manifest_path.read_text())
    for key, path in (("picture_sha256", picture), ("plan_sha256", plan_path),
                      ("export_sha256", export), ("mix_sha256", manifest_path.parent / "mix.wav")):
        if sha256(path) != manifest.get(key):
            failures.append(f"{key} differs from manifest")
    if picture_duration != final_duration or picture_signature(picture) != picture_signature(export):
        failures.append("final video content or packet timestamps differ from the picture master")
    if stream["codec_name"] != "h264" or final_stream["codec_name"] != "h264":
        failures.append("delivery profile requires H.264 video")
    plan, cues, landmarks, rows = resolved_cues(plan_path, export)
    if landmark_rows(landmarks) != manifest.get("landmarks"):
        failures.append("manifest landmarks differ from decoded export frames")

    track, start, discontinuity, duration = audio_timing(export)
    decoded = decode(export)
    count = sample(picture_duration)
    if (track["codec_name"], track["channels"], track["sample_rate"]) != ("aac", 2, str(RATE)):
        failures.append("delivery profile requires 48 kHz stereo AAC")
    # MP4 edit-list durations may round to a millisecond. AAC decode can expose a final padded frame.
    if abs(start) > 1 or discontinuity > 1:
        failures.append("decoded audio PTS has a nonzero start or gaps/overlaps")
    if abs(duration - count) > 48 or not count - 48 <= len(decoded) <= count + 1024:
        failures.append("audio duration differs from picture beyond MP4 rounding/AAC padding")

    true_peak = float(np.max(np.abs(signal.resample_poly(decoded, 4, 1, axis=0))))
    peak = float(np.max(np.abs(decoded)))
    if peak >= 1 or true_peak >= 1:
        failures.append("decoded audio clips or exceeds full scale between samples")
    expected = decode(manifest_path.parent / "mix.wav")
    if len(expected) != count:
        failures.append("approved PCM duration differs from picture")
    gaps = rms_gaps(expected, decoded)
    if gaps:
        failures.append("decoded audio has energy dropouts relative to the approved PCM")

    quiet_checks = []
    for start_sample, end_sample, limit, purpose in silence_ranges(plan, landmarks, count):
        peak_quiet = float(np.max(np.abs(decoded[start_sample:end_sample]), initial=0))
        passed = peak_quiet <= 10 ** (limit / 20)
        quiet_checks.append({"start_sample": start_sample, "end_sample": end_sample,
                             "purpose": purpose, "peak_dbfs": db(peak_quiet), "pass": passed})
        if not passed:
            failures.append(f"encoded audio intrudes on intended silence ({purpose})")

    match_audio = match_signal(decoded)
    differences = pcm_differences(match_signal(expected), match_audio)
    if differences:
        failures.append("decoded audio differs materially from the approved PCM")
    source_cache = {}
    cue_results = []
    observations = {}
    manifest_rows = {row["id"]: row for row in manifest.get("cues", [])}
    if len(manifest.get("cues", [])) != len(cues) or set(manifest_rows) != {cue.id for cue in cues}:
        failures.append("manifest cue IDs differ from the sound plan")
    for cue, row in zip(cues, rows):
        compiled = manifest_rows.get(cue.id, {})
        for key in ("event_frame", "asset_start_sample", "impact_sample", "offset_samples",
                    "onset_marker_sample"):
            if row[key] != compiled.get(key):
                failures.append(f"{cue.id}: manifest {key} differs from decoded picture resolution")
        asset_hash = sha256(cue.asset)
        if asset_hash != compiled.get("asset_sha256"):
            failures.append(f"{cue.id}: source audio hash differs from manifest")
        if cue.event is None:
            continue
        if cue.asset not in source_cache:
            source_cache[cue.asset] = match_signal(decode(cue.asset))
        result = check_cue(cue, row["impact_sample"], source_cache[cue.asset], match_audio, start,
                           float(plan.get("bus_gain_db", {}).get(cue.bus, 0)))
        if result["verdict"] == "pass":
            observed = result["observed_asset_alignment_sample"]
            matches = observations.setdefault(asset_hash, [])
            for previous_start, previous_observed, previous_id in matches:
                if row["asset_start_sample"] != previous_start and abs(observed - previous_observed) < 48:
                    result["verdict"] = "ambiguous"
                    result["shared_observation_with"] = previous_id
                    break
            matches.append((row["asset_start_sample"], observed, cue.id))
        cue_results.append(result)
        if result["verdict"] != "pass":
            failures.append(f"{cue.id}: {result['verdict']} against decoded picture")
    return {"pass": not failures, "failures": failures, "picture_duration": str(picture_duration),
            "first_audio_sample": start, "audio_clock_max_discontinuity_samples": discontinuity,
            "audio_stream_duration_samples": duration, "decoded_audio_samples": len(decoded),
            "sample_peak_dbfs": db(peak), "estimated_true_peak_dbfs": db(true_peak),
            "energy_dropouts_s": gaps, "pcm_difference_ranges_s": differences, "silence": quiet_checks, "landmarks": landmark_rows(landmarks),
            "cues": cue_results, "human_audition": "pending unless documented separately"}
