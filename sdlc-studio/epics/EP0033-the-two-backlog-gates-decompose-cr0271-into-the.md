# EP0033: The two-backlog gates: decompose CR0271 into the delivery units that build it

> **Status:** Done
> **Size:** L
> **Derived Point Total:** 14
> **Parent:** CR0271
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Implementation epic for CR0271 (RFC0038 U6). CR0271 is a REQUEST (T-shirt sized); this epic is its decomposition into the sized delivery stories that build the two-backlog gates (G1-G5). Traces to CR0271; CR0271 reaches Complete by derivation (its own G2 gate) when these stories are Done.

## Story Breakdown

- [x] [US0120: G3 request-child link primitive: resolve parent<->child both ways, write links on both sides, reconcile verifies](../stories/US0120-g3-request-child-link-primitive-resolve-parent-child.md)
- [x] [US0121: G1 plan refuses an RFC or CR as a sprint unit and names the decompose command](../stories/US0121-g1-plan-refuses-an-rfc-or-cr-as.md)
- [x] [US0122: G2 terminal request status is derived from children, never asserted](../stories/US0122-g2-terminal-request-status-is-derived-from-children.md)
- [x] [US0123: G4 status reports the request backlog and the product backlog separately](../stories/US0123-g4-status-reports-the-request-backlog-and-the.md)
- [x] [US0124: G5 reconcile reports a childless non-terminal request as UNDECOMPOSED](../stories/US0124-g5-reconcile-reports-a-childless-non-terminal-request.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
