# US1199: The mutation probe drops each conjunct of a guard and flips polarity words in a document a test reads

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0673
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Epic:** EP0327
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The mutation probe drops each conjunct of a guard and flips polarity words in a document a test reads
**So that** CR0673 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Drop-conjunct removes each operand of a guard in turn

- **Given** a Python file holding `if a and b and c:`, an `or` guard of two operands and a guard of one operand, with a test that passes when `b` is dropped (US1117's M11)
- **When** `mutation.py run --files <file> --test <cmd>` is run
- **Then** the report lists one drop-conjunct mutant per operand of each `and` and `or` guard (three and two), none for the single-operand guard, the mutant that drops `b` as survived and the others as killed, and the file is byte-identical afterwards. Fails on: a probe that only inverts the whole guard, so a conjunct no test pins is never reported
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DropConjunctTests::test_each_operand_is_dropped_in_turn_and_an_unpinned_one_survives

### AC2: Flip-polarity inverts a rule in a document a declared test reads

- **Given** a unit whose Affects names a `.md` file and a test that reads it with a pattern accepting the inverted rule (US1120's `only while` with no `below`)
- **When** `mutation.py run --story <id> --test <cmd>` is run
- **Then** the report lists a flip-polarity mutant for each of below and above, only and also, never and always, must and may, and `not` removed, wherever the document holds the word, and reports the flip of `below` to `above` as survived. Fails on: a probe that mutates no markdown, so a doc-pin test that cannot fail on the inverted rule passes unnoticed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::FlipPolarityTests::test_an_inverted_rule_the_test_accepts_is_reported_as_a_survivor

### AC3: Flip-polarity leaves alone what no declared test reads, and whole words only

- **Given** a `.md` file in the unit's Affects that no declared test reads, and a read one holding `mustard`, `cannot` and `notice`
- **When** `mutation.py run --story <id> --test <cmd>` is run
- **Then** the unread document yields no mutant and is named with the reason it was skipped, and the read one yields no mutant inside `mustard`, `cannot` or `notice`. Fails on: mutants spent on a document no test could kill, or a word mutated inside a longer word
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::FlipPolarityTests::test_an_unread_document_and_a_partial_word_yield_no_mutant

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
