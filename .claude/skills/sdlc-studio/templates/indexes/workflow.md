# Workflow Registry

This document tracks all implementation workflows for the project.

**Last Updated:** {{last_updated}}

## Summary

| Status | Count |
|--------|-------|
| In Progress | {{in_progress_count}} |
| Paused | {{paused_count}} |
| Done | {{done_count}} |
| **Total** | **{{total_count}}** |

## Active Workflows

Workflows currently in progress or paused.

| ID | Story | Current Phase | Status | Last Updated |
|----|-------|---------------|--------|--------------|
{{#each active_workflows}}
| [WF{{id}}](WF{{id}}-{{slug}}.md) | [US{{story_id}}](../stories/US{{story_id}}-{{story_slug}}.md) | {{current_phase}} | {{status}} | {{last_updated}} |
{{/each}}

## Completed Workflows

| ID | Story | Completed | Duration | Sessions |
|----|-------|-----------|----------|----------|
{{#each completed_workflows}}
| [WF{{id}}](WF{{id}}-{{slug}}.md) | [US{{story_id}}](../stories/US{{story_id}}-{{story_slug}}.md) | {{completed_date}} | {{duration}} | {{session_count}} |
{{/each}}

## Notes

- Workflows are created automatically by `story implement`
- Each workflow tracks progress across multiple sessions
- Paused workflows can be resumed with `story implement --story US{NNNN}`
- Completed workflows serve as audit trail for implementation
