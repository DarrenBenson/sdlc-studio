# BG1455: escape.py trace counts a Mentions: trailer id as a unit the release shipped, so a commit that only names a unit puts it among the suspects

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/escape.py, .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py, changelog.d/BG1455.md
> **Evidence:** Run thirteen (RUN-01M7EYR3) review of US1158, qa-seat-US1158-r1, verdict sdlc-studio/reviews/verdicts/US1158/231a64965fb7-5c9a341f.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run thirteen orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T08:01:36Z

## Summary

`release_units` (scripts/escape.py:75, regex `_UNIT_ID_RE` :39) counts every US or BG id anywhere in a commit message as shipped, `Mentions:` trailers included. In this repository's convention a Mentions id is one the commit names without owning any of its files (`engagement_floor.py`:119-124), and 110 of the last 400 commits carry one, so trace proposes units the release never changed. The same review found three documented behaviours untested: the latest APPROVE rather than the latest row (`_verdict`, escape.py:104), the exclusion of the bug's own id (`trace`, :139), and the refusal for a bug with no Affects (:136-138).

## Steps to Reproduce

1. In a throwaway repository, commit US0005 (`Affects: scripts/a.py`) and tag `v0.9.0`.
2. Commit `docs(D0001): rule the release` with the trailer `Mentions: US0005`, and tag `v1.0.0`.
3. File BG0001 (`Affects: scripts/a.py`, `Shipped-in: v1.0.0`) and run
   `escape.py trace --bug BG0001 --format json`.

Measured at HEAD 3791e5193: exit 0, `units` is `['US0005']` and US0005 is proposed, though
v1.0.0 never changed it. Separately, each of three mutants of escape.py survives
`test_escape_trace.py` (4 passed each): taking the latest row instead of the latest APPROVE,
dropping the bug's own id from the filter, and dropping the no-Affects refusal.

## Proposed Fix

Count the units a commit owns, its subject ids and its `Refs:` trailer ids, and not the ids its
`Mentions:` trailers name; pin the three documented behaviours in `test_escape_trace.py`.

## Acceptance Criteria

- [ ] **AC1** Given a release whose only commit names US0005 in a `Mentions:` trailer, when `escape.py trace` runs for a bug sharing US0005's file, then US0005 is not proposed and the trace refuses with `tags no unit`. Fails on: HEAD (measured: `units` is `['US0005']` and it is proposed).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceUnitsTests::test_a_unit_named_only_in_a_mentions_trailer_is_not_proposed
  - **Verified:** yes (2026-11-23)
- [ ] **AC2** Given a release with a shared commit whose subject names US0001 and US0003 and whose trailers are `Refs: US0001` and `Refs: US0003`, and a commit whose subject alone names US0006, when trace runs for a bug sharing all three units' file, then all three are proposed. Fails on: a fix that reads only the subject line or drops every trailer line, so a `Refs:` unit is lost.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceUnitsTests::test_a_subject_or_refs_unit_is_still_proposed
  - **Verified:** yes (2026-11-23)
- [ ] **AC3** Given a unit whose ledger holds an APPROVE then a later REJECT, a release commit naming the escaped bug itself, and a bug with no Affects, when trace runs on each, then the proposal carries the APPROVE, the bug is never proposed as its own cause, and the bug with no Affects is refused with `names no Affects`. Fails on: HEAD's suite, under which the three mutants (latest row, own id kept, refusal dropped) each survive (measured).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceDocumentedRulesTests
  - **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run thirteen orchestrator) | Filed |
| 2026-11-23 | Sam Eriksson (qa) | Groomed for run twenty-four: reproduced at HEAD (a `Mentions:`-only unit proposed) and the three documented behaviours shown unpinned by three surviving mutants; criteria rewritten as three executable ones in `test_escape_trace.py`, a `Refs:` control among them; Affects moves the tests from a module that does not exist to `test_escape_trace.py`; line references corrected |
