# BG0452: _verifiers_all_green splits the artefact key on a hyphen, so it is blind to v3 ids and its forecast exclusions never fire in any new project

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** independent round-2 reviewer (isolated worktree); agent; v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`sprint._verifiers_all_green` identifies an artefact with `stem.split("-")[0]`, which yields the bare type prefix `US` for a v3 key such as `US-01KYPZ1G2AB4-a-v3-story`. Schema v3 is the seed for every `init` (`templates/config.yaml` sets `schema_version: 3`), so in every newly created project the BUILT-NOT-CLOSED exclusion, the retraction override and `exclusion_line` never fire at all. The legacy v2 shape returns correctly, which is why the shipped tests pass: they are written against the shape this repo carries rather than the shape it ships.

## Steps to Reproduce

Executed at d7a1ad8f, 2026-07-30, by an independent round-2 reviewer in an isolated worktree:

```text
key US-01KYPZ1G2AB4-a-v3-story  ->  uid US-01KYPZ1G2AB4
   `_verifiers_all_green` = False,  `_built_not_closed` = False
the equivalent v2 pair       ->  both True
```

This is the SAME defect class as the reopen-invalidation finding ruled CLOSED in this round (`_invalidate_verify_report` was repaired to match by `extract_record_id`), in a function the repairing story itself calls, left untouched. `readiness.py:953` and `handoff.py:711` carry the identical `split("-")[0]` pattern and are candidates for the same failure.

## Proposed Fix

Use `sdlc_md.extract_record_id`, which is what the repaired sibling now uses and what every other reader of an artefact key uses. This is the divergent-reader-of-a-shared-field class already named in CR0504 - a new reader hand-rolling an id parse instead of the one idiom - and the fix is to stop having two.

Sweep the other two call sites in the same slice rather than filing them separately, and pin all three with a v3-shaped fixture. The reason this survived is that every existing test uses a v2 key, so the tests agree with the code about a shape the product no longer ships by default. A test matrix covering both schema versions is the durable fix; repairing this one call site leaves the next reader free to make the same mistake.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `sprint._verifiers_all_green` identifies an artefact with `stem.split("-")[0]`, which yields the bare type prefix `US` for a v3 key such as...
- [ ] Following the recorded steps no longer reproduces the defect: Executed at d7a1ad8f, 2026-07-30, by an independent round-2 reviewer in an isolated worktree: This is the SAME defect class as the reopen-invalidation finding...
- [ ] The proposed fix lands, pinned by a test: Use `sdlc_md.extract_record_id`, which is what the repaired sibling now uses and what every other reader of an artefact key uses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | independent round-2 reviewer (isolated worktree) | Filed |
