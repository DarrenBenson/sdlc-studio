# US0054: Gate wiring and docs: advisory mutation lane, discipline prose links to the executable gate

> **Status:** Done
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Epic:** EP0011
> **Persona:** Lena (Product amigo)
> **Story Points:** 2
> **Depends on:** US0052, US0053

## User Story

**As a** consuming project
**I want** the release gate to surface a stale-or-surviving mutation report as an advisory lane, and the assertion-integrity prose to point at the executable gate
**So that** the discipline is discoverable as enforcement, not prose that relies on the agent remembering

## Design

- **Gate lane (advisory in v1, per RFC-0022 D5):** when `sdlc-studio/.local/mutation-report.json`
  exists, `gate.py` reports survivors as an advisory `[warn]`; absent report = the lane states
  "not run" (advisory) rather than passing silently. Never blocking in v1.
- **Docs:** `reference-test-best-practices.md#mutation-check` links to the gate as its
  enforcement; `reference-verify.md` names the complement (verify_ac checks pass, mutation
  checks can-fail); a `help/` entry documents the CLI lanes.

## Acceptance Criteria

### AC1: the gate surfaces survivors as advisory

- **Given** a mutation-report with one survivor
- **When** gate runs
- **Then** the mutation lane warns naming the survivor count and the gate result is unchanged (advisory)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p 'test_gate.py' -k test_survivors_warn_advisory
- **Verified:** yes (2026-07-04)

### AC2: no report reads as not-run, not as pass

- **Given** no mutation-report on disk
- **When** gate runs
- **Then** the lane reports not-run (advisory), never PASS
- **Verified:** yes (2026-07-04)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p 'test_gate.py' -k test_absent_report_is_not_run

### AC3: the discipline prose links to the executable gate

- **Given** the assertion-integrity sections
- **When** read
- **Verified:** yes (2026-07-04)
- **Then** reference-test-best-practices.md#mutation-check and reference-verify.md name mutation.py as the enforcement, and a help file documents the lanes
- **Verify:** shell grep -q 'mutation.py' .claude/skills/sdlc-studio/reference-test-best-practices.md && grep -q 'mutation' .claude/skills/sdlc-studio/reference-verify.md && test -f .claude/skills/sdlc-studio/help/mutation.md

### AC4: a stale report never reads PASS

- **Given** a mutation-report recorded at another git rev
- **When** gate runs
- **Then** the lane reports STALE (advisory), never PASS for the current tree
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p 'test_gate.py' -k test_stale_report_never_reads_pass
- **Verified:** yes (2026-07-04)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | sdlc | Created via `new` (deterministic) |
| 2026-07-04 | claude | Authored at design: advisory-in-v1 gate lane per accepted RFC-0022; points + ACs + Verify lines |
| 2026-07-04 | claude | AC4 added from the critic's staleness finding: the report records git_rev and the lane compares it |
