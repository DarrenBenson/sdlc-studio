# BG0786: flow.py compute takes about 90 seconds on this repository, so its CLI grammar control times out at 120 under load and reddens the push gate

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py, changelog.d/BG0786.md
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T13:24:08Z

## Summary

`test_cli_grammar.py`::RootIsReadNotJustParsed::`test_every_listed_verb_can_actually_fail_the_guard` runs flow.py compute against the real repository with a 120s timeout. Measured 2026-09-26 at load ~8: 89s at 93d37f16, 92s at HEAD, so not a regression, but under the push gate's parallel full suite it exceeded 120s and refused the push.

## Steps to Reproduce

time python3 -B .claude/skills/sdlc-studio/scripts/flow.py --root . compute

## Proposed Fix

Profile flow.py compute and cut its cost; or point the control at a fixture root that still names a real artefact, since the control only needs the verb to discriminate.

## Acceptance Criteria

- [ ] **AC1** Given a fixture repository whose units were closed, reopened and closed again, set to Won't Do, and edited after closing, when `flow.compute` runs, then every unit's delivery date equals the per-file `git log -1 -G` answer. Fails on: a batched pattern broader than the anchored Status header, which moves a unit's date
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_flow.py::BatchedTerminalDateTests::test_the_batched_read_equals_the_per_file_read
  - **Verified:** yes (2026-09-27)
- [ ] **AC2** Given a fixture of 40 delivered units, when `flow.compute` runs, then it spawns a bounded number of git processes independent of the unit count. Fails on: HEAD's `terminal_date`, one `git log` per delivered unit (1,483 on this repository: 39.5 s of a 43.9 s profile waiting on them)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_flow.py::BatchedTerminalDateTests::test_git_is_called_a_bounded_number_of_times
  - **Verified:** yes (2026-09-27)

## Notes

- Measured in a clean clone at dee380d9, load 3.5: `flow.py --root . compute` 41.4 s; one `git log --format=%x00%aI --name-only -G '^> \*\*Status:\*\* (<terminal statuses>)$' -- sdlc-studio/` 0.94 s. The newest matching commit per path is the per-file answer because a file has one Status line; keep the per-file call for the few `Blocked` reads. Every `sprint close` pays `flow.compute` at least twice (the checklist step and the report render both reach `sprint_report._flow_summary`), so this also shortens the close. In v6.0.0: no behaviour change, and it stops the grammar control timing the push gate out under load. 2 to 3 points for the differential fixture.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | Groomed for Sprint 6: one batched history read, pinned by a differential test; 2 to 3 points |
