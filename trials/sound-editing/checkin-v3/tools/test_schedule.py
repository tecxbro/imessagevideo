import unittest
from build_score import canonical


class ScheduleTests(unittest.TestCase):
    def test_native_sample_and_one_shared_arrival(self):
        s=canonical({'fps':30,'frames':720,'events':{'460':[{'frame':460,'action':'arrival','targets':['a','b']}]}},'picture')
        self.assertEqual(len(s['events']),1)
        self.assertEqual(s['events'][0]['sample_offset_48000'],736000)

    def test_empty(self):
        self.assertEqual(canonical({'fps':30,'frames':720,'events':{}},'picture')['events'],[])

    def test_invisible_space_is_not_key(self):
        with self.assertRaisesRegex(ValueError,'Invisible'):
            canonical({'fps':30,'frames':720,'events':{'350':[{'frame':350,'action':'type char','char':' '}]}},'picture')

    def test_wrong_cadence(self):
        with self.assertRaisesRegex(ValueError,'30fps'):
            canonical({'fps':29.97,'frames':720,'events':{}},'picture')


if __name__=='__main__':unittest.main()
