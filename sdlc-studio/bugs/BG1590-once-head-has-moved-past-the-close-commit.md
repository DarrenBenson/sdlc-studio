# BG1590: Once HEAD has moved past the close commit, sprint sign judges the tree against that commit but still re-derives the page from the working tree, so a ruling recorded after the close blocks the seal

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_respects_carried_units.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, changelog.d/BG1590.md, .claude/skills/sdlc-studio/scripts/tests/test_sign_ruling_after_close.py
> **Evidence:** Run sixteen sign rehearsal, 2026-11-18, at local commit 1c7ae77a (never pushed): sign judged against 59763d63 and refused on issue_detail[0]; sprint.py lines 11251-11268.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T14:12:06Z

## Summary

D0524 says a waiting run is judged against its committed close once HEAD moves past it, and that a later change belongs in a commit on top. sprint sign does take the tree check from the close commit, but `_page_no_longer_matches` then re-derives the report from the working tree. A known-issue ruling the operator makes after the close, written into the retro's Known issues carried table, changes the page's issue detail, so sign refuses with 'RPT0035 no longer matches what it re-derives to'. There is no tool path for a ruling made after the close to reach the retro without re-closing the run; run sixteen's eight rulings (D0527) had to stay in the decision log.

## Steps to Reproduce

On a run closed awaiting signature, with a commit on top of the close commit: add a not-stop-ship row for a finding the close left unruled to the retro's Known issues carried table, commit it, then run sprint.py sign --report <the run's report> --principal <anyone> in a clone. It prints 'judged against <close commit>' and then 'sign REFUSED: ... no longer matches what it re-derives to ... `issue_detail[0]`'.

## Proposed Fix

When sign judges against the committed close, re-derive the page from that commit's tree as well, or give sign a way to record a ruling made after the close (beside the signature, not in the page), and test both with a retro row added on top of the close commit.

## Acceptance Criteria

- [ ] **AC1** Given a run closed awaiting signature and a later commit adding a not-stop-ship row to the retro's Known issues carried table, when `sprint.py sign --report <the run's report> --principal <operator>` runs in a clone, then it judges both the tree and the re-derived page against the close commit and seals, with no 'no longer matches what it re-derives to' refusal. Fails on: sign refuses on `issue_detail[0]` because the page is re-derived from the working tree.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_ruling_after_close.py::SignJudgesPageFromCloseCommitTests
- [ ] **AC2** Given the same run where the later commit changes a file the report's page is built from in a way the close did not describe, when `sprint.py sign` runs, then it still refuses on the page that the close commit derives, as a positive control. Fails on: the page check is dropped when sign judges against the close commit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_ruling_after_close.py::SignJudgesPageFromCloseCommitTests

## Impact

The operator cannot record a stop-ship ruling for a finding the close left unruled without re-closing the run, and the sign path contradicts D0524: half of it reads the close commit and half the live tree.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (qa seat, groom) | Acceptance criteria authored for planning (run twenty-one) |
