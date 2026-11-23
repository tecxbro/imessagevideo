from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import csv, hashlib, json, subprocess

root=Path('codex-direction-library')
work=Path('/tmp/imv-goal-production-01-02')
out=Path('codex-trial/review/imv-v3/goal-audit/production-01-02-manifest.tsv')
commit='c49482aec7b8ed0b840f97c61a5e5b860c4077b6'
manual={
'01': {'analysis.md','steps-rebuild.md','steps.md','apply-root-alpha-v10.py','apply-root-alpha-v10-continuous-rejected.py','apply_v9_repairs.py','build-scenes.py','fix-clipped-card-transforms.py','refine-intro-cursor-press.py','refine-local-flips.py','track-wall-ocr.py','assets/SFProDisplay-Medium-v1.failed.html','assets/SFProDisplay-Medium.failed.html','assets/SFProDisplay-Regular.failed.html','assets/apple-fonts.css'},
'02': {'analysis.md','steps-rebuild.md','steps.md','steps-root-copy.md','steps-root-final.md','steps-root-header-exit-v17.md','steps-root-house-v17.md','steps-phonebook.md','muse-continuation-v19/measure-overlaps.py','muse-continuation-v19/apply.py','muse-continuation-v19/gate.py','muse-continuation-v19/prove.py','freeze-v19.py','prove-v19.py','prove-v19-avatar-native.mjs','refine-v11-phone-exit.py','apply-root-house-v17.py','apply-root-header-exit-v17.py','final-midstate-fix/validate_native.py','phonebook-v14/verify_helper_equivalence.py'},
}

manual['01'].update({
    'apply-intro-review.py','apply-title-lifetime-review.py','apply-wall-title-fit.mjs',
    'apply_call_entrance_v8.py','apply_early_walls_v7.py','build-title-lifetime-review.py',
    'build_edge_poses_v8.py','build_v9_mail.py','build_v9_sms.py','build_v9_sms_poses.py',
    'compare-wall-previews.py','entrance-v8-measure/check.py','perspective-v9-measure/diagnose.py',
    'finish_wall_components_v6.py','fit-font.py','fit-fonts.py','fit-wall-titles.py','fit_free_v6.py',
    'fit_wall_headings_v6.py','patch-email-wall.py','track_wall_cards_v6.py','track_early_wall_cards_v7.py',
    'preview-final-walls.mjs','preview-held.mjs','preview-local-flips.mjs','preview-walls.mjs',
    'refine-free-zoom.py','v9-repair/check_dense.py','v9-repair/check_expanded.py',
    'v9-repair/check_expanded_6.py','v9-repair/check_peaks.py','build-intro-review.py',
    'rebuild-walls.py','rebuild-walls-overlap.py','refine-wall-fits.py','refine_wall_v6.py',
    'refine-channel-stack.py','trace-wall-titles.py','track-title-words.py','vector_free_v6.py',
    'refine-cta-native.py','refine-cta-pose-art.py','refine-held-graphics.py','refine-intro-native-2.py',
    'restore-edge-artwork.py','track-wall-elements.py',
})
assert len(manual['01']) == 61
manual['02'].update(f'freeze-v{version}.py' for version in range(14,19))
manual['02'].update(f'run-browser-v{version}.py' for version in range(14,20))
manual['02'].update({'refine-middle-every-frame.py','refine-middle-motion.py'})



manual['02'].update({
    'apply-orb-exit-v18.py','orb-exit-v18/measure.py','orb-exit-v18/prepare_probe.mjs',
    'orb-exit-v18/archive_authorized_histories.py','prove-v11-merged-scope.mjs','prove-v11-scope.mjs',
    'prove-v12-scope.mjs','prove-v15.mjs','prove-v16.mjs','prove-v17.mjs','prove-v18.py',
    'verify-browser-v19-parity.py','batch-gate-handoff-v14.py','apply-early-end-refinement.py',
    'apply-endcard-refinement.py','apply-middle-refinement.py','apply-header-formation-final.py',
    'apply-intro797-review.py','apply-phonebook-birth.py','apply-phonebook-native-unfold.py',
    'apply-v11-refinements.py','apply-root-copy.py','apply-root-query-camera.py','apply-root-query-fade.py',
    'apply-root-send-flight.py','apply-root-orbit.py','apply-reaction-clip-v17.py','apply-reasoning-v17.py',
    'apply-midstate-review.py','apply-late-state-review.py','apply-phonebook-grid-review.py',
})


manual['02'].update({
    'apply-root-header-birth.py','apply-root-header-birth-v2.py','apply-root-header-birth-v3.py',
    'apply-root-header-birth-v4.py','apply-uber-affine.py','preview-combined-v10.mjs','preview-end-v5.mjs',
    'preview-final-v10.mjs','preview-last-v10.mjs','preview-middle-v9.mjs','preview-ui-v5.mjs',
    'prepare-orbit-root.mjs','rebuild-refinements.py','rebuild-v11.py','final-midstate-fix/acquire_dense.py',
    'final-midstate-fix/audit_birth.py','final-midstate-fix/cache_nodes.py','final-midstate-fix/confirm_native.py',
    'final-midstate-fix/prepare-late-probes.mjs','final-midstate-fix/prepare-letter-base.mjs',
    'final-midstate-fix/prepare-probes.mjs','final-midstate-fix/verify-production-native-v16.py',
    'final-midstate-fix/verify-production-native.py','final-midstate-fix/label_exit_ink.py',
    'final-midstate-fix/measure_exit_label.py','final-midstate-fix/measure_label_clipping.py',
    'final-midstate-fix/refine_optics.py','final-midstate-fix/validate_late_native.py',
    'muse-continuation-v19/audit.py','muse-continuation-v19/measure-endpoints.py',
    'muse-continuation-v19/prepare-patch.py','muse-continuation-v19/prepare-base.mjs',
    'muse-attribution-v17/apply.py','muse-attribution-v17/prepare.py','muse-attribution-v17/prove.py',
    'muse-attribution-v17/gate.py',
})


manual['02'].update({
    'refine-middle.py','trace_glyphs.py','trace_glyphs_before_scalar_cleanup.py',
    'refine-phonebook-native-unfold.py','refine-phonebook-native-unfold-single.py',
    'analyze-middle.py','refine-middle-runs.py','refine-middle-avatar-checkpoint.py',
    'phonebook-v14/archive_superseded.py','phonebook-v14/audit_logo_cameras.py',
    'phonebook-v14/compare_native.py','phonebook-v14/finalize_release.py',
    'phonebook-v14/fix_query_precision.py','phonebook-v14/prepare_templates.py',
    'phonebook-v14/probe_caps_affine.py','phonebook-v14/verify_refinement.py',
})


manual['02'].update({
    'orbit-identity-v17/check-prototype.py','orbit-identity-v17/extend-green.py',
    'orbit-identity-v17/final-gate.py','orbit-identity-v17/fit_green.py','orbit-identity-v17/measure-green.py',
    'orbit-identity-v17/measure.py','orbit-identity-v17/prepare-patch.py','orbit-identity-v17/prove-scope.py',
    'orbit-identity-v17/prepare-base.mjs','orbit-identity-v17/apply.py','muse-attribution-v17/contour-dense.py',
    'muse-attribution-v17/contour.py','muse-attribution-v17/post-attribution.py','muse-attribution-v17/sift.py',
    'v17-refinement/acquire_g17_peaks.py','v17-refinement/acquire_g19_peaks.py',
    'v17-refinement/archive_neutral_prototypes.py','v17-refinement/repair_archives.py',
    'v17-refinement/run_reasoning_dense.py','v17-refinement/verify_g17_native_reasoning.py',
    'v17-refinement/build_reaction_clip.py','v17-refinement/extract_reasoning_art.py',
    'v17-refinement/finalize_reasoning.py','v17-refinement/measure_color_clusters.py',
    'v17-refinement/validate_reaction.py','v17-refinement/validate_reasoning.py',
    'v17-refinement/prepare_reaction_probe.mjs','v17-refinement/prepare_reasoning_probe.mjs',
    'v17-refinement/cache_components.py','v17-refinement/release_reasoning.py','v17-refinement/simplify_neutral.py',
    'archive_requested_private.py','v17-refinement/build_reasoning_neutral.py',
    'v17-refinement/fit_reasoning_emoji.py','v17-refinement/compose_reasoning_emoji.py',
})


manual['02'].update({
    'refine-composer-material-root.py','refine-composer-material-root-gray.py','refine-copy-root.py','refine-send-flight-root.py',
    'phonebook-v14/build_dense.py','phonebook-v14/build_probe486.py','phonebook-v14/measure_dense.py','phonebook-v14/fit_field.py',
    'phonebook-v14/diagnose_field.py','phonebook-v14/refine_native.py','inspect-v14-midgate.py','merge-phonebook-review.py',
    'refine-query-camera-root.py','refine-query-fade-root.py','build-v11-end.py','refine-v11-card-edge.py',
    'refine-v11-card-textures.py','refine-flight-checkpoint.py','refine-reasoning-checkpoint.py','build-header-formation-prototype.py',
    'refine-header-formation-muse.py','measure-orbit-root.py','build-phonebook-birth.py','refine-phonebook-glyphs.py',
    'refine-endcards.py','apply-capsule-collapse-review.py','build-capsule-collapse-review.py','build-intro797-review.py',
    'extend-intro797-review.py','refine-intro797-sharp-words.py',
})


manual['02'].update({
    'apply-phonebook-review.py','build-v11-boundary.py','final-midstate-fix/build_late_birth.py',
    'final-midstate-fix/build_spec.py','final-midstate-fix/build_typing.py','final-midstate-fix/extend_late_label.py',
    'final-midstate-fix/measure_lifecycles.py','final-midstate-fix/preserve_g16_peak_batch.py','measure-root-house-v17.py',
    'patch-ui-v5.py','refine-early-end.py','refine-header-birth-root-v2.py','refine-header-birth-root-v3.py',
    'refine-header-birth-root-v4.py','refine-header-birth-root.py','refine-middle-final-checkpoint.py',
    'refine-phone-checkpoint.py','refine-phonebook.py','refine-v11-middle-checkpoint.py',
})
assert len(manual['02']) == 200


def js_syntax(entry):
    if entry['ext'] not in ('.mjs','.js'):
        return (entry['asset'],entry['parser'])
    result=subprocess.run(['node','--check',str(root/entry['asset'])],capture_output=True,text=True)
    if result.returncode:
        raise RuntimeError(f"{entry['asset']}: {result.stderr.splitlines()[-2:]}")
    return (entry['asset'],'Node syntax OK')

with out.open('w',encoding='utf-8',newline='') as stream:
    writer=csv.writer(stream,delimiter='\t',lineterminator='\n')
    writer.writerow(['snapshot','path_relative_to_codex_direction_library','sha256','bytes','lines','automated_coverage','manual_direct_lines','topics_indexed'])
    for pack in ('01-photonhq-complete-v1','02-danieltian-complete-v1'):
        scanned=json.loads((work/f'scan-{pack}.json').read_text())
        with ThreadPoolExecutor(max_workers=4) as pool:
            syntax=dict(pool.map(js_syntax,scanned))
        for entry in scanned:
            topic_keys=','.join(k for k, matches in entry['topics'].items() if matches)
            count=entry['recomputed_lines']
            ranges=f'1-{count}' if entry['refpath'] in manual[pack[:2]] else ''
            writer.writerow([commit,entry['asset'],entry['sha256'],entry['bytes'],count,syntax[entry['asset']],ranges,topic_keys])
        for name in json.loads((work/f'excluded-{pack}.json').read_text()):
            path=root/name
            with path.open('rb') as src:
                digest=hashlib.file_digest(src,'sha256').hexdigest()
            writer.writerow([commit,name,digest,path.stat().st_size,'','Excluded from text/code review','', 'binary/source' if path.suffix=='.mp4' else 'generated metadata or asset provenance'])
