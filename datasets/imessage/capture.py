"""Validate a capture record, its exact video clock, and its reviewed grant."""

import hashlib
import json
import re
import subprocess
from datetime import date
from fractions import Fraction
from pathlib import Path

DATASET = Path(__file__).resolve().parent
ROOT = DATASET.parent.parent
ID = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")
SHA256 = re.compile(r"[0-9a-f]{64}")
SCOPE = "private-repo-and-team-analysis"
CONTAINERS = {".mp4": "mov", ".mov": "mov", ".mkv": "matroska", ".webm": "webm"}
BUFFER = 1024 * 1024


class IntakeError(Exception):
    """An intake decision that requires no traceback."""


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise IntakeError("duplicate JSON field")
        result[key] = value
    return result


def invalid_constant(_):
    raise IntakeError("non-finite JSON value")


def parse_json(data):
    return json.loads(data, object_pairs_hook=unique_keys, parse_constant=invalid_constant)


def fields(value, expected, label):
    if not isinstance(value, dict) or value.keys() != set(expected.split()):
        raise IntakeError(f"{label} must contain exactly: {expected}")


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise IntakeError(f"{label} needs a nonempty text value")


def safe_id(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise IntakeError("capture id must be lowercase alphanumeric with optional hyphens")
    return value


def sha256(value, label):
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise IntakeError(f"{label} needs a lowercase SHA-256")
    return value


def file_info(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        while chunk := source.read(BUFFER):
            size += len(chunk)
            digest.update(chunk)
    return {"bytes": size, "sha256": digest.hexdigest()}


def record_digest(record):
    return hashlib.sha256(json_bytes(record)).hexdigest()


def integer(value, label):
    if type(value) is not int:
        raise IntakeError(f"{label} must be an integer")
    return value


def rational(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]*/[1-9][0-9]*", value):
        raise IntakeError(f"{label} must be a positive numerator/denominator")
    return Fraction(value)


def validate_record(record):
    fields(record, "schema_version id classification source rights device interaction media_sha256 clock range", "record")
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise IntakeError("unsupported capture record version")
    safe_id(record["id"])
    if record["classification"] not in ("native", "sandbox", "fixture"):
        raise IntakeError("classification must be native, sandbox or fixture")
    for name, expected in {
        "source": "reference method captured_on",
        "rights": "holder permission_ref scope",
        "device": "model os build",
    }.items():
        section = record[name]
        fields(section, expected, name)
        for key, value in section.items():
            nonempty(value, f"{name}.{key}")
    captured_on = record["source"]["captured_on"]
    if date.fromisoformat(captured_on).isoformat() != captured_on:
        raise IntakeError("source.captured_on must use YYYY-MM-DD")
    if record["rights"]["scope"] != SCOPE:
        raise IntakeError(f"rights.scope must cover {SCOPE}")
    sha256(record["media_sha256"], "media_sha256")

    clock = record["clock"]
    fields(clock, "time_base average_fps", "clock")
    for name, value in clock.items():
        rational(value, f"clock.{name}")

    span = record["range"]
    fields(span, "start_frame end_frame start_pts end_pts", "range")
    for name, value in span.items():
        integer(value, f"range.{name}")
    if not (0 <= span["start_frame"] < span["end_frame"] and span["start_pts"] < span["end_pts"]):
        raise IntakeError("range must cover at least two frames in time order")

    interaction = record["interaction"]
    fields(interaction, "name before action after landmarks layers", "interaction")
    for key in ("name", "before", "action", "after"):
        nonempty(interaction[key], f"interaction.{key}")
    if not isinstance(interaction["layers"], list) or not interaction["layers"]:
        raise IntakeError("interaction.layers must describe at least one layer")
    for item in interaction["layers"]:
        nonempty(item, "interaction layer")
    if not isinstance(interaction["landmarks"], list) or not interaction["landmarks"]:
        raise IntakeError("interaction.landmarks must identify at least one frame")
    previous = span["start_frame"] - 1
    names = set()
    for landmark in interaction["landmarks"]:
        fields(landmark, "name frame", "landmark")
        nonempty(landmark["name"], "landmark.name")
        frame = integer(landmark["frame"], "landmark.frame")
        if not previous <= frame <= span["end_frame"] or frame < span["start_frame"]:
            raise IntakeError("landmarks must be ordered and within the recorded range")
        if landmark["name"] in names:
            raise IntakeError("landmark names must be unique")
        names.add(landmark["name"])
        previous = frame


def probe(path):
    container = CONTAINERS.get(path.suffix.lower())
    if container is None:
        raise IntakeError("candidate needs an MP4, MOV, MKV or WebM suffix")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-protocol_whitelist", "file,pipe,crypto", "-f", container,
         "-select_streams", "V:0", "-show_frames", "-show_streams",
         "-show_entries", "frame=best_effort_timestamp:stream=time_base,avg_frame_rate,width,height",
         "-of", "json", str(path.resolve())],
        capture_output=True,
    )
    if result.returncode or result.stderr:
        raise IntakeError("FFprobe could not decode the candidate video")
    payload = parse_json(result.stdout)
    streams = payload.get("streams", [])
    frames = payload.get("frames", [])
    if len(streams) != 1 or not frames:
        raise IntakeError("candidate needs a decodable video track with frame timestamps")
    stream = streams[0]
    clock = {"time_base": stream.get("time_base"), "average_fps": stream.get("avg_frame_rate")}
    for name, value in clock.items():
        rational(value, f"decoded {name}")
    pts = [integer(frame.get("best_effort_timestamp"), "decoded PTS") for frame in frames]
    if any(left >= right for left, right in zip(pts, pts[1:])):
        raise IntakeError("decoded video PTS must increase in presentation order")
    return {
        "clock": clock, "frame_count": len(pts), "width": stream["width"], "height": stream["height"],
    }, pts


def verify_span(path, record):
    media, pts = probe(path)
    if any(Fraction(value) != Fraction(media["clock"][key]) for key, value in record["clock"].items()):
        raise IntakeError("recorded clock does not match the decoded video")
    span = record["range"]
    if span["end_frame"] >= len(pts):
        raise IntakeError("recorded frame range exceeds the decoded video")
    for boundary in ("start", "end"):
        actual = Fraction(pts[span[f"{boundary}_frame"]]) * Fraction(media["clock"]["time_base"])
        claimed = Fraction(span[f"{boundary}_pts"]) * Fraction(record["clock"]["time_base"])
        if actual != claimed:
            raise IntakeError(f"recorded {boundary} PTS does not match its decoded frame")
    media["landmark_pts"] = {
        item["name"]: pts[item["frame"]] for item in record["interaction"]["landmarks"]
    }
    return media


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, check=check)


def approval(record):
    # Review is a repository decision. Candidate-supplied or uncommitted grants are ignored.
    path = f"datasets/imessage/approvals/{record['id']}.json"
    result = git("show", f"HEAD:{path}", check=False)
    if result.returncode:
        raise IntakeError("no committed source and rights approval for this capture")
    grant = parse_json(result.stdout)
    fields(grant, "record_sha256 reviewer source_evidence rights_evidence", "approval")
    for key in ("reviewer", "source_evidence", "rights_evidence"):
        nonempty(grant[key], f"approval.{key}")
    if sha256(grant["record_sha256"], "approval.record_sha256") != record_digest(record):
        raise IntakeError("committed approval does not match the capture record")
    return {"path": path, "sha256": hashlib.sha256(result.stdout).hexdigest()}
