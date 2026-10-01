# HO-0093: Maya signs, without a re-close, a report that checks VALID and names every operator ruling and carry

> **Date:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M3T8N1 (started 2026-09-30T23:00:50Z)
> **Outcome:** running
> **Goal:** done
> **Batch source:** argument

## Where to pick up

9 of 9 unit(s) remain (0 suit copilot-assisted completion, 9 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Unanswered stop-ship questions

None: every batch unit is delivered, abandoned, ruled, dropped, parked or awaiting only a signature. Rulings read from RETRO0128's `## Known issues carried` for RUN-01M3T8N1.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 485.7 min, 0 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~4,637,152 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (9)

### BG0826 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/templates/reviews/retro.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_retro_scaffold_run.py` - declared Affects
- **file:** `changelog.d/BG0826.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_retro.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0826-the-scaffolded-retro-carries-neither-the-run-id.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### BG0859 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `changelog.d/BG0859.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0859-the-close-s-status-preflight-stops-every-approved.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### BG0848 (bug, In Progress) - judgement

- **issue:** `unmet-deps: BG0859:In Progress` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py` - declared Affects
- **file:** `changelog.d/BG0848.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0848-sprint-sign-invalidates-its-own-report-when-it.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps, issue:already-satisfied

### BG0829 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_groomed.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `changelog.d/BG0829.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0829-a-unit-carried-at-the-review-cap-is.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### BG0850 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-review.md` - declared Affects
- **file:** `changelog.d/BG0850.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0850-a-carried-unit-s-discharge-approval-is-refused.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### BG0851 (bug, In Progress) - judgement

- **issue:** `unmet-deps: BG0848:In Progress` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_report_operator_interventions.py` - declared Affects
- **file:** `changelog.d/BG0851.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0851-the-sprint-report-says-the-operator-ruled-nothing.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps, issue:already-satisfied

### BG0849 (bug, In Progress) - judgement

- **issue:** `unmet-deps: BG0826:In Progress, BG0851:In Progress` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/retro.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_graduation_ruling.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/sprint.md` - declared Affects
- **file:** `changelog.d/BG0849.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0849-a-close-dry-run-mints-a-different-graduation.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps, issue:already-satisfied

### BG0862 (bug, In Progress) - judgement

- **issue:** `unmet-deps: BG0826:In Progress, BG0829:In Progress, BG0848:In Progress, BG0849:In Progress, BG0850:In Progress, BG0851:In Progress, BG0859:In Progress, BG0865:In Progress` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_signed_run_end_to_end.py` - declared Affects
- **file:** `changelog.d/BG0862.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0862-nothing-runs-the-unstubbed-close-sign-and-check.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:unmet-deps, issue:already-satisfied

### BG0865 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issue_rulings.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `changelog.d/BG0865.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0865-the-signed-page-names-a-known-issue-s.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Generated at the run close (`handoff generate`) |
