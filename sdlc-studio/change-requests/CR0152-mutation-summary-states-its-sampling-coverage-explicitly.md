# CR-0152: mutation summary states its sampling coverage explicitly

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

A mutation lane reading '12/12 mutations killed (2621 truncated)' is honest in its parts but the headline reads stronger than the coverage is: 12 of ~2633 enumerated is under 0.5% of the surface. The summary (CLI text, report JSON, gate lane detail) should state the sampled fraction plainly - e.g. '12/2633 enumerated sampled (0.5%); 12/12 sampled killed' - so a green lane can never be read as whole-surface assurance. Follow-on to the CR0146 v2 scope; one line per output path.

## Acceptance Criteria

- [ ] the CLI summary, report summary, and gate lane detail each state sampled/enumerated and the percentage when truncation occurred
- [ ] no change when nothing was truncated (sampled == enumerated reads as today)
- [ ] unit tests pin both wordings; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
