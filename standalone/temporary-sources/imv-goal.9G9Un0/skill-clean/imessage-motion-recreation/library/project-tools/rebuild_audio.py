#!/usr/bin/env python3
"""Rebuild UI in an isolated sandbox without overwriting accepted audio exports."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--example',required=True);p.add_argument('--with-music',action='store_true');p.add_argument('--sandbox',type=Path,required=True);a=p.parse_args()
 source=ROOT/'audio-recreation';sandbox=a.sandbox.resolve()
 if sandbox.exists() and any(sandbox.iterdir()):raise FileExistsError('Choose an empty isolated sandbox')
 sandbox.mkdir(parents=True,exist_ok=True);dest=sandbox/'audio-recreation';dest.mkdir(exist_ok=True)
 for name in ['scripts','synthesis']:
  shutil.copytree(source/name,dest/name)
 # Inputs are read-only links into the materialized pack; accepted outputs stay outside.
 for name in ['library','ui-cues','ai','mixes']:
  if (source/name).exists():(dest/name).symlink_to(source/name,target_is_directory=True)
 cmd=[sys.executable,str(dest/'scripts/render_ui.py'),'--id',a.example]
 if not a.with_music:cmd+=['--no-music']
 subprocess.run(cmd,cwd=sandbox,check=True)
 output=dest/'ui-mixes'/a.example
 if not a.with_music:output=output/'no-music'
 print(json.dumps({'sandbox':str(sandbox),'ui_output':str(output),'music_used':a.with_music,'accepted_exports_overwritten':False}))
if __name__=='__main__':main()
