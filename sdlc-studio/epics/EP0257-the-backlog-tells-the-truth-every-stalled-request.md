# EP0257: the backlog tells the truth: every stalled request carries a dated ruling, and the state cannot rebuild

> **Status:** Draft
> **Parent:** CR0557
> **Derived Point Total:** 31
> **Parent:** CR0591
> **Created:** 2026-09-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0591. Delivers the work CR0591 requested.

## Story Breakdown

- [ ] [US0848: the guard: a discovery request In Progress with no unresolved child and no dated ruling is reported](../stories/US0848-the-guard-a-discovery-request-in-progress-with.md)
- [ ] [US0849: rule the close-and-ceremony cluster against HEAD](../stories/US0849-rule-the-close-and-ceremony-cluster-against-head.md)
- [ ] [US0850: rule the review-and-critic cluster against HEAD](../stories/US0850-rule-the-review-and-critic-cluster-against-head.md)
- [ ] [US0851: rule the evidence-and-mutation cluster against HEAD](../stories/US0851-rule-the-evidence-and-mutation-cluster-against-head.md)
- [ ] [US0852: rule the config, docs and remaining requests against HEAD](../stories/US0852-rule-the-config-docs-and-remaining-requests-against.md)
- [ ] [US0853: re-triage BG0463's twenty batch-boundary findings against HEAD and file the survivors](../stories/US0853-re-triage-bg0463-s-twenty-batch-boundary-findings.md)
- [ ] [US0854: decompose the four 8-point stories and resolve the US0793/US0794 duplicate, so the delivery backlog is honest before the build run plans from it](../stories/US0854-decompose-the-four-8-point-stories-and-resolve.md)

## Acceptance Criteria (Epic Level)

- [ ] Every one of the 41 In-Progress discovery requests carries a dated ruling afterwards, naming which of the four outcomes it took and why. A request left In Progress is a RULING that it is still wanted and correctly started, not the absence of a decision - the sweep is judged on having ruled all 41, never on how many it closed.
- [ ] A request whose work another unit has already delivered is closed with that unit named, so the claim is checkable rather than asserted. Where the premise is that the work is done, it is verified by execution against HEAD, not by reading the title - this project has already shipped a finding whose premise had stopped being true.
- [ ] A request still wanted but never actually started returns to Proposed and rejoins the refine queue, so `status` counts it where it belongs. After the sweep, the In Progress count and the awaiting-refine count each describe what their name says.
- [ ] The tooling can tell these apart afterwards without a human re-reading them: a check reports a discovery request that is In Progress with no unresolved child and no dated ruling, so the state this sweep clears cannot silently rebuild. Without it the audit is a one-off tidy and the count drifts back.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Created via `new` (deterministic) |
