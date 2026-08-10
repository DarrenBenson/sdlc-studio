# HO-0057: A user who has never run SDLC Studio, and a user upgrading a v4 project, both reach a planned sprint and a green gate without editing config or reading source

> **Date:** 2026-08-10
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZM49Y (started 2026-08-09T20:45:59Z)
> **Outcome:** goal-reached
> **Batch source:** run-state.json

## Where to pick up

5 of 8 unit(s) remain (0 suit copilot-assisted completion, 5 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 960 min, units 8 unit(s)
- **Spent:** 1056.3 min, 3 unit(s) terminal
- **Delivered:** 3 unit(s)
- **Token forecast:** ~2,065,412 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (3)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0558](../../sdlc-studio/bugs/BG0558-a-greenfield-project-cannot-plan-its-first-sprint.md) | bug | Fixed | 5/5 AC(s) verified; critic APPROVE (qa seat - independent subagent, final delivery round) |
| [BG0559](../../sdlc-studio/bugs/BG0559-the-doc-surface-gate-lane-raises-modulenotfounderror-in.md) | bug | Fixed | 5/5 AC(s) verified; critic APPROVE (qa seat - independent subagent, final delivery round) |
| [BG0560](../../sdlc-studio/bugs/BG0560-the-page-readme-sends-every-existing-user-to.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (qa seat - independent subagent, final delivery round) |

## Remaining (5)

### US0662 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/plan_review.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_plan_review.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0662-a-project-with-no-closed-run-reports-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0663 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/plan_review.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-config.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/config-defaults.yaml` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_plan_review.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0663-the-softening-expires-on-run-history-alone-so.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0664 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `tools/rehearse-release.sh` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py` - declared Affects
- **file:** `sdlc-studio/stories/US0664-a-greenfield-fixture-is-built-from-nothing-and.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0665 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `tools/rehearse-release.sh` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py` - declared Affects
- **file:** `sdlc-studio/stories/US0665-a-v4-era-fixture-is-driven-through-migrate.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0666 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `AGENTS.md` - declared Affects
- **file:** `tools/tests/test_check_spec_claims.py` - declared Affects
- **file:** `sdlc-studio/stories/US0666-the-rehearsal-runs-as-a-gate-lane-at.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Generated at the run close (`handoff generate`) |
