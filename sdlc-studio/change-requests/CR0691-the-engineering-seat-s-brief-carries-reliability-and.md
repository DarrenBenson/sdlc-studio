# CR-0691: The engineering seat's brief carries reliability and observability checks drawn from the TRD

> **Status:** Proposed
> **Parent:** RFC0063
> **Related:** RFC0062, RFC0064
> **Priority:** Medium
> **Type:** enhancement
> **Size:** M
> **Date:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T12:22:10Z

## Summary

The engineering seat reviews a unit against its criteria and its charter, but nothing in its brief asks how the change behaves when a dependency fails, or whether it emits what an operator needs to see it fail. RFC0064 cites a published case that credits reliability, observability and review agents informed by production incident history, together, with a lower change failure rate. This CR gives the TRD a place to declare each dependency's failure behaviour and the required observability patterns, and has `critic.py brief --seat engineering` carry checks drawn from it, scoped to the unit's Affects and sized against RFC0062's context budget.

Where the requirements live today: the shipped PRD template keeps non-functional requirements in its section 5 (Performance, Security, Scalability, Availability). The TRD template has Integration Patterns, Security and Performance sections but no reliability or observability section, and this repository's TRD has none either. So the checks need a source before a brief can carry them.

## Impact

Serves Abena Osei's End goal 4 and Graham Doyle's End goal 3 (O12). Without it a change that swallows a dependency failure, or fails without a log line or a metric, passes engineering review. Cost: every engineering brief grows, so the size is capped (criterion 4).

## Acceptance Criteria

- [ ] The TRD template gains a Reliability and Observability section: for each external dependency, the behaviour when it fails (fail the request, return a partial result, or return a default) with its timeout and retry policy; and the observability patterns every change must keep (for example a structured log line with a correlation id on the failure path, error and latency metrics, a health check, and an alert on a declared failure)
- [ ] `critic.py brief --seat engineering` carries, for a unit whose Affects touch a component the TRD's section names, that component's declared failure behaviour and observability requirements as checks the reviewer answers; a unit touching none carries one line saying so
- [ ] The engineering seat's charter, shipped and this repository's card, asks for a finding when a change's failure path differs from the declared behaviour or emits none of the required signals, and treats a missing declaration as a note, not a REJECT
- [ ] Context budget (RFC0062): the added checks cost at most 500 tokens on any engineering brief, as `critic.py brief` counts it, measured on a fixture TRD with five dependencies; the product and QA seats' briefs do not change
- [ ] A project whose TRD has no Reliability and Observability section gets one line in the engineering brief naming the section to add, and review is neither refused nor slowed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Raised |
