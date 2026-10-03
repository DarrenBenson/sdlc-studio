# BG0935: The 6.1 notes say migrate leaves prose alone and give no way to install main on Windows

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** docs/release-notes-v6.1.0.md, tools/tests/test_lean_release_notes_v61.py, changelog.d/BG0935.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T13:31:34Z

## Summary

docs/release-notes-v6.1.0.md says migrate names retired commands 'in code' and 'leaves your prose alone', but in a fixture it also named a retired command written in plain prose (only prose about handoffs goes unnamed); and with BG0934 install.ps1 defaults to the latest release, so the breaking bullet should give -Version main as the way to install main. Found by the US0983 review (D0326).

## Steps to Reproduce

1. Run migrate on a fixture whose plain prose names a retired command. 2. It is named, against the notes' sentence. 3. Read the breaking bullet: no -Version main.

## Proposed Fix

Make the sentence say what migrate names, and add -Version main to the install bullet. No behaviour change.

## Acceptance Criteria

- [ ] **AC1** Given the 6.1 notes, then the migrate sentence matches what migrate names in a fixture (a retired command in code and in plain prose is named, prose about handoffs is not), and the install bullet names -Version main for install.ps1 and --version main for install.sh. Fails on: the current 'leaves your prose alone' sentence and the bullet without -Version main
  - **Verify:** pytest tools/tests/test_lean_release_notes_v61.py::ReleaseNotesTests::test_the_migrate_and_install_sentences_are_true
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
