#!/usr/bin/env python3
"""Promote a measured movement, verify its replay, then index the original film."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from learn import library_path, register as promote_motion
from sources import identify, register as register_film


def save(candidate, source, library, selection, crop, reviewed_by, title=None):
    if not reviewed_by.strip():
        raise ValueError('Record who inspected the source and independently rendered motion.')
    identity = identify(source, library)
    if identity['status'] == 'known':
        film = identity['matches'][0]
        film_id, film_title = film['id'], film['title']
    else:
        # A visually similar edit/retime gets its own exact-source record.
        film_id, film_title = 'source-'+identity['sha256'][:24], title or source.stem
    entry = promote_motion(library, candidate, source, selection, crop)
    receipt = {'verdict':'pass','reviewed_by':reviewed_by,'source_sha256':identity['sha256'],'recipe_ids':[entry.name]}
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'review.json'
        path.write_text(json.dumps(receipt))
        result=register_film(source, library, film_id=film_id, title=film_title, verification_path=path)
    return {'film':result,'motion':entry.name,'preview':str(entry/'preview.mp4'),
            'editable_scene':str(entry/'scene.json'),'frame_comparison':str(entry/'evidence/comparison/report.json')}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('candidate',type=Path)
    ap.add_argument('source',type=Path)
    ap.add_argument('--frames',help='Source frame window FIRST:EXCLUSIVE_END.')
    ap.add_argument('--crop',help='Optional native pixel X,Y,W,H, with --frames.')
    ap.add_argument('--library',type=Path)
    ap.add_argument('--reviewed-by',required=True)
    ap.add_argument('--title')
    args=ap.parse_args()
    try:
        result=save(args.candidate.resolve(),args.source.resolve(),library_path(args.library),args.frames,args.crop,args.reviewed_by,args.title)
        print(json.dumps(result,indent=2))
    except (KeyError,ValueError,OSError,subprocess.CalledProcessError) as exc:
        ap.exit(2,f'{exc}\n')

if __name__=='__main__':
    main()
