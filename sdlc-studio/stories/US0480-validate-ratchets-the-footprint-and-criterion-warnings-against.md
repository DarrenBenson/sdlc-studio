# US0480: validate ratchets the footprint and criterion warnings against a recorded set of tolerated instances

> **Status:** Draft
> **Delivers:** CR0443
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, sdlc-studio/.validate-warning-baseline.json, .githooks/pre-commit, tools/tests/test_precommit_lane_order.py, tools/tests/test_precommit_warning_ratchet.py, CHANGELOG.md
> **Epic:** EP0173
> **Points:** 5

## User Story

**As a** maintainer who stopped reading validate's output
**I want** the standing warnings held at a recorded set so a new instance fails
**So that** a defect introduced today is visible, instead of being the 427th line of a report nobody reads

## Notes

This is the same ratchet concept as **US0461** (CR0433), which refuses an unbaselined
duplicate Verify selector. The two share one design, deliberately: a baseline that
records each tolerated **instance by identity, with a stated reason**, compared as a
SET. A count is not an option here - it cannot say which instance is new, cannot carry
a waiver, and a total recomputed from the corpus being judged always equals the actual,
so it can never refuse anything. The two stories keep separate baseline files because
the instances differ (`sdlc-studio/.validate-warning-baseline.json` here,
`sdlc-studio/.verify-lint-baseline.json` in US0461); the entry schema and the
untrustworthy-baseline states are the same.

The three warning kinds are `affects-undeclared`, `affects-unresolvable` and
`pseudo-verify`, all emitted by `validate.validate_file` at severity `warning`.

The ratchet is wired into a blocking lane, not left CLI-only. `gate.py._validate`
counts only `severity == "error"` and discards every warning, and the pre-commit hook
runs `gate.py` rather than `validate.py check`, so a ratchet that only changed
`validate.py`'s exit code would refuse nothing at commit time - which is precisely the
report nobody reads, one indirection further along.

## Acceptance Criteria

### AC1: an instance the baseline does not record refuses, and the recorded ones pass

- **Given** a workspace whose `sdlc-studio/.validate-warning-baseline.json` records each tolerated instance by identity - the artefact id, the rule, and the specific path or line the warning names - each entry carrying a stated reason
- **When** the ratchet runs and an artefact carries one `affects-undeclared` instance whose identity the baseline does not hold
- **Then** it exits non-zero naming that artefact, that rule and that instance, while every recorded instance passes unremarked, because the comparison is over the SET of instance identities and a count could not say which one is new
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::WarningRatchetTests::test_an_unrecorded_instance_refuses_while_the_recorded_ones_pass

### AC2: a swap that keeps the total flat is still refused, and a repaired entry is spent

- **Given** a change that repairs one recorded `affects-undeclared` instance and introduces a different one, so the total across the three kinds is unchanged
- **When** the ratchet runs
- **Then** the new instance is refused on its own identity, and the repaired entry is reported as stale and removable so the tolerated set only ever shrinks - a fixed instance cannot be spent again to admit a new one, and no recomputed total is consulted anywhere in the comparison
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::WarningRatchetTests::test_a_swap_that_keeps_the_total_flat_is_still_refused

### AC3: a kind paid down elsewhere cannot mask a regression in another

- **Given** a change that repairs two `pseudo-verify` instances and introduces one `affects-undeclared`
- **When** the ratchet runs
- **Then** it refuses, naming the `affects-undeclared` instance, because the rule is part of each entry's identity rather than a per-kind tally that a surplus in one kind could offset
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::WarningRatchetTests::test_a_kind_paid_down_elsewhere_cannot_mask_another

### AC4: a baseline it cannot trust never reports clean

- **Given** four workspaces: one with no baseline file, one whose baseline is unreadable, one recording an instance no artefact in the workspace still carries, and one whose entry has an empty reason
- **When** the ratchet runs over each
- **Then** each exits non-zero in a distinct not-baselined / corrupt / stale / reasonless state naming the offending entries and the command to restamp, never reporting clean on a reference state it could not establish
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::WarningRatchetTests::test_no_untrustworthy_baseline_reports_clean

### AC5: the verdict reaches a lane that refuses a real commit

- **Given** a temp clone with the shipped hooks enabled and a staged artefact carrying one unrecorded `affects-undeclared` instance
- **When** `git commit` is run for real
- **Then** the commit is refused by the named ratchet lane with the tree unchanged, so the verdict is not discarded by `gate.py._validate`'s `severity == "error"` filter, and `EXPECTED_LANES` in `tools/tests/test_precommit_lane_order.py` carries the new key so `test_no_lane_is_lost_in_the_reorder` stays green on the commit that lands this
- **Verify:** pytest tools/tests/test_precommit_warning_ratchet.py::WarningRatchetLaneTests::test_a_commit_carrying_an_unrecorded_instance_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
| 2026-07-28 | Claude Opus 5 (BG0345) | Regroomed: count baseline replaced by the set-with-reasons form shared with US0461, a reference-state file named, and the ratchet wired into a blocking lane |
