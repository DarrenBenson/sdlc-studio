# BG1643: The TRD checks left by run nineteen's TRD repairs accept rewordings and leave three claims unpinned

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, tools/tests/test_trd_coverage_soft_dependency.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T00:41:24Z

## Summary

The builder of the BG1516, BG1517 and BG1531 repairs (RUN-01M7TTK3) left these non-blocking gaps. BG1516: AC1's 'which worktree' is pinned by no test, an AC3 mutant that changes only words survives, and the TRD does not name Codex's --skip-git-repo-check among the flags the lane runner passes. BG1517: the exfiltration row's opening clause in sdlc-studio/trd.md reads as if Verify-line commands cannot reach the network, which its later clauses contradict, and `verify_ac`'s `shell_allowed_for` with `allow_external` is pinned by no test. BG1531: other phrasings of the read-only helper list escape the check.

Wave two's qa reviews (RUN-01M7TTK3, verdicts d04bae0479db-a7f80fa9, 86c7cf341406-10fe25a0, 318f0c89748e-5993d0c9, all APPROVE) add: BG1096's run-clause regex allows anything but a semicolon between its anchors, so a self-contradicting clause at trd.md:242 passes tools/tests/test_trd_coverage_soft_dependency.py:102-103; BG1556's Decision log row (trd.md:574) calls the log append-only although `decisions.py add --supersedes` rewrites an earlier row's Status in place (decisions.py:112-127), the same word the shipped templates/decisions.md header uses; BG1557's AC2 test skips every column headed global and never requires a local one, so relabelling trd.md:748's column passes with half the row subtests gone, and its AC1 test checks section 2 only for the literal word read-only.

Further wave-two qa findings (verdicts a5a25da4fc19-867be567 for BG1565, f4709601651b-cd31e586 for BG1621, 49e7fb86b77d-8d7917eb for US1299): BG1565's AC1 test pins each step of the persona-learning loop by its verb, not its actor (test_lean_trd_refresh.py:1792), and its AC2 check reads only the words open, not yet built and unbuilt (`_UNBUILT_CLAIM`, :1760), so 'is not built' and 'still to come' beside a Done story pass; BG1621's storage-row test reads the Writer and Purpose cells by containment (:656-659), so a row denying the replay or crediting a second writer passes; US1299's AC2 assertions read leading words (:1875, :1883), so 'refuse nothing' and 'never refused' pass.

US1299's round-two review (verdict 49fb4419390d-99600593) adds: TrdRequiredPyYamlTests still passes four rephrasings that make PyYAML optional (a pronoun after a semicolon or in the next sentence, 'If PyYAML is not installed, ... fall back', 'no config, just the defaults').

BG1531's round-two review (verdict b94816e1cd21-612bc20b) adds: Rule 5's claim that review_prep.py close backfills all four meta indexes (trd.md:296-301) is true by execution but pinned only to sdlc_md.META_TYPES; a mutant where reconcile.apply_meta skips handoffs survives every test module that names apply_meta, because the confinement fixture holds only a retro.

## Steps to Reproduce

In a throwaway copy, reword the read-only helper list in sdlc-studio/trd.md (for example 'these helpers only read') to list critic brief again, and run tools/tests/`test_lean_trd_refresh.py`: green.

## Proposed Fix

Pin the worktree path the TRD names, judge the read-only list by meaning rather than one phrasing, name --skip-git-repo-check, reword the exfiltration row's opening clause, and add a `shell_allowed_for` test with `allow_external` on.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The builder of the BG1516, BG1517 and BG1531 repairs (RUN-01M7TTK3) left these non-blocking gaps.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a throwaway copy, reword the read-only helper list in sdlc-studio/trd.md (for example 'these helpers only read') to list critic brief again, and run...
- [ ] **AC3** The proposed fix lands, pinned by a test: Pin the worktree path the TRD names, judge the read-only list by meaning rather than one phrasing, name --skip-git-repo-check, reword the exfiltration row's...

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Run nineteen's TRD repairs hold; their checks accept rewordings and leave claims unpinned. Non-blocking test gaps. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
