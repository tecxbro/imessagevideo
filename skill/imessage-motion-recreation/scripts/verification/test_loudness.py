import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('loudness', Path(__file__).with_name('loudness.py'))
loudness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loudness)


class Loudness(unittest.TestCase):
    def test_tones(self):
        with tempfile.TemporaryDirectory() as tmp:
            measurements = []
            for name, volume in [('source', 1), ('quiet', .1), ('hot', 8), ('silence', 0)]:
                path = Path(tmp) / (name + '.wav')
                subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                                'sine=frequency=1000:duration=3:sample_rate=48000',
                                '-af', f'volume={volume}', '-c:a', 'pcm_f32le', str(path)], check=True)
                measurements.append(loudness.measure(path))
            source, quiet, hot, silence = measurements
            self.assertTrue(loudness.evaluate(source, source)[1])
            self.assertAlmostEqual(loudness.evaluate(source, quiet)[0], -20, delta=.2)
            self.assertFalse(loudness.evaluate(source, quiet)[1])
            self.assertFalse(loudness.evaluate(hot, hot)[1])
            self.assertFalse(loudness.evaluate(source, silence)[1])

    def test_measurement_error(self):
        with self.assertRaises(subprocess.CalledProcessError):
            loudness.measure('/nonexistent/loudness.wav')


if __name__ == '__main__':
    unittest.main()
