# US0440: TRD and TSD stages: generate the technical and test-strategy docs from the PRD, draft-then-confirm

> **Status:** Review
> **Delivers:** RFC0055
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Epic:** EP0163
> **Points:** 5

## User Story

**As an** operator in guided onboarding
**I want** the TRD and TSD stages to seed the technical-design and test-strategy docs from my PRD
**So that** the test strategy the sprint plan later reads actually exists, without me knowing to write it

## Acceptance Criteria

### AC1: the TRD and TSD stages seed their docs and direct generation from the PRD

- **Given** onboarding at the TRD stage, then the TSD stage
- **When** each stage runs
- **Then** it seeds `sdlc-studio/trd.md` / `sdlc-studio/tsd.md` from the template (leaving an existing
  one untouched) and directs it to be generated from the PRD (the TSD also from the detected stack)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_trd_and_tsd_stages_seed_and_direct
- **Verified:** yes (2026-07-26)

### AC2: the TRD and TSD stages advance the guided flow to personas

- **Given** guided onboarding with agents and prd confirmed
- **When** `init guided --confirm` is run for trd, then for tsd
- **Then** the runner advances trd -> tsd -> personas, each seeded and confirmed in turn
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_trd_tsd_advance_to_personas
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
