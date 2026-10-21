# US1073: A user persona writes its learning from its usage evidence, approved by a seat, and the goal review carries it

> **Status:** Draft
> **Delivers:** CR0634
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/scripts/tests/test_user_persona_learning.py, changelog.d/US1073.md
> **Epic:** EP0287
> **Points:** 3
> **Depends on:** US1072, US1066, US1068, US1056, US1040
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose persona cards are read at planning and then sit still
**I want** `persona_memory.py learn-brief --persona <card>` to brief a user persona with its observed outcomes and recorded feedback, its learning to go through the same propose, approve and signature steps as a seat's, and the goal-review brief to carry it beside that persona's End goals
**So that** what a persona learns from how the work served it reaches the next goal review

## Acceptance Criteria

- **AC1:** Given Maya's memory holding two observed entries and one added with `--evidence` citing a stakeholder consult's artefact, and Jonah's holding one observed entry, when `persona_memory.py learn-brief --persona maya-okafor-founder-engineer` runs, then the brief frames Maya's card and lists her three entries and nothing of Jonah's.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_user_persona_learning.py::UserPersonaLearningTests::test_the_learning_brief_carries_the_personas_own_usage_evidence
- **AC2:** Given Maya's learning proposed, approved by `Lena Marsh (product)` and listed by a signed close, when `sprint.py goal-review brief --goal` runs on a goal naming Maya, then her learning is carried beside her End goals and her observed entries are not, and on a goal naming only Jonah it is not carried.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_user_persona_learning.py::UserPersonaLearningTests::test_the_goal_review_carries_a_traced_personas_live_learning
- **AC3:** Given a user persona with no observed or added entry, when `persona_memory.py propose --persona jonah-reyes-team-lead --from-file <path>` runs, then it exits 2 naming that the persona has no usage evidence to learn from.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_user_persona_learning.py::UserPersonaLearningTests::test_a_persona_with_no_usage_evidence_cannot_propose

## Notes

- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the brief reads every user persona's memory, or only observed entries, so recorded feedback is lost
- AC2 must fail on: the goal review carries every persona's learnings, or carries observed entries as if they were learnings
- AC3 must fail on: a user persona proposes with nothing behind it, the same unevidenced learning the seat path refuses
- Serves: Maya Okafor #4.
- D6: seats first, then user personas from usage evidence.
- Stakeholder feedback (RFC0058) enters as `persona_memory.py add --evidence <artefact>` on the artefact that holds the consult; no automatic reader (out of scope).
- Reuses the seat path's propose, approve and signature with `--persona <card stem>`; any seat may approve. The renderer is the memory brief story's, keyed by the card stem.
- Edits the goal-review listing after US1040 and the traced-card refusal story.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1072, US1066, US1068, US1056 and US1040 (all Draft)
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
