# BG1120: A self-check record reads an author's own edit made in a merge commit as another unit's, so the brief gate admits a changed diff in a project that merges

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_survives_a_later_unit.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_merge_commit.py, changelog.d/BG1120.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** BG1117 QA review round 1, qa-seat-BG1117-r1, at 57a2bb7a: non-blocking finding 1.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T13:35:28Z

## Summary

BG1117's QA review (round 1, 2026-10-22). The own-change view walks `git log --name-only` per declared file to set aside other units' later commits. A merge commit lists no files there, so an edit the author makes while resolving a merge conflict is never seen, the record's digest still matches the content with that edit set aside, and `critic.py brief` under block admits a diff the self-check never covered (critic.py:2802). This repository lands by fast-forward, so it is not exposed here; a project that merges pull requests is.

## Steps to Reproduce

Record a self-check; on a branch, change a declared file in a merge commit's conflict resolution; brief under block: admitted.

## Proposed Fix

Treat a merge commit that touches a declared file (`git log -m --name-only`, or `--first-parent` with `-m`) as the author's own unless its subject names only another unit; pin it with a fixture that resolves a conflict in a declared file.

## Acceptance Criteria

- [ ] **AC1** Given a record and then a merge commit whose conflict resolution changes a declared file, when the unit is briefed under block, then it is refused as stale
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_merge_commit.py::MergeCommitTests::test_an_edit_in_a_merge_resolution_stales_the_record

## Impact

The self-check gate admits a changed diff, the defect the gate exists to stop.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
