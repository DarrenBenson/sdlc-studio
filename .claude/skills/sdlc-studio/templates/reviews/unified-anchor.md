<!--
Template: Unified Review Anchor (LATEST.md)
File: sdlc-studio/reviews/LATEST.md (overwritten on every full /sdlc-studio review run)
Status values: N/A (immutable record; the dated RV{NNNN}-unified-*.md is the historical copy)
Related: help/review.md, reference-review.md, templates/reviews/findings.md

Purpose: First-read orientation for fresh conversations. CLAUDE.md should point at this
file as the entry-point so a new session can absorb current project state in one read.
The dated RV{NNNN}-unified-review-*.md remains the audit trail; LATEST.md is the
stable filename pointing at the most recent unified anchor.

Rule: rewritten on every `/sdlc-studio review` run that is not `--focus {single-doc}`.
Do not edit by hand; edit the latest dated `RV{NNNN}-unified-*.md` instead.
-->

# {{review_id}} – Unified Review – {{project_version}} + {{anchor_event}}

> **Review type:** Unified PRD/TRD/TSD/Persona consolidation
> **Reviewer:** {{reviewer}}
> **Date:** {{review_date}}
> **Triggered by:** {{trigger_summary}}
> **Project version:** {{project_version}}
> **Predecessor unified:** {{predecessor_review_id}}

## Headline

{{one_paragraph_state_of_the_project}}

```
══════════════════════════════════════════════════════════
                   DOCUMENT REVIEW SUMMARY
══════════════════════════════════════════════════════════

📋 PRD REVIEW ({{prd_findings_id}})    {{prd_status}}
   {{prd_summary_line_1}}
   {{prd_summary_line_2}}
   {{prd_verdict}}

📐 TRD REVIEW ({{trd_findings_id}})    {{trd_status}}
   {{trd_summary_line_1}}
   {{trd_summary_line_2}}
   {{trd_verdict}}

🧪 TSD REVIEW ({{tsd_findings_id}})    {{tsd_status}}
   {{tsd_summary_line_1}}
   {{tsd_summary_line_2}}
   {{tsd_verdict}}

👥 PERSONA REVIEW ({{persona_findings_id}})  {{persona_status}}
   {{persona_summary_line_1}}
   {{persona_summary_line_2}}
   {{persona_verdict}}

──────────────────────────────────────────────────────────
📝 CHANGE REQUESTS

   Proposed: {{cr_proposed_count}}{{cr_proposed_drift_note}}
   In Progress: {{cr_inprogress_count}}{{cr_inprogress_drift_note}}
   Complete: {{cr_complete_count}}

──────────────────────────────────────────────────────────
🔗 CROSS-DOCUMENT CONSISTENCY

   PRD → TRD: {{prd_trd_status}}
   TRD → TSD: {{trd_tsd_status}}
   PRD → TSD: {{prd_tsd_status}}
   PRD → Persona: {{prd_persona_status}}
   Persona → CRs / Stories: {{persona_artefact_status}}
   Persona → Persona: {{persona_consistency_status}}

──────────────────────────────────────────────────────────
📌 PRIORITY ACTIONS

{{priority_actions_block}}

──────────────────────────────────────────────────────────
🚀 PRODUCTION STATE

{{production_state_block}}

══════════════════════════════════════════════════════════
```

## Persona Delta

What changed since the predecessor unified review:

| Persona | Change | Why |
| --- | --- | --- |
| {{persona_name}} | {{persona_change_kind}} | {{persona_change_rationale}} |

If no personas changed, replace with: *No persona deltas since {{predecessor_review_id}}.*

## Cross-Document Consistency Detail

Detailed findings from the cross-doc consistency check. Brief one-liner per row; link to the relevant `RV{NNNN}-*-review.md` for depth.

| Check | Result | Detail |
| --- | --- | --- |
| PRD → TRD coverage | {{prd_trd_result}} | {{prd_trd_detail}} |
| TRD → TSD coverage | {{trd_tsd_result}} | {{trd_tsd_detail}} |
| PRD NFR → TSD gates | {{prd_tsd_result}} | {{prd_tsd_detail}} |
| PRD → Persona refs | {{prd_persona_result}} | {{prd_persona_detail}} |
| Persona → CR/Story activity | {{persona_artefact_result}} | {{persona_artefact_detail}} |
| Persona → Persona consistency | {{persona_consistency_result}} | {{persona_consistency_detail}} |

## Auto-Fixes Applied This Review

Mechanical fixes the review applied automatically (no judgment required). See `reference-review.md#3b-auto-apply-mechanical-fixes` for the exhaustive list of categories.

{{auto_fixes_applied_block}}

If empty, replace with: *No auto-fixes were necessary.*

## Priority Actions (next session pickup)

{{priority_actions_detail_block}}

If empty, replace with: *No priority actions blocking the next session.*

## Production State Snapshot

For projects with a deployed runtime – capture the state at review time so a fresh-session reader can orient without polling. Skip this section for non-deployed projects (libraries, tools, work-in-progress greenfield).

| Aspect | State |
| --- | --- |
| Version live | {{prod_version}} |
| Topology | {{prod_topology}} |
| Health | {{prod_health}} |
| Last deploy | {{prod_last_deploy}} |
| Test suite | {{test_suite_summary}} |
| Coverage gate (CI) | {{coverage_gate_summary}} |

## Files Updated This Review

| File | Change |
| --- | --- |
| {{file_path}} | {{change_summary}} |

If empty, replace with: *No artefact files were modified by this review run.*

## See Also

- `templates/reviews/findings.md` – per-artefact RV{NNNN} findings template (the inputs to this anchor)
- `reference-review.md#review-workflow` – full unified review workflow
- `help/review.md` – command quick reference
- {{predecessor_review_path}} – the previous unified anchor for delta comparison

---

> **First-read in fresh conversations:** point CLAUDE.md (or the project's equivalent orientation file) at this file as the canonical entry point. The unified anchor survives compaction better than narrative docs because it is a *snapshot*, not a *stream*.
