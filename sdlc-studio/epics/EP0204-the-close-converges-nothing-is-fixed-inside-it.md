# EP0204: The close converges: nothing is fixed inside it, and the ledger can tell a close-time repair from an unaccounted unit

> **Status:** Draft
> **Derived Point Total:** 10
> **Parent:** CR0527
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0527. Delivers the work CR0527 requested.

## Story Breakdown

- [ ] [US0616: sprint close and sprint stop refuse while the tree carries a repair to a batch unit](../stories/US0616-sprint-close-and-sprint-stop-refuse-while-the.md)
- [ ] [US0617: the close-owed ledger distinguishes a close-time repair from an unaccounted unit](../stories/US0617-the-close-owed-ledger-distinguishes-a-close-time.md)
- [ ] [US0618: an unavoidable close-time repair is recorded as an explicit override with its reason](../stories/US0618-an-unavoidable-close-time-repair-is-recorded-as.md)
- [ ] [US0619: re-running a completed close over an unchanged tree is a no-op that says so](../stories/US0619-re-running-a-completed-close-over-an-unchanged.md)

## Acceptance Criteria (Epic Level)

- [ ] The RULE is stated in the doctrine and enforced: a finding surfaced during a close is FILED and deferred to the next run, never repaired inline, so the close has a fixed point
- [ ] `sprint close` and `sprint stop` REFUSE to proceed while the working tree carries a repair to a batch unit, naming what must be committed or deferred first - the rule is gated in the command, not left to discipline
- [ ] The close-owed ledger distinguishes a unit that reached terminal BEFORE the retro was written from one that reached it after, and reports the second as a close-time repair rather than as an unaccounted unit
- [ ] A close-time repair that is unavoidable is recorded as an explicit override with its reason, so the exception is visible and countable rather than routine
- [ ] Re-running a completed close over an unchanged tree is a no-op that reports the run already accounted for, rather than re-deriving an account that can differ

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
