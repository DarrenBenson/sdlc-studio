# US1195: A refused landing or a REJECT yields a repair brief carrying the refusal and the findings verbatim

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0672
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py, changelog.d/US1195.md
> **Epic:** EP0326
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A refused landing or a REJECT yields a repair brief carrying the refusal and the findings verbatim
**So that** CR0672 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A refused landing's repair brief carries the refusal output verbatim

- **Given** a unit whose `sprint.py lane land` exited 1 because the commit hook refused, the hook's output kept in the landing's `commit.log`
- **When** the unit's repair-scope brief is asked of `sprint.py lane brief`
- **Then** the brief exits 0 and carries the hook's refusal output byte for byte under a heading naming it as the landing's refusal, beside the existing obligation that a repair carries only the blocking fix. Fails on: a repair brief that summarises or truncates the refusal, or carries none
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py::LaneBriefRepairScopeTests::test_a_refused_landing_yields_a_repair_brief_with_the_refusal_verbatim

### AC2: A REJECT's repair brief carries the reviewer's findings verbatim

- **Given** a unit whose verdict `sprint.py lane accept` recorded as a REJECT with two BLOCKING findings and one non-blocking issue
- **When** the unit's repair-scope brief is asked of `sprint.py lane brief`
- **Then** the brief carries the verdict's ISSUES and BLOCKING text byte for byte, each blocking finding marked as blocking, and names the verdict file it was read from. Fails on: a brief that paraphrases a finding, drops one of the two blocking findings, or presents the non-blocking issue as blocking
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py::LaneBriefRepairScopeTests::test_a_reject_yields_a_repair_brief_with_the_findings_verbatim

### AC3: A unit with no refusal and no REJECT gets no repair brief

- **Given** a unit with neither a refused landing nor a recorded REJECT, and a unit whose latest verdict is an APPROVE recorded after an earlier REJECT
- **When** the repair-scope brief is asked for each, and an ordinary `sprint.py lane brief` for the first
- **Then** each repair-scope request exits 2 saying there is nothing to repair and prints no brief, and the ordinary brief is the brief it was, with its five obligations. Fails on: an empty repair brief issued at exit 0, a brief quoting a REJECT a later APPROVE answered, or the ordinary brief changed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py::LaneBriefRepairScopeTests::test_a_unit_with_nothing_to_repair_is_refused_a_repair_brief

### AC4: The runbook routes every repair to a fresh agent holding the repair brief

- **Given** `reference-sprint-toolchain.md`
- **When** its row for a refused landing or a REJECT is read
- **Then** the row names the command that writes the repair-scope brief, and says the orchestrator hands it to a fresh repair agent and does not edit or run tests in its own context; the command it names is one `sprint.py lane --help` accepts. Fails on: a runbook that leaves the repair to the orchestrator, or names a command the parser refuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_brief_repair_scope.py::LaneBriefRepairScopeTests::test_the_runbook_routes_a_repair_to_a_fresh_agent

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
