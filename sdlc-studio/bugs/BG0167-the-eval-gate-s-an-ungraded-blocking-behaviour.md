# BG0167: The eval gate's 'an ungraded blocking behaviour fails the gate' only sees scenarios someone started grading - a wholly-ungraded scenario is invisible and the run prints 'gate pass'

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/eval_run.py, sdlc-studio/tsd.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

tsd.md sells the eval gate as 'Fails on any blocking behaviour that failed or was left ungraded - a behaviour nobody graded is not a pass' (lines 172, 289). `eval_run.py`'s report computes ungraded behaviours as expected minus recorded, but only for scenario ids present in the results JSON (`for sid, behaviours in sorted(data.items())`); it never enumerates evals/scenarios/*.json (no glob/iterdir anywhere in the file). A scenario with zero recorded verdicts contributes nothing, so all of its blocking behaviours are skipped silently: grade one behaviour in scenario 01 and report prints 'gate pass (0 blocking failure(s)/ungraded)' while scenarios 02-08 were graded by nobody. The partial-grading guard catches the easy case and exempts the dangerous one (LL0013 + LL0008) in the exact tool the TSD holds up as the honesty gate; BG0079's history shows the manual drive-each-scenario ceremony does get skipped in practice. Verified 3x.

## Steps to Reproduce

Record one passing behaviour for scenario 01 only; run `eval_run.py report` - it prints 'gate pass' and exits 0 although every blocking behaviour in scenarios 02-08 is ungraded.

## Proposed Fix

Make report enumerate evals/scenarios/*.json and treat every blocking behaviour of a scenario absent from the results file as ungraded (gate fail, listing the scenario); add a wholly-ungraded-scenario test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
