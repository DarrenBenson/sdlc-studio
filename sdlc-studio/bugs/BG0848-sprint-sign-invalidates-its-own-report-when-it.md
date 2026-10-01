# BG0848: sprint sign invalidates its own report when it moves an approved unit to Done

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py, changelog.d/BG0848.md
> **Depends on:** BG0859
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T08:37:31Z

## Summary

An approved story left at Review at close is moved to Done by `sprint sign` (as 6.0.0 intends: it awaits only the signature). The move gives that unit an elapsed time, and the report's `eu_minutes` row re-derives from it, so the report `sign` has just sealed no longer re-derives to its fingerprint: `sprint_report.py check` prints INVALIDATED straight after a clean seal. Found by a seal rehearsal on the sdlc-studio.com web run (RUN-01M3HRHY): four approved units at Review, `eu_minutes` signed 0.0 and now 2024.2 to 2107.6.

## Steps to Reproduce

Reproduced at HEAD 46cb9acf on 2026-09-30 in a throwaway tree built from the lean close fixture (`test_lean_close._fixture`), batch US0101 and BG0101, with the real seal (`_seal_units` not stubbed) and a token meter (`SDLC_STUDIO_TRANSCRIPTS` pointing at a transcript whose usage grows between steps):

1. `transition.py set` US0101 Ready -> In Progress, BG0101 Open -> In Progress, US0101 -> Review; this opens each unit's In Progress span in `unit_actuals`. The transcript then gains 5000 tokens.
2. `verify_ac.py run --id` each unit; `critic.py record` an APPROVE on each by a reviewer other than the author; commit.
3. `sprint.py close --retro RETRO0001` (chain steps stubbed green with `_green_steps`, as the close tests do); commit the paperwork. The transcript then gains 3000 tokens.
4. `sprint.py sign --report RPT0001 --principal Darren`: `sign: US0101 -> Done`, `sign: BG0101 -> Fixed`, `2 moved to their terminal status`.
5. `sprint_report.py check --report RPT0001` exits 1:

```text
INVALIDATED: RPT0001 records fingerprint a8085684510bd723; re-deriving it from the tree now yields b0064d27585e9747
  model_tokens[0]: signed 5000, now 8000
  tokens_total: signed 5000, now 8000
  est_actual[2]: signed 5000, now 8000
  eu_minutes[0]: signed 0.0, now 0.1
  eu_minutes[1]: signed 0.0, now 0.1
  eu_tokens[1]: signed 0, now 8000
```

One mechanism moves every row. The close derives each unit's actuals from a span still open (0.0 minutes, 0 tokens). The sign's terminal move closes the span through `run_state.record_unit_actual`, which also appends a meter stamp, so the unit rows AND the run's token total re-derive to new values. Positive control on the same fixture and meter: moving US0101 to Done and BG0101 to Fixed before the close gives `sign: 0 moved ... 2 already there` and `VALID: RPT0001 re-derives to the fingerprint it records`. The same fault struck RUN-01M3RPSK (`eu_minutes` and `eu_tokens` on every unit the sign moved) and RUN-01M3HRHY.

With no meter (the first grooming's fixture) only `eu_minutes` moves, so a criterion on that fixture passes a fix that freezes minutes alone.

## Proposed Fix

The close closes, at its own moment, the In Progress span of every unit it leaves for the sign to move, stamping the meter once, and derives the report from that reading. The sign's terminal move then finds no open span, so `record_unit_actual` records nothing and appends no stamp, and nothing the page digests moves. Dropping the figures from the digest, or leaving an open span at 0, makes `check` pass while the signed page under-reports the unit's time and spend; neither is the fix.

## Acceptance Criteria

The criteria are unit-level. Their tests drive `sprint.py close` with the close-chain steps stubbed green (`_green_steps`), as every close test does, so they do not prove the unstubbed close; the end-to-end unit filed beside this one runs the real chain.

- [ ] **AC1** Given a run whose batch holds an approved story at Review and an approved bug at In Progress, each with an In Progress span opened inside the run and its ACs verified, and a token meter whose usage grows between the close and the sign, when `sprint.py close`, a commit, `sprint.py sign` with the real seal and then `sprint_report.py check --report` run in turn, then the sign moves both units (Done and Fixed) and `check` prints VALID. Fails on: HEAD, which prints INVALIDATED on `eu_minutes`, `eu_tokens`, `tokens_total`, `model_tokens` and `est_actual`; on a fix that freezes `eu_minutes` only, which leaves `eu_tokens` and the run total moving (the RPT0012 shape); and on a fix that freezes only stories at Review, which leaves the bug's rows moving
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py::SealedReportStaysValidTests::test_a_unit_the_sign_moves_leaves_the_page_valid
  - **Verified:** yes (2026-10-01)
- [ ] **AC2** Given the same run, opened with a meter baseline so both spans start on a reading, with the unit clock advanced and the meter grown between the span's start and the close, when `sprint.py close` files the report, then each unit's `eu_minutes` is the span's elapsed minutes at the close (greater than 0) and its `eu_tokens` is the meter's growth between the span's start and the close (greater than 0), and the sealed page after `sprint.py sign` carries the same two values. Fails on: HEAD, which files 0.0 minutes and 0 tokens for an open span; and on a fix that drops `eu_minutes` and `eu_tokens` from the fingerprint, which passes AC1 while the page still reads 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py::SealedReportStaysValidTests::test_the_page_measures_an_open_span_to_the_close
  - **Verified:** yes (2026-10-01)

## Impact

Any run that relies on the sign to finish an approved unit ends with a signed report that fails its own check in every clone, which reads as tampering. Workaround: transition approved units to Done before `sprint close`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Groomed: premise re-run at HEAD in a throwaway fixture (INVALIDATED on `eu_minutes` for a story at Review and a bug at In Progress; VALID when both move before the close); two executable criteria (VALID after the real seal; minutes measured to the close, not 0.0); Affects gains lib/run_state.py, test_lean_sign.py and the changelog fragment, drops test_sprint.py and test_sprint_report.py; Points 3 kept. |
| 2026-09-30 | sprint planning | Regroomed after goal review round 1: premise re-run with a token meter - the sign also moves `eu_tokens` and the run's token total (`tokens_total`, `model_tokens`, `est_actual`) through the stamp `record_unit_actual` appends; AC1 now pins them and names the freeze-minutes-only fix; AC2 pins `eu_tokens` beside `eu_minutes`; criteria marked unit-level (chain stubbed), the unstubbed path left to the end-to-end unit; Depends on BG0859 (until it lands the close names the approved In Progress bug as undelivered: a STOP under --dry-run, a `[status]` line on the real close, which still exits 0); Points 3 kept, one mechanism. |
