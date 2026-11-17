# CR-0717: Document the sequential id era's concurrency story in the TRD, since this repository is pinned to it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md §6 Two id eras (lines 408-430); §8 Scaling Strategy (lines 744-750); ADR-008 including Residual risk (lines 1024-1074)
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:25Z

## Summary

ADR-008 in `sdlc-studio/trd.md` (lines 1024 to 1074) is accepted on the grounds that sequential id allocation is not safe for several uncoordinated writers, and its residual-risk analysis and the Distribution scales too paragraph in section 8 (lines 744 to 750) are written entirely for short-ULID ids. This workspace is pinned to schema version 2 in `sdlc-studio/.config.yaml` and mints sequential ids while running parallel agent lanes, as does every consuming project that has not migrated. The defence that era relies on is absent from the TRD: the read of the remote main branch by `next_id.py` with `--remote`, its scan states, the warning that allocation fell back to local ids only, and the fetch-first step that `AGENTS.md` carries as prose. The TRD does not say which era this project is in or why it declined its own accepted decision. The phrase calling schema version 3 the default is also true only of the new-project seed in `templates/config.yaml`; an unstamped workspace resolves to 2 from `templates/config-defaults.yaml`.

## Impact

Maintainers and any team on the sequential schema read an architecture document that describes only the era they are not in. An agent or person rebuilding from the TRD learns nothing about the fetch-first precondition or the remote scan, so a stale clone mints an id the remote already holds and the collision is found only at push. Reviewers have no stated design to judge an id-allocation change against.

## Acceptance Criteria

- [ ] Section 6 or ADR-008 of the TRD states that this repository is pinned to schema version 2, with the reason, citing the pin in `sdlc-studio/.config.yaml`.
- [ ] The TRD describes the sequential era's concurrency defence: the remote scan by `next_id.py` with `--remote`, its scan states, the local-only fallback warning and the fetch-first precondition, each matching the script's behaviour.
- [ ] The TRD distinguishes the seeded schema version for a new project from the fallback an unstamped workspace resolves to, naming both template files.
- [ ] A test in `tools/tests/test_lean_trd_refresh.py` fails when the TRD omits the remote scan or states a pinned schema version different from the one in `sdlc-studio/.config.yaml`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
