# CR-0289: TRD lists critic among read-only helpers that 'never mutate the workspace'; critic record writes two committed verdict logs via a bare non-atomic append that silently drops torn rows

> **Status:** Proposed
> **Priority:** Medium
> **Type:** docs
> **Size:** S
> **Affects:** sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/critic.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

trd.md §5 rule 5 lists critic among read-only helpers and §3 puts it on the emit-JSON side, but `critic.py record` - the command `sdlc_md.py`:856's REMEDIATION text instructs agents to run - creates and appends to two committed workspace files (reviews/critic-verdicts.md, plan-review-verdicts.md) via a plain open('a') with no `atomic_write` or `allocation_lock.` The verdict log is written by concurrent seat subagents by design and feeds the conformance 'critiqued' Done-gate; `read_verdicts` accepts only 5/6-cell rows, so a torn row from a crash mid-write is silently dropped - erasing a recorded verdict. reference-scripts.md:156 already documents critic as a writer, confirming the TRD drifted. Panel notes the right remedy for the append is documenting an append-only exception (`atomic_write` whole-file replace would lose concurrent rows) plus torn-row surfacing. Verified 3x.

## Impact

trd.md §5 rule 5 lists critic among read-only helpers and §3 puts it on the emit-JSON side, but `critic.py record` - the command `sdlc_md.py`:856's REMEDIATION text instructs agents to run - creates and appends to two committed workspace files (reviews/critic-verdicts.md, plan-review-verdicts.md) via a plain open('a') with no `atomic_write` or `allocation_lock.`

## Acceptance Criteria

- [ ] trd.md §3/§5 move `critic record` to the writer list (append-only verdict logs), keeping critique/detect read-only
- [ ] Rule 5 documents the append-only exception to the atomic-write guarantee (or the append is hardened, e.g. single `O_APPEND` write per row)
- [ ] `read_verdicts` surfaces a malformed/torn row as a warning instead of silently dropping it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
