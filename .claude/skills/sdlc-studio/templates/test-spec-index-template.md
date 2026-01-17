# Test Specification Index

> **Generated:** {{generated_date}}
> **Total Specs:** {{total_specs}}
> **Total Test Cases:** {{total_cases}}

## Overview

This index catalogues all test specifications for the project. Each spec consolidates test cases for an Epic.

## Summary by Epic

| Spec | Epic | Cases | Automated | Status |
|------|------|-------|-----------|--------|
{{#each specs}}
| [TSP{{id}}](TSP{{id}}-{{slug}}.md) | [EP{{epic_id}}](../../epics/EP{{epic_id}}-{{epic_slug}}.md) | {{case_count}} | {{automated_count}} ({{automated_pct}}%) | {{status}} |
{{/each}}

## Coverage Summary

| Metric | Value |
|--------|-------|
| Epics with specs | {{epics_covered}}/{{total_epics}} |
| Total test cases | {{total_cases}} |
| Automated | {{total_automated}} ({{automation_pct}}%) |
| Pending | {{total_pending}} |

## By Test Type

| Type | Count | Automated |
|------|-------|-----------|
| Unit | {{unit_count}} | {{unit_automated}} |
| Integration | {{integration_count}} | {{integration_automated}} |
| API | {{api_count}} | {{api_automated}} |
| E2E | {{e2e_count}} | {{e2e_automated}} |

## By Priority

| Priority | Count | Automated |
|----------|-------|-----------|
| Critical | {{critical_count}} | {{critical_automated}} |
| High | {{high_count}} | {{high_automated}} |
| Medium | {{medium_count}} | {{medium_automated}} |
| Low | {{low_count}} | {{low_automated}} |

---

## Specifications

{{#each specs}}
### TSP{{id}}: {{title}}

**Epic:** [EP{{epic_id}}: {{epic_title}}](../../epics/EP{{epic_id}}-{{epic_slug}}.md)
**Status:** {{status}}
**Cases:** {{case_count}} ({{automated_count}} automated)

| TC | Title | Type | Priority | Automated |
|----|-------|------|----------|-----------|
{{#each cases}}
| TC{{id}} | {{title}} | {{type}} | {{priority}} | {{automated}} |
{{/each}}

---

{{/each}}

## Quick Reference

### Status Values

| Status | Meaning |
|--------|---------|
| Draft | Initial creation, needs review |
| Ready | Reviewed, ready for automation |
| In Progress | Automation in progress |
| Complete | All cases automated |

### Next Steps

{{#if missing_epics}}
**Epics without specs:**
{{#each missing_epics}}
- [ ] EP{{id}}: {{title}} - Run `/spec test-spec --epic EP{{id}}`
{{/each}}
{{/if}}

{{#if pending_automation}}
**Specs with pending automation:**
{{#each pending_automation}}
- [ ] TSP{{id}}: {{pending_count}} cases - Run `/spec test-automation --spec TSP{{id}}`
{{/each}}
{{/if}}

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{generated_date}} | {{author}} | Index generated |
