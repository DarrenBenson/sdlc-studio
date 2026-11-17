# BG1550: Public docs say the evidence pack refuses to name an agent as accountable, but the check is a word match on agent

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** docs/engineering-leaders.md, .claude/skills/sdlc-studio/reference-scripts-domain.md, tools/tests/test_engineering_leaders_page.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, cross lens, survived 3 of 3 refute votes; observed at docs/engineering-leaders.md line 15-17 ('The pack refuses a report nobody has signed, and it refuses to name an agent as the accountable person'); also docs/release-notes-v6.4.0.md 'a signer who reads as an agent refuses the pack' and reference-scripts-domain.md:94-95; code at .claude/skills/sdlc-studio/scripts/evidence_pack.py:44-48,134-151 and sprint.py:10954-10985
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:15Z

## Summary

docs/engineering-leaders.md lines 15 to 17 state without qualification that the evidence pack refuses to name an agent as the accountable person, and reference-scripts-domain.md lines 94 to 95 say the same. What enforces it is `principal_refusal` in `evidence_pack.py`: it refuses a blank principal, one that holds the word agent or subagent, and one the review ledgers record as an author of that report's own units. `sprint sign` itself refuses only a blank principal, the unit's author and a recorded reviewer. Any agent principal that avoids the word and is not that run's recorded builder, such as an orchestrator's model name, is accepted by both and printed as the accountable person who signed the report. The CHANGELOG entry for 6.4.0 describes the heuristic accurately, so only the public page and the reference over-claim. The page is the one a head of engineering reads to judge the evidence, and it says every claim links what enforces it.

## Steps to Reproduce

1. Read docs/engineering-leaders.md lines 15 to 17 and reference-scripts-domain.md lines 94 to 95. Both state the refusal as absolute.
2. From the scripts directory, import `evidence_pack` and call `principal_refusal` with a signature whose principal is Claude Opus 5.5 and an authors list holding builder-US1155.
3. Observed: it returns None, so the pack would name that principal as accountable. The same holds for GPT-5 orchestrator, sdlc-builder and the bot.
4. Positive control: the principal an AI agent is refused with the message that it reads as an agent and an agent is never the accountable person.
5. Expected: the public wording matches the check, or the check refuses what the wording says.

## Proposed Fix

Reword the sentence in docs/engineering-leaders.md and the matching one in reference-scripts-domain.md to state what is enforced: the pack refuses a blank principal, one that reads as an agent by name, and one recorded as an author of the report's own units, and it cannot tell a person from an agent session signing under another name, so the named person stays the operator's responsibility. Add a test beside the existing factual wording tests in tools/tests/`test_engineering_leaders_page.py` that the page does not state the refusal as absolute. A stronger check, such as a configured list of people allowed to sign, is a separate design question and not part of this correction.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: docs/engineering-leaders.md lines 15 to 17 state without qualification that the evidence pack refuses to name an agent as the accountable person, and...
- [ ] **AC2** The proposed fix lands, pinned by a test: Reword the sentence in docs/engineering-leaders.md and the matching one in reference-scripts-domain.md to state what is enforced: the pack refuses a blank...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
