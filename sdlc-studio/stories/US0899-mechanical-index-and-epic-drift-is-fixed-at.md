# US0899: Mechanical index and epic drift is fixed at commit, not refused

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/reference-outputs.md, tools/repo_writes.py, tools/tests/test_lean_index_drift.py, .claude/skills/sdlc-studio/scripts/sprint.py, tools/rehearse-release.sh, .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/help/epic.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_archive.py, tools/release-rehearsal-baseline.txt
> **Epic:** EP0262
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a status change
**I want** a stale index or an epic whose children are all finished to be brought up to date by the commit itself
**So that** a commit is no longer refused for drift whose only remedy is to run `reconcile apply` and stage again

## Acceptance Criteria

- **AC1:** Given a staged story transition that leaves its type's `_index.md` stale and its epic's every child terminal, when the commit runs through the real hook, then the hook applies the fix (`reconcile apply` for the index, `transition.py set` for the epic), restages exactly the files it wrote, and the commit lands containing them with the repo-writes lane green
  - **Verify:** pytest tools/tests/test_lean_index_drift.py::IndexDriftTests::test_the_hook_applies_and_restages_mechanical_drift
  - **Verified:** yes (2026-09-24)
- **AC2:** Given one of those files also carrying unstaged edits of its own, when the commit runs, then the hook does not restage it and names the drift it left - the author's unstaged work never enters the commit (a `git add -u` implementation fails this)
  - **Verify:** pytest tools/tests/test_lean_index_drift.py::IndexDriftTests::test_a_file_with_unstaged_edits_is_never_restaged
  - **Verified:** yes (2026-09-24)
- **AC3:** Given an epic whose every child is Superseded, Won't Implement or Won't Fix, then the status it derives is Superseded, a new terminal in the epic vocabulary, never Done; an epic with any Done child derives Done
  - **Verify:** pytest tools/tests/test_lean_index_drift.py::IndexDriftTests::test_an_epic_of_abandoned_children_derives_superseded
  - **Verified:** yes (2026-09-24)
- **AC4:** Given `gate.py --root .` over a tree with index-derived or epic-status-stale drift (as CI runs it), then those two lanes report without failing, while any other reconcile drift kind still fails
  - **Verify:** pytest tools/tests/test_lean_index_drift.py::IndexDriftTests::test_the_gate_reports_mechanical_drift_without_failing
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
