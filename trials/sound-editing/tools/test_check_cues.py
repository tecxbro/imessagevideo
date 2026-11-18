import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile
import json
import hashlib
import numpy as np
from check_cues import add, locate, outside_tolerance, review
from score_cues import score


class CueTests(unittest.TestCase):
    def test_shift_and_gain(self):
        wave = np.random.default_rng(12).normal(size=(100, 2))
        audio = np.zeros((1000, 2)); add(audio, wave, 420, .25)
        start, corr, gain = locate(audio, wave, 400, 50)
        self.assertEqual(start, 420); self.assertAlmostEqual(corr, 1); self.assertAlmostEqual(gain, .25)

    def test_silence(self):
        _, corr, gain = locate(np.zeros((1000, 2)), np.ones((100, 2)), 400, 50)
        self.assertEqual(corr, 0); self.assertEqual(gain, 0)

    def test_boundary(self):
        audio = np.zeros((10, 2)); add(audio, np.ones((5, 2)), -2)
        self.assertEqual(audio.sum(), 6)

    def test_picture_mismatch_never_decodes_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'receipt.json'
            path.write_text(json.dumps({'picture_packet_sha256': 'expected'}))
            with patch('check_cues.packet_hash', return_value='wrong'), patch('check_cues.decode') as decode:
                self.assertFalse(review(Path('movie.mp4'), path)['picture_match'])
                decode.assert_not_called()

    def test_empty_score(self):
        self.assertEqual(score({'cues': [], 'extras': []}, {'defects': []})['true_positives'], 0)

    def test_fractional_frame_boundary(self):
        fps = 30000/1001
        self.assertFalse(outside_tolerance(1602, 1, fps))
        self.assertTrue(outside_tolerance(1603, 1, fps))
        self.assertTrue(outside_tolerance(-1602, .5, fps))

    def test_pinned_background_subtraction(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); (base/'receipts').mkdir()
            wave = np.random.default_rng(8).normal(size=(4800, 2)) * .01
            np.save(base/'bed.npy', wave)
            receipt = {'picture_packet_sha256': 'expected', 'fps': 30, 'cues': [],
                       'background_reference': {'reference': 'bed.npy',
                           'reference_sha256': hashlib.sha256((base/'bed.npy').read_bytes()).hexdigest()}}
            path = base/'receipts/review.json'; path.write_text(json.dumps(receipt))
            with patch('check_cues.packet_hash', return_value='expected'), patch('check_cues.decode', return_value=wave.copy()), patch('check_cues.background_codec_floor', return_value=np.zeros(20)), patch('check_cues.subprocess.check_output', return_value='{"packets":[{}]}'):
                result = review(Path('movie.mp4'), path)
            self.assertEqual(result['status'], 'pass')
            self.assertEqual(result['background_reference_review']['gain_delta_db'], 0)
            extra = wave.copy(); extra[2400:2640] += .03
            with patch('check_cues.packet_hash', return_value='expected'), patch('check_cues.decode', return_value=extra), patch('check_cues.background_codec_floor', return_value=np.zeros(20)), patch('check_cues.subprocess.check_output', return_value='{"packets":[{}]}'):
                result = review(Path('movie.mp4'), path)
            self.assertEqual(result['status'], 'fail')
            self.assertEqual(len(result['extras']), 1)
            receipt['background_reference']['reference_sha256'] = 'wrong'
            path.write_text(json.dumps(receipt))
            with patch('check_cues.packet_hash', return_value='expected'), patch('check_cues.decode', return_value=wave.copy()):
                with self.assertRaisesRegex(ValueError, 'Background reference hash mismatch'):
                    review(Path('movie.mp4'), path)


if __name__ == '__main__':
    unittest.main()
