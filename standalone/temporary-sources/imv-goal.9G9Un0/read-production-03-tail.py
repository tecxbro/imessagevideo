from pathlib import Path
import csv,hashlib,json,sys
root=Path('/Users/darshan/Documents/ChatGPT/imessage-video')
reference=root/'codex-direction-library/projects/03-photon-mini-complete-v1/imessage-recreations/references/03-photon-mini'
manifest=root/'codex-trial/review/imv-v3/goal-audit/production-03-sources.csv'
snapshot=Path(__file__).with_suffix('.json')
rows=list(csv.DictReader(manifest.open()))
if not snapshot.exists():
    snapshot.write_text(json.dumps([r['path'] for r in rows if not r['coverage'].startswith('full direct')]))
todo=json.loads(snapshot.read_text())
mode,first,last=sys.argv[1:]
choices=set(todo[int(first)-1:int(last)])
if mode=='read':
    for i,name in enumerate(todo,1):
        if name not in choices:
            continue
        file=reference/name
        raw=file.read_bytes()
        row=next(r for r in rows if r['path']==name)
        assert hashlib.sha256(raw).hexdigest()==row['sha256']
        lines=raw.decode().splitlines()
        print(f'\n=== {i} {name} | 1–{len(lines)} ===')
        for line_number,line in enumerate(lines,1):
            print(f'{line_number:3d} {line}')
elif mode=='mark':
    for row in rows:
        if row['path'] in choices:
            row['coverage']='full direct source reading and syntax'
    with manifest.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(sum(r['coverage']=='full direct source reading and syntax' for r in rows),'additional full-read files verified')
