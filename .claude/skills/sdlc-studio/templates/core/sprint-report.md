# Sprint Report: {{run_id}}

<!-- repeat: invalidation -->
> **INVALIDATED** - signed at fingerprint `{{signed_fingerprint}}`; re-deriving this report from
> the tree now yields `{{current_fingerprint}}`. Moved: {{moved_figures}}. The sign-off below
> records what WAS signed and is left standing; re-prepare the report to sign the tree as it is.
<!-- end -->

## Goal

{{sprint_goal}}

**Verdict: {{goal_verdict}}** - {{goal_verdict_note}}

> **Run:** {{started_at}} to {{ended_at}} ({{duration_hours}})
> **Verified on:** {{verified_sha}}   **Fingerprint:** {{report_fingerprint}}

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
<!-- repeat: estimates -->
| {{est_measure}} | {{est_forecast}} | {{est_actual}} | {{est_ratio}} | {{est_basis}} |
<!-- end -->

<!-- when: estimates_units -->
Each unit's minutes and tokens are measured over its own open span. Units open at the same time
share hours and tokens, so these spans may overlap and are never added up into the run's figures
above.

| Unit | Forecast minutes | Minutes (open span) | Forecast tokens | Tokens (open span) |
| --- | --- | --- | --- | --- |
<!-- repeat: estimates_units -->
| {{unit_id}} | {{eu_forecast_minutes}} | {{eu_minutes}} | {{eu_forecast_tokens}} | {{eu_tokens}} |
<!-- end -->
<!-- end -->

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | {{planned_units}} | {{planned_points}} |
| Delivered of the plan | {{plan_delivered_units}} | {{plan_delivered_points}} |
| Added mid-run and delivered | {{added_delivered_units}} of {{added_units}} added | {{added_points}} |
| Dropped | {{dropped_units}} | {{dropped_points}} |
| Carried undelivered | {{carried_units}} | {{carried_points}} |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: {{points_delivered}}.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
<!-- repeat: plan_units -->
| {{unit_id}} | {{unit_planned_points}} | {{unit_points}} | {{unit_outcome}} | {{unit_rounds}} |
<!-- end -->

## Known issues handed over

{{findings_scan}}

<!-- when: known_issues_rows -->
| Issue | Priority | Detail |
| --- | --- | --- |
<!-- repeat: issues -->
| {{issue_id}} | {{issue_priority}} | {{issue_detail}} |
<!-- end -->
<!-- end -->
<!-- unless: known_issues_rows -->
No open finding, close gap or carried unit is recorded.
<!-- end -->

## Sign-off

| Reviewer of record | Date | Fingerprint signed |
| --- | --- | --- |
| {{principal}} | {{signed_at}} | {{signed_fingerprint}} |

Signing records the principal, the date and this report's fingerprint against {{run_id}}.

## Appendix

### Tokens by model

<!-- when: cost_measured -->
| Model | Tokens |
| --- | --- |
<!-- repeat: models -->
| {{model_name}} | {{model_tokens}} |
<!-- end -->

Total {{tokens_total}}, of which delegated {{tokens_delegated}}. Coverage: {{token_coverage}};
{{token_shape}}.
<!-- end -->
<!-- unless: cost_measured -->
NOT MEASURED - {{cost_reason}}

Delegated: {{tokens_delegated}}.
<!-- end -->

### DORA

<!-- when: dora_measured -->
| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
<!-- repeat: dora -->
| {{dora_key}} | {{dora_value}} | {{dora_mapping}} | {{dora_band}} | {{dora_source}} |
<!-- end -->
<!-- end -->
<!-- unless: dora_measured -->
NOT MEASURED - {{dora_reason}}
<!-- end -->

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | {{cal_tokens_per_point}} | {{cal_tokens_source}} |
| Minutes per point | {{cal_minutes_per_point}} | {{cal_minutes_source}} |

### Rulings

<!-- when: rulings_measured -->
Persona seats ruled {{persona_rulings}} time(s), {{cited_rulings}} of them by citing a
precedent; the operator ruled {{operator_rulings}} time(s).
<!-- end -->
<!-- unless: rulings_measured -->
NOT MEASURED - {{rulings_reason}}
<!-- end -->

### Waivers in force

<!-- when: waivers_measured -->
{{waivers_note}}

<!-- repeat: waivers -->
- **{{waiver_id}}** - {{waiver_subject}} ({{waiver_date}}): {{waiver_reason}}
<!-- end -->
<!-- end -->
<!-- unless: waivers_measured -->
NOT MEASURED - {{waivers_reason}}
<!-- end -->

<!-- when: lane_yield_present -->
### Lane yield

<!-- when: lane_yield_measured -->
{{lane_yield_note}} A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

<!-- when: lane_yield_rows -->
| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
<!-- repeat: lane_yield -->
| {{yield_lane}} | {{yield_refusals}} | {{yield_catches}} | {{yield_paperwork}} | {{yield_verdict}} |
<!-- end -->
<!-- end -->
<!-- end -->
<!-- unless: lane_yield_measured -->
NOT MEASURED - {{lane_yield_reason}}
<!-- end -->
<!-- end -->

<!-- when: lessons_present -->
### Lessons

<!-- when: lessons_measured -->
{{lessons_note}}

<!-- when: lessons_rows -->
| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
<!-- repeat: lessons -->
| {{lesson_id}} | {{lesson_class}} | {{lesson_state}} | {{lesson_hits_run}} | {{lesson_hits_total}} |
<!-- end -->
<!-- end -->
<!-- end -->
<!-- unless: lessons_measured -->
NOT MEASURED - {{lessons_reason}}
<!-- end -->
<!-- end -->
