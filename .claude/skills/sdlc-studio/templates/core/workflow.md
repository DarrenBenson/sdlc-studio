<!--
Template: Workflow State Tracker
File: sdlc-studio/workflows/WF{NNNN}-{story-slug}.md
Purpose: Track implementation progress across sessions for resumability and auditability
Related: reference-story.md#story-implement-workflow
-->
# WF{{workflow_id}}: {{story_title}} - Workflow State

> **Status:** {{status}}
> **Story:** [US{{story_id}}: {{story_title}}](../stories/US{{story_id}}-{{story_slug}}.md)
> **Plan:** [PL{{plan_id}}: {{story_title}}](../plans/PL{{plan_id}}-{{plan_slug}}.md)
> **Test Spec:** [TS{{spec_id}}: {{story_title}}](../test-specs/TS{{spec_id}}-{{spec_slug}}.md)
> **Started:** {{start_date}}
> **Last Updated:** {{last_updated}}
> **Approach:** {{approach}}

## Phase Progress

| # | Phase | Status | Started | Completed | Notes |
|---|-------|--------|---------|-----------|-------|
| 1 | Plan | {{phase1_status}} | {{phase1_started}} | {{phase1_completed}} | {{phase1_notes}} |
| 2 | Test Spec | {{phase2_status}} | {{phase2_started}} | {{phase2_completed}} | {{phase2_notes}} |
| 3 | Implement | {{phase3_status}} | {{phase3_started}} | {{phase3_completed}} | {{phase3_notes}} |
| 4 | Tests | {{phase4_status}} | {{phase4_started}} | {{phase4_completed}} | {{phase4_notes}} |
| 5 | Test | {{phase5_status}} | {{phase5_started}} | {{phase5_completed}} | {{phase5_notes}} |
| 6 | Verify | {{phase6_status}} | {{phase6_started}} | {{phase6_completed}} | {{phase6_notes}} |
| 7 | Check | {{phase7_status}} | {{phase7_started}} | {{phase7_completed}} | {{phase7_notes}} |
| 8 | Review | {{phase8_status}} | {{phase8_started}} | {{phase8_completed}} | {{phase8_notes}} |

**Current Phase:** {{current_phase}}

---

## Plan Task Progress

Checkboxes synced from plan file. Updated as tasks complete.

| # | Task | Status |
|---|------|--------|
{{#each plan_tasks}}
| {{index}} | {{description}} | {{status}} |
{{/each}}

---

## Session Log

### Session 1: {{session1_date}}
- **Phases completed:** {{session1_phases}}
- **Tasks completed:** {{session1_tasks}}
- **Notes:** {{session1_notes}}

---

## Errors & Pauses

{{#if has_errors}}
### Error at Phase {{error_phase}}

**Error:** {{error_message}}

**Resolution:**
{{error_resolution}}

**Resume command:**
```bash
/sdlc-studio story implement --story US{{story_id}} --from-phase {{resume_phase}}
```
{{else}}
No errors recorded.
{{/if}}

---

## Artifacts

| Type | Path | Status |
|------|------|--------|
| Plan | `sdlc-studio/plans/PL{{plan_id}}-{{plan_slug}}.md` | {{plan_status}} |
| Test Spec | `sdlc-studio/test-specs/TS{{spec_id}}-{{spec_slug}}.md` | {{spec_status}} |
| Tests | `{{test_file_path}}` | {{tests_status}} |
| Implementation | `{{impl_file_paths}}` | {{impl_status}} |

---

## Completion

{{#if is_complete}}
**Completed:** {{completion_date}}
**Duration:** {{total_duration}}

### Final Summary
- All {{total_phases}} phases completed
- {{total_tasks}} plan tasks completed
- {{total_tests}} tests passing
- All AC verified
{{/if}}
