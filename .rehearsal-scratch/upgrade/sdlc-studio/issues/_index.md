# Issue Registry – Discovery Intake

**Last Updated:** 2026-08-10

## Summary

| Status | Count |
| --- | --- |
| Open | 0 |
| Triaging | 0 |
| Triaged | 0 |
| Resolved | 0 |
| Closed | 0 |
| Won't Fix | 0 |
| Superseded | 0 |
| **Total** | **0** |

## All Issues

| ID | Title | Severity | Status | Author | Date | Triaged-into |
| --- | --- | --- | --- | --- | --- | --- |

## Notes

- An Issue is a **Discovery-backlog** item: a raw report or symptom, not yet reproduced or scoped. It carries a T-shirt **Size** (the discovery estimate) and a **Severity** (the urgency a triager prioritises on), but no story points - it is not a delivery unit.
- Lifecycle: **Open → Triaging → Triaged** (decomposed into bugs), then **Resolved** by DERIVATION when every child is resolved. Terminal: **Resolved / Closed / Won't Fix / Superseded**.
- Turn an Issue into deliverable work with `triage.py apply --issue IS-NNNN --bug 'title|points|severity'`; if it is really a change, file a CR and `refine` it instead.
- Issues are numbered globally (IS0001, IS0002, …). Cross-repo: confirm the next free number against `origin/main` before filing.
