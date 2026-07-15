# BG0148: The two creators disagree on a CR size: file_finding writes a T-shirt Size, artifact.py has no --size flag and writes Points

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

CR0269 made a CR carry a T-shirt Size (S/M/L/XL) not Points, and wired --size into `file_finding.py.` But artifact.py - which AGENTS.md documents as the CANONICAL creation path - has NO --size flag and still writes Points on a CR. So the two creators produce different shapes for the same type: the filer writes a T-shirt, the canonical creator writes points. That is LL0016 (two code paths building the same artefact must agree on what it MEANS), the same class as BG0136 where the filer could not record what the planner demanded. CR0269 deliberately left artifact.py legacy-tolerant to stay in lane and flagged this as the follow-up.

## Steps to Reproduce

1. `file_finding.py` file --type cr --size M ... writes > Size: M. 2. artifact.py new --type cr --size M -> error: unrecognized arguments: --size M. 3. artifact.py new --type cr writes Points, the legacy shape, never a T-shirt. The canonical creator cannot produce a correctly-sized CR.

## Proposed Fix

Add --size to artifact.py new/`new_batch` for the T-shirt types (cr, rfc, epic), writing Size through the ONE shared definition in `sdlc_md` (`SIZE_FIELD`/`check_size)` that `file_finding` already calls. Story/bug keep --points. Both creators call one type-aware definition of a sized artefact, so they cannot drift again - the BG0136/BG0132 shared-authority pattern applied to the size vocabulary.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
