# HO-0025: Clear the delivery backlog to zero open units: every remaining bug fixed and every remaining story delivered with executable acceptance criteria, so the v5 release cut that follows has no known-open work behind it

> **Date:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KY8M6Q (started 2026-07-23T23:26:21Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** argument

## Where to pick up

10 of 28 unit(s) remain (10 suit copilot-assisted completion, 0 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 240 min, units 8 unit(s)
- **Spent:** 820.8 min, 18 unit(s) terminal
- **Delivered:** 18 unit(s)
- **Token forecast:** ~6,040,798 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (18)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [US0354](../../sdlc-studio/stories/US0354-conformance-and-validate-gain-a-diff-scoped-mode.md) | story | Done | 3/3 AC(s) verified |
| [US0357](../../sdlc-studio/stories/US0357-a-periodic-or-pre-release-lane-lints-the.md) | story | Done | 3/3 AC(s) verified |
| [US0358](../../sdlc-studio/stories/US0358-the-report-distinguishes-a-pre-existing-failure-from.md) | story | Done | 3/3 AC(s) verified |
| [US0361](../../sdlc-studio/stories/US0361-a-shared-fields-file-and-stdin-helper-in.md) | story | Done | 3/3 AC(s) verified |
| [US0362](../../sdlc-studio/stories/US0362-a-command-substitution-fingerprint-detector-with-a-recorded.md) | story | Done | 3/3 AC(s) verified |
| [US0363](../../sdlc-studio/stories/US0363-document-the-safe-form-in-reference-scripts-md.md) | story | Done | 0/2 AC(s) verified, 2 manual |
| [US0372](../../sdlc-studio/stories/US0372-validate-the-commit-message-rules-ahead-of-the.md) | story | Done | 3/3 AC(s) verified |
| [US0374](../../sdlc-studio/stories/US0374-critic-correct-supersedes-a-verdict-row-with-an.md) | story | Done | 3/3 AC(s) verified |
| [US0375](../../sdlc-studio/stories/US0375-the-sign-off-gate-ignores-a-superseded-row.md) | story | Done | 3/3 AC(s) verified |
| [US0377](../../sdlc-studio/stories/US0377-skill-entry-points-warn-or-refuse-while-the.md) | story | Done | 3/3 AC(s) verified |
| [US0382](../../sdlc-studio/stories/US0382-resolve-root-and-under-root-in-sdlc-md.md) | story | Done | 3/3 AC(s) verified |
| [US0383](../../sdlc-studio/stories/US0383-census-the-62-root-scripts-and-fix-or.md) | story | Done | 3/3 AC(s) verified |
| [US0384](../../sdlc-studio/stories/US0384-rewrite-help-mutation-md-and-reference-scripts-verify.md) | story | Done | 0/3 AC(s) verified, 3 manual |
| [US0385](../../sdlc-studio/stories/US0385-reconcile-trd-md-and-tsd-md-and-record.md) | story | Done | 0/2 AC(s) verified, 2 manual |
| [US0388](../../sdlc-studio/stories/US0388-a-forward-port-drift-check-exits-non-zero.md) | story | Done | 3/3 AC(s) verified |
| [US0389](../../sdlc-studio/stories/US0389-surface-the-drift-in-the-status-hint-and.md) | story | Done | 3/3 AC(s) verified |
| [US0394](../../sdlc-studio/stories/US0394-verify-ac-run-accepts-an-id-list-a.md) | story | Done | 3/3 AC(s) verified |
| [US0395](../../sdlc-studio/stories/US0395-the-scoped-report-merges-rather-than-replaces-shared.md) | story | Done | 3/3 AC(s) verified |

## Remaining (10)

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
