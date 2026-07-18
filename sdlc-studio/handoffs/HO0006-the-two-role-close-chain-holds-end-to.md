# HO-0006: The two-role close chain holds end-to-end: the close ceremony cascades and signs off deterministically, resists the running-run hazard, and a sprint-level review satisfies the per-unit gate

> **Date:** 2026-07-18
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KXS5JY (started 2026-07-17T23:02:34Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

5 of 7 unit(s) remain (0 suit copilot-assisted completion, 5 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 240 min, units 8 unit(s)
- **Spent:** 465.9 min, 2 unit(s) terminal
- **Delivered:** 2 unit(s)
- **Token forecast:** ~650,000 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (2)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0188](../../sdlc-studio/bugs/BG0188-sprint-plan-write-accumulates-a-new-batch-into.md) | bug | Fixed | no verifier or verdict on record |
| [BG0189](../../sdlc-studio/bugs/BG0189-project-upgrade-current-schema-2-contradicts-init-py.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (5)

### US0236 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0236-sprint-close-apply-signoff-records-per-unit-sign.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0237 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0237-cascade-parent-epics-crs-rfcs-terminal-write-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0238 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0238-idempotent-re-run-after-a-mid-cascade-stop.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0247 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `sdlc-studio/stories/US0247-a-recorded-sprint-level-adversarial-full-diff-verdict.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0248 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/reference-sprint.md` - declared Affects
- **file:** `sdlc-studio/stories/US0248-the-close-sign-off-brief-reads-a-sprint.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

## Open decisions

_None recorded._ Rulings made during the run live in the tranche ledger (`sdlc-studio/decisions/`); settled decisions belong in `sdlc-studio/decisions.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Generated at the run close (`handoff generate`) |
