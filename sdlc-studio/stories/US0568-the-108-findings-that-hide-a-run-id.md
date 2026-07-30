# US0568: The 108 findings that hide a run id in prose are backfilled across all five run ids, with the lens honestly unknown rather than guessed

> **Status:** Draft
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/audit_cost.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, sdlc-studio/bugs, sdlc-studio/change-requests, CHANGELOG.md
> **Epic:** EP0169
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

- **AC1:** All five run ids are seeded, not three, and a test pins the count against the live corpus so a sixth id appearing later fails rather than being silently skipped.
- **AC2:** Every one of the 108 artefacts carries the run metadata field, and the closing sweep - no run id in prose absent from the metadata field - passes against the real tree rather than a fixture, because a fixture-only sweep is what let four artefacts hide.
- **AC3:** Each seeded register row is stamped `backfilled`, and a test asserts an owed verdict resting only on backfilled rows is reported differently from one resting on recorded rows.
- **AC4:** The canonical form of the suffixed id is pinned by a test that fails if the writer normalises it and the scanner does not.
- **AC5:** The lens is recorded as explicitly unknown on every backfilled artefact, and the story states that lens data begins with the next real run - so nothing in the record claims a lens nobody attributed.

## Summary

Split out of US0462, where it was AC5 inside a 3-point story and was self-contradicting in two separate ways.

**It named three run ids and there are five.** 108 artefacts (68 bugs, 40 CRs) carry a `wf_` id in their `Raised-by` prose: `wf_804ef18d` (108 mentions), `wf_9903a6e6-53a` (50), `wf_d141ccb5` (24), `wf_b62b2ed2` (6) and `wf_95377bad` (2). The last two were unnamed, so BG0375, BG0376, BG0377 and BG0379 would have stayed unbackfilled - and the AC's own closing sweep, that no artefact carries a run id in prose absent from its metadata field, would then have FAILED on the real corpus. The AC could not pass itself.

**Its stated purpose was falsified by its own mechanism.** The justification was that the backfill exercises `detector-owed` against a real corpus 'rather than only reaching its cannot-judge state'. But `detector-owed` groups by LENS, the backfill supplies RUN IDS, and `Raised-by` prose carries no lens at all. Every backfilled finding therefore lands in cannot-judge - exactly the state the AC claimed to move the corpus out of. Deriving 108 lenses is model judgement over 108 artefacts, not a mechanical pass, and pretending otherwise is how a 3-point estimate absorbs a migration.

So this unit does the honest half: it backfills RUN attribution across all five ids, records the lens as explicitly unknown, and states plainly that lens data comes from future runs and fixtures rather than from reconstruction. Guessing 108 lenses from prose written for a different purpose would be inventing evidence at scale, which is the class this project files bugs about.

**A normalisation rule is needed before the pass, not after.** `wf_9903a6e6-53a` appears 50 times and `wf_9903a6e6` once - one of them is canonical and the register must say which. That same id also appears under two different activities, 'adversarial audit' and 'audit-process-retro', so an audit run is not 1:1 with a harness workflow id.

## Steps to Reproduce

1. `grep -rhoE 'wf_[a-z0-9-]+' sdlc-studio/bugs sdlc-studio/change-requests` and count: five distinct ids, not three.
2. Read US0462's original AC5: it names three.
3. Note BG0375/0376/0377 carry only `wf_b62b2ed2` and BG0379 only `wf_95377bad`, so a three-id seed leaves four artefacts failing the AC's own sweep.

## Proposed Fix

1. Seed the register with all five ids, each row stamped provenance `backfilled` rather than `recorded`, so a reader can never mistake an id asserted from prose for one a close-out observed.
2. Rule the `wf_9903a6e6-53a` versus `wf_9903a6e6` normalisation FIRST and pin the canonical form in a test, since the writer and the scanner must agree or the sweep passes while the data is split.
3. Backfill the run metadata field on all 108, lens recorded as explicitly unknown.
4. Do NOT derive lenses from prose. State in the story that lens attribution starts with the next real run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
