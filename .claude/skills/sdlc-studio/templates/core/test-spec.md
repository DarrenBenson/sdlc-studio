<!--
Template: Test Specification (Streamlined)
File: sdlc-studio/test-specs/TS{NNNN}-{slug}.md
Status values: See reference-outputs.md
Related: help/test-spec.md, reference-test-spec.md
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

| Story | AC | Description | Test Cases | Status |
|-------|-----|-------------|------------|--------|
{{#each ac_coverage}}
| {{story}} | {{ac}} | {{description}} | {{test_cases}} | {{status}} |
{{/each}}

**Coverage:** {{covered_count}}/{{total_count}} ACs covered

### Test Types Required

| Type | Required | Rationale |
|------|----------|-----------|
| Unit | {{unit_required}} | {{unit_rationale}} |
| Integration | {{integration_required}} | {{integration_rationale}} |
| E2E | {{e2e_required}} | {{e2e_rationale}} |

---

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

**Type:** {{type}} | **Priority:** {{priority}} | **Story:** {{story_ref}}

| Step | Action | Expected Result |
|------|--------|-----------------|
| Given | {{given}} | {{given_result}} |
| When | {{when}} | {{when_result}} |
| Then | {{then}} | {{then_result}} |

**Assertions:**
{{#each assertions}}
- [ ] {{this}}
{{/each}}

---
{{/each}}

## Fixtures

```yaml
{{fixtures_yaml}}
```

---

## Automation Status

| TC | Title | Status | Implementation |
|----|-------|--------|----------------|
{{#each test_cases}}
| TC{{id}} | {{title}} | Pending | - |
{{/each}}

---

## Traceability

| Artefact | Reference |
|----------|-----------|
| PRD | [sdlc-studio/prd.md](../../prd.md) |
| Epic | [EP{{epic_id}}](../../epics/EP{{epic_id}}-{{epic_slug}}.md) |
| TSD | [sdlc-studio/tsd.md](../tsd.md) |

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{created_date}} | {{author}} | Initial spec |
