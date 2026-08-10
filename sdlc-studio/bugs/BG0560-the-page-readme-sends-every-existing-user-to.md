# BG0560: the page README sends every existing user to is the v4 upgrade page, so v5's breaking gate changes reach an upgrading project with no document that names them

> **Status:** Fixed
> **Severity:** High
> **Points:** 5
> **Affects:** README.md, docs/existing-users.md, .claude/skills/sdlc-studio/reference-upgrade.md, .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py
> **Evidence:** Read on the tracked tree, 2026-08-09, during a v5 release-readiness sweep. `docs/existing-users.md:1` is `# SDLC Studio v4 for existing projects` and its body describes v4's changes and the v3 numbering question. README.md lines 150, 382 and 440 all route an existing user to it, line 382 calling the update `a drop-in: no project migration, existing sdlc-studio/ directories keep working`. Measured against a v4-era fixture (schema_version 2, legacy stories, a CR carrying `Effort: M`): `migrate` reports and applies correctly, and `gate.py` immediately after it returns FAIL on conformance, reconcile and index-derived. The drop-in claim is therefore false for the gate, which is the surface an upgrading project runs in CI.
> **Verification depth:** functional (unit: the page's own upgrade steps parsed out of its fenced block and executed against a v4-era fixture, the resolved config defaults compared with the page's stated ones; mutation: 4 planned mutants applied and killed, including emptying the page's block and restoring the drop-in wording on one of three README routes)
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

> **Plan repaired after a REJECT at plan review (2026-08-09, qa seat, brief `3e9a0bbc44b9`), and
> NARROWED under D0135.** The release-notes half - the 4,001-line composed draft and the 34
> uncomposed fragments - moves to SC0007, the charter that cuts the release. The seat proved the
> two halves mechanically contradictory rather than merely large: `changelog.py compose` folds
> only into `[Unreleased]`, is destructive and all-or-nothing, and its output carries unit ids on
> essentially every bullet, so clearing the fragments produces exactly the id-laden section the
> release-notes criterion required to be free of them.
>
> **Ruling - the page is checked by EXECUTING what it says, not by grepping it.** The seat's
> sharpest finding was that "run the page's own upgrade steps" is mechanised nowhere, so a test
> hardcoding the sequence still passes after the page is reverted: it measures the fixture, not
> the document. The steps are therefore PARSED OUT of the page's own fenced command block and
> run, so a page that stops saying something stops having it checked, and a page whose steps do
> not work reddens. `Affects` gains the test file the previous plan had nowhere legal to put.

### AC1

- **Given** `docs/existing-users.md` and a v4-era fixture project
- **When** the shell commands in the page's upgrade-steps fenced block are PARSED FROM THE PAGE
  and each is run in order against the fixture
- **Then** every one exits as the page says it will, and the test fails if the page's block is
  emptied or replaced with commands that do not run - so the check cannot pass on a page that no
  longer says anything.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py -k the_pages_own_steps_are_parsed_and_executed
- **Verified:** yes (2026-08-10)
- **Mutant:** in the test, hardcode the command sequence instead of parsing it from the page - reverting the page to its v4 text must then stop reddening the test.

### AC2

- **Given** every route in `README.md` that sends an existing user to the upgrade page - the three
  at lines 150, 382 and 440, each verified present today
- **When** they are read
- **Then** none of them describes v5 as a drop-in requiring no migration, and each points at a
  page whose own title says v5. The previous plan covered one of the three.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py -k every_readme_route_points_at_the_v5_page_and_claims_no_drop_in
- **Verified:** yes (2026-08-10)
- **Mutant:** in `README.md`, restore the drop-in wording on ONE of the three routes - a test checking only the best-known route must fail to notice.

### AC3

- **Given** the defaults that decide what an existing project is held to on upgrade -
  `sprint.breakdown`, `conformance.adopt_after`, `review.two_role_after`, `review.test_plan_after`
  and `plan_review.enabled`
- **When** the page's table of what changes is compared against the values those keys actually
  resolve to
- **Then** they agree, so a page claiming a gate is dormant when it fires - or fires when it is
  dormant - reddens rather than reassuring a reader who is about to be refused.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py -k the_pages_gate_table_agrees_with_the_resolved_defaults
- **Verified:** yes (2026-08-10)
- **Mutant:** in `docs/existing-users.md`, change one row's stated default to the opposite value.

### AC4

- **Given** `reference-upgrade.md`, which covers schema v1 to v3 identity and says nothing about
  the v5 gate changes
- **When** it is read
- **Then** it names the v5 gate delta or explicitly hands the reader to the page that does, so the
  document a migration reads first does not silently omit the half that will refuse them.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py -k the_upgrade_reference_hands_off_the_v5_gate_delta
- **Verified:** yes (2026-08-10)
- **Mutant:** in `reference-upgrade.md`, delete the hand-off paragraph.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `test_existing_users_page.py`, hardcode the command sequence instead of parsing it from `docs/existing-users.md` | |
| AC2 | in `README.md`, restore the drop-in wording on ONE of the three routes | |
| AC3 | in `docs/existing-users.md`, change one row's stated default to the opposite value | |
| AC4 | in `reference-upgrade.md`, delete the hand-off paragraph | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Filed |
