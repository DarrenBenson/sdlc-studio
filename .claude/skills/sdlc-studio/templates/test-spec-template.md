<!--
Template: Test Specification
File: sdlc-studio/test-specs/TS{NNNN}-{slug}.md
Status values: See reference-outputs.md
Related: help/test-spec.md, reference-testing.md
-->
# TS{{spec_id}}: {{spec_title}}

> **Status:** Draft
> **Epic:** [EP{{epic_id}}: {{epic_title}}](../../epics/EP{{epic_id}}-{{epic_slug}}.md)
> **Created:** {{created_date}}
> **Last Updated:** {{created_date}}

## Overview

{{overview_description}}

## Scope

### Stories Covered

| Story | Title | Priority |
|-------|-------|----------|
{{#each stories}}
| [US{{id}}](../../stories/US{{id}}-{{slug}}.md) | {{title}} | {{priority}} |
{{/each}}

### AC Coverage Matrix

Maps each Story AC to test cases ensuring complete coverage.

| Story | AC | Description | Test Cases | Status |
|-------|-----|-------------|------------|--------|
{{#each ac_coverage}}
| {{story}} | {{ac}} | {{description}} | {{test_cases}} | {{status}} |
{{/each}}

**Coverage Summary:**
- Total ACs: {{total_ac_count}}
- Covered: {{covered_ac_count}}
- Uncovered: {{uncovered_ac_count}}

{{#if uncovered_acs}}
**UNCOVERED ACs (blocking):**
{{#each uncovered_acs}}
- {{story}}/{{ac}}: {{description}}
{{/each}}

> **Warning:** Test spec cannot be marked Ready until all ACs have at least one test case.
{{/if}}

### Test Types Required

| Type | Required | Rationale |
|------|----------|-----------|
| Unit | {{unit_required}} | {{unit_rationale}} |
| Integration | {{integration_required}} | {{integration_rationale}} |
| API | {{api_required}} | {{api_rationale}} |
| E2E | {{e2e_required}} | {{e2e_rationale}} |

## Environment

| Requirement | Details |
|-------------|---------|
| Prerequisites | {{prerequisites}} |
| External Services | {{external_services}} |
| Test Data | {{test_data_requirements}} |

---

## Test Cases

{{#each test_cases}}
### TC{{id}}: {{title}}

**Type:** {{type}}
**Priority:** {{priority}}
**Story:** {{story_ref}}
**Automated:** No

#### Scenario

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Given {{given}} | {{given_result}} |
| 2 | When {{when}} | {{when_result}} |
| 3 | Then {{then}} | {{then_result}} |

#### Test Data

```yaml
input:
  {{input_data}}
expected:
  {{expected_data}}
```

#### Assertions

{{#each assertions}}
- [ ] {{this}}
{{/each}}

---

{{/each}}

## Fixtures

```yaml
# Shared test data for this spec
{{fixtures_yaml}}
```

## Automation Status

| TC | Title | Status | Implementation |
|----|-------|--------|----------------|
{{#each test_cases}}
| TC{{id}} | {{title}} | Pending | - |
{{/each}}

## Traceability

| Artefact | Reference |
|----------|-----------|
| PRD | [sdlc-studio/prd.md](../../prd.md) |
| Epic | [EP{{epic_id}}](../../epics/EP{{epic_id}}-{{epic_slug}}.md) |
| TSD | [sdlc-studio/tsd.md](../tsd.md) |

## Lessons Learned

<!-- Optional section. Document issues discovered during testing that should inform future test design. -->
<!-- Example:
### E2E Mocking Blindspot
**Issue:** E2E tests with mocked data passed but production showed "--" for a field.
**Root Cause:** Backend schema omitted the field even though DB stored it.
**Prevention:** Add API contract tests that verify backend returns all frontend-expected fields.
-->

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{created_date}} | {{author}} | Initial spec generation |
