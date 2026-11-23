"""Signal-level acceptance tests for the exported original sound designs."""
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from ui_synth import EFFECTS, PEAK_CEILING, SAMPLE_RATE, analyze, render, write_wav


class SynthesisAcceptance(unittest.TestCase):
    def test_every_design_is_safe_and_repeatable(self):
        for effect, spec in EFFECTS.items():
            with self.subTest(effect=effect):
                first = render(effect, seed=7)
                np.testing.assert_array_equal(first, render(effect, seed=7))
                self.assertFalse(np.array_equal(first, render(effect, seed=8)))
                stats = analyze(first)
                self.assertEqual(first.shape, (round(spec['duration'] * SAMPLE_RATE), 2))
                self.assertEqual(first.dtype, np.float32)
                self.assertTrue(stats['finite'] and stats['endpoints_zero'])
                self.assertFalse(stats['clipped'])
                self.assertAlmostEqual(stats['peak'], PEAK_CEILING * .75, places=6)
                self.assertLess(max(abs(v) for v in stats['dc']), 1e-7)
                # Tails must return gently to digital silence, beyond a single
                # forced last zero. This catches accidentally truncated decays.
                self.assertLess(float(np.max(np.abs(first[-24:]))), .002)

    def test_parameter_extremes_and_pan(self):
        for effect in EFFECTS:
            for pitch, duration, energy, pan in [(.25, .01, 1., -1.), (4., .04, .2, 1.)]:
                with self.subTest(effect=effect, pitch=pitch):
                    x = render(effect, pitch=pitch, duration=duration, energy=energy, pan=pan, seed=9)
                    self.assertEqual(len(x), round(duration * SAMPLE_RATE))
                    self.assertTrue(np.isfinite(x).all())
                    self.assertLess(float(np.max(np.abs(x))), .709)
                    self.assertTrue(np.all(x[:, 1 if pan < 0 else 0] == 0))
        self.assertTrue(np.all(render('bubble_pop', energy=0) == 0))

    def test_pitch_is_a_frequency_ratio(self):
        peaks = []
        for pitch in [1., 2.]:
            x = render('glass_confirm', pitch=pitch, seed=11)[:, 0]
            spectrum = abs(np.fft.rfft(x * np.hanning(len(x))))
            frequency = np.fft.rfftfreq(len(x), 1 / SAMPLE_RATE)
            peaks.append(frequency[np.argmax(spectrum)])
        self.assertAlmostEqual(peaks[1] / peaks[0], 2., delta=.01)

    def test_short_impulse_attacks_are_prompt(self):
        for effect in ['touch_click', 'key_tap', 'bubble_pop']:
            x = render(effect, seed=20261109)
            self.assertLess(np.argmax(np.max(np.abs(x), axis=1)) / SAMPLE_RATE, .008)

    def test_pcm24_round_trip(self):
        samples = render('digital_sparkle', duration=.1, seed=12)
        with tempfile.TemporaryDirectory() as folder:
            file = write_wav(Path(folder) / 'check.wav', samples)
            with wave.open(str(file), 'rb') as handle:
                self.assertEqual((handle.getnchannels(), handle.getsampwidth(), handle.getframerate()), (2, 3, SAMPLE_RATE))
                self.assertEqual(handle.getnframes(), len(samples))
                raw = np.frombuffer(handle.readframes(len(samples)), dtype=np.uint8).reshape(-1, 3)
            values = raw[:, 0].astype(np.int32) | (raw[:, 1].astype(np.int32) << 8) | (raw[:, 2].astype(np.int32) << 16)
            values = np.where(values >= 2 ** 23, values - 2 ** 24, values).reshape(-1, 2)
            np.testing.assert_allclose(values / (2 ** 23 - 1), samples, atol=1 / (2 ** 23 - 1))
            self.assertTrue(np.all(values[[0, -1]] == 0))

    def test_invalid_input_is_rejected(self):
        for parameters in [{'pitch': float('nan')}, {'duration': 0}, {'energy': 2}, {'pan': -2}]:
            with self.assertRaises(ValueError):
                render('bubble_pop', **parameters)
        with self.assertRaises(ValueError):
            render('unknown')
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                write_wav(Path(folder) / 'clipped.wav', np.ones((10, 2)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
