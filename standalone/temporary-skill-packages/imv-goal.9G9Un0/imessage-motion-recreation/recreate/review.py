"""Check that a decoded candidate closes every frozen shot criterion."""
from hashlib import sha256
import json
import os
from pathlib import Path

from media import MediaError, digest


def frame_span(span, start, end):
    return (isinstance(span, list) and len(span) == 2
            and all(type(frame) is int for frame in span)
            and start <= span[0] <= span[1] <= end)


def overlapping(spans, start, end):
    return [span for span in spans if span[0] <= end and span[1] >= start]


def shot_criteria(plan):
    count = plan["frame_count"]
    shots = plan["shots"]
    if type(count) is not int or count <= 0 or not isinstance(shots, list) or not shots:
        raise MediaError("The review plan needs a positive frame count and a complete shot list")
    next_frame = 0
    criteria = {}
    for shot in shots:
        shot_id, span, checks = (shot[key] for key in ("id", "frames", "checks"))
        if not isinstance(shot_id, str) or not shot_id.strip() or shot_id in criteria:
            raise MediaError(f"Invalid or repeated shot ID: {shot_id!r}")
        if not frame_span(span, 0, count - 1) or span[0] != next_frame:
            raise MediaError(f"{shot_id}: shots must cover every frame in order without gaps or overlaps")
        if not isinstance(checks, dict) or not checks:
            raise MediaError(f"{shot_id}: declare at least one observable visual check")
        for check_id, check in checks.items():
            if not check_id.strip() or not frame_span(check["frames"], *span):
                raise MediaError(f"{shot_id}/{check_id}: check must cover frames inside its shot")
            if not isinstance(check["target"], str) or not check["target"].strip():
                raise MediaError(f"{shot_id}/{check_id}: missing visual target")
            if "region" in check and (not isinstance(check["region"], str) or not check["region"].strip()):
                raise MediaError(f"{shot_id}/{check_id}: invalid comparison region")
        criteria[shot_id] = checks
        next_frame = span[1] + 1
    if next_frame != count:
        raise MediaError("The review plan omits the end of the film")
    return criteria


def review_inputs(plan_path, report_path):
    plan_path, report_path = map(Path, (plan_path, report_path))
    plan_bytes = plan_path.read_bytes()
    report_bytes = report_path.read_bytes()
    plan = json.loads(plan_bytes)
    report = json.loads(report_bytes)
    criteria = shot_criteria(plan)
    if not report.get("decode_completed") or report["reference"]["sha256"] != plan["reference_sha256"]:
        raise MediaError("A completed comparison of the planned reference is required")
    if report["checks_sha256"] != plan["comparison_checks_sha256"]:
        raise MediaError("The comparison used different thresholds or regions from the review plan")
    if report["reference"]["clock"]["frames"] != plan["frame_count"]:
        raise MediaError("The plan and decoded reference cover different frame counts")
    return plan, report, criteria, sha256(plan_bytes).hexdigest(), sha256(report_bytes).hexdigest()


def prepare_review(plan_path, report_path, output):
    plan, report, criteria, plan_hash, report_hash = review_inputs(plan_path, report_path)
    folder, output_dir = Path(report_path).parent, Path(output).parent
    viewer = folder / "index.html"
    failed_spans = report.get("pixel_equality", {}).get("different_spans", [])
    tasks = []
    for shot_id, checks in criteria.items():
        for check_id, check in checks.items():
            start, end = check["frames"]
            stats = check_region(report, shot_id, check_id, check)
            first = stats.get("first_difference") or {}
            worst = stats.get("worst_pixel_difference") or {}
            step = stats.get("worst_step") or {}
            frame = worst.get("frame", start)
            pixel_failures = overlapping(stats.get("failed_spans", []), start, end)
            motion_failures = overlapping(stats.get("failed_step_spans", []), start, end)
            tasks.append({
                "shot": shot_id, "check": check_id, "frames": check["frames"], "target": check["target"],
                "region": check.get("region"),
                "priority": "high" if pixel_failures or motion_failures or overlapping(failed_spans, start, end) else "normal",
                "failed_pixel_spans": pixel_failures, "failed_motion_spans": motion_failures,
                "first_difference": first.get("frame"), "worst_frame": worst.get("frame"),
                "worst_crop_mae": worst.get("mae"),
                "worst_step": stats.get("worst_step"),
                "evidence_ids": [
                    name for name, record in report.get("evidence", {}).items()
                    if record["region"] == check.get("region")
                    and overlapping(record["spans"], start, end)
                ],
                "crop_evidence": [os.path.relpath(folder / item["crop"], output_dir)
                                  for item in (first, worst, step) if "crop" in item],
                "viewer": f"{os.path.relpath(viewer, output_dir)}?frame={frame}" if viewer.is_file() else None,
            })
    tasks.sort(key=lambda task: (task["priority"] != "high", task["region"] is None,
                                 -max(task["worst_crop_mae"] or 0, (task["worst_step"] or {}).get("mae", 0))))
    return {
        "plan_sha256": plan_hash, "comparison_sha256": report_hash,
        "candidate_sha256": report["candidate"]["sha256"],
        "instructions": "Open the linked evidence at native size. Step consecutive frames for motion. Record only inspected results.",
        "tasks": tasks, "results": {},
    }


def check_region(report, shot_id, check_id, check):
    if "region" not in check:
        return {}
    region = check["region"]
    stats = report["regions"].get(region)
    if stats is None or not frame_span(check["frames"], *stats["frames"]):
        raise MediaError(f"{shot_id}/{check_id}: region {region!r} must cover the planned window")
    return stats


def evidence_covers(ids, span, region, evidence, directory, verified):
    if not isinstance(ids, list) or not ids or not all(isinstance(name, str) for name in ids):
        return False
    remaining = set(range(span[0], span[1] + 1))
    for name in ids:
        record = evidence.get(name)
        if record is None or record["region"] != region:
            return False
        if name not in verified:
            file = (directory / name).resolve()
            verified[name] = file.is_relative_to(directory) and file.is_file() and digest(file) == record["sha256"]
        if not verified[name] or not overlapping(record["spans"], *span):
            return False
        for start, end in record["spans"]:
            remaining.difference_update(range(start, end + 1))
    return not remaining


def verify_review(plan_path, review_path, report_path, candidate, *, scoped=False):
    review_path = Path(review_path)
    review = json.loads(review_path.read_text(encoding="utf-8"))
    plan, report, criteria, plan_hash, report_hash = review_inputs(plan_path, report_path)
    diagnostics = plan.get("rgb_diagnostics", [])
    if not isinstance(diagnostics, list) or any(
        key not in ("whole_frame_mae", "local_tile_mae") and key not in report["regions"]
        for key in diagnostics
    ):
        raise MediaError("Only named RGB checks in the comparison may be marked diagnostic")
    candidate_hash = digest(candidate)
    if review["plan_sha256"] != plan_hash or review["candidate_sha256"] != candidate_hash:
        raise MediaError("The visual review belongs to a different plan or candidate")
    if report["candidate"]["sha256"] != candidate_hash:
        raise MediaError("The comparison belongs to a different candidate")
    if "comparison_sha256" in review and review["comparison_sha256"] != report_hash:
        raise MediaError("The visual review belongs to a different comparison")

    required_failures = []
    if "comparison_sha256" not in review:
        required_failures.append({"check": "unbound_review"})
    for failure in report["failures"]:
        name = failure["check"]
        if name in ("whole_frame_mae", "local_tile_mae") and name in diagnostics:
            continue
        if name == "region" and failure["id"] in diagnostics:
            continue
        required_failures.append(failure)
    if report["compared_frames"] != plan["frame_count"]:
        required_failures.append({"check": "incomplete_comparison"})
    pixels = report.get("pixel_equality")
    pixel_failed_shots = []
    if not scoped:
        if report.get("exact_clock") is not True:
            if not any(item["check"] == "exact_clock" for item in required_failures):
                required_failures.append({"check": "exact_clock_required"})
        if pixels is None:
            required_failures.append({"check": "pixel_equality_unmeasured"})
        elif pixels["identical_frames"] != plan["frame_count"]:
            if not any(item["check"] == "pixel_equality" for item in required_failures):
                required_failures.append({"check": "pixel_equality", "first_difference": pixels["first_difference"]})
            pixel_failed_shots = [shot["id"] for shot in plan["shots"]
                                  if overlapping(pixels["different_spans"], *shot["frames"])]

    results = review["results"]
    if not isinstance(results, dict) or results.keys() - criteria.keys():
        raise MediaError("Visual review contains shots outside the plan")
    open_shots = {}
    evidence = report.get("evidence", {}) if "comparison_sha256" in review else {}
    evidence_directory = Path(report_path).resolve().parent
    verified_evidence = {}
    for shot_id, checks in criteria.items():
        reviewed = results.get(shot_id, {})
        if not isinstance(reviewed, dict) or reviewed.keys() - checks.keys():
            raise MediaError(f"{shot_id}: visual review contains checks outside the plan")
        for check_id, check in checks.items():
            stats = check_region(report, shot_id, check_id, check)
            result = reviewed.get(check_id, {"verdict": "unverified"})
            verdict = result["verdict"]
            if verdict not in ("pass", "fail", "unverified"):
                raise MediaError(f"{shot_id}/{check_id}: invalid verdict {verdict!r}")
            if verdict != "unverified":
                frames = result.get("frames")
                observation = result.get("observation")
                if (not frame_span(frames, *check["frames"])
                        or not isinstance(observation, str) or not observation.strip()
                        or (verdict == "pass" and frames != check["frames"])
                        or not evidence_covers(result.get("evidence_ids"), frames, check.get("region"),
                                               evidence, evidence_directory, verified_evidence)):
                    verdict = "unverified"
            if overlapping(stats.get("failed_step_spans", []), *check["frames"]) or (
                overlapping(stats.get("failed_spans", []), *check["frames"])
                and (not scoped or check["region"] not in diagnostics)
            ):
                verdict = "fail"
            if verdict != "pass":
                open_shots.setdefault(shot_id, {})[check_id] = verdict

    failed_shots = set(open_shots).union(pixel_failed_shots)
    verdict = "FAIL" if failed_shots or required_failures else ("SCOPED_PASS" if scoped else "PASS")
    return {
        "verdict": verdict,
        "scope": "scoped" if scoped else "exact",
        "candidate_sha256": candidate_hash,
        "plan_sha256": plan_hash,
        "shot_count": len(criteria),
        "passed_shots": len(criteria) - len(failed_shots),
        "observed_passed_shots": len(criteria) - len(open_shots),
        "open_shots": open_shots,
        "pixel_failed_shots": pixel_failed_shots,
        "required_comparison_failures": required_failures,
    }
