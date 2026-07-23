# HO-0022: All 43 units reach Review with every acceptance criterion proven by a test that fails without the code it guards, and every guard this batch ships is ENABLED in this project's own config - so nothing here can be delivered inert

> **Date:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KY5Y3W (started 2026-07-22T22:19:16Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

34 of 43 unit(s) remain (0 suit copilot-assisted completion, 34 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 600 min, units 43 unit(s)
- **Spent:** 699.4 min, 9 unit(s) terminal
- **Delivered:** 9 unit(s)
- **Token forecast:** ~3,000,000 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (9)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0257](../../sdlc-studio/bugs/BG0257-a-retro-s-batch-field-accepts-an-id.md) | bug | Fixed | no verifier or verdict on record |
| [BG0261](../../sdlc-studio/bugs/BG0261-the-state-anchor-and-the-goal-verdict-both.md) | bug | Fixed | no verifier or verdict on record |
| [BG0262](../../sdlc-studio/bugs/BG0262-a-seat-that-says-the-goal-is-not.md) | bug | Fixed | no verifier or verdict on record |
| [BG0265](../../sdlc-studio/bugs/BG0265-a-second-verify-line-under-one-acceptance-criterion.md) | bug | Fixed | no verifier or verdict on record |
| [BG0256](../../sdlc-studio/bugs/BG0256-a-done-story-read-verified-yes-for-two.md) | bug | Fixed | no verifier or verdict on record |
| [BG0258](../../sdlc-studio/bugs/BG0258-the-docs-checker-s-escape-enumeration-has-been.md) | bug | Fixed | no verifier or verdict on record |
| [BG0259](../../sdlc-studio/bugs/BG0259-the-window-message-s-reason-clause-is-a.md) | bug | Fixed | no verifier or verdict on record |
| [BG0263](../../sdlc-studio/bugs/BG0263-the-goal-review-has-no-rounds-so-rewriting.md) | bug | Fixed | no verifier or verdict on record |
| [BG0260](../../sdlc-studio/bugs/BG0260-round-10-s-three-findings-carried-forward-with.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (34)

### US0311 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/repair_plan.py` - declared Affects
- **file:** `sdlc-studio/stories/US0311-a-reject-verdict-produces-a-written-repair-plan.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0312 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/repair_plan.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/reviewer-brief.md` - declared Affects
- **file:** `sdlc-studio/stories/US0312-the-repair-plan-is-attacked-by-an-independent.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0313 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/repair_plan.py` - declared Affects
- **file:** `sdlc-studio/stories/US0313-a-repair-plan-verdict-is-pinned-to-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0314 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/stories/US0314-a-repair-commit-records-which-plan-it-executed.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0315 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/repair_plan.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-config.md` - declared Affects
- **file:** `sdlc-studio/stories/US0315-the-repair-plan-gate-is-opt-in-per.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0316 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/best-practices/script.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/best-practices/documentation.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py` - declared Affects
- **file:** `sdlc-studio/stories/US0316-the-best-practice-guide-states-the-derivation-rule.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0317 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/best-practices/testing.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py` - declared Affects
- **file:** `sdlc-studio/stories/US0317-where-a-message-and-a-verdict-must-agree.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0318 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/stories/US0318-the-shipped-reviewer-brief-carries-per-item-repair.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

### US0319 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0319-a-repair-review-is-briefed-with-the-previous.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0320 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/stories/US0320-the-reviewer-brief-directs-a-first-pass-enumerating.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

### US0321 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0321-a-claim-that-cannot-be-checked-mechanically-is.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0322 (story, Review) - judgement

- **issue:** `unmet-deps: US0320:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/review_prep.py` - declared Affects
- **file:** `sdlc-studio/stories/US0322-the-claim-pass-runs-before-the-logic-review.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:unmet-deps, issue:already-satisfied

### US0323 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/refine.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py` - declared Affects
- **file:** `sdlc-studio/stories/US0323-one-shared-resolvable-affects-predicate-serves-file-finding.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0324 (story, Review) - judgement

- **issue:** `unmet-deps: US0323:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/refine.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_refine.py` - declared Affects
- **file:** `sdlc-studio/stories/US0324-artifact-new-and-refine-apply-refuse-an-unresolvable.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps, issue:already-satisfied

### US0325 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py` - declared Affects
- **file:** `sdlc-studio/stories/US0325-the-refusal-names-the-closest-unique-basename-match.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0326 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `sdlc-studio/stories/US0326-sprint-plan-write-refuses-a-disjoint-batch-against.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0327 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `sdlc-studio/stories/US0327-the-refusal-names-the-open-run-s-id.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0328 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `sdlc-studio/stories/US0328-a-run-whose-only-close-artefact-is-a.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0329 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/help/sprint.md` - declared Affects
- **file:** `sdlc-studio/stories/US0329-help-sprint-md-states-the-single-run-slot.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

### US0330 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/changelog.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_changelog.py` - declared Affects
- **file:** `sdlc-studio/stories/US0330-a-structural-check-fails-on-subsection-headings-out.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0331 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0331-the-structural-check-joins-the-gate-lane-that.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0332 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-config.md` - declared Affects
- **file:** `sdlc-studio/stories/US0332-a-project-declares-a-review-policy-block-on.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0333 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `sdlc-studio/stories/US0333-under-carry-forward-every-finding-is-filed-or.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0334 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0334-the-close-records-which-policy-was-in-force.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0335 (story, Review) - judgement

- **issue:** `unmet-deps: US0332:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `sdlc-studio/stories/US0335-a-carried-forward-finding-is-linked-to-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps, issue:already-satisfied

### US0336 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0336-the-forecast-carries-an-explicit-fixed-per-sprint.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0337 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_retro.py` - declared Affects
- **file:** `sdlc-studio/stories/US0337-the-fixed-term-is-measured-from-the-project.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0338 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0338-a-fit-is-never-applied-automatically-the-plan.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0339 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/reference-sprint.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0339-the-shipped-seed-s-basis-text-states-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0340 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/templates/audit-profiles/process.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/audit.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py` - declared Affects
- **file:** `sdlc-studio/stories/US0340-a-process-audit-lens-pack-ships-alongside-test.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0341 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/templates/audit-profiles/process.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-audit.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/audit.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py` - declared Affects
- **file:** `sdlc-studio/stories/US0341-each-lens-names-its-mechanically-detectable-signature-and.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0342 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/templates/audit-profiles/process.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-audit.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py` - declared Affects
- **file:** `sdlc-studio/stories/US0342-every-lens-cites-the-incident-it-derives-from.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0343 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/repair_plan.py` - declared Affects
- **file:** `sdlc-studio/stories/US0343-a-repair-answering-a-finding-in-the-same.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0344 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/stories/US0344-the-reviewer-brief-asks-whether-the-approach-itself.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Generated at the run close (`handoff generate`) |
