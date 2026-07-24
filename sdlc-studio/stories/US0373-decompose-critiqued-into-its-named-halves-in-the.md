# US0373: decompose critiqued into its named halves in the report and correct the remedy line

> **Status:** Review
> **Delivers:** CR0368
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0132
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py

## User Story

**As an** operator closing a unit past the two-role cutoff
**I want** conformance to name which half of `critiqued` is unmet
**So that** I can act on the finding without reading the composition logic in the source

## Acceptance Criteria

### AC1: the unmet half is named, not the composite stage

- **Given** a Done unit past `review.two_role_after` with an independent APPROVE verdict and an
  adversarial pass recorded, but no reviewer-of-record sign-off
- **When** `conformance.py check` reports it
- **Then** the output names the reviewer-of-record sign-off and does NOT name the two halves that
  are satisfied - naming all three whenever any is unmet would pass a weaker check while
  misdirecting exactly as the composite did
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::CritiquedHalvesTests::test_only_the_signoff_missing_names_the_signoff_not_the_composite
- **Verified:** yes (2026-07-24)

### AC2: every unmet half is named on one line, not just the first

- **Given** a Done unit past the cutoff with no verdict, no evidence and no sign-off
- **When** `conformance.py check` reports it
- **Then** all three halves appear on that unit's single line - the composition short-circuited on
  the first failure, so an operator repairing what it named met the gate again and was refused
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::CritiquedHalvesTests::test_several_unmet_halves_are_all_named_in_one_line
- **Verified:** yes (2026-07-24)

### AC3: a satisfied critiqued stage is unchanged

- **Given** a Done unit past the cutoff with verdict, evidence and an independent sign-off all
  recorded
- **When** conformance runs
- **Then** the unit is conformant, `critiqued` is absent from `missing`, and no half is named - the
  change is diagnostic detail, never a new refusal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::CritiquedHalvesTests::test_a_satisfied_critiqued_stage_stays_conformant_and_names_nothing
- **Verified:** yes (2026-07-24)

### AC4: the remedy line stops pointing at the wrong gate

- **Given** a run whose only non-conformance is `critiqued`
- **When** the guidance and the gate one-liner are printed
- **Then** neither offers the `verify_ac` back-annotation remedy, which clears the VERIFIED stage;
  it is still offered when a unit genuinely misses `verified`, so the lever is aimed rather than
  deleted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::CritiquedHalvesTests -k remedy
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
