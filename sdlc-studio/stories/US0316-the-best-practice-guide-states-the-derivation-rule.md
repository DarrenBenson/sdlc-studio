# US0316: The best-practice guide states the derivation rule and names its counter-example: an enumeration of spellings is a restatement wearing a function's clothes

> **Status:** Review
> **Depends on:** BG0265, BG0256
> **Delivers:** CR0394
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/best-practices/script.md,.claude/skills/sdlc-studio/best-practices/documentation.md,.claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py
> **Epic:** EP0107
> **Points:** 2

## User Story

**As an** author writing a guard, gate or check that prints a sentence about what it will
do
**I want** the script and documentation guides to state that such a sentence is computed
from the guard's own predicate, and to name the enumeration that impersonates a derivation
**So that** the next author repairing a wrong message reaches for a probe instead of
writing a sixth corrected list

## Context

CR0394's evidence: the `window open` sentence was wrong five times in one sprint, and
every one of the five was an independent restatement of a rule living in code elsewhere.
The same class produced a documented config key no code read (BG0250) and a docstring
naming an opt-out that did nothing.

The guides are prose, so the guarantee available here is the one
`test_docs_single_writer.py` already establishes for `reference-sprint.md`: the statement
is present, and no sentence in the file asserts its opposite. That is a polarity scan over
named topics, not a semantic proof, and nothing below should be read as claiming more.
What raises it above a `grep` is AC3, which holds the rule to itself: one statement, one
place, reached by a link rather than copied.

## Acceptance Criteria

### AC1: the script guide states the rule, and prose denying it fails wherever it sits

- **Given** `best-practices/script.md`, which every author writing a user-facing guard
  message reads
- **When** the doc-invariant check runs over it
- **Then** the rule sentence is required present, and every sentence in the file about a
  guard's message is read for polarity, so prose asserting that a hand-written message
  beside the predicate is acceptable FAILS the check wherever it is appended - the state
  before this story, where the guide says nothing about it, fails on the required half
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py::DerivationRuleStatedTests::test_the_script_guide_states_the_rule_and_no_sentence_denies_it
- **Verified:** yes (2026-07-23)

### AC2: the counter-example is named in both halves, and half of it fails

- **Given** the guide's counter-example - an enumeration of spellings is a restatement
  wearing a function's clothes, and probing the real predicate is what makes it a
  derivation
- **When** the check runs over a version naming only the enumeration, and over one naming
  only the probe
- **Then** each fails, because the enumeration alone reads as "list the cases carefully"
  and the probe alone gives an author no way to recognise the shape they are writing;
  only the guide carrying both passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py::CounterExampleTests::test_either_half_of_the_counter_example_alone_fails
- **Verified:** yes (2026-07-23)

### AC3: the rule is stated once and pointed at, not copied into the second guide

- **Given** `best-practices/documentation.md`, which covers the same failure for prose
- **When** the check runs over both guides together
- **Then** the rule sentence appears exactly once across the two, and `documentation.md`
  reaches it by a link whose anchor resolves in `script.md`, so a second copy cannot drift
  from the first - the rule applied to its own statement
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py::OneStatementTests::test_the_rule_is_stated_once_and_the_documentation_guide_links_to_it
- **Verified:** yes (2026-07-23)

## Open Questions

- Whether the polarity axes for this rule live in the new module or are folded into
  `test_docs_single_writer.py`'s `POLARITY_AXES`. BG0258 is rebuilding that module's
  disclosure and a fold-in before it lands would collide.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
