# HO-0037: The ceremony costs less than the work it certifies and the open bug backlog reaches zero, so the discipline is cheap enough to keep running and nothing known-broken is carried into the next run

> **Date:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYNKDP (started 2026-07-29T00:16:41Z)
> **Outcome:** stopped
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

11 of 47 unit(s) remain (0 suit copilot-assisted completion, 11 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 262 min, 36 unit(s) terminal
- **Delivered:** 36 unit(s)
- **Token forecast:** ~7,841,694 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (36)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0385](../../sdlc-studio/bugs/BG0385-five-units-of-run-01kymjem-ship-mechanisms-with.md) | bug | Fixed | 5/5 AC(s) verified |
| [BG0386](../../sdlc-studio/bugs/BG0386-caller-check-unit-is-single-valued-so-a.md) | bug | Fixed | 4/4 AC(s) verified |
| [BG0387](../../sdlc-studio/bugs/BG0387-judge-defects-against-goal-is-blind-to-this.md) | bug | Fixed | 6/6 AC(s) verified |
| [BG0388](../../sdlc-studio/bugs/BG0388-the-seam-owner-check-matches-by-naive-substring.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0392](../../sdlc-studio/bugs/BG0392-open-run-destroys-the-plan-side-content-review.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0397](../../sdlc-studio/bugs/BG0397-index-derived-issues-never-consults-the-new-field.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0399](../../sdlc-studio/bugs/BG0399-file-finding-discards-a-cr-s-steps-and.md) | bug | Fixed | 5/5 AC(s) verified |
| [BG0307](../../sdlc-studio/bugs/BG0307-retired-review-generate-still-shipped-as-live-surface.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0308](../../sdlc-studio/bugs/BG0308-tsd-calls-the-shipped-forecast-currently-falsified-citing.md) | bug | Fixed | 1/1 AC(s) verified |
| [BG0309](../../sdlc-studio/bugs/BG0309-trd-and-tsd-both-claim-the-suite-runs.md) | bug | Fixed | 1/1 AC(s) verified |
| [BG0310](../../sdlc-studio/bugs/BG0310-trd-and-tsd-declare-version-4-1-0.md) | bug | Fixed | 4/4 AC(s) verified |
| [BG0311](../../sdlc-studio/bugs/BG0311-close-owed-push-release-guard-is-enforced-at.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0320](../../sdlc-studio/bugs/BG0320-rfc0052-marked-superseded-with-no-superseder-named-decision.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0347](../../sdlc-studio/bugs/BG0347-31-terminal-artefacts-carry-an-unfilled-body-scaffold.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0354](../../sdlc-studio/bugs/BG0354-three-more-places-still-enumerate-the-v2-four.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0357](../../sdlc-studio/bugs/BG0357-mutation-py-records-no-per-test-attribution-so.md) | bug | Fixed | 5/5 AC(s) verified |
| [BG0359](../../sdlc-studio/bugs/BG0359-nothing-keeps-the-rfc-index-s-spawned-work.md) | bug | Fixed | 5/5 AC(s) verified |
| [BG0363](../../sdlc-studio/bugs/BG0363-gate-py-records-a-cost-baseline-on-every.md) | bug | Fixed | 4/4 AC(s) verified |
| [BG0364](../../sdlc-studio/bugs/BG0364-two-more-modules-hand-roll-the-strict-timestamp.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0367](../../sdlc-studio/bugs/BG0367-the-ac-less-baseline-is-not-one-way.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0369](../../sdlc-studio/bugs/BG0369-the-conformance-waiver-report-is-blanked-when-the.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0389](../../sdlc-studio/bugs/BG0389-preserves-is-honoured-anywhere-in-a-unit-s.md) | bug | Fixed | 1/1 AC(s) verified |
| [BG0390](../../sdlc-studio/bugs/BG0390-the-seam-map-misses-a-shared-file-written.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0391](../../sdlc-studio/bugs/BG0391-the-lane-brief-s-seam-map-is-scoped.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0393](../../sdlc-studio/bugs/BG0393-goal-panel-returns-a-verdict-when-no-seat.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0394](../../sdlc-studio/bugs/BG0394-blocker-grouping-merges-different-causes-and-files-a.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0395](../../sdlc-studio/bugs/BG0395-the-in-flight-lane-warning-fires-only-for.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0396](../../sdlc-studio/bugs/BG0396-cmd-seams-silently-drops-unresolvable-ids-and-re.md) | bug | Fixed | 1/1 AC(s) verified |
| [BG0398](../../sdlc-studio/bugs/BG0398-listing-only-paths-never-checks-that-the-declared.md) | bug | Fixed | 4/4 AC(s) verified |
| [BG0332](../../sdlc-studio/bugs/BG0332-test-scope-pinned-to-a-58-script-inventory.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0333](../../sdlc-studio/bugs/BG0333-product-seat-calibrates-against-an-end-goal-maya.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0368](../../sdlc-studio/bugs/BG0368-init-s-derived-artefact-tree-creates-a-type.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0371](../../sdlc-studio/bugs/BG0371-the-repeated-lesson-report-rests-on-a-single.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0372](../../sdlc-studio/bugs/BG0372-the-overhead-ratio-never-reaches-the-velocity-record.md) | bug | Fixed | 4/4 AC(s) verified |
| [BG0373](../../sdlc-studio/bugs/BG0373-the-review-currency-carve-out-repaired-in-bg0336.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0374](../../sdlc-studio/bugs/BG0374-the-markdownlint-path-fixed-in-bg0341-still-cannot.md) | bug | Fixed | 3/3 AC(s) verified |

## Remaining (11)

### US0479 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/arguments.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/gate.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-scripts-verify.md` - declared Affects
- **file:** `tools/tests/test_dead_flag_docs.py` - declared Affects
- **file:** `CHANGELOG.md` - declared Affects
- **file:** `sdlc-studio/stories/US0479-delete-gate-s-dead-verify-batch-flag-and.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0531 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/reconcile.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_reconcile.py` - declared Affects
- **file:** `sdlc-studio/stories/US0531-the-sweep-detectors-read-the-artefact-corpus-once.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0532 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/reconcile.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_reconcile.py` - declared Affects
- **file:** `sdlc-studio/stories/US0532-the-corpus-read-is-measured-by-a-test.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0533 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0533-the-gate-attributes-its-seconds-per-lane-so.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0553 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `sdlc-studio/stories/US0553-a-close-phase-commit-over-an-unchanged-test.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0554 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_root_census.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0554-a-listing-only-declaration-names-the-ids-its.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0555 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0555-sprint-close-dry-run-reports-every-unmet-prerequisite.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0556 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0556-critic-evidence-record-and-signoff-each-record-a.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0557 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0557-a-batch-invocation-missing-a-required-argument-is.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0558 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/reviews/retro.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_retro.py` - declared Affects
- **file:** `sdlc-studio/stories/US0558-a-retro-created-by-the-scaffold-and-filled.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0559 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0559-the-close-reports-its-own-cost-gate-seconds.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Generated at the run close (`handoff generate`) |
