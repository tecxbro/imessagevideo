import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import numpy as np

spec=importlib.util.spec_from_file_location('onsets',Path(__file__).with_name('event_onsets.py'))
onsets=importlib.util.module_from_spec(spec)
spec.loader.exec_module(onsets)


class EventOnsets(unittest.TestCase):
    def test_tiny_roi_different_resolutions(self):
        source=np.zeros((40,32,32,3),np.uint8)
        candidate=np.zeros((40,64,64,3),np.uint8)
        source[12:]=[20,120,240]
        candidate[18:]=[20,120,240]
        meta={'fps':30}
        for box in [[.25,.25,.28125,.28125],[.25,.25,.375,.375],[.25,.25,.28125,.5]]:
            with self.subTest(box=box):
                event={'frame':12,'time':.4,'bbox':box,'kind':'local-onset','magnitude':10}
                for a,b in [(source,candidate),(candidate,source)]:
                    current={**event,'frame':12 if a is source else 18}
                    rows=onsets.compare_frames(a,b,meta,meta,[current])
                    self.assertEqual(rows[0]['candidate_frame'],18 if a is source else 12)
                    self.assertEqual(rows[0]['status'],'late' if a is source else 'early')
                    self.assertEqual(onsets.compare_frames(a,a,meta,meta,[current])[0]['status'],'pass')
                self.assertEqual(onsets.compare_frames(source,np.zeros_like(candidate),meta,meta,[event])[0]['status'],'missing')

    def test_coalesce(self):
        def event(box, frame=12):
            return {'frame':frame,'time':frame/30,'bbox':box,'kind':'local-onset','magnitude':10}
        a=event([0,0,.4,.4])
        b=event([.3,.3,.6,.6])
        c=event([.6,.4,.8,.6])
        self.assertEqual(onsets.coalesce([]),[])
        merged=onsets.coalesce([a,c,b,a,event([0,0,.4,.4],13)])
        self.assertEqual(len(merged),2)
        self.assertEqual(merged[0]['bbox'],[0,0,.8,.6])
        self.assertEqual(a['bbox'],[0,0,.4,.4])

    def test_spatial_signed_match_and_nearest_tie(self):
        source=np.zeros((30,32,32,3),np.uint8)
        source[12:,8:16,24:32]=[20,120,240]
        candidate=np.zeros_like(source)
        candidate[8,8:16,0:8]=[20,120,240]
        candidate[14:,8:16,24:32]=[20,120,240]
        meta={'fps':30}
        event={'frame':12,'time':.4,'bbox':[0,0,1,1],'kind':'local-onset','magnitude':10}
        rows=onsets.compare_frames(source,candidate,meta,meta,[event,event])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['candidate_frame'],14)
        candidate[8]=source[12]
        candidate[12]=source[12]
        self.assertEqual(onsets.compare_frames(source,candidate,meta,meta,[event])[0]['candidate_frame'],12)

    def test_sheets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            source,sm=self.clip(root/'source.mp4',12)
            candidate,cm=self.clip(root/'candidate.mp4',18)
            events=[e for e in onsets.scan_frames(source,sm) if e['frame']==12]
            rows=onsets.compare_frames(source,candidate,sm,cm,events)
            onsets.write_sheets(root/'sheets',root/'source.mp4',root/'candidate.mp4',rows)
            self.assertEqual(len(list((root/'sheets').glob('*.jpg'))),2)
            self.assertTrue((root/'sheets/source/frame-000012.png').is_file())
            self.assertTrue((root/'sheets/candidate/frame-000018.png').is_file())
            onsets.write_sheets(root/'empty',root/'source.mp4',root/'candidate.mp4',[])
            self.assertEqual(list((root/'empty').glob('*.jpg')),[])
            with self.assertRaises(subprocess.CalledProcessError):
                onsets.write_sheets(root/'bad',root/'missing.mp4',root/'candidate.mp4',rows)

    def test_joint_region_support(self):
        source=np.zeros((30,32,32,3),np.uint8)
        source[12:,0:8,0:8]=100
        source[12:,24:32,24:32]=100
        candidate=np.zeros_like(source)
        candidate[8:,0:8,0:8]=100
        candidate[14:,0:8,0:8]=120
        candidate[14:,24:32,24:32]=100
        def event(frame,box):
            return {'frame':frame,'time':frame/30,'bbox':box,'kind':'local-onset','magnitude':10}
        left,right=[0,0,.25,.25],[.75,.75,1,1]
        source_events=[event(12,left),event(12,right)]
        candidate_events=[event(8,left),event(14,left),event(14,right)]
        rows=onsets.compare_frames(source,candidate,{'fps':30},{'fps':30},source_events,candidate_events=candidate_events)
        self.assertEqual([r['candidate_frame'] for r in rows],[14,14])
        candidate[:]=100
        candidate[14:,0:8,0:8]=0
        rows=onsets.compare_frames(source,candidate,{'fps':30},{'fps':30},source_events[:1],candidate_events=[event(14,left)])
        self.assertEqual(rows[0]['status'],'missing')

    def test_cadence_option_fallback_and_cache(self):
        for help_text,expected in [('-vsync sync_method', '-vsync'), ('-fps_mode fps_mode', '-fps_mode'), ('-fps_mode[:<stream_spec>]  set framerate mode', '-fps_mode')]:
            onsets.cadence_option.cache_clear()
            try:
                with mock.patch.object(onsets.subprocess,'check_output',return_value=help_text) as probe:
                    self.assertEqual(onsets.cadence_option(),expected)
                    self.assertEqual(onsets.cadence_option(),expected)
                    probe.assert_called_once()
            finally:
                onsets.cadence_option.cache_clear()

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

    def test_first_video_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.clip(root/'first.mp4',12,80,48)
            self.clip(root/'second.mp4',18,160,96)
            subprocess.run(['ffmpeg','-v','error','-i',str(root/'first.mp4'),'-i',str(root/'second.mp4'),'-map','0:v:0','-map','1:v:0','-c','copy',str(root/'two.mp4')],check=True)
            frames,meta=onsets.decode(root/'two.mp4')
            self.assertEqual((meta['width'],meta['height'],meta['frames']),(80,48,40))
            self.assertEqual(frames.shape,(40,48,80,3))

    def test_vfr_native_packet_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'vfr.mp4'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc=size=80x48:rate=30:duration=2','-vf',r'select=if(lt(n\,30)\,1\,not(mod(n\,3)))','-fps_mode','vfr','-c:v','libx264','-pix_fmt','yuv420p',str(path)],check=True)
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_packets','-show_entries','stream=nb_read_packets','-show_packets','-show_entries','packet=pts_time','-of','json',str(path)]))
            times=sorted(float(p['pts_time']) for p in probe['packets'])
            self.assertGreater(len(set(np.round(np.diff(times),3))),1)
            frames,meta=onsets.decode(path)
            self.assertEqual(len(frames),int(probe['streams'][0]['nb_read_packets']))
            self.assertEqual(meta['frames'],40)


if __name__=='__main__':
    unittest.main()
