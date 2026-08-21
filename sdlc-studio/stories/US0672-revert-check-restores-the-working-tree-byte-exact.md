# US0672: revert-check restores the working tree byte-exact, including when it is interrupted

> **Status:** Draft
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
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
- [ ] **AC2** Given the revert-check INTERRUPTED partway, the selector run raising, when the process unwinds, then the working tree is still byte-identical - the restore happens in a `finally`, so a check that dies cannot leave a unit's production change reverted on disk
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_the_tree_is_byte_identical_after_an_interrupted_run
- [ ] **AC3** Given UNCOMMITTED edits present in the working tree when the check starts, when it completes, then those edits are still there. The revert must snapshot and restore BYTES, never restore from HEAD: a `git checkout HEAD --` restore destroyed uncommitted work the first time this was built, including the fix it had just been used to validate
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_uncommitted_edits_survive_the_check

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
