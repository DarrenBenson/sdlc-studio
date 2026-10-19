# BG1070: conformance reads US0357 and US0358 as missing their verified stage in a fresh checkout, though both carry Verified stamps, so the lane's verdict depends on the clone's .local state

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, tools/tests/test_conformance_fresh_checkout.py, changelog.d/BG1070.md, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Evidence:** 2026-10-19: fresh worktree at c704e6c7 -> 'US0357 (Done): missing verified', 'US0358 (Done): missing verified', rc=1; main clone -> rc=0. US1079 round-1 QA verdict, [pre-existing] finding (sdlc-studio/reviews/critic-verdicts.md).
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T11:19:03Z

## Summary

`conformance.py check` over the whole workspace passes in this clone, and fails in a fresh `git worktree` of the same commit: `conformance: 1002/1086 conformant, 2 not ... US0357 (Done): missing verified; US0358 (Done): missing verified`. Every criterion on both stories is stamped `Verified: yes (2026-07-24)`, and their selectors are in tools/tests/`test_lint_corpus.py` and `test_lint_corpus_attribution.py.` So the verified stage for these two is read from something only this clone's gitignored `.local` holds, and a checkout without it (a reviewer's worktree, a second machine, CI's whole-workspace runs) reaches a different verdict on the same commit. Found by US1079's round-1 QA reviewer as a pre-existing finding.

## Steps to Reproduce

1. `git worktree add --detach <tmp> HEAD` on main (c704e6c7). 2. In it, `python3 .claude/skills/sdlc-studio/scripts/conformance.py check` -> exit 1, US0357 and US0358 'missing verified'. 3. The same command in the main clone -> exit 0.

## Proposed Fix

Find what the verified stage reads for these two that the committed tree does not carry (their stamps are present), and make it read committed evidence; or record why these two need a reading the others do not.

## Acceptance Criteria

- [ ] **AC1** The whole-workspace conformance check reaches the same verdict on US0357 and US0358 in a fresh checkout as in a clone that holds .local state
  - **Verify:** pytest tools/tests/test_conformance_fresh_checkout.py -k fresh_checkout_reads_the_same_verdict

## Impact

A whole-workspace conformance verdict is not a function of the commit, so a review or a second machine can see a failure the author's clone cannot reproduce (LL0029).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
