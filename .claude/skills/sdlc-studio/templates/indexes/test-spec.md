<!--
Template: Test Spec Index (Streamlined)
File: sdlc-studio/test-specs/_index.md
Status values: See reference-outputs.md
Related: help/test-spec.md, reference-test-spec.md
-->
# Test Specification Index

> **Generated:** {{generated_date}}
> **Total Specs:** {{total_specs}}
> **Total Test Cases:** {{total_cases}}

## Summary by Epic

| Spec | Epic | Cases | Automated | Status |
|------|------|-------|-----------|--------|
{{#each specs}}
| [TS{{id}}](TS{{id}}-{{slug}}.md) | [EP{{epic_id}}](../../epics/EP{{epic_id}}-{{epic_slug}}.md) | {{case_count}} | {{automated_count}} ({{automated_pct}}%) | {{status}} |
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

## Next Steps

{{#if missing_epics}}
**Epics without specs:**
{{#each missing_epics}}
- [ ] EP{{id}}: {{title}} - Run `/sdlc-studio test-spec --epic EP{{id}}`
{{/each}}
{{/if}}

{{#if pending_automation}}
**Specs with pending automation:**
{{#each pending_automation}}
- [ ] TS{{id}}: {{pending_count}} cases - Run `/sdlc-studio test-automation --spec TS{{id}}`
{{/each}}
{{/if}}
