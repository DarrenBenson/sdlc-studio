# US0317: Where a message and a verdict must agree, ONE test drives both over the same input battery and asserts they agree

> **Status:** Draft
> **Delivers:** CR0394
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/best-practices/testing.md,.claude/skills/sdlc-studio/scripts/tests/test_mutation.py,.claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py
> **Epic:** EP0107
> **Points:** 3

## User Story

**As a** reviewer deciding whether a printed sentence can be trusted
**I want** a message and the verdict it describes driven by ONE test over ONE input set,
asserting they agree
**So that** a sentence that keeps the word an assertion pinned while denying the verdict
beside it goes red, instead of passing as coverage

## Context

The live instance, measured rather than assumed: `window open`'s reason clause is asserted
by `assertIn(EXPECTED_REASON[claim], msg)`, which pins the word `glob`. Rewriting the
clause from "a glob matching every path the matcher probes" to "a glob matching no path
the matcher probes" - a sentence that denies the WHOLE TREE verdict printed in the same
line - leaves `WindowOpenMessageTests` green. Verified in a scratch copy with
`__pycache__` purged, under `python3 -B`, before this criterion was written.

That is what "assert the text separately" buys. This story builds the pattern and states
it; BG0259 applies it to that clause.

## Acceptance Criteria

### AC1: one battery drives both sides, and a side exercised over less fails

- **Given** a message and a verdict that must agree, such as `window open`'s scope
  sentence and `gate.py`'s window lane
- **When** the agreement test runs
- **Then** both are driven from ONE shared input constant, and the test fails if either
  side is exercised over a set the other is not - so neither can be selected around the
  shapes it happens to pass, which is how the previous oracle came to agree with the
  matcher only on the families it had chosen
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::MessageVerdictAgreementTests::test_one_battery_drives_both_the_message_and_the_verdict

### AC2: a derivation that keeps the pinned word but denies the verdict goes red

- **Given** a derivation deliberately inverted so its sentence contradicts the verdict
  printed beside it, while retaining every word the current assertions pin
- **When** the agreement check reads both over the shared battery
- **Then** it FAILS, naming the input whose message and verdict disagree - the inversion
  measured in Context above passes today and must not after this story
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::MessageVerdictAgreementTests::test_an_inverted_derivation_fails_even_when_it_keeps_the_pinned_word

### AC3: the testing guide states the pattern and names what it replaces

- **Given** `best-practices/testing.md`
- **When** the doc-invariant check runs over it
- **Then** the guide states that a message and a verdict which must agree are driven by
  one test over one input set, and names the counter-example it replaces - asserting the
  message's text on its own, which passes for an input the text does not describe - and a
  version stating only the pattern without the counter-example fails
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_derivation_rule.py::AgreementPatternGuideTests::test_the_testing_guide_states_the_agreement_pattern_and_names_what_it_replaces

## Open Questions

- AC1 says "fails if either side is exercised over a set the other is not". Enforcing that
  mechanically means the battery is a module constant both sides read, and a test that
  asserts neither side holds a second literal list. Whether that check belongs in
  `test_mutation.py` or in a repo-wide conformance guard is unsettled; a repo-wide one
  reaches every future pair and is out of this story's size.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
