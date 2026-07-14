<!--
Template: User Story (Streamlined)
File: sdlc-studio/stories/US{NNNN}-{slug}.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->
# US{{story_id}}: {{story_title}}

> **Status:** {{status}}
> **Epic:** [EP{{epic_id}}: {{epic_title}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)
> **Persona:** {{persona_name}}
> **Serves:** {{optional - design personas whose End Goals this story serves; names must resolve to persona files (validate serves)}}
> **Owner:** {{owner}}
> **Reviewer:** {{reviewer}}
> **Estimated-by:** {{who made the size call - so the report can tell you your own hit rate}}
> **Delivered-by:** {{the model that delivered it - written at close, not at filing}}
> **Created:** {{created_date}}
> **GitHub Issue:** {{github_issue}}
> **Affects:** {{source files this story touches, comma-separated}}
> **Plan-Review:** {{plan_review}}

<!-- Affects: the source files this story changes. Declaring it lets the engagement floor
     confirm a single-file change is genuinely small; a multi-file change without an acceptance
     criterion is refused. See reference-config.md#engagement-floor. -->

<!-- Plan-Review (schema v3, optional): the plan-review gate's verdict for a spec-derived
     story, as `verdict · reviewer · date` - recorded via `plan_review record` (which pins the
     ACs by fingerprint). Leave blank when the gate does not apply. A `> **Plan-Review-Override:**`
     field here is the only sanctioned skip of the gate (auditable). See reference-config.md#plan-review. -->

## User Story

**As a** {{persona_name}}
**I want** {{capability}}
**So that** {{benefit}}

## Context

### Persona Reference

**{{persona_name}}** - {{persona_summary}}
[Full persona details](../personas.md#{{persona_anchor}})

### Background

{{background}}

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type | Constraint | AC Implication |
| --- | --- | --- | --- |
| Epic | {{epic_constraint_type}} | {{epic_constraint}} | {{constraint_ac}} |
| PRD | Performance | {{performance_constraint}} | {{performance_ac}} |
| PRD | Security | {{security_constraint}} | {{security_ac}} |

---

## Acceptance Criteria

### AC1: {{ac1_name}}

- **Given** {{ac1_given}}
- **When** {{ac1_when}}
- **Then** {{ac1_then}}
- **Verify:** {{ac1_verify}}
- **Verification target:** {{ac1_verification_target}}
- **Mutation-checked:** {{ac1_mutation_checked}}
- **Verified:** no

### AC2: {{ac2_name}}

- **Given** {{ac2_given}}
- **When** {{ac2_when}}
- **Then** {{ac2_then}}
- **Verify:** {{ac2_verify}}
- **Verification target:** {{ac2_verification_target}}
- **Mutation-checked:** {{ac2_mutation_checked}}
- **Verified:** no

### AC3: {{ac3_name}}

- **Given** {{ac3_given}}
- **When** {{ac3_when}}
- **Then** {{ac3_then}}
- **Verify:** {{ac3_verify}}
- **Verification target:** {{ac3_verification_target}}
- **Mutation-checked:** {{ac3_mutation_checked}}
- **Verified:** no

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.
>
> **Mutation-checked** answers a prior question the tiers assume: *would the test go red if the feature were broken?* For any behaviour-bearing AC (`functional` and above), break the feature on purpose (unset the field the loader delivers, revert the component to a stub, invert the guard), confirm the AC's test **fails**, then restore. Record the result, e.g. `unsetting reAttestation turns governance-lifecycle GP1 red`. Leave `n/a` only for pure config/layout ACs with no runtime behaviour. A test never seen to fail cannot gate a release - see `reference-test-best-practices.md#assertion-integrity`.

---

## Scope

### In Scope

- {{in_scope_item}}

### Out of Scope

- {{out_of_scope_item}}

---

## Technical Notes

{{technical_notes}}

### API Contracts

{{api_contracts}}

### Data Requirements

{{data_requirements}}

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| {{edge_case}} | {{expected_behaviour}} |

> **Minimum edge cases:** {{config.story_quality.edge_cases.api}} for API stories, {{config.story_quality.edge_cases.other}} for others

---

## Test Scenarios

- [ ] {{test_scenario}}

> **Minimum test scenarios:** {{config.story_quality.test_scenarios.api}} for API stories, {{config.story_quality.test_scenarios.ui}} for UI

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| [US{{dep_story_id}}](US{{dep_story_id}}-{{dep_slug}}.md) | {{type}} | {{what_needed}} | {{status}} |

### External Dependencies

| Dependency | Type | Status |
| --- | --- | --- |
| {{dependency}} | {{dependency_type}} | {{dependency_status}} |

---

## Estimation

**Story Points:** {{story_points}}
**Complexity:** {{complexity}}

---

## Rollback Envelope

> Required when `affects_production_runtime: true`; optional otherwise. See `reference-story.md#rollback-envelope`.

**Affects production runtime:** {{affects_production_runtime}}

| Component | Reversal | Expected time |
| --- | --- | --- |
| {{component}} | {{reversal_command_or_steps}} | {{reversal_eta}} |

If `affects_production_runtime: false`, replace with: *Not applicable – story does not change runtime behaviour.*

---

## Open Questions

- [ ] {{question}} - Owner: {{question_owner}}

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| {{revision_date}} | {{revision_author}} | {{revision_change}} |
