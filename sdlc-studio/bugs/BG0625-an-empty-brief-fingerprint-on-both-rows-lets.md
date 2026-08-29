# BG0625: an empty brief fingerprint on both rows lets a different seat's APPROVE retire a REJECT, which is the defect BG0607 exists to close

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Adversarial review of BG0607, wave 3 of RUN-01M0YXN3, 2026-08-26, finding 6. Reproduced by the reviewer in an isolated copy and reported as latent rather than live.
> **Verification depth:** functional [[derived: criteria 5; plan rows 5; executed 5; killed 5; survived 0; not-run 0; entry point 1 of 5 criteria through the shipped CLI, 4 in-process | fp 9f9910077dae ]] (five criteria, every mutant applied to the real file with bytecode purged and the tree restored after each. One reaches the shipped CLI - `critic.py record` twice then `critic.py show --format json`, read as the json payload rather than as a substring of the text branch, which prints a raw dict. AC5 is measured on this repository's own 856-row ledger rather than on a fixture, because a code mutant cannot move a claim about what the corpus holds.)
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_unanswered_rejects` (critic.py:528-530) retires a REJECT when a later APPROVE carries the SAME brief fingerprint. An empty string equals an empty string, so two rows that both lack a brief match each other and a cross-seat approval retires the rejection - exactly the behaviour BG0607 replaced. Reproduced in isolation: REJECT by `engineering` with an empty brief, then APPROVE by `product` with an empty brief, and the standing verdict is APPROVE. NOT latent - LIVE, and the filing said otherwise. Measured 2026-08-27 over `critic.read_verdicts`: 556 of 856 delivery rows carry the ledger's absent-brief placeholder, the literal string `-`, and NINE rejections are already retired by a later placeholder-brief approval. FOUR of those nine are cross-seat - US0570, US0571, US0575 and US0576, where the `qa` seat rejected and the `engineering` seat's approval retired it - so four units are certified approved today while an independent seat's rejection stands unanswered. That is the two-role rule failing inside the record the rule is enforced from.

The remaining five are the SAME reviewer retiring its own rejection in a later round, which is correct behaviour and is what `test_critic.py::test_a_seat_may_retire_its_own_reject` exists to protect. Any rule that closes the four by treating an absent fingerprint as matching nothing also freezes those five permanently, so the fix is not the fail-closed one this bug was filed with.

## Steps to Reproduce

1. Record a REJECT with an empty brief from one seat. 2. Record an APPROVE with an empty brief from a DIFFERENT seat. 3. `critic.py show --unit <id>` prints APPROVE. Reproduced 2026-08-26 in an isolated fixture during the BG0607 review.

## Proposed Fix

The fix this bug was filed with does not work and would not have been caught by its own
criteria. `if not fp: ...` never fires, because an absent brief is stored as `-` and that string
is truthy - the empty string this bug named is a state `critic record` has never written. The
write site is `critic.py`:230 and `critic.py`:1443 already normalises with `.strip(" -")`, so
there is a precedent to reuse rather than a new convention to invent.

So: normalise `-` and the empty string to ABSENT at read time, and let an absent fingerprint
match NOTHING. All nine currently-retired rejections then stand as unanswered, which is the
honest reading - none of the nine has a repair record, so none was ever actually answered.

Reviewer identity was considered as a way to preserve the five same-seat retirements and is
REJECTED, on the corpus rather than on taste. Measured over all nine pairs, 0 of 9 match on
exact reviewer string: every approval carries different free-text from its rejection
(`engineering seat (independent, isolated worktree)` against `engineering seat (independent,
isolated worktree, rejoinder over the EP0192 repairs)`). The rule would freeze all nine, exactly
like the blunt one. `_unanswered_rejects`'s own docstring already records that reviewer-string
keying SHIPPED AND WAS WITHDRAWN at 579/690, and `test_critic.py`:5427 carries a
`qa-seat-round-1` / `qa-seat-round-2` fixture as a standing counterexample.

What retires a rejection is a REPAIR, not a hash coincidence and not a name match. That rule is
BG0629's, and the two units carry one rule between them: this one decides what ABSENT means,
BG0629 decides what ANSWERS. Neither is complete without the other, and BG0629 lands first
because it is what makes any rejection clearable at all.

## Acceptance Criteria

- [x] **AC1** Given a REJECT and a later APPROVE from a DIFFERENT reviewer, both carrying the ledger's absent-brief placeholder `-`, when the standing verdict is read, then it is the REJECT. The absent value is `-`, not the empty string: that string is truthy, so the predicate this bug was filed with never fired and its own criteria would not have caught that
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::AbsentBriefTests::test_a_placeholder_brief_does_not_retire_a_cross_seat_reject
  - **Verified:** yes (2026-08-27)
- [x] **AC2** Given a REJECT and a later APPROVE from the SAME reviewer, both carrying `-`, when the standing verdict is read, then it is STILL the REJECT. Identity does not retire a rejection - a repair does, per BG0629 - and this row exists because the identity rule was proposed, measured against all nine real pairs, and falsified at 0 of 9 matching
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::AbsentBriefTests::test_a_placeholder_brief_does_not_retire_a_same_seat_reject_either
  - **Verified:** yes (2026-08-27)
- [x] **AC3** Given a REJECT and a later APPROVE carrying the SAME real fingerprint, when the standing verdict is read, then it is the APPROVE - the unchanged path, so normalising the absent case cannot be satisfied by breaking the matched one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::AbsentBriefTests::test_a_real_fingerprint_still_retires_after_normalisation
  - **Verified:** yes (2026-08-27)
- [x] **AC4** Given a fixture workspace whose `.config.yaml` carries `review.require_brief_provenance: false`, when `critic.py record` writes an unbriefed REJECT from one seat and an unbriefed APPROVE from another, then `critic.py show --format json` reports `verdict.verdict` as REJECT. The bug's own Steps run through `critic.py show`, and its text branch prints a raw dict, so the oracle is the json payload rather than a substring of it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::AbsentBriefTests::test_the_cli_stands_an_unbriefed_cross_seat_reject
  - **Verified:** yes (2026-08-27)
- [x] **AC5** Given THIS repository's verdict ledger, when the roll-up runs after the change, then all NINE placeholder-brief retirements stand as REJECT - US0570, US0571, US0575, US0576, US0569, US0572, US0574, BG0442 and BG0452 - because none of the nine carries a repair record, so none was answered. Seven of them are at Done, and the criterion states that consequence rather than discovering it at the close
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::AbsentBriefTests::test_every_placeholder_brief_retirement_in_the_corpus_stands
  - **Verified:** yes (2026-08-27)

## Impact

It is the whole of BG0607, re-armed by a config decision the project explicitly offers. A consuming project that stands `--brief` down gets the last-row-wins behaviour back with no sign that anything changed, and BG0607's own criteria would still pass because every row in THIS corpus has a brief.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/critic.py`, drop the read-time normalisation so `_unanswered_rejects` compares the raw cells again and two `-` placeholders match each other | Given a REJECT and a later APPROVE from a DIFFERENT reviewer, both carrying the ledger's absent-brief placeholder `-`, when the standing verdict is read, then it is the REJECT. The absent value is `-`, not the empty string: that string is truthy, so the predicate this bug was filed with never fired and its own criteria would not have caught that |
| AC2 | in `.claude/skills/sdlc-studio/scripts/critic.py`, add a reviewer-identity fallback for the absent case, so an approval retires a rejection when the reviewer cells are equal - the rule this repository shipped and withdrew at 579/690 | Given a REJECT and a later APPROVE from the SAME reviewer, both carrying `-`, when the standing verdict is read, then it is STILL the REJECT. Identity does not retire a rejection - a repair does, per BG0629 - and this row exists because the identity rule was proposed, measured against all nine real pairs, and falsified at 0 of 9 matching |
| AC3 | in `.claude/skills/sdlc-studio/scripts/critic.py`, remove the `any(...)` APPROVE match from `_unanswered_rejects` so nothing ever retires a rejection - the over-correction the absent-value fix makes tempting, and the one AC1 and AC2 cannot catch because both already expect a REJECT to stand | Given a REJECT and a later APPROVE carrying the SAME real fingerprint, when the standing verdict is read, then it is the APPROVE - the unchanged path, so normalising the absent case cannot be satisfied by breaking the matched one |
| AC4 | in `.claude/skills/sdlc-studio/scripts/critic.py`, change `cmd_show` to read `rows[-1]` directly instead of calling `verdict_for`, bypassing the roll-up the command exists to report | Given a fixture workspace whose `.config.yaml` carries `review.require_brief_provenance: false`, when `critic.py record` writes an unbriefed REJECT from one seat and an unbriefed APPROVE from another, then `critic.py show --format json` reports `verdict.verdict` as REJECT. The bug's own Steps run through `critic.py show`, and its text branch prints a raw dict, so the oracle is the json payload rather than a substring of it |
| AC5 | in `.claude/skills/sdlc-studio/scripts/critic.py`, normalise only the empty string and leave `-` truthy - the predicate this bug was FILED with, which moves no row in the corpus | Given THIS repository's verdict ledger, when the roll-up runs after the change, then all NINE placeholder-brief retirements stand as REJECT - US0570, US0571, US0575, US0576, US0569, US0572, US0574, BG0442 and BG0452 - because none of the nine carries a repair record, so none was answered. Seven of them are at Done, and the criterion states that consequence rather than discovering it at the close |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
