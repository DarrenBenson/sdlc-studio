# BG1174: The v6.2 notes test exempts the whole no-Breaking paragraph, so a changed-default sentence added inside it passes with no Instead clause

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_release_notes_v62.py, changelog.d/BG1174.md
> **Evidence:** scratchpad probe US1110-r2-probe.py, mutant R1, run in isolation beside its control.
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T09:14:31Z

## Summary

2026-11-02, US1110's round-2 review (qa-seat-US1110-r1, APPROVE, non-blocking). `changed_problems` skips every paragraph that `NO_BREAKING` matches anywhere in it (tools/tests/`test_lean_release_notes_v62.py`:337-338). The sentence '`artifact.py new` now refuses a story with no `--epic`.' added inside that paragraph passes with no `Instead:`. The same sentence as its own paragraph is refused with 'the section holds text outside its change bullets'. The US1110 fragment says any paragraph but the no-Breaking statement is refused, which over-states the check by that one paragraph. The shipped notes hold no such sentence.

## Steps to Reproduce

1. Append a changed-default sentence to the no-Breaking paragraph of docs/release-notes-v6.2.0.md.
2. Run `pytest tools/tests/test_lean_release_notes_v62.py`: it passes.
3. Put the same sentence in its own paragraph: it is refused.

## Proposed Fix

Exempt only the no-Breaking sentence itself, and judge the rest of its paragraph like any other text in the section.

## Acceptance Criteria

- [ ] **AC1** A sentence other than the no-Breaking statement, inside that statement's paragraph, is refused as text outside the change bullets.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v62.py::ReleaseNotesTests::test_every_changed_behaviour_names_what_to_do

## Impact

A later edit to the notes can add an unlisted changed default with no replacement, and the test stays green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
