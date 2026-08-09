# BG0560: the page README sends every existing user to is the v4 upgrade page, so v5's breaking gate changes reach an upgrading project with no document that names them

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** docs/existing-users.md, README.md, CHANGELOG.md, .claude/skills/sdlc-studio/reference-upgrade.md
> **Evidence:** Read on the tracked tree, 2026-08-09, during a v5 release-readiness sweep. `docs/existing-users.md:1` is `# SDLC Studio v4 for existing projects` and its body describes v4's changes and the v3 numbering question. README.md lines 150, 382 and 440 all route an existing user to it, line 382 calling the update `a drop-in: no project migration, existing sdlc-studio/ directories keep working`. Measured against a v4-era fixture (schema_version 2, legacy stories, a CR carrying `Effort: M`): `migrate` reports and applies correctly, and `gate.py` immediately after it returns FAIL on conformance, reconcile and index-derived. The drop-in claim is therefore false for the gate, which is the surface an upgrading project runs in CI.
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

v5 changes what a project is held to, and no consuming-facing document states the delta. Two changes are load-bearing and both were found by execution rather than by reading:

`sprint.breakdown` defaults to `enforce` and refuses a plan over any unit missing `Affects` or `Points`, with the config comment stating that omission is not an escape and an absent config BLOCKS. An upgrading project's entire legacy backlog predates both fields, so the first thing v5 does to an existing user is refuse to plan their backlog. This repo's own backlog carries 20 such units.

`conformance.adopt_after` defaults to null, documented as `Unset (default) judges every story`. An upgrading project's whole history is therefore judged against a gate that did not exist when it was written, and `gate.py` fails on the first run after a clean migrate.

Both have correct remedies - the grooming pass, and a recorded adoption cutoff - and neither is discoverable from any page a user is pointed at. RFC0040 anticipated exactly this class and required an upgrade guide plus a CHANGELOG breaking-change section before the post-freeze release; the guide was written for v4 and never revised. The reference-upgrade.md that does exist covers schema v1 to v3 identity, not the v5 gate changes.

Separately, the draft `## [5.0.0]` CHANGELOG section is 4,001 lines of composed fragment prose carrying unit ids and internal review narratives, and 34 further fragments are uncomposed - the release gate names them: `run changelog.py compose before tagging`. That is currently what a user would read as v5's release notes.

## Steps to Reproduce

1. `head -1 docs/existing-users.md` - it says v4. 2. `grep -n existing-users README.md` - three routes to it, one of them calling v5 a drop-in. 3. Build a v4-era fixture: init a project, set `schema_version: 2`, add a Done story and a Ready story with no Affects/Points, and a CR with `Effort: M`. 4. `migrate.py --root <fixture> --apply`. 5. `gate.py --root <fixture>` - FAIL on conformance, reconcile and index-derived. 6. `sprint.py plan --root <fixture> --worklist <ready story> --write` - refused as ungroomed. Neither refusal is named on any page the README points an upgrading user at.

## Proposed Fix

Rewrite docs/existing-users.md as the v5 page and keep the v4 content only where it is still true. It must name every gate whose default changes what an existing project is held to, state the remedy for each beside it, and be honest that the gate is red until the remedy is applied - the current drop-in wording is the specific claim the fixture falsifies. Add the CHANGELOG breaking-change section RFC0040 required, and hand-author the v5.0.0 release notes rather than shipping 4,001 lines of composed fragments. Cross-check the page against the fixture rather than against the source: the two defects above were both invisible to reading and both fell out of one migrate-then-gate run, which is the pass this page should be verified by.

## Acceptance Criteria

- [ ] **AC1** docs/existing-users.md describes v5 and names every default whose change alters what an existing project is held to, each with its remedy - verified by running the page's own upgrade steps against a v4-era fixture and reaching a green gate
- [ ] **AC2** No claim on the page survives that the fixture falsifies, and the drop-in wording in README.md is corrected to match whatever the fixture proves
- [ ] **AC3** CHANGELOG.md carries a v5.0.0 breaking-change section naming the same set, and the release gate's changelog-fragments lane passes with no uncomposed fragments
- [ ] **AC4** The v5.0.0 release notes are hand-authored for a reader outside this repository and carry no internal unit id as their only explanation of a change

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Filed |
