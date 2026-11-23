"""Regression checks for the distinctions that change what the user receives."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import decide
import learn
import recipes
import renderer


class DecisionExamples(unittest.TestCase):
    def test_same_reference_different_requests(self):
        cases = [
            ('Recreate this entire video and save its motions.', 'recreate', 'film'),
            ('Recreate just the swipe from this video.', 'recreate', 'motion'),
            ('Learn all of the motions in this clip.', 'learn', 'source-motions'),
            ('I want that swipe for a different film. Save it if you don’t have it.', 'learn', 'motion'),
            ('Use the swipe from this clip in a new iMessage video.', 'direct', 'film'),
            ('Replace the first message and use the transition from my other clip.', 'edit', 'changes'),
            ('Here is the reference.', 'clarify', 'film'),
        ]
        for request, job, scope in cases:
            with self.subTest(request=request):
                self.assertEqual(decide.interpret(request), (job, scope))

    def test_explicit_semantic_decision(self):
        self.assertEqual(decide.interpret('responder al mensaje', 'edit'), ('edit', 'changes'))
        self.assertEqual(decide.interpret('Make it blue.', has_project=True), ('edit', 'changes'))

    def test_catalog_coverage_joins_by_source(self):
        films=json.loads((ROOT/'assets/known-films.json').read_text())['films']
        source=next(x for x in films if x['id']=='05-linq')
        linked=decide.catalog_coverage({'matches':[source]})
        rail=next(row for row in linked if row['id']=='photos-under-fixed-heading')
        self.assertEqual(rail['source']['framesInclusive'],[1091,1111])
        self.assertTrue(Path(rail['preview']).is_file())

    def test_missing_motion_is_not_approved_from_a_low_quality_match(self):
        import tempfile
        with tempfile.TemporaryDirectory() as empty:
            result=decide.lookup('spiral sixteen marbles through a triangular wire labyrinth', Path(empty))
        self.assertEqual(result['decision'],'author_motion')
        self.assertFalse(result['seed'])

    def test_catalog_has_real_code_and_video(self):
        self.assertGreaterEqual(len(recipes.inventory()),70)
        self.assertLessEqual(len(recipes.inventory()),80)
        for key in recipes.inventory():
            item=recipes.info(key)
            self.assertTrue(Path(item['implementation']).is_file(),key)
            self.assertTrue(Path(item['preview']).is_file(),key)

    def test_published_learning_case(self):
        base=ROOT/'assets/library'
        item=learn.show(base,'toggle-thumb-then-tint')
        selected=decide.lookup(item['id'],base)
        self.assertEqual(selected['decision'],'inspect_learned_preview')
        evidence=Path(item['evidence'])
        report=json.loads(evidence.read_text())
        self.assertEqual(report['compared_frames'],36)
        decision=renderer.select([dict(engine='svg',report=str(evidence),visual_review='pass',
                                       observation='Travel then fill, visible on the sampled source frames.')])
        self.assertEqual(decision['engine'],'svg')
        negative=evidence.parent.parent/'control'/'report.json'
        result=renderer.select([dict(engine='svg',report=str(negative),visual_review='pass',
                                     observation='The target position was displaced.')])
        self.assertIsNone(result['engine'])

if __name__=='__main__':
    unittest.main()
