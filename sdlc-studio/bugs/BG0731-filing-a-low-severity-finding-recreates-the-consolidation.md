# BG0731: filing a Low-severity finding recreates the consolidation bucket that was just ruled not to be a change request

> **Status:** Open
> **Merged from:** BG0738 (backlog sweep 2026-09-24, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

D0217 retired CR0511 and CR0575 on 2026-09-20, ruling that a consolidation bucket is not a change request: it cannot be refined, because `refine` decomposes a request into sized units and a bucket whose only shared property is a severity band has no coherent decomposition. Both were Rejected with that reason recorded. On 2026-09-21, the very next day, filing two Low-severity findings created CR0592 `Low-severity bugs (consolidated)` - the same artefact, same `Consolidation: low-severity-bugs` key, same permanent residence at the bottom of the discovery backlog. The mechanism is `triage_noise.should_consolidate`, which routes any Low finding into a themed bucket instead of minting its own artefact. So an operator ruling that removes a bucket is undone by the next Low finding anybody files, and the ruling has no way to reach the code that recreates it.

## Steps to Reproduce

1. Note D0217 and the Rejected CR0511/CR0575. 2. File any finding with `--severity Low`. 3. A new `Low-severity X (consolidated)` CR appears in Proposed, counted by `status` as discovery awaiting refine. Observed 2026-09-21: CR0592, one day after the retirement.

## Proposed Fix

Decide what a Low finding should be and make the code and the decisions log agree - they currently do not. Either consolidation is right and D0217 was wrong, in which case the bucket needs to be refinable or excluded from the awaiting-refine count so it stops reading as a live option; or D0217 is right and Low findings should mint their own artefacts like every other severity, with the noise problem solved by triage rather than by a holding pen. What must not persist is the present state, where an operator retires a bucket and the filer silently rebuilds it. If consolidation stays, `should_consolidate` should at least refuse to reuse a consolidation key whose previous bucket was Rejected, and say why.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: D0217 retired CR0511 and CR0575 on 2026-09-20, ruling that a consolidation bucket is not a change request: it cannot be refined, because `refine` decomposes a...
- [ ] **AC2** The proposed fix lands, pinned by a test: Decide what a Low finding should be and make the code and the decisions log agree - they currently do not.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
