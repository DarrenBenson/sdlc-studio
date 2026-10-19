# EP0288: The push gate and the full suite run on a configured gate host

> **Status:** Draft
> **Derived Point Total:** 13
> **Parent:** CR0635
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0635. Delivers the work CR0635 requested.

## Story Breakdown

- [ ] [US1075: A push is judged on the gate host this clone configures](../stories/US1075-a-push-is-judged-on-the-gate-host.md)
- [ ] [US1076: Runs on a gate host are serialised, and an abandoned push stops its run](../stories/US1076-runs-on-a-gate-host-are-serialised-and.md)
- [x] [US1077: One command says whether a gate host can judge a push](../stories/US1077-one-command-says-whether-a-gate-host-can.md)
- [ ] [US1078: run-suite.sh runs the full suite on the gate host and records a verdict its check can read](../stories/US1078-run-suite-sh-runs-the-full-suite-on.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a clone configured with a gate host, when a push runs the pre-push hook, then the commit being pushed is sent to the host, `gate.py --boundary push` runs there against exactly that commit, its output streams back, and its exit code decides the push
- [ ] Given a configured gate host that cannot be reached, when a push runs, then the hook refuses and names both the host and the local fallback, and never silently runs locally or passes
- [ ] Given a clone with no gate host configured, when a push runs, then the gate runs locally exactly as today
- [ ] Given a configured gate host, when the full suite is asked for before a commit through the documented wrapper, then it runs on the host against the working tree's staged state, and a red run there is red here

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
