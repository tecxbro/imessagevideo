"""Small in-memory/tiny-temporary fixtures; never build/extract final delivery."""
from pathlib import Path
import base64,hashlib,importlib.util,io,json,stat,tempfile,unittest,warnings,zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('zip_audit',ROOT/'verification/audit_delivery_zip.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
OUTER='imessage-recreations';SKILL='imessage-motion-recreation';SKILL_ZIP='imessage-motion-recreation-skill.zip';SKILL_TREE='skill/'+SKILL


def digest(data):return hashlib.sha256(data).hexdigest()
def checksums(files):return {name:digest(data) for name,data in files.items() if name!='checksums.json'}
def archive_bytes(prefix,files,manifest=None,extra=None,modes=None,compression=zipfile.ZIP_DEFLATED):
    entries=dict(files);entries['checksums.json']=json.dumps(checksums(files) if manifest is None else manifest).encode();entries.update(extra or {});output=io.BytesIO()
    with zipfile.ZipFile(output,'w') as packed:
        for name,data in entries.items():
            info=zipfile.ZipInfo(prefix+'/'+name);info.create_system=3;info.external_attr=((modes or {}).get(name,stat.S_IFREG|0o644))<<16
            packed.writestr(info,data,compress_type=compression)
    return output.getvalue()

def delivery_files(skill_files=None,skill_manifest=None):
    skill_files={'SKILL.md':b'Instructions only','scripts/tool.py':b'print("source")\n',**(skill_files or {})};nested=archive_bytes(SKILL,skill_files,manifest=skill_manifest)
    result={'README.md':b'Portable review',SKILL_ZIP:nested}
    with zipfile.ZipFile(io.BytesIO(nested)) as packed:
        for info in packed.infolist():result[SKILL_TREE+'/'+info.filename[len(SKILL)+1:]]=packed.read(info)
    return result


class StreamedZipAudit(unittest.TestCase):
    def run_bytes(self,data,stage_change=None):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive=root/'tiny-delivery.zip';archive.write_bytes(data);stage=None
            if stage_change is not None:
                stage=root/'stage';stage.mkdir()
                with zipfile.ZipFile(io.BytesIO(data)) as packed:
                    for info in packed.infolist():
                        relative=info.filename[len(OUTER)+1:];target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(packed.read(info))
                if stage_change:(stage/'README.md').write_bytes(b'changed stage')
            result=audit.audit_delivery(archive,stage=stage)
            self.assertFalse((root/'outside.txt').exists())
            return result

    def test_full_outer_nested_expanded_and_stage_pass(self):
        report=self.run_bytes(archive_bytes(OUTER,delivery_files()),stage_change=False)
        self.assertTrue(report['passed'],report['errors']);self.assertTrue(report['skillRepresentationsIdentical']);self.assertTrue(report['stage']['passed'])
        self.assertEqual(report['outer']['entryCount'],report['outer']['crcVerifiedEntries']);self.assertEqual(report['nestedSkill']['entryCount'],report['nestedSkill']['crcVerifiedEntries'])
        nested_manifest=SKILL_TREE+'/checksums.json'
        self.assertIn(nested_manifest,[e.get('relativePath') for e in report['outer']['entries']])

    def test_root_manifest_coverage_rejects_unhashed_extra(self):
        report=self.run_bytes(archive_bytes(OUTER,delivery_files(),extra={'extra.txt':b'not hashed'}))
        self.assertFalse(report['passed']);self.assertIn('extra.txt',report['outer']['coverage']['unhashedEntries'])

    def test_root_manifest_coverage_rejects_missing_payload(self):
        files=delivery_files();manifest=checksums(files);manifest['absent.txt']='0'*64
        report=self.run_bytes(archive_bytes(OUTER,files,manifest=manifest));self.assertFalse(report['passed']);self.assertIn('absent.txt',report['outer']['coverage']['missingEntries'])

    def test_nested_checksum_is_not_exempt_from_outer_hashing(self):
        files=delivery_files();manifest=checksums(files);del manifest[SKILL_TREE+'/checksums.json']
        report=self.run_bytes(archive_bytes(OUTER,files,manifest=manifest));self.assertFalse(report['passed']);self.assertIn(SKILL_TREE+'/checksums.json',report['outer']['coverage']['unhashedEntries'])

    def test_sha_mismatch_with_valid_crc_fails(self):
        files=delivery_files();manifest=checksums(files);manifest['README.md']='0'*64
        report=self.run_bytes(archive_bytes(OUTER,files,manifest=manifest));self.assertFalse(report['passed']);self.assertEqual(report['outer']['coverage']['sha256Mismatches'],['README.md'])

    def test_crc_corruption_is_streamed_and_reported(self):
        data=bytearray(archive_bytes(OUTER,delivery_files(),compression=zipfile.ZIP_STORED))
        with zipfile.ZipFile(io.BytesIO(data)) as packed:info=packed.getinfo(OUTER+'/README.md')
        offset=info.header_offset+30+len(info.filename.encode())+len(info.extra);data[offset]^=1
        report=self.run_bytes(data);self.assertFalse(report['passed']);self.assertLess(report['outer']['crcVerifiedEntries'],report['outer']['entryCount'])
        self.assertTrue(any('stream/CRC' in e['problem'] for e in report['errors']))

    def test_traversal_path_is_rejected_without_extracting(self):
        report=self.run_bytes(archive_bytes(OUTER,delivery_files(),extra={'../outside.txt':b'never extracted'}));self.assertFalse(report['passed'])
        self.assertTrue(any('traversal' in e['problem'] for e in report['errors']))

    def test_symlink_metadata_is_rejected(self):
        files=delivery_files();files['link']=b'../elsewhere'
        report=self.run_bytes(archive_bytes(OUTER,files,modes={'link':stat.S_IFLNK|0o777}));self.assertFalse(report['passed'])
        self.assertTrue(any('regular file' in e['problem'] for e in report['errors']))

    def test_duplicate_names_are_rejected(self):
        output=io.BytesIO(archive_bytes(OUTER,delivery_files()))
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with zipfile.ZipFile(output,'a') as packed:
                info=zipfile.ZipInfo(OUTER+'/README.md');info.create_system=3;info.external_attr=(stat.S_IFREG|0o644)<<16;packed.writestr(info,b'Portable review')
        report=self.run_bytes(output.getvalue());self.assertFalse(report['passed']);self.assertTrue(any('duplicate ZIP' in e['problem'] for e in report['errors']))

    def test_case_collisions_are_rejected(self):
        files=delivery_files();files['readme.md']=b'collision'
        report=self.run_bytes(archive_bytes(OUTER,files));self.assertFalse(report['passed']);self.assertTrue(any('extraction collision' in e['problem'] for e in report['errors']))

    def test_skill_font_extension_is_rejected(self):
        report=self.run_bytes(archive_bytes(OUTER,delivery_files({'font.otf':b'font bytes'})));self.assertFalse(report['passed']);self.assertTrue(any('font/video filename' in e['problem'] for e in report['errors']))

    def test_skill_renamed_font_binary_is_rejected(self):
        report=self.run_bytes(archive_bytes(OUTER,delivery_files({'opaque.dat':b'OTTO'+b'\0'*100})));self.assertFalse(report['passed']);self.assertTrue(any('font binary signature' in e['problem'] for e in report['errors']))

    def test_skill_renamed_video_binary_is_rejected(self):
        report=self.run_bytes(archive_bytes(OUTER,delivery_files({'opaque.dat':b'\0\0\0\x18ftypmp42'+b'\0'*50})));self.assertFalse(report['passed']);self.assertTrue(any('video/container' in e['problem'] for e in report['errors']))

    def test_embedded_font_data_uri_is_rejected(self):
        data=b'{"font":"data:font/woff2;base64,'+base64.b64encode(b'wOF2'+b'\0'*64)+b'"}'
        report=self.run_bytes(archive_bytes(OUTER,delivery_files({'fixture.json':data})));self.assertFalse(report['passed']);self.assertTrue(any('embedded font/woff2' in e['problem'] for e in report['errors']))

    def test_nested_manifest_sha_is_verified(self):
        manifest={'SKILL.md':'0'*64,'scripts/tool.py':digest(b'print("source")\n')}
        report=self.run_bytes(archive_bytes(OUTER,delivery_files(skill_manifest=manifest)));self.assertFalse(report['passed']);self.assertFalse(report['nestedSkill']['coverage']['passed'])

    def test_skill_folder_must_match_installable_zip(self):
        files=delivery_files();files[SKILL_TREE+'/SKILL.md']=b'different expanded folder'
        report=self.run_bytes(archive_bytes(OUTER,files));self.assertFalse(report['passed']);self.assertFalse(report['skillRepresentationsIdentical'])

    def test_stage_hash_drift_is_rejected(self):
        report=self.run_bytes(archive_bytes(OUTER,delivery_files()),stage_change=True);self.assertFalse(report['passed']);self.assertEqual(report['stage']['sha256Mismatches'],['README.md'])


if __name__=='__main__':unittest.main(verbosity=2)
