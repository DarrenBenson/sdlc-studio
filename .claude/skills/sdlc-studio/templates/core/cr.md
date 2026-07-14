<!--
Template: Change Request
File: sdlc-studio/change-requests/CR{NNNN}-{slug}.md
Status values: See reference-outputs.md
Related: help/cr.md, reference-cr.md
-->
# CR-{{cr_id}}: {{title}}

> **Status:** {{status}}
> **Priority:** {{priority}}
> **Type:** {{type}}
> **Requester:** {{requester}}
> **Estimated-by:** {{who made the size call - so the report can tell you your own hit rate}}
> **Delivered-by:** {{the model that delivered it - written at close, not at filing}}
> **Date:** {{date}}
> **Affects:** {{affects}}
> **Depends on:** {{depends_on}}
> **GitHub Issue:** {{github_issue}}

<!--
The CR's own `**Points:**` sits under Impact Assessment below: a RELATIVE size on the modified
Fibonacci scale (1, 2, 3, 5, 8, 13, 20), sized against units already delivered rather than
predicted in hours. The gaps widen deliberately, because uncertainty grows with size - a value
off the scale is REFUSED, never rounded, because the scale IS the estimate. Above 8, split the
CR: estimator consistency collapses beyond it.
-->

## Summary

{{summary}}

## Problem

{{problem_statement}}

---

## Proposed Changes

### Item 1: {{item_1_title}}

<!-- `Item points`, not `Points`: `Points` is the CR's own job size, read by the planner from
the FIRST match in the document. A per-item field spelled the same way shadows it, and the CR
plans as unsized. -->

**Item priority:** {{item_1_priority}}
**Item points:** {{item_1_points}}

{{item_1_description}}

<!-- Add more items as needed:
### Item 2: {{item_2_title}}
-->

---

## Impact Assessment

**Points:** {{1|2|3|5|8|13|20 - the CR's own job size, read by the planner}}

### Existing Functionality

{{impact_existing}}

### Affected Modules

| Module | Impact | Change Type |
| --- | --- | --- |
| {{module}} | {{impact}} | New / Modified / Removed |

### Breaking Changes

{{breaking_changes}}

---

## Acceptance Criteria

- [ ] {{acceptance_criterion}}

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| {{risk}} | {{likelihood}} | {{impact}} | {{mitigation}} |

---

## Dependencies

### CR Dependencies

| CR | Title | Status | Required Before |
| --- | --- | --- | --- |
| [CR-{{dep_id}}](CR{{dep_id}}-{{dep_slug}}.md) | {{dep_title}} | {{dep_status}} | {{required_before}} |

### External Dependencies

| Dependency | Type | Status |
| --- | --- | --- |
| {{dependency}} | {{type}} | {{status}} |

---

## Linked Epics

> *Populated when CR is actioned via `/sdlc-studio cr action`*

| Epic | Title | Status |
| --- | --- | --- |
| [EP{{epic_id}}](../epics/EP{{epic_id}}-{{epic_slug}}.md) | {{epic_title}} | {{epic_status}} |

---

## Out of Scope

- {{out_of_scope_item}}

---

## Open Questions

- [ ] {{question}} -- Owner: {{question_owner}}

---

## Close Reason

> *Filled when CR is closed*

**Outcome:** {{outcome}}
**Rationale:** {{rationale}}

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| {{date}} | {{requester}} | CR proposed |
