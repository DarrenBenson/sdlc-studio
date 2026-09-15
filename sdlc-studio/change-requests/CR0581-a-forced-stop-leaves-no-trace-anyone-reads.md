# CR-0581: A forced stop leaves no trace anyone reads, needs no reason or principal, and shares the outcome word stopped with two other endings

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/help/sprint.md
> **Evidence:** US0823 stakeholder consult, RUN-01M2JA6J 2026-09-15 (consult-US0823-stakeholders.md), list B items B2 (High for the Primary), B3 (Medium) and B4 (Low), evidence E1-E3; changelog.d/US0823.md discloses the uncommitted record and the silent next plan.
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

stop --force records the unanswered set it waived only in the archived run record under sdlc-studio/.local/, which git ignores and no shipped reader reads; it writes no handoff and does not touch reviews/LATEST.md. `pending_handoff` returns None when the last run left no handoff (sprint.py:3419-3422), so the next plan is silent after a forced stop, and `handoff_line` prints 'nothing carried over - its backlog is clear' when Remaining is zero (sprint.py:3517-3520) even though a Done or Fixed unit with a standing REJECT sits in the unanswered set and in neither Remaining nor the worklist. --reason is optional ('no reason given') and no principal is recorded when --force waives a non-empty set (sprint.py:10543-10620, 11504). 'stopped' is one outcome word for three endings - a partial-verdict close, a pending-decision stop and a forced stop over unanswered questions; the record separates them through stop.cause and unanswered, but no report or handoff head does.

## Impact

The operator and team who plan the next run: a stop-ship question waived on Friday is invisible on Monday unless someone opens a gitignored JSON file, and nobody can tell who waived it or why. Raised by all three consulted personas; the Primary persona rates the missing trace High and the missing reason Medium.

## Acceptance Criteria

- [ ] After stop --force over a non-empty unanswered set, the next sprint.py plan names the waived units, beside a forced stop over an empty set, which adds nothing
- [ ] stop --force over a non-empty set without --reason is refused, naming the flag; with --reason the record carries the reason and the acting principal
- [ ] The close report and the handoff head name a partial-verdict close, a pending-decision stop and a forced stop over unanswered questions differently

## Recommendation

Have the plan's last-run notice read the closed run state's unanswered set. Have stop --force write a handoff, as the boundary stop does, or an outcome block in reviews/LATEST.md. Require --reason when --force waives a non-empty set and record the acting principal as attribution, reusing the trust-boundary predicate the carried-table ruler check introduces; no approver. Name the three endings distinctly in the report and handoff head. Committing run records under .local/ stays declined.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
