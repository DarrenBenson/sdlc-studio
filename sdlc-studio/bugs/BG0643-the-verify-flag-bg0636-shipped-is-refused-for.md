# BG0643: the --verify flag BG0636 shipped is refused for the one case it exists for: a criterion whose test is not written yet

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-09-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0636 added `--verify` so a finding can be filed with an executable criterion. The write guard then refuses any selector naming a test that does not exist. For a bug filed BEFORE its fix - which is every bug - the test never exists yet, so the flag is refused in the ordinary case and accepted only when the work is already done. Found by using it three times in the run that shipped it: BG0640, BG0641 and this artefact all had to be filed WITHOUT the flag and then hand-edited to add the Verify lines, which is precisely the hand-rolling the flag was added to end.

## Steps to Reproduce

1. `file_finding.py file --type bug --ac '<criterion>' --verify 'pytest tests/test_x.py::NewTests::test_new'` where the file exists and the class does not.
2. Refused: `a Verify: selector names no test that exists`.
3. The same criterion, hand-written into the artefact afterwards, is accepted by `verify_ac run`, which reports it RED - the correct state for a criterion whose fix is not built.

## Proposed Fix

Separate a MISTYPED selector from a NOT-YET-WRITTEN one at the filing boundary, the way `selector_resolves` already separates a missing tree from a broken file. A selector whose test FILE resolves and whose node does not is not obviously a typo when the artefact is a bug in Open status: the node is what the fix will add. The guard's own suggestion mechanism proves the distinction is available - it offers `did you mean` from the file's real nodes - so a near-miss can be refused while a genuinely new node name is accepted and reported RED. What must not happen is the flag being usable only after the work it is meant to precede.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0636 added `--verify` so a finding can be filed with an executable criterion.
- [ ] **AC2** The proposed fix lands, pinned by a test: Separate a MISTYPED selector from a NOT-YET-WRITTEN one at the filing boundary, the way `selector_resolves` already separates a missing tree from a broken file.

## Impact

The flag is the whole of BG0636's authoring half, and the grooming gate BG0636 also shipped now REFUSES a batch holding a unit whose criteria carry no verifier. So a filer hits a refusal at filing, hand-edits the artefact to get past it, and the doctrine's no-hand-rolling rule is broken by the tool that exists to uphold it. Three of the four findings filed after BG0636 landed took exactly that route.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-03 | sdlc-studio | Filed |
