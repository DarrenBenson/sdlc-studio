# RFC-0041: A migrate command that reviews every artefact and upgrades where necessary

> **Status:** Accepted
> **Decomposed-into:** EP0042
> **Size:** L
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

project upgrade refreshes some conventions (it added personas) but does not sweep the whole workspace: an operator reported that after running it, the project version was not stamped and no open RFCs, CRs, epics or stories were reviewed or updated. Operators expect an upgrade to review EVERYTHING and bring each artefact to current schema/conventions. Propose a unified migrate command that reviews every artefact type and upgrades where necessary, orchestrating the existing pieces (`migrate_v3` for ids/sizing, project upgrade for conventions) and reporting what it upgrades deterministically vs what needs a human.

## Design Options

- **A single 'migrate' command that sweeps every artefact type, orchestrates `migrate_v3` + project upgrade, stamps the version, and reports deterministic-upgrade vs needs-human per artefact**
- **Extend 'project upgrade' to cover the full sweep (version stamp + open RFCs/CRs/epics/stories) rather than adding a new command**
- **Keep them separate but add a migrate orchestrator that calls both and adds the artefact-review pass**

## Recommendation

**Option C - a `migrate` orchestrator.** `project_upgrade` (conventions + version) and `migrate_v3`
(ids + sizing, with its `needs_refine`/`needs_triage`/`needs_resize`/`needs_manual` buckets) already
exist and are tested; `reconcile.undecomposed_drift` already finds accepted childless items. Option A
risks duplicating that; option B buries a real command inside `project upgrade`, against the operator's
ask for "an actual migrate command". C reuses the pieces: `migrate` runs them in order, adds the
artefact-review sweep, and emits ONE report split into what it upgraded deterministically vs what needs
a human. It auto-applies only the deterministic, reversible set (version stamp, config, container
sizing) and REPORTS the judgement items (a request's `refine`, an Issue's `triage`, a delivery unit's
re-size) with the exact command - never guessing a number the estimator would then be judged on.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Command shape: new command / extend project upgrade / orchestrator | Resolved: option C (orchestrator) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
| 2026-07-15 | sdlc-studio | Resolved D1 = option C (a migrate orchestrator over project_upgrade + migrate_v3, plus an artefact-review sweep and a deterministic-vs-needs-human report) |
