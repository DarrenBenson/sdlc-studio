# US0566: Feature work keeps the cheaper bar, and a repair with no mutatable surface RECORDS that rather than being silently exempt

> **Status:** Ready
> **Delivers:** CR0501
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0191
> **Depends on:** BG0533
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** maintainer who has to keep the gate switched on
**I want** feature work held to the existing cheaper bar, and a repair with no mutatable surface to record that fact
**So that** the requirement stays affordable rather than being turned off wholesale, and an exemption is stated evidence rather than a silent gap

## Acceptance Criteria

### AC1: feature work is not held to the repair bar

- **Given** a story delivering new capability, with no mutation record
- **When** `transition.py set --id <story> --status Done` runs and every other Done gate is satisfied
- **Then** it proceeds, because the scope of the demand is the repair class the evidence indicts and a blanket requirement on all work is the one that gets switched off for cost
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RepairScopeTests::test_a_feature_story_is_not_held_to_the_repair_bar

### AC2: the repair class is read from the artefact, not inferred from prose

- **Given** four units: a bug, a story whose parent is a review-residue finding, a regression fix, and an ordinary feature story
- **When** each is classified
- **Then** the first three are typed as repairs from their recorded type and provenance fields and the fourth is not, with the classification derived from the artefact's own metadata rather than keyword-matched against its title or summary
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RepairScopeTests::test_the_repair_class_is_derived_from_metadata_not_prose

### AC3: a repair with no mutatable surface records the exemption with its reason

- **Given** a repair whose entire change is a markdown file or a single constant, so mutant generation yields nothing
- **When** the transition runs
- **Then** it proceeds only after writing a durable no-mutatable-surface record naming the unit, the changed paths and why no mutant could be generated, so the artefact says an absence was established rather than leaving the reader unable to tell it from a skipped run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::NoSurfaceExemptionTests::test_a_no_surface_repair_records_the_exemption_and_its_reason

### AC4: the exemption is verified, never taken on the author's word

- **Given** a repair that changed a Python function, accompanied by a hand-written no-mutatable-surface record claiming there was nothing to mutate
- **When** the transition runs
- **Then** it refuses, because the exemption is re-derived from the unit's changed lines and the claim contradicts a surface the generator can demonstrably mutate. An exemption an author can assert is the gate's own fail-open
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::NoSurfaceExemptionTests::test_a_claimed_exemption_over_a_mutatable_surface_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
