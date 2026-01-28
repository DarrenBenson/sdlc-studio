<!--
Template: Test Strategy Document (Streamlined)
File: sdlc-studio/tsd.md
Status values: See reference-outputs.md
Modules: tsd/contract-tests.md, tsd/performance-tests.md, tsd/security-tests.md
Related: help/tsd.md, reference-tsd.md
-->
# Test Strategy Document

> **Project:** {{project_name}}
> **Version:** {{version}}
> **Last Updated:** {{last_updated}}
> **Owner:** {{owner}}

## Overview

{{overview}}

## Test Objectives

- {{objective}}

## Scope

### In Scope
- {{in_scope_item}}

### Out of Scope
- {{out_of_scope_item}}

---

## Test Levels

### Coverage Targets

| Level | Target | Rationale |
|-------|--------|-----------|
| Unit | {{config.coverage.unit}}% | Core business logic |
| Integration | {{config.coverage.integration}}% | API and database interactions |
| E2E | {{config.coverage.e2e}}% feature coverage | Every user-visible feature |

> **Why these targets?** See `reference-tsd.md#why-90`

### Unit Testing

| Attribute | Value |
|-----------|-------|
| Coverage Target | {{config.coverage.unit}}% |
| Framework | {{unit_framework}} |
| Execution | {{unit_execution}} |

### Integration Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{integration_scope}} |
| Framework | {{integration_framework}} |
| Execution | {{integration_execution}} |

### End-to-End Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{e2e_scope}} |
| Framework | {{e2e_framework}} |
| Execution | {{e2e_execution}} |

### E2E Feature Coverage Matrix

| Feature Area | Spec File | Test Count | Status |
|--------------|-----------|------------|--------|
| {{feature_area}} | {{spec_file}} | {{test_count}} | {{status}} |

### API Contract Testing

> **Critical:** E2E tests with mocks don't catch backend bugs. Contract tests bridge this gap.
> See `modules/tsd/contract-tests.md` for implementation patterns.

### Performance Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{performance_scope}} |
| Framework | {{performance_framework}} |

> **Load testing:** See `modules/tsd/performance-tests.md`

### Security Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{security_scope}} |
| Tools | {{security_tools}} |

> **OWASP coverage:** See `modules/tsd/security-tests.md`

---

## Test Environments

| Environment | Purpose | URL | Data |
|-------------|---------|-----|------|
| Local | Development | localhost | Fixtures |
| {{env_name}} | {{env_purpose}} | {{env_url}} | {{env_data}} |

## Test Data Strategy

### Approach
{{test_data_approach}}

### Sensitive Data
{{sensitive_data_handling}}

---

## Automation Strategy

### Automation Candidates
- Regression tests for stable features
- Happy path scenarios for all user stories
- Critical business flows
- API contract validation

### Manual Testing
- Exploratory testing
- Usability assessment
- Edge cases requiring human judgement

### Automation Framework Stack

| Layer | Tool | Language |
|-------|------|----------|
| E2E/UI | {{e2e_tool}} | {{e2e_language}} |
| API | {{api_tool}} | {{api_language}} |
| Unit | {{unit_tool}} | {{unit_language}} |

---

## CI/CD Integration

### Pipeline Stages

1. **Pre-commit:** Linting, unit tests
2. **PR:** Unit + integration tests
3. **Merge to main:** Full E2E suite
4. **Nightly:** Full regression + performance
5. **Pre-release:** Full suite + security scan

### Quality Gates

| Gate | Criteria | Blocking |
|------|----------|----------|
| Unit coverage | >= {{config.coverage.unit}}% | Yes |
| Integration tests | 100% pass | Yes |
| E2E critical path | 100% pass | Yes |
| E2E full suite | {{e2e_gate_criteria}} | No (alerts) |

---

## Defect Management

### Severity Definitions

| Severity | Definition | SLA |
|----------|------------|-----|
| Critical | System unusable, data loss | {{critical_sla}} |
| High | Major feature broken, no workaround | {{high_sla}} |
| Medium | Feature impaired, workaround exists | {{medium_sla}} |
| Low | Minor issue, cosmetic | Backlog |

---

## Tools & Infrastructure

| Purpose | Tool |
|---------|------|
| Test Management | {{test_management_tool}} |
| CI/CD | {{ci_cd_tool}} |
| Browser Automation | {{browser_automation_tool}} |
| Coverage | {{coverage_tool}} |

---

## Test Organisation

```text
tests/
  unit/
    backend/
    frontend/
  integration/
  api/
  e2e/
  contracts/
  fixtures/
```

> See `reference-tsd.md#test-organisation` for naming conventions.

---

## Related Specifications

- [Product Requirements Document](../prd.md)
- [User Personas](../personas.md)

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{revision_date}} | {{revision_author}} | {{revision_change}} |
