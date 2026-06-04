<!--
Template: RFC Index
File: sdlc-studio/rfcs/_index.md
Status values: See reference-outputs.md
Related: help/rfc.md, reference-rfc.md
-->
# RFC Registry — Design Exploration

**Last Updated:** {{last_updated}}
**TRD Reference:** [Technical Requirements Document](../trd.md)

## Summary

| Status | Count |
| --- | --- |
| Draft | {{draft_count}} |
| In Review | {{in_review_count}} |
| Accepted | {{accepted_count}} |
| Superseded | {{superseded_count}} |
| Withdrawn | {{withdrawn_count}} |
| **Total** | **{{total_count}}** |

## All RFCs

| ID | Title | Priority | Status | Author | Date | Spawned CRs |
| --- | --- | --- | --- | --- | --- | --- |
| [RFC-{{rfc_id}}](RFC{{rfc_id}}-{{slug}}.md) | {{title}} | {{priority}} | {{status}} | {{author}} | {{date}} | {{spawned_crs}} |

## Notes

- An RFC explores an **unsettled** design space (multiple options, open decisions) BEFORE a CR commits a change. Use a CR directly when the change is already clear.
- Lifecycle: **Draft → In Review → Accepted** (then spawns CRs). Terminal: **Superseded / Withdrawn**.
- An **Accepted** RFC is not "done" — it stays the living design home its CRs reference.
- RFCs are numbered globally (RFC-0001, RFC-0002, …). Cross-repo: confirm the next free number against `origin/main` before filing.
- Promote with `/sdlc-studio rfc accept --rfc RFC-NNNN` (records the decision + spawns/links the workstream CRs).
