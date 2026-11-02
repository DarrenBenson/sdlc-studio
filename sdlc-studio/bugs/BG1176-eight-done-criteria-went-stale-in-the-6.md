# BG1176: Eight Done criteria went stale in the 6.2 work: five Verify greps lost their sentences to run four's spec refreshes, and three criteria still name v6.1.0 or a folded fragment after the cut

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/stories/US0201-prd-sections-3-10-11-to-the-shipped.md, sdlc-studio/stories/US0203-document-the-version-check-urllib-and-sprint-plan.md, sdlc-studio/stories/US0206-tsd-record-the-blocking-80-coverage-gate-and.md, sdlc-studio/stories/US1101-the-trd-s-type-registry-network-section-adr.md, sdlc-studio/stories/US1103-the-prd-s-baseline-reads-v6-1-0.md, sdlc-studio/bugs/BG0945-bg0940-s-changelog-entry-says-a-page-with.md
> **Evidence:** scratchpad triage-red-acs.md (the triage of the release gate's 11 red criteria) and US1101's full-tier verdict of 2026-11-02.
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T16:14:23Z

## Summary

2026-11-02, `gate.py --release` at e217a3b8 and US1101's full-tier re-review. Five Verify lines grep sentences that run four's refreshes rewrote: US0201 AC2 and US0203 AC1 (8f380767, US1104, PRD), US0203 AC3 (0f26c3e8, US1101, TRD), and US0206 AC1 and AC2 (d4028a31, US1102, TSD). Each phrase is present at v6.1.0 and absent at 519d125c, and each claim still holds in new words. The v6.2.0 cut (8267f275) left three criteria false of the tree: US1101 AC3 and US1103 AC1 still say the coverage line names v6.1.0 plus 6.2 on main, though the TRD and PRD and their tests now read the release package.json declares plus the next minor series. BG0945 AC1 still names changelog.d/BG0940.md, which the cut folded into the 6.2.0 section. No code is wrong. The criteria are.

## Steps to Reproduce

1. `python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --ids US0201,US0203,US0206 --dry-run` at e217a3b8: five criteria fail on a missing grep phrase.
2. Read US1101 AC3, US1103 AC1 and BG0945 AC1 against sdlc-studio/trd.md:37, sdlc-studio/prd.md and the CHANGELOG's 6.2.0 section.

## Proposed Fix

Re-point each of the five greps, never retire it, at the sentence that carries its claim today: `judges only the forecast recorded at plan time` (prd.md), `reach the network on these outbound, optional paths only` (prd.md), `Network access is limited to the outbound paths` (trd.md), `80% statement, the blocking CI floor` (tsd.md) and `bandit covers the shipped script tier only` (tsd.md). Reword US1101 AC3 and US1103 AC1 to name the release package.json declares plus the next minor series on main, and BG0945 AC1 to name BG0940's entry wherever it is read: the fragment before a cut, the released section after. Add a revision row to each artefact naming this bug. Change no code and add no changelog fragment (D0396).

## Acceptance Criteria

- [ ] **AC1** Each of the five re-pointed greps finds its sentence, and `verify_ac.py run --ids US0201,US0203,US0206 --dry-run` passes every criterion.
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --ids US0201,US0203,US0206 --dry-run
  - **Verified:** yes (2026-11-02)
- [ ] **AC2** US1101 AC3 and US1103 AC1 no longer state the literal v6.1.0 plus 6.2, and BG0945 AC1 no longer names changelog.d/BG0940.md as the only place its entry is read. `verify_ac.py run --ids US1101,US1103,BG0945 --dry-run` passes every criterion.
  - **Verify:** shell ! grep -nE '^- \*\*AC[0-9]+:\*\*.*v6\.1\.0 plus 6\.2' sdlc-studio/stories/US1101-the-trd-s-type-registry-network-section-adr.md sdlc-studio/stories/US1103-the-prd-s-baseline-reads-v6-1-0.md && python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --ids US1101,US1103,BG0945 --dry-run
  - **Verified:** yes (2026-11-02)

## Impact

`gate.py --release` is red, so 6.2.0 cannot be tagged, and three Done criteria state what the tree no longer holds.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
