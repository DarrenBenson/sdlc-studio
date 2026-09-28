# BG0817: The bug-close guidance says briefed with critic.py brief but never says to hand the reviewer the brief whole, so agents relay a trimmed or broken brief

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-bug.md, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py, changelog.d/BG0817.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** US0963 eval run v6-main, scenario 06-independence-gate, final run grader report (EB3 caveat) and run 2 transcript, 2026-09-28
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T15:20:30Z

## Summary

In the v6 eval 06 runs on main (run v6-main, 2026-09-28) the worker ran critic.py brief correctly, then relayed its own shortened version to the reviewing subagent: the final run dropped the brief's standing practices and lessons and added its own mutation instruction; run 2's first reviewer launch carried an unexpanded shell placeholder reading 'see below' and no brief at all. help/bug.md and reference-bug.md say the reviewer is 'briefed with critic.py brief' but not that the brief text is passed verbatim; only reference-scripts-review.md:118 says 'pipe it to the reviewing subagent verbatim', which the worker never read. critic.py brief prints to stdout with no file to hand over.

## Steps to Reproduce

Run scenario 06 against main; the worker briefs with critic.py brief, then writes its own prompt for the reviewer from a summary of the brief.

## Proposed Fix

State in the bug fix and close steps that the reviewer receives the brief text whole (the fingerprint records exactly that text), and give critic.py brief an --out FILE so the brief can be handed over without transcription; name it in the guidance.

## Acceptance Criteria

- [ ] **AC1** Given help/bug.md and reference-bug.md's fix and close steps, then each says the reviewer is given the brief text whole, not a summary. Fails on: 'briefed with critic.py brief' alone
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py::BriefHandoverTests::test_the_close_steps_say_pass_the_brief_whole
- [ ] **AC2** Given critic.py brief --unit <id> --seat qa --out <file>, then the file holds exactly the brief printed to stdout and its fingerprint is unchanged. Fails on: no --out, or a file whose text differs from the fingerprinted brief
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py::BriefHandoverTests::test_brief_out_writes_the_fingerprinted_text

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
