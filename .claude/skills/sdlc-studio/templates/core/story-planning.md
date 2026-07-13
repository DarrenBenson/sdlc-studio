<!--
Template: User Story (Planning tier)
File: sdlc-studio/stories/US{NNNN}-{slug}.md
Status values: See reference-outputs.md
Tier: the lean pre-implementation shape - what a story must settle to be planned and
      prioritised, and nothing more. Promote to the full tier (`artifact.py promote`) before
      implementation; the transition gate refuses In Progress/Review/Done until the deferred
      sections are present. Promotion adds them as empty scaffolds - it gives you the headings
      and the obligation to fill them, not the content.
Related: help/story.md, reference-story.md, templates/core/story.md
-->
# US{{story_id}}: {{story_title}}

> **Status:** {{status}}
> **Template:** planning
> **Epic:** [EP{{epic_id}}: {{epic_title}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)
> **Persona:** {{persona_name}}
> **Created:** {{created_date}}

## User Story

**As a** {{persona_name}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: {{ac1_name}}

- **Given** {{ac1_given}}
- **When** {{ac1_when}}
- **Then** {{ac1_then}}
- **Verify:** {{ac1_verify}}
- **Verification target:** {{ac1_verification_target}}

### AC2: {{ac2_name}}

- **Given** {{ac2_given}}
- **When** {{ac2_when}}
- **Then** {{ac2_then}}
- **Verify:** {{ac2_verify}}
- **Verification target:** {{ac2_verification_target}}

> **Verification target tiers:** `functional` | `conversational` | `soak` | `live` - see `reference-test-best-practices.md#verification-depth-tiers`. The `- **Mutation-checked:**` and `- **Verified:**` lines arrive with promotion: they record work only implementation can do.

## Scope

### In Scope

- {{in_scope_item}}

### Out of Scope

- {{out_of_scope_item}}

## Technical Notes

{{technical_notes}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| {{revision_date}} | {{revision_author}} | {{revision_change}} |
