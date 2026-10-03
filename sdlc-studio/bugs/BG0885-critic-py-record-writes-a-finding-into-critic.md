# BG0885: critic.py record writes a finding into critic-verdicts.md unescaped, so markdown-shaped text breaks the lint

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_finding_escape.py, changelog.d/BG0885.md
> **Evidence:** RUN-01M3VF2J paperwork commit refused on US0972's verdict
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T18:37:45Z

## Summary

critic.py record copies --issues text into sdlc-studio/reviews/critic-verdicts.md as raw markdown. A finding quoting a regex such as [A-Z][A-`Z_]`{4,} is read as an undefined reference link (MD052), so the paperwork commit carrying the verdict is refused until the ledger is hand-edited.

## Steps to Reproduce

1. critic.py record --unit X --verdict REJECT ... --issues '[new] the shape [A-Z][A-`Z_]`{4,} matches UNKNOWN'. 2. git commit the ledger -> markdown lane FAIL MD052.

## Proposed Fix

Write each finding's text inside a code span, or escape [ ] and | when recording.

## Acceptance Criteria

- [ ] **AC1** Given a fixture bug briefed with `critic.py brief`, when `critic.py record ... --issues '[new] the shape [A-Z][A-Z_]{4,} matches UNKNOWN'` writes the verdict, then markdownlint with this repository's config reports no MD052 on `critic-verdicts.md`, and the ledger's reader (`critic.parse_findings` on the recorded row) returns the finding text exactly as given.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_finding_escape.py::VerdictFindingEscapeTests::test_a_bracketed_finding_lints_and_reads_back
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD writes the brackets raw and markdownlint fails MD052

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (groomer) | Groomed: premise executed at 78ae6c43: `critic.py record --issues '[new] the shape [A-Z][A-Z_]{4,} matches UNKNOWN'` writes `[A-Z][A-Z\_]{4,}` raw into critic-verdicts.md; markdownlint reports MD052 (`Missing link or image reference definition: "a-z"`); criteria authored, Points and Affects set |
