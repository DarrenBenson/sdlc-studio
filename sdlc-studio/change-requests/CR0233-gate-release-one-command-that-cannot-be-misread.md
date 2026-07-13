# CR-0233: gate --release: one command that cannot be misread before a tag

> **Status:** Proposed
> **Target:** v4.1
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

BG0104's process half: the pre-tag ritual today is gate.py PLUS a separate `verify_ac` run whose exit code the operator (human or agent) must remember not to discard - exactly the judgement-shaped gap the engagement-floor work just measured elsewhere. Ship gate.py --release: the standard gate plus the executable-AC verify pass and the release checklist reads, failing loudly as one exit code, so tagging on a red verify layer requires ignoring a failing command rather than misreading a passing-looking one.

## Acceptance Criteria

- [ ] gate.py --release runs the standard gate plus `verify_ac` run and fails (exit 1, named failures) on any red AC
- [ ] The release-gate workflow template and doctrine rule 5 name the single command; the checklist references it
- [ ] A regression test proves --release exits 1 when a story carries a failing Verify line

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
