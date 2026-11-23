"""Regression checks for route precedence and strict last-frame verification."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

import imv
from package import skill_files


class EntryPointTests(unittest.TestCase):
    def test_package_has_one_skill_entry_point(self):
        entry_points = [path for path in skill_files(imv.ROOT) if Path(path).name == "SKILL.md"]
        self.assertEqual(entry_points, ["SKILL.md"])

    def test_ordinary_requests(self):
        cases = (
            ("Rebuild this reference film with editable layers", "reference", "recreation"),
            ("Build a launch video about sending a message", "brief", "direction"),
            ("Make an animated video about new keyboard shortcuts", None, "direction"),
            ("Add a Tapback to the last message", "project", "interaction"),
            ("Add a reaction to the last message", "project", "interaction"),
            ("Use the reference film as inspiration and make a new product video", "reference", "direction"),
            ("Change the easing on the keyboard slide", "project", "motion"),
            ("Move the heading while the pictures stay fixed", "project", "motion"),
            ("Move the heading in this reference film", "reference", "motion"),
            ("Leave the snapshots pinned while the title travels over them", None, "motion"),
            ("Show a count climb to the real total then give the statistic time to read", None, "motion"),
            ("Slow only the takeoff of the floating card", "project", "motion"),
            ("Move the sound cue three frames later", "project", "sound"),
            ("Move the reaction to the last incoming message", "project", "interaction"),
            ("Make the send click quieter in the launch video", "project", "sound"),
            ("Fix the sound in the reference video", "reference", "sound"),
            ("Register a reference footage archive", None, "dataset"),
        )
        for request, kind, expected in cases:
            with self.subTest(request=request):
                selected = imv.route(request, kind, None)
                self.assertEqual(selected["route"], expected)
                self.assertEqual(selected["workflow"], "specialist")
                self.assertTrue(all((imv.ROOT / path).is_file() for path in selected["read"]))

    def test_rational_clock_and_bounds(self):
        scene = imv.read_json(imv.ROOT / "contracts" / "example.scene.json")
        fps = Fraction(30000, 1001)
        scene["fps"] = float(fps)
        scene["duration"] = float(24 / fps)
        scene["layers"][0]["keyframes"]["x"][1]["t"] = float(12 / fps)
        scene["timeline"]["picture"].update(fpsNum=fps.numerator, fpsDen=fps.denominator)
        result = imv.resolve(scene)
        self.assertEqual(result["events"][0]["sample"], 19219)
        self.assertEqual(result["cues"][0]["sample"], 19339)

        changed = copy.deepcopy(scene)
        changed["timeline"]["events"][0]["frame"] = 24
        with self.assertRaisesRegex(ValueError, "inside the picture"):
            imv.resolve(changed)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, output = root / "scene.json", root / "picture.mp4"
            project.write_text(json.dumps(scene), encoding="utf-8")
            report = imv.render(project, output, "pillow")
            self.assertEqual(report["fps"], "30000/1001")
            self.assertEqual(report["lastFrameTime"], "23023/30000")

            cut = root / "cut.mp4"
            imv.local_video("ffmpeg", output, [
                "-frames:v", "23", "-c:v", "libx264", "-threads", "1", str(cut),
            ], decode=True)
            with self.assertRaisesRegex(ValueError, "frame count"):
                imv.audit_video(cut, scene)


if __name__ == "__main__":
    unittest.main()
