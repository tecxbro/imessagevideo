import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

import numpy as np

spec=importlib.util.spec_from_file_location('onsets',Path(__file__).with_name('event_onsets.py'))
onsets=importlib.util.module_from_spec(spec)
spec.loader.exec_module(onsets)


class EventOnsets(unittest.TestCase):
    def clip(self, path, onset, width=160, height=96):
        frames=np.full((40,height,width,3),240,np.uint8)
        if onset is not None:
            frames[onset:,height//3:height//3+32,width//3:width//3+32]=[10,150,240]
        subprocess.run(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r','30','-i','-','-c:v','libx264rgb','-crf','0',str(path)],input=frames.tobytes(),check=True)
        return onsets.decode(path)

    def test_late_normal_empty_and_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            source,sm=self.clip(Path(tmp)/'source.mp4',12)
            candidate,cm=self.clip(Path(tmp)/'candidate.mp4',18)
            events=onsets.scan_frames(source,sm)
            onset=[e for e in events if e['kind']=='local-onset' and e['frame']==12]
            self.assertTrue(onset)
            rows=onsets.compare_frames(source,candidate,sm,cm,onset)
            self.assertEqual(rows[0]['delta_frames'],6)
            self.assertEqual(rows[0]['status'],'late')
            self.assertEqual(onsets.compare_frames(source,source,sm,sm,onset)[0]['status'],'pass')
            empty,em=self.clip(Path(tmp)/'empty.mp4',None)
            self.assertEqual(onsets.scan_frames(empty,em),[])
            self.assertEqual(onsets.compare_frames(source,empty,sm,em,onset)[0]['status'],'missing')
            self.assertEqual(onsets.compare_frames(source,candidate,sm,cm,onset,frame_map=[[0,6],[39,45]])[0]['status'],'pass')
            resized=np.repeat(np.repeat(source,2,axis=1),2,axis=2)
            self.assertEqual(onsets.compare_frames(source,resized,sm,sm,onset)[0]['status'],'pass')

    def test_cut_and_settle(self):
        frames=np.zeros((40,96,160,3),np.uint8)
        frames[12:]=240
        events=onsets.scan_frames(frames,{'fps':30})
        self.assertTrue(any(e['kind']=='cut' and e['frame']==12 for e in events))
        frames=np.zeros((40,96,160,3),np.uint8)
        for f in range(10,20):
            frames[f,32:64,32:64]=(f-9)*20
        frames[20:,32:64,32:64]=200
        self.assertTrue(any(e['kind']=='settle' and e['frame']==20 for e in onsets.scan_frames(frames,{'fps':30})))

    def test_decode_error(self):
        with self.assertRaises(subprocess.CalledProcessError):
            onsets.decode('/nonexistent/event-onsets.mp4')


if __name__=='__main__':
    unittest.main()
