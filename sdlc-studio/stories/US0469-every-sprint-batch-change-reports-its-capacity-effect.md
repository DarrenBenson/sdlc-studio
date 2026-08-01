# US0469: Every sprint batch change reports its capacity effect through the plan-time renderer: points and token forecast against capacity.tokens, unit count against the appetite

> **Status:** Ready
> **Delivers:** CR0441
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py, changelog.d/US0469.md
> **Epic:** EP0171
> **Points:** 5

## User Story

**As a** operator mutating a running sprint's batch
**I want** every batch change to state the points it moved and to name each ceiling it is measured against separately
**So that** a mid-sprint change is never silent about what it did to the plan, and never invents a comparison the capacity model cannot make

## Acceptance Criteria

### AC1: AC1: an add names the points it moved, the unit count either side, and BOTH ceilings by their own axis

- **Given** an open run with a resolved appetite (units, minutes) and a configured capacity.tokens, holding a batch of priced units
- **When** `sprint.py batch add <id>` runs on a unit whose file declares Points
- **Then** the output names that unit's points; the batch UNIT COUNT before and after against appetite.units and appetite.minutes; and the batch's TOKEN FORECAST before and after against capacity.tokens - the two comparisons stated as two, because the appetite carries no points axis (resolve_appetite, sprint.py:501, returns minutes/units only; DEFAULT_CAPACITY, sprint.py:471). No line ever compares a points total to appetite.units
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::CapacityEffectTests::test_add_names_points_unit_count_against_appetite_and_tokens_against_capacity

### AC2: AC2: every batch action the parser exposes renders from capacity_report, and the sweep names them all

- **Given** a table in the test mapping each batch action to a valid invocation, asserted equal to the parser's batch `action` choices (the ID_VERBS pattern from test_cli_grammar)
- **When** each mapped action runs on an open run and its printed capacity line is compared with `capacity_report(root, batch, forecast, appetite)` computed independently on the same post-change state
- **Then** every action's line carries the same fields and the same numbers as capacity_report for that state, and an action present in the parser but absent from the table fails the sweep - so `swap` and `add-epic` cannot ship a second renderer that disagrees with the plan-time one, and the over-ceiling report of AC5 is inherited by every action rather than attached to `add` alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::CapacityRendererSweepTests::test_every_parser_batch_action_renders_from_capacity_report

### AC3: AC3: an unpriced unit is named, counted in the unit total, and left out of the token total

- **Given** a batch containing a unit whose file declares no Points
- **When** the capacity effect of any batch change is reported
- **Then** the unpriced unit is named in the output (the `unpriced` list `_token_forecast` already builds), the token forecast is stated as covering only the priced units rather than treating the absent value as 0, and the unit COUNT still includes it - unpriced is not unsized
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::CapacityEffectTests::test_an_unpriced_unit_is_named_counted_in_units_and_left_out_of_tokens

### AC4: AC4: the JSON report carries the same numbers the text line prints

- **Given** the same open run and the same batch change
- **When** the change is run once with `--format text` and once with `--format json`
- **Then** the points moved, the unit count before and after, the token forecast before and after, the appetite pair and capacity.tokens in the JSON all equal the values parsed out of the printed line
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::CapacityEffectTests::test_json_and_text_report_the_same_numbers

### AC5: AC5: a change past a ceiling names WHICH ceiling and is not refused

- **Given** an open run already at its appetite.units ceiling, and separately a run whose token forecast already exceeds capacity.tokens
- **When** a further unit is added to each
- **Then** both adds succeed with exit 0 and the unit is in the batch, and each output names the axis passed - 'unit count N against appetite.units M' or 'forecast T tokens against capacity.tokens C' - never a bare 'past the appetite' that does not say what was passed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::CapacityEffectTests::test_an_over_ceiling_change_names_the_axis_and_is_not_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
