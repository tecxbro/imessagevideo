"""Annotate trial receipts without changing historical hash values."""
import json
from pathlib import Path
from check_cues import PACKET_HASH_METHOD

base = Path(__file__).resolve().parents[1]
for path in base.rglob('*.json'):
    if 'audio-recreation' in path.parts or 'blind' in path.parts:
        continue
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        continue
    methods = {}
    for key in data:
        if key in {'picture_packet_sha256', 'video_packet_sha256', 'actual_picture', 'expected_picture'}:
            methods[key] = PACKET_HASH_METHOD
        elif key in {'picture_sha256', 'picture_file_sha256', 'video_sha256', 'output_sha256'}:
            methods[key] = 'SHA-256 of entire named MP4 file bytes, including container and all streams; not stream packets or decoded frames'
        elif key == 'aac_packet_sha256':
            methods[key] = 'SHA-256 of concatenated encoded first-audio-stream packet payloads; ffmpeg -map 0:a:0 -c copy -f hash -hash sha256'
    if methods:
        data['hash_methods'] = methods
        path.write_text(json.dumps(data, indent=2)+'\n')
        print(path.relative_to(base))
