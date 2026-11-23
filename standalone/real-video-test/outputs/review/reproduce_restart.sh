#!/bin/sh
set -eu

reviewer_root=$(pwd)/work/reviewer
skill=$(pwd)/work/imessagevideo/skill/imessage-video
source=$(pwd)/work/inputs/unseen-complete.mp4
candidate=$(pwd)/work/run/novel/candidate/candidate.json
scratch="$reviewer_root/restart-reproduced"
py="$reviewer_root/venv/bin/python"
library="$scratch/library"
project="$library/projects/tether"

mkdir "$scratch"
mkdir -p "$project"
"$py" "$skill/scripts/decide.py" "Recreate this." --video "$source" --workdir "$scratch/intake-1" --library "$library" > "$scratch/first.json"
"$py" "$skill/scripts/save_motion.py" "$candidate" "$source" --frames 0:90 --library "$library" --reviewed-by 'Independent reviewer' > "$scratch/saved-motion.json"
"$py" "$skill/scripts/learn.py" --library "$library" replay tether-extend-then-pivot-dock --project "$scratch/editable" --out "$scratch/picture.mp4"
cp "$skill/verification/real-video/tether_sound.py" "$scratch/editable/sound.py"
"$py" "$scratch/editable/sound.py" "$scratch/picture.mp4" "$scratch/stem.wav" "$project/master.mp4"
"$py" -m zipfile -c "$project/editable.zip" "$scratch/editable"
"$py" "$skill/scripts/frames.py" "$source" "$project/master.mp4" --out "$project/comparison" --require-structure-match --max-pts-error-ms 0 --max-mae 6 --check-audio \
    --roi shuttle-and-tether:92,69,302,123 --roi swipe-midpoint:219,161,75,31 \
    --roi fixed-heading:47,50,92,20 --roi fixed-baseline:48,202,383,19
"$py" - "$scratch" "$source" <<'PY'
import hashlib, json, sys
from pathlib import Path

scratch, source = map(Path, sys.argv[1:])
library = scratch / 'library'

def artifact(name):
    path = Path('projects/tether') / name
    return {'path': str(path), 'sha256': hashlib.sha256((library / path).read_bytes()).hexdigest()}

first = json.loads((scratch / 'first.json').read_text())
assert first['next'] == 'learn_before_recreating', first
save = json.loads((scratch / 'saved-motion.json').read_text())
receipt = {'verdict': 'pass', 'reviewed_by': 'Independent reviewer', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
           'recipe_ids': [save['motion']], 'reconstruction': {'editable_project': artifact('editable.zip'),
             'master': artifact('master.mp4'), 'comparison': artifact('comparison/report.json')}}
(scratch / 'film-id.txt').write_text(save['film']['id'])
(scratch / 'review.json').write_text(json.dumps(receipt))
PY
film_id=$(cat "$scratch/film-id.txt")
"$py" "$skill/scripts/sources.py" register "$source" --library "$library" --id "$film_id" --title unseen-complete --verification "$scratch/review.json" > "$scratch/registered-film.json"
"$py" "$skill/scripts/decide.py" "Recreate this." --video "$source" --workdir "$scratch/intake-2" --library "$library" > "$scratch/after-restart.json"
"$py" "$skill/scripts/sources.py" register "$source" --library "$library" --id "$film_id" --title unseen-complete --verification "$scratch/review.json" > "$scratch/registration-retry.json"
"$py" - "$scratch" <<'PY'
import json, sys
from pathlib import Path
scratch = Path(sys.argv[1])
route = json.loads((scratch / 'after-restart.json').read_text())
assert route['next'] == 'return_verified_editable_project_and_master', route
assert len(list((scratch / 'library/entries').iterdir())) == 1
assert len(list((scratch / 'library/films').glob('*.json'))) == 1
assert json.loads((scratch / 'registration-retry.json').read_text())['changed'] is False
print('Independent clean restart reproduced and registry stayed at one source and one learned motion')
PY
