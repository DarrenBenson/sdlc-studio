# BG1781: escape.py became a tree-walking scanner in US1234, and its bare bug-file read at line 224 now fails the repository's bare-read sweep

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/escape.py, .claude/skills/sdlc-studio/scripts/tests/test_escape_trace_confirm_unreadable.py, changelog.d/BG1781.md
> **Evidence:** Run twenty-eight's push of main (2026-11-27, 23:30Z) was refused by the pre-push full suite (sdlc-studio/.local/boundary-suite-last.log): 2 red of 10874.
> **Created:** 2026-11-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-28T00:13:38Z

## Summary

US1234 (0f99dbdb2) gave escape.py a pass over the workspace, so `test_repo_hygiene`'s scanner census now counts it, and `confirm_trace`'s `path.read_text(encoding="utf-8")` at escape.py:224 is a bare artefact-body read in a scanner. BareArtefactReadSweepTests::`test_no_bare_artefact_body_reads_in_scanners` is red on main, so the push gate refuses every push. The read takes the one bug file `escape trace --confirm` rewrites, so a decode error there must refuse, not skip.

## Steps to Reproduce

1. On main, run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py::BareArtefactReadSweepTests::test_no_bare_artefact_body_reads_in_scanners`.
2. It fails naming `escape.py:224: text = path.read_text(encoding="utf-8")`.

## Proposed Fix

Mark the line `# bare-read-ok: <reason>` stating that the confirm rewrites this one bug and must refuse on an unreadable file, or route any tree-walk read through `sdlc_md.read_text_safe` while this single-file rewrite stays loud; pin that `escape trace --confirm` on a non-UTF-8 bug file refuses with nothing written.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1234 (0f99dbdb2) gave escape.py a pass over the workspace, so `test_repo_hygiene`'s scanner census now counts it, and `confirm_trace`'s...
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py::BareArtefactReadSweepTests::test_no_bare_artefact_body_reads_in_scanners
  - **Verified:** yes (2026-11-28)
- [ ] **AC2** The proposed fix lands, pinned by a test: Mark the line `# bare-read-ok: <reason>` stating that the confirm rewrites this one bug and must refuse on an unreadable file, or route any tree-walk read...
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace_confirm_unreadable.py::ConfirmOnAnUnreadableBugTests::test_confirm_on_a_non_utf8_bug_refuses_and_writes_nothing
  - **Verified:** yes (2026-11-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-28 | sdlc-studio | Filed |
