# CR-0527: the close has no fixed point, so a repair made during it re-opens the ledger it just satisfied

> **Status:** In Progress
> **Decomposed-into:** EP0204
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** human
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-sprint.md
> **Priority:** Critical
> **Type:** Improvement
> **Size:** M

## Summary

A close writes a retro that accounts for its batch, then stamps the close-owed baseline. Any unit that reaches a terminal status AFTER that stamp is unaccounted for, and the ledger re-opens. Repairs made DURING a close are exactly such units, so the ceremony cannot converge while anything is being fixed inside it.

Observed twice in one close of RUN-01KYZKY5. BG0496 was found and fixed during the close, re-opened the ledger, and was accounted for by amending the retro and re-stamping. BG0498 - eleven tests silently absent - was then found and fixed, and re-opened it again. Each repair invalidated the account written moments before.

The operator's reading was that the sprint was never being closed. The mechanism is worse than that: it WAS closed, repeatedly, and each close was undone by the next repair. Every mechanical check passed each time - `is_open` False, outcome stopped, goal judged, zero units in Review, zero non-conformant - and the ledger still said a close was owed.

## Impact

This is the direct cause of a close that appears never to finish, and it punishes exactly the right instinct: finding and fixing a defect during a close is what a careful close is for, and it is the thing that makes the close unconvergeable. It also makes the close-owed advisory untrustworthy, because it fires on a run that has genuinely accounted for itself - and an advisory that cries wolf is one people learn to step over.

## Acceptance Criteria

- [ ] The RULE is stated in the doctrine and enforced: a finding surfaced during a close is FILED and deferred to the next run, never repaired inline, so the close has a fixed point
- [ ] `sprint close` and `sprint stop` REFUSE to proceed while the working tree carries a repair to a batch unit, naming what must be committed or deferred first - the rule is gated in the command, not left to discipline
- [ ] The close-owed ledger distinguishes a unit that reached terminal BEFORE the retro was written from one that reached it after, and reports the second as a close-time repair rather than as an unaccounted unit
- [ ] A close-time repair that is unavoidable is recorded as an explicit override with its reason, so the exception is visible and countable rather than routine
- [ ] Re-running a completed close over an unchanged tree is a no-op that reports the run already accounted for, rather than re-deriving an account that can differ

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
