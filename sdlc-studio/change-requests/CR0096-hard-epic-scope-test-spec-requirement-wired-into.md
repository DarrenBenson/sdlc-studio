# CR-0096: hard epic-scope test-spec requirement wired into epic implement

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

**Estimate: 3 points.** The deferred half of CR0085: make the test-spec bridge a **hard
requirement at epic scope**. Today CR0085 ships the enforceable checks (`verify_ac ts-check`,
`lint`) and the documented discipline, but nothing *requires* a test-spec when implementing an
epic. Wire it into the conformance gate: an epic moving to Done (or its stories) must have a
test-spec whose AC Coverage Matrix passes `ts-check` - so the AC↔test bridge is mandatory, not
optional, for epic-scale work. Single-story work stays exempt.

## Acceptance Criteria

- [x] `conformance`/`epic implement` requires a test-spec at epic scope; an epic with no TS (or
      a TS failing `ts-check`) cannot reach Done (gated, with a clear message)
- [x] single-story implementation is exempt (a full TS is overkill there)
- [x] the requirement is configurable (a project can opt out via `.config.yaml`), default on for
      epic scope; reuses `ts-check` (CR0085), no new verification logic
- [x] unit tests: epic without a passing TS is blocked, with TS passes; CHANGELOG entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
