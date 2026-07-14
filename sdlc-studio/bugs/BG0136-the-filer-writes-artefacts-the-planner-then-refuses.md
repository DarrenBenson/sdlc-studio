# BG0136: The filer writes artefacts the planner then refuses: no --affects flag exists, so every filed bug is unplannable

> **Status:** Open
> **Severity:** High
> **Effort:** M
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Depends on:** BG0133
> **Raised-by:** sdlc-studio; agent; v1

## Summary

CR0260 makes sprint plan refuse an ungroomed unit - one lacking Affects or a size. But `file_finding.py` cannot record Affects AT ALL: there is no --affects flag. So every bug it files is born ungroomed, and the planner refuses it. The two ends of the pipeline disagree about what a complete artefact is - the filer says fine, the planner says unplannable. That is LL0016: when two code paths build or judge the same artefact they must agree on what it MEANS. Proved immediately by dogfooding: the first run of the new gate refused BG0133, BG0134 and BG0135, all three filed that same day by `file_finding.py`, all three lacking Affects because the tool provides no way to supply it. The grooming gap the gate exists to close is being manufactured by our own filer, one artefact at a time, and the repair is then handed to an operator at plan time - the wrong person, at the wrong moment. The author knows which files are involved when they file. Nobody knows it better later.

## Steps to Reproduce

1. Run `file_finding.py` file --type bug --affects x.py ... -> error: unrecognized arguments: --affects. The flag does not exist. 2. File the bug without it; it is written without complaint, with no Affects line. 3. Plan a batch containing it: sprint.py plan --bugs Open --no-fetch --skip-personas -> exit 2, no plan printed, the bug named as ungroomed for lacking Affects. The filer created the exact defect the planner refuses.

## Proposed Fix

Add --affects to `file_finding.py` (and check artifact.py new/batch agrees), and make the filer demand what the planner demands FROM ONE SHARED DEFINITION of groomed - do not restate the rule in two places or they will drift again. sprint.breakdown already owns the predicate; the filer should call it rather than re-express it. Require affects and effort for a bug and a CR at filing, refusing without them exactly as the filer already refuses a hollow artefact for missing steps/fix. Honour the same recorded escape (sprint.breakdown: judgement) so an operator who has opted out is not blocked at the filer either.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
