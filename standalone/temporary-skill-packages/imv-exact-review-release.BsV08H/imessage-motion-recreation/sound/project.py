"""Read a sound plan, resolve the picture, and render editable stems."""
from dataclasses import dataclass
from fractions import Fraction
import json
import math
from pathlib import Path
import re
from tempfile import TemporaryDirectory

import numpy as np
from scipy.io import wavfile

from landmarks import resolve_landmarks
from media import RATE, db, decode, dump, mux, picture_track, probe, sample, sha256

BUSES = ("dialogue", "music", "atmosphere", "effects")


def millisecond_samples(value):
    return sample(Fraction(str(value)) / 1000)


@dataclass
class Cue:
    id: str
    bus: str
    asset: Path
    provenance: str
    purpose: str
    event: str | None
    fixed_sample: int | None
    offset: int
    impact: int
    onset: int
    gain_db: float
    tolerance: int
    search: int
    min_correlation: float
    fingerprint: tuple[int, int] | None

    @classmethod
    def from_json(cls, data, folder):
        anchor = data.get("event")
        fixed = sample(Fraction(str(data["time_s"]))) if "time_s" in data else None
        if (anchor is None) == (fixed is None):
            raise ValueError("each cue needs exactly one of event or time_s")
        if not re.fullmatch(r"[a-zA-Z0-9_.:-]+", data["id"]):
            raise ValueError("cue ids support only letters, digits, underscore, dot, colon and dash")
        if data["bus"] not in BUSES or not data["source"].strip() or not data["purpose"].strip():
            raise ValueError(f'{data["id"]}: cue needs a supported bus, source and purpose')
        if "offset_samples" in data and "offset_ms" in data:
            raise ValueError(f'{data["id"]}: specify one offset unit')
        offset = data.get("offset_samples", millisecond_samples(data.get("offset_ms", 0)))
        if type(offset) is not int or (anchor is None and offset):
            raise ValueError(f'{data["id"]}: offsets are integer samples on event-bound cues')
        impact = millisecond_samples(data.get("impact_ms", 0))
        onset = millisecond_samples(data.get("onset_ms", 0))
        tolerance = millisecond_samples(data.get("tolerance_ms", 25))
        search = millisecond_samples(data.get("search_ms", 500))
        correlation = float(data.get("min_correlation", 0.62))
        gain = float(data.get("gain_db", 0))
        if (not 0 <= onset <= impact or not 0 < tolerance < search
                or not 0 < correlation <= 1 or not math.isfinite(gain) or not -96 <= gain <= 24):
            raise ValueError(f'{data["id"]}: invalid asset marker, search, tolerance, correlation or gain')
        fingerprint = None
        if "fingerprint_ms" in data:
            begin, end = map(millisecond_samples, data["fingerprint_ms"])
            if begin < 0 or end - begin < millisecond_samples(12):
                raise ValueError(f'{data["id"]}: fingerprint needs at least 12 ms of source audio')
            fingerprint = (begin, end)
        return cls(data["id"], data["bus"], folder / data["asset"], data["source"], data["purpose"],
                   anchor, fixed, offset, impact, onset, gain, tolerance, search, correlation, fingerprint)

    def impact_at(self, landmarks):
        return (sample(landmarks[self.event]["pts"]) + self.offset if self.event is not None
                else self.fixed_sample)


def read_plan(path):
    plan = json.loads(path.read_text())
    if not isinstance(plan.get("landmarks"), dict) or not isinstance(plan.get("cues"), list):
        raise ValueError("plan must contain a landmarks object and cues array")
    cues = [Cue.from_json(data, path.parent) for data in plan["cues"]]
    if len({cue.id for cue in cues}) != len(cues):
        raise ValueError("cue ids must be unique")
    for cue in cues:
        if cue.event is not None and cue.event not in plan["landmarks"]:
            raise ValueError(f"{cue.id}: unknown visual landmark {cue.event}")
    for bus in plan.get("bus_gain_db", {}):
        if bus not in BUSES:
            raise ValueError(f"unknown bus {bus}")
    return plan, cues


def resolved_cues(plan_path, picture):
    plan, cues = read_plan(plan_path)
    landmarks = resolve_landmarks(picture, plan["landmarks"], plan_path.parent)
    rows = []
    for cue in cues:
        impact = cue.impact_at(landmarks)
        rows.append({
            "id": cue.id, "event": cue.event, "bus": cue.bus, "purpose": cue.purpose,
            "source": cue.provenance, "event_frame": landmarks[cue.event]["frame"] if cue.event else None,
            "offset_samples": cue.offset, "asset_start_sample": impact - cue.impact,
            "onset_marker_sample": impact - cue.impact + cue.onset, "impact_sample": impact,
        })
    return plan, cues, landmarks, rows


def landmark_rows(landmarks):
    return {key: {**match, "pts": str(match["pts"]), "sample": sample(match["pts"])}
            for key, match in landmarks.items()}


def silence_ranges(plan, landmarks, count):
    for quiet in plan.get("silence", []):
        start = sample(landmarks[quiet["start_event"]]["pts"]) if "start_event" in quiet else sample(Fraction(str(quiet["start_s"])))
        end = sample(landmarks[quiet["end_event"]]["pts"]) if "end_event" in quiet else sample(Fraction(str(quiet["end_s"])))
        if not 0 <= start < end <= count or not quiet["purpose"].strip():
            raise ValueError("silence must have a purpose and fit within picture")
        limit = float(quiet.get("max_peak_dbfs", -55))
        if not -120 <= limit < 0:
            raise ValueError("silence max_peak_dbfs must be between -120 and 0")
        yield start, end, limit, quiet["purpose"]


def mix(plan_path, picture, output, *, replace_audio=False):
    picture_hash = sha256(picture)
    plan_hash = sha256(plan_path)
    stream, duration = picture_track(picture)
    streams = probe(picture, "-show_streams")["streams"]
    if any(track["codec_type"] == "audio" for track in streams) and not replace_audio:
        raise ValueError("picture contains audio; classify it before using --replace-audio")
    plan, cues, landmarks, rows = resolved_cues(plan_path, picture)
    count = sample(duration)
    stems = {bus: np.zeros((count, 2), dtype=np.float32) for bus in BUSES}
    assets = {}
    names = ("mix.mp4", "mix.wav", "manifest.json", *(f"{bus}.wav" for bus in BUSES))
    input_paths = {picture.resolve(), plan_path.resolve(), *(cue.asset.resolve() for cue in cues)}
    input_paths.update((plan_path.parent / entry["template"]).resolve()
                       for entry in plan["landmarks"].values() if "template" in entry)
    if input_paths & {(output / name).resolve() for name in names}:
        raise ValueError("output conflicts with the picture, plan or source assets")
    # Validate sources and bounds before overwriting any previous render.
    for cue, row in zip(cues, rows):
        if cue.asset not in assets:
            asset_hash = sha256(cue.asset)
            assets[cue.asset] = (decode(cue.asset), asset_hash)
        audio, asset_hash = assets[cue.asset]
        start = row["asset_start_sample"]
        end = start + len(audio)
        if not 0 <= start < end <= count or cue.impact >= len(audio):
            raise ValueError(f"{cue.id}: asset or impact extends outside picture; trim or refit explicitly")
        row.update(asset_sha256=asset_hash, asset_end_sample=end, gain_db=cue.gain_db)
        stems[cue.bus][start:end] += audio * 10 ** (cue.gain_db / 20)
    for bus, audio in stems.items():
        level = float(plan.get("bus_gain_db", {}).get(bus, 0))
        if not math.isfinite(level) or not -96 <= level <= 24:
            raise ValueError(f"{bus}: invalid bus gain")
        audio *= 10 ** (level / 20)
    master = sum(stems.values())
    peak = float(np.max(np.abs(master)))
    if peak > 10 ** (-1 / 20):
        raise ValueError(f"PCM peak {db(peak)} dBFS exceeds -1 dBFS; adjust gain")
    for start, end, limit, purpose in silence_ranges(plan, landmarks, count):
        if np.max(np.abs(master[start:end])) > 10 ** (limit / 20):
            raise ValueError(f"planned silence contains audio ({purpose})")
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".sound-", dir=output) as temporary:
        staging = Path(temporary)
        for bus, audio in stems.items():
            wavfile.write(staging / f"{bus}.wav", RATE, audio)
        wavfile.write(staging / "mix.wav", RATE, master)
        mux(picture, staging / "mix.wav", staging / "mix.mp4")
        stable_inputs = {picture: picture_hash, plan_path: plan_hash,
                         **{asset: signature for asset, (_, signature) in assets.items()}}
        if any(sha256(path) != signature for path, signature in stable_inputs.items()):
            raise ValueError("picture, plan or audio changed during the render; retry with a stable cut")
        manifest = {
            "picture_sha256": picture_hash, "plan_sha256": plan_hash,
            "mix_sha256": sha256(staging / "mix.wav"),
            "export_sha256": sha256(staging / "mix.mp4"),
            "picture_time_base": stream["time_base"], "picture_duration": str(duration),
            "sample_rate": RATE, "sample_count": count, "pcm_peak_dbfs": db(peak),
            "stems": {bus: sha256(staging / f"{bus}.wav") for bus in BUSES},
            "landmarks": landmark_rows(landmarks), "cues": rows,
        }
        dump(staging / "manifest.json", manifest)
        # Publish the binding manifest only after the other files have been written.
        for name in names:
            if name != "manifest.json":
                (staging / name).replace(output / name)
        (staging / "manifest.json").replace(output / "manifest.json")
    return manifest
