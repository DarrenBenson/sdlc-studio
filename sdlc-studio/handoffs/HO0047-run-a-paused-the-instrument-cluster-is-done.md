# HO-0047: Run A paused: the instrument cluster is done, the epic units are not

> **Date:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZ79C1 (started 2026-08-04T21:10:20Z)
> **Outcome:** running
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

11 of 15 unit(s) remain (7 suit copilot-assisted completion, 4 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 480 min, units 15 unit(s)
- **Spent:** 113.4 min, 4 unit(s) terminal
- **Delivered:** 4 unit(s)
- **Token forecast:** ~3,515,866 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (4)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0507](../../sdlc-studio/bugs/BG0507-the-suite-collapse-lane-sets-fail-1-after.md) | bug | Fixed | no verifier or verdict on record |
| [BG0513](../../sdlc-studio/bugs/BG0513-run-suite-sh-all-is-intermittently-red-the.md) | bug | Fixed | no verifier or verdict on record |
| [BG0514](../../sdlc-studio/bugs/BG0514-queue-show-is-blind-exactly-when-an-operator.md) | bug | Fixed | no verifier or verdict on record |
| [BG0518](../../sdlc-studio/bugs/BG0518-close-owed-detect-prints-a-sprint-close-is.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (11)

### BG0406 (bug, Open) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/reconcile.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_reconcile.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0406-three-units-delivered-nothing-bg0372-writes-no-velocity.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### BG0421 (bug, Open) - judgement

- **file:** `sdlc-studio/stories` - declared Affects
- **file:** `sdlc-studio/change-requests` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0421-twenty-one-open-questions-reached-a-terminal-status.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### BG0463 (bug, Open) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `tools/check_spec_claims.py` - declared Affects
- **file:** `tools/check_script_tests.py` - declared Affects
- **file:** `tools/tests/test_check_versions.py` - declared Affects
- **file:** `tools/tests/test_porting_doctrine.py` - declared Affects
- **file:** `sdlc-studio/tsd.md` - declared Affects
- **file:** `sdlc-studio/trd.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `tools/tests/test_check_spec_claims.py` - declared Affects
- **file:** `tools/tests/test_check_script_tests.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0463-twenty-non-blocking-findings-from-the-run-01kytka1.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### BG0500 (bug, Open) - copilot-tail

- **file:** `tools/runbook.py` - declared Affects
- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `tools/tests/test_runbook.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0500-the-runbook-guard-runs-in-no-gate-lane.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### BG0515 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0515-the-charter-queue-has-no-exit-nothing-sets.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0468 (story, Ready) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/help/sprint.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/arguments.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_help_structure.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/fixtures/sprint-help-pre-rewrite.md` - declared Affects
- **file:** `sdlc-studio/stories/US0468-help-sprint-md-documents-the-run-lifecycle-batch.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0480 (story, Ready) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `sdlc-studio/.validate-warning-baseline.json` - declared Affects
- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `tools/tests/test_precommit_lane_order.py` - declared Affects
- **file:** `tools/tests/test_precommit_warning_ratchet.py` - declared Affects
- **file:** `CHANGELOG.md` - declared Affects
- **file:** `sdlc-studio/stories/US0480-validate-ratchets-the-footprint-and-criterion-warnings-against.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0481 (story, Ready) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0481-sprint-plan-validates-the-units-in-its-batch.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0635 (story, Ready) - copilot-tail

- **file:** `sdlc-studio/stories` - declared Affects
- **file:** `sdlc-studio/.verify-lint-baseline.json` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/stories/US0635-the-thirteen-story-side-duplicate-verify-groups-are.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0636 (story, Ready) - copilot-tail

- **file:** `sdlc-studio/bugs` - declared Affects
- **file:** `sdlc-studio/.verify-lint-baseline.json` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/stories/US0636-the-seven-bug-side-duplicate-verify-groups-are.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0637 (story, Ready) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/stories/US0637-the-duplicate-groups-no-collection-can-answer-are.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Generated at the run close (`handoff generate`) |
