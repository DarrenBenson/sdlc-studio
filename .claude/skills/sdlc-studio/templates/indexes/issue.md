<!--
Template: Issue Index
File: sdlc-studio/issues/_index.md
Status values: See reference-outputs.md
Related: help/issue.md, help/triage.md
-->
# Issue Registry – Discovery Intake

**Last Updated:** {{last_updated}}

## Summary

| Status | Count |
| --- | --- |
| Open | {{open_count}} |
| Triaging | {{triaging_count}} |
| Triaged | {{triaged_count}} |
| Resolved | {{resolved_count}} |
| Closed | {{closed_count}} |
| Won't Fix | {{wont_fix_count}} |
| Superseded | {{superseded_count}} |
| **Total** | **{{total_count}}** |

## All Issues

| ID | Title | Severity | Status | Author | Date | Triaged-into |
| --- | --- | --- | --- | --- | --- | --- |
| [IS{{issue_id}}](IS{{issue_id}}-{{slug}}.md) | {{title}} | {{severity}} | {{status}} | {{author}} | {{date}} | {{triaged_into}} |

## Notes

- An Issue is a **Discovery-backlog** item: a raw report or symptom, not yet reproduced or scoped. It carries a T-shirt **Size** (the discovery estimate) and a **Severity** (the urgency a triager prioritises on), but no story points - it is not a delivery unit.
- Lifecycle: **Open → Triaging → Triaged** (decomposed into bugs), then **Resolved** by DERIVATION when every child is resolved. Terminal: **Resolved / Closed / Won't Fix / Superseded**.
- Turn an Issue into deliverable work with `triage.py apply --issue IS-NNNN --bug 'title|points|severity'`; if it is really a change, file a CR and `refine` it instead.
- Issues are numbered globally (IS0001, IS0002, …). Cross-repo: confirm the next free number against `origin/main` before filing.
