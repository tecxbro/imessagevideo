"""Contract/data regression checks; no source media or browser required."""
import copy
import unittest
import build_scene

def flatten(layers):
    for layer in layers:
        yield layer
        yield from flatten(layer.get('children',[]))

class ProjectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.copy=build_scene.load('copy.json')
        cls.timing=build_scene.load('timing.json')
        cls.timing['output_scale']=1
        cls.scene=build_scene.build(cls.copy,cls.timing)

    def test_contract_and_lifecycles(self):
        s=self.scene
        self.assertEqual((s['width'],s['height'],s['fps'],s['duration']),(1920,1080,30,37))
        nodes=list(flatten(s['layers']))
        ids=[n['id'] for n in nodes]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(all(n['type']!='image' for n in nodes))
        for n in nodes:
            self.assertLessEqual(n.get('start',0),n.get('end',37))
            for track in n.get('keyframes',{}).values():
                self.assertEqual(track,sorted(track,key=lambda k:k['t']))

    def test_complete_shots_and_black_tail(self):
        for f,expected in [(68,'x-ui-camera'),(139,'browser-camera'),(211,'share-phone-camera'),(333,'share-phone-camera')]:
            active=[n['id'] for n in self.scene['layers'] if n.get('start',0)<=f/30<n.get('end',37)]
            self.assertIn(expected,active)
        self.assertEqual(self.scene['background'],'#000000')
        for f in range(1100,1110):
            active=[n for n in self.scene['layers'] if n.get('start',0)<=f/30<n.get('end',37)]
            self.assertEqual([n['id'] for n in active],['shared-background'])
            children=[n for n in active[0]['children'] if n.get('start',0)<=f/30<n.get('end',37)]
            self.assertEqual([n['id'] for n in children],['frame-evaluation-anchor'])
            self.assertEqual((children[0]['width'],children[0]['height']),(0,0))
        anchor=self.scene['layers'][0]['children'][-1]
        self.assertNotEqual(anchor['keyframes']['x'][0]['value'],anchor['keyframes']['x'][-1]['value'])

    def test_camera_and_clipped_screen(self):
        nodes={n['id']:n for n in flatten(self.scene['layers'])}
        self.assertIn('clip',nodes['phone-screen-clipped'])
        self.assertIn('keyframes',nodes['phone-camera'])
        self.assertEqual(nodes['phone-camera']['start'],404/30)
        self.assertEqual(nodes['phone-camera']['end'],991/30)

    def test_insert_states_and_editable_copy(self):
        nodes={n['id']:n for n in flatten(self.scene['layers'])}
        self.assertEqual(nodes['x-bookmark-filled']['start'],107/30)
        config=self.timing['insert_shots']['browser']
        self.assertEqual(nodes['reader-toolbar']['start'],(config['resolve']+config['relative']['toolbar'])/30)
        self.assertEqual(nodes['ios-share-sheet']['start'],235/30)
        self.assertEqual(nodes['reader-saved-content']['start'],278/30)
        self.assertIn('clip',nodes['share-screen-clipped'])
        c=copy.deepcopy(self.copy);c['x_post']['reply']='Changed reply';c['browser']['article']=[]
        changed={n['id']:n for n in flatten(build_scene.build(c,self.timing)['layers'])}
        self.assertEqual(changed['x-reply-placeholder']['text'],'Changed reply')
        self.assertFalse(any(n.startswith('article-line-') for n in changed))

    def test_copy_and_timing_are_live_inputs(self):
        c=copy.deepcopy(self.copy);t=copy.deepcopy(self.timing)
        c['header']['name']='Edited name'
        c['titles']['S1']['text']='Test from anywhere.'
        t['typing']['S1']['births'][0]['frame']=8
        nodes={n['id']:n for n in flatten(build_scene.build(c,t)['layers'])}
        self.assertEqual(nodes['header-name']['text'],'Edited name')
        self.assertEqual(nodes['S1-0-white']['text'],'T')
        self.assertEqual(nodes['S1-prefix-0']['start'],8/30)

    def test_resolution_and_relative_resolve(self):
        t=copy.deepcopy(self.timing);t['output_scale']=2
        scene=build_scene.build(self.copy,t)
        self.assertEqual((scene['width'],scene['height']),(3840,2160))
        self.assertEqual(scene['layers'][0]['scaleX'],2)
        nodes={n['id']:n for n in flatten(scene['layers'])}
        t['insert_shots']['browser']['resolve']+=15
        shifted={n['id']:n for n in flatten(build_scene.build(self.copy,t)['layers'])}
        for id in ['browser-badge','reader-toolbar','reader-toast','reader-toast-check','reader-toast-spinner']:
            self.assertAlmostEqual(shifted[id]['start']-nodes[id]['start'],.5)
        self.assertAlmostEqual(shifted['reader-toast-spinner']['end']-nodes['reader-toast-spinner']['end'],.5)
        self.assertAlmostEqual(shifted['reader-toast-progress']['keyframes']['width'][-1]['t']-nodes['reader-toast-progress']['keyframes']['width'][-1]['t'],.5)
        self.assertEqual(shifted['share-phone-camera'],nodes['share-phone-camera'])

    def test_native_frame_fixes(self):
        nodes={n['id']:n for n in flatten(self.scene['layers'])}
        self.assertEqual(nodes['x-bookmark-hover']['start'],98/30)
        self.assertEqual(nodes['x-bookmark-hover']['end'],107/30)
        self.assertEqual(nodes['share-preview-placeholder']['end'],244/30)
        self.assertEqual(nodes['share-preview-loaded']['start'],244/30)
        self.assertEqual(nodes['ios-share-sheet']['end'],273/30)
        self.assertEqual(nodes['reader-spinner']['start'],273/30)
        self.assertEqual(nodes['send-draft-user1']['end'],571/30)
        self.assertEqual(nodes['send-draft-user2']['end'],833/30)
        self.assertEqual(nodes['key-pop-1']['start'],480/30)
        self.assertEqual(nodes['key-pop-1-label']['text'],'o')
        motion=[n for n in nodes.values() if n['id'].endswith('-motion') and n.get('keyframes')]
        self.assertTrue(motion)
        self.assertGreater(motion[0]['keyframes']['y'][0]['value'],10)

    def test_empty_and_error_cases(self):
        c=copy.deepcopy(self.copy)
        c['titles']['S1']['text']='';c['titles']['S1']['accent']=None
        scene=build_scene.build(c,self.timing)
        self.assertEqual(next(n for n in flatten(scene['layers']) if n['id']=='S1-0-white')['text'],'')
        with self.assertRaises(KeyError):
            build_scene.build({},self.timing)
        t=copy.deepcopy(self.timing);t['output_scale']=3
        with self.assertRaises(ValueError):build_scene.build(c,t)

if __name__=='__main__':
    unittest.main()
