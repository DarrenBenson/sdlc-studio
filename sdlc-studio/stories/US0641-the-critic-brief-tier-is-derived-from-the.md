# US0641: The critic brief tier is derived from the risk band, recorded on the verdict, and read by the coverage predicate

> **Status:** Ready
> **Delivers:** CR0510
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/conformance.py,.claude/skills/sdlc-studio/scripts/tests/test_critic.py,.claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Epic:** EP0208
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The critic brief tier is derived from the risk band, recorded on the verdict, and read by the coverage predicate
**So that** CR0510 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the tier is derived from the risk band, not defaulted

- **Given** two units that band differently under `route.estimate`
- **When** `critic.py brief` is invoked on each with no `--tier`
- **Then** the low-banding unit briefs at `light` and the high-banding one at `full`, and the mapping from band to tier is a single declared table rather than a chain of conditionals
- **Mutant:** keep the `full` default and ignore the band - both briefs come back full and the tiering is cosmetic exactly as it is today
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefTierTests::test_the_tier_is_derived_from_the_band_when_none_is_given

### AC2: an unresolvable band tiers full, never light

- **Given** a unit whose estimate raises or returns no band
- **When** the tier is derived
- **Then** it is `full`, because the direction an unknown risk must fail in is the strict one
- **Mutant:** treat a missing band as low - an unestimable unit gets the lighter review
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefTierTests::test_an_unresolvable_band_tiers_full

### AC3: the tier is recorded on the verdict as a parsed field

- **Given** a verdict recorded after a briefed review
- **When** it is read back through the shipped reader
- **Then** the tier is a field of the returned record, not a phrase inside free text, and a verdict written without one reads as absent rather than as `full`
- **Mutant:** write the tier into the issues prose - the field is empty and the read-back assertion reddens
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefTierTests::test_the_tier_is_a_parsed_field_on_the_verdict

### AC4: coverage reads the tier - a light verdict does not cover a unit the band tiers full

- **Given** a high-banding unit carrying an APPROVE recorded at `light`
- **When** the coverage predicate is asked whether the unit is reviewed
- **Then** it answers no and names the tier shortfall
- **Mutant:** ignore the tier in coverage - the light verdict reads as coverage and the whole wiring buys nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::TierCoverageTests::test_a_light_verdict_does_not_cover_a_full_tier_unit

### AC5: a tier-less historical verdict still covers, so the change is not retrospective

- **Given** an APPROVE recorded before this change, carrying no tier
- **When** coverage is evaluated
- **Then** it still covers, because a rule applied backwards would re-open every closed unit in the corpus
- **Mutant:** treat absent as light - historical verdicts on high-band units stop covering
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::TierCoverageTests::test_a_verdict_recorded_without_a_tier_still_covers

### AC6: an explicit `--tier` overrides the derivation and the record says which it was

- **Given** `--tier full` passed on a low-banding unit
- **When** the review is briefed and its verdict recorded
- **Then** the brief is full and the record distinguishes an operator's choice from a derived tier
- **Mutant:** let the derivation win over the flag - the operator cannot ask for a deeper pass than the band demands
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefTierTests::test_an_explicit_tier_overrides_the_derivation_and_is_recorded_as_explicit

### AC7: the bands this corpus actually produces are asserted, so the tiering is not a no-op

- **Given** every story and bug in this repository
- **When** each is banded
- **Then** the distribution spans more than one band and the test states the counts, because a band that always resolves the same way is a config key wearing the appearance of a gate
- **Mutant:** widen the low threshold until nothing bands low - the distribution assertion reddens
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefTierTests::test_the_corpus_spans_more_than_one_band

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
