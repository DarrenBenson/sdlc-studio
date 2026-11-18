# BG1590: Once HEAD has moved past the close commit, sprint sign judges the tree against that commit but still re-derives the page from the working tree, so a ruling recorded after the close blocks the seal

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_respects_carried_units.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
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

- [ ] **AC1** The behaviour described is corrected: D0524 says a waiting run is judged against its committed close once HEAD moves past it, and that a later change belongs in a commit on top.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: On a run closed awaiting signature, with a commit on top of the close commit: add a not-stop-ship row for a finding the close left unruled to the retro's Known...
- [ ] **AC3** The proposed fix lands, pinned by a test: When sign judges against the committed close, re-derive the page from that commit's tree as well, or give sign a way to record a ruling made after the close...

## Impact

The operator cannot record a stop-ship ruling for a finding the close left unruled without re-closing the run, and the sign path contradicts D0524: half of it reads the close commit and half the live tree.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
