<!--
Template: Epic Workflow
File: sdlc-studio/workflows/WF{NNNN}-epic-{slug}.md
Status values: See reference-outputs.md
Related: help/epic.md, reference-epic.md
-->
# WF{{workflow_id}}: {{epic_title}} - Epic Workflow

> **Status:** {{status}}
> **Epic:** [EP{{epic_id}}: {{epic_title}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)
> **Started:** {{started_date}}
> **Stories:** {{total_stories}} ({{done_stories}} Done, {{pending_stories}} Pending)

## Workflow Summary

| Attribute | Value |
|-----------|-------|
| Epic | EP{{epic_id}} |
| Total Stories | {{total_stories}} |
| Stories Done | {{done_stories}} |
| Stories Pending | {{pending_stories}} |
| Current Story | {{current_story}} |

## Execution Order

Stories are processed in dependency order.

### Dependency Graph

```
{{dependency_graph}}
```

### Story Queue

| Order | Story | Title | Dependencies | Approach | Status | Phases |
|-------|-------|-------|--------------|----------|--------|--------|
{{#each stories}}
| {{order}} | US{{story_id}} | {{title}} | {{dependencies}} | {{approach}} | {{status}} | {{phases_complete}}/8 |
{{/each}}

## Story Progress

### Completed Stories

{{#each completed_stories}}
#### US{{story_id}}: {{title}}

- **Workflow:** [WF{{workflow_id}}](WF{{workflow_id}}-{{slug}}.md)
- **Approach:** {{approach}}
- **Started:** {{started}}
- **Completed:** {{completed}}
- **Duration:** {{duration}}

{{/each}}

{{#if no_completed_stories}}
No stories completed yet.
{{/if}}

### Current Story

{{#if current_story}}
#### US{{current_story_id}}: {{current_story_title}}

- **Workflow:** [WF{{current_workflow_id}}](WF{{current_workflow_id}}-{{current_slug}}.md)
- **Status:** {{current_story_status}}
- **Phase:** {{current_phase}}/8 - {{current_phase_name}}
- **Started:** {{current_started}}

**Progress:**

| Phase | Status |
|-------|--------|
| 1. Plan | {{current_phase1}} |
| 2. Test Spec | {{current_phase2}} |
| 3. Tests | {{current_phase3}} |
| 4. Implement | {{current_phase4}} |
| 5. Test | {{current_phase5}} |
| 6. Verify | {{current_phase6}} |
| 7. Check | {{current_phase7}} |
| 8. Review | {{current_phase8}} |
{{else}}
No story currently in progress.
{{/if}}

### Pending Stories

{{#each pending_stories}}
#### US{{story_id}}: {{title}}

- **Order:** {{order}}
- **Dependencies:** {{#if dependencies}}{{dependencies}}{{else}}None{{/if}}
- **Blocked:** {{#if blocked}}Yes - waiting for {{blocked_by}}{{else}}No{{/if}}
- **Approach:** {{approach}}

{{/each}}

{{#if no_pending_stories}}
All stories complete.
{{/if}}

### Blocked Stories

{{#each blocked_stories}}
#### US{{story_id}}: {{title}}

- **Blocked by:** {{blocked_by}}
- **Reason:** {{block_reason}}

{{/each}}

{{#if no_blocked_stories}}
No blocked stories.
{{/if}}

## Aggregate Statistics

| Metric | Value |
|--------|-------|
| Total phases | {{total_phases}} |
| Phases complete | {{phases_complete}} |
| Phases remaining | {{phases_remaining}} |
| Tests generated | {{tests_generated}} |
| Tests passing | {{tests_passing}} |
| Files created | {{files_created}} |
| Files modified | {{files_modified}} |

## Error Log

{{#if errors}}
### Errors Encountered

| Timestamp | Story | Phase | Error | Resolution |
|-----------|-------|-------|-------|------------|
{{#each errors}}
| {{timestamp}} | US{{story_id}} | {{phase}} | {{error}} | {{resolution}} |
{{/each}}
{{else}}
No errors encountered.
{{/if}}

## Resume Instructions

{{#if status_paused}}
**Paused at:** Story US{{paused_story_id}} - {{paused_story_title}}
**Phase:** {{paused_phase}}/8 - {{paused_phase_name}}
**Reason:** {{pause_reason}}

**To resume:**
```
/sdlc-studio epic implement --epic EP{{epic_id}} --story US{{paused_story_id}}
```

**Before resuming:**
{{resume_instructions}}
{{/if}}

## Workflow Links

| Story | Workflow File |
|-------|---------------|
{{#each stories}}
| US{{story_id}} | [WF{{workflow_id}}](WF{{workflow_id}}-{{slug}}.md) |
{{/each}}

## Timeline

| Event | Timestamp |
|-------|-----------|
| Epic workflow created | {{started_date}} |
{{#each timeline}}
| {{event}} | {{timestamp}} |
{{/each}}

## Notes

{{notes}}
