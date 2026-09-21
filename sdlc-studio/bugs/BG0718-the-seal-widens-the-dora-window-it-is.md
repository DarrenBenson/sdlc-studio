# BG0718: the seal widens the DORA window it is sealing, so a signed report reads INVALIDATED one second after the signature lands

> **Status:** Fixed
> **Verification depth:** functional (both criteria drive `build_report` over a REAL git repository built with `gitutil`, not a mkdtemp - the first fixture attempt used a bare temp directory, where `_git_commits` returns nothing, every DORA figure falls back to the static CI fixture and the window cannot be observed to move at all; both mutants applied against the current bytes, both KILLED, file restored byte-exactly)
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`build_report` bounds the DORA window with `end = _at(state.get('ended_at')) or _at(generated_at)`. `ended_at` is None until SEAL and is written BY the seal, so on re-derivation - where `as_of` carries the page's own generation time precisely so the same window is reproduced - the seal's freshly written `ended_at` wins instead, widens the window, and moves every figure derived from it. RUN-01M2SPNS signed RPT0002 with a lead time of 12h 29m and `check` re-derived 12h 57m one second later, so the page was INVALIDATED by the act of signing it. This is the failure `OUTSIDE_THE_DIGEST` (US0835 AC4) was built to stop, arriving through a DORA figure that set does not name: excluding the figures the seal WRITES is not the same as excluding the figures the seal MOVES. No existing fixture could see it because none writes `ended_at` into the run state after generating a page - the sealed fixtures set a signature block only.

## Steps to Reproduce

1. Open a run in a real git repository and work its batch to a state PREPARE accepts. 2. `sprint close --retro RETROxxxx --goal-verdict achieved` - the page is filed while the run is OPEN, so its window is bounded at the page's generation time. 3. Make any commit dated after the page but before the seal - on this project the close's own paperwork commit is one. 4. `sprint sign --report RPTxxxx --principal '<name>'` - the seal writes `ended_at`. 5. `sprint_report.py check --report RPTxxxx`: INVALIDATED, naming a DORA figure that moved. Observed on RUN-01M2SPNS at RPT0002.

## Proposed Fix

An explicit `as_of` is a RE-DERIVATION bound and must win outright: `end = _at(generated_at) if as_of else (_at(state.get('ended_at')) or _at(generated_at))`. A first derivation passes no `as_of`, so the open-run fallback that closes an otherwise unbounded window is unchanged. The discriminating fixture needs a REAL git repository, a commit dated after the page and before the `ended_at`, and `ended_at` written into the run state - without all three the window cannot be observed to move.

## Acceptance Criteria

### AC1: ending a run does not change what its own report re-derives to

- **Given** a REAL git repository whose run is made genuinely OPEN - `fixture_run` writes an `ended_at`, so it is cleared and the outcome set to `running` - its report filed and fingerprinted while the run is open, a commit dated after that page, and `ended_at` then written into the run state as the seal writes it
- **When** the report is revalidated, which re-derives it over the window the page itself records
- **Then** it re-derives to the fingerprint the signature holds, unchanged - the commit made after the page stays outside the window because the page replays the bound it was derived under rather than recomputing it from a run record the seal has since written to
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, change `build_report` to re-derive the window's end from the run record instead of replaying the one the page carries - the seal's `ended_at` then widens the window, every figure derived from it moves, and no run can hold a valid signature over its own report
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TheSealDoesNotMoveTheWindowTests::test_writing_ended_at_does_not_change_what_the_page_re_derives_to
- **Verified:** yes (2026-09-19)

### AC2: an open run's window is still closed at the page's generation time

- **Given** a REAL git repository whose run is made genuinely open, and a commit dated after the page is generated
- **When** the page is derived with no bound passed to it
- **Then** it records its own generation time as the window's end and re-derives to itself over that bound, so the commit made after it never enters its figures
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, replace the `_at(state.get("ended_at")) or _at(generated_at)` fallback in `build_report` with `None`, leaving an open run's window unbounded - every commit made after the page then enters its figures, and because this project ships the paperwork in the same commit as the code, committing the report invalidates the report
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TheSealDoesNotMoveTheWindowTests::test_an_open_run_is_still_bounded_at_its_generation_time
- **Verified:** yes (2026-09-19)

### AC3: a page built after the run ended also re-derives valid

- **Given** a REAL git repository whose run has ALREADY ended, and a commit dated after that `ended_at` but before the page is generated - so it belongs to neither the run nor the page
- **When** the page is derived and then revalidated
- **Then** it records the run's end as its window bound, not its own generation time, and re-derives valid with nothing touched
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, change `build_report` to bound every derivation at the generation time - replace the whole `end` expression with `_at(generated_at)` - the first derivation then excludes that commit and the re-derivation includes it, so a page nobody has touched reads INVALID. This is the repair that was FIRST made for AC1, and this criterion exists because an independent plan review demonstrated that it moved the defect onto the other case rather than removing it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TheSealDoesNotMoveTheWindowTests::test_a_page_built_after_the_run_ended_also_re_derives_valid
- **Verified:** yes (2026-09-19)

### AC4: a page recording no bound replays the one it was actually derived under

- **Given** two pages filed before the bound was carried, so neither records one: (i) derived AFTER its run ended, with a commit dated between the run's end and the page; (ii) derived while its run was OPEN and sealed afterwards, so the run now carries an `ended_at` LATER than the page - which is the shape every already-signed page is in
- **When** each is revalidated
- **Then** both re-derive valid: (i) is bounded at the run's end, which is where it was written, and (ii) at its own generation time, so the seal that came after it does not widen its window
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, change `_legacy_window_end` to return the generation time for both cases - (i) then re-derives over a wider window than it was written under, a commit between the run's end and the page enters only the re-derivation, and an untouched page reads INVALID. That is this bug's own defect surviving in exactly the pages the fallback exists to protect, and an independent plan review found it there after the first repair was accepted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TheSealDoesNotMoveTheWindowTests::test_a_page_recording_no_bound_replays_the_one_it_was_derived_under
- **Verified:** yes (2026-09-19)

### AC5: the bound is an envelope field and never a digest figure

- **Given** a page carrying a recorded `window_end`
- **When** its figure set is walked and its fingerprint taken
- **Then** `window_end` appears in no leaf figure, and changing its value leaves the fingerprint unchanged - the bound is recorded BESIDE the digest, never inside it
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, record it the way every other value on the page is recorded, as a `fig()` in a section. That passes all four of this bug's other criteria and all 208 tests in the module, while making every page filed before the bound shipped read INVALIDATED with `window_end` as the mover - this bug's own failure mode returning through its own repair. Required by the third plan review, which found the property stated only in a code comment
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TheSealDoesNotMoveTheWindowTests::test_the_bound_is_an_envelope_field_and_never_a_digest_figure
- **Verified:** yes (2026-09-21)

### AC6: the bound reaches the FILED page, not only the derived dict

- **Given** a report derived and then filed
- **When** the stored JSON is read back
- **Then** its `window_end` equals the one the derivation resolved, so a reader re-deriving the page REPLAYS the bound rather than inferring it
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, strip `window_end` in `file_report` before writing. AC1, AC2 and AC3 all stay green, because the legacy fallback happens to infer the same answer for their fixtures; across the whole module the only thing that notices is a `KeyError` in another test's fixture setup, which a defensive `.pop(..., None)` would erase entirely. The design's central claim would then be untested on the only artefact anybody reads
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TheSealDoesNotMoveTheWindowTests::test_the_bound_reaches_the_filed_page_not_only_the_derived_dict
- **Verified:** yes (2026-09-21)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, change `build_report` to re-derive the window end from the run record - replace the `_at(window_end) if window_end` branch with `_at(state.get("ended_at")) or _at(generated_at)` - so the seal's `ended_at` widens the window and invalidates the page it signs | ending a run does not change what its own report re-derives to |
| AC2 | in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, change `build_report` to drop the open-run fallback - replace `_at(state.get("ended_at")) or _at(generated_at)` with `None` - leaving an open run's window unbounded so every later commit enters its figures. This mutant reddens all four selectors; what makes AC2's row discriminating is its own `window_end == generated_at` assertion, which no other criterion makes | an open run's window is still closed at the page's generation time |
| AC3 | in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, change `build_report` to bound every derivation at the generation time - replace the whole expression with `_at(generated_at)` - so a page built on an already-ended run re-derives over a wider window than it was written under and reads INVALID untouched | a page built after the run ended also re-derives valid |
| AC4 | in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, change `_legacy_window_end` to return the stored generation time for both legacy cases - replace the `ended < g` branch with a bare `return gen` - so a page derived after its run ended re-derives over a wider window than it was written under | a page recording no bound replays the one it was actually derived under |
| AC5 | in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, record the bound as a section `fig()` instead of an envelope key, so it enters the digest it exists to protect | the bound is an envelope field and never a digest figure |
| AC6 | in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, strip `window_end` in `file_report` before writing, so the filed page carries no bound and a reader must infer the window | the bound reaches the FILED page, not only the derived dict |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-19 | sdlc-studio | Filed |
| 2026-09-19 | post-seal repair | Criteria authored and both mutants executed against the current bytes. AC2's mutant SURVIVED twice before its fixture could see it: first in a bare temp directory, where `_git_commits` returns nothing and an unbounded window admits nothing observable; then in a real git repository where the later commit was made AFTER the page was built, so neither window could admit it either. The fixture now makes the commit first and dates it beyond the page. A criterion whose fixture cannot reach the bound it is about measures nothing, which is exactly how the defect shipped. |
| 2026-09-19 | plan review r1 REJECT | Both blocking findings accepted. AC2's fixture was not an open run at all - `fixture_run` writes an `ended_at` - so the fallback it was about never executed and its mutant survived a THIRD time. And the repair itself relocated the defect: bounding re-derivations at the generation time left a page built on an already-ended run re-deriving over a wider window than it was written under. The design changed in response - the resolved bound is now recorded on the page and replayed, the treatment `generated_at` already gets - and AC3 was added for the case the review demonstrated. |
| 2026-09-19 | plan review r2 REJECT | Findings 1 and 2 ruled CLOSED. One new blocking finding: the legacy fallback for a page carrying no `window_end` returned the generation time for both cases, so a page derived AFTER its run ended still re-derived over a wider window - the same defect surviving in the pages the fallback exists to protect. The review's proposed remedy (prefer the run's `ended_at`) would have broken the opposite case and invalidated RPT0002's real signature; the two are distinguishable by which timestamp came first, and AC4 pins both directions with the signed shape as its positive control. |
| 2026-09-20 | operator ruling | ESCALATION ANSWERED: stays OPEN, and the next run closes it with a fresh plan review. The repair is committed and in force - four criteria, four mutants applied and killed against the final bytes, and the signed RPT0002 re-derives at its signed fingerprint - but two of this bug's three repairs were got wrong by their own author and caught by an independent seat, so the third is not closed on that author's say-so. Disclosed as an open High in the v5.1.0 notes meanwhile. |
| 2026-09-21 | plan review r3 REJECT | All four declared rows verified real, executed and uniquely discriminating. Rejected for what no row covered, and both findings are the same shape: the property the repair RESTS on was stated in a comment rather than pinned. Nothing asserted `window_end` stays outside the digest - recording it as a figure passes every one of the 208 tests in the module and invalidates every page ever filed. And nothing asserted the bound reaches the FILED page; stripping it in `file_report` was noticed only by a KeyError in another test's fixture setup. Repaired as AC5 and AC6, both mutants applied and killed. Third REJECT: the tooling escalated again. |
| 2026-09-21 | push boundary | `revert-check` reported this unit GREEN AFTER THE REVERT on all six criteria, which normally means a test that never reached its change. Investigated and it is NOT that: the production fix landed in commit 2bd54b9d during RUN-01M2SPNS, so this run's base ref already carries it - 9 `window_end` references at 2407e237, none at 0e22292e - and reverting to that base leaves the fix in place. This run added AC5 and AC6, which are pins rather than production code. It is the predicted consequence of D0226, adopting a unit whose code shipped before the run that accounts for it, and it is exactly the distortion D0226 recorded rather than hid. Verified by reverting the production file alone and re-running: 6 passed, file restored byte-exact. |
