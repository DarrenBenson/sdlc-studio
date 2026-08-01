# US0567: The shipped doctrine states that a fix's author is not sufficient evidence for that fix, so a consuming project inherits the mechanism not only the lesson

> **Status:** Draft
> **Delivers:** CR0501
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/reference-agentic-lessons.md, tools/tests/test_doctrine_repair_evidence.py
> **Epic:** EP0191
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** maintainer of a project that installs this skill
**I want** the shipped doctrine to state that a fix's author is not sufficient evidence for that fix, and to name the mechanism that enforces it
**So that** a consuming project inherits the gate and not merely the lesson, which is what it inherits today

## Acceptance Criteria

### AC1: the doctrine states the rule and names the mechanism that acts on it

- **Given** `reference-doctrine.md` as shipped, which today contains no mention of mutation or of author-written evidence
- **When** the repair-evidence rule is added to it
- **Then** the passage states the rule, states why the repair class specifically carries it, and names the transition gate as what enforces it, so a reader arrives at a mechanism rather than at advice
- **Verify:** pytest tools/tests/test_doctrine_repair_evidence.py::DoctrineTests::test_doctrine_states_the_rule_and_names_the_enforcing_gate

### AC2: the definition-of-done template carries the clause

- **Given** `templates/core/definition-of-done.md`, which a consuming project copies as its own Done contract
- **When** it is read
- **Then** it carries a repair-evidence clause consistent with the shipped gate, phrased tool-neutrally and without an internal provenance tag, so `tools/lint-style.sh` stays green on a consuming-facing file
- **Verify:** bash tools/lint-style.sh

### AC3: the guard discriminates, and its own Revision History cannot satisfy it

- **Given** a guard asserting the doctrine carries this rule
- **When** the stating passage is deleted while every other line of the file, including the Revision History row describing this change, is left intact
- **Then** the guard goes red. It anchors on the passage in its own section rather than on a whole-file substring, because a whole-file `assertIn` satisfied by the row describing the change is exactly the defect BG0457 records, and a guard shipped in the same change that introduces the prose is the easiest place to repeat it
- **Verify:** pytest tools/tests/test_doctrine_repair_evidence.py::DoctrineTests::test_deleting_the_stating_passage_reddens_the_guard

### AC4: the carried lesson points at the mechanism instead of restating it

- **Given** the existing carried lesson in `reference-agentic-lessons.md` that a test written by a fix's author asserts the shape of the fix
- **When** the doctrine passage lands
- **Then** the lesson cites the gate rather than repeating the advice, so the two cannot drift into disagreeing about what is required
- **Verify:** pytest tools/tests/test_doctrine_repair_evidence.py::DoctrineTests::test_the_carried_lesson_cites_the_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
