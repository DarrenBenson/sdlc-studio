# US1332: `loop_guard` budget stops a run on spend as well as minutes and units, warning at 75 and 95 per cent

> **Status:** Ready
> **Risk-class:** elevated
> **Delivers:** CR0752
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/loop_guard.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_loop_guard_spend.py, changelog.d/US1332.md
> **Epic:** EP0380
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who holds each team's delivery to a budget (Abena)
**I want** `loop_guard budget` to stop a run on spend as well as minutes and units, warning at 75 and 95 per cent
**So that** a run cannot spend past the ceiling set for it without the breaker saying so, and the unit in flight still finishes cleanly

A spend appetite, counted in priced input-equivalent tokens, joins the minutes and units that `loop_guard budget` judges at each unit boundary. It resolves from `--appetite-spend`, then the run state's `appetite.spend`, then config `appetite.spend`, then `capacity.spend`, else 0, which means unbounded and is the shipped default of both keys. Spend is read as a first close reads it: a meter reading taken and held, never written, added to the run's stamps and totalled by `run_state.run_token_total`. The breaker warns at 75 and 95 per cent. At 100 the next unit does not start (exit 4), units already dispatched finish, and no unit's status moves. A meter that cannot read leaves the spend axis unjudged at that boundary and says why, while minutes and units still judge.

## Acceptance Criteria

### AC1: spend at the appetite stops the run and marks nothing

- **Given** a fixture run whose run state records an opening meter stamp and an appetite of `spend: N`, and a session transcript (reached through `SDLC_STUDIO_TRANSCRIPTS`) whose usage since that stamp prices at exactly N, then at N - 1
- **When** `loop_guard.py budget --root <fixture> --format json` runs on each, and once more in text form at N
- **Then** at N it exits 4 with `reason` naming `spend`, the verdict carries the spend read and the appetite, the text form says the units already dispatched finish and no further unit starts, and no unit's Status moves; at N - 1 it exits 0. Fails on: HEAD, which exits 0 with a verdict that has no spend field whatever the transcript priced
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_loop_guard_spend.py::LoopGuardSpendTests::test_spend_at_the_appetite_stops_the_run_and_marks_nothing
- **Caller:** `loop_guard.py budget --root .`, which the sprint loop runs between units (reference-sprint.md#appetite)

### AC2: the breaker warns at 75 and 95 per cent and keeps going

- **Given** the same run with spend at 74, 75, 94 and 95 per cent of the appetite
- **When** `loop_guard.py budget` runs at each, in JSON and in text
- **Then** each exits 0; `spend_warning` is null at 74, 75 at 75 and at 94, and 95 at 95; the text form prints one WARNING line naming the share, the spend and the appetite at 75 and above, and none below. Fails on: HEAD, which prints no spend warning at any share because it reads no spend
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_loop_guard_spend.py::LoopGuardSpendTests::test_spend_warns_at_75_and_95_per_cent
- **Caller:** `loop_guard.py budget --root .`, which the sprint loop runs between units (reference-sprint.md#appetite)

### AC3: a meter that cannot read is named, and the other axes still judge

- **Given** a run with a spend appetite and `SDLC_STUDIO_TRANSCRIPTS` pointing at an empty directory, once with its minutes appetite unspent and once with it spent
- **When** `loop_guard.py budget` runs on each
- **Then** the first exits 0 with `spend_unread` carrying the meter's own reason and a text line saying the spend axis was not judged at this boundary; the second exits 4 on `minutes` and carries the same spend note. Fails on: HEAD, which says nothing about spend whatever the meter does, so a declared spend ceiling judges nothing in silence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_loop_guard_spend.py::LoopGuardSpendTests::test_an_unreadable_meter_is_named_and_minutes_still_stop_the_run
- **Caller:** `loop_guard.py budget --root .`, which the sprint loop runs between units (reference-sprint.md#appetite)

### AC4: the spend appetite resolves flag, then run, then config, and ships unbounded

- **Given** a fixture with config `capacity.spend: 1000`, then also `appetite.spend: 500`, then a run state recording `appetite.spend: 300`, then `--appetite-spend 200` on the command line; and a fixture that sets no spend key anywhere
- **When** `loop_guard.py budget --format json` runs on each
- **Then** the appetite judged is 1000, then 500, then 300, then 200; with nothing set `appetite_spend` is 0 and no spend warning or stop can fire; `templates/config-defaults.yaml` ships both keys at 0, and `reference-config.md` documents both keys, the unit (priced input-equivalent tokens), the two warning bands, the unread behaviour, and that the reading is a lower bound, so the breaker can fire late but never early. Fails on: HEAD, which refuses `--appetite-spend` as an unrecognised argument (exit 2) and reads neither key
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_loop_guard_spend.py::LoopGuardSpendTests::test_the_spend_appetite_resolves_flag_then_run_then_config_and_ships_unbounded
- **Caller:** `loop_guard.py budget`, and `sprint plan`, which resolves the same keys once US1333 lands

## Notes

- Operator calls (D0637): spend is counted in priced input-equivalent tokens, not dollars; an unreadable meter leaves spend unjudged at that boundary and says why, while minutes and units still stop the run; both spend keys ship at 0.
- `capacity.tokens` is not reused: it is a forecast warning (500,000 shipped, 15,000,000 in this repository) while run twenty-six priced 146.4M, so gating on it would stop every run.
- `transition.py` calls `loop_guard.budget_verdict(minutes, units, elapsed, done)` positionally: keep those four working and add spend as keyword arguments.
- Read spend through one new `run_state` helper that does what `sprint._close_priced_total` does on a first close (`_stamp`, `_append_stamp`, `_rederivations`, `run_token_total`, nothing written) and returns `priced`, `includes_subagents` and the reason when there is none. `_stamp` returns None and drops the reason, so the helper takes it from `session_tokens`. One reading alone covers no delta, so a fixture needs the opening stamp `open_run` writes. A reading whose `includes_subagents` is false says so on the verdict.
- Rewrite the prose this makes false: the module docstring of `loop_guard.py` ("A token number is never a gate here"), the `capacity` and `appetite` comments in `config-defaults.yaml`, `reference-config.md#capacity` and `#appetite` ("never a gate"), and `reference-sprint.md#appetite` ("Tokens are a FORECAST, never a gate"). The plan's own capacity lines in `sprint.py` belong to US1333.
- Out of scope: `transition.py`'s boundary report and `handoff.py`'s appetite line stay on minutes and units; a meter read at every transition is a cost nobody asked for.
- Grounded at HEAD db54c42bb on 2026-11-26, in a throwaway fixture:
  - AC1 to AC3: with run-state appetite `{minutes: 0, units: 0, spend: 100}` and a two-record transcript, `SDLC_STUDIO_TRANSCRIPTS=<tx> loop_guard.py budget --root <fx> --format json` printed `{"exhausted": false, "reason": "", "elapsed_minutes": 10.02, "units_done": 0, "appetite_minutes": 0.0, "appetite_units": 0, "run_id": "RUN-TEST"}`, exit 0: no spend field, warning or unread note.
  - AC4: `loop_guard.py budget --root <fx> --appetite-spend 100 --format json` exited 2 with argparse's unrecognised-arguments error; a grep for `appetite.spend`, `capacity.spend` and `"spend"` over `loop_guard.py`, `sprint.py`, `lib/run_state.py`, `config-defaults.yaml` and `reference-config.md` printed nothing.
  - The helper: `run_state._stamp(<fx>, "open")` read tokens 10060 and priced 12920; appended alone, `run_token_total` gave priced None with the reason "1 session(s) carry no closing meter reading".
- Each Verify is one test in a new module; the neighbouring `test_loop_guard.py` runs 29 tests in 0.54 s.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Groomed for run twenty-eight from the D0635 breakdown |
