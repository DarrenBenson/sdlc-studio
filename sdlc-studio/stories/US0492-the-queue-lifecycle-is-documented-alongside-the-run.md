# US0492: The queue lifecycle is documented alongside the run lifecycle, with every invocation shown taken from the shipped parser

> **Status:** Ready
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/sprint.py, tools/tests/test_help_coverage.py
> **Epic:** EP0176
> **Points:** 3

## User Story

**As a** reader looking for how to plan several sprints and run the next
**I want** the queue lifecycle documented beside the run lifecycle, with runnable invocations
**So that** the documented surface is the shipped surface, rather than something to be discovered from argparse

## Acceptance Criteria

### AC1: every queue verb the parser defines is documented

- **Given** the shipped command parser
- **When** the coverage check runs
- **Then** each queue verb the parser defines appears in the documentation, and the expected set is read from the parser rather than from a list in the check
- **Verify:** pytest tools/tests/test_help_coverage.py::QueueDocsTests::test_every_parser_verb_is_documented
- **Verified:** yes (2026-08-04)

### AC2: every invocation shown is one the parser accepts

- **Given** the invocations shown in the documentation
- **When** each is parsed by the shipped parser
- **Then** every one parses, so an example cannot document a form the command would reject
- **Verify:** pytest tools/tests/test_help_coverage.py::QueueDocsTests::test_every_documented_invocation_parses
- **Verified:** yes (2026-08-04)

### AC3: the recorded reasoning for materialising late is stated where a reader looks for a queue

- **Given** a reader arriving expecting frozen queued plans
- **When** the documentation is read
- **Then** it states that charters queue intent and the batch is resolved at start, and why - so the design answer is found rather than the absence of a feature
- **Verify:** pytest tools/tests/test_help_coverage.py::QueueDocsTests::test_the_materialise_late_reasoning_is_documented
- **Verified:** yes (2026-08-04)

## Verification evidence

Functional. Four mutants executed, source restored byte-identical after each:

| Mutant | Result |
| --- | --- |
| show an invocation the parser rejects | killed |
| name a verb in prose instead of showing it as a command | killed |
| remove the queue section's heading | killed |
| blind the derivation so no verb is expected | killed |

**Two of these SURVIVED the first draft, and the reason is the criterion itself.** AC1 says the
expected set must be "read from the parser rather than from a list in the check", and my first
version kept a hardcoded tuple of verb names - the exact defect the criterion forbids, written
into the test meant to enforce it. It now reads the parser's own help table
(`_choices_actions`), so a verb is expected because it DESCRIBES ITSELF as charter-queue work,
and one added later is covered without editing this test. `sprint call` had to say so in its own
help, which is the honest direction: the verb declares what it is, and the check reads that.

The second survivor was subtler. `queue {sub}` matched a verb NAMED in a sentence, so the page
could describe a command nobody can copy and still pass. The check now looks only at lines that
are real invocations.

Both were found by mutation rather than by review, which is the point of running the mutants on
a test whose whole subject is whether documentation can be trusted.

**The lane-check advisory on this unit is accepted, not silenced.** It fires because the unit's
`Affects` names `sprint.py` - the `call` verb had to declare itself as charter-queue work for
the derivation to see it - while none of the three verifiers calls `main()`. That is correct as
a heuristic and wrong here: this unit's subject is whether the DOCS match the PARSER, and the
tests load `build_parser()` out of the shipped script to ask it. Driving `main()` would add a
process boundary and prove nothing about the question. Recorded rather than worked around,
because a rule bent quietly is worse than one bent openly - and the alternative, dropping
`sprint.py` from `Affects`, would understate where the fix landed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
