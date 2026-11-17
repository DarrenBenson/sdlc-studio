# EP0338: An engineering review checks a change's failure behaviour and signals against what the TRD declares

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0691
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0691. Delivers the work CR0691 requested.

## Story Breakdown

- [ ] [US1230: The TRD template gains a Reliability and Observability section for dependency failure and required signals](../stories/US1230-the-trd-template-gains-a-reliability-and-observability.md)
- [ ] [US1231: The engineering brief carries the TRD's failure and observability checks for touched components, under a cap](../stories/US1231-the-engineering-brief-carries-the-trd-s-failure.md)
- [ ] [US1232: The engineering seat charter asks for a finding on an undeclared failure path and a note on a missing section](../stories/US1232-the-engineering-seat-charter-asks-for-a-finding.md)

## Acceptance Criteria (Epic Level)

- [ ] The TRD template gains a Reliability and Observability section: for each external dependency, the behaviour when it fails (fail the request, return a partial result, or return a default) with its timeout and retry policy; and the observability patterns every change must keep (for example a structured log line with a correlation id on the failure path, error and latency metrics, a health check, and an alert on a declared failure)
- [ ] `critic.py brief --seat engineering` carries, for a unit whose Affects touch a component the TRD's section names, that component's declared failure behaviour and observability requirements as checks the reviewer answers; a unit touching none carries one line saying so
- [ ] The engineering seat's charter, shipped and this repository's card, asks for a finding when a change's failure path differs from the declared behaviour or emits none of the required signals, and treats a missing declaration as a note, not a REJECT
- [ ] Context budget (RFC0062): the added checks cost at most 500 tokens on any engineering brief, as `critic.py brief` counts it, measured on a fixture TRD with five dependencies; the product and QA seats' briefs do not change
- [ ] A project whose TRD has no Reliability and Observability section gets one line in the engineering brief naming the section to add, and review is neither refused nor slowed

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
