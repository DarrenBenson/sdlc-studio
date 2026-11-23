# BG1721: BG1550 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** docs/engineering-leaders.md, .claude/skills/sdlc-studio/reference-scripts-domain.md, tools/tests/test_engineering_leaders_page.py, changelog.d/BG1550.md
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T07:56:36Z

## Summary

BG1550 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the absolute-refusal check still passes plain refusals of an agent. `_REFUSAL` (tools/tests/test\_engineering\_leaders\_page.py:234-236) reads refuse, reject, bar, block and exclude, and a negated accept, admit, allow, let, name, sign or be. Put beside the good paragraph, "It prevents an agent from being the accountable person.", "It forbids an agent as the accountable person.", "Agents are not permitted to sign.", "It will not take an agent as accountable." and "It keeps agents out of the accountable role." each return no problem through `signer_check_problems`. AC1 fails on the page "stating without qualification that the pack refuses to name an agent as accountable", and each of these sentences states it. The changelog now lists the verbs, so it no longer over-claims, but the test is still held to the words the round-one probes used rather than to the claim. A closed world over the clauses that name an agent in the change approval section and the reference entry would end it, as BG1056 did for pip (test\_prereq\_list\_is\_ci\_list.py:9); BLOCKING: [new] the absolute-refusal check refuses true statements of the limit. "It does not block an agent that signs under a person's name." and "An agent that signs under a person's name is not refused." are each reported as "states the agent refusal as absolute". The check reads a negation only in front of the admitting verbs, never in front of refuse, reject, bar, block or exclude (tools/tests/test\_engineering\_leaders\_page.py:234-236 and 264-266). Both sentences say what AC1 asks the page to say, that the pack does not stop an agent signing under a person's name, so the guard refuses the page if the page words the limit that way; RULINGS: Round one, ruled. "the absolute-refusal check fires only on the stem" MOVED. The five rewordings it named, and "It never names an agent as accountable." added to the reference entry, now turn their tests red (checked). changelog.d/BG1550.md now names the verbs it reads instead of claiming every unqualified refusal. Other plain refusals still pass (first finding). "`reference_entry` ends the entry at a heading of any level" CLOSED. Narrowing the end to a level-three heading, widening it to seven hashes, or unanchoring it are each killed by the new level and seven-hash cases. My mutation pass on this round's code killed all 10 applied mutants: the by-name lookahead, its optional comma, the word bound on bar, be, n't, exclude, the three heading mutants, and "It will not accept an agent as accountable." added to the reference entry. A mutant dropping the one-word gap was not applied, because its text occurs twice in the file. Neither page has changed since round one, and neither has evidence\_pack.py since the base, so the round-one claim inventory stands. I checked that by running `principal_refusal` and `unit_authors` over planted ledgers. `verify_ac.py run --id BG1550 --dry-run` is 2 of 2 pass.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1550 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1550 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the absolute-refusal check still passes plain refusals of an agent. `_REFUSAL` (tools/tests/test\_engineering\_leaders\_page.py:234-236) reads refuse, reject, bar, block and exclude, and a negated accept, admit, allow, let, name, sign or be. Put beside the good paragraph, "It prevents an agent from being the accountable person.", "It forbids an agent as the accountable person.", "Agents are not permitted to sign.", "It will not take an agent as accountable." and "It keeps agents out of the accountable role." each return no problem through `signer_check_problems`. AC1 fails on the page "stating without qualification that the pack refuses to name an agent as accountable", and each of these sentences states it. The changelog now lists the verbs, so it no longer over-claims, but the test is still held to the words the round-one probes used rather than to the claim. A closed world over the clauses that name an agent in the change approval section and the reference entry would end it, as BG1056 did for pip (test\_prereq\_list\_is\_ci\_list.py:9)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: BLOCKING: [new] the absolute-refusal check refuses true statements of the limit. "It does not block an agent that signs under a person's name." and "An agent that signs under a person's name is not refused." are each reported as "states the agent refusal as absolute". The check reads a negation only in front of the admitting verbs, never in front of refuse, reject, bar, block or exclude (tools/tests/test\_engineering\_leaders\_page.py:234-236 and 264-266). Both sentences say what AC1 asks the page to say, that the pack does not stop an agent signing under a person's name, so the guard refuses the page if the page words the limit that way
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1550 AC1 still passes: Given docs/engineering-leaders.md, when its account of the evidence pack's signer check is read, then it states the three refusals that are enforced (a blank principal, one that reads as an agent by name, one recorded as an author of the report's own units) and that the pack cannot tell a person from an agent session signing under another name, so the named person is the operator's responsibility. Fails on: the page stating without qualification that the pack refuses to name an agent as accountable.
  - **Verify:** pytest tools/tests/test_engineering_leaders_page.py::FactualWordingTests::test_the_agent_refusal_is_not_stated_as_absolute
- [ ] **AC4** BG1550 AC2 still passes: Given `reference-scripts-domain.md`, when its evidence-pack entry is read, then it states the same three refusals and the same limit as the public page. Fails on: the reference still claiming an absolute refusal, or the two pages disagreeing on what is enforced.
  - **Verify:** pytest tools/tests/test_engineering_leaders_page.py::FactualWordingTests::test_the_reference_states_the_same_refusals_and_limit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
