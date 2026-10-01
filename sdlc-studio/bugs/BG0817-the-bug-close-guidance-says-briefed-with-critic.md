# BG0817: The bug-close guidance says briefed with critic.py brief but never says to hand the reviewer the brief whole, so agents relay a trimmed or broken brief

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-bug.md, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py, changelog.d/BG0817.md
> **Evidence:** US0963 eval run v6-main, scenario 06-independence-gate, final run grader report (EB3 caveat) and run 2 transcript, 2026-09-28
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T15:20:30Z

## Summary

> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: help/bug.md:158 and reference-bug.md:197/268 say only 'briefed with `critic.py brief`'; `critic.py brief --unit BG0827 --seat qa > brief.txt` already writes the whole 99-line brief to the file with the fingerprint footer on stderr, so no `--out` flag is needed.

In the v6 eval 06 runs on main (run v6-main, 2026-09-28) the worker ran critic.py brief correctly, then relayed its own shortened version to the reviewing subagent: the final run dropped the brief's standing practices and lessons and added its own mutation instruction; run 2's first reviewer launch carried an unexpanded shell placeholder reading 'see below' and no brief at all. help/bug.md and reference-bug.md say the reviewer is 'briefed with critic.py brief' but not that the brief text is passed verbatim; only reference-scripts-review.md:118 says 'pipe it to the reviewing subagent verbatim', which the worker never read. critic.py brief prints to stdout with no file to hand over.

## Steps to Reproduce

Run scenario 06 against main; the worker briefs with critic.py brief, then writes its own prompt for the reviewer from a summary of the brief.

## Proposed Fix

State in the bug fix and close steps that the reviewer receives the brief text whole, handed over as a file: `critic.py brief --unit BG{NNNN} --seat qa > brief.txt` (stdout is the brief; the fingerprint footer is on stderr). Documentation only: the `--out` flag first proposed is dropped, because stdout redirection already does it.

## Acceptance Criteria

- [ ] **AC1** Given help/bug.md and reference-bug.md, when their fix and close steps are read, then each says the reviewer is given the brief text whole and names the `> brief.txt` hand-over. Fails on: HEAD's 'briefed with `critic.py brief`' alone
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py::BriefHandoverTests::test_the_close_steps_say_pass_the_brief_whole
- [ ] **AC2** Given a fixture bug, when `critic.py brief --unit BG0001 --seat qa --root <fixture> > brief.txt` runs as the guidance says, then brief.txt holds the brief and no `brief fingerprint:` line, and stderr carries the fingerprint the file's text hashes to (`critic.brief_fingerprint`). Fails on: a brief that printed its footer to stdout, which would put the footer into the file the reviewer reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py::BriefHandoverTests::test_a_redirected_brief_is_the_fingerprinted_text

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
| 2026-10-01 | backlog value pass (D0291) | Groomed: premise executed at HEAD; `--out` dropped (stdout redirection already hands the brief over); Points 2 to 1; critic.py and test_critic.py leave Affects |
