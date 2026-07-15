# RFC-0040: Upgrade and migration path for the sizing and two-backlog model, before release

> **Status:** Draft
> **Decomposed-into:** EP0034
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate_v3.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/transition.py
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

This session's RFC0038 (sizing: points/T-shirt sizes) and two-backlog gates (G1 plan refuses a request, G2 terminal status derived from children, undecomposed/link-asymmetry drift, BG0148 CR-needs-Size-at-creation, BG0144 Affects-must-resolve) are UNIVERSAL, not schema-gated - they check `is_request()` with no `is_schema_v3` guard. An existing consuming project upgrading to this skill version gets the new behaviour immediately, and several changes are BREAKING: sprint plan --crs is refused (G1), marking a childless CR Complete is blocked (G2), creating a CR needs --size not --points (BG0148), a unit whose Affects names a since-renamed file flags ungroomed (BG0144), and Approved/In-Review childless CRs show as undecomposed drift. Already backward-compatible: link-asymmetry/undecomposed only fire on declared links and post-intake states (terminal CRs and link-less old artefacts are NOT flagged); legacy Points on a CR still reads; old Effort fields are ignored. All of this is UNRELEASED (freeze until ~2026-07-21), so there is a window to build the migration before it ships.

## Design Options

- **Migration pass (extend `migrate_v3.py)`: map Effort->Points/Size, add Size to pointed CRs, flag childless-Approved CRs for refinement; PLUS gate the hard workflow gates (G1/G2, BG0148 creation refusal) behind `schema_version` or a config flag so an upgrade does not break a project mid-flight until it opts in; PLUS an upgrade guide and a semver-major bump (5.0.0)**
- **Alternative rejected: ship universal with no migration - breaks every existing project's CR workflow on upgrade with no opt-in and no data migration**

## Recommendation

Option 1. Decompose into CRs: (a) migration pass in `migrate_v3.py` for the sizing fields; (b) schema/config gate for G1/G2/BG0148 so the two-backlog workflow is opt-in per project; (c) undecomposed/BG0144 as advisories (not hard drift) for a grace period; (d) upgrade guide + CHANGELOG breaking-change section + 5.0.0 bump. MUST land before the post-freeze release.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
