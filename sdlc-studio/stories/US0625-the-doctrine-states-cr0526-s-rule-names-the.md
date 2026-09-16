# US0625: the doctrine states CR0526's rule, names the one store a stop-ship ruling lives in, and who rules it

> **Status:** Done
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-doctrine.md, tools/tests/test_doctrine_stop_ship.py, .claude/skills/sdlc-studio/scripts/retro.py
> **Epic:** EP0206
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record deciding whether a finding stops a release
**I want** the doctrine to state CR0526's rule, the one table a stop-ship ruling is recorded in, and who rules it (D0194)
**So that** a release decision rests on a ruling somebody made against a named finding, rather than on a severity label read later

## Acceptance Criteria

Every criterion reads the **stop-ship passage**: the numbered rule under `## The rules` whose
heading carries the `{#stop-ship}` anchor, from that heading to the next numbered rule or `##`
heading - never the whole file. The doctrine already says `severity-rated bug` (rule 21) and
names the operator elsewhere, so a whole-file check is green before a word of this rule exists
(BG0457, the precedent `tools/tests/test_doctrine_review_scope.py`). A claim is probed inside ONE
sentence of the passage. Each test asserts green on the shipped doctrine AND, in the same test,
red on a gutted copy built in memory (its positive control).

### AC1: the doctrine states CR0526's rule, both outcomes

- **Given** the stop-ship passage of reference-doctrine.md
- **When** its three outcome claims are probed one by one
- **Then** one sentence says a finding ruled `not-stop-ship` is filed as its own bug or CR; one sentence says that finding's unit closes pointing at the filed id; one sentence says a finding ruled `stop-ship` holds the close, with `stop-ship` matched as a whole token so `not-stop-ship` never satisfies it; and the same test deletes the passage from a copy, re-homes its sentences in rule 21 and in a Revision History row, and asserts all three claims are then reported missing
- **Mutant:** delete the sentence filing a `not-stop-ship` finding as its own bug or CR - the rule survives only as practice, the state LL0027 names
- **Verify:** pytest tools/tests/test_doctrine_stop_ship.py::StopShipDoctrineTests::test_the_rule_names_both_outcomes
- **Verified:** yes (2026-09-15)

### AC2: severity alone is not the ruling

- **Given** the stop-ship passage
- **When** the severity claim is probed
- **Then** one sentence pairs `severity` with a negation and `ruling` (severity alone is not the ruling); and the same test builds a copy whose passage lacks that sentence while rule 21's `severity-rated bug` is left in place, and asserts the claim is reported missing
- **Mutant:** delete the severity sentence from the `{#stop-ship}` rule, leaving rule 21's `severity-rated bug` in the file
- **Verify:** pytest tools/tests/test_doctrine_stop_ship.py::StopShipDoctrineTests::test_severity_is_not_the_ruling
- **Verified:** yes (2026-09-15)

### AC3: the passage names one store and no second one (D0194)

- **Given** the stop-ship passage
- **When** its recording sentences and store terms are counted
- **Then** exactly one sentence matches the recording shape (`is|are|be` + `recorded|stored|kept|logged`, or `live in|lives in`) and that sentence names `retro.KNOWN_ISSUES_SECTION`'s value with the word `only`; no term of the repository's other record stores (`ledger`, `decisions.md`, `decision log`, `handoff`, `LATEST.md`, `charter`) appears anywhere in the passage; the proposal and delegate sentences of AC4 use neither shape, so they cannot clash; and the same test refuses a copy given a second recording sentence naming a place outside the vocabulary (by the count alone) and a copy given a sentence naming the critic ledger with no recording verb (by the vocabulary alone)
- **Mutant:** add a sentence to the passage recording a stop-ship ruling in the critic ledger as well - the ruling a reader follows is then one the close never reads
- **Verify:** pytest tools/tests/test_doctrine_stop_ship.py::StopShipDoctrineTests::test_the_one_store_is_named_and_no_second
- **Verified:** yes (2026-09-15)

### AC4: who rules, and a reviewer's proposal is not a ruling (D0194)

- **Given** the stop-ship passage
- **When** the ruler and proposal claims are probed one by one
- **Then** one sentence names the operator AND a recorded delegate together as who rules; a separate sentence says a reviewer's proposal in a finding's text is not a ruling (`propos` with `not a ruling`); and the same test asserts a copy with `or a recorded delegate` cut reports ONLY the delegate claim missing, and a copy with the passage re-homed in a Revision History row reports both missing
- **Mutant:** remove `or a recorded delegate` from the who-rules sentence, leaving the operator alone
- **Verify:** pytest tools/tests/test_doctrine_stop_ship.py::StopShipDoctrineTests::test_the_ruler_and_the_proposal_are_named
- **Verified:** yes (2026-09-15)

### AC5: the table and vocabulary the doctrine quotes are the ones the close reads

- **Given** `retro.KNOWN_ISSUES_SECTION` and `retro.KNOWN_ISSUE_RULINGS`, imported from retro.py at test time and never restated (LL0042)
- **When** the passage is compared with them
- **Then** the passage carries the section value as an exact backticked span; the set of code spans in the passage's vocabulary sentence - its one sentence with `one of` followed by code spans, so AC1's sentences quoting `stop-ship` cannot stand in for it - EQUALS `set(retro.KNOWN_ISSUE_RULINGS)` - equality, not subset, compared as whole tokens and never by substring; and the same test runs the comparison against the imported tuple plus one extra value AND against the tuple minus one value, and asserts a mismatch is reported for each - so a one-directional subset check cannot pass, then against the imported tuple and asserts none is
- **Mutant:** in retro.py, change the value of KNOWN_ISSUES_SECTION to `Known issues ruled`, leaving the name - caught by the span assertion, never by an AttributeError
- **Verify:** pytest tools/tests/test_doctrine_stop_ship.py::StopShipDoctrineTests::test_the_quoted_table_is_the_one_the_close_reads
- **Verified:** yes (2026-09-15)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in reference-doctrine.md, delete what happens to a finding the ruler lets through, so nothing is opened for it | the doctrine states CR0526's rule, both outcomes |
| AC1 | in reference-doctrine.md, remove the clause about the unit closing on the filed id, keeping the filing sentence | the doctrine states CR0526's rule, both outcomes |
| AC1 | in reference-doctrine.md, change which ruling blocks, naming `not-stop-ship` there instead | the doctrine states CR0526's rule, both outcomes |
| AC1 | in reference-doctrine.md, move the `{#stop-ship}` rule's sentences into rule 21 and drop its anchor | the doctrine states CR0526's rule, both outcomes |
| AC2 | in reference-doctrine.md, delete the severity sentence from the `{#stop-ship}` rule, leaving rule 21 intact | severity alone is not the ruling |
| AC2 | in reference-doctrine.md, invert the severity sentence so a High finding is stop-ship by default | severity alone is not the ruling |
| AC3 | in reference-doctrine.md, add a sentence recording a stop-ship ruling in the critic ledger as well | the passage names one store and no second one (D0194) |
| AC3 | in reference-doctrine.md, add that rulings are also kept on the verdicts page, a home outside the store list | the passage names one store and no second one (D0194) |
| AC3 | in reference-doctrine.md, weaken the store's `only` to `a`, making the retro table merely an option | the passage names one store and no second one (D0194) |
| AC4 | in reference-doctrine.md, remove `or a recorded delegate`, leaving the operator alone | who rules, and a reviewer's proposal is not a ruling (D0194) |
| AC4 | in reference-doctrine.md, delete the sentence denying a reviewer's proposal the force of a ruling | who rules, and a reviewer's proposal is not a ruling (D0194) |
| AC4 | in reference-doctrine.md, replace `the operator` with `the adversarial reviewer` as who decides | who rules, and a reviewer's proposal is not a ruling (D0194) |
| AC5 | in retro.py, change the value of KNOWN_ISSUES_SECTION to `Known issues ruled`, keeping the name | the table and vocabulary the doctrine quotes are the ones the close reads |
| AC5 | in retro.py, append `waived` to KNOWN_ISSUE_RULINGS | the table and vocabulary the doctrine quotes are the ones the close reads |
| AC5 | in reference-doctrine.md, delete `stop-ship` from the listed vocabulary, keeping `not-stop-ship` | the table and vocabulary the doctrine quotes are the ones the close reads |
| AC5 | in reference-doctrine.md, change the quoted section name to `Known issues` | the table and vocabulary the doctrine quotes are the ones the close reads |
| AC5 | in retro.py, remove `deferred` from KNOWN_ISSUE_RULINGS while the doctrine still offers it, which a one-directional subset check passes | the table and vocabulary the doctrine quotes are the ones the close reads |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sdlc-studio | Retitled: was 'the doctrine states the rule and the stop-ship judgement is recorded per finding at review time' |
| 2026-09-15 | sprint planning 2026-09-15 | Re-groomed at the sprint goal review (round 1: all three seats refused a goal carrying CR0526) against D0193 (an unfinished unit feeds the close's stop-ship step, not a third gate) and D0194 (one stop-ship store, the retro's carried table). Shrunk to the doctrine: the per-finding critic-ledger store it specified would have been a second store nothing reads. 3 -> 2 points. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan repair after QA r1 REJECT: every test now reads only the {#stop-ship} rule (BG0457 scope, test_doctrine_review_scope.py precedent) and carries its own gutted-copy control. Split into five criteria: AC1 filed / closes-pointing-at / holds, each probed in one sentence with stop-ship matched as a whole token; AC2 severity alone is not the ruling, with rule 21's severity-rated bug left in the gutted copy; AC3 one store by two independent assertions (exactly one recording sentence, naming the section with only; no other-store term in the passage), neither shape used by the proposal or delegate sentences; AC4 operator plus recorded delegate, and proposal is not a ruling; AC5 section span and vocabulary sentence compared by set equality against retro.py read at test time, with an extra-value control. retro.py joins Affects so its mutants (section value changed, a ruling appended) are production edits caught by assertion; this unit does not edit it. 16 mutant rows, one or more per clause. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Re-sized 2 -> 3 points after the plan repair grew it from 3 criteria to 5 and 16 mutant rows. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan round 2 repair: AC5's control compares against the tuple minus one value as well as plus one, and a row removes deferred from KNOWN_ISSUE_RULINGS while the doctrine still offers it - the case a one-directional subset check passes. |
