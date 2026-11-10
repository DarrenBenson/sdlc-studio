# CR-0692: A change evidence pack per release, built from the run's record and grouped by risk and compliance class

> **Status:** Proposed
> **Parent:** RFC0063
> **Depends on:** RFC0064 (D4, D5); EP0275; EP0276; EP0280
> **Related:** RFC0064
> **Priority:** High
> **Type:** feature
> **Size:** L
> **Date:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T12:22:11Z

## Summary

RFC0063 WS4 and O10: a change that reaches a change board carries one evidence pack, built from what the run recorded rather than written afterwards and readable without running the tool. Graham Doyle approves from that one document.

Filed now with its dependency recorded (D0456): grouping the pack by risk and compliance class, and what a class changes, wait for RFC0064's D4 (who sets the class) and D5 (what a class changes). Criteria 1, 2 and 4 do not depend on RFC0064 and can be refined first.

## Impact

Serves O10, Abena Osei's End goal 1 and Graham Doyle's End goals 1 and 2. Builds on EP0275 (the evidence annex), EP0276 (the report of record from the committed tree) and EP0280 (a recorded verdict is what the reviewer wrote).

## Acceptance Criteria

- [ ] One command writes a release's evidence pack from committed records only: the signed reports, verdicts, verify runs, known issues and the accountable person for each unit in the release
- [ ] Each change in the pack states what changed, which criteria passed, who reviewed it independently, what is known to be wrong, and the accountable person, never 'the agent'
- [ ] Pending RFC0064 D4 and D5: the pack groups changes by risk and compliance class, and states for each class what it changed in review
- [ ] The pack reads without running the tool, and the companion dashboard can read it through the versioned evidence annex (EP0275)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Raised |
