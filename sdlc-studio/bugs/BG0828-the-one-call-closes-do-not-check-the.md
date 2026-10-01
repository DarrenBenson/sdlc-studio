# BG0828: The one-call closes do not check the review brief: artifact.py close records a verdict with no brief and no warning, and transition --brief accepts a fingerprint no brief printed

> **Status:** Won't Fix
> **Closed with findings in:** D0291, discovery backlog sweep 2026-10-01 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/help/arguments.md, .claude/skills/sdlc-studio/help/help.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_one_call_close_brief.py, changelog.d/BG0828.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** BG0812 r1 review finding 3; BG0815 builder hand-back; HEAD 7e53a438 `artifact.py close --help` (no --brief); transition.py:1572 warns only when brief is empty
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:30Z

## Summary

BG0812 made `transition.py set --verdict` warn when no `--brief` is given. `artifact.py close --verdict --reviewer --author` is a second one-call route to a terminal status with a recorded critic verdict, listed in help/arguments.md:86 and help/help.md:245; it takes no `--brief` and prints no warning, and the eval 06 grader accepts it. On the warned route, `--brief <fp>` is stored as given: a fingerprint matching no brief `critic.py brief` printed for the unit (`critic.noted_brief`) passes silently.

## Steps to Reproduce

`artifact.py close --id BGxxxx --verdict approve --reviewer R --author A`: Fixed with a verdict row, no warning. `transition.py set BGxxxx Fixed --verdict approve --reviewer R --author A --brief 000000000000`: no warning.

## Proposed Fix

Route both through one helper: warn (never refuse) when the verdict carries no brief, and when the given fingerprint matches no brief noted for the unit; add `--brief` to `artifact.py close` and document it beside the transition form.

## Acceptance Criteria

- [ ] **AC1** Given `artifact.py close` with a verdict and no brief, then it prints the same stderr warning transition prints. Fails on: HEAD's silent close
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_call_close_brief.py::OneCallCloseBriefTests::test_artifact_close_warns_without_a_brief
- [ ] **AC2** Given a --brief fingerprint that matches no brief noted for the unit, then the close warns naming the fingerprints noted. Fails on: HEAD, which stores it silently
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_one_call_close_brief.py::OneCallCloseBriefTests::test_an_unmatched_brief_is_warned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
