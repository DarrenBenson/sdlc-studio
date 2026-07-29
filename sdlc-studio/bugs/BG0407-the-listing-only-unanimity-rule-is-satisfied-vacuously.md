# BG0407: The listing-only unanimity rule is satisfied vacuously by the 59 of 170 suite modules whose reads are not statically visible

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; each repair verified by applying its own mutant and watching it redden, bytecode purged, python3 -B)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Independent review of RUN-01KYNKDP: 59 of 170 suite modules measure an empty read set; a module asserting over file CONTENTS via a runtime-assembled path is silenced by a neighbour's declaration.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0398 made a directory listing-only only when every module that READS it declares it so. `readers` is built from `suite_read_map`, which by its own admission cannot see a path assembled at run time - 59 of 170 suite modules on this repo measure an empty read set. Such a module is not counted as a reader, so its CONTENT read is silenced by another module's declaration, and the rule that was presented as closing the hole closes only the visible half.

The contradiction is inside one file. `select_tests` reads an empty read map as 'an unanswered question, not an answer of it reaches nothing', and always includes the module. `listing_only_scopes` reads the identical silence as 'not a reader, so the declaration is unanimous'. Two opposite readings of the same evidence, and the unsafe one runs first: `is_test_relevant` gates whether `select_tests` is ever reached.

This is not a regression - the previous code applied a declaration globally regardless - but the claim that unanimity makes the narrowing safe is stronger than the mechanism.

## Steps to Reproduce

1. Module A declares `sdlc-studio` listing-only. Module B asserts over the contents of files under it via `Path(str(REPO) + '/sdlc-studio')`.
2. B's read map is empty, so `listing_only_scopes` reports the directory listing-only.
3. A content edit under it answers `test-relevant: no` while B's assertion would fail.

## Proposed Fix

Read the two silences the same way. A module whose read set could not be measured is an UNANSWERED question for unanimity exactly as it is for selection: it must count as a potential reader, so its silence withholds the narrowing rather than granting it. Say how many modules were unmeasurable when the narrowing is withheld, so the cost is attributable and someone can make those reads visible.

## Acceptance Criteria

- [ ] A module whose read set is unmeasurable counts as a potential reader, so its silence withholds the narrowing rather than granting it.
- [ ] The two readings of an empty read map agree: what `select_tests` treats as unanswered, `listing_only_scopes` treats as unanswered.
- [ ] When the narrowing is withheld for unmeasurable readers, the count is reported so the cost is attributable.

## Impact

A test-selection narrowing is only as trustworthy as the set of readers it can see. Granting unanimity on silence means the one module doing a dynamic content read is the one module the mechanism cannot protect - and the gate answers `no` for an edit it asserts over.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
