# BG0383: One whole-tree reader collapses the test-relevance set to `sdlc-studio`, so every artefact commit pays the full suites

> **Status:** Fixed
> **Verification depth:** functional (tests red-first, four load-bearing predicates mutation-killed)
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5; human; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py
> **Severity:** High
> **Points:** 5

## Summary

`gate.test_relevant_paths` measures what the suites actually read, which is the right design. But `test_root_census.py` takes a census of the whole workspace, so it records the bare entry `sdlc-studio`. `_minimal()` then removes every entry that one covers, and the four genuinely narrow reads - `sdlc-studio/retros`, `sdlc-studio/trd.md`, `sdlc-studio/personas.md`, `sdlc-studio/prd.md` - are absorbed into it.

The result is that `is_test_relevant` answers yes for every path under `sdlc-studio/`. Filing a change request, editing a retro's prose, correcting an index row: each selects both suites.

The reuse path is NOT the same defect, and this bug claimed it was. `surface_files` deliberately hashes every TRACKED file rather than the measured set, and its docstring records why: measured on this repo the set omitted 233 tracked files, so an edit to SKILL.md left the digest byte-identical while three tests went red. Reuse exists for an unchanged tree, so a new artefact correctly invalidates it. Only the relevance fast path is broken.

## Steps to Reproduce

1. `python3 gate.py --test-relevant sdlc-studio/change-requests/CR0497-x.md` -> `test-relevant: yes`.
2. `gate.test_relevant_paths('.')` contains the bare entry `sdlc-studio`; no narrower `sdlc-studio/*` entry survives `_minimal()`.
3. `gate.suite_read_map('.')` shows `test_root_census.py` is the only module that records the bare directory; the other four workspace readers name specific files or one subdirectory.

## Proposed Fix

The census reads the tree's SHAPE, not the artefact bodies. Adding, removing or renaming a file under `sdlc-studio/` can change its outcome; editing the prose inside one cannot. So the relevance entry for a whole-tree reader should be structural, and a module needs a way to declare that its read is of the listing rather than of the contents. Do NOT exempt the census test - that would be a false skip, and a guard that cannot fail is not evidence (L-0250).

## Acceptance Criteria

- [ ] A commit that only edits artefact BODIES under `sdlc-studio/` does not select the unit suites.
- [ ] A commit that adds, deletes or renames a file under `sdlc-studio/` still selects them, pinned by a test asserting both halves against one fixture - so the carve-out cannot widen into a blanket exemption of the workspace.
- [ ] The reuse path is left alone: hashing every tracked file is the deliberate design recorded in `surface_files`, and narrowing it to the measured set is the false-green that docstring exists to refuse.
- [ ] `gate.py --test-relevant --format json` reports WHICH entry matched a path, so the next time one reader collapses the set it is visible from the tool rather than by reading the read map by hand.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Acceptance criteria back-filled. They were supplied at filing and neither creation path wrote them: `artifact.py` has no Acceptance Criteria section for a bug, and `file_finding.py` rendered the STATED ABSENCE over them. Both are repaired under BG0384; these four documents are the evidence of the defect and are restored from the fields files they were filed from, not re-invented. |
| 2026-07-28 | Claude Opus 5 | Corrected BEFORE implementation. The summary, the title and one criterion claimed the verdict-reuse path was defeated by the same entry. It is not: `surface_files` hashes every tracked file on purpose and its docstring gives the measurement that forced the choice. The claim was written from the shape of the code rather than from reading it - L-0253 exactly. The relevance defect stands unchanged. |
