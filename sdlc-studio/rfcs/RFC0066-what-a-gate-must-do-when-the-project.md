# RFC-0066: What a gate must do when the project config exists but cannot be read because PyYAML is absent

> **Status:** Delivered
> **Forced-override:** 2026-11-17: --force waived 1 gate(s) on Accepted - RFC0066 cannot be Accepted: its status is DERIVED from its children, and 1 is/are not yet resolved: CR0731 (Proposed). Finish or close them first
> **Decomposed-into:** CR0731
> **Evidence:** audit AUDIT-2026-11-17, project profile, prd lens, survived 2 of 3 refute votes; observed at sdlc-studio/prd.md Section 1 Tech Stack (lines 141-144) against Mission 'Gates over goodwill' (lines 78-81) and Section 4 Business Logic Rules (lines 481-483)
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:45Z

## Summary

The PRD states that no third-party package is required, and that PyYAML is used for config when present and degrades to the caller's default when absent. It also states, in its mission and its business logic rules, that a gate's escape is a recorded operator decision, never an omission, and that an absent config blocks rather than disarms. The two cannot both hold for any gate whose shipped default is off or weaker than the project's setting. On a machine without PyYAML the project's whole `.config.yaml` is not applied, so opted-in gates such as `two_backlog.enforce`, `constitution.enforce`, `review.line_coverage` and `review.author_self_check` fall back to their defaults with one warning on stderr and an unchanged exit code. The warn-and-default path was chosen deliberately by earlier work, but the PRD has no requirement for the case where a config exists and cannot be read, so the design question is open at the requirements level.

## Design Options

- **Keep warn-and-default and say so: the PRD and TRD state plainly that gates armed by config need PyYAML, and the gate-bearing rule is reworded to exclude an unreadable config**
- **Refuse at gates only: a gate-bearing command exits non-zero when `.config.yaml` exists and PyYAML is absent, while read-only commands keep the warning; the escape is a recorded config-free flag**
- **Remove the dependency: read the config with a small stdlib parser for the subset of YAML the config uses, so the stdlib-only claim becomes true and no gate can disarm this way**
- **Make PyYAML required: the installer and the prerequisite check refuse without it, and the PRD drops the stdlib-only claim**

## Recommendation

Refuse at gates only. It honours the PRD's own rule that an escape is recorded and never an omission, it keeps the documented PyYAML-free path for reading and reporting, and it is a small change beside the existing unparseable-config refusal in `lib/sdlc_md.py`. Whichever option is chosen, record it as an ADR and correct the PRD's tech stack and business logic sentences so they agree with each other.

## Decision

**PyYAML is required** (operator, 2026-11-17, D0505), chosen over the recommended refusal at gates only. The installer and the prerequisite check refuse without it, no command reads a present config as defaults, and the PRD and TRD drop the standard-library-only claim.

**Spawned CRs:** CR0731. CR0714 is reconciled with this ruling when it is refined.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: Keep warn-and-default and say so: the PRD and TRD state plainly that gates armed by config need PyYAML, and the gate-bearing rule is reworded to exclude an unreadable config, Refuse at gates only: a gate-bearing command exits non-zero when `.config.yaml` exists and PyYAML is absent, while read-only commands keep the warning; the escape is a recorded config-free flag, Remove the dependency: read the config with a small stdlib parser for the subset of YAML the config uses, so the stdlib-only claim becomes true and no gate can disarm this way or Make PyYAML required: the installer and the prerequisite check refuse without it, and the PRD drops the stdlib-only claim | Resolved: PyYAML is required; the installer and the prerequisite check refuse without it (D0505). -> CR0731 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-17 | rfc resolve (operator decision) | resolve: D1 - PyYAML is required; the installer and the prerequisite check refuse without it (D0505). |
| 2026-11-17 | transition set --force | forced RFC0066 -> Accepted, waiving 1 gate(s): RFC0066 cannot be Accepted: its status is DERIVED from its children, and 1 is/are not yet resolved: CR0731 (Proposed). Finish or close them first |
