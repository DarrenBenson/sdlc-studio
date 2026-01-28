<!--
Template: Review Findings
File: sdlc-studio/reviews/RV{NNNN}-{artifact-id}-review.md
Status values: N/A (immutable record)
Related: help/review.md, reference-epic.md, reference-story.md
-->
# RV{{review_id}}: Review of {{artifact_type}} {{artifact_id}}

> **Artifact:** [{{artifact_id}}: {{artifact_title}}]({{artifact_path}})
> **Reviewed:** {{review_timestamp}}
> **Reviewer:** {{reviewer}}

## Summary

| Severity | Count |
|----------|-------|
| Critical | {{critical_count}} |
| Important | {{important_count}} |
| Suggestion | {{suggestion_count}} |

## Critical Issues

{{#if critical_issues}}
{{#each critical_issues}}
### {{issue_number}}. {{issue_title}}

**Location:** {{location}}
**Description:** {{description}}
**Suggested Fix:** {{fix_suggestion}}

{{/each}}
{{else}}
No critical issues found.
{{/if}}

## Important Issues

{{#if important_issues}}
{{#each important_issues}}
### {{issue_number}}. {{issue_title}}

**Location:** {{location}}
**Description:** {{description}}

{{/each}}
{{else}}
No important issues found.
{{/if}}

## Suggestions

{{#if suggestions}}
{{#each suggestions}}
- **{{location}}:** {{description}}
{{/each}}
{{else}}
No suggestions.
{{/if}}

## Changed Files Since Last Review

{{#if changed_files}}
| File | Last Modified |
|------|---------------|
{{#each changed_files}}
| {{path}} | {{modified_at}} |
{{/each}}
{{else}}
No file changes tracked for this artifact.
{{/if}}

## Cohesion Analysis (Story Generation Only)

{{#if cohesion_analysis}}
### AC Coverage

{{ac_coverage_summary}}

| Epic AC | Mapped Story | Story AC |
|---------|--------------|----------|
{{#each ac_mappings}}
| {{epic_ac}} | {{story_id}} | {{story_ac}} |
{{/each}}

### Edge Case Distribution

{{edge_case_summary}}

{{#if unhandled_edge_cases}}
**Unhandled Edge Cases:**
{{#each unhandled_edge_cases}}
- {{edge_case}} → Added to {{assigned_story}}
{{/each}}
{{/if}}

### Dependency Validation

{{dependency_summary}}

{{#if dependency_issues}}
**Issues:**
{{#each dependency_issues}}
- {{issue}}
{{/each}}
{{/if}}

### Sizing Assessment

{{sizing_summary}}

{{#if oversized_stories}}
**Oversized Stories:**
| Story | Points | AC Count | Recommendation |
|-------|--------|----------|----------------|
{{#each oversized_stories}}
| {{story_id}} | {{points}} | {{ac_count}} | {{recommendation}} |
{{/each}}
{{/if}}

### Overlap Detection

{{overlap_summary}}

{{#if overlapping_ac}}
**Potential Overlaps:**
| Story A | Story B | Similar AC | Similarity |
|---------|---------|------------|------------|
{{#each overlapping_ac}}
| {{story_a}} | {{story_b}} | {{ac_text}} | {{similarity}}% |
{{/each}}
{{/if}}
{{/if}}

## Actions Taken

{{#if actions_taken}}
{{#each actions_taken}}
- {{action}}
{{/each}}
{{else}}
No automatic actions taken.
{{/if}}

## Next Steps

{{#if next_steps}}
{{#each next_steps}}
- [ ] {{step}}
{{/each}}
{{else}}
No follow-up actions required.
{{/if}}
