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
> **Estimated-by:** {{who made the Effort call - so the report can tell you your own hit rate}}
> **Delivered-by:** {{the model that delivered it - written at close, not at filing}}
> **Date:** {{date}}
> **Affects:** {{affects}}
> **Depends on:** {{depends_on}}
> **GitHub Issue:** {{github_issue}}

<!--
The CR's own `**Effort:**` (S, M, L, or `unknown`) sits under Impact Assessment below. `unknown`
is a real answer: it satisfies the grooming gate, so nobody has to invent a size to get the CR
planned, and it is excluded from every accuracy figure rather than coerced into a number. A size
guessed to satisfy a gate is worse than no size, because it looks like data.
-->

## Summary

{{summary}}

## Problem

{{problem_statement}}

---

## Proposed Changes

### Item 1: {{item_1_title}}

<!-- `Item effort`, not `Effort`: `Effort` is the CR's own job size, read by the planner from
the FIRST match in the document. A per-item field spelled the same way shadows it, and the CR
plans as unsized. -->

**Item priority:** {{item_1_priority}}
**Item effort:** {{item_1_effort}}

{{item_1_description}}

<!-- Add more items as needed:
### Item 2: {{item_2_title}}
-->

---

## Impact Assessment

**Effort:** {{S|M|L, or `unknown` - the CR's own job size, read by the planner}}

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
