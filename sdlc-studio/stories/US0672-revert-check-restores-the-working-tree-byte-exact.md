# US0672: revert-check restores the working tree byte-exact, including when it is interrupted

> **Status:** Draft
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Verification depth:** functional [[derived: criteria 3; plan rows 3; executed 3; killed 3; survived 0; not-run 0; entry point 3 of 3 criteria through the shipped CLI, 0 in-process | fp 74af77eb7c4d ]] (byte-equality is asserted over every file in the fixture outside `.git`, not over the reverted file alone, so a restore that repaired its target and damaged a sibling would fail. NOT covered: a process killed by a signal the interpreter cannot handle, where no `finally` runs at all)
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** revert-check restores the working tree byte-exact, including when it is interrupted
**So that** CR0547 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given the revert-check completing normally, when it returns, then every file it touched is byte-identical to how it started, asserted by comparing a per-file hash taken before the revert against one taken after rather than by inspecting `git status`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_the_tree_is_byte_identical_after_a_normal_run
  - **Verified:** yes (2026-08-21)
- [ ] **AC2** Given the revert-check INTERRUPTED partway, the selector run raising, when the process unwinds, then the working tree is still byte-identical - the restore happens in a `finally`, so a check that dies cannot leave a unit's production change reverted on disk
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_the_tree_is_byte_identical_after_an_interrupted_run
  - **Verified:** yes (2026-08-21)
- [ ] **AC3** Given UNCOMMITTED edits present in the working tree when the check starts, when it completes, then those edits are still there. The revert must snapshot and restore BYTES, never restore from HEAD: a `git checkout HEAD --` restore destroyed uncommitted work the first time this was built, including the fix it had just been used to validate
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_uncommitted_edits_survive_the_check
  - **Verified:** yes (2026-08-21)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, delete the snapshot-restore loop from `revert_check` | Given the revert-check completing normally, when it returns, then every file it touched is byte-identical to how it started, asserted by comparing a per-file hash taken before the revert against one taken after rather than by inspecting `git status` |
| AC2 | in `verify_ac.py`, replace `snapshot` with `({} if sys.exc_info()[0] else snapshot)` in `revert_check`'s `finally`, so the restore runs only when nothing is unwinding | Given the revert-check INTERRUPTED partway, the selector run raising, when the process unwinds, then the working tree is still byte-identical - the restore happens in a `finally`, so a check that dies cannot leave a unit's production change reverted on disk |
| AC3 | in `verify_ac.py`, replace the byte-snapshot restore in `revert_check` with a git-sourced one - `_base_blob(root, "HEAD", rel)` | Given UNCOMMITTED edits present in the working tree when the check starts, when it completes, then those edits are still there. The revert must snapshot and restore BYTES, never restore from HEAD: a `git checkout HEAD --` restore destroyed uncommitted work the first time this was built, including the fix it had just been used to validate |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
