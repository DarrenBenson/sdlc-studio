# Test Strategy

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

## Test Levels

### Unit Testing

| Attribute | Value |
|-----------|-------|
| Coverage Target | {{unit_coverage_target}} |
| Framework | {{unit_framework}} |
| Responsibility | {{unit_responsibility}} |
| Execution | {{unit_execution}} |

### Integration Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{integration_scope}} |
| Framework | {{integration_framework}} |
| Responsibility | {{integration_responsibility}} |
| Execution | {{integration_execution}} |

### End-to-End Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{e2e_scope}} |
| Framework | {{e2e_framework}} |
| Responsibility | {{e2e_responsibility}} |
| Execution | {{e2e_execution}} |

### Performance Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{performance_scope}} |
| Framework | {{performance_framework}} |
| Responsibility | {{performance_responsibility}} |
| Execution | {{performance_execution}} |

### Security Testing

| Attribute | Value |
|-----------|-------|
| Scope | {{security_scope}} |
| Tools | {{security_tools}} |
| Responsibility | {{security_responsibility}} |
| Execution | {{security_execution}} |

## Test Environments

| Environment | Purpose | URL | Data |
|-------------|---------|-----|------|
| Local | Development | localhost | Mocked/Fixtures |
| {{env_name}} | {{env_purpose}} | {{env_url}} | {{env_data}} |

## Test Data Strategy

### Approach

{{test_data_approach}}

### Sensitive Data

{{sensitive_data_handling}}

### Data Reset

{{data_reset_strategy}}

## Automation Strategy

### Automation Candidates

{{automation_candidates}}

- All regression tests for stable features
- Happy path scenarios for all user stories
- Critical business flows
- API contract validation

### Manual Testing

{{manual_testing}}

- Exploratory testing
- Usability assessment
- Edge cases requiring human judgement

### Automation Framework Stack

| Layer | Tool | Language |
|-------|------|----------|
| E2E/UI | {{e2e_tool}} | {{e2e_language}} |
| API | {{api_tool}} | {{api_language}} |
| Unit | {{unit_tool}} | {{unit_language}} |
| BDD | {{bdd_tool}} | Gherkin |
| Performance | {{perf_tool}} | {{perf_language}} |

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
| Unit coverage | {{unit_gate_criteria}} | {{unit_gate_blocking}} |
| Integration tests | 100% pass | Yes |
| E2E critical path | 100% pass | Yes |
| E2E full suite | {{e2e_gate_criteria}} | No (alerts) |
| Performance | {{perf_gate_criteria}} | {{perf_gate_blocking}} |

## Defect Management

### Severity Definitions

| Severity | Definition | SLA |
|----------|------------|-----|
| Critical | System unusable, data loss | {{critical_sla}} |
| High | Major feature broken, no workaround | {{high_sla}} |
| Medium | Feature impaired, workaround exists | {{medium_sla}} |
| Low | Minor issue, cosmetic | Backlog |

### Defect Workflow

{{defect_workflow}}

## Reporting

### Metrics Tracked

- Test pass/fail rates by suite
- Code coverage trends
- Defect discovery rate
- Test execution time
- Flaky test percentage

### Reporting Cadence

- **Daily:** CI dashboard
- **Sprint:** Test summary in retrospective
- **Release:** Full test report

## Roles & Responsibilities

| Role | Responsibilities |
|------|------------------|
| Developers | Unit tests, integration tests, fixing bugs |
| QA Engineers | Test plans, E2E tests, exploratory testing |
| Tech Lead | Test strategy review, tooling decisions |
| Product Owner | Acceptance criteria validation, UAT |

## Tools & Infrastructure

| Purpose | Tool |
|---------|------|
| Test Management | {{test_management_tool}} |
| CI/CD | {{ci_cd_tool}} |
| Browser Automation | {{browser_automation_tool}} |
| API Testing | {{api_testing_tool}} |
| Mocking | {{mocking_tool}} |
| Coverage | {{coverage_tool}} |
| Reporting | {{reporting_tool}} |

## Related Specifications

- [Product Requirements Document](../prd.md)
- [User Personas](../personas.md)
- [Definition of Done](../definition-of-done.md)

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{revision_date}} | {{revision_author}} | {{revision_change}} |
