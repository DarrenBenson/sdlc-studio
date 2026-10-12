# BG1027: The commit-time links lane resolves a link against the working tree, so a staged index row linking to an untracked file passes the commit and turns CI red

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/check_links.py, .githooks/pre-commit, tools/tests/test_check_links_staged_targets.py, changelog.d/BG1027.md, tools/tests/test_check_links.py
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-12T10:33:01Z

## Summary

`tools/check_links.py` (run by `.githooks/pre-commit:198`) walks the working tree with `rglob` and tests each target on disk, so an untracked file satisfies a link that the commit does not carry. 19415be3 staged `sdlc-studio/bugs/_index.md` while another agent's filer had already written BG1024's row into it, without BG1024's file; the commit passed locally and CI run 38235507321 failed on `sdlc-studio/bugs/_index.md:102 -> BG1024-... [file missing]`. Every filer writes its index row at filing time, so a shared index routinely carries rows for files another session has not committed yet.

## Steps to Reproduce

Create an untracked bug file and add its row to the bug index; stage only the index and commit: the links lane passes. Push: CI's links lane fails on [file missing].

## Proposed Fix

At commit time, resolve a relative link from a staged markdown file against the tree the commit will record (the index plus HEAD), not the working tree; name the untracked target and say to stage it or drop the row.

## Acceptance Criteria

- [ ] **AC1** Given a staged markdown file linking to a file that exists only untracked in the working tree, when the pre-commit links lane runs, then it refuses and names the untracked target
  - **Verify:** pytest tools/tests/test_check_links_staged_targets.py::StagedTargetTests::test_an_untracked_target_is_refused
- [ ] **AC2** Given the same link with its target staged, when the lane runs, then it passes
  - **Verify:** pytest tools/tests/test_check_links_staged_targets.py::StagedTargetTests::test_a_staged_target_passes
- [ ] **AC3** Given a link to a tracked file deleted in the working tree but not in the index, when the lane runs, then it passes, because the commit still carries the target
  - **Verify:** pytest tools/tests/test_check_links_staged_targets.py::StagedTargetTests::test_an_unstaged_deletion_still_resolves

## Impact

A commit the hooks passed reds main on push; it happened on 2026-10-12 with an artefact-only commit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | Claude Opus 5.5 (triage) | Filed |
