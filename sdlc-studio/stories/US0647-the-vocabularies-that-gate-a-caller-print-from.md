# US0647: The vocabularies that gate a caller print from the constant that enforces them

> **Status:** Ready
> **Delivers:** CR0535
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Epic:** EP0210
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The vocabularies that gate a caller print from the constant that enforces them
**So that** CR0535 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the refusal prints from the enforcing constant

- **Given** a verb refusing a value outside its vocabulary
- **When** the refusal is read
- **Then** the accepted set is rendered from the same constant the check uses - a copy in the message is a second source of truth for one fact
- **Mutant:** hard-code the list in the message - it is right until the constant grows, and nothing reddens when it does
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VocabularyFromTheConstantTests::test_the_refusal_renders_the_enforcing_constant

### AC2: adding a value changes the message with no edit

- **Given** a vocabulary that gains a member
- **When** the same refusal is produced
- **Then** the new member appears in the message automatically
- **Mutant:** keep the message list separate - the two disagree the moment either moves
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VocabularyFromTheConstantTests::test_a_new_member_appears_without_an_edit

### AC3: every gating vocabulary is covered, and the uncovered are named

- **Given** the shipped scripts
- **When** the vocabularies that gate a caller are enumerated
- **Then** each either renders from its constant or is NAMED as not doing so - an enumeration that silently omits what it forgot is the failure this repository files hardest against
- **Mutant:** report only the covered ones - the count looks complete and the gaps are invisible
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::VocabularyFromTheConstantTests::test_uncovered_vocabularies_are_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
