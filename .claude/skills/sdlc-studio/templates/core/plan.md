<!--
Template: Implementation Plan (Streamlined)
File: sdlc-studio/plans/PL{NNNN}-{slug}.md
Status values: See reference-outputs.md
Related: help/code.md, reference-code.md
-->
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

---

## Technical Context

### Language & Framework
- **Primary Language:** {{language}}
- **Framework:** {{framework}}
- **Test Framework:** {{test_framework}}

### Relevant Best Practices
{{best_practices_summary}}

### Library Documentation (Context7)

| Library | Context7 ID | Key Patterns |
|---------|-------------|--------------|
| {{library}} | {{context7_id}} | {{patterns}} |

### Existing Patterns
{{existing_patterns}}

---

## Recommended Approach

**Strategy:** {{implementation_strategy}}  <!-- TDD | Test-After | Hybrid -->
**Rationale:** {{strategy_rationale}}

### Test Priority
1. {{priority_test_1}}
2. {{priority_test_2}}
3. {{priority_test_3}}

---

## Implementation Tasks

| # | Task | File | Depends On | Status |
|---|------|------|------------|--------|
{{#each tasks}}
| {{index}} | {{description}} | `{{file_path}}` | {{dependencies}} | [ ] |
{{/each}}

### Parallel Execution Groups

| Group | Tasks | Prerequisite |
|-------|-------|--------------|
{{#each agentic_groups}}
| {{group}} | {{tasks}} | {{prerequisite}} |
{{/each}}

---

## Implementation Phases

### Phase 1: {{phase1_name}}
**Goal:** {{phase1_goal}}

- [ ] {{step1_task}}
- [ ] {{step2_task}}

**Files:** `{{file_path}}` - {{change_description}}

### Phase 2: {{phase2_name}}
**Goal:** {{phase2_goal}}

- [ ] {{step1_task}}
- [ ] {{step2_task}}

### Phase 3: Testing & Validation
**Goal:** Verify all acceptance criteria

| AC | Verification Method | File Evidence | Status |
|----|---------------------|---------------|--------|
| AC1 | {{ac1_verification}} | `{{ac1_file}}:{{ac1_line}}` | Pending |
| AC2 | {{ac2_verification}} | `{{ac2_file}}:{{ac2_line}}` | Pending |
| AC3 | {{ac3_verification}} | `{{ac3_file}}:{{ac3_line}}` | Pending |

---

## Edge Case Handling

| # | Edge Case (from Story) | Handling Strategy | Phase |
|---|------------------------|-------------------|-------|
{{#each edge_cases}}
| {{index}} | {{scenario}} | {{strategy}} | {{phase}} |
{{/each}}

**Coverage:** {{planned_count}}/{{story_count}} edge cases handled

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| {{risk}} | {{impact}} | {{mitigation}} |

---

## Definition of Done

- [ ] All acceptance criteria implemented
- [ ] Unit tests written and passing
- [ ] Edge cases handled
- [ ] Code follows best practices
- [ ] No linting errors
- [ ] Documentation updated (if needed)

---

## Notes

{{additional_notes}}
