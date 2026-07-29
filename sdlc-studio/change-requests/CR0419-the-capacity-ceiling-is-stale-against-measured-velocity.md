# CR-0419: the capacity ceiling is stale against measured velocity, so every plan reports OVER BUDGET and the warning stops being read

> **Status:** Superseded
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/.config.yaml, .claude/skills/sdlc-studio/scripts/sprint.py
> **Priority:** Medium
> **Type:** Feature
> **Size:** S

## Summary

Not recorded at the time. Its substance is the title above and the units it was decomposed into.

## Impact

Not recorded at the time. Stated rather than left blank, so a finished record is not mistaken for an unexamined one.

## Detail

`sdlc-studio/.config.yaml` sets `capacity.tokens: 1000000`, `capacity.units: 8` and
`capacity.minutes: 240`. The last four sprints actually ran:

| Run | Units | Points | Tokens |
| --- | --- | --- | --- |
| RETRO0068 | 44 | 122 | 8,332,558 |
| RETRO0069 | 19 | 61 | 6,839,526 |
| RETRO0070 | 28 | 89 | 6,722,205 |
| RETRO0071 | 18 | 44 | this run |

So every plan for months has reported OVER BUDGET on tokens, and most on units too. A warning
that fires on every single run carries no information: it cannot distinguish the 43-unit batch
that genuinely needs cutting from the 18-unit one that does not. The capacity report is
currently a constant.

The ceiling is not wrong because the numbers are low - it is wrong because nobody chose them
against evidence that now exists. `retros/VELOCITY.md` holds four measured rows.

## Impact on planning

The one instrument meant to say "this batch does not fit" says it unconditionally, so the
operator learns to scroll past the only warning that would catch a genuinely oversized sprint.

## Options

**A. Derive the ceiling from VELOCITY.md** - compute the appetite from the measured rows for
the model that will do the work, and refuse to carry a hand-set constant forward silently.
Self-maintaining. Risk: a ceiling fitted to what was done can never say the last four sprints
were all too big.

**B. Re-set the constants by hand, now, and record the reasoning** as a decision. Cheapest and
honest, but rots again.

**C. Report the ratio rather than a verdict** - state "this batch is 2.1x the standing
appetite" and let the operator judge, instead of a binary over/under that is always over.

Recommend B now and A once there are enough rows to fit against, with C as the reporting shape
either way.

## Resolution

Option B was taken: D0064 re-set `capacity` to `tokens: 15000000, minutes: 960, units: 64` by
hand, as a recorded decision, against the four measured VELOCITY rows this CR cited. The acute
symptom - every plan reporting OVER BUDGET on capacity - is resolved: a typical batch (18-44 units,
6-8M tokens) now sits inside the ceiling. Option A (derive the ceiling from VELOCITY rather than
carry a hand-set constant) is a self-maintaining refinement, deferred until there are enough rows
to fit against and refilable then; it is not needed to close the acute issue this CR raised.

## Acceptance Criteria

- [ ] The capacity ceiling is set from the measured VELOCITY rows, and the basis is recorded rather than assumed (Option A - DEFERRED, not needed for the acute fix)
- [x] A plan within the ceiling reports no over-budget warning, so the warning distinguishes the two cases (D0064: a typical batch now sits within 64 units / 15M tokens)
- [x] The decision between A, B and C is recorded in the decisions ledger before the change lands (D0064 records Option B)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-26 | sdlc-studio | Resolved via D0064 (Option B); Option A deferred |
