# US0420: each unit carries the proof its risk band requires, and coverage the TSD demands but the batch omits is flagged

> **Status:** Done
> **Delivers:** RFC0049
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0157
> **Points:** 5

## User Story

**As an** operator reading a sprint plan
**I want** each unit to carry the proof its risk band requires, with omitted coverage flagged
**So that** a unit in the highest risk band cannot ship on the weakest proof

## Acceptance Criteria

### AC1: each unit carries the proof its risk band requires

- **Given** a batch whose units fall in different risk bands
- **When** the plan is produced
- **Then** each unit carries a stated proof requirement matching its band, and a unit in the highest band cannot carry the weakest proof - the requirement is derived from the band, not chosen per unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ProofRequirementTests::test_each_unit_carries_the_proof_its_band_requires
- **Verified:** yes (2026-07-24)

### AC2: coverage the TSD demands but the batch omits is flagged

- **Given** a TSD demanding coverage in an area no unit in the batch delivers
- **When** the plan runs
- **Then** the gap is reported against the batch - a plan that silently omits demanded coverage is the case this story exists for, and it cannot be found by reading the batch alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ProofRequirementTests::test_demanded_coverage_the_batch_omits_is_flagged
- **Verified:** yes (2026-07-24)

### AC3: the close compares what was claimed with what the evidence shows

- **Given** a unit whose plan-time proof requirement was mutation evidence, closed with none
- **When** the close runs
- **Then** the mismatch is reported - a stated intent nobody checks at the end is a comment, and the whole value of writing it at plan time is being measured against it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ProofRequirementTests::test_the_close_reports_a_claimed_proof_the_evidence_does_not_show
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
