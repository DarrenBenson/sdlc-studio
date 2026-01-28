<!--
Template: Story Index (Streamlined)
File: sdlc-studio/stories/_index.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->
# Story Registry

**Last Updated:** {{last_updated}}
**Personas Reference:** [User Personas](../personas.md)

## Summary

| Status | Count |
|--------|-------|
| Draft | {{draft_count}} |
| Ready | {{ready_count}} |
| Planned | {{planned_count}} |
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

## Notes

- Stories are numbered globally (US0001, US0002, etc.)
- Story points should be assigned during team refinement
