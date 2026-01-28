<!--
Template: Review Findings Index (Streamlined)
File: sdlc-studio/reviews/_index.md
Status values: N/A (immutable records)
Related: help/review.md, reference-review.md
-->
# Review Findings Index

Registry of all review findings for traceability and audit.

## Summary

| Metric | Value |
|--------|-------|
| Total Reviews | {{total_reviews}} |
| Open Critical Issues | {{open_critical}} |
| Open Important Issues | {{open_important}} |
| Last Review | {{last_review_date}} |

## Reviews by Artifact

| RV ID | Artifact | Type | Date | Critical | Important |
|-------|----------|------|------|----------|-----------|
{{#each reviews}}
| [RV{{review_id}}](RV{{review_id}}-{{artifact_id}}-review.md) | {{artifact_id}} | {{artifact_type}} | {{review_date}} | {{critical_count}} | {{important_count}} |
{{/each}}

## Reviews Requiring Attention

{{#if attention_required}}
| RV ID | Artifact | Critical | Reason |
|-------|----------|----------|--------|
{{#each attention_required}}
| RV{{review_id}} | {{artifact_id}} | {{critical_count}} | {{reason}} |
{{/each}}
{{else}}
No reviews currently require attention.
{{/if}}
