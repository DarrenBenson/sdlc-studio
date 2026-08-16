# US0649: A lint lane counts contract-reporter coverage and names every refusing verb it cannot reach

> **Status:** Ready
> **Delivers:** CR0535
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_contract_coverage.py, tools/tests/test_contract_coverage.py, package.json, .githooks/pre-commit
> **Epic:** EP0210
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A lint lane counts contract-reporter coverage and names every refusing verb it cannot reach
**So that** CR0535 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the lane reports coverage as a measured fraction

- **Given** the shipped script family
- **When** `npm run lint:contract-coverage` runs
- **Then** it prints how many refusing verbs answer the reporter, out of how many refuse at all
- **Mutant:** print the covered count alone - a numerator with no denominator reads as completeness
- **Verify:** pytest tools/tests/test_contract_coverage.py::CoverageLaneTests::test_the_lane_reports_a_fraction

### AC2: every unreachable refusing verb is NAMED

- **Given** verbs that refuse but cannot be asked
- **When** the lane runs
- **Then** each is named individually - a count tells a maintainer there is a gap, a name tells them where
- **Mutant:** report the shortfall as a number - the gap is visible and unactionable
- **Verify:** pytest tools/tests/test_contract_coverage.py::CoverageLaneTests::test_every_unreachable_verb_is_named

### AC3: the lane is advisory until its yield is measured

- **Given** a repository below full coverage
- **When** the lane runs in the gate
- **Then** it reports and does not fail the commit - a new blocking check on a gate already over its ceiling earns its place on a number rather than on assertion
- **Mutant:** make it blocking immediately - the gate refuses on a lane nobody has measured the yield of
- **Verify:** pytest tools/tests/test_contract_coverage.py::CoverageLaneTests::test_the_lane_does_not_fail_the_commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
