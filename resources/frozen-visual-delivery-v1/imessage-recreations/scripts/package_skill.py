#!/usr/bin/env python3
"""Package the skill with reproducible renderer source and captured execution logs."""
from pathlib import Path
import shutil,json,zipfile,hashlib

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skill/imessage-motion-recreation'

def copy(src,dest):
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)

def main():
    # Source only: no node_modules, caches, executables, original fonts or reference video.
    engine_names={'common.mjs','scene-loader.mjs','runtime-scene.mjs','web-runtime.mjs','remotion-entry.jsx',
        'motion-canvas-runtime.mjs','render.mjs','render_checkpoints.mjs',
        'render_motion_canvas.mjs','render_pillow.py','snapshot_scene.py',
        'package.json','package-lock.json','requirements.txt','README.md'}
    for p in (SKILL/'scripts/engines').glob('*'):
        if p.is_file() and p.name not in engine_names:p.unlink()
    for name in engine_names:
        copy(ROOT/'engines'/name,SKILL/'scripts/engines'/name)
    for name in ['compare.py','measure_phone.py','scan_timeline.py','prove_scene_scope.mjs','validate_review.mjs','test_package_delivery.py','audit_packaged_html.py','audit_delivery_zip.py','test_audit_delivery_zip.py','README.md']:
        copy(ROOT/'verification'/name,SKILL/'scripts/verification'/name)
    for p in (ROOT/'shared').glob('*'):
        if p.is_file():copy(p,SKILL/'scripts/shared'/p.name)
    copy(ROOT/'figma/prepare-figma.mjs',SKILL/'scripts/figma/prepare-figma.mjs')
    copy(ROOT/'figma/README.md',SKILL/'scripts/figma/README.md')
    if (ROOT/'render-overrides.json').exists():copy(ROOT/'render-overrides.json',SKILL/'references/render-overrides.json')
    copy(ROOT/'verification/packaging-audit/ZIP-AUDIT.md',SKILL/'scripts/verification/ZIP-AUDIT.md')
    for name in ['build_review.py','build_final_quality.py','add_reference_audio.py','verify_scene_assets.py','check_declared_font_coverage.py','verify_method_parity.py','final_encode.py','finalize_delivery.py','package_delivery.py','package_skill.py']:
        copy(ROOT/'scripts'/name,SKILL/'scripts'/name)
    for ref in sorted((ROOT/'references').iterdir()):
        if not ref.is_dir():continue
        evidence={p.name:p for pattern in ['steps*.md','lessons*.md','iteration-notes*.md','analysis.md','source.json','segments.json','QUALITY.md','quality.md'] for p in ref.glob(pattern)}
        for name,p in evidence.items():
            if p.exists():copy(p,SKILL/'references/evidence'/ref.name/name)
    # The outline tracer is a source-independent helper, not a bundled source asset.
    copy(ROOT/'references/02-danieltian/trace_glyphs.py',SKILL/'scripts/trace_glyphs.py')
    copy(ROOT/'references/04-poke/rank_glyph_shapes.py',SKILL/'scripts/rank_glyph_shapes.py')
    for area in ['engines','verification','figma']:
        for p in (ROOT/area).glob('steps*.md'):
            copy(p,SKILL/'references/evidence'/area/p.name)
    for area in ('motion-canvas-text-inventory','motion-canvas-kerning-inventory'):
        for p in (ROOT/'outputs/alternative-methods'/area).glob('*.json'):
            copy(p,SKILL/'references/evidence'/area/p.name)
    for p in [ROOT/'figma/status.json',ROOT/'verification/fidelity-review/findings.json',
              ROOT/'verification/fidelity-review/findings.md',ROOT/'shared/fonts/provenance.json',
              ROOT/'verification/font-style-once-parity.json',
              ROOT/'verification/runtime-prune-actual-parity.json',ROOT/'verification/runtime-prune-chunk-parity.json',
              ROOT/'verification/tracer-scalar-parity.json',ROOT/'verification/remotion-browser-reuse-parity.json',ROOT/'verification/remotion-v13-all-frames-parity.json',ROOT/'verification/portable-scene-parity.json',ROOT/'verification/font-coverage-notes.json',
              ROOT/'verification/superseded-prototype-archives.json',ROOT/'verification/final-quality.json',
              ROOT/'verification/superseded-canonical-archives.json',
              ROOT/'verification/snapshot-idempotence.json',
              ROOT/'verification/snapshot-compressed-input-parity.json',
              ROOT/'shared/fonts/license-repair.json',
              ROOT/'verification/packaging-audit/storage-cleanup.json',
              ROOT/'verification/packaging-audit/portable-canonical-assets.json',
              ROOT/'verification/packaging-audit/package-focused-tests.json',
              ROOT/'verification/review-browser.json',
              ROOT/'verification/final-source-summary.json',
              ROOT/'verification/delivery-holds.json',
              ROOT/'verification/delivery-holds-before-normal-resolution.json',
              ROOT/'verification/delivery-hold-preflight.json',
              ROOT/'verification/06-private-prototype-archives.json',
              ROOT/'verification/06-private-pre20-archives.json',
              ROOT/'verification/02-superseded-helper-payload-archives.json',
              ROOT/'verification/packaging-audit/html-portability.json',
              ROOT/'verification/packaging-audit/viewer-image-checksums.json',
              ROOT/'verification/packaging-audit/zip-audit-tool-tests.json',
              ROOT/'verification/final/motion-canvas-text-baseline52/ranked-release.json',
              ROOT/'verification/final/motion-canvas-text-baseline52/rms-assay/comparison.json',
              ROOT/'verification/final/motion-canvas-text-baseline52/svg-causal-control/comparison.json',
              ROOT/'verification/final/motion-canvas-text-baseline52/svg-causal-control/geometry.json',
              ROOT/'verification/final/poke-kerning-probe/finding.json',
              ROOT/'verification/final/normal-kerning-safety/release-gate.json',
              ROOT/'verification/05-raster-parity-607/repair-journal.json',
              ROOT/'verification/05-raster-parity-607/fresh-same-process/comparison.json',
              ROOT/'verification/05-final-v20-primary-parity.json',
              ROOT/'verification/05-final-v20-html-parity.json',
              ROOT/'outputs/02-danieltian/final-v19/private-prototype-archives.json',
              ROOT/'outputs/02-danieltian/final-v19/remotion-gsap-all-native-parity.json',
              ROOT/'outputs/02-danieltian/final-v19/html-gsap-all-native-parity.json',
              ROOT/'outputs/05-linq/root-cash-plane-v20/release.json',
              ROOT/'outputs/05-linq/root-cash-plane-v20/quantized-scope.json',
              ROOT/'outputs/05-linq/root-cash-plane-v20/quantized-metrics.json',
              ROOT/'engines/fixtures/pillow-coordinate-conditioning/release-report.json',
              ROOT/'engines/fixtures/pillow-coordinate-conditioning/production-completion.json',
              ROOT/'outputs/alternative-methods/pillow-avatar-diagnosis/affected-scope-audit.json',
              ROOT/'verification/final/06-gallery/v23/text-metric-diagnosis/release-proposal.json',
              ROOT/'verification/final/06-gallery/v23/text-metric-diagnosis/dom-boundary-validation.json',
              ROOT/'outputs/alternative-methods/motion-canvas-text-inventory/release-report.json',
              ROOT/'verification/final/motion-canvas-text-box-release.json',
              ROOT/'verification/generated-bundle-cleanup.json',
              ROOT/'outputs/alternative-methods/04-history-cleanup-ledger.json',
              ROOT/'outputs/alternative-methods/04-font-baselines.json',
              ROOT/'verification/comparison-frame-selection-parity.json',ROOT/'verification/batch-native-decode-parity.json',
              ROOT/'verification/batch-native-coalesced-parity.json',
              ROOT/'verification/native-cadence-rounding-parity.json',
              ROOT/'verification/05-raster-parity-625/diagnostic.json',ROOT/'verification/05-raster-parity-625/native-ssim-diagnostic.json',
              ROOT/'references/02-danieltian/phonebook-v14/superseded-scene-archives.json',
              ROOT/'engines/fixtures/shadow-opacity/release-report.json',ROOT/'engines/fixtures/shadow-opacity/capture-audit.json',ROOT/'engines/fixtures/shadow-opacity/scene.json',
              ROOT/'engines/fixtures/shadow-opacity/actual-property-audit.json',ROOT/'engines/fixtures/shadow-opacity/coordinator-pause-report.json',ROOT/'engines/fixtures/shadow-opacity/combined-fixture-report.json',
              ROOT/'engines/fixtures/startup-recalculation/diagnosis.json',
              ROOT/'verification/motion-canvas-transport/report.json',ROOT/'engines/fixtures/dynamic-path/report.json',ROOT/'engines/fixtures/anisotropic-blur/release-report.json',ROOT/'verification/encode-range/RECOMMENDATION.md',
              ROOT/'references/02-danieltian/phonebook-v14/alpha-fixture/report.json']:
        if p.exists():copy(p,SKILL/'references/evidence'/p.parent.name/p.name)
    setup='''# Running the bundled tools

The package contains source, schema, dependency pins and detailed execution evidence. It does not include generated video, dependency directories, browser binaries, or proprietary font binaries.

For a standalone project, copy scripts/engines, scripts/shared and scripts/verification to its root as engines, shared and verification, and copy scripts/*.py into its scripts directory. The project utilities locate delivery-state.json, references and outputs beside those directories. The portable delivery archive already has that layout. Install JavaScript dependencies with `cd engines` then `npm ci`; engines may also be run directly from this skill's scripts/engines directory with explicit scene/output paths. The browser adapters need an installed Chromium (set CHROME_PATH if its path differs from /usr/bin/chromium) and FFmpeg. Python needs the pinned packages in engines/requirements.txt; use a local virtual environment. FontTools can subset actual verified fonts into WOFF without a Brotli dependency. Obtain any source fonts from their original provider and preserve the license; this package records the Apple source and hashes, not the binaries.

Use scripts/shared/SCHEMA.md for measured scene authoring. Run the engines from the scripts directory as described in scripts/engines/README.md. The neutral smoke tests in the original project proved capability only. The Figma converter remains an unexecuted prototype because account discovery did not respond; follow its audit and the installed Figma skills before use.

Per-source observations and step logs are in references/evidence. The execution-ledger.md distinguishes observed facts, failed attempts and corrections. A future run must acquire its own actual reference and repeat fidelity checks.
'''
    (SKILL/'RUNNING.md').write_text(setup)
    files=sorted(p for p in SKILL.rglob('*') if p.is_file() and p!=SKILL/'checksums.json')
    (SKILL/'checksums.json').write_text(json.dumps({str(p.relative_to(SKILL)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
    archive=ROOT/'imessage-motion-recreation-skill.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(SKILL.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(SKILL.parent))
    local=ROOT.parent/'.agents/skills/imessage-motion-recreation'
    shutil.copytree(SKILL,local,dirs_exist_ok=True)
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'installed_workspace_skill':str(local),'files':len(files)+1},indent=2))

if __name__=='__main__':main()
