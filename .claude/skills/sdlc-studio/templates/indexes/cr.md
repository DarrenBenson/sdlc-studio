<!--
Template: Change Request Index
File: sdlc-studio/change-requests/_index.md
Status values: See reference-outputs.md
Related: help/cr.md, reference-cr.md
-->
# Change Request Registry

**Last Updated:** {{last_updated}}
**PRD Reference:** [Product Requirements Document](../prd.md)

## Summary

| Status | Count |
| --- | --- |
| Proposed | {{proposed_count}} |
| Approved | {{approved_count}} |
| In Progress | {{in_progress_count}} |
| Complete | {{complete_count}} |
| Rejected | {{rejected_count}} |
| Deferred | {{deferred_count}} |
| **Total** | **{{total_count}}** |

## By Priority

| Priority | Proposed | Approved | In Progress | Complete |
| --- | --- | --- | --- | --- |
| P1 | {{p1_proposed}} | {{p1_approved}} | {{p1_in_progress}} | {{p1_complete}} |
| P2 | {{p2_proposed}} | {{p2_approved}} | {{p2_in_progress}} | {{p2_complete}} |
| P3 | {{p3_proposed}} | {{p3_approved}} | {{p3_in_progress}} | {{p3_complete}} |
| P4 | {{p4_proposed}} | {{p4_approved}} | {{p4_in_progress}} | {{p4_complete}} |

## All Change Requests

| ID | Title | Priority | Status | Type | Linked Epics | Date |
| --- | --- | --- | --- | --- | --- | --- |
| [CR-{{cr_id}}](CR{{cr_id}}-{{slug}}.md) | {{title}} | {{priority}} | {{status}} | {{type}} | {{linked_epics}} | {{date}} |

## Dependencies

| CR | Depends On | Dependency Status |
| --- | --- | --- |
| CR-{{cr_id}} | CR-{{dep_id}} | {{dep_status}} |

## Notes

- CRs are numbered globally (CR-0001, CR-0002, etc.)
- Priority: P1 (critical gap) > P2 (important) > P3 (desirable) > P4 (nice to have)
- Types: feature-request, production-feedback, spec-gap, retrospective, design-change
- Use `/sdlc-studio cr action --cr CR-NNNN` to turn a CR into epics and stories
