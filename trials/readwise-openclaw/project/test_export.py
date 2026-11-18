import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import export
from audio import master_audio

class ExportTest(unittest.TestCase):
    def test_delivery_loudness_bounds(self):
        export.validate_delivery({'input_i':'-16.6','input_tp':'-1.8'},-16.4)
        for data in [{'input_i':'-18','input_tp':'-2'},{'input_i':'-16.4','input_tp':'-.9'}]:
            with self.assertRaises(RuntimeError):export.validate_delivery(data,-16.4)
        with self.assertRaises(RuntimeError):master_audio.read_measurement('')
        with self.assertRaises(ValueError):master_audio.read_measurement('{"input_i":"-inf","input_tp":"-inf"}')

    def test_encoded_true_peak_gate(self):
        with patch.object(export.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stderr=json.dumps({'input_i':'-25','input_tp':'-9.2'}))):
            self.assertEqual(export.true_peak(Path('encoded-aac.mp4'))['input_tp'],'-9.2')
        for stderr in [json.dumps({'input_i':'-25','input_tp':'-.9'}),'no measurement']:
            with patch.object(export.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stderr=stderr)):
                with self.assertRaises(RuntimeError):export.true_peak(Path('encoded-aac.mp4'))

    def test_existing_export_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'already-published.mp4';path.write_bytes(b'immutable fixture')
            with patch.object(export.sys,'argv',['export.py','--out',str(path),'--source','source.mp4','--first','first.mp4']),patch.object(export.subprocess,'run') as run:
                with self.assertRaises(FileExistsError):export.main()
                run.assert_not_called()
            self.assertEqual(path.read_bytes(),b'immutable fixture')

    def test_fresh_export_uses_external_evidence_directory(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d).resolve()/'new-delivery.mp4'
            source=Path(d)/'source.mp4';source.touch()
            first=Path(d)/'first.mp4';first.touch()
            argv=['export.py','--out',str(out),'--source',str(source),'--first',str(first)]
            with patch.object(export.sys,'argv',argv),patch.object(export,'attempt',side_effect=RuntimeError('stop before capture')) as attempt:
                with self.assertRaisesRegex(RuntimeError,'stop before capture'):export.main()
            self.assertEqual(attempt.call_args.args[0],out.with_name(out.name+'.evidence')/'LOG.md')
            self.assertFalse(out.exists())

if __name__=='__main__':unittest.main()
