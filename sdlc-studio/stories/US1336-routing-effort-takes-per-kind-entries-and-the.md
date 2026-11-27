# US1336: routing.effort takes per-kind entries, and the plan and the lane brief carry each unit's resolved effort

> **Status:** Done
> **Depends on:** US1332, US1333
> **Risk-class:** high
> **Delivers:** CR0754
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_effort_by_kind.py, changelog.d/US1336.md
> **Epic:** EP0382
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who answers for what each team's delivery costs (Abena)
**I want** `routing.effort` to take an effort per kind of unit (docs, bug and code), with the plan and the lane brief carrying each unit's resolved effort
**So that** a team that has measured the difference can spend less effort on a docs change than on a code change, while a project that sets nothing sees no change

`routing.effort` accepts `docs`, `bug` and `code` entries beside `builder` and `reviewer`, each mapping a role to an effort; a role an entry leaves out takes the default. A unit's kind is route's existing classification: a bug by its id, else code when an Affects path ends in one of `route.CODE_EXTS`, else docs. `sprint plan` stamps each unit's resolved effort with its kind, refuses an unknown kind, role or value by name, and applies the reviewer-below-builder rule per kind; the lane brief names the unit's own effort. The kind entries ship empty, so every unit resolves to the role defaults, which ship as `inherit`.

## Acceptance Criteria

### AC1: each unit is stamped with its kind's effort

- **Given** a fixture with `routing.effort` set to builder medium, reviewer high, `docs: {builder: low}` and `bug: {builder: high}`, a Ready story whose Affects names only `.md` files, a Ready story naming a `.py` file, and an Open bug naming a `.py` file
- **When** `sprint.py plan --stories Ready --bugs Open --format json` runs, then again with the `docs` and `bug` entries removed
- **Then** the first plan stamps the docs story `{builder: low, reviewer: high, kind: docs}`, the code story `{builder: medium, reviewer: high, kind: code}` and the bug `{builder: high, reviewer: high, kind: bug}`; the second stamps builder medium and reviewer high on all three. Fails on: HEAD, which stamps builder medium and reviewer high on every unit whatever the kind entries say
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_by_kind.py::EffortByKindTests::test_each_unit_is_stamped_with_its_kinds_effort
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint plan --write`, whose stamp `lanes.stamped_effort` and the report's `_effort_counts` read

### AC2: an unknown kind, role or value is refused by name

- **Given** `routing.effort` holding `doc: {builder: low}`, then `docs: {author: low}`, then `docs: {builder: fast}`
- **When** `sprint.py plan --stories Ready` runs on each
- **Then** each exits 2 with nothing selected or written, naming `routing.effort.doc` and the kinds it takes, then `routing.effort.docs.author` and the roles, then `routing.effort.docs.builder` and the efforts. Fails on: HEAD, which plans with `doc:` present and exits 0, ignoring it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_by_kind.py::EffortByKindTests::test_an_unknown_kind_role_or_value_is_refused_by_name
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint.py plan` (`cmd_plan`), which resolves the effort before it selects or writes anything

### AC3: a reviewer below its builder within a kind needs a recorded decision

- **Given** `routing.effort.docs: {builder: high, reviewer: low}` with the role defaults `inherit`, once with no `reviewer_below_builder`, once naming D0001, which `decisions.md` records
- **When** `sprint.py plan --stories Ready` runs on each
- **Then** the first is refused naming the docs kind and both efforts; the second plans and prints the decision id. Fails on: HEAD, which accepts the pair and stamps inherit for both roles, since it never reads the kind entry
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_by_kind.py::EffortByKindTests::test_a_reviewer_below_its_builder_within_a_kind_needs_a_decision
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint.py plan` (`cmd_plan`), which resolves the effort before it selects or writes anything

### AC4: the lane brief names the unit's own effort

- **Given** the AC1 configuration and an open run
- **When** `sprint.py lane brief --units <docs story>` runs, and then for the code story
- **Then** the docs brief tells the orchestrator to spawn the builder at low effort and the reviewer at high, naming the docs kind; the code brief says medium and high. Fails on: HEAD, which reads `routing.effort` once per dispatch for every unit, and with only kind entries set prints "Effort: dispatch the builder and its reviewer at the session's own effort (routing.effort is not set)."
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_by_kind.py::EffortByKindTests::test_the_lane_brief_names_the_units_own_effort
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint.py lane brief` (`lane_brief_text`), which the orchestrator reads before it spawns a builder

## Notes

- Depends on US1332 (both edit `config-defaults.yaml` and `reference-config.md`) and US1333 (both edit `sprint.py`).
- Reuse route's classification, never a second one: `route._kind_of` (bug, cr or story by id prefix, which `routing.floor` uses) and `route._touches_code` (the critic's code test). Expose one public function in `route.py` composing them. The review tier classifies by difficulty band, not by kind, so it is not a source.
- Ship `docs: {}`, `bug: {}` and `code: {}` under `routing.effort` in `config-defaults.yaml` (D0637), documented in `reference-config.md#routing` with the classification rule and a sentence that values come from measuring the project's own work. `test_lean_config_keys_read.py` enforces both files.
- Keep the plan row's `effort` a mapping with `builder` and `reviewer`: `lanes.stamped_effort` reads `effort.builder` and the report's `_effort_counts` reads both, and the report already counts mixed efforts per unit, so it needs no change.
- Setting this repository's own values is a later decision on measured work; no criterion here sets one.
- One story at 5 rather than two at 3 and 2: both halves edit `sprint.py`, which US1333 and US1335 also edit, so a split adds a fourth serial `sprint.py` slot.
- Out of scope: `lanes.HEADLESS_EFFORT_FLAGS` is empty, so a headless lane carries no effort for any kind; unchanged here.
- Grounded at HEAD db54c42bb on 2026-11-26, in a throwaway fixture with a docs-only story (US0001), a story naming a `.py` file (US0002) and a bug naming a `.py` file (BG0001):
  - AC1: with builder medium, reviewer high, `docs: {builder: low}` and `bug: {builder: high}`, `sprint._stamp_effort` stamped builder medium and reviewer high on all three units.
  - AC2: with `docs: {builder: low}`, `code: {builder: high}` and `doc: {builder: low}`, `sprint.py plan --root <fx> --stories Ready --skip-personas --no-fetch --format json` exited 0 and stamped builder medium and reviewer high on US0001 and US0002.
  - AC3, AC4: with only `docs: {builder: high, reviewer: low}`, `sprint.effort_setting` returned inherit for both roles with no refusal, and `_effort_brief_line` printed the line AC4 quotes. `lane brief` itself was not run, since it writes run state.
  - Classification: `route._kind_of` and `route._touches_code` gave US0001 story and False, US0002 story and True, BG0001 bug and True; `route` has no public kind function.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Groomed for run twenty-eight from the D0635 breakdown |
