# US1069: The close runs each traced persona's executable End goal Verify and records the result beside the goal verdict

> **Status:** Draft
> **Delivers:** CR0629
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_goal_verdict_end_goal_evidence.py, changelog.d/US1069.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1040
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, closing a run whose Sprint Goal traces to a persona with a testable End goal
**I want** the close to run each traced persona's executable End goal Verify and record each result beside the goal verdict, naming a red one under an achieved verdict
**So that** a goal is never closed as met while the End goal it traces to still fails without anyone being told

## Acceptance Criteria

- **AC1:** Given a goal naming Maya Okafor, whose End goal 2 carries an executable Verify that passes and End goal 4 one that fails, when `sprint.py close --goal-verdict achieved --note ...` runs, then the run record's goal verdict carries End goal 2 pass and End goal 4 fail with their selectors, and the close output names End goal 4 as red under an achieved verdict.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_verdict_end_goal_evidence.py::EndGoalEvidenceTests::test_the_close_runs_traced_end_goals_and_names_a_red_one
- **AC2:** Given End goal 1 with a manual Verify and End goal 3 with none, and an untraced persona whose End goal carries an executable Verify, when the close runs, then End goals 1 and 3 are listed as not run with the reason and the untraced persona's Verify is never executed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_verdict_end_goal_evidence.py::EndGoalEvidenceTests::test_only_traced_executable_end_goals_are_run
- **AC3:** Given an End goal whose Verify names a runner the machine lacks, when the close runs, then its result reads error with the runner's reason, distinct from pass and fail, and the close's outcome is the same as with it passing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_verdict_end_goal_evidence.py::EndGoalEvidenceTests::test_an_unrunnable_end_goal_reads_error_not_fail
- **AC4:** Given a close that recorded End goal 4 failing, when End goal 4 is repaired and the close runs again, then the record holds one result per End goal, End goal 4 now passing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_verdict_end_goal_evidence.py::EndGoalEvidenceTests::test_a_reclose_replaces_the_end_goal_results

## Notes

- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the Verify lines never run, so the verdict is judged on done_means alone as at HEAD, or a red result recorded silently under 'achieved'
- AC2 must fail on: a manual or missing check counted as passing, or every persona's End goals run whatever the goal traces to
- AC3 must fail on: an error read as a failure, which tells the operator the goal is unmet when it was never measured, or as a pass (LL0018)
- AC4 must fail on: results appended per close attempt, so the record holds a stale red beside the green
- Serves: Maya Okafor #4 (specs, code and tests never quietly drift).
- D0364 ruling 4: CR0629 joins this epic and 6.2. Checked at HEAD: `cmd_goal_verdict` (sprint.py:4574) and the close (:9181-9200) record the verdict word and note only; nothing reads an End goal's Verify, which US1039 introduces.
- Strength: reported by name, as CR0629's own criterion says ('reported by name rather than read as met'). No refusal: none has a measured yield yet (LL0056); the close and the report put the red result in front of the signer.
- One executor: `verify_ac.run_verifier` (verify_ac.py:498), the runner AC Verify lines use, with its timeout. The traced personas and their executable End goals come from US1040's `goal_trace` (including `--serves`, after BG1002); a manual Verify is never run, as US1040 never counts it.
- Results go beside the verdict in `sprint_goal_verdict` via `run_state.record_goal_verdict` (run_state.py:1567), so the tracked record carries them (a key the annex tolerates, US0994).
- Builds after US1040 and before the served-goal story, which records these results in the persona's memory.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1040, and through it on US1039, which adds End goal Verify lines and lib/persona_goals.py. Today no persona card in this repository carries an End goal Verify (maya-okafor-founder-engineer.md:24-31), so there is nothing to run here until a card gains one
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
