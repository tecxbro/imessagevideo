from pathlib import Path
import concurrent.futures
import json
import os
import subprocess
import sys

root, target = map(Path, sys.argv[1:])
catalog = json.loads((root / 'motion/catalog.json').read_text())
fresh = target / 'fresh'
fresh.mkdir(exist_ok=True)
def run(row_variant):
    row, ui = row_variant
    stem = f"ui.{row['id']}" if ui else row['id']
    extra = ['--ui'] if ui else []
    video = fresh / f'{stem}.mp4'
    commands = ['node','motion/cli.mjs','render','--id',row['id'],'--method','pillow','--out',str(video),*extra]
    p = subprocess.run(commands, cwd=root, env={**os.environ,'MOTION_PYTHON':'/tmp/imv-catalog-venv/bin/python','PYTHONDONTWRITEBYTECODE':'1','FONTCONFIG_FILE':'/tmp/imv-ui-matrix.rS4TSx/fonts.conf'},
                       capture_output=True, text=True)
    status = {'id':row['id'],'ui':ui,'code':p.returncode, 'stderr':p.stderr[-1800:] if p.returncode else ''}
    print(json.dumps(status), flush=True)
    return status
variants = [(row, ui) for row in catalog['entries'] for ui in ([False,True] if row.get('ui') else [False])]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    result = list(executor.map(run, variants))
(target / 'fresh.json').write_text(json.dumps(result,indent=2)+'\n')
