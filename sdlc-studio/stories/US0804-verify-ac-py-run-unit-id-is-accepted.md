# US0804: `verify_ac.py run --unit <id>` is accepted as an alias for `--id`

> **Status:** Ready
> **Merged from:** US0806, US0807 (backlog sweep 2026-09-24, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Delivers:** CR0559
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_verify_run_unit_alias.py, changelog.d/US0804.md
> **Epic:** EP0244
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** `verify_ac.py run --unit US0001` to work the way `verify_ac.py revert-check --unit US0001` already does
**So that** the first guess at the flag is not a refusal I pay for and retry

## Summary

Reshaped by D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) to 1 point: one argparse alias on `run`'s existing `--id` (verify_ac.py:4322), the same pattern `--story, --file` already uses. The merged US0806 (deprecation notice) and US0807 (surface reference rows) are dropped: an alias needs neither, and the surface reference lists verbs, not flags. Other verbs are out of scope.

## Premise at HEAD

Executed at `85042135`:

```text
$ python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --unit US0804 --dry-run
verify_ac.py: error: unrecognized arguments: --unit US0804
exit=2
```

## Acceptance Criteria

- [ ] **AC1** Given a fixture story US0001 whose one Verify line passes, when `verify_ac.py run --unit US0001 --dry-run --root <fixture>` runs, then it exits 0 and prints the same `ac=1 pass=1` line that `--id US0001` prints. Fails on: HEAD exits 2 `unrecognized arguments: --unit`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verify_run_unit_alias.py::VerifyRunUnitAliasTests::test_unit_runs_the_same_story_as_id
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | sdlc-studio | Retitled: was 'Every verb identifying a unit accepts `--unit`, including `verify_ac run` where it is refused today' |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
