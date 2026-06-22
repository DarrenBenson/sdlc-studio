# CR-0066: deploy contract and .config.yaml deploy schema (RFC0013 WS1)

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

RFC0013 WS1. Define the `deploy.*` contract in `.config.yaml` (orchestrate-only): the project supplies the runtime, the skill owns the gate + verification. All keys optional; secrets never read.

## Acceptance Criteria

- [x] `templates/config-defaults.yaml` gains a `deploy:` block (command, smoke, soak_minutes, rollback) with orchestrate-only comments
- [x] `reference-config.md#deploy` documents each key + the contract (smoke=rolled-out, soak=verified, rollback=surfaced procedure)
- [x] all keys optional - with none set, deploy is a pure gate+verify harness

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
