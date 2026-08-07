# US0658: Every reference over the stated threshold carries a Reading Guide with an anchor and a line span

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/docgen.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-decisions.md, tools/check_budgets.py, .claude/skills/sdlc-studio/scripts/tests/test_docgen.py, tools/tests/test_check_budgets.py
> **Epic:** EP0211
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Every reference over the stated threshold carries a Reading Guide with an anchor and a line span
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: every reference over the threshold carries a GENERATED Reading Guide

- **Given** the 26 `reference-*.md` files over 400 lines, of which exactly THREE carry a Reading
  Guide today - `reference-cr.md`, `reference-epic.md` and `reference-story.md` - and 23 carry
  none, `reference-sprint.md` at 827 lines among them
- **When** `docgen.py reading-guides` runs
- **Then** all 26 carry one, inside generation markers, and the three hand-written ones are
  replaced by generated equivalents so there is one shape rather than two. The count is DERIVED
  from the threshold in the test rather than typed, and pinned by a second assertion that at
  least one file which previously had none now has one - a derived count alone cannot catch the
  mutant that generates only where a guide is absent, because every file still carries something
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReadingGuideTests::test_every_reference_over_the_threshold_has_one

### AC2: each entry carries a LINE SPAN, not only an anchor

- **Given** a generated guide
- **When** an agent reads it
- **Then** each section entry carries its start and end line, so a partial read is
  `Read(offset, limit)` rather than a grep. That is strictly more than the 9 hand-written guides
  offer, and it is the difference between a table of contents and something that saves a read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReadingGuideTests::test_each_entry_carries_a_line_span

### AC3: the spans are TRUE of the file, and stay true when it changes

- **Given** a reference whose sections have moved since its guide was generated
- **When** `docgen.py reading-guides --check` runs
- **Then** it reports the drift, AND reports none over a reference whose sections have not
  moved - the silent case is the positive control, without which a checker that always reports
  drift passes the first half
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docgen.py::ReadingGuideTests::test_a_moved_section_is_reported_as_drift

### AC4: no file is split and no budget is raised to fit the guide

- **Given** the guides add roughly 15 lines to each of 26 files, several already inside the
  budget tolerance
- **When** the budgets are checked afterwards
- **Then** every ceiling equals the value US0657 recorded, asserted against a pinned expected
  set. Asserting only that the budgets PASS is the wrong direction: raising a ceiling makes them
  pass more easily, so the mutant this criterion is about would strengthen its own test.
  Splitting a reference to fit a guide would be the tail wagging the dog, and raising a ceiling
  to accommodate a generator is the ratchet running backwards
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_the_recorded_ceilings_are_unchanged_by_the_guides

### AC5: a ceiling justification that names a Reading Guide must have one, and it does

- **Given** `reference-sprint.md`'s budget justification, which asserts a Reading Guide twice
  over a file that has none
- **When** `check_budgets.py` runs
- **Then** a justification naming a Reading Guide is required to have one in the file it
  justifies, and every justification passes - because this story generated the guides FIRST. The
  check lands here rather than in US0657 because `check_budgets.py` is a BLOCKING pre-commit
  lane: a demand that arrives one story before the thing that satisfies it leaves the trunk red
  in between, and the premise is fixed by making it TRUE rather than by deleting a sentence that
  is right about what the file needs
- **And** a positive control beside it: a justification naming a guide over a file that HAS one
  must PASS. After this story `reference-sprint.md` is the only justification naming a guide, so
  a checker that matched nothing would pass the refusal test for the wrong reason. The checker
  and the guides land in ONE commit, since the lane blocks
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_a_justification_naming_a_reading_guide_must_have_one

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | generate a guide only where one is absent, leaving the three hand-written ones as a second shape | every reference over the threshold carries one |
| AC2 | emit the anchor without the line span | each entry carries a LINE SPAN |
| AC3 | report no drift when a section has moved | the spans are TRUE of the file |
| AC4 | raise a ceiling to fit the generated guide, so the budgets pass more easily | no file is split and no budget is raised |
| AC5 | accept a justification that names a Reading Guide the file does not have | a justification naming a guide must have one |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-08 | sdlc-studio | AC5 arrives from US0657, from the plan-time engineering seat's finding: `check_budgets.py` is a blocking lane, so the demand and the thing that satisfies it must land in one commit or the trunk is red between them |
| 2026-08-08 | sdlc-studio | Plan review round 1 REJECTed on constants that were mine and wrong: 26 references exceed 400 lines and THREE carry a guide, not 27 and nine - the other six carrying the phrase sit under the threshold and are not the population. AC4's mutant made its own test pass MORE strongly, since raising a ceiling makes the budgets pass, so it asserts the recorded ceilings against a pinned set instead. AC5 gains its positive control and states that the checker and the guides land in one commit |
| 2026-08-08 | sdlc-studio | Plan review round 2 APPROVEd, ruling all three round-1 findings CLOSED. Its minors are folded in: AC4's verifier is renamed to match the pinned-set assertion it now carries rather than the exit-0 one it replaced, and AC3 gains the silent positive control |
