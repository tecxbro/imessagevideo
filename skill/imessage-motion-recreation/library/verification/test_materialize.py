import importlib.util,hashlib,json,tempfile,unittest,zipfile
from pathlib import Path
source=Path(__file__).resolve().parents[1]/'materialize.py';spec=importlib.util.spec_from_file_location('materialize',source);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class RetrievalTests(unittest.TestCase):
 def test_join_parts_checks_both_part_and_whole_hash(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);chunks=[b'complete ',b'source'];parts=[]
   for i,data in enumerate(chunks,1):
    name=f'part{i}';(root/name).write_bytes(data);parts.append({'number':i,'file_name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
   item={'parts':parts,'bytes':15,'sha256':hashlib.sha256(b''.join(chunks)).hexdigest()};out=root/'joined';mod.assemble(item,root,None,out);self.assertEqual(out.read_bytes(),b'complete source')
   (root/'part2').write_bytes(b'broken');self.assertRaises(ValueError,mod.assemble,item,root,None,root/'bad');self.assertFalse((root/'bad').exists())
 def test_pack_crc_sha_and_conflicting_file_guard(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);archive=root/'case.zip';data=b'actual complete code';checks={'file.py':hashlib.sha256(data).hexdigest()}
   with zipfile.ZipFile(archive,'w') as z:z.writestr('project/file.py',data);z.writestr('project/PACK-CHECKSUMS.json',json.dumps(checks))
   self.assertTrue(mod.extract(archive,root/'out')['pack_checksums_verified']);mod.extract(archive,root/'out')
   (root/'out/project/file.py').write_bytes(b'user edit');self.assertRaises(ValueError,mod.extract,archive,root/'out')
 def test_traversal_cannot_escape_destination(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);archive=root/'unsafe.zip'
   with zipfile.ZipFile(archive,'w') as z:z.writestr('../outside.py','no')
   self.assertRaises(ValueError,mod.extract,archive,root/'out');self.assertFalse((root/'outside.py').exists())
 def test_complementary_packs_keep_separate_checksum_receipts(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)
   for name in ['scene.py','audio.py']:
    data=name.encode();archive=root/(name+'.zip');checks={name:hashlib.sha256(data).hexdigest()}
    with zipfile.ZipFile(archive,'w') as z:z.writestr('project/'+name,data);z.writestr('project/PACK-CHECKSUMS.json',json.dumps(checks))
    self.assertTrue(mod.extract(archive,root/'out')['pack_checksums_verified'])
   self.assertEqual(len(list((root/'out/.library-receipts').glob('*.json'))),2)
   self.assertTrue((root/'out/project/scene.py').is_file());self.assertTrue((root/'out/project/audio.py').is_file())
if __name__=='__main__':unittest.main()
