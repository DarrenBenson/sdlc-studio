# BG0886: The done gate's own refusal messages still print a v3 id as its hyphenless comparison key

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_done_gate_display_id.py, changelog.d/BG0886.md
> **Evidence:** BG0877 QA review (RUN-01M3VF2J)
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T18:37:46Z

## Summary

After BG0825 and BG0877 the done-gate prefix names US-01ABCDEF, but with an unanswered delivery REJECT the gate's inner message still reads US01ABCDEF carries an unanswered delivery REJECT (transition.py:1030 passes `sdlc_md.norm_id` into `_unanswered_delivery_reject`, and :783 builds the messages).

## Steps to Reproduce

1. A v3 story US-01ABCDEF with a recorded delivery REJECT. 2. transition.py set US-01ABCDEF Done -> the refusal's inner line names US01ABCDEF.

## Proposed Fix

Carry the display id into the gate messages, as BG0877 did for the prefix.

## Acceptance Criteria

- [ ] **AC1** Given a v3 story `US-<ulid>` with a recorded delivery REJECT, when `transition.py set --id <id> --status Done --root <fixture>` runs, then every line of the refusal names the story as `US-<ulid>` and none as the hyphenless key `US<ulid>`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_done_gate_display_id.py::DoneGateDisplayIdTests::test_the_reject_refusal_names_the_file_spelling
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD's inner line reads `US01M3WDB2 carries an unanswered delivery REJECT`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (groomer) | Groomed: premise executed at 78ae6c43: a v3 story US-01M3WDB2 with a recorded delivery REJECT, `transition.py set --status Done` -> the prefix names `US-01M3WDB2` but the inner line reads `US01M3WDB2 carries an unanswered delivery REJECT`; criteria authored, Points and Affects set |
