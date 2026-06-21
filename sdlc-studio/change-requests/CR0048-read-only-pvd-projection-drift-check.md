# CR-0048: read-only PVD projection + drift check (RFC0015 WS2)

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson (RFC decision session)
> **Date:** 2026-06-21
> **Affects:** scripts/pvd.py (new) or pvd workflow, reference-config.md
> **Depends on:** RFC0015, CR0047
> **GitHub Issue:** --

## Summary

Project the one writable master PVD into each project read-only (symlink in prod, synced copy in dev) and detect when a project's copy has drifted from / fallen behind the master (version + checksum).

## Proposed Changes

- `pvd sync` projects the master into a project's `sdlc-studio/` read-only.
- A version/checksum drift check flags a stale or locally-modified projection.

## Acceptance Criteria

- [x] `pvd sync` places a read-only master copy in a project; re-running is idempotent.
- [x] The drift check reports a project whose PVD copy differs from, or is older than, the master.
- [x] Unit-tested where code; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0048) | Complete - US0033: pvd.py sync+drift; critic REJECT->fixed |
| 2026-06-21 | Darren Benson | Raised - RFC decision session |
