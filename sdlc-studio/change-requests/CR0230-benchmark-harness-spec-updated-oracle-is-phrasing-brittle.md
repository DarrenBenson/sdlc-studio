# CR-0230: benchmark harness: spec-updated oracle is phrasing-brittle

> **Status:** Superseded
> **Target:** v4.1
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Two of the 72 v4-rerun rows are oracle artefacts: the ledger-drift fixture's `test_9_spec_r3_updated` regex requires 'case-insensitive' or 'ignore(d) [letter] case' word order, so a semantically correct spec update ('email matches once case differences and surrounding whitespace are ignored') scores as an escape. Per the freeze discipline the rows stand as recorded and the report annotates them; fix the oracle for the NEXT protocol revision (semantic check or a broader validated phrasing set, re-validated both ways against naive and reference solutions) rather than editing the frozen fixture in place.

## Acceptance Criteria

- [ ] The fixture's spec-updated check accepts semantically equivalent phrasings (validated both ways: fails on the un-updated spec, passes on all reference phrasings collected from the v4 rerun)
- [ ] The change lands as a protocol revision note (new fixture version), never a silent edit to the frozen v2 fixture; the v4-rerun report's artefact annotations are linked

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
| 2026-07-13 | Darren | Superseded: re-homed to the `sdlc-bench` repo, which now owns the fixtures, protocol and arms under RFC0029. The oracle fix belongs where the frozen fixture lives; delivering it here would mean two homes for one workstream. Refiled as a `sdlc-bench` artefact. |
