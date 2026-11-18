# US1231: The engineering brief carries the TRD's failure and observability checks for touched components, under a cap

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0691
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_reliability.py
> **Epic:** EP0338
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The engineering brief carries the TRD's failure and observability checks for touched components, under a cap
**So that** CR0691 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A unit touching a declared component carries that component's checks

- **Given** a project whose TRD's Reliability and Observability section declares five dependencies, and a unit whose Affects touch the component of one of them
- **When** `critic.py brief --unit <id> --seat engineering` is run
- **Then** the brief carries that component's declared failure behaviour, timeout and retry policy and the required observability patterns as checks the reviewer answers, and carries none of the other four dependencies' rows. Fails on: every dependency printed whatever the unit touches, or the declaration quoted as prose with nothing to answer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_reliability.py::BriefReliabilityChecksTests::test_a_unit_touching_a_declared_component_carries_its_checks

### AC2: A unit touching no declared component carries one line saying so

- **Given** the same project and a unit whose Affects touch no component the section names
- **When** `critic.py brief --unit <id> --seat engineering` is run
- **Then** the brief carries exactly one line saying the unit touches no component with a declared failure behaviour, and no check. Fails on: silence, which reads the same as a brief that never looked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_reliability.py::BriefReliabilityChecksTests::test_a_unit_touching_no_declared_component_carries_one_line

### AC3: A TRD without the section costs one line and no refusal

- **Given** a project whose TRD has no Reliability and Observability section, and one with no TRD at all
- **When** `critic.py brief --unit <id> --seat engineering` is run in each
- **Then** it exits 0 with the brief written, carrying one line that names the section to add to the TRD. Fails on: a refused or failed brief, or a brief that says nothing of the missing section
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_reliability.py::BriefReliabilityChecksTests::test_a_trd_without_the_section_gets_one_line_and_no_refusal

### AC4: The added checks stay under the cap and the other seats' briefs do not change

- **Given** the five-dependency fixture and a unit whose Affects touch all five components
- **When** the engineering, product and qa briefs are each printed with and without the TRD's section
- **Then** the engineering brief grows by at most 2,000 characters (500 tokens at four characters a token) and says how many declared rows it left out when the cap cuts any, and the product and qa briefs are byte-identical with and without the section. Fails on: a brief that grows with every dependency, a cut made silently, or the checks leaking into another seat's brief
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_reliability.py::BriefReliabilityChecksTests::test_the_checks_are_capped_and_other_seats_are_unchanged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
