<!--
Template: Story Workflow
File: sdlc-studio/workflows/WF{NNNN}-story-{slug}.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->
# WF{{workflow_id}}: {{story_title}} - Story Workflow

> **Status:** {{status}}
> **Story:** [US{{story_id}}: {{story_title}}](../stories/US{{story_id}}-{{story_slug}}.md)
> **Epic:** [EP{{epic_id}}: {{epic_title}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)
> **Started:** {{started_date}}
> **Approach:** {{approach}}

## Workflow Summary

| Attribute | Value |
|-----------|-------|
| Story | US{{story_id}} |
| Approach | {{approach}} |
| Phases | 7 |
| Current Phase | {{current_phase}} |

## Approach Decision

**Strategy:** {{approach}}
**Reason:** {{approach_reason}}

### Decision Factors

| Factor | Value | Weight |
|--------|-------|--------|
| Edge case count | {{edge_case_count}} | {{#if edge_case_count_gt_5}}Favours TDD{{else}}Neutral{{/if}} |
| AC clarity | {{ac_clarity}} | {{ac_clarity_weight}} |
| Story type | {{story_type}} | {{story_type_weight}} |
| Complexity | {{complexity}} | {{complexity_weight}} |

## Dependencies Check

### Story Dependencies

| Story | Title | Required Status | Actual Status | OK |
|-------|-------|-----------------|---------------|-----|
{{#each story_dependencies}}
| US{{story_id}} | {{title}} | Done | {{status}} | {{#if done}}Yes{{else}}**No**{{/if}} |
{{/each}}

{{#if has_blocking_dependencies}}
> **Warning:** Blocking dependencies detected. Story may not proceed until resolved.
{{/if}}

## Phase Progress

| # | Phase | Status | Artifact | Started | Completed | Notes |
|---|-------|--------|----------|---------|-----------|-------|
| 1 | Plan | {{phase1_status}} | {{phase1_artifact}} | {{phase1_started}} | {{phase1_completed}} | {{phase1_notes}} |
| 2 | Test Spec | {{phase2_status}} | {{phase2_artifact}} | {{phase2_started}} | {{phase2_completed}} | {{phase2_notes}} |
| 3 | Tests | {{phase3_status}} | {{phase3_artifact}} | {{phase3_started}} | {{phase3_completed}} | {{phase3_notes}} |
| 4 | Implement | {{phase4_status}} | {{phase4_artifact}} | {{phase4_started}} | {{phase4_completed}} | {{phase4_notes}} |
| 5 | Test | {{phase5_status}} | {{phase5_artifact}} | {{phase5_started}} | {{phase5_completed}} | {{phase5_notes}} |
| 6 | Verify | {{phase6_status}} | {{phase6_artifact}} | {{phase6_started}} | {{phase6_completed}} | {{phase6_notes}} |
| 7 | Check | {{phase7_status}} | {{phase7_artifact}} | {{phase7_started}} | {{phase7_completed}} | {{phase7_notes}} |
| 8 | Review | {{phase8_status}} | {{phase8_artifact}} | {{phase8_started}} | {{phase8_completed}} | {{phase8_notes}} |

### Phase Status Values

- **Pending** - Not yet started
- **In Progress** - Currently executing
- **Done** - Completed successfully
- **Skipped** - Not applicable for this workflow
- **Paused** - Stopped due to error
- **Blocked** - Waiting on external factor

## Execution Detail

### Phase 1: Plan

**Command:** `code plan --story US{{story_id}}`
**Expected Output:** `sdlc-studio/plans/PL{{plan_id}}-{{story_slug}}.md`

{{#if phase1_status_done}}
**Result:**
- Plan created: {{phase1_artifact}}
- Implementation phases: {{plan_phase_count}}
- Key files: {{plan_key_files}}
{{/if}}

### Phase 2: Test Spec

**Command:** `test-spec --story US{{story_id}}`
**Expected Output:** `sdlc-studio/test-specs/TS{{spec_id}}-{{story_slug}}.md`

{{#if phase2_status_done}}
**Result:**
- Spec created: {{phase2_artifact}}
- Test cases: {{test_case_count}}
- AC coverage: {{ac_coverage}}
{{/if}}

### Phase 3: Tests

**Command:** `test-automation --spec TS{{spec_id}}`
**Expected Output:** `tests/{{test_file}}`

{{#if phase3_status_done}}
**Result:**
- Tests created: {{phase3_artifact}}
- Test count: {{test_count}}
- Initial status: {{initial_test_status}}
{{/if}}

### Phase 4: Implement

**Command:** `code implement --plan PL{{plan_id}}`
**Expected Output:** Implementation per plan phases

**CRITICAL:** Complete ALL plan phases (backend, frontend, integration, etc.) before marking this phase done. Do NOT pause to ask questions mid-implementation.

**Completion checklist:**
- [ ] All plan phases executed (not just backend)
- [ ] All ACs have implementing code
- [ ] Frontend components created (if in plan)
- [ ] Integration code complete (if in plan)

{{#if phase4_status_done}}
**Result:**
- Files created: {{files_created}}
- Files modified: {{files_modified}}
- Lines added: {{lines_added}}
- Plan phases complete: {{plan_phases_complete}}/{{plan_phases_total}}
{{/if}}

### Phase 5: Test

**Command:** `code test --story US{{story_id}}`
**Expected Output:** All tests pass

{{#if phase5_status_done}}
**Result:**
- Tests run: {{tests_run}}
- Passed: {{tests_passed}}
- Failed: {{tests_failed}}
{{/if}}

### Phase 6: Verify

**Command:** `code verify --story US{{story_id}}`
**Expected Output:** Verification report

{{#if phase6_status_done}}
**Result:**
- AC verified: {{ac_verified}}/{{ac_total}}
- Edge cases: {{edge_cases_verified}}/{{edge_cases_total}}
- Issues: {{verify_issues}}
{{/if}}

### Phase 7: Check

**Command:** `code check`
**Expected Output:** Quality gates pass

{{#if phase7_status_done}}
**Result:**
- Lint errors: {{lint_errors}}
- Auto-fixed: {{lint_fixed}}
- Remaining: {{lint_remaining}}
{{/if}}

### Phase 8: Review

**Command:** `status`
**Expected Output:** Final status review before marking complete

{{#if phase8_status_done}}
**Result:**
- Requirements: {{review_requirements_pct}}%
- Code: {{review_code_pct}}%
- Tests: {{review_tests_pct}}%
- Issues: {{review_issues}}
{{/if}}

## Error Log

{{#if errors}}
### Errors Encountered

| Timestamp | Phase | Error | Resolution |
|-----------|-------|-------|------------|
{{#each errors}}
| {{timestamp}} | {{phase}} | {{error}} | {{resolution}} |
{{/each}}
{{else}}
No errors encountered.
{{/if}}

## Resume Instructions

{{#if status_paused}}
**Paused at:** Phase {{paused_phase}} - {{paused_phase_name}}
**Reason:** {{pause_reason}}

**To resume:**
```
/sdlc-studio story implement --story US{{story_id}} --from-phase {{paused_phase}}
```

**Before resuming:**
{{resume_instructions}}
{{/if}}

## Artifacts Created

| Type | ID | Path |
|------|-----|------|
| Plan | PL{{plan_id}} | sdlc-studio/plans/PL{{plan_id}}-{{story_slug}}.md |
| Test Spec | TS{{spec_id}} | sdlc-studio/test-specs/TS{{spec_id}}-{{story_slug}}.md |
| Tests | - | tests/{{test_file}} |

## Timeline

| Event | Timestamp |
|-------|-----------|
| Workflow created | {{started_date}} |
{{#each timeline}}
| {{event}} | {{timestamp}} |
{{/each}}

## Notes

{{notes}}
