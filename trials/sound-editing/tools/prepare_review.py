"""Freeze the actual varied cue waveforms and packet identity before review."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'audio-recreation/scripts'))
import render_ui as renderer
from check_cues import PACKET_HASH_METHOD, packet_hash

schedule, path = renderer.load_schedule('04-poke')
report = json.loads((BASE / 'audio-recreation/ui-mixes/04-poke/no-music/report.json').read_text())
cues = []
for ordinal, event in enumerate(schedule['events']):
    if event['kind'] == 'control_appear':
        continue
    waveform, receipt = renderer.render_event(event, schedule, ordinal)
    waveform *= 10 ** (report['common_peak_guard_gain_db'] / 20)
    dest = BASE / 'references' / f'cue-{ordinal:02}.npy'
    np.save(dest, waveform)
    cues.append({**receipt, 'reference': str(dest.relative_to(BASE)),
                 'reference_sha256': hashlib.sha256(dest.read_bytes()).hexdigest()})
picture = BASE.parents[1] / 'projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/gsap.mp4'
result = {'picture_packet_sha256': packet_hash(picture), 'schedule_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
          'picture_packet_hash_method': PACKET_HASH_METHOD,
          'picture_file_sha256': hashlib.sha256(picture.read_bytes()).hexdigest(),
          'picture_file_hash_method': 'SHA-256 of all bytes of original accepted gsap.mp4 including container and all streams; not decoded frames',
          'fps': schedule['fps_numerator'] / schedule['fps_denominator'], 'samples': schedule['sample_count'],
          'sample_rate': 48000, 'cues': cues}
(BASE / 'references/receipt.json').write_text(json.dumps(result, indent=2) + '\n')
print(f'Frozen {len(cues)} reference waveforms; picture {result["picture_packet_sha256"]}')
