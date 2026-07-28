# HO-0034: A defect is caught by the lane that made it, the loop measures what it costs, and a lesson carried forward is read by the work that would repeat it

> **Date:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYKVZM (started 2026-07-28T08:01:09Z)
> **Outcome:** stopped
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

23 of 31 unit(s) remain (0 suit copilot-assisted completion, 23 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 290 min, 8 unit(s) terminal
- **Delivered:** 8 unit(s)
- **Token forecast:** ~6,862,776 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (8)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0351](../../sdlc-studio/bugs/BG0351-the-constitution-lane-is-81-of-the-per.md) | bug | Fixed | no verifier or verdict on record |
| [BG0313](../../sdlc-studio/bugs/BG0313-us0433-ac3-s-verifier-never-evaluates-the-done.md) | bug | Fixed | 1/1 AC(s) verified |
| [BG0319](../../sdlc-studio/bugs/BG0319-rfc-index-spawned-crs-column-is-false-for.md) | bug | Fixed | 0/2 AC(s) verified |
| [BG0331](../../sdlc-studio/bugs/BG0331-gate-py-s-reconcile-lane-enumerates-two-drift.md) | bug | Fixed | no verifier or verdict on record |
| [BG0336](../../sdlc-studio/bugs/BG0336-review-currency-close-bookkeeping-carve-out-is-direction.md) | bug | Fixed | no verifier or verdict on record |
| [BG0352](../../sdlc-studio/bugs/BG0352-pytest-cannot-collect-the-scripts-and-tools-suites.md) | bug | Fixed | 0/0 AC(s) verified |
| [BG0353](../../sdlc-studio/bugs/BG0353-telemetry-parse-iso-rejects-a-valid-iso-8601.md) | bug | Fixed | 1/1 AC(s) verified |
| [BG0341](../../sdlc-studio/bugs/BG0341-per-commit-markdownlint-lanes-cannot-see-tracked-github.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (23)

### US0508 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0508-a-lane-refuses-to-start-on-a-unit.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0509 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0509-a-lane-runs-its-unit-s-own-acceptance.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0510 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0510-a-lane-returns-the-proof-the-test-strategy.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0511 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/../reference-agent-prompt-template.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/../reference-sprint.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `tools/tests/test_doc_claims.py` - declared Affects
- **file:** `sdlc-studio/stories/US0511-the-lane-obligations-travel-with-the-dispatch-prompt.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0512 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/../templates/core/story.md` - declared Affects
- **file:** `tools/tests/test_doc_claims.py` - declared Affects
- **file:** `sdlc-studio/stories/US0512-a-unit-adding-a-mechanism-carries-an-acceptance.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0513 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_validate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0513-a-unit-whose-mechanism-has-no-caller-yet.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0514 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_validate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0514-a-bug-reaching-a-terminal-status-with-no.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0515 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_validate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0515-the-existing-ac-less-units-are-baselined-so.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0516 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_file_finding.py` - declared Affects
- **file:** `sdlc-studio/stories/US0516-a-filed-finding-carries-acceptance-criteria-derived-from.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0517 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_file_finding.py` - declared Affects
- **file:** `sdlc-studio/stories/US0517-a-finding-s-affects-names-where-the-fix.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0518 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_retro.py` - declared Affects
- **file:** `sdlc-studio/stories/US0518-the-retro-curates-a-fixed-size-set-of.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0519 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/lessons.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lessons.py` - declared Affects
- **file:** `sdlc-studio/stories/US0519-a-lesson-earns-a-place-only-by-displacing.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0520 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0520-the-sprint-reads-the-carried-lessons-at-plan.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0521 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lessons.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lessons.py` - declared Affects
- **file:** `sdlc-studio/stories/US0521-a-lesson-violated-again-after-being-carried-is.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0522 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/lessons.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lessons.py` - declared Affects
- **file:** `sdlc-studio/stories/US0522-a-repeatedly-violated-lesson-can-propose-a-change.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0523 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0523-the-close-reports-delivery-time-against-overhead-time.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0524 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0524-an-unmeasured-component-is-reported-as-unmeasured-rather.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0525 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_conformance.py` - declared Affects
- **file:** `sdlc-studio/stories/US0525-the-conformance-lane-reads-recorded-waivers-and-reports.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0526 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/decisions.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_decisions.py` - declared Affects
- **file:** `sdlc-studio/stories/US0526-a-waiver-naming-no-reason-or-an-unknown.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0527 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_validate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0527-validate-can-be-pointed-at-one-artefact-so.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0528 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_validate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0528-a-draft-story-declaring-a-file-it-will.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0529 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/init.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_init.py` - declared Affects
- **file:** `sdlc-studio/stories/US0529-init-creates-the-issues-directory-and-its-index.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0530 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/init.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_init.py` - declared Affects
- **file:** `sdlc-studio/stories/US0530-the-artefact-tree-init-creates-is-derived-from.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Generated at the run close (`handoff generate`) |
