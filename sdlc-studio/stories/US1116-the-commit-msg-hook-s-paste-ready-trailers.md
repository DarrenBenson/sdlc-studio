# US1116: The commit-msg hook's paste-ready trailers never ask for Refs: on an id a Mentions: line already accounts for

> **Status:** Ready
> **Delivers:** CR0659
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/commit-msg, tools/enable-hooks.sh, tools/tests/test_commit_msg_mentions.py, changelog.d/US1116.md
> **Epic:** EP0297
> **Points:** 1
> **Persona:** Rowan Achterberg

## User Story

**As a** the skill maintainer committing in this repository (Rowan)
**I want** the commit-msg hook's refusal to print only the trailers still owed, and to offer `Mentions:`
**So that** the paste-ready fix never asks for the false attribution CR0659 removes

## Acceptance Criteria

- **AC1:** Given a commit whose subject names US1110, BG0989 and BG1000 with `Mentions: BG0989`, when the commit-msg hook refuses, then it prints `Refs: US1110` and `Refs: BG1000`, prints no `Refs: BG0989`, and offers `Mentions: <id>` for an id the commit only mentions
  - **Verify:** pytest tools/tests/test_commit_msg_mentions.py::CommitMsgMentionsTests::test_the_hint_skips_an_id_a_mentions_line_covers
- **AC2:** Given `.githooks/commit-msg --list`, then the message-refs lane's rule names `Mentions:` as the way to account for an id that owns none of the commit's files
  - **Verify:** pytest tools/tests/test_commit_msg_mentions.py::CommitMsgMentionsTests::test_the_lane_rule_names_mentions

## Notes

- Serves: Rowan Achterberg, End goal 3. CR0659; D0399. Depends on US1115; without it the script refuses anyway.
- AC1 must fail on: `covered` grepping only `^Refs:`, as the hook's message_lane does today.
- AC2 must fail on: the `run "message-refs"` rule string left as it is.
- Also update the echo line at tools/enable-hooks.sh:77. Check that `test_commit_msg_hook.py` and `test_lean_gate_commit_msg_snippet.py` do not pin the rule sentence verbatim.
- A cleaner alternative (LL0042) is for `check-commit-msg` to print the paste-ready lines itself and the hook to drop its duplicate id grammar; that moves this work into US1115 at one more point there. Decide at build; stay inside Affects.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Groomed under D0399 from the run-five planning pass: user story, criteria with Verify lines, mutants and risks |
