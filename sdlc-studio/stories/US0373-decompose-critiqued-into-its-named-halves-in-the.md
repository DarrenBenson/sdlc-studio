# US0373: decompose critiqued into its named halves in the report and correct the remedy line

> **Status:** Done
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
- **Verify:** manual - retired by US0916: the evidence and sign-off halves were deleted, so critiqued names only the independent APPROVE or its depth
- **Verified:** manual (2026-09-25) - retired, superseded by US0916

### AC2: every unmet half is named on one line, not just the first

- **Given** a Done unit past the cutoff with no verdict, no evidence and no sign-off
- **When** `conformance.py check` reports it
- **Then** all three halves appear on that unit's single line - the composition short-circuited on
  the first failure, so an operator repairing what it named met the gate again and was refused
- **Verify:** manual - retired by US0916: the evidence and sign-off halves were deleted, so critiqued names only the independent APPROVE or its depth
- **Verified:** manual (2026-09-25) - retired, superseded by US0916

### AC3: a satisfied critiqued stage is unchanged

- **Given** a Done unit past the cutoff with verdict, evidence and an independent sign-off all
  recorded
- **When** conformance runs
- **Then** the unit is conformant, `critiqued` is absent from `missing`, and no half is named - the
  change is diagnostic detail, never a new refusal
- **Verify:** manual - retired by US0916: the evidence and sign-off halves were deleted, so critiqued names only the independent APPROVE or its depth
- **Verified:** manual (2026-09-25) - retired, superseded by US0916

### AC4: the remedy line stops pointing at the wrong gate

- **Given** a run whose only non-conformance is `critiqued`
- **When** the guidance and the gate one-liner are printed
- **Then** neither offers the `verify_ac` back-annotation remedy, which clears the VERIFIED stage;
  it is still offered when a unit genuinely misses `verified`, so the lever is aimed rather than
  deleted
- **Verify:** manual - retired by US0916: the evidence and sign-off halves were deleted with CritiquedHalvesTests; the backfill-remedy tests moved to test_conformance.py::BackfillRemedyTests
- **Verified:** manual (2026-09-25) - retired, superseded by US0916

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
