# US1018: The close and the sign judge each unit once, a preview never reverts, and the sign prints what the transition reported

> **Status:** Draft
> **Delivers:** CR0624
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_close_sign_revert_gate.py, changelog.d/US1018.md
> **Epic:** EP0281
> **Points:** 5
> **Depends on:** US1017
> **Persona:** Maya Okafor

## User Story

**As** a team lead who closes and signs a sprint of a dozen or more units
**I want** the close to record each unit's revert verdict once, every preview to leave the tree alone, and the sign to show me what each transition reported
**So that** a refusal shows up on the close's report before I sign, a dry run never rewrites a file, and a report-mode finding is not lost at the one command that closes sprint units

## Acceptance Criteria

- **AC1:** Given a unit the lane refuses, whose verifier touches a marker file, when `transition.py set --dry-run`, `transition.py requirements` and `sprint.py close --dry-run` each preview it, then no production file's bytes or mtime change, the marker is absent, and each output names the lane as not previewed together with `verify_ac.py revert-check --unit <id>`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_sign_revert_gate.py::CloseSignRevertGateTests::test_no_preview_reverts_and_each_says_not_previewed
- **AC2:** Given a run whose batch holds a unit the lane refuses, when `sprint.py close` prepares it, then the report's terminal-gate hold names that unit's revert-check refusal, and the unit's verifier ran against the reverted file exactly once during the close.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_sign_revert_gate.py::CloseSignRevertGateTests::test_the_close_judges_each_unit_once_and_holds_the_refusal
- **AC3:** Given a closed run awaiting its signature whose batch holds a reviewed story the lane refuses under `block`, when `sprint.py sign` runs, then it stops at that story, naming the revert-check refusal, and moves nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_sign_revert_gate.py::CloseSignRevertGateTests::test_sign_stops_at_a_unit_whose_criteria_pass_without_the_change
- **AC4:** Given `review.revert_check: report` and a reviewed unit the lane would refuse under `block`, when `sprint.py sign` moves it to Done, then the sign's output carries the transition's revert-check line for that unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_sign_revert_gate.py::CloseSignRevertGateTests::test_the_sign_prints_what_each_transition_reported

## Notes

- Release: later (D0355 breakdown G7, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: let a dry run revert like a real transition, so the marker appears and the mtime moves
- AC2 must fail on: judge the revert in both `_report_holds` and the `report_gate_clear` call, so it runs twice; or in neither, so there is no hold
- AC3 must fail on: delete the run fallback from `run_state.unit_base_ref`, so a unit at the sign has no base and is never judged; `revert_check` keeps no fallback of its own to mask this
- AC4 must fail on: `_seal_units` discards the transition's result, as it does at HEAD (sprint.py:6182, 6186)
- Preview callers that reach the ladder on a dry run, and so say 'not previewed':
- `close_preflight`, via `_seal_preview` and `_done_gate_preflight` (sprint.py:7224, 7245).
- `build_gate_briefing`, via `transition.requirements`, which `sprint plan` calls on an open run (sprint.py:4321, 4359).
- `close --dry-run`, whose contract is that a preview writes nothing (sprint.py:7336).
- `transition set --dry-run` and `transition requirements`.
- The one opt-in is `_report_gate_verdicts` (sprint.py:9336). It passes the judge flag through `artifact.close(dry_run=True)` once per close invocation, and the same result serves both the terminal-gate hold (sprint.py:9264, 9405) and `report_gate_clear` (sprint.py:9300). That is one measurement inside one command, not a verdict reused across commands, so D0180 holds. The sign then judges for real.
- Measured cost (panel, RUN-01M40TSJ): one revert pass over 19 units took 369 seconds, 147 of them for BG0938. So the close and the sign each add about 6 minutes on a batch that size, against about 18 minutes for the close if all three preview paths reverted.
- A refusal first shows on the close's report, as a known issue in the terminal-gate hold (sprint.py:9264-9276), and the sign then refuses. Both come after review, which is why the lane-return story exists.
- The verifier that counts runs appends a line only when it sees the base bytes. That way the close's own verify pass over the batch does not add to the count.
- Sized at 5, not the panel's 3. It has four CLI criteria, each over a close or sign fixture: the heaviest fixtures in the suite (test_lean_close.py, test_lean_sign.py builds whole runs and recorded reviews). It also threads a judge flag through `artifact.close` and `transition`, and splits one verdict between two consumers. For comparison, US0816 (the coverage gate) was 8 points. Drive the CLIs by `SCRIPTS / "sprint.py"`. Copy fixture shapes rather than importing another test module (BG1000).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G7 after the refine panel's review |
