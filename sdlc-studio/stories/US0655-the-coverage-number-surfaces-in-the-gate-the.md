# US0655: The coverage number surfaces in the gate, the lint aggregate and the close report

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, package.json, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/help/gate.md, tools/tests/test_check_spec_claims.py
> **Epic:** EP0211
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The coverage number surfaces in the gate, the lint aggregate and the close report
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the gate carries a non-blocking `doc-surface` lane

- **Given** `gate.py`, beside its existing `_disclosure` and `_doc_coverage` advisory lanes
- **When** the gate runs over a tree with undocumented verbs
- **Then** a `doc-surface` lane reports the count and the gate's exit code is unchanged - a tree
  that was green stays green. The lane sits with the other advisory ones because that is where a
  reader already looks for a number they are not being stopped by
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DocSurfaceLaneTests::test_the_lane_reports_and_does_not_change_the_exit_code

### AC2: `lint:disclosure` joins the aggregate, and the aggregate still passes

- **Given** `npm run lint`, which today runs every guard except `disclosure.py` - a checker with
  28 open advisory findings that nothing invokes
- **When** the aggregate runs
- **Then** `lint:disclosure` is among its lanes and the aggregate's exit code is unchanged. This
  is the cheapest real fix in the whole change: a checker nobody runs reports nothing, however
  good it is, and it has been sitting one line away from being read
- **Verify:** pytest tools/tests/test_check_spec_claims.py::LintAggregateTests::test_disclosure_is_in_the_lint_aggregate

### AC3: the close report carries one row, derived not typed

- **Given** a close
- **When** the report is composed
- **Then** it carries one row naming the documented and undocumented verb counts, derived by
  calling the coverage measurement rather than by reading a number somebody wrote down. A figure
  typed into a report is a figure that stops being true the day after
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::DocSurfaceRowTests::test_the_close_row_is_derived_from_the_measurement

### AC4: the three readers agree, because there is one measurement

- **Given** the gate lane, the lint lane and the close row over one tree
- **When** each reports
- **Then** all three quote the same number, because all three call the same function. Three
  readers of one fact that compute it three times are three chances to disagree, and this
  project has already paid for that shape more than once
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DocSurfaceLaneTests::test_the_three_readers_quote_one_measurement

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | make the `doc-surface` lane fail the gate when the count is non-zero | the gate carries a non-blocking lane |
| AC1 | drop the lane from the gate's advisory list entirely | the gate carries a non-blocking lane |
| AC2 | remove `lint:disclosure` from the aggregate again | `lint:disclosure` joins the aggregate |
| AC3 | render the close row from a constant rather than from the measurement | the close report carries one row |
| AC4 | give the gate lane its own re-derivation of the count | the three readers agree |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
