# CR-0147: doc_freshness test-count must count what the runner reports, not test definitions

> **Status:** Approved
> **Priority:** Low
> **Type:** Bug
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

doc_freshness's test-count-drift lane counts test definitions statically (1019 that day) while unittest discover reported Ran 1017 - the two-off is subclass/skip accounting. The operator ends up writing the LATEST.md claim to satisfy the checker rather than the runner, which is backwards: the claim readers care about is 'how many tests ran green'. The checker should derive its truth the same way the suite reports it (or the claim wording should name what is counted).

## Acceptance Criteria

- [ ] PREFERRED (cheap half): the finding names its counting method ("N test functions
      counted statically; the runner may report fewer for skips/subclasses") so the claim
      and the checker agree on what is being counted - doc_freshness must NOT run the
      1000+-test suite to check a prose claim
- [ ] a regression test pins the parity on a fixture with a skipped/conditional test; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
| 2026-07-04 | claude | Operator review applied: the name-the-method half is the preferred AC; running the suite inside the freshness check is explicitly rejected |
