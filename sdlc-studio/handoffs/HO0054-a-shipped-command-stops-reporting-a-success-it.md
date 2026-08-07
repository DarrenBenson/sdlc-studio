# HO-0054: A shipped command stops reporting a success it did not achieve, the bug backlog becomes visible to the tooling that is supposed to execute it, and v5.0.0 is cut on that basis

> **Date:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZCAJX (started 2026-08-06T19:54:48Z)
> **Outcome:** stopped
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

9 of 12 unit(s) remain (0 suit copilot-assisted completion, 9 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 750.1 min, 3 unit(s) terminal
- **Delivered:** 3 unit(s)
- **Token forecast:** ~4,197,908 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (3)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0530](../../sdlc-studio/bugs/BG0530-verify-ac-reports-a-unit-whose-criteria-it.md) | bug | Fixed | 7/7 AC(s) verified; critic APPROVE (engineering; delivery review subagent; round 1) |
| [BG0533](../../sdlc-studio/bugs/BG0533-the-mutation-engine-enumerates-a-mutant-at-one.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (engineering; final independent pass; RUN-01KZCAJX) |
| [BG0524](../../sdlc-studio/bugs/BG0524-warning-ratchet-reports-a-stale-baseline-as-clean.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (engineering; final independent pass; RUN-01KZCAJX) |

## Remaining (9)

### US0591 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0591-every-checklist-item-declares-its-enforcing-command-and.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0592 (story, Review) - judgement

- **issue:** `unmet-deps: US0595:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/decisions.md` - declared Affects
- **file:** `sdlc-studio/stories/US0592-the-goal-seat-review-is-enforced-by-sprint.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps, issue:already-satisfied

### US0593 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0593-a-run-whose-only-review-verdicts-are-reject.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0594 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0594-a-unit-whose-ticked-criteria-the-tree-contradicts.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0595 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/decisions.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_decisions.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0595-a-waiver-records-whether-it-was-deliberate-or.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0596 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0596-coverage-is-computed-once-and-two-rows-disagreeing.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0635 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/stories` - declared Affects
- **file:** `sdlc-studio/.verify-lint-baseline.json` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/stories/US0635-the-thirteen-story-side-duplicate-verify-groups-are.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0636 (story, Review) - judgement

- **issue:** `unmet-deps: US0635:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/bugs` - declared Affects
- **file:** `sdlc-studio/.verify-lint-baseline.json` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `sdlc-studio/stories/US0636-the-seven-bug-side-duplicate-verify-groups-are.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps, issue:already-satisfied

### CR0535 (cr, In Progress) - judgement

- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/file_finding.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-scripts.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/help/` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_file_finding.py` - declared Affects
- **file:** `sdlc-studio/change-requests/CR0535-a-refusing-verb-cannot-state-its-contract-until.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Generated at the run close (`handoff generate`) |
