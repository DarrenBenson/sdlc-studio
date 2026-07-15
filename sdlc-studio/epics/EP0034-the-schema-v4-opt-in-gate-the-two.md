# EP0034: The schema-v4 opt-in gate: the two-backlog workflow becomes enforce-on-request, upgrade-safe

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M
> **Derived Point Total:** 9
> **Parent:** RFC0040

## Summary

RFC0040 keystone. A `two_backlog_enforced(root)` predicate (config `two_backlog.enforce`, default off = upgrade-safe) gates the hard workflow rules (G1 plan-refusal, G2 derived terminal status, undecomposed drift, the CR-creation Size demand) so an existing project keeps its old flow until it opts in. This repo sets the flag true to stay enforced. Traces to RFC0040.

## Story Breakdown

- [x] [US0125: two_backlog_enforced predicate + this repo opts in](../stories/US0125-two-backlog-enforced-predicate-this-repo-opts-in.md)
- [x] [US0126: G1 plan-refusal fires only when enforced](../stories/US0126-g1-plan-refusal-fires-only-when-enforced.md)
- [x] [US0127: G2 derived-terminal gate fires only when enforced](../stories/US0127-g2-derived-terminal-gate-fires-only-when-enforced.md)
- [x] [US0128: undecomposed drift + CR-creation Size demand respect the gate](../stories/US0128-undecomposed-drift-cr-creation-size-demand-respect-the.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
