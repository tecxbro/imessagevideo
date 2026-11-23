"""Exercise portable color glyphs without using system emoji artwork."""
import unittest

from ui.glyphs import GlyphText


class GlyphTextTests(unittest.TestCase):
    def test_complete_graphemes_have_editable_ink_and_advance(self):
        england_flag = "\U0001f3f4\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f"
        glyphs = ["👍🏻", "👩🏽‍💻", "🇺🇸", "1️⃣", "❤️", england_flag]
        renderer = GlyphText(
            {glyph: {"assetId": "ink", "advance": 1.25, "ink": [.125, .2, 1, .9]} for glyph in glyphs},
            {"ink": ("assets/ink.png", 16, 16)},
        )
        self.assertEqual(renderer.width("".join(glyphs), 16), 120)
        layers = renderer.layers("message.copy", ["".join(glyphs)], 10, 20, 16, 20, "#05101a")
        self.assertEqual(len(layers), 6)
        self.assertEqual([layer["x"] for layer in layers], [12, 32, 52, 72, 92, 112])
        self.assertEqual({layer["src"] for layer in layers}, {"assets/ink.png"})

    def test_reject_unknown_assets_and_split_glyph_keys(self):
        entry = {"assetId": "ink", "advance": 1, "ink": [0, 0, 1, 1]}
        with self.assertRaisesRegex(ValueError, "name a declared local image"):
            GlyphText({"🇺🇸": entry}, {})
        with self.assertRaisesRegex(ValueError, "one grapheme"):
            GlyphText({"AB": entry}, {"ink": ("assets/ink.png", 16, 16)})
