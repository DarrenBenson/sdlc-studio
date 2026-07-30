# US0568: The 108 findings that hide a run id in prose are backfilled across all five run ids, with the lens honestly unknown rather than guessed

> **Status:** Done
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/audit_cost.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, sdlc-studio/bugs, sdlc-studio/change-requests, CHANGELOG.md
> **Epic:** EP0169
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As an** operator closing out an audit
**I want** the run that raised each existing finding readable as a field rather than buried in a sentence
**So that** a class recurring across runs can be counted from the record instead of reconstructed from prose, without anybody inventing the lens nobody attributed

## Acceptance Criteria

### AC1: all five run ids are seeded, with the counts pinned

- **Given** the live corpus, whose findings attribute to FIVE run ids and not the three the request named
- **When** the backfill scans it
- **Then** every one is seeded and the per-run finding counts are pinned, so a sixth id appearing later reddens the test rather than being silently skipped - the two the request missed were the two with the fewest findings, which a spot check would have missed the same way
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py::TheLiveCorpusAgreesTests::test_all_FIVE_run_ids_are_seeded_with_the_counts_pinned
- **Verified:** yes (2026-07-30)

### AC2: the closing sweep passes against the REAL tree

- **Given** every finding whose `Raised-by` prose names a run
- **When** the sweep runs over the live repository rather than a fixture
- **Then** none names a run in prose that its metadata field does not carry, because a fixture-only sweep is exactly what let four artefacts hide
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py::TheLiveCorpusAgreesTests::test_the_live_sweep_is_clean
- **Verified:** yes (2026-07-30)

### AC3: a seeded row is stamped backfilled, never recorded

- **Given** a run id lifted from prose rather than measured by this project
- **When** it is seeded into the register
- **Then** it carries `backfilled`, so no verdict can rest on an unverifiable string while reading as though it rested on a measurement
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py::ApplyStampsAndSeedsTests::test_a_seeded_run_is_BACKFILLED_never_recorded
- **Verified:** yes (2026-07-30)

### AC4: the filing run is read from the prose, never guessed

- **Given** the twelve findings naming two ids, in the shape `adversarial audit <A> carry-over, run <B>`
- **When** the filing run is resolved
- **Then** it is `<B>`, which the sentence says outright, and a line the prose does NOT disambiguate is refused rather than resolved by order - the carry-over id comes FIRST, so taking `ids[0]` would attribute twelve findings to the wrong run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py::FilingRunIsReadNotGuessedTests::test_the_carry_over_shape_is_resolved_by_the_PROSE_not_by_order
- **Verified:** yes (2026-07-30)

### AC5: the lens is explicitly unknown, and counts as unattributed

- **Given** 108 findings whose prose carries a run but no lens
- **When** each is stamped
- **Then** the lens is recorded as explicitly unknown, and `detector-owed` counts that placeholder as unattributable rather than as a lens of that name - 108 findings sharing one placeholder across five runs would otherwise read as a detector owed on every one of them, a verdict manufactured out of nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py::TheLiveCorpusAgreesTests::test_the_backfilled_corpus_does_NOT_read_as_detector_owed
- **Verified:** yes (2026-07-30)

## Summary

Split out of US0462, where it was AC5 inside a 3-point story and was self-contradicting in two separate ways.

**It named three run ids and there are five.** 108 artefacts (68 bugs, 40 CRs) carry a `wf_` id in their `Raised-by` prose: `wf_9903a6e6-53a` (50 findings), `wf_804ef18d` (42), `wf_d141ccb5` (12), `wf_b62b2ed2` (3) and `wf_95377bad` (1). Those per-run figures are the corrected ones: an earlier count of raw mentions read 108/50/24/6/2, which double-counted findings citing a run more than once and mis-assigned the twelve carry-over cases. The last two were unnamed, so BG0375, BG0376, BG0377 and BG0379 would have stayed unbackfilled - and the AC's own closing sweep, that no artefact carries a run id in prose absent from its metadata field, would then have FAILED on the real corpus. The AC could not pass itself.

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
