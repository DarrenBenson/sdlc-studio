# HO-0021: Every story's acceptance criteria would fail if the behaviour were absent, every bug states what makes its fix complete and tested, and any declared dependency records a logical constraint the file census cannot already derive

> **Date:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KY5EJX (started 2026-07-22T17:41:50Z)
> **Outcome:** stopped
> **Goal:** design
> **Batch source:** run-state.json

## Where to pick up

38 of 38 unit(s) remain (27 suit copilot-assisted completion, 11 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 300 min, units 38 unit(s)
- **Spent:** 137.9 min, 0 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~2,700,000 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (38)

### BG0257 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/reviews/retro.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_retro.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0257-a-retro-s-batch-field-accepts-an-id.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0261 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/doc_freshness.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0261-the-state-anchor-and-the-goal-verdict-both.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0256 (bug, Open) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_conformance.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0256-a-done-story-read-verified-yes-for-two.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### BG0258 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0258-the-docs-checker-s-escape-enumeration-has-been.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### BG0259 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0259-the-window-message-s-reason-clause-is-a.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0260 (bug, Open) - judgement

- **issue:** `unmet-deps: US0315:Draft` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0260-round-10-s-three-findings-carried-forward-with.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps

### US0311 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/plan_review.py` - declared Affects
- **file:** `sdlc-studio/stories/US0311-a-reject-verdict-produces-a-written-repair-plan.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0312 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/plan_review.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/reviewer-brief.md` - declared Affects
- **file:** `sdlc-studio/stories/US0312-the-repair-plan-is-attacked-by-an-independent.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0313 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/plan_review.py` - declared Affects
- **file:** `sdlc-studio/stories/US0313-a-repair-plan-verdict-is-pinned-to-the.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0314 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/stories/US0314-a-repair-commit-records-which-plan-it-executed.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0315 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/plan_review.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-config.md` - declared Affects
- **file:** `sdlc-studio/stories/US0315-the-repair-plan-gate-is-opt-in-per.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0316 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/best-practices/script.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/best-practices/documentation.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py` - declared Affects
- **file:** `sdlc-studio/stories/US0316-the-best-practice-guide-states-the-derivation-rule.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:medium

### US0317 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/best-practices/testing.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py` - declared Affects
- **file:** `sdlc-studio/stories/US0317-where-a-message-and-a-verdict-must-agree.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0318 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/stories/US0318-the-shipped-reviewer-brief-carries-per-item-repair.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0319 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0319-a-repair-review-is-briefed-with-the-previous.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0320 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/stories/US0320-the-reviewer-brief-directs-a-first-pass-enumerating.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0321 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `sdlc-studio/stories/US0321-a-claim-that-cannot-be-checked-mechanically-is.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0322 (story, Draft) - judgement

- **issue:** `unmet-deps: US0320:Draft` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/review_prep.py` - declared Affects
- **file:** `sdlc-studio/stories/US0322-the-claim-pass-runs-before-the-logic-review.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:unmet-deps

### US0323 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/refine.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py` - declared Affects
- **file:** `sdlc-studio/stories/US0323-one-shared-resolvable-affects-predicate-serves-file-finding.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0324 (story, Draft) - judgement

- **issue:** `unmet-deps: US0323:Draft` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/refine.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_refine.py` - declared Affects
- **file:** `sdlc-studio/stories/US0324-artifact-new-and-refine-apply-refuse-an-unresolvable.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps

### US0325 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py` - declared Affects
- **file:** `sdlc-studio/stories/US0325-the-refusal-names-the-closest-unique-basename-match.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0326 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `sdlc-studio/stories/US0326-sprint-plan-write-refuses-a-disjoint-batch-against.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0327 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `sdlc-studio/stories/US0327-the-refusal-names-the-open-run-s-id.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0328 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `sdlc-studio/stories/US0328-a-run-whose-only-close-artefact-is-a.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0329 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/help/sprint.md` - declared Affects
- **file:** `sdlc-studio/stories/US0329-help-sprint-md-states-the-single-run-slot.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0330 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/changelog.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_changelog.py` - declared Affects
- **file:** `sdlc-studio/stories/US0330-a-structural-check-fails-on-subsection-headings-out.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0331 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0331-the-structural-check-joins-the-gate-lane-that.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0332 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-config.md` - declared Affects
- **file:** `sdlc-studio/stories/US0332-a-project-declares-a-review-policy-block-on.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0333 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `sdlc-studio/stories/US0333-under-carry-forward-every-finding-is-filed-or.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0334 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0334-the-close-records-which-policy-was-in-force.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0335 (story, Draft) - judgement

- **issue:** `unmet-deps: US0332:Draft` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `sdlc-studio/stories/US0335-a-carried-forward-finding-is-linked-to-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps

### US0336 (story, Draft) - copilot-tail

- **ac:** `AC1` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheForecastCarriesAFixedTermTests::test_the_total_is_a_fixed_term_plus_points_times_the_marginal_rate (pytest)
- **ac:** `AC2` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheForecastCarriesAFixedTermTests::test_the_rendered_forecast_shows_both_terms_and_not_one_product (pytest)
- **ac:** `AC3` - pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheForecastCarriesAFixedTermTests::test_a_half_size_batch_costs_more_than_half_and_more_per_point (pytest)
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0336-the-forecast-carries-an-explicit-fixed-per-sprint.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0337 (story, Draft) - judgement

- **issue:** `unmet-deps: BG0257:Open` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_retro.py` - declared Affects
- **file:** `sdlc-studio/stories/US0337-the-fixed-term-is-measured-from-the-project.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps

### US0338 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0338-a-fit-is-never-applied-automatically-the-plan.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0339 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/reference-sprint.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0339-the-shipped-seed-s-basis-text-states-the.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0340 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/templates/audit-profiles/process.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/audit.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py` - declared Affects
- **file:** `sdlc-studio/stories/US0340-a-process-audit-lens-pack-ships-alongside-test.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0341 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/templates/audit-profiles/process.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-audit.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/audit.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py` - declared Affects
- **file:** `sdlc-studio/stories/US0341-each-lens-names-its-mechanically-detectable-signature-and.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0342 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/templates/audit-profiles/process.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-audit.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py` - declared Affects
- **file:** `sdlc-studio/stories/US0342-every-lens-cites-the-incident-it-derives-from.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Generated at the run close (`handoff generate`) |
