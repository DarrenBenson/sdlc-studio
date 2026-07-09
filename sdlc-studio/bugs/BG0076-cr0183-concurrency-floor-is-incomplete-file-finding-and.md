# BG0076: CR0183 concurrency floor is incomplete: file_finding and new_batch allocate unlocked and truth-file stamps are non-atomic (4-way id collision reproduced)

> **Status:** Open
> **Severity:** High
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4 (single-writer operation is today's norm; multi-agent waves are the exposure). CR0183 (Complete) scoped 'atomic writes + advisory lock around allocate+write in artifact.py/file_finding.py' - only artifact.py new (artifact.py:318) takes sdlc_md.allocation_lock. file_finding.py:153-209 allocates and writes with no lock; new_batch allocates n0 unlocked (artifact.py:389) and writes files with plain write_text (:429); meta_new likewise (:276,293). Reproduced (RV0007): 4 concurrent file_finding calls all filed BG0003 (four files, one id; next_id collisions exits 1) and the index kept 1 of 4 rows. Non-atomic truncate-and-write also survives on truth files and shared state: transition.py:340 (the artefact Status stamp - a crash mid-write truncates the artefact, which reconcile then reads as 'Unknown asserts nothing', not even drift) and :251, artifact.py:222/610, github_sync.py:290/328, verify_ac.py:589/646, archive.py:81-102, reconcile.py:1108/1303-1304, lessons.py:205, decisions.py:108/139, triage_noise.py:104/162/202, resume.py:74, loop_guard.py:77, project_upgrade.py:310-337/534. trd.md:209-212 states the guarantee as universal - an overclaim.

## Steps to Reproduce

Fixture workspace; launch 4 parallel 'file_finding.py file --type bug ...' -> all four mint the same id; next_id.py collisions -> exit 1; index shows one row.

## Proposed Fix

Take allocation_lock in file_finding.file, new_batch and meta_new; sweep the writer inventory through sdlc_md.atomic_write (truth-file stamps, epic cascade, sync state first); correct trd.md:209-212 until done.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
