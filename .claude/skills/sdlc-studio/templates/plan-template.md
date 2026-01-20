# PL{{plan_id}}: {{story_title}} - Implementation Plan

> **Status:** {{status}}
> **Story:** [US{{story_id}}: {{story_title}}](../stories/US{{story_id}}-{{story_slug}}.md)
> **Epic:** [EP{{epic_id}}: {{epic_title}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)
> **Created:** {{created_date}}
> **Language:** {{language}}

## Overview

{{overview}}

## Acceptance Criteria Summary

| AC | Name | Description |
|----|------|-------------|
| AC1 | {{ac1_name}} | {{ac1_summary}} |
| AC2 | {{ac2_name}} | {{ac2_summary}} |
| AC3 | {{ac3_name}} | {{ac3_summary}} |

## Technical Context

### Language & Framework

- **Primary Language:** {{language}}
- **Framework:** {{framework}}
- **Test Framework:** {{test_framework}}

### Relevant Best Practices

{{best_practices_summary}}

### Library Documentation (Context7)

Query Context7 for each library before implementation:

| Library | Context7 ID | Query | Key Patterns |
|---------|-------------|-------|--------------|
| {{library_1}} | {{context7_id_1}} | {{query_1}} | {{patterns_1}} |
| {{library_2}} | {{context7_id_2}} | {{query_2}} | {{patterns_2}} |

### Existing Patterns

{{existing_patterns}}

## Recommended Approach

**Strategy:** {{implementation_strategy}}  <!-- TDD | Test-After | Hybrid -->
**Rationale:** {{strategy_rationale}}

### Test Priority

1. {{priority_test_1}}
2. {{priority_test_2}}
3. {{priority_test_3}}

### Documentation Updates Required

- [ ] {{doc_update_1}}
- [ ] {{doc_update_2}}

## Implementation Steps

### Phase 1: {{phase1_name}}

**Goal:** {{phase1_goal}}

#### Step 1.1: {{step1_1_name}}

- [ ] {{step1_1_task1}}
- [ ] {{step1_1_task2}}

**Files to modify:**
- `{{file_path}}` - {{file_change_description}}

**Considerations:**
{{step1_1_considerations}}

#### Step 1.2: {{step1_2_name}}

- [ ] {{step1_2_task1}}
- [ ] {{step1_2_task2}}

**Files to modify:**
- `{{file_path}}` - {{file_change_description}}

### Phase 2: {{phase2_name}}

**Goal:** {{phase2_goal}}

#### Step 2.1: {{step2_1_name}}

- [ ] {{step2_1_task1}}
- [ ] {{step2_1_task2}}

### Phase 3: Testing & Validation

**Goal:** Verify all acceptance criteria are met

#### Step 3.1: Unit Tests

- [ ] Write tests for {{test_target}}
- [ ] Ensure edge cases covered

#### Step 3.2: Integration Tests

- [ ] Test {{integration_point}}
- [ ] Verify error handling

#### Step 3.3: Acceptance Criteria Verification

| AC | Verification Method | Status |
|----|---------------------|--------|
| AC1 | {{ac1_verification}} | Pending |
| AC2 | {{ac2_verification}} | Pending |
| AC3 | {{ac3_verification}} | Pending |

## Edge Case Handling Plan

Every edge case from the Story MUST appear here with an explicit handling strategy.

### Edge Case Coverage

| # | Edge Case (from Story) | Handling Strategy | Implementation Phase | Validated |
|---|------------------------|-------------------|---------------------|-----------|
{{#each edge_cases}}
| {{index}} | {{scenario}} | {{strategy}} | Phase {{phase}} | [ ] |
{{/each}}

### Coverage Summary

- Story edge cases: {{story_edge_case_count}}
- Handled in plan: {{planned_edge_case_count}}
- Unhandled: {{unhandled_edge_case_count}}

{{#if unhandled_edge_cases}}
**UNHANDLED EDGE CASES (blocking):**
{{#each unhandled_edge_cases}}
- {{scenario}}
{{/each}}

> **Error:** Plan cannot proceed until all story edge cases have handling strategies.
{{/if}}

### Edge Case Implementation Notes

{{edge_case_notes}}

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| {{risk}} | {{risk_impact}} | {{risk_mitigation}} |

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| {{dependency}} | {{dependency_type}} | {{dependency_notes}} |

## Open Questions

- [ ] {{question}}

## Definition of Done Checklist

- [ ] All acceptance criteria implemented
- [ ] Unit tests written and passing
- [ ] Edge cases handled
- [ ] Code follows best practices
- [ ] No linting errors
- [ ] Documentation updated (if needed)
- [ ] Ready for code review

## Notes

{{additional_notes}}
