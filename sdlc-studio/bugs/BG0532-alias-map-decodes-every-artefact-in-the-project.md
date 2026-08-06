# BG0532: alias_map decodes every artefact in the project with a bare read_text, so one unreadable file takes down any command that resolves an id

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** RUN-01KZBBZ0, 2026-08-06. Reproduced by the full suite and confirmed absent at c5c7bb07 in a detached worktree, so the trigger was new and the trap pre-existing. Chain: file_finding.py:1648 -> check_groomed -> grooming_gaps -> sprint.breakdown -> verify_ac.unit_unnameable_rows -> sdlc_md.find_by_id:2440 -> alias_map:2394.
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sdlc_md.alias_map` reads every artefact in the project with `p.read_text(encoding="utf-8")` and no error handling, and `find_by_id` calls it whenever a plain filename match misses. A single non-UTF-8 file anywhere in `sdlc-studio/` therefore raises `UnicodeDecodeError` out of any command that resolves an id - including commands with no interest in the corrupt file at all.

The module ships `read_text_safe` precisely for this, and uses it nearly everywhere else. This one path does not, so the fragility is latent rather than absent: it costs nothing until some caller adds a `find_by_id` on a hot path, and then it surfaces as a crash in an apparently unrelated command.

That is exactly how it was found. A grooming-census change on RUN-01KZBBZ0 called `find_by_id`, and `file_finding`'s own regression test - `test_file_finding_survives_a_non_utf8_sibling_and_leaves_no_drift`, which exists because this class has bitten before - went red. The census change was wrong for its own reasons and has been fixed, but the trap it stepped in is still armed for the next caller.

## Steps to Reproduce

1. Put a file containing invalid UTF-8 bytes in `sdlc-studio/bugs/`. 2. Call any code path that reaches `sdlc_md.find_by_id` for an id whose filename does not match directly. 3. `alias_map` raises `UnicodeDecodeError` at `sdlc_md.py`:2394, out of a call that was asking about a different artefact entirely.

## Proposed Fix

Use `read_text_safe` in `alias_map`, as the rest of the module does - an unreadable artefact contributes no aliases rather than aborting the lookup. A file nobody can decode should be reported by the guard whose job that is, not by whichever command happened to resolve an id first.

Pin it with a test that puts a non-UTF-8 file beside a real one and asserts `find_by_id` still resolves the real one, so the next caller to add a lookup does not rediscover this.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `sdlc_md.alias_map` reads every artefact in the project with `p.read_text(encoding="utf-8")` and no error handling, and `find_by_id` calls it whenever a plain...
- [ ] The proposed fix lands, pinned by a test: Use `read_text_safe` in `alias_map`, as the rest of the module does - an unreadable artefact contributes no aliases rather than aborting the lookup.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
