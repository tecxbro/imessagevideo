"""Inventory omitted trial binary payloads without staging library copies."""
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]


def main():
    suffixes={'.mp4','.flac','.m4a','.npy','.mp3','.wav','.ogg','.zip'}
    files=[]
    for p in sorted(BASE.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(BASE).as_posix()
        binary=p.suffix in suffixes or (p.suffix=='.png' and p.name.startswith('frame-'))
        if not binary or rel=='checkin/v1-first-export.mp4':continue
        if rel.startswith('checkin-v3/delivery/'):
            command='checkin-v3/README.md then checkin-v3/delivery/README.md: python trials/sound-editing/checkin-v3/tools/build_delivery.py'
        elif rel.startswith('checkin-v3/'):
            command='checkin-v3/README.md: restore pinned director input, python trials/sound-editing/checkin-v3/tools/inspect_frames.py and tools/build_score.py'
        elif rel.startswith(('audio-recreation/library/','audio-recreation/synthesis/')):
            command='README.md: bootstrap existing sound kit from synchronized library'
        elif p.suffix=='.npy':command='python trials/sound-editing/tools/restore_outputs.py --references-only'
        elif p.suffix=='.png':command='python trials/sound-editing/checkin/tools/inspect_frames.py'
        else:command='README.md: named outputs, Poke damage/repair, or Check In damage commands'
        files.append({'path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                      'reproduction':command,'note':'Historical failed/first attempts may be evidence-only; see results and logs' if 'first' in rel else None})
    value={'policy':'Ordinary Git, no LFS. Generated review/audio/NPY payloads collectively exceed50MB, so omitted; no new library archive registration.',
           'included_binary_source':'checkin/v1-first-export.mp4; original director input, not reproducible from audio tools',
           'included_evidence':'Contact and transition sheets PNG; individual decoded frames omitted',
           'omitted_count':len(files),'omitted_bytes':sum(f['bytes'] for f in files),'files':files}
    (BASE/'BINARY-MANIFEST.json').write_text(json.dumps(value,indent=2)+'\n')
    print(f'Inventoried {len(files)} omitted binaries, {value["omitted_bytes"]} bytes')


if __name__=='__main__':main()
