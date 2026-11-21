# BG1639: The PRD drift checkers accept rewordings of the claims they exist to refuse

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_prd_refresh.py, changelog.d/BG1525.md, changelog.d/BG1553.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T00:05:43Z

## Summary

The repair round for BG1525, BG1180 and BG1553 (RUN-01M7TTK3) left these checker gaps, each re-tested by the reviewer or the repairer. BG1525's single-exception regex lets 'The sole exception is ...' and 'Apart from `two_backlog.enforce`, ...' through; its reason pattern never compares the stated value with the shipped one; a filler reason passes. BG1180's `_NO_FETCH_RE` matches a negation anywhere in the sentence, and the id-allocation check misses '`next_id.py` fetches', 'Allocating an id fetches', 'id-allocation' and 'pulls'. BG1553's `env_reads()` getenv and `_env`-suffix branches are exercised by no test.

Round two of BG1525, BG1180 and BG1553 (RUN-01M7TTK3, verdicts 3327f43dc85c-7ad77e02, 390a4ea54db9-7e5ab7f8, d96c2271f869-d399f70a) adds: the gate-key collector misses a `*.enforce` key only a script reads (contradicting changelog.d/BG1525.md), misses a mode list written in another form, and nothing checks the PRD's count word; the harmless-fetch check misses 'Each sprint boundary fetches origin\; a failure there is ignored' and nothing pins how passages() splits list items; env_reads() matches a read to the wrong variable when a parameter or constant name is shared across functions or modules, so it passes unreported (contradicting its docstring and changelog.d/BG1553.md), and six of its new branches are pinned by nothing.

BG1525's round-two review by its round-one reviewer (verdict 495e843a47b2-221479af) adds three gaps in the new key scanner: keys whose modes are described in prose, a script-side check that matches only a key's last segment, and three-level key names.

## Steps to Reproduce

In a throwaway copy of sdlc-studio/prd.md, reword the Feature Flags exception to 'The sole exception is `two_backlog.enforce`' and run tools/tests/`test_lean_prd_refresh.py`: green.

## Proposed Fix

Judge each claim by the paragraph's meaning against the shipped value (read from config-defaults.yaml or the code) rather than by fixed phrasings, anchor the no-fetch negation to the fetch clause, and add tests over the getenv and `_env`-suffix collector branches.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The repair round for BG1525, BG1180 and BG1553 (RUN-01M7TTK3) left these checker gaps, each re-tested by the reviewer or the repairer.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a throwaway copy of sdlc-studio/prd.md, reword the Feature Flags exception to 'The sole exception is `two_backlog.enforce`' and run...
- [ ] **AC3** The proposed fix lands, pinned by a test: Judge each claim by the paragraph's meaning against the shipped value (read from config-defaults.yaml or the code) rather than by fixed phrasings, anchor the...

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it affects only this repository's own CI, hooks or tools, nothing a consuming project installs. Gaps in this repository's own PRD drift checkers, accepting rewordings; the shipped skill is unaffected and the PRD is reviewed by hand. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
