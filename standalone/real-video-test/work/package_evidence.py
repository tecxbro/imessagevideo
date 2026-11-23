import csv
from html import escape
import json
from pathlib import Path
import shutil
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path.cwd()
OUT = ROOT / "outputs"
WORK = ROOT / "work"
RUN = WORK / "final-run"
REVIEW = WORK / "reviewer"
REV = subprocess.check_output(["git", "-C", str(WORK / "imessagevideo"), "rev-parse", "HEAD"], text=True).strip()


def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def tree(source, destination, ignored=()):
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", ".*lock", *ignored))


def make_zip(destination, source):
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for item in sorted(source.rglob("*")):
            if item.is_file() and "__pycache__" not in item.parts and not item.name.startswith("."):
                archive.write(item, item.relative_to(source))


with ZipFile(OUT / "iMessage-Video-skill.zip") as archive:
    assert archive.testzip() is None
    archive.extractall(OUT / "skill")

for name in ["01-photonhq", "02-danieltian", "03-photon-mini", "04-poke", "05-linq",
             "06-gallery", "unseen-complete", "linq-fixed-swipe", "linq-excerpt-480x360"]:
    copy(WORK / "inputs" / (name + ".mp4"), OUT / "inputs" / (name + ".mp4"))
copy(WORK / "inputs/unseen-complete-provenance.md", OUT / "inputs/unseen-complete-provenance.md")
tree(WORK / "inputs/transfer-photos", OUT / "inputs/transfer-photos")
tree(RUN / "recreation", OUT / "recreation", ("intake", "reopened", "editable", "candidate",
                                               "two-frame-delay-picture.mp4*", "two-frame-delay.scene.json"))
tree(RUN / "linq-final", OUT / "linq", ("intake",))
tree(RUN / "concert", OUT / "concert", ("intake",))
tree(RUN / "edit-evidence", OUT / "edit")
for pitch in (OUT / "concert").glob("pitch-*.md"):
    pitch.write_text(pitch.read_text().replace("../imessagevideo/skill/imessage-video/", "../skill/imessage-video/"))
make_zip(OUT / "concert-editable-project.zip", OUT / "concert")
make_zip(OUT / "learned-motion-library.zip", RUN / "library")

for relative in ("FINAL-REVIEW.md", "audit_catalog.py", "catalog_sheets.py", "make_unseen.py",
                 "measure_linq.py", "review_unseen.py", "review_direction.py", "reproduce_restart.sh"):
    source = REVIEW / relative
    if source.is_file():
        copy(source, OUT / "review" / relative)
for relative in ("first-unseen", "second-unseen", "muxed-unseen", "final-controls", "direction-review",
                 "direction-clean", "final-linq-footer", "restart-reproduced", "linq-visual", "toggle-final"):
    tree(REVIEW / relative, OUT / "review" / relative)
for relative in ("linq/source-tracking.csv", "final-recognition/alignment/report.json",
                 "final-recognition/alignment/frames.csv", "final-recognition/alignment/worst.png"):
    copy(REVIEW / relative, OUT / "review" / relative)
for relative in ("direct.json", "browse.json", "reply.json", "linq.json", "recreate.json"):
    copy(WORK / "baseline" / relative, OUT / "review/baseline" / relative)
copy(WORK / "novel/pilot.mp4", OUT / "review/baseline/first-recreation.mp4")
tree(WORK / "novel/pilot-evidence", OUT / "review/baseline/first-recreation-comparison")
with (OUT / "review/baseline/linq-original-seed.mp4").open("wb") as preview:
    subprocess.run(["git", "-C", str(WORK / "imessagevideo"), "show",
                    "HEAD^:skill/imessage-video/assets/seed/previews/photos-under-fixed-heading.mp4"], stdout=preview, check=True)

catalog = OUT / "catalog"
review_rows = []
for line in (REVIEW / "catalog-final/results.jsonl").read_text().splitlines():
    row = json.loads(line)
    rid = row["id"]
    assert row["status"] == "comparison within limits" and row["structure_match"] and row["frame_count"] == 72
    assert row["replay_peak_change"] > 0
    tree(REVIEW / "catalog-final" / rid, catalog / rid, ("commands.log",))
    review_rows.append(dict(row, preview=f"{rid}/preview.mp4", replay=f"{rid}/project/replay.mp4",
                            code=f"{rid}/project/scene.json", report=f"{rid}/compare/report.json",
                            strip=f"{rid}/strip.jpg", kind="Seed"))
assert len(review_rows) == 77
tree(REVIEW / "catalog-final/contact-sheets", catalog / "contact-sheets")
for rid in ("toggle-thumb-then-tint", "tether-extend-then-pivot-dock"):
    source = RUN / "library/entries" / rid
    dest = catalog / rid
    copy(source / "preview.mp4", dest / "preview.mp4")
    if rid.startswith("toggle"):
        tree(REVIEW / "toggle-final/project", dest / "project")
        copy(REVIEW / "toggle-final/portable-rerender.mp4", dest / "project/replay.mp4")
        tree(REVIEW / "toggle-final/compare", dest / "compare")
        copy(REVIEW / "toggle-final/decoded-motion.png", dest / "strip.png")
        review_dir = dest / "compare"
        kind = "Shipped learned"
    else:
        tree(RUN / "recreation/editable", dest / "project")
        copy(RUN / "recreation/reopened/fresh-render.mp4", dest / "project/replay.mp4")
        compare_dir = dest / "compare"
        subprocess.run([str(WORK / "venv/bin/python"),
                        str(OUT / "skill/imessage-video/scripts/frames.py"),
                        str(dest / "preview.mp4"), str(dest / "project/replay.mp4"), "--out", str(compare_dir),
                        "--require-structure-match", "--max-pts-error-ms", "0", "--max-mae", "0"],
                       check=True, stdout=subprocess.DEVNULL)
        copy(REVIEW / "muxed-unseen/frame-pairs.jpg", dest / "strip.jpg")
        review_dir = compare_dir
        kind = "New in benchmark"
    src = json.loads((source / "recipe.json").read_text())
    comparison = json.loads((review_dir / "report.json").read_text())
    assert comparison["limits_passed"] and comparison["metrics"]["full"]["max_frame_mae"] == 0
    review_rows.append({
        "id": rid, "kind": kind, "status": "comparison within limits",
        "preview": f"{rid}/preview.mp4", "replay": f"{rid}/project/replay.mp4", "code": f"{rid}/project/scene.json",
        "report": f"{rid}/compare/report.json",
        "strip": f"{rid}/strip.{'png' if rid.startswith('toggle') else 'jpg'}",
        "moves": src["description"], "fixed": ", ".join(src["fixed"]),
        "frame_count": comparison["compared_frames"], "errors": comparison["metrics"]["full"],
    })

with (catalog / "results.csv").open("w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(("motion_id", "scope", "result", "decoded_frames", "worst_rgb_mae",
                     "preview", "fresh_replay", "editable_scene", "frame_report"))
    writer.writerows((r["id"], r["kind"], "PASS", r["frame_count"], r["errors"]["max_frame_mae"],
                      r["preview"], r["replay"], r["code"], r["report"]) for r in review_rows)
(catalog / "results.json").write_text(json.dumps(review_rows, ensure_ascii=False, indent=2) + "\n")

html = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>iMessage Video motion audit</title>
<style>
:root{color-scheme:dark;--background:#101520;--panel:#1b2637;--ink:#f2f7ff;--muted:#b6c7df;--link:#97cafb}
body{margin:auto;max-width:1120px;padding:32px 24px 68px;font:16px/1.5 system-ui,sans-serif;background:var(--background);color:var(--ink)}
header{padding-bottom:32px} h1{margin-bottom:8px;font-size:clamp(30px,5vw,47px);line-height:1.12}
h2{font-size:1.2rem;margin:0 0 8px} p{max-width:70ch;margin:8px 0} a{color:var(--link)}
input{box-sizing:border-box;width:min(420px,100%);margin:20px 0 4px;padding:11px;font:inherit;border:1px solid #788ba2;border-radius:8px;background:var(--panel);color:var(--ink)}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,375px),1fr));gap:16px}
article{padding:18px;background:var(--panel);border-radius:12px} .muted{color:var(--muted)} .videos{display:grid;grid-template-columns:1fr 1fr;gap:10px}
video{width:100%;aspect-ratio:3/2;background:#101520;border-radius:6px} .links{display:flex;gap:14px;flex-wrap:wrap;margin-top:12px}
</style><body>
<header><h1>iMessage Video motion audit</h1><p>78 shipped motions passed. The newly learned tether makes 79 verified entries in the benchmark library.</p>
<p><a href="../Report.md">Verification report</a> · <a href="results.csv">Results CSV</a></p>
<label for="filter">Find a motion</label><br><input id="filter" type="search" placeholder="Try swipe, toggle or tether">
</header><main>
"""
for row in review_rows:
    for name in ("preview", "replay", "code", "report", "strip"):
        assert (catalog / row[name]).is_file(), row[name]
    html += f"""<article><h2>{escape(row['id'].replace('-', ' '))}</h2>
<p class="muted">{escape(row['kind'])} · {row['frame_count']} frames · PASS</p>
<p>{escape(row['moves'])}</p><p class="muted">Fixed layers — {escape(row['fixed'])}</p>
<div class="videos"><div><video controls preload="none" src="{row['preview']}" aria-label="Saved preview"></video><div>Saved preview</div></div>
<div><video controls preload="none" src="{row['replay']}" aria-label="Fresh replay"></video><div>Fresh replay</div></div></div>
<div class="links"><a href="{row['code']}">Editable scene</a><a href="{row['report']}">Comparison</a><a href="{row['strip']}">Frame strip</a></div></article>
"""
html += """</main><script>
const input = document.getElementById('filter');
const cards = Array.from(document.querySelectorAll('article'));
input.addEventListener('input', () => {
  const query = input.value.toLowerCase().trim();
  for (const card of cards) card.hidden = !card.textContent.toLowerCase().includes(query);
});
</script></body></html>
"""
(catalog / "index.html").write_text(html)
(OUT / "revision.txt").write_text(REV + "\n")
