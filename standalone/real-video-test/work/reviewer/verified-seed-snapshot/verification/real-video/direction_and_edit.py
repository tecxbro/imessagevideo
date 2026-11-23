"""Drive the exact brief and edit through the skill's documented commands."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

SKILL = Path(__file__).resolve().parents[2]
BRIEF = "Make an iMessage video about two friends getting concert tickets."
EDIT = "Change this message to ‘Meet at the doors’ and replace this shot’s motion with the swipe from this second clip."


def run(script, *arguments, expected=0):
    command = [sys.executable, str(SKILL / "scripts" / script), *map(str, arguments)]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != expected:
        raise RuntimeError(f"{command}\n{result.stdout}\n{result.stderr}")
    return result.stdout if expected == 0 else result.stderr


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def decide(output, library, request, *options):
    result = json.loads(run("decide.py", request, "--workdir", output.parent / "intake",
                            "--library", library, *options))
    write(output, result)
    return result


def ticket_art(root):
    assets = root / "art"
    assets.mkdir()
    cards = [
        ("FLOOR", "Standing near the stage", "$56", "#151b35", "#c2deff"),
        ("BALCONY", "A clear view from above", "$44", "#3c1536", "#ffb5e9"),
        ("SIDE BOX", "A reserved seat", "$62", "#133b34", "#c2f5de"),
        ("ENTRY", "Doors open at 7:00 PM", "7 PM", "#352419", "#ffc98d"),
    ]
    for index, (title, detail, price, background, ink) in enumerate(cards):
        size = (592, 394)
        art = Image.new("RGB", size, background)
        draw = ImageDraw.Draw(art)
        draw.rectangle((28, 25, 564, 367), outline=ink, width=2)
        for x in range(43, 558, 15):
            draw.line((x, 282, x + 7, 282), fill=ink, width=2)
        for x, y, text, points in ((48, 53, "AFTERGLOW LIVE", 26), (48, 104, title, 65),
                                   (48, 206, detail, 25), (48, 301, price, 37)):
            draw.text((x, y), text, font=ImageFont.load_default(size=points), fill=ink)
        art.save(assets / f"ticket-{index + 1}.png")
    return [f"art/ticket-{i + 1}.png" for i in range(len(cards))]


def shot(shot_id, frames, purpose, visual, motion, copy, copy_key="copy", **fields):
    return {"id": shot_id, "frames": frames, "purpose": purpose, "visual": visual,
            "motion": {"kind": "seed", "id": motion}, "copy": copy, "copy_key": copy_key,
            "bindings": {"heading": "Jo + Tessa", **fields}}


def prove(shots, plan, shot_id, root, label, representative_frame):
    proof = root / ("proof-" + label)
    shots("render-shot", plan, shot_id, proof)
    still = proof / "board.png"
    subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(proof / "preview.mp4"), "-vf",
        f"select=eq(n\\,{representative_frame})", "-frames:v", "1", str(still),
    ], check=True)
    patch = write(root / f"attach-{label}.json", {
        "preview": f"{proof.name}/preview.mp4", "code": f"{proof.name}/scene.json",
        "board": f"{proof.name}/board.png",
    })
    current = root / ("plan-" + label + ".json")
    shots("revise", plan, shot_id, patch, current)
    return current


def revision(shots, plan, pitch):
    shots("pitch", plan, "--out", pitch)
    return re.search(r"Plan revision `([a-f0-9]+)`", pitch.read_text())[1]


def exercise_direction(root, library):
    def shots(*args, **kwargs):
        return run("shots.py", "--library", library, *args, **kwargs)

    first = decide(root / "initial-request.json", library, BRIEF)
    assert first["next"] == "clarify_missing_brief" and first["question"]
    browse = decide(root / "browse-decision.json", library, BRIEF, "--brief-ready", "--motion", "browse ticket options")
    browse_id = browse["motion_choices"]["seed"][0]["id"]
    assert browse_id == "photos-under-fixed-heading"
    photos = ticket_art(root)
    target = "Floor or balcony?"
    screenplay = write(root / "brief.json", {
        "mode": "director", "fps": 30,
        "brief": "Jo and Tessa get Afterglow tickets. Show how they decide where to sit and confirm both tickets.",
        "shots": [
            shot("open", 108, "Establish a concrete invitation.", "Jo sends a draft into the conversation.",
                 "draft-send-flight", "Tickets for Afterglow?", reply="Presale just opened."),
            shot("choice", 96, "Give the two friends a choice.", "Browse the available tickets beneath the fixed event heading.",
                 browse_id, "Afterglow · Friday", "heading", detail="Compare the venue sections", photos=photos),
            shot("payoff", 108, "Confirm that both friends have a ticket.",
                 "The confirmation leaves the composer and settles below the plan.",
                 "draft-send-flight", "Got both tickets!", reply="Floor works for me."),
        ],
    })
    plan = root / "plan.json"
    shots("create", screenplay, plan)
    plan = prove(shots, plan, "open", root, "open", 82)
    plan = prove(shots, plan, "choice", root, "browse", 40)
    plan = prove(shots, plan, "payoff", root, "payoff", 82)
    browse_revision = revision(shots, plan, root / "pitch-browse.md")
    blocked = shots("render-cut", plan, root / "unapproved-browse.mp4", expected=1)
    assert "must be approved" in blocked and not (root / "unapproved-browse.mp4").exists()

    reply = decide(root / "reply-decision.json", library, BRIEF, "--brief-ready", "--motion",
                   "show which message I’m replying to")
    reply_id = reply["motion_choices"]["seed"][0]["id"]
    assert reply_id == "swipe-to-quote" and reply_id != browse_id
    patch = write(root / "reply-goal.json", {
        "purpose": "Make it clear exactly which earlier message the answer refers to.",
        "visual": "Tessa drags only the seating question. It returns to its slot while the quoted copy opens above the composer.",
        "motion": {"kind": "seed", "id": reply_id}, "copy": target, "copy_key": "copy",
        "bindings": {"heading": "Jo + Tessa", "reply": "Tickets for Afterglow?", "title": "Replying to Jo"},
    })
    revised = root / "plan-reply.json"
    shots("revise", plan, "choice", patch, revised)
    replied = prove(shots, revised, "choice", root, "reply", 74)
    reply_revision = revision(shots, replied, root / "pitch-reply.md")
    blocked_reply = shots("render-cut", replied, root / "unapproved-reply.mp4", expected=1)
    assert "must be approved" in blocked_reply and not (root / "unapproved-reply.mp4").exists()
    stale = shots("approve", replied, browse_revision, root / "stale-approval.json",
                  "--response", "Looks good", expected=1)
    assert "has changed" in stale and not (root / "stale-approval.json").exists()

    response = "Approved. Show which message I’m replying to, then finish the film."
    approved = root / "plan-reply-approved.json"
    shots("approve", replied, reply_revision, approved, "--response", response)
    ready = json.loads(shots("check", approved, "--for-production"))
    assert ready["approved"] and not ready["open_work"]
    write(root / "approval-evidence.json", {
        "simulated": True, "initial_skill_question": first["question"],
        "simulated_response": "No reference. Show two friends comparing seats and getting tickets.",
        "first_goal": "browse ticket options", "first_motion": browse_id, "first_revision": browse_revision,
        "first_production_attempt": blocked.strip(),
        "revised_goal": "show which message I’m replying to", "revised_motion": reply_id, "revised_revision": reply_revision,
        "revised_production_attempt": blocked_reply.strip(), "stale_approval_attempt": stale.strip(),
        "final_simulated_approval": response, "production_check": ready,
    })
    movie = root / "concert-tickets.mp4"
    shots("render-cut", approved, movie)
    return approved, movie, photos


def exercise_edit(root, library, approved, movie, photos, donor):
    def shots(*args, **kwargs):
        return run("shots.py", "--library", library, *args, **kwargs)

    entry = decide(root / "edit-request.json", library, EDIT, "--video", movie, "--donor", donor,
                   "--project", approved, "--motion", "Slide the photos beneath a fixed heading")
    assert entry["intent"] == "edit" and [x["role"] for x in entry["sources"]] == ["edit-target", "motion-donor"]
    patch = write(root / "donor-edit.json", {
        "purpose": "Show the venue options changing while Jo’s meeting message stays visible.",
        "visual": "Keep the title and ‘Meet at the doors’ bubble pinned. Swipe the clipped ticket strip to the left with the Linq restaurant-photo timing.",
        "motion": {"kind": "seed", "id": "photos-under-fixed-heading"},
        "copy": "Meet at the doors", "copy_key": "message",
        "bindings": {"heading": "Jo + Tessa", "detail": "Afterglow · Friday", "photos": photos},
    })
    edit = root / "plan-edit.json"
    shots("revise", approved, "choice", patch, edit)
    edit = prove(shots, edit, "choice", root, "donor-edit", 52)
    edit_revision = revision(shots, edit, root / "pitch-edit.md")
    edit_approved = root / "plan-edit-approved.json"
    shots("approve", edit, edit_revision, edit_approved,
          "--response", "Simulated approval: use the donor swipe and exact requested message.")
    shots("render-cut", edit_approved, root / "meet-at-the-doors.mp4")
    old, new = (json.loads(path.read_text())["plan"]["shots"] for path in (approved, edit_approved))
    assert old[0] == new[0] and old[2] == new[2]
    return edit_approved


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("library", type=Path)
    parser.add_argument("donor", type=Path)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    approval, film, art = exercise_direction(root, args.library.resolve())
    exercise_edit(root, args.library.resolve(), approval, film, art, args.donor.resolve())
