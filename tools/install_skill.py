#!/usr/bin/env python3
"""Link this checked-out local skill into a local agent skill folder."""
from pathlib import Path
import argparse, json

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--dest',type=Path,default=Path.home()/'.agents/skills/imessage-motion-recreation')
a=p.parse_args();root=Path(__file__).resolve().parents[1];source=root/'skill/imessage-motion-recreation';dest=a.dest.expanduser().absolute()
if not (source/'SKILL.md').is_file():raise SystemExit('Complete skill folder is missing')
if dest.exists() or dest.is_symlink():
    if dest.resolve()!=source:raise SystemExit('Destination already exists and differs; refusing to overwrite: '+str(dest))
else:
    dest.parent.mkdir(parents=True,exist_ok=True);dest.symlink_to(source,target_is_directory=True)
print(json.dumps({'skill_path':str(source),'installed_link':str(dest),'overwritten':False,'internet_used':False},indent=2))
