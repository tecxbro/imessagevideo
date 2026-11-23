"""Focused staging/guard checks using released actual scenes and picture metadata.
No final package/archive is built. All test writes live in temporary directories.
"""
from pathlib import Path
import copy,importlib.util,json,os,shutil,stat,tempfile,unittest,zipfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('delivery_package',ROOT/'scripts/package_delivery.py')
package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)


class PackageSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state=package.load(ROOT/'delivery-state.json')
        cls.scene=ROOT/cls.state['scenes']['04-poke']['scene']
        cls.scene_hash=package.sha(cls.scene)
        cls.identity='03-photon-mini'
        cls.scene03=package.sha(ROOT/cls.state['scenes'][cls.identity]['scene'])
        cls.records={};cls.audio={}
        for method in package.METHODS:
            picture=ROOT/'outputs'/cls.identity/(method+'.mp4')
            video=ROOT/'deliverables'/cls.identity/(method+'.mp4')
            meta=package.load(str(picture)+'.render.json')
            key=(cls.identity,method)
            cls.audio[key]=package.load(video.with_suffix('.audio.json'))
            cls.records[key]={'reference':cls.identity,'method':method,
                'picture':str(picture.relative_to(ROOT)),
                'with_reference_audio':str(video.relative_to(ROOT)),
                'sceneSHA256':cls.scene03,'pictureSHA256':package.sha(picture),
                'muxedSHA256':package.sha(video),'picturePacketsUnchanged':True,
                'probe':meta['encoding']['probe']}

    def test_fresh_stage_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'stage';package.Stage(path)
            (path/'stale.txt').write_text('stale')
            with self.assertRaisesRegex(ValueError,'fresh and empty'):package.Stage(path)

    def test_default_copy_is_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source.json';source.write_text('original')
            stage=package.Stage(root/'stage');stage.copy(source,'copied.json',immutable=True)
            self.assertNotEqual(source.stat().st_ino,(stage.root/'copied.json').stat().st_ino)
            stage.text('copied.json','replacement');self.assertEqual(source.read_text(),'original')

    def test_generated_atomic_replace_preserves_live_state(self):
        source=ROOT/'delivery-state.json';before=package.sha(source)
        with tempfile.TemporaryDirectory() as tmp:
            stage=package.Stage(Path(tmp)/'stage',True)
            stage.copy(source,'delivery-state.json',immutable=True)
            self.assertEqual(source.stat().st_ino,(stage.root/'delivery-state.json').stat().st_ino)
            stage.json('delivery-state.json',{'scenes':{'portable':'only'}})
            self.assertNotEqual(source.stat().st_ino,(stage.root/'delivery-state.json').stat().st_ino)
            self.assertEqual(package.sha(source),before)

    def test_linked_stage_extracts_as_independent_regular_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'frozen.bin';source.write_bytes(b'immutable bytes')
            stage=package.Stage(root/'stage',True);stage.copy(source,'frozen.bin',immutable=True)
            archive=root/'focused-fixture.zip'
            with zipfile.ZipFile(archive,'w') as output:output.write(stage.root/'frozen.bin','delivery/frozen.bin')
            with zipfile.ZipFile(archive) as packed:
                self.assertTrue(stat.S_ISREG(packed.getinfo('delivery/frozen.bin').external_attr>>16))
                packed.extractall(root/'extracted')
            extracted=root/'extracted/delivery/frozen.bin'
            self.assertNotEqual(extracted.stat().st_ino,source.stat().st_ino)
            extracted.write_bytes(b'edited extraction');self.assertEqual(source.read_bytes(),b'immutable bytes')

    def test_actual_canonical_bytes_both_copy_modes(self):
        for linked in (False,True):
            with self.subTest(linked=linked),tempfile.TemporaryDirectory() as tmp:
                stage=package.Stage(Path(tmp)/'stage',linked)
                package.export_scene(self.scene,Path('scenes/04-poke'),stage)
                delivered=stage.root/'scenes/04-poke/scene.json'
                self.assertEqual(package.sha(delivered),self.scene_hash)
                self.assertEqual(delivered.read_bytes(),self.scene.read_bytes())
                self.assertEqual(delivered.stat().st_ino==self.scene.stat().st_ino,linked)
                proof=package.load(delivered.with_name('provenance.json'))
                self.assertEqual(proof['portable_sha256'],self.scene_hash)
                self.assertEqual(package.sha(self.scene),self.scene_hash)

    def test_existing_wrong_asset_is_rejected(self):
        scene=package.load(self.scene)
        def first_asset(layers):
            for layer in layers:
                if layer.get('src'):return layer['src']
                found=first_asset(layer.get('children',[]))
                if found:return found
        asset=first_asset(scene['layers'])
        with tempfile.TemporaryDirectory() as tmp:
            stage=package.Stage(Path(tmp)/'stage',True)
            stage.text(Path('scenes/04-poke')/asset,'incorrect asset')
            with self.assertRaisesRegex(ValueError,'asset has different bytes'):
                package.export_scene(self.scene,Path('scenes/04-poke'),stage)
            self.assertEqual(package.sha(self.scene),self.scene_hash)

    def test_state_evidence_is_independent_of_manifest(self):
        state={'scenes':{'04-poke':self.state['scenes']['04-poke']}}
        with tempfile.TemporaryDirectory() as tmp:
            stage=package.Stage(Path(tmp)/'stage',True);package.copy_state_evidence(state,stage)
            pin=Path(state['scenes']['04-poke']['source_report'])
            self.assertTrue((stage.root/pin).is_file())
            self.assertTrue((stage.root/pin.with_name('index.html')).is_file())

    def test_visual_gate_is_required_and_copied_as_one_file(self):
        pin=self.state['scenes']['06-gallery']['source_visual_gate']
        state={'scenes':{'06-gallery':{'source_visual_gate':pin}}}
        with tempfile.TemporaryDirectory() as tmp:
            stage=package.Stage(Path(tmp)/'stage',True);package.copy_state_evidence(state,stage)
            self.assertEqual(package.sha(stage.root/pin),package.sha(ROOT/pin))
            self.assertEqual([str(p.relative_to(stage.root)) for p in stage.root.rglob('*') if p.is_file()],[pin])
            state['scenes']['06-gallery']['source_visual_gate']='verification/nonexistent-package-test-visual-gate.json'
            with self.assertRaisesRegex(ValueError,'Missing source visual gate'):
                package.copy_state_evidence(state,stage)

    def test_actual_capture_and_master_guards(self):
        # These are real released03 bytes; packet validation itself remains the
        # responsibility of finalize_delivery, not this staging unit check.
        record=self.records[(self.identity,'remotion')]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for field in ('picture','with_reference_audio'):
                source=ROOT/record[field];target=root/record[field]
                target.parent.mkdir(parents=True,exist_ok=True);os.link(source,target)
            capture=root/(record['picture']+'.render.json')
            shutil.copy2(ROOT/(record['picture']+'.render.json'),capture)
            audio=(root/record['with_reference_audio']).with_suffix('.audio.json')
            shutil.copy2((ROOT/record['with_reference_audio']).with_suffix('.audio.json'),audio)
            with patch.object(package,'ROOT',root):
                self.assertEqual(package.check_record(record,self.state,{self.identity:self.scene03}),self.audio[(self.identity,'remotion')])
                changed=package.load(capture);changed['encoding']['pictureSHA256']='0'*64
                capture.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError,'Capture picture provenance'):
                    package.check_record(record,self.state,{self.identity:self.scene03})
                shutil.copy2(ROOT/(record['picture']+'.render.json'),capture)
                master=root/record['picture'];replacement=master.with_suffix('.replacement');replacement.write_bytes(b'new master');os.replace(replacement,master)
                with self.assertRaisesRegex(ValueError,'Current master changed'):
                    package.check_record(record,self.state,{self.identity:self.scene03})

    def test_manifest_audio_coverage_and_provenance(self):
        state={'scenes':{self.identity:self.state['scenes'][self.identity]}}
        candidates=[{'path':r['with_reference_audio'],'reference_audio':True,
            'meta':r['probe'],'provenance':self.audio[key]} for key,r in self.records.items()]
        manifest={'videos':[{'id':self.identity,'sceneSHA256':self.scene03,'candidates':candidates}]}
        package.check_manifest(state,manifest,self.records,{self.identity:self.scene03},self.audio)
        bad=copy.deepcopy(manifest);bad['videos'][0]['candidates'].append(bad['videos'][0]['candidates'][0])
        with self.assertRaisesRegex(ValueError,'Duplicate/unknown'):package.check_manifest(state,bad,self.records,{self.identity:self.scene03},self.audio)
        bad=copy.deepcopy(manifest);bad['videos'][0]['candidates'][0]['provenance']['picture_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'provenance is stale'):package.check_manifest(state,bad,self.records,{self.identity:self.scene03},self.audio)

    def test_thirty_number_cannot_replace_actual_coverage(self):
        with self.assertRaisesRegex(ValueError,'cover each'):
            package.validate_inputs(self.state,{'videos':[]},{'errors':[],'validated':30,'expected':30,'videos':[]})

    def test_license_header(self):
        package.verify_license(ROOT/'shared/fonts/package/Resources/en.lproj/License.rtf')
        with tempfile.TemporaryDirectory() as tmp:
            wrong=Path(tmp)/'License.rtf';wrong.write_bytes(b'\x1f\x8bnot RTF')
            with self.assertRaisesRegex(ValueError,'real RTF'):package.verify_license(wrong)


if __name__=='__main__':unittest.main(verbosity=2)
