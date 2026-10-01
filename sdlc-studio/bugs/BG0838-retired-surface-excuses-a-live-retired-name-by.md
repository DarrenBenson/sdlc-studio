# BG0838: retired_surface excuses a live retired name by the shape of its sentence, so a live instruction passes as history

> **Status:** Won't Fix
> **Closed with findings in:** D0291, discovery backlog sweep 2026-10-01 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/retired_surface.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retired.py, evals/scenarios/09-lean-sprint.json, .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_marker.py, changelog.d/BG0838.md
> **Evidence:** HEAD 7e53a438 in-process probe of retired_surface.live_mentions (three sentences); US0924 review Lows; website project W5 review
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:27:11Z

## Summary

`retired_surface.live_mentions` returns nothing for '`sprint.py preflight` refuses a close that is not ready.' because its clause says 'refuses', while 'Run `sprint.py preflight` before the close.' is caught: the exemption reads prose shape. The same class leaked three rounds running in the website project's mirror of this rule and was repaired there with an explicit marker. US0924's review also found a parenthetical refusal gap, bare v5 retired-context untested, a flag lead that accepts a bare backtick (false positive at help/arguments.md:86), and a FileNotFoundError when the module runs in an installed copy (it reads the repo CHANGELOG). Eval scenario 09's FB5 names the retired `close --apply-signoff` to forbid it and is flagged under evals/.

## Steps to Reproduce

``live_mentions('`sprint.py preflight` refuses a close that is not ready.')`` returns `[]`.

## Proposed Fix

Replace the prose-shape exemptions with an explicit history marker (an HTML comment or a `retired:` prefix) and exempt nothing else; mark scenario 09's FB5.

## Acceptance Criteria

- [ ] **AC1** Given a sentence naming a retired verb with no history marker, whatever its verbs, then `live_mentions` reports it; with the marker it does not. Fails on: HEAD's 'refuses' exemption
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_marker.py::RetiredMarkerTests::test_only_the_marker_exempts

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
