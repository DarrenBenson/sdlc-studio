# BG0888: help/gate.md says the commit-msg hook snippet degrades honestly with no script, but it blocks

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/gate.md, tools/tests/test_lean_gate_commit_msg_snippet.py, changelog.d/BG0888.md
> **Evidence:** US0973 QA review (RUN-01M3VF2J)
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T19:02:09Z

## Summary

help/gate.md:350 says the commit-msg hook snippet exits without blocking when its script is missing; python3 exits 2 on the missing file and the commit is blocked.

## Steps to Reproduce

1. Install the help/gate.md commit-msg snippet with `CLAUDE_SKILL_DIR` pointing at a folder with no scripts. 2. git commit -> blocked, exit 2.

## Proposed Fix

Guard the call on the script existing, or reword the sentence to say it blocks.

## Acceptance Criteria

- [ ] **AC1** Given the commit-msg snippet extracted from `help/gate.md` and run with `CLAUDE_SKILL_DIR` at a folder holding no `scripts/engagement_floor.py`, when it runs on a message file, then it exits 0 and prints one line naming the missing script.
  - **Verify:** pytest tools/tests/test_lean_gate_commit_msg_snippet.py::GateCommitMsgSnippetTests::test_a_missing_script_does_not_block
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD's snippet exits 2 and blocks the commit
- [ ] **AC2** Given the same snippet with the shipped skill in place and a message whose subject names two ids and carries no `Refs:` trailer, when it runs, then it exits non-zero, as `--strict` promises.
  - **Verify:** pytest tools/tests/test_lean_gate_commit_msg_snippet.py::GateCommitMsgSnippetTests::test_the_strict_check_still_refuses
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** a guard that makes the snippet exit 0 whatever the message

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (groomer) | Groomed: premise executed at 78ae6c43: the help/gate.md commit-msg snippet with `CLAUDE_SKILL_DIR` at a folder holding no scripts exits 2 (`python3: can't open file .../engagement_floor.py`), so the commit is blocked while the guide says it exits without blocking; criteria authored, Points and Affects set |
