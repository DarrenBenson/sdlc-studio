# CR-0183: Passive concurrency safety: atomic index writes and an advisory allocation lock

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0015](../epics/EP0015-passive-concurrency-and-write-path-safety.md)
> **Priority:** Medium
> **Type:** Improvement
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

There is no file locking or atomic write anywhere: id allocation and index updates are
read-modify-write with a TOCTOU window, and every shared-file write is a non-atomic
truncate-and-write - under a documented parallel-agent execution model.

## Motivation

Parallel agents are a first-class feature (README: "waves of parallel implementation agents";
`reference-agentic-lessons.md:154`: "Two agents creating different new files in the same
directory is always safe"), and `status.py:44-72` ships an advisory acknowledging concurrent
sessions happen. Yet `artifact.py:268-285` computes the next number, checks `path.exists()`,
then writes - two concurrent `new` calls with different titles mint the same number - and a
crash mid-`write_text` can leave a truncated `_index.md`. This is the same coordination
problem the future distributed-identity work (RFC0024/CR0167) removes at the id layer; this CR
is the passive-safety floor for the current sequential scheme and for index writes, which
RFC0024 does not by itself cover. sdlc-studio is the ledger and must be passively safe under
concurrent writes when orchestration fails.

## Scope

**In scope**

- Advisory lock (single lockfile under `sdlc-studio/.local/`) around allocate+write in
  `artifact.py`/`file_finding.py` and around `_index.md` rewrites in `reconcile.apply_type`.
- Switch shared-file writes (`_index.md`, sync state, epic cascade) to
  write-temp-then-`os.replace` for atomicity.
- No behaviour change for the single-writer common case (lock is uncontended).

**Out of scope**

- Distributed identity (RFC0024/CR0167) - complementary, not a substitute; this CR is the
  floor even after ULIDs land, for index and cascade writes.
- Any scheduler/claiming behaviour (orchestrator territory).

## Acceptance Criteria

- [ ] Two concurrent `artifact.py new` calls (different titles) never mint the same id
      (stress test with the lock).
- [ ] A simulated crash mid-index-write leaves the previous `_index.md` intact (atomic
      replace), never a truncated file.
- [ ] Uncontended single-writer path shows no measurable regression.
- [ ] Lockfile is under `.local/` (gitignored) and self-heals from a stale lock.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| RFC0024 / CR0167 | Complementary: ULIDs remove the id-allocation race; this covers index/cascade writes and the pre-ULID scheme |
| BG0066 | Related create-path/index-write correctness |

## Risk

A poorly scoped lock could deadlock an agent wave or leave a stale lock blocking work.
Mitigate with a timeout + stale-lock reclaim and keeping the critical section minimal
(allocate+write only).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted from RV0006 architecture leg; positioned as complement to RFC0024 |
