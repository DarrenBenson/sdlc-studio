# CR-0305: audit_cost.py estimates from one frozen reference run and never records actuals - give the audit the record-forecast/record-actual loop the skill preaches for sprints

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/audit_cost.py, .claude/skills/sdlc-studio/reference-audit.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; audit-process-retro wf_9903a6e6-53a

## Summary

reference-audit.md#audit-preflight step 4 says 'when the run finishes, report actuals against the estimate' - but nothing records them, so the estimator's constants (~8 candidates/lens, ~36k tokens/agent) stay frozen at the one measured reference run. The 2026-07-16 full project run estimated ~217 agents / ~7.8M tokens and actually cost 265 agents / ~12.4M tokens (~8 candidates/lens held, but candidates ran 122 with 3 find rounds, and an outage forced rework the estimate has no contingency for). The skill's own sizing doctrine (RFC0038) is record the forecast, record the actual, recalibrate from evidence - the audit estimator should obey it too.

## Impact

Every audit pre-flight estimate is calibrated to a single 2026-07-15 reference run; the operator confirms multi-million-token fan-outs against constants that drift from reality with nothing closing the loop.

## Acceptance Criteria

- [ ] `audit_cost.py` gains a 'record' subcommand appending {date, lenses, rounds, votes, estimated agents/tokens, actual agents/tokens/minutes, notes} to a committed evidence ledger
- [ ] When ledger entries exist, the estimate is derived from measured medians (falling back to the shipped constants) and the output names which basis it used
- [ ] reference-audit.md#audit-preflight step 4 instructs recording actuals via the subcommand, not just reporting them in chat

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
