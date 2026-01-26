<!--
Template: Epic Index
File: sdlc-studio/epics/_index.md
Status values: See reference-outputs.md
Related: help/epic.md, reference-epic.md
-->
# Epic Registry

This document provides an overview of all Epics in the project.

**Last Updated:** {{last_updated}}
**PRD Reference:** [Product Requirements Document](../prd.md)

## Summary

| Status | Count |
|--------|-------|
| Draft | {{draft_count}} |
| Ready for Review | {{review_count}} |
| Approved | {{approved_count}} |
| In Progress | {{in_progress_count}} |
| Done | {{done_count}} |
| **Total** | **{{total_count}}** |

## Epics

| ID | Title | Status | Owner | Stories | Target |
|----|-------|--------|-------|---------|--------|
| [EP{{epic_id}}](EP{{epic_id}}-{{epic_slug}}.md) | {{epic_title}} | {{status}} | {{owner}} | {{story_count}} | {{target}} |

## By Status

### In Progress

{{in_progress_epics}}

### Ready for Review

{{review_epics}}

### Draft

{{draft_epics}}

### Done

{{done_epics}}

## Dependency Graph

```
{{dependency_graph}}
```

## Notes

- Epics are numbered globally (EP0001, EP0002, etc.)
- Stories are tracked separately in [Story Registry](../stories/_index.md)
- For PRD traceability, see the PRD Reference link in each Epic
