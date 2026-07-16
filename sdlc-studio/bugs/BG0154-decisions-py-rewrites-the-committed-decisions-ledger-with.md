# BG0154: decisions.py rewrites the committed decisions ledger with no allocation lock and no atomic write, violating both halves of the TRD's shared-file guarantee

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, sdlc-studio/trd.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

trd.md:241-244 guarantees shared-file writes go through `sdlc_md.atomic_write` and id allocation is serialised by `sdlc_md.allocation_lock` 'so a crash or a concurrent writer never corrupts a shared file'. decisions.py - which allocates D-ids by scanning table text (`_next_id)` and does full read-modify-write rewrites of the committed sdlc-studio/decisions.md spine - uses neither: all three write sites (lines 50, 121, 180) are plain `write_text`, and grep finds no lock/atomic anywhere in the file. Two concurrent `decisions add` calls mint the same D-id and one silently loses the other's row; a crash mid-write truncates the ledger. This ledger is load-bearing for the gate architecture: gate.py:551/564 and `engagement_floor.py` route waivers through `decisions.py waive`, so the audit trail the enforcement story rests on is the one shared file without the promised defences. BG0076 named decisions.py in its non-atomic inventory but its fix commit never touched it; CR0207's sweep also excluded it. decisions.py is also absent from rule 5's writer enumeration. Verified 3x by the refute panel.

## Steps to Reproduce

grep -n 'lock\|atomic' .claude/skills/sdlc-studio/scripts/decisions.py -> zero hits; inspect lines 50/121/180 - plain `p.write_text` after read-modify-write. Race two `decisions add` invocations - both scan the same table and mint the same D-id; the second write clobbers the first's row. Kill the process mid-write - decisions.md is truncated.

## Proposed Fix

Route all three writes through `sdlc_md.atomic_write`, take `sdlc_md.allocation_lock` around `_next_id` + insert (the same lock `run_state.py`:128-134 already takes), add decisions.py to trd.md rule 5's writer list, and add concurrency/crash regression tests.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
