# CR-0725: Give the advisory disclosure lint lane a committed baseline that fails on a rise

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** M
> **Affects:** package.json, .claude/skills/sdlc-studio/scripts/disclosure.py, sdlc-studio/tsd.md, tools/tests/test_baselines_only_shrink.py, .claude/skills/sdlc-studio/scripts/tests/test_disclosure.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, tsd lens, survived 3 of 3 refute votes; observed at sdlc-studio/tsd.md Static / Lint table row Disclosure (line 276), CI Quality Gates row Disclosure (lint:disclosure) (line 707), NFR row Scalability - "Progressive disclosure keeps always-loaded context minimal" (line 429); package.json lint script
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:11Z

## Summary

The `lint:disclosure` lane runs `disclosure.py` without `--strict` in every lint chain, so it reports its findings and always exits 0. It reports 58 findings today: 33 reference or help files with no load trigger, 18 scripts not executable, 4 help pages missing a block, 2 templates with no placeholder and 1 script with no help. The TSD records that the lane is advisory, but nothing bounds what it tolerates, so a new reference file with no `Load when:` trigger lands unnoticed among 58 standing lines. The project's other tolerated debts (test noise, corpus verify and the release rehearsal) each carry a committed baseline that fails on a rise; this lane has none. The progressive-disclosure requirement in the TSD is marked as verified on the strength of `check_budgets.py` alone, which measures line counts and not whether a file is loaded on demand.

## Impact

Maintainers and CI readers see 58 warnings on every lint run and learn to skim past them, which is the habit the TSD itself warns against for test output. A contributor who adds a reference or help file with no load trigger gets a green lint, so the always-loaded context the requirement protects can grow without any gate noticing.

## Acceptance Criteria

- [ ] A committed baseline under tools/ records the current disclosure findings by kind and name, and the `lint:disclosure` lane exits non-zero when a finding appears that the baseline does not hold
- [ ] The lane prints one summary line when the findings equal the baseline, and lists only the findings that are new
- [ ] tools/tests/`test_baselines_only_shrink.py` covers the new baseline, so a commit that grows it fails
- [ ] The TSD rows for the disclosure lane and for the progressive-disclosure requirement say the lane fails on a rise against its baseline, and the requirement row names the lane beside `check_budgets.py`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
