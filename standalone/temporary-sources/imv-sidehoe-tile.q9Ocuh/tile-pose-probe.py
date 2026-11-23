from pathlib import Path
import json
import sys

project = Path('/tmp/imv-goal.9G9Un0/sidehoe-clean-project')
sys.path.insert(0, str(project))
from render import Film

correction_native_px = {614: -12, 615: -10, 616: -7, 617: -20, 618: -22}

class RegisteredFilm(Film):
    def track(self, key, frame):
        value = super().track(key, frame)
        if key == 'blueOrbit' and frame in correction_native_px:
            x, y, size = value
            return x, y + correction_native_px[frame] / 2, size
        return value

film = RegisteredFilm(json.loads((project / 'scene.json').read_text()))
output = Path(sys.argv[1])
output.mkdir(exist_ok=False)
for frame in range(612, 624):
    film.frame(frame).save(output / f'{frame:06d}.png', compress_level=1)
