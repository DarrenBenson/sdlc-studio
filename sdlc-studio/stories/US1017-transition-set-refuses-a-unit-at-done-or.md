# US1017: transition set refuses a unit at Done or Fixed when none of its criteria fail with its change reverted

> **Status:** Draft
> **Delivers:** CR0624
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, sdlc-studio/.config.yaml, .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_gate.py, changelog.d/US1017.md
> **Epic:** EP0281
> **Points:** 5
> **Depends on:** BG1009, BG1014, US1049
> **Persona:** Maya Okafor

## User Story

**As** a team lead whose developers and their agents close units every day
**I want** the terminal transition to revert each unit's production change and report it, or refuse it once I switch the gate to block, when none of its criteria notices
**So that** a test that cannot fail is caught by the command everyone runs, not by a reviewer breaking the code by hand a round later, and I can turn the gate on when my team is ready

## Acceptance Criteria

- **AC1:** Given, under `review.revert_check: block`, a story and a bug at In Progress whose criteria all stay green with their Affects production files reverted to a base ref, and a story with one criterion that goes red, when `transition.py set` moves each to its terminal status with `--base <ref>`, then the first two are refused naming every green criterion, the base and `verify_ac.py revert-check`, with their Status unchanged and production files byte-identical, and the third reaches Done.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_gate.py::TransitionRevertGateTests::test_done_and_fixed_refuse_only_a_unit_whose_criteria_pass_without_the_change
- **AC2:** Given `block`, a unit whose Affects names no production file, and a unit with no `--base` and no recorded base while an open run whose batch does not name it holds a different base, when each moves to its terminal status, then both proceed with their production files untouched, and the output says `revert-check: not judged` with the reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_gate.py::TransitionRevertGateTests::test_a_unit_the_revert_cannot_judge_proceeds_and_says_why
- **AC3:** Given `block`, a unit transitioned while another owner holds a rewrite window, and a unit whose verifier times out after the revert, when each moves to its terminal status, then each is refused, naming the window's holder or the timed-out criterion together with the command that clears it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_gate.py::TransitionRevertGateTests::test_a_transient_not_judged_result_refuses_under_block
- **AC4:** Given a unit the lane refuses under `block`, when `transition.py set <id> Done --base <ref> --force` runs, then the unit reaches Done and its `Forced-override` field names the revert-check refusal it waived.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_gate.py::TransitionRevertGateTests::test_force_records_the_waived_revert_refusal
- **AC5:** Given a unit the lane refuses under `block`, whose verifier touches a marker file, with `review.revert_check` set in turn to `report`, `off` and an unknown value, when it moves to Done, then `report` proceeds and prints the refusal, `off` proceeds with no marker and no revert-check line, and the unknown value is refused by name.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition_revert_gate.py::TransitionRevertGateTests::test_the_setting_reports_blocks_or_stands_the_gate_down

## Notes

- Release: later (D0355 breakdown G7, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: leave the lane out of `_pre_write_gates`, or run it for `story` only (the refusal half fails); or refuse every unit the lane judges (the paired control fails)
- AC2 must fail on: fall back to `run_state.base_ref` (any open run) when `unit_base_ref` is empty, so the second unit is reverted to an unrelated run's base and refused; or treat a permanent not-judged result as a refusal
- AC3 must fail on: let a transient not-judged result (a held window, a timeout) proceed like a permanent one, so `mutation.py window open --owner x`, or a window stranded by a SIGKILL, turns the gate off with nothing recorded
- AC4 must fail on: `_force_bypassed` re-derives the ladder without the `--base` it was given (it drops `coverage_opts` at HEAD, transition.py:1109-1110), so the waived refusal reads as not judged and is never recorded
- AC5 must fail on: run the revert under `off`, so the marker appears; or read the setting as `block` whatever its value
- Probed at HEAD: a fixture story whose two criteria both stay green with its change reverted was moved In Progress -> Done by `transition.py set` with exit 0. `verify_ac.py revert-check` refused the same unit with exit 1.
- Base: `--base`, else `run_state.unit_base_ref` from G12 (the base of the run whose batch names the unit, open or closed; else the unit's `Small-change` base; else empty, which means not judged). `revert_check` keeps no fallback of its own: G12 AC4 removes the fallback to `run_state.base_ref` (verify_ac.py:4123). If the transition finds no base, it reports not judged before calling `revert_check`.
- `revert_check` returns a machine-readable `cause` with every not-judged result, so the lane separates permanent from transient causes without parsing prose (LL0042). Permanent causes, which proceed: no production file (a directory in Affects included), no base, and an empty revert (BG1009, the BUILT-NOT-CLOSED case). Transient causes, which refuse under `block`: a held window (BG1014) and a timed-out verifier (BG1009). Under `report`, every cause is printed and the unit proceeds.
- The lane fires when a unit enters a delivered terminal (`sdlc_md.is_delivered_terminal`) from a status that is not one: Done for a story; Fixed, Verified or Closed for a bug. So Open -> Closed cannot skip it, and Fixed -> Verified does not re-run it. This differs from the unanswered-REJECT guard, which also fires on Fixed -> Verified (transition.py:1019-1027).
- On a dry run the lane does not revert; it reports 'not previewed', unless its caller passes the judge flag. The story about the close and the sign threads that flag and tests every preview caller.
- Default: config-defaults.yaml ships `review.revert_check: report` (question 2). This repository's own sdlc-studio/.config.yaml sets `block`, so the yield is measured where the tool is dogfooded. The mode reader mirrors `line_coverage_mode`.
- Rule 21 is reworded without naming `transition.py`, and it keeps the word 'mutant', to satisfy `test_lean_no_repair_mutation_gate.py` (US0935 AC3). Proposed wording: 'A unit's terminal status change reverts its production change and refuses it when none of its criteria goes red; a mutant is still measured on demand, never demanded.' The rewording is conditional on the operator's ruling (question 1).
- The yield, stated exactly (LL0056). CR0624 relays that a consuming project rejected 11 of 18 units at least once, for any reason; reviewers there found tests that passed with the behaviour removed, and how many is not counted. BG0593 was found by a hand deletion on RUN-01M0CT8P, and revert-check was built afterwards (CR0547). The retired lane's 18 would-refuse in 730 examinations is unaudited, and it came from an instrument that refuses an empty revert (BG1009). On RUN-01M40TSJ the shipped CLI refused 0 of 19 units: 15 passed and 4 were not judged (panel).
- Retires nothing yet. The reviewer's hand revert stays in the brief's standing practices (critic.py:2200-2233) until the follow-up after G6 and G10 (question 4). The licence is therefore the yield alone, which is why the yield count comes first.
- Docs ship in the same commit (LL0004): reference-verify.md (Gated Completion); help/verify.md (a gate paragraph after BG1009's verdict section); reference-config.md; config-defaults.yaml; and the toolchain runbook's 'Change status' row. Do not name the lane in gate.py, .githooks/pre-push, tools/enable-hooks.sh or help/gate.md (test_lean_revert_lane_retired.py pins those).
- Fixtures run `verify_ac.py run` first, so the Done gate's verify-report is green, then drive `transition.py` by `SCRIPTS / "transition.py"` (BG1000).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G7 after the refine panel's review |
