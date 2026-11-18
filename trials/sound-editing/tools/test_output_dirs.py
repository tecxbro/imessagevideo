"""Export helpers must work when Git omitted every file in an output folder."""
from pathlib import Path
import tempfile
import unittest
import numpy as np
from build_treatments import write
from render_mix import encode


class OutputDirectoryTests(unittest.TestCase):
    def test_nested_json(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'missing/receipts/output.json'
            write(path,{'status':'pass'})
            self.assertIn('pass',path.read_text())

    def test_nested_flac(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'missing/stems/ui.flac'
            encode(path,np.zeros((4800,2)),aac=False)
            self.assertTrue(path.is_file())

    def test_invalid_audio_creates_no_directory(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'missing/ui.flac'
            with self.assertRaises(ValueError):encode(path,np.ones((10,2)),aac=False)
            self.assertFalse(path.parent.exists())


if __name__=='__main__':unittest.main()
