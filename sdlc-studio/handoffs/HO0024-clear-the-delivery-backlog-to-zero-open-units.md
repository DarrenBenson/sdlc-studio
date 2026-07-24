# HO-0024: Clear the delivery backlog to zero open units: every remaining bug fixed and every remaining story delivered with executable acceptance criteria, so the v5 release cut that follows has no known-open work behind it

> **Date:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KY8M6Q (started 2026-07-23T23:26:21Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

28 of 28 unit(s) remain (23 suit copilot-assisted completion, 5 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 240 min, units 8 unit(s)
- **Spent:** 752.9 min, 0 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~6,040,798 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (28)

### BG0269 (bug, Open) - copilot-tail

- **file:** `tools/tests/test_skill_tests_env.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0269-the-scrub-site-sweep-s-worktrees-exclusion-matches.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### BG0270 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0270-the-goal-review-gate-refuses-a-plan-when.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0272 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_nondone_close.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0272-retro-accuracy-misattributes-a-run-s-rung-run.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0273 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/refine.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_refine.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0273-refine-resolve-story-affects-inherit-subset-bypasses-the.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0274 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_retitle_refs.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0274-artifact-retitle-write-phase-is-a-sequence-of.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0275 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/reviews/LATEST.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0275-a-successful-sprint-close-never-refreshes-sdlc-studio.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0276 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0276-conformance-reports-ungroomed-0-while-31-stories-carry.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0277 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0277-the-seat-brief-is-circular-goal-review-brief.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0354 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/gate.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0354-conformance-and-validate-gain-a-diff-scoped-mode.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0357 (story, Draft) - copilot-tail

- **file:** `tools/lint_corpus.py` - declared Affects
- **file:** `tools/tests/test_lint_corpus.py` - declared Affects
- **file:** `.github/workflows/lint.yml` - declared Affects
- **file:** `sdlc-studio/stories/US0357-a-periodic-or-pre-release-lane-lints-the.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0358 (story, Draft) - copilot-tail

- **file:** `tools/lint_corpus.py` - declared Affects
- **file:** `tools/tests/test_lint_corpus_attribution.py` - declared Affects
- **file:** `.github/workflows/lint.yml` - declared Affects
- **file:** `sdlc-studio/stories/US0358-the-report-distinguishes-a-pre-existing-failure-from.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0361 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/decisions.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lessons.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/ledger.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/handoff.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_prose_writer_hazard.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_artifact.py` - declared Affects
- **file:** `sdlc-studio/stories/US0361-a-shared-fields-file-and-stdin-helper-in.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0362 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0362-a-command-substitution-fingerprint-detector-with-a-recorded.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0363 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/reference-scripts.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/agent-instructions.md` - declared Affects
- **file:** `sdlc-studio/stories/US0363-document-the-safe-form-in-reference-scripts-md.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0372 (story, Draft) - copilot-tail

- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `.githooks/commit-msg` - declared Affects
- **file:** `tools/tests/test_message_first_gate.py` - declared Affects
- **file:** `tools/tests/test_precommit_lane_order.py` - declared Affects
- **file:** `tools/tests/test_commit_msg_hook.py` - declared Affects
- **file:** `sdlc-studio/stories/US0372-validate-the-commit-message-rules-ahead-of-the.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0374 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/reviews/critic-verdicts.md` - declared Affects
- **file:** `sdlc-studio/stories/US0374-critic-correct-supersedes-a-verdict-row-with-an.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0375 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `sdlc-studio/stories/US0375-the-sign-off-gate-ignores-a-superseded-row.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0377 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/status.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_inflight_guard.py` - declared Affects
- **file:** `sdlc-studio/stories/US0377-skill-entry-points-warn-or-refuse-while-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0382 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-scripts.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/best-practices/script.md` - declared Affects
- **file:** `sdlc-studio/stories/US0382-resolve-root-and-under-root-in-sdlc-md.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0383 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/next_id.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_next_id.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_root_census.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-scripts.md` - declared Affects
- **file:** `sdlc-studio/reviews/root-census.md` - declared Affects
- **file:** `sdlc-studio/stories/US0383-census-the-62-root-scripts-and-fix-or.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0384 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/help/mutation.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-scripts-verify.md` - declared Affects
- **file:** `sdlc-studio/stories/US0384-rewrite-help-mutation-md-and-reference-scripts-verify.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0385 (story, Draft) - copilot-tail

- **file:** `sdlc-studio/trd.md` - declared Affects
- **file:** `sdlc-studio/tsd.md` - declared Affects
- **file:** `sdlc-studio/stories/US0385-reconcile-trd-md-and-tsd-md-and-record.md` - declared Affects
- **file:** `sdlc-studio/stories/US0385-reconcile-trd-md-and-tsd-md-and-record.md` - the unit itself
- **Suitability:** copilot-tail (confidence low) - seeded by difficulty:low

### US0388 (story, Draft) - copilot-tail

- **file:** `tools/forward-port.sh` - declared Affects
- **file:** `tools/tests/test_forward_port.py` - declared Affects
- **file:** `AGENTS.md` - declared Affects
- **file:** `sdlc-studio/stories/US0388-a-forward-port-drift-check-exits-non-zero.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### US0389 (story, Draft) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/status.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_status.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0389-surface-the-drift-in-the-status-hint-and.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

### US0394 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/verify.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/stories/US0394-verify-ac-run-accepts-an-id-list-a.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### US0395 (story, Draft) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/verify.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/stories/US0395-the-scoped-report-merges-rather-than-replaces-shared.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

### BG0267 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/repair_plan.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0267-a-repair-plan-verdict-carrying-no-findings-hash.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:low

### BG0268 (bug, Open) - copilot-tail

- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0268-sprint-plan-leaves-a-stale-sprint-plan-json.md` - the unit itself
- **Suitability:** copilot-tail (confidence high) - seeded by difficulty:medium

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Generated at the run close (`handoff generate`) |
