import unittest
import numpy as np
from build_scores import motion_texture


class TextureTests(unittest.TestCase):
    def test_deterministic_finite_span_and_fades(self):
        wave=motion_texture(336000)
        self.assertEqual(wave.shape,(336000,2))
        self.assertTrue(np.isfinite(wave).all())
        np.testing.assert_array_equal(wave,motion_texture(336000))
        np.testing.assert_array_equal(wave[[0,-1]],0)
        self.assertLess(np.max(np.abs(wave)),.1)

    def test_empty(self):
        with self.assertRaisesRegex(ValueError,'positive'):
            motion_texture(0)

    def test_negative(self):
        with self.assertRaisesRegex(ValueError,'positive'):
            motion_texture(-1)


if __name__=='__main__':
    unittest.main()
