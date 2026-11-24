# BG1316: `sprint.py handoff` silently drops an `--agent` naming a unit outside the batch, both new verbs crash on an unreadable run state, and the next-step line's stream is unpinned

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1316.md
> **Evidence:** US1141-verdict-r1 (RUN-01M7061X), findings 1-3
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T16:33:53Z

## Summary

From US1141's QA review (qa-seat-US1141-r1, non-blocking, 2026-11-09). (1) `sprint.py handoff --agent <unit>=<id>` accepts a unit outside the open run's batch, exits 0 and drops the id (sprint.py around :12281), so a mistyped unit loses the agent the resumed session needs. (2) An unreadable `sdlc-studio/.local/run-state.json` makes `handoff` and `resume` crash with a traceback and exit 1 rather than refuse with exit 2, the class of BG0405 and BG0453. (3) The test never checks that the plan's next-step line goes to stdout in text mode: `_capture` merges stdout and stderr, so a mutant printing it to stderr survives.

## Steps to Reproduce

1. Run `sprint.py handoff --agent US9999=abc` on an open run whose batch has no US9999: it exits 0 and the brief carries no such agent.
2. Corrupt a scratch copy's run-state.json and run `sprint.py resume`: it prints a traceback and exits 1.
3. Move the next-step print to stderr in a scratch copy and run `test_sprint_handoff.py`: it passes.

## Proposed Fix

Refuse an `--agent` whose unit is not in the batch, naming it; read the run state through the guarded loader and refuse with exit 2 when it cannot be read; capture stdout and stderr apart in the test and pin the next-step line to stdout.

## Acceptance Criteria

- [ ] **AC1** Given an open run whose batch has no US9999, when `sprint.py handoff --agent US9999=abc` is run, then it exits 2 naming US9999 and writes no brief; an `--agent` for a unit in the batch is still carried into the brief. Fails on: exit 0 with the agent id dropped.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::HandoffCliTests::test_an_agent_for_a_unit_outside_the_batch_is_refused_by_name
- [ ] **AC2** Given a `run-state.json` that cannot be read, when `sprint.py handoff` and `sprint.py resume` are each run, then each exits 2 with a one-line refusal naming the file and no traceback. Fails on: a traceback and exit 1.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::ResumeCliTests::test_an_unreadable_run_state_is_refused_with_exit_2_by_both_verbs
- [ ] **AC3** Given `sprint.py plan --write` in text mode, when its stdout and stderr are captured apart, then the next-step line is on stdout and not on stderr. Fails on: the line moved to stderr passing a test that merges the two streams.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::PlanNextStepTests::test_the_next_step_line_is_printed_to_stdout

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. Handoff edge cases on bad input; workaround is to pass the right unit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
