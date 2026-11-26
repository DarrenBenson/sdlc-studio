# US1335: The close names a role whose cache-read share fell more than 10 points, and the retro must explain it

> **Status:** Ready
> **Depends on:** US1334, US1336, US1337, US1338
> **Risk-class:** high
> **Delivers:** CR0753
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/scripts/tests/test_cache_read_fall.py, changelog.d/US1335.md
> **Epic:** EP0381
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who answers for what each team's delivery costs (Abena)
**I want** the close to name any role whose cache-read share fell more than 10 points below its five-run mean, and the retro to explain it
**So that** a fall in cache reuse is explained in the run's own record before the run is signed, not found in a later bill

Beside its cost-per-point check, before its chain, the close reads the session's anatomy once, sets each role's cache-read share against US1334's mean, prints the comparison and records each role that fell more than 10 points as a `cache-read` known issue. The page's Cost by role table is stamped from that same reading. `retro validate` refuses a retro whose `## Cost` section names no fallen role, and a rolling boundary does not halt on a fall its retro names, as it does not halt on a named cost issue.

## Acceptance Criteria

### AC1: the close records the fall from one reading of the anatomy

- **Given** a fixture run whose session anatomy gives the builder a 40.0% cache-read share, and five earlier signed pages averaging 64.1% for the builder
- **When** `sprint.py close` runs for the first time
- **Then** it prints one line naming builder, 40.0%, the 64.1% mean, -24.1 points and the five pages, records a known issue with source `cache-read` naming the role, and reads the anatomy once: the Cost by role table the page states is the reading the check judged. Fails on: HEAD, whose close has no cache-read check and records no such issue
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cache_read_fall.py::CacheReadFallTests::test_the_close_records_a_fall_from_one_anatomy_read
- **Caller:** `sprint.py close` (`cmd_close`), whose cost step runs before its chain

### AC2: ten points or less, or no baseline, records nothing and says why

- **Given** five earlier pages at 60.0% for the builder, and runs whose builder share is 50.0% (a fall of exactly 10.0 points), 49.9% (10.1) and 75.0% (a rise of 15); and a reviewer row with no earlier figure
- **When** the close's cost check runs on each
- **Then** only 49.9% records a known issue, and the close line names the reviewer as not judged and why. Shares are compared at one decimal place, as the pages print them. Fails on: HEAD, which prints no cache-read line, so a role left unjudged is never named
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cache_read_fall.py::CacheReadFallTests::test_ten_points_or_less_or_no_baseline_records_nothing
- **Caller:** `sprint.py close` (`cmd_close`), whose cost step runs this check before its chain

### AC3: the retro must name each fallen role

- **Given** a run carrying a `cache-read` known issue for the builder, and a Keep/Stop/Try retro with no `## Cost` section, then one whose `## Cost` bullet names only repair, then one whose bullet names the builder
- **When** `retro.py validate --id <retro>` runs on each
- **Then** the first two fail naming the builder, its share and its mean; the third passes. Fails on: HEAD, which validates a retro with no `## Cost` section as ok over a run whose builder share fell 22.9 points below five signed pages
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cache_read_fall.py::CacheReadFallTests::test_retro_validate_demands_each_fallen_role_be_named
- **Caller:** `retro.py validate`, which `sprint close` runs first in its chain

### AC4: a named fall does not halt a rolling boundary

- **Given** a rolling cycle whose close recorded a `cache-read` known issue, once with the retro naming the role and once without
- **When** `sprint.py boundary` reaches its close-gate check
- **Then** the named one does not stop the boundary and the unnamed one stops it, naming the issue. Fails on: HEAD, which halts on every known issue except a cost issue whose cause is named and an unpriced unit, so a fall the retro explains would still halt it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cache_read_fall.py::CacheReadFallTests::test_a_named_fall_does_not_halt_a_rolling_boundary
- **Caller:** `sprint.py boundary` (`cmd_boundary`), the rolling run's close-gate check

## Notes

- Depends on US1334 for the baseline helper. It goes in the last wave because it shares `sprint.py` with US1333 and US1336, `lib/run_state.py` with US1332, US1333 and US1338, and `reference-sprint.md` with US1332 and US1337.
- The fall must be known before the close's retro-validate step, because the close then files the page and stamps the tree `sprint sign` refuses to see changed. The cost check already runs before the chain for that reason, while the spend by role is stamped later, inside `_file_the_report`. On this repository's live session (a 955 MB main transcript and 2.4 GB of subagent transcripts) `sprint cost --anatomy` did not finish in 110 seconds, so read the anatomy once, before the chain, and hand the same reading to `run_state.stamp_cost_roles` through a new optional parameter. The transcript does not grow while one `sprint close` runs.
- A re-close takes no new reading; judge from the cost roles the first close stamped.
- BG1764 is not a code dependency, but once it lands reviewers move out of `other`, where every signed page put them, so the first run after it can show `other` moving by more than 10 points through re-attribution alone; that run's retro names BG1764 as the cause.
- Mirror `close_cost_regression`, `retro.cost_cause_errors` and `_cost_cause_named`; one `## Cost` section serves both demands. Update `reference-sprint.md#cost-regression` and the cost item in `reference-retro.md`.
- Keep each test under 120 seconds: call the close's check function directly for AC2 and AC3, and run one CLI close for AC1.
- Grounded at HEAD db54c42bb on 2026-11-26:
  - AC1, AC2: `grep -c "cache-read\|cache_read_fall"` on `sprint.py` and `retro.py` printed 0 and 0, and `run_state.stamp_cost_roles` takes `(repo_root, transcripts_dir=None)` only. No full `sprint close` fixture was run for these two.
  - AC3: in a fixture with five signed pages at builder 62.9%, a run state whose report stamp carries builder `split.cache_read 0.40`, and a Keep/Stop/Try retro with no `## Cost` section, `retro.py --root <fx> validate --id RETRO0001` printed "retro RETRO0001: ok - 1 lesson(s), 0 finding(s) all dispositioned", exit 0.
  - AC4: read `cmd_boundary`'s close-gate check, which keeps every known issue as a halting gap unless its source is `unpriced` or it is a cost issue whose cause `_cost_cause_named` finds.
  - Timing: `time timeout 110 sprint.py cost --anatomy --format json` on the live session was killed at the timeout with no output.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Groomed for run twenty-eight from the D0635 breakdown |
