# CR-0294: Per-AC 'Verified: yes' stamps ride on non-discriminating Verify selectors: US0172/US0173 share a byte-identical command, US0163/US0166 run one whole-file command for two ACs

> **Status:** Complete
> **Decomposed-into:** EP0075
> **Priority:** Medium
> **Type:** process
> **Size:** S
> **Affects:** sdlc-studio/stories/US0172-per-attempt-telemetry-records-carry-an-attempts-list.md, sdlc-studio/stories/US0173-true-cost-with-rework-unit-cost-sums-priced.md, sdlc-studio/stories/US0163-*.md, sdlc-studio/stories/US0166-ship-a-stop-hook-installer-and-redefine-sprint.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

The workspace's claim is per-AC machine-checkability, but US0172 AC1 and US0173 AC1 - different behaviours in different stories - carry the byte-identical `-k AttemptsAndCost` selector against one shared test class (`test_telemetry.py`:566): delete every `unit_cost` test and US0173 stays 'Verified: yes' because US0172's `attempts_of` tests still match. Likewise US0163 AC1/AC2 and US0166 AC1/AC2 run identical whole-file commands, so an AC-specific regression cannot fail its own AC distinctly. This contradicts reference-verify.md's own guidance ('Prefer narrow scope', 'Name tests after ACs'). One panel vote refuted citing the mutation gate as the systemic backstop; two confirmed no per-AC-uniqueness rule or lint exists and the false-green mechanism is real. Filed as process CR: split the selectors in the affected stories and optionally lint duplicate Verify lines.

## Impact

The workspace's claim is per-AC machine-checkability, but US0172 AC1 and US0173 AC1 - different behaviours in different stories - carry the byte-identical `-k AttemptsAndCost` selector against one shared test class (`test_telemetry.py`:566): delete every `unit_cost` test and US0173 stays 'Verified: yes' because US0172's `attempts_of` tests still match.

## Acceptance Criteria

- [ ] US0172 and US0173 select distinct test classes/methods so each AC fails on a regression in its own behaviour
- [ ] US0163 and US0166 per-AC Verify lines are narrowed (-k per AC) rather than whole-file
- [ ] Optional: a verify lint flags byte-identical Verify commands appearing under different ACs/stories

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
