#!/usr/bin/env python3
"""Optional original-path aliases for legacy cue-derivation/authoring programs."""
from pathlib import Path
import argparse,json,os,shutil
ROOT=Path(__file__).resolve().parents[1]
VERSIONS={'01-photonhq':'final-v10','02-danieltian':'final-v19','03-photon-mini':'final-v18','04-poke':'final-v19','05-linq':'final-v20','06-gallery':'final-v23'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--example',choices=list(VERSIONS));p.add_argument('--copy',action='store_true');a=p.parse_args();records=[]
 for ident,version in VERSIONS.items():
  if a.example and ident!=a.example:continue
  source=ROOT/'scenes'/ident;dest=ROOT/'outputs'/ident/version
  if not source.is_dir():continue
  if dest.exists():
   if dest.resolve()!=source.resolve():raise FileExistsError('Do not overwrite an existing source snapshot: '+str(dest))
  else:
   dest.parent.mkdir(parents=True,exist_ok=True)
   if a.copy:shutil.copytree(source,dest)
   else:dest.symlink_to(os.path.relpath(source,dest.parent),target_is_directory=True)
  records.append({'original':str(dest),'portable':str(source),'mode':'copy' if a.copy else 'relative symlink'})
 print(json.dumps(records,indent=2))
if __name__=='__main__':main()
