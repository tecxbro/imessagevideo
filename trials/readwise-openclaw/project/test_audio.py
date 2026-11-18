import copy
import json
from pathlib import Path
import unittest
import numpy as np
from audio import render_audio as audio

class AudioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cues=json.loads((Path(__file__).parent/'audio/cues.json').read_text())

    def test_observed_human_keys_only(self):
        timing=json.loads((Path(__file__).parent/'timing.json').read_text())
        expected=sorted(b['frame'] for k in ['user1','user2'] for b in timing['typing'][k]['births'])
        actual=[e['frame'] for e in self.cues['events'] if e['kind']=='typing']
        self.assertEqual(actual,expected)
        self.assertEqual(len(actual),len(set(actual)))

    def test_full_mix(self):
        mix,ui,bed,report=audio.build(self.cues)
        self.assertEqual(mix.shape,(1776000,2))
        self.assertTrue(np.isfinite(mix).all())
        self.assertLess(abs(mix).max(),10**(-9/20)+1e-9)
        self.assertEqual(abs(mix[1760000:]).max(),0)
        self.assertEqual(len(report['receipts']),len(self.cues['events']))
        self.assertGreater(abs(ui).max(),0);self.assertGreater(abs(bed).max(),0)

    def test_empty_and_error(self):
        cues=copy.deepcopy(self.cues);cues.update(frames=1,music_end_frame=0,events=[])
        mix,_,_,_=audio.build(cues)
        self.assertEqual(abs(mix).max(),0)
        cues['events']=[{'frame':5,'kind':'tap'}]
        with self.assertRaises(ValueError):audio.build(cues)
        self.assertTrue(np.array_equal(audio.music_bed(10000,self.cues['music']),audio.music_bed(10000,self.cues['music'])))

if __name__=='__main__':unittest.main()
