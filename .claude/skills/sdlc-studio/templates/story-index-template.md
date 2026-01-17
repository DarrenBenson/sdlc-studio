# Story Registry

This document provides an overview of all User Stories in the project.

**Last Updated:** {{last_updated}}
**Personas Reference:** [User Personas](../personas.md)

## Summary

| Status | Count |
|--------|-------|
| Draft | {{draft_count}} |
| Ready | {{ready_count}} |
| In Progress | {{in_progress_count}} |
| Review | {{review_count}} |
| Done | {{done_count}} |
| **Total** | **{{total_count}}** |

## Stories by Epic

### [EP{{epic_id}}: {{epic_title}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)

| ID | Title | Status | Points | Owner |
|----|-------|--------|--------|-------|
| [US{{story_id}}](US{{story_id}}-{{story_slug}}.md) | {{story_title}} | {{status}} | {{points}} | {{owner}} |

## All Stories

| ID | Title | Epic | Status | Points | Persona |
|----|-------|------|--------|--------|---------|
| [US{{story_id}}](US{{story_id}}-{{story_slug}}.md) | {{story_title}} | [EP{{epic_id}}](../epics/EP{{epic_id}}-{{epic_slug}}.md) | {{status}} | {{points}} | {{persona}} |

## By Status

### In Progress

{{in_progress_stories}}

### Ready

{{ready_stories}}

### Draft

{{draft_stories}}

### Done

{{done_stories}}

## Estimation Summary

| Metric | Value |
|--------|-------|
| Total Story Points | {{total_points}} |
| Estimated Stories | {{estimated_count}} |
| Unestimated Stories | {{unestimated_count}} |
| Average Points/Story | {{avg_points}} |

## Notes

- Stories are numbered globally (US0001, US0002, etc.) to allow movement between Epics
- Story points should be assigned during team refinement, not by AI generation
- For Definition of Done, see [Definition of Done](../definition-of-done.md)
