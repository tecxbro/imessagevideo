import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import export

class ExportTest(unittest.TestCase):
    def test_encoded_true_peak_gate(self):
        with patch.object(export.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stderr=json.dumps({'input_i':'-25','input_tp':'-9.2'}))):
            self.assertEqual(export.true_peak(Path('encoded-aac.mp4'))['input_tp'],'-9.2')
        for stderr in [json.dumps({'input_i':'-25','input_tp':'-.9'}),'no measurement']:
            with patch.object(export.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stderr=stderr)):
                with self.assertRaises(RuntimeError):export.true_peak(Path('encoded-aac.mp4'))

    def test_existing_export_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'already-published.mp4';path.write_bytes(b'immutable fixture')
            with patch.object(export.sys,'argv',['export.py','--out',str(path)]),patch.object(export.subprocess,'run') as run:
                with self.assertRaises(FileExistsError):export.main()
                run.assert_not_called()
            self.assertEqual(path.read_bytes(),b'immutable fixture')

if __name__=='__main__':unittest.main()
