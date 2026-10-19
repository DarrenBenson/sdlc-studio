# BG1076: The rejoinder brief asks a reviewer to rule each earlier finding, but the return contract has no place for the rulings, so a round-2 verdict that writes them untagged is refused by critic.py record

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_rulings.py, changelog.d/BG1076.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M59TRM, 2026-10-19: US1075's round-2 verdict refused ('these findings carry no origin') until re-emitted with '[new] info, round-1 rulings:'; US1079's round-1 verdict refused for an unescaped ';'.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T13:07:53Z

## Summary

`critic.py brief --rejoinder` asks the reviewer to rule each round-1 finding CLOSED, OVER-CLAIMED or MOVED. The return contract offers only VERDICT, ISSUES (every item tagged [regression], [new] or [pre-existing]) and BLOCKING, so a reviewer writes the rulings as an ISSUES item and either leaves it untagged, which `record` refuses outright, or tags it `[new] info`, which records the rulings as a new finding. In RUN-01M59TRM two of three round-2 verdicts needed re-emitting before they could be recorded: one for an untagged rulings item, one for an unescaped ';' inside a finding.

## Steps to Reproduce

Brief a REJECTed unit with `critic.py brief --unit <id> --seat qa --rejoinder <verdict>`; return a block whose ISSUES opens with 'Round-1 rulings: ... CLOSED ...'; `critic.py record --from-verdict` -> 'record refused: these findings carry no origin'.

## Proposed Fix

Give the rejoinder contract a RULINGS line, parsed and stored beside the round, or accept an untagged rulings item there and record it as such.

## Acceptance Criteria

- [ ] **AC1** A round-2 verdict that rules the earlier findings in a place the contract names is recorded without re-emitting, and the rulings are stored as rulings
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_rulings.py -k rulings_are_recorded_as_rulings

## Impact

Every round-2 verdict risks a refusal and a second exchange with the reviewer, and rulings recorded as [new] findings inflate the finding count.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
