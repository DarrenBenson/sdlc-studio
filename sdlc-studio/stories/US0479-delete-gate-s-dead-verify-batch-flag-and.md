# US0479: Delete gate's dead --verify-batch flag and the documentation claiming it does something

> **Status:** Review
> **Delivers:** CR0437
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/help/arguments.md, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, tools/tests/test_dead_flag_docs.py, CHANGELOG.md
> **Epic:** EP0172
> **Points:** 2

## User Story

**As an** operator choosing gate flags before a tag
**I want** `--verify-batch` gone rather than accepted and ignored
**So that** no documented flag promises a verify behaviour that no invocation of the gate has ever produced

## Acceptance Criteria

### AC1: the flag and its dead parameter are gone

- **Given** the gate CLI and `run_gate`
- **When** `gate --verify-batch` is parsed and `run_gate`'s signature is inspected
- **Then** the parse exits non-zero as an unrecognised option and `run_gate` no longer declares `verify_batch`, so nothing can pass a value nothing reads
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::VerifyBatchRemovalTests::test_the_dead_flag_and_its_parameter_are_gone
- **Verified:** yes (2026-07-29)

### AC2: the release lane still batches and a scoped run still registers no verify lane

- **Given** the verify lane spied on for its `batch` argument
- **When** `run_gate` runs with release=True and then release=False
- **Then** the release run requests batching and the scoped run registers no verify lane at all (registry["verify"] is assigned only at gate.py:1610 inside `if release:`), so removing the flag changed no gate behaviour - and the existing test's message asserting `only --release (or --verify-batch) may batch` is corrected in the same edit rather than left naming a flag that no longer exists
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::VerifyBatchRemovalTests::test_release_still_batches_and_a_scoped_run_registers_no_verify_lane
- **Verified:** yes (2026-07-29)

### AC3: nothing tracked under the skill tree still documents the flag

- **Given** the tracked files under .claude/skills/sdlc-studio enumerated with `git ls-files`, so build artefacts and untracked scratch cannot participate, and the inline comment at gate.py:1609 claiming the flag remains available for a scoped run
- **When** each tracked text file is read and searched for the option string
- **Then** there is no occurrence, and the same scan is asserted to FIND a control string that is present, so a scan that silently matched nothing cannot read as a pass - and this workspace assertion lives in tools/tests as a pytest node id like every other repo-state check, because a `shell` verifier is unresolvable to verify_ac.py's staleness sweep
- **Verify:** pytest tools/tests/test_dead_flag_docs.py::VerifyBatchDocsTests::test_no_tracked_skill_file_mentions_the_removed_flag
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
