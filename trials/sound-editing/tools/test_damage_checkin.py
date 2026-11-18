import tempfile
import unittest
from pathlib import Path
import numpy as np
from damage_checkin import intervene
from render_mix import sha256


class CheckInDamageTests(unittest.TestCase):
    def test_seeded_six_and_required_delays(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);ref=base/'cue.npy';np.save(ref,np.ones((32,2))*.01)
            frames=[132,186,445,451,469,590]
            cues=[{'ordinal':i,'canonical_event':{'frame':f,'kind':'tap' if f==132 else 'typing'},
                   'reference':'cue.npy','reference_sha256':sha256(ref),'clip_start_sample_unclipped':10000+i*5000,
                   'event_sample':f*1600} for i,f in enumerate(frames)]
            audio=np.zeros((600000,2));receipt={'cues':cues,'fps':30}
            actual,key=intervene(audio,receipt,base,420186)
            repeat,repeat_key=intervene(audio,receipt,base,420186)
            np.testing.assert_array_equal(actual,repeat);self.assertEqual(key,repeat_key)
            self.assertEqual(len(key),6)
            self.assertEqual([(d['frame'],d['offset_samples']) for d in key[:2]],[(445,1600),(186,4800)])
            self.assertTrue(np.any(actual[492000:492032]))
            self.assertFalse(audio.any())

    def test_empty_receipt(self):
        with self.assertRaisesRegex(ValueError,'absent'):
            intervene(np.zeros((10,2)),{'cues':[],'fps':30},Path('.'),1)

    def test_bad_reference_hash(self):
        cues=[{'ordinal':i,'canonical_event':{'frame':f,'kind':'typing'},'reference':'x','reference_sha256':'wrong'}
              for i,f in enumerate([186,445,451,469,590])]
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory)/'x').write_bytes(b'not a waveform')
            with self.assertRaisesRegex(ValueError,'hash'):
                intervene(np.zeros((10,2)),{'cues':cues,'fps':30},Path(directory),1)


if __name__=='__main__':unittest.main()
