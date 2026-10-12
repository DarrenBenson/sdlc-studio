# US1068: A learning reaches a brief only once a signed close has listed it, and one the operator strikes at the signature never does

> **Status:** Draft
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py, changelog.d/US1068.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1067, US1059
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, the operator who signs each run
**I want** `sprint.py sign --strike M-NNNN` to strike any learning the close listed as I seal the run, and every brief to carry a learning only while the run that listed it is signed and has not struck it
**So that** no learning reaches a seat before I have had the chance to strike it, one I strike never does, and a reopened run holds its learnings until I sign again

## Acceptance Criteria

- **AC1:** Given a closed run that listed M-0001 (qa) and M-0002 (product), when `sprint.py sign --principal <operator> --strike M-0001 --strike-reason ...` runs, then the run is sealed with M-0001 recorded as struck by the principal with the date and reason, the next qa brief does not carry M-0001, the next product brief carries M-0002, and `persona_memory.py list` shows M-0001 struck.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_a_struck_learning_never_reaches_the_brief
- **AC2:** Given an approved learning listed by a run that is closed but not signed, when `critic.py brief --seat qa` runs, then the learning is not carried and the brief says one approved learning awaits its run's signature.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_a_learning_of_an_unsigned_run_is_held
- **AC3:** Given a signed run that listed M-0002, when `sprint.py reopen --reason ...` runs, then the next product brief holds M-0002, and after the close and `sprint.py sign --strike M-0002` it is struck and never carried.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_a_reopened_run_holds_its_learnings_until_resigned
- **AC4:** Given `--strike` naming a learning another run listed and an id no memory file holds, when `sprint.py sign` runs, then it exits 2 naming both, nothing is sealed and no memory file changes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_a_bad_strike_refuses_the_seal_and_writes_nothing

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the strike written only where the renderer does not read, so the struck learning still reaches the qa brief
- AC2 must fail on: approved learnings injected before the signature, so the operator's strike arrives after a seat has read the learning
- AC3 must fail on: 'signed' stamped into memory at the seal, so a reopened run's learnings stay live while the signature they relied on is broken
- AC4 must fail on: the strike checked after the seal is written, or a partial strike applied
- Serves: Maya Okafor #3.
- Checked at HEAD: `cmd_sign` (sprint.py:9708) takes no strike, and the sign refuses a tree changed since the close (`tree_moved_since_close`, :9671), so a strike made by editing the retro or memory after the close would cost a re-close.
- Live = approved, within its horizon, not retired, and its Listed-in run's tracked record (`run_state.file_tracked`, sprint.py:9809, held by every clone) is sealed and does not strike it. 'Signed' is read from that record and never written into memory, so a reopen holds the run's learnings until the re-sign, which may strike them (panel's reopen boundary).
- The struck ids are part of what the signature writes, after the page check, kept on the sealed run record (a key the annex tolerates, US0994) and not on the report, so the report's fingerprint and US0992's catalogue are untouched. Every refusal runs before anything is written.
- `cmd_sign` is also edited by US1018 (later); whichever lands second rebases.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
