# US1333: sprint plan stamps the spend appetite on the run, and raising it mid-run names a recorded decision

> **Status:** Ready
> **Depends on:** US1332
> **Risk-class:** high
> **Delivers:** CR0752
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/arguments.md, .claude/skills/sdlc-studio/scripts/tests/test_appetite_spend_raise.py, changelog.d/US1333.md
> **Epic:** EP0380
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who holds each team's delivery to a budget (Abena)
**I want** `sprint plan` to stamp the spend appetite on the run, and raising it mid-run to name a recorded decision
**So that** the ceiling the breaker reads is the one the plan was sized against, and every raise is on the record with its values before and after

The plan resolves the spend appetite once with the other two axes (`--appetite-spend` on `sprint plan`, then `appetite.spend`, then `capacity.spend`), and `--write` stamps it on the run beside its standing value, so an edit to `.config.yaml` mid-run cannot move the ceiling the breaker reads. `sprint appetite resize --spend N` raises it only with `--decision <id>` naming a row `decisions.md` records, keeping the value before and after and the decision. A lowering needs only a reason, and a units or minutes resize keeps the recorded spend.

## Acceptance Criteria

### AC1: the plan stamps the spend appetite it resolved

- **Given** a fixture with config `capacity.spend: 1000` and two Ready stories
- **When** `sprint.py plan --stories Ready --write` runs, and on a fresh fixture with `--appetite-spend 400`
- **Then** the run state's appetite records `spend: 1000` and `standing_spend: 1000`, then `spend: 400`; the plan's capacity line names the spend appetite and its source beside minutes and units; after `.config.yaml` changes to `capacity.spend: 5`, `loop_guard budget` still judges the stamped value. Fails on: HEAD, which with `capacity.spend: 1000` set prints "the run BREAKER is wall-clock/unit-count" and names no spend, and refuses `--appetite-spend`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_appetite_spend_raise.py::AppetiteSpendTests::test_the_plan_stamps_the_spend_appetite_it_resolved
- **Caller:** `sprint plan --write`, which opens the run; `loop_guard.py budget` reads the stamp back between units

### AC2: a spend raise needs a decision decisions.md records

- **Given** an open run whose appetite records `spend: 1000`, and a `decisions.md` that records D0001 and not D0002
- **When** `sprint.py appetite resize --spend 1500 --reason r` runs, then with `--decision D0002`, then with `--decision D0001`, then `--spend 800 --reason r` with no decision
- **Then** the first two exit 2 naming the missing or unrecorded decision and leave the run state byte-identical; the third records `spend: 1500` and an `appetite_changes` entry whose `from` and `to` carry 1000 and 1500 and whose decision is D0001, and reports the run over its standing spend; the lowering is recorded on its reason alone. Fails on: HEAD, which refuses `--spend` and `--decision` as unrecognised arguments, so a spend raise cannot be recorded at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_appetite_spend_raise.py::AppetiteSpendTests::test_a_spend_raise_needs_a_recorded_decision
- **Caller:** `sprint.py appetite resize` (`cmd_appetite`), which the operator runs to move a ceiling mid-run

### AC3: a units or minutes resize keeps the spend appetite

- **Given** an open run whose appetite records `spend: 1000` and `standing_spend: 1000`
- **When** `sprint.py appetite resize --units 9 --reason r` runs
- **Then** the appetite still records both spend values, and the change entry's `from` and `to` carry them unchanged. Fails on: HEAD, which rebuilds the appetite from units and minutes alone, so the resize drops a recorded `spend`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_appetite_spend_raise.py::AppetiteSpendTests::test_a_units_resize_keeps_the_spend_appetite
- **Caller:** `sprint.py appetite resize` (`cmd_appetite`), which the operator runs to move a ceiling mid-run

## Notes

- Depends on US1332, which adds the keys and the breaker that reads `appetite.spend` from the run; both edit `lib/run_state.py` and `reference-config.md`.
- Only a spend raise needs a decision id. Minutes and units raises keep needing a reason alone, since extending the rule to them would change behaviour for every project.
- Look the decision up with `sprint._decision_recorded`, which `routing.effort.reviewer_below_builder` already uses; never a second reader of `decisions.md`.
- `run_state.appetite_record`, `resize_appetite`, `appetite_overage` and `sprint.appetite_overage_line` gain the spend axis; the rule that a recorded resize outranks a re-resolution covers spend too.
- `tests/test_help_structure.py` requires `help/sprint.md` to name every field `appetite_record` writes, so the two new fields go there; add `--appetite-spend` to `help/arguments.md` beside `--appetite-minutes`.
- Rewrite `capacity_report`'s basis text and the breaker line `sprint plan` prints.
- Grounded at HEAD db54c42bb on 2026-11-26, in a throwaway fixture:
  - AC1: with `capacity.spend: 1000` and `appetite.spend: 1000`, `sprint.py plan --root <fx> --stories Ready --skip-personas --no-fetch` printed "capacity: the run BREAKER is wall-clock/unit-count - appetite 240 min (config capacity.minutes) / 8 unit(s) (config capacity.units)"; `sprint.py plan --help` lists only `--appetite-minutes` and `--appetite-units`.
  - AC2: `sprint.py appetite resize --spend 200 --reason x` and `sprint.py appetite resize --units 9 --decision D0001 --reason x` each exited 2 with argparse's unrecognised-arguments error.
  - AC3: on a run state whose appetite held `spend: 100`, `sprint.py appetite resize --units 9 --reason x --format json` exited 0 and printed the appetite as `{"units": 9, "minutes": 0.0, "standing_units": 0, "standing_minutes": 0.0, "over_appetite": true}`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Groomed for run twenty-eight from the D0635 breakdown |
