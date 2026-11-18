import unittest
import numpy as np
from repair_cues import patch_regions


class RepairTests(unittest.TestCase):
    def test_merge_preserve_neighbors_and_outside(self):
        audio=np.zeros((100,2));expected=np.ones_like(audio)
        actual,regions=patch_regions(audio,expected,[(10,30),(20,40)],fade=0)
        self.assertEqual(regions,[[10,40]])
        np.testing.assert_array_equal(actual[10:40],1)
        np.testing.assert_array_equal(actual[:10],0)
        np.testing.assert_array_equal(actual[40:],0)

    def test_empty_findings_do_not_rebuild_track(self):
        audio=np.ones((20,2));actual,regions=patch_regions(audio,np.zeros_like(audio),[])
        np.testing.assert_array_equal(actual,audio)
        self.assertEqual(regions,[])

    def test_span_mismatch(self):
        with self.assertRaisesRegex(ValueError,'spans'):
            patch_regions(np.zeros((20,2)),np.zeros((10,2)),[])


if __name__=='__main__':
    unittest.main()
