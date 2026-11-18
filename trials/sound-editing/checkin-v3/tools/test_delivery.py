import unittest
import numpy as np
from build_delivery import master


class DeliveryTests(unittest.TestCase):
    def test_silence_and_span(self):
        wave=np.zeros((4800,2))
        np.testing.assert_array_equal(master(wave,20),wave)

    def test_invalid_input(self):
        for wave in [np.zeros((0,2)),np.zeros((10,1)),np.full((10,2),np.nan)]:
            with self.assertRaises(ValueError):master(wave,0)

    def test_gain_limit_and_latency(self):
        wave=np.zeros((48000,2));wave[24000]=.1
        quiet=master(wave,6)
        self.assertEqual(int(np.argmax(np.abs(quiet[:,0]))),24000)
        baseline=master(wave,0)
        np.testing.assert_allclose(quiet,baseline*10**(6/20),atol=1e-8)
        hot=master(wave,40)
        self.assertEqual(hot.shape,wave.shape)
        self.assertLess(np.max(np.abs(hot)),.9)
        self.assertEqual(int(np.argmax(np.abs(hot[:,0]))),24000)


if __name__=='__main__':unittest.main()
