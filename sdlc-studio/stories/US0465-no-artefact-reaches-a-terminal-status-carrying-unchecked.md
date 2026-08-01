# US0465: No artefact reaches a terminal status carrying unchecked Open Questions, and the 16 that already did are swept

> **Status:** Done
> **Delivers:** CR0438
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, sdlc-studio/stories/US0001-reconcile-census-autofix.md, sdlc-studio/stories/US0002-verify-ac-gate.md, sdlc-studio/stories/US0003-review-cadence.md, sdlc-studio/stories/US0004-status-hint.md, sdlc-studio/stories/US0005-next-id-allocation.md, sdlc-studio/stories/US0288-close-owed-treats-a-missing-velocity-row-as.md, sdlc-studio/stories/US0289-backfill-the-velocity-record-from-retro0029-marking-unmeasurable.md, sdlc-studio/stories/US0290-each-plan-re-measures-the-rate-from-the.md, sdlc-studio/stories/US0291-derive-shared-file-clusters-from-the-files-a.md, sdlc-studio/stories/US0292-report-an-affects-line-the-unit-s-own.md, sdlc-studio/stories/US0297-the-plan-puts-the-sprint-goal-to-the.md, sdlc-studio/stories/US0298-a-goal-unreachable-by-construction-is-detected-and.md, sdlc-studio/stories/US0299-the-loop-continues-while-any-unit-the-pending.md, sdlc-studio/stories/US0300-a-stop-names-what-could-have-proceeded-so.md, sdlc-studio/epics/EP0010-skill-self-improvement-token-economy-learning-loop-consuming.md, sdlc-studio/change-requests/CR0019-progressive-disclosure-archived-indexes.md, CHANGELOG.md
> **Epic:** EP0169
> **Points:** 5

## User Story

**As an** engineer reading a Done story or a Superseded CR
**I want** its Open Questions resolved with a recorded ruling or filed as follow-up work before it goes terminal
**So that** terminal means the question was answered, not that the answer stopped being asked for

## Acceptance Criteria

### AC1: AC1: validate flags a terminal artefact with unchecked questions

- **Given** a Done story with two unchecked items under an Open Questions heading, and a story whose items are all checked
- **When** `validate.py check` runs over each
- **Then** each unchecked item is reported as an error quoting its text, and the clean story passes, so the finding is the item and not merely the presence of a heading
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::OpenQuestionsTests::test_validate_ITSELF_reports_the_finding_not_only_the_helper
- **Verified:** yes (2026-07-29)

### AC2: AC2: the terminal transition refuses, naming both ways out

- **Given** a story in Review carrying an unchecked Open Questions item
- **When** `transition.py` moves it to Done
- **Then** the move is refused, nothing is written to the file or the index, and the refusal names both routes - a ruling recorded under Resolved Questions, or the question filed as a follow-up artefact
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::OpenQuestionsGateTests::test_a_terminal_move_is_refused_while_a_question_is_unchecked
- **Verified:** yes (2026-07-29)

### AC3: AC3: both resolution routes are accepted, and a tick with no destination is not

- **Given** one artefact whose question moved under Resolved Questions with a ruling, one whose question is checked off citing a filed artefact id that resolves, and one citing an id nothing in the workspace holds
- **When** each is validated and transitioned
- **Then** the first two pass and the third is refused, so the escape hatch cannot be a tick pointing at nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::OpenQuestionsGateTests::test_a_ruling_or_a_resolvable_follow_up_id_is_accepted_and_a_dangling_id_is_not
- **Verified:** yes (2026-07-29)

### AC4: AC4: the gate is type-general and both callers agree from one helper

- **Given** fixture artefacts of every type in `sdlc_md.TERMINAL_STATUS` - epic, story, bug, cr, rfc, issue, test-spec, workflow - in each of their terminal statuses
- **When** the offending items are computed through validate and through the transition gate
- **Then** both return identical items for every fixture because both call one helper in `lib/sdlc_md.py`, and every terminal status is derived from the map rather than from an enumerated Done, so a CR reaching Superseded is held to the same rule as a story reaching Done
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::OpenQuestionsTests::test_the_GATE_refuses_every_terminal_status_not_only_Done
- **Verified:** yes (2026-07-29)

### AC5: AC5: the whole workspace is swept, not just the stories

- **Given** the artefacts that reached a terminal status carrying unchecked questions - 14 stories, EP0010 at Done and CR0019 at Superseded
- **When** the check is run over `sdlc-studio/stories`, `sdlc-studio/epics`, `sdlc-studio/change-requests`, `sdlc-studio/bugs` and `sdlc-studio/rfcs`
- **Then** none remains: each question carries a recorded ruling or a follow-up artefact id that resolves, and the sweep enumerates the directories from the type map rather than a list of the 16 filenames, so an offender in a type nobody thought about is still caught
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::OpenQuestionsTests::test_no_terminal_artefact_in_the_workspace_carries_an_unresolved_question
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
