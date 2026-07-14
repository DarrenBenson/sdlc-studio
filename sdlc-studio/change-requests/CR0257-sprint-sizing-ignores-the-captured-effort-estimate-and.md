# CR-0257: Sprint sizing ignores the captured Effort estimate, and bugs carry no size at all

> **Provenance:** RFC0034 (estimate-side workstream)
> **Status:** Proposed
> **Priority:** P3
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/scripts/file_finding.py

## Summary

Two disconnected size vocabularies. CRs carry a human Effort: S/M/L field captured at filing, but sprint.py never reads it - its WSJF size comes only from a seat-scored estimate (.local/wsjf-inputs.json) or the cognitive complexity of a unit's Affects files, falling back to `DEFAULT_UNKNOWN_SIZE`=3. So for a backlog with no Affects declarations and no seat-scoring (the common case), WSJF collapses to plain priority order and the token forecast collapses to a flat `BASE_TOKEN_BUDGET` x `unit_count` (proven: the internal-hardening plan forecast ~500k = 50k x 10, complexity contributing zero). The one estimate a human actually recorded does not count. Bugs are worse off: they have no effort/size field at all, only Severity (which is priority, not size), so a bug can never be sized even in principle.

## Provisional calibration applied (2026-07-14) - the next sprint is its test

The token forecast has been calibrated against measured actuals for the first time.
`TOKENS_PER_COGNITIVE` 5,000 -> **600**; `BASE_TOKEN_BUDGET` stays 50,000 (validated: the one
complexity-0 unit measured 46,359).

Evidence - six units, all delivered by instrumented subagents and recorded in telemetry:

| unit | complexity | actual | old forecast |
| --- | --- | --- | --- |
| CR0250 | 0 | 46,359 | 50,000 |
| BG0130 | 15 | 42,687 | 125,000 |
| BG0126 | 39 | 46,792 | 245,000 |
| CR0249 | 39 | 98,513 | 245,000 |
| BG0127 | 52 | 65,625 | 310,000 |
| CR0248 | 52 | 84,302 | 310,000 |
| **batch** | | **384,278** | **1,285,000 (3.3x over)** |

At 600 the batch forecast lands at 1.09x actual instead of 3.34x. The old 3.3x inflation was
not harmless: a 10-unit batch was cut to 5 on the belief it was too big, when it was not.

**Two honest limits, both pinned in `tests/test_token_calibration.py` so they cannot be
forgotten:**

1. **This is a HYPOTHESIS, not a settled calibration.** Six units, one model, one repo, one day.
   The next sprint is its falsification test. (The value it replaces was never validated at all,
   so this is strictly better - but it is not yet earned.)
2. **Complexity is a weak PER-UNIT predictor; this is a BATCH tool.** Two units of identical
   complexity (39) cost 46,792 and 98,513 - 2.1x apart. The cognitive complexity of the FILE is a
   poor proxy for the WORK done in it. The batch errors wash out; the per-unit ones do not. A
   work-based input (rather than file-complexity) is the likely next model, once there is data to
   justify it.

## Impact

Every sprint plan whose units lack Affects declarations or seat-scoring - i.e. most of them. The token forecast and WSJF ordering are currently uninformed (flat per-unit constant), so 'sizing' gives the operator no real signal despite an Effort estimate being on file. Fixing it makes the estimate the operator already provides actually shape the plan.

**Effort:** M

## Acceptance Criteria

- [ ] sprint.py reads the CR Effort field and uses it as a WSJF size input when no seat-score is present, ranked above the unknown default. Verify: rg -q -i 'effort' .claude/skills/sdlc-studio/scripts/sprint.py
- [ ] Bugs carry an effort field (template + filer), so a bug can be sized. Verify: rg -qi 'effort' .claude/skills/sdlc-studio/templates/core/bug.md
- [ ] The token forecast reflects Effort when Affects/complexity is absent, rather than a flat base x count. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k sprint

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
