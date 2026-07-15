# RFC-0041: A migrate command that reviews every artefact and upgrades where necessary

> **Status:** Draft
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

TBD - pending decision.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
