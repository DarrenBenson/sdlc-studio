# US1001: The lane-yield appendix is read from the committed run record, as the close froze it

> **Status:** Ready
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_yield_frozen.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py, changelog.d/US1001.md
> **Epic:** EP0276
> **Points:** 3
> **Depends on:** US0997, BG1010
> **Persona:** Graham Doyle

## User Story

**As** the operator deciding which commit gates have earned their place
**I want** the lane-yield tally the close read from this clone's refusal log frozen onto the run record
**So that** a signed page's delete-candidate verdicts can be re-read on any machine, not only the one whose hooks wrote the log

## Acceptance Criteria

- **AC1:** Given a clone whose refusal log holds a refusal inside the run and whose run archive holds an earlier run, when `sprint close` files the report, then the lane-yield rows are recorded on the run record, every lane-yield figure cites the tracked run record ahead of `git log`, and no figure anywhere on the page names a path under `.local/`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_yield_frozen.py::FrozenLaneYieldTests::test_close_freezes_the_tally_on_the_run_record
- **AC2:** Given that run signed and committed, when `sprint_report.py build --run <RUN-ID> --id <RETRO> --format json` runs in a fresh clone holding no refusal log and no run archive, then the lane-yield section is present with the rows the filed page carries.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_yield_frozen.py::FrozenLaneYieldTests::test_a_fresh_clone_reads_the_frozen_tally

## Notes

- Release: 6.4, run ten (D0461, which takes EP0276 whole); was 'later' (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: `_lane_yield_section` (sprint_report.py:5042) re-reading sdlc-studio/.local/refusals.jsonl at every derivation and citing REFUSALS_REL (defined at :4955; cited at :5053 and :5057)
- AC2 must fail on: returning None when the clone holds no log, as `_lane_yield_section` does today (:5050-5052), so the section vanishes everywhere but the closing machine
- Checked at HEAD 508e2408 (2026-11-12): neither criterion is met. RPT0028.json cites `sdlc-studio/.local/refusals.jsonl, git log` on 11 lane-yield figures, and no run record carries a lane-yield key.
- Marked later: the panel recommends cutting it and amending CR0610's first criterion to exclude the appendix. The section is per clone by design and outside the digest; only this repository's hooks write the log; a run's refusals land on whichever machines committed to it, so a tally frozen from the closer's log is still partial; and it is machinery measuring machinery (LL0056). If kept, the page must say the tally is this clone's log as the close read it.
- The second criterion needs BG1010: `cmd_build` resolves --run but builds the default run (sprint_report.py:6075), so at HEAD the selector fails for that reason, not this story's. The first needs US0997, which makes the rest of the page cite the tracked record.
- Two .local reads feed the section today: the refusal log (sprint_report.py:5050-5060) and the run archive that bounds the last three runs (`_yield_windows`, :5027, reading `run_state.archived`, lib/run_state.py:507, the .local archive). Freeze both beside freeze_ci_runs in `_file_the_report` (sprint.py:10022-10024, where `freeze_review_rows` also runs), with the freezer in sprint_report.py beside `freeze_ci_runs` (:3019).
- An unfrozen preview of an open run keeps reading the log, as `_ci_runs` does for an unfrozen open run (:3044); test_lean_lane_yield.py::LaneYieldTests::test_the_appendix_shows_lane_yield (:224) builds such a preview.
- test_lean_lane_yield.py::LaneYieldTests::test_a_lane_that_caught_nothing_in_three_runs_is_listed_not_enforced (:245) closes the same run with and without the log and requires the same exit, new files, known issues, fingerprint and output: the freeze must add no file and print nothing, and a close with no log must still show no section.
- Say on the page that the tally is this clone's log as the close read it in `lane_yield_note` (:5100-5106), a figure, so neither template changes. reference-scripts.md:282 is the one page that describes the appendix's provenance; it gains that sentence.
- Refreshed on every prepare, as CI runs are; the section stays outside the digest (SECTIONS_OUTSIDE_THE_DIGEST, :2807), so no rule mark is needed.
- help/sprint.md was in Affects but says nothing of lane yield; dropped 2026-11-12.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Marked 'Release: later'; D0356 holds the later stories for 6.3.
- CR0610's lane-yield question is unruled: the refine panel recommended cutting this story and amending CR0610's first criterion, because a tally frozen from the closer's clone is still partial and only this repository writes the log (LL0056).
- Persona: consuming projects never hold the refusal log, so Maya Okafor gains nothing; the beneficiary is the repository maintainer (Rowan Achterberg).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: line references corrected (sprint_report.py moved by about 450 lines, sprint.py by about 560); Affects gains test_lean_lane_yield.py, which closes with and without the log, and reference-scripts.md, and drops help/sprint.md, which never mentions lane yield; release set to 6.4 (D0461); criteria unchanged |
