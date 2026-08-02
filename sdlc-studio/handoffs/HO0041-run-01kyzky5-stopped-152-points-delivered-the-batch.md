# HO-0041: RUN-01KYZKY5 stopped - 152 points delivered, the batch did not pass review

> **Date:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYZKY5 (started 2026-08-01T21:31:48Z)
> **Outcome:** stopped
> **Batch source:** run-state.json

## Where to pick up

19 of 44 unit(s) remain (0 suit copilot-assisted completion, 19 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 945.3 min, 25 unit(s) terminal
- **Delivered:** 25 unit(s)
- **Token forecast:** ~8,158,984 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (25)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0438](../../sdlc-studio/bugs/BG0438-audit-run-provenance-is-not-durable-the-register.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0423](../../sdlc-studio/bugs/BG0423-the-commit-gate-s-unit-suite-lane-fails.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0432](../../sdlc-studio/bugs/BG0432-test-selection-still-misses-eleven-scripts-whose-tests.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0433](../../sdlc-studio/bugs/BG0433-the-duplicate-verifier-ratchet-is-not-enforced-as.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0435](../../sdlc-studio/bugs/BG0435-the-loading-guide-path-checker-skips-a-whole.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0436](../../sdlc-studio/bugs/BG0436-resolve-affects-never-resolves-against-the-installed-skill.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0448](../../sdlc-studio/bugs/BG0448-eight-bugs-stand-at-the-terminal-status-fixed.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0462](../../sdlc-studio/bugs/BG0462-the-version-guard-s-discovery-test-cannot-tell.md) | bug | Fixed | 1/1 AC(s) verified |
| [BG0470](../../sdlc-studio/bugs/BG0470-the-recorded-sprint-base-ref-is-two-weeks.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0476](../../sdlc-studio/bugs/BG0476-a-test-module-importing-a-sibling-fixture-is.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0478](../../sdlc-studio/bugs/BG0478-artifact-py-new-mints-a-cr-the-commit.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0431](../../sdlc-studio/bugs/BG0431-one-unresolvable-namespace-escape-demotes-every-flag-in.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0434](../../sdlc-studio/bugs/BG0434-two-of-the-four-signature-detector-shapes-are.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0437](../../sdlc-studio/bugs/BG0437-filing-run-resolves-a-two-id-provenance-line.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0475](../../sdlc-studio/bugs/BG0475-decisions-py-writes-a-multi-paragraph-rationale-straight.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0483](../../sdlc-studio/bugs/BG0483-claim-drift-reads-append-only-ledgers-as-prose.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0359](../../sdlc-studio/bugs/BG0359-nothing-keeps-the-rfc-index-s-spawned-work.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0420](../../sdlc-studio/bugs/BG0420-test-fixtures-mirror-real-lists-by-hand-so.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0474](../../sdlc-studio/bugs/BG0474-an-artefact-documenting-the-shell-mangling-hazard-is.md) | bug | Fixed | 3/3 AC(s) verified |
| [US0602](../../sdlc-studio/stories/US0602-a-panel-signed-unit-is-distinguishable-from-an.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (engineering-seat-ep0198) |
| [BG0401](../../sdlc-studio/bugs/BG0401-four-of-this-sprint-s-repairs-can-be.md) | bug | Fixed | 4/4 AC(s) verified |
| [US0605](../../sdlc-studio/stories/US0605-verify-ac-lane-check-reports-criteria-whose-verifiers.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (qa-seat-ep0199) |
| [US0610](../../sdlc-studio/stories/US0610-tools-run-suite-sh-runs-a-suite-and.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (engineering-seat-ep0201) |
| [US0614](../../sdlc-studio/stories/US0614-a-points-census-answers-how-much-is-left.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (engineering-seat-ep0201) |
| [BG0487](../../sdlc-studio/bugs/BG0487-lane-check-misses-lane-entry-made-through-a.md) | bug | Fixed | 3/3 AC(s) verified |

## Remaining (19)

### US0607 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/best-practices/testing.md` - declared Affects
- **file:** `tools/best_practice_rules.py` - declared Affects
- **file:** `tools/tests/test_best_practice_rules.py` - declared Affects
- **file:** `sdlc-studio/stories/US0607-best-practices-testing-md-states-the-entry-point.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0466 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/refine.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/SKILL.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/doc_coverage.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_refine.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py` - declared Affects
- **file:** `sdlc-studio/stories/US0466-the-ungroomed-ac-marker-routes-to-the-shape.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0470 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py` - declared Affects
- **file:** `changelog.d/US0470.md` - declared Affects
- **file:** `sdlc-studio/stories/US0470-sprint-batch-swap-trades-units-in-one-recorded.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0471 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/sprint.md` - declared Affects
- **file:** `changelog.d/US0471.md` - declared Affects
- **file:** `sdlc-studio/stories/US0471-sprint-batch-add-epic-adds-an-epic-s.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0472 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_appetite_resize.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/sprint.md` - declared Affects
- **file:** `changelog.d/US0472.md` - declared Affects
- **file:** `sdlc-studio/stories/US0472-the-appetite-can-be-resized-on-an-open.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0473 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/help/sprint.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-sprint.md` - declared Affects
- **file:** `tools/check_budgets.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_help_structure.py` - declared Affects
- **file:** `tools/tests/test_check_budgets.py` - declared Affects
- **file:** `changelog.d/US0473.md` - declared Affects
- **file:** `sdlc-studio/stories/US0473-the-in-flight-sprint-controls-are-documented-as.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0601 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0601-review-signoff-is-operator-by-default-and-panel.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0606 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0606-the-lane-check-runs-in-the-gate-that.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0609 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0609-file-and-close-accepts-a-stale-periodic-review.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0611 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `tools/run-suite.sh` - declared Affects
- **file:** `.githooks/commit-msg` - declared Affects
- **file:** `tools/tests/test_run_suite.py` - declared Affects
- **file:** `sdlc-studio/stories/US0611-a-greenness-claim-whose-verdict-file-is-absent.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0615 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0615-sprint-review-batch-takes-its-findings-from-a.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0598 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/persona_resolve.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py` - declared Affects
- **file:** `sdlc-studio/stories/US0598-persona-resolve-panel-assigns-the-adversarial-seats-and.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0599 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0599-a-panel-may-sign-a-unit-only-when.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0600 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0600-the-review-repair-loop-declares-a-round-cap.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0603 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0603-a-unit-the-panel-rejects-twice-or-whose.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0604 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0604-the-close-actively-reports-to-the-operator-shipped.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0608 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0608-a-stale-repo-wide-unified-review-no-longer.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0612 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/reference-sprint-toolchain.md` - declared Affects
- **file:** `tools/runbook.py` - declared Affects
- **file:** `tools/tests/test_runbook.py` - declared Affects
- **file:** `sdlc-studio/stories/US0612-a-runbook-ordered-by-sprint-step-names-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0613 (story, Ready) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `tools/runbook.py` - declared Affects
- **file:** `tools/tests/test_runbook.py` - declared Affects
- **file:** `sdlc-studio/stories/US0613-sprint-plan-and-sprint-run-print-the-runbook.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Generated at the run close (`handoff generate`) |
