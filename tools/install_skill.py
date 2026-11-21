#!/usr/bin/env python3
"""Link this checked-out skill into a local agent skill folder."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--dest", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = root / "skill" / "imessage-motion-recreation"
if not (source / "SKILL.md").is_file():
    raise SystemExit("Complete skill folder is missing")

skill_home = Path.home() / ".agents" / "skills"
dest = args.dest.expanduser().absolute() if args.dest else skill_home / "imessage-video-codex-trial"
legacy = skill_home / "imessage-motion-recreation"
if args.dest is None and not (dest.exists() or dest.is_symlink()):
    if legacy.is_symlink() and legacy.resolve() == source:
        dest = legacy

if dest.exists() or dest.is_symlink():
    if dest.resolve() != source:
        raise SystemExit(f"Destination already exists and differs; refusing to overwrite: {dest}")
else:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.symlink_to(source, target_is_directory=True)

print(json.dumps({
    "skill_path": str(source),
    "installed_link": str(dest),
    "overwritten": False,
    "internet_used": False,
}, indent=2))
