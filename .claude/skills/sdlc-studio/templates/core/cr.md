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
> **Size:** {{size}}
> **Requester:** {{requester}}
> **Estimated-by:** {{who made the size call - so the report can tell you your own hit rate}}
> **Delivered-by:** {{the model that delivered it - written at close, not at filing}}
> **Date:** {{date}}
> **Affects:** {{affects}}
> **Depends on:** {{depends_on}}
> **GitHub Issue:** {{github_issue}}

<!--
A CR carries a T-shirt `**Size:**` (S / M / L / XL), NOT story points. A CR is a REQUEST - it is
not a unit of work until someone decomposes it into stories, and pointing it is guessing at a
shape that does not exist yet. A T-shirt size is coarse ON PURPOSE: it says "roughly this big"
before the stories are known. Story points (the modified Fibonacci scale) belong on the DELIVERY
unit - a story or a bug - which is measured against actuals. A value off the size scale is
REFUSED, never rounded. The answer to a CR that feels too big is to DECOMPOSE it, not to size it
harder.
-->

## Summary

{{summary}}

## Problem

{{problem_statement}}

---

## Proposed Changes

### Item 1: {{item_1_title}}

<!-- `Item points`, never `Points`: story points belong on the stories this CR decomposes into,
and a per-item field spelled `Points` would be mis-read as a CR-level size (the CR is sized by
its T-shirt `Size` above, not by points). Keep the per-item estimate spelled `Item points`. -->

**Item priority:** {{item_1_priority}}
**Item points:** {{item_1_points}}

{{item_1_description}}

<!-- Add more items as needed:
### Item 2: {{item_2_title}}
-->

---

## Impact Assessment

<!-- The CR's own size is the T-shirt `**Size:**` in the metadata block above (S/M/L/XL), not
points. A CR is a request, sized before it is decomposed; story points belong on the stories. -->

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
