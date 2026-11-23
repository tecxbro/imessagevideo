"""Regressions from the shared-contract and cold authoring checks."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from .adapter import compile_conversation
from .tracks import loop_layers

EXAMPLES = Path(__file__).with_name("examples")


def fixture(name):
    return json.loads((EXAMPLES / name).read_text(encoding="utf8"))


def compile_fixture(doc):
    return compile_conversation(doc, input_dir=EXAMPLES, output_dir=EXAMPLES)


def layers(scene):
    return {node["id"]: node for node in loop_layers(scene["layers"])}


def value_at(node, prop, frame, fps):
    track = node.get("keyframes", {}).get(prop, [])
    return next((key["value"] for key in reversed(track) if key["t"] <= frame / fps),
                node.get(prop, 0))


class AdapterRegressionTests(unittest.TestCase):
    def test_mock_approval_follows_one_card_and_dismissal_does_not_settle_it(self):
        doc = fixture("payment-mock.json")
        scene = compile_fixture(doc)
        events = scene["timeline"]["events"]
        self.assertEqual([event["target"] for event in events], ["request"] * 4)
        self.assertEqual([event["uiState"]["viewport"]["surface"] for event in events],
                         ["conversation", "payment-approval", "conversation", "conversation"])
        card = layers(scene)["ui.message/request/card"]
        self.assertEqual([part["start"] for part in card["children"]], [14 / 24, 78 / 24])

        missing_dismissal = deepcopy(doc)
        missing_dismissal["events"].pop(2)
        with self.assertRaisesRegex(ValueError, "dismiss the mock approval"):
            compile_fixture(missing_dismissal)

        missing_review = deepcopy(doc)
        del missing_review["events"][1:3]
        with self.assertRaisesRegex(ValueError, "explicit dismissal of that card"):
            compile_fixture(missing_review)

        replaced_review = deepcopy(doc)
        replaced_review["events"][2]["surface"] = "list"
        with self.assertRaisesRegex(ValueError, "dismiss the mock approval into the thread"):
            compile_fixture(replaced_review)

        invalid_target = deepcopy(doc)
        invalid_target["events"][1]["messageId"] = "question"
        with self.assertRaisesRegex(ValueError, "requires a requested payment-mock"):
            compile_fixture(invalid_target)

    def test_retargeted_reaction_scroll_and_typing_survive_shared_readback(self):
        doc = fixture("conversation.json")
        doc["initial"]["draft"] = "I will meet you by the north exit. " * 4
        for event in doc["events"]:
            if event["id"] == "station.send":
                event["frame"] = 19
            elif event["id"] == "station.love":
                event.update(messageId="meet", mark="Wow")
        scene = compile_fixture(doc)
        events = {event["id"]: event for event in scene["timeline"]["events"]}
        sent = events["station.send"]
        self.assertEqual(sent["frame"], 19)
        self.assertEqual(sent["uiState"]["composer"],
                         {"text": "", "focused": True, "keyboardVisible": True})
        self.assertEqual(events["station.typing"]["uiState"]["typingSenderIds"], ["morgan"])
        self.assertEqual(events["station.reply"]["uiState"]["typingSenderIds"], [])
        reaction = events["station.love"]
        self.assertEqual(reaction["layerIds"], ["ui.message/meet/reaction"])
        scrolled = events["station.scroll"]["uiState"]
        sent_message = next(message for message in scrolled["messages"] if message["id"] == "meet")
        self.assertEqual(sent_message["reactions"], {"alex": "Wow"})
        self.assertGreater(scrolled["viewport"]["scrollOffset"], 0)

    def test_zero_duration_cut_has_no_extra_motion_frame(self):
        doc = fixture("field-notes.json")
        receive = next(event for event in doc["events"] if event["kind"] == "receive")
        receive["durationFrames"] = 0
        receive["message"]["card"]["detail"] *= 10
        media = next(event for event in doc["events"] if event.get("surface") == "media")
        media["durationFrames"] = 0
        scene_layers = layers(compile_fixture(doc))
        transcript = scene_layers["ui.transcript"]
        overlay = scene_layers["ui.overlay"]
        self.assertLess(value_at(transcript, "y", 176, 24), value_at(transcript, "y", 175, 24))
        self.assertEqual(value_at(transcript, "y", 176, 24), value_at(transcript, "y", 177, 24))
        self.assertEqual(value_at(overlay, "y", 146, 24), 0)
        self.assertEqual(value_at(overlay, "y", 147, 24), 0)
        self.assertEqual(value_at(overlay, "opacity", 146, 24), 1)

    def test_empty_edit_keeps_attachment_but_requires_text_on_text_only_row(self):
        doc = fixture("field-notes.json")
        edit = next(event for event in doc["events"] if event["kind"] == "edit")
        edit["text"] = ""
        with self.assertRaisesRegex(ValueError, "edited message"):
            compile_fixture(doc)
        revised = deepcopy(doc)
        next(event for event in revised["events"] if event["kind"] == "edit")["messageId"] = "photos"
        events = compile_fixture(revised)["timeline"]["events"]
        message = next(message for event in events if event["kind"] == "edit"
                       for message in event["uiState"]["messages"] if message["id"] == "photos")
        self.assertEqual(message["text"], "")
        self.assertEqual(message["attachmentIds"], ["north", "south"])

    def test_contact_thread_keeps_editable_shape_and_camera_ownership(self):
        scene_layers = layers(compile_fixture(fixture("contact-thread.json")))
        camera = scene_layers["ui.camera"]
        self.assertEqual([node["id"] for node in camera["children"]], ["ui.handset", "ui.screen"])
        screen = scene_layers["ui.screen"]
        self.assertGreater(screen["clip"]["radius"], 0)
        avatar = scene_layers["ui.header.avatar"]
        image = scene_layers["ui.header.avatar.image"]
        self.assertEqual(avatar["clip"]["width"], avatar["clip"]["radius"] * 2)
        self.assertGreater(image["width"], avatar["clip"]["width"])
        self.assertLess(image["x"], 0)
        self.assertNotIn("ui.message/arriving.tail", scene_layers)
        self.assertEqual(scene_layers["ui.message/door.tail"]["scaleX"], -1)
        self.assertEqual(scene_layers["ui.message/coming.tail"]["scaleX"], 1)
        self.assertEqual(scene_layers["ui.message/coming.ink"]["type"], "rect")
        self.assertEqual(scene_layers["ui.message/coming.copy.runs"]["text"], "On my way down.")

    def test_contact_thread_typing_is_on_picture_clock_and_resets_on_receive(self):
        doc = fixture("contact-thread.json")
        doc["events"].extend([
            {"id": "pickup.typing-again", "kind": "typing", "frame": 105, "senderId": "jamie", "active": True},
        ])
        scene = compile_fixture(doc)
        scene_layers = layers(scene)
        typing = scene_layers["ui.typing"]
        dots = [scene_layers[f"ui.typing.dot.{index}"] for index in range(1, 4)]
        self.assertEqual(value_at(typing, "opacity", 51, 24), 0)
        self.assertGreater(value_at(typing, "opacity", 52, 24), 0)
        self.assertEqual(value_at(typing, "opacity", 86, 24), 0)
        self.assertEqual([value_at(dot, "opacity", 105, 24) for dot in dots], [.44] * 3)
        self.assertNotEqual([value_at(dot, "opacity", 56, 24) for dot in dots], [.44] * 3)
        for dot in dots:
            keys = dot["keyframes"]["opacity"]
            self.assertTrue(all(abs(key["t"] * 24 - round(key["t"] * 24)) < 1e-8 for key in keys))
        timeline = {event["id"]: event for event in scene["timeline"]["events"]}
        self.assertEqual(timeline["pickup.typing"]["layerIds"], ["ui.typing"])
        self.assertEqual(timeline["pickup.reply"]["uiState"]["typingSenderIds"], [])

    def test_contact_thread_asset_is_explicit_and_handset_is_optional(self):
        doc = fixture("contact-thread.json")
        doc["avatarAssetId"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown avatar asset missing"):
            compile_fixture(doc)
        del doc["avatarAssetId"], doc["display"]["handset"], doc["canvas"]
        scene = compile_fixture(doc)
        scene_layers = layers(scene)
        self.assertNotIn("ui.handset", scene_layers)
        self.assertEqual(scene["width"], doc["display"]["width"])
        self.assertEqual(scene_layers["ui.header.avatar.initials"]["text"], "JR")


if __name__ == "__main__":
    unittest.main()
