# US0874: A persona seat answers the run's questions and cites precedent, so the operator is not asked

> **Status:** Done
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_rulings.py, .claude/skills/sdlc-studio/help/decisions.md
> **Epic:** EP0260
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator who wants to be asked only what needs a human
**I want** persona seats to rule on the run's questions and cite their precedents
**So that** the run keeps going and the same question is never asked twice

## Acceptance Criteria

- **AC1:** Given decisions.py rule with a seat, a subject key, a question, a ruling and a reason, when it runs, then a decision is recorded Accepted with its seat and subject retrievable, and its id is printed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_rulings.py::RuleTests::test_a_ruling_is_recorded_with_seat_and_subject
  - **Verified:** yes (2026-09-23)
- **AC2:** Given recorded rulings, when decisions.py precedent runs with a subject and question text, then accepted non-superseded rulings with that subject come first, then keyword matches across the whole log including rows written before subjects existed, at most 3
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_rulings.py::PrecedentTests::test_precedent_ranks_subject_then_keywords
  - **Verified:** yes (2026-09-23)
- **AC3:** Given a precedent exists for the subject, when rule runs with neither --cites nor --differs, then it is refused and prints the precedents; with --cites Dxxxx no new decision is written and the cited ruling is printed; with --differs REASON a new ruling is written naming the precedent it departs from
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_rulings.py::RuleTests::test_a_precedent_must_be_cited_or_departed_from
  - **Verified:** yes (2026-09-23)
- **AC4:** Given an open run, when a ruling is recorded or a precedent cited, then run state key rulings counts it as persona, and a decision added by the operator counts as operator - the counts the report shows
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_rulings.py::RulingCountTests::test_the_run_counts_persona_and_operator_rulings
  - **Verified:** yes (2026-09-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
