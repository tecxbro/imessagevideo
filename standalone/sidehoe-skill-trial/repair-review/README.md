# Sidehoe repair baseline

The workflow let a full benchmark become the endpoint. Native timing matched
and RGB averages improved while failures stayed open. The scene also used shared
curves where the reference called for separately moving layers or true first
visibility. The original audit identifies each mismatch with a frame, source
evidence, scene property and targeted repair. [19-shot audit](../frame-audit/AUDIT.md)

The updated Recreation skill keeps a failing test for each item before work
begins. Each repair must clear that test in the decoded full candidate. It also
rechecks affected neighboring frames and shared layers. Treat the attached plan
as the starting criteria for this repair. Add specific numeric tolerances from
the source before tuning a property, and record how the criterion behaves on the
preserved benchmark. [General repair workflow](../../codex-trial/skill/imessage-motion-recreation/recreate/COMPLETION.md)

- [Repair plan](review-plan.json) covers the 24 shot spans and all 778 frames.
- [Baseline observations](baseline-visual-review.json) preserve the 19 failed
  shot checks and five previously accepted scoped checks. The RGB gates are
  diagnostic for this historical benchmark.
- [Baseline acceptance](baseline-acceptance.json) is a verified failure on the
  existing MP4. It lists all 19 shots still open.

From the workspace root, reproduce the baseline verdict with the existing
Python environment for the skill.

```sh
S=codex-trial/skill/imessage-motion-recreation/recreate
D=sidehoe-skill-trial/repair-review
python3 "$S/recreate.py" verify-review sidehoe-skill-trial/exports/sidehoe.mp4 \
  --plan "$D/review-plan.json" --review "$D/baseline-visual-review.json" \
  --comparison "$D/baseline-comparison/report.json" \
  --scoped --out /tmp/sidehoe-baseline-acceptance.json
```

Expect exit 1 and 5 of 24 passing scoped shot checks. The
[native-pixel review](native/README.md) uses the exact acceptance gate.
