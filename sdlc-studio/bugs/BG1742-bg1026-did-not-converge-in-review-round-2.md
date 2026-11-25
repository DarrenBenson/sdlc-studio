# BG1742: BG1026 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_ac_heading_with_suffix.py, changelog.d/BG1026.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T00:14:15Z

## Summary

BG1026 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the `[^)]` class that limits the tag to one parenthesis group (sdlc\_md.py:61, `AC_HEADING_RE`) is unpinned, though the repair's comment at sdlc\_md.py:58 says a tag has "nothing after it": replacing `[^)]*` with `.*` passes `test_ac_heading_with_suffix.py`, `test_sdlc_md.py`, `test_verify_ac.py`, `test_validate.py` and `test_conformance.py` (802 passed), yet the mutant reads `### AC5 (DEFERRED) - moved to US0123 (round two)` as AC5, a prose heading opening a phantom criterion as in round one\; a probe asserting None for that heading, which f61970331 returns, kills it; [pre-existing] a tag heading with a trailing space after `### AC3 (DEFERRED)` still opens no criterion, as at 74903e754 (`verify_ac.parse_story` lists only AC1 for that fixture at both refs), while the colon form tolerates the space\; this is BG1026's own symptom in a whitespace variant and no other open bug covers it; RULINGS: Round-one finding "the widened `AC_HEADING_RE` (sdlc\_md.py:58) reads the three" CLOSED: `validate.py --root . check` exits 0 with 0 errors at f61970331, and `verify_ac.parse_story` over all 4,707 markdown files under sdlc-studio/ reads identically with the base code and the repair code (only US0629 and BG0573 differ from the round-one code). Round-one finding "the prose heading `### AC5 and AC6 were WITHDRAWN, and this is why`" CLOSED: `verify_ac.py run --id BG0573 --dry-run` reports ac=5 unspecified=0, and `test_prose_headings_that_start_with_an_id_are_not_criteria` fails on the round-one code. Claim inventory: the new comment and the changelog are TRUE by execution (the changelog's "read the repository's own stories and bugs as they did before" by the corpus comparison above). AC1 and AC2 fail at base and pass at head\\\; verify\_ac dry run: ac=2 pass=2\\\; the seven touched test modules pass at head (934 passed). My other mutants: an empty tag refused, a colon needing a space, a trailing space after the tag allowed, a square-bracket tag and any heading level SURVIVE, none claimed by the criteria or the comment.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1026 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1026 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the `[^)]` class that limits the tag to one parenthesis group (sdlc\_md.py:61, `AC_HEADING_RE`) is unpinned, though the repair's comment at sdlc\_md.py:58 says a tag has "nothing after it": replacing `[^)]*` with `.*` passes `test_ac_heading_with_suffix.py`, `test_sdlc_md.py`, `test_verify_ac.py`, `test_validate.py` and `test_conformance.py` (802 passed), yet the mutant reads `### AC5 (DEFERRED) - moved to US0123 (round two)` as AC5, a prose heading opening a phantom criterion as in round one; a probe asserting None for that heading, which f61970331 returns, kills it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] a tag heading with a trailing space after `### AC3 (DEFERRED)` still opens no criterion, as at 74903e754 (`verify_ac.parse_story` lists only AC1 for that fixture at both refs), while the colon form tolerates the space; this is BG1026's own symptom in a whitespace variant and no other open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1026 AC1 still passes: Given a story whose third criterion heading is `### AC3 (DEFERRED)` with its own `Verify: manual` line, when `verify_ac` lists the story's criteria, then AC3 is listed with the manual Verify line and AC2 keeps only its own. Fails on: `AC_HEADING_RE` accepts only a colon and title after the id, so `### AC3 (DEFERRED)` opens no criterion and its Verify line folds into AC2.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ac_heading_with_suffix.py::AcHeadingWithSuffixTests::test_a_suffixed_heading_opens_its_own_criterion
  - **Verified:** yes (2026-11-25)
- [ ] **AC4** BG1026 AC2 still passes: Given a heading `### AC10: title`, when the criteria are parsed, then it opens AC10, never AC1 with a suffix. Fails on: a loosened heading pattern that matches the id prefix would read `AC10` as AC1 with a suffix; today nothing tests it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ac_heading_with_suffix.py::AcHeadingWithSuffixTests::test_ac10_is_not_ac1_with_a_suffix
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
