# US0369: correct the CR0304 TRD sentence and disposition the doc-drift residuals

> **Status:** Review
> **Delivers:** CR0365
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0129
> **Points:** 3
> **Affects:** sdlc-studio/trd.md

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the TRD sentence CR0304 flagged is corrected

- **Given** the TRD sentence CR0304 recorded as false
- **When** a reader compares it with the shipped behaviour
- **Then** the sentence states what actually ships, and the correction is dated in the TRD's revision history rather than made silently
- **Verify:** grep 'Revision History' sdlc-studio/trd.md
- **Verified:** yes (2026-07-24)

### AC2: every doc-drift residual is dispositioned, none left silent

- **Given** the doc-drift residuals CR0365's sweep found
- **When** the pass finishes
- **Then** each residual is either corrected or explicitly declined with a reason - the discipline the retro already enforces, applied here, because silence is what let twelve requests derive Complete over unmet criteria
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::DocDriftResidualTests::test_every_residual_is_corrected_or_declined_with_a_reason
- **Verified:** yes (2026-07-24)

## Residual disposition

Every row of CR0365's residual table, with what happened to it. `corrected` = fixed in this
unit; `refiled` = a named unit owns it; `declined` = deliberately not done, with the reason.
`test_conformance.py::DocDriftResidualTests` reads CR0365's own table and this one, so a
residual added there and left out here fails the suite rather than going quiet.

| From | Disposition | Reason |
| --- | --- | --- |
| CR0281 | declined | The PRD Coverage note names eight workstreams while the tables cover more. Checked at prd.md:14-19 and it still reads that way, but the note is a narrative summary that nothing parses, and the count will be stale again after the next workstream. The defect is the shape (an enumeration where a pointer belongs), not the number, and re-counting it here would buy one correct sentence and the same drift next sprint. prd.md is also outside this unit's declared surface. |
| CR0284 | refiled | US0370 carries AC1 as an AC defect, per CR0365's own criterion that the AC-correction cases are recorded as AC defects rather than as outstanding build work. The VELOCITY.md backfill and the RETRO0028 ratio are not covered by that unit and remain genuinely outstanding - stated here rather than folded into US0370's scope, so the gap is visible. |
| CR0294 | declined | Re-checked today: US0166 AC1 and AC2 still carry byte-identical whole-file `-p test_close_guard.py` selectors, so the residual is real and unrepaired. Not corrected here: US0166 is another unit's artefact and editing a third party's Verify lines from this unit would rewrite a Done story's evidence without its owner. The duplicate-verifier lint shipped and already reports this pair, so the finding is not lost. |
| CR0298 | declined | Cross-reference only. The close-ceremony report step shipped, in reference-sprint.md rather than the reference-retro.md the AC named. Nothing is missing or wrong; correcting a delivered CR's AC text to match where the code landed changes no behaviour and rewrites history to look tidier than it was. |
| CR0299 | declined | Re-checked and no longer outstanding: templates/workflows/release-gate.md line 22 now carries `gate.py --root . --release` as its own checklist item, ahead of the version/budget/link checks the residual said had been mistaken for the enforcement. The gap the residual describes was closed by later work; nothing here to correct. |
| CR0302 | corrected | trd.md's two remaining exact component counts are now growth-tolerant bands: §1 "58 scripts" -> "60+ scripts" and ADR-001 "52 reference files, 41 help files" -> "50+ / 40+" (actual 69, 54, 44). This matches §3's existing band convention. The freshness GUARD half is US0367's, and it should land against corrected counts - a test that needs the live TRD to stay wrong would be a guard anchored to the defect. |
| CR0304 | corrected | §6 Migrations claimed `SKILL.md`'s type table points an `upgrade` type at reference-upgrade.md. It carries no `upgrade` row at all; the operator-facing types are `migrate` and `skill-update`, and reference-upgrade.md is reached from the Progressive Loading Guide's "Schema upgrade (project artifacts)" row. The sentence now says that, and the correction is dated in the TRD changelog rather than made silently. |
| CR0334 | refiled | US0370 owns it, as an AC defect rather than build work: the fingerprint deliberately excludes AC body prose and the delivering story said so, which makes AC2 over-broad as written. |
| CR0338 | corrected | conformance.py's repo-wide doc-coverage finding said "at least one undocumented item" and told the operator to run doc_coverage.py to learn which. The check already returns the names, so the finding now states the count and names the items, and the remedy says how to catalogue them instead of how to rediscover them. Pinned by `DocCoverageGapNamedTests`. |
| CR0340 | refiled | US0368 owns it: the pre-commit test-relevant set omits help/ and SKILL.md while three shipped tests read them. |
| CR0357 | corrected | US0364 in this same lane: the accept refusal now names the fail-closed fallback as its source, and reference-rfc.md documents the false-positive trade where the gate is described rather than only in a source docstring. |
| CR0363 | declined | Re-checked and no longer outstanding: `_selected_test_files` enumerates the selection, `_selection_warnings` reports the out-of-selection case, and both ride on the run record as `selected_tests` / `selection_warnings`. The residual was recorded against line numbers that have since moved; the behaviour it asked for shipped, so there is nothing to correct. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
