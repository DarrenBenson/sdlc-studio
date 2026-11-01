# Project Lessons

**Last Updated:** 2026-11-01

<!-- Append new entries at the top. Keep each entry under 10 lines. -->
<!-- Per-project tier (this repo only). Cross-project wisdom is promoted to the
     skill's lessons/ folder ONLY once it clearly generalises - see help/lessons.md. -->

## L-0450: Land units whose Affects do not overlap as one proven tree, so one host run covers several landings

- **Added:** 2026-10-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `.githooks/pre-push` header (`.githooks/pre-push:5-7`) runs the full suite once per push, so several non-overlapping landings share one host run; `sprint.py` `delivery_mode_offer` (`sprint.py:2318`) offers parallel only for file-disjoint groups. No gate forces landing as one tree.

Land units whose Affects do not overlap as one proven tree, so one host run covers several landings.

Recorded from retro RETRO0136.

## L-0449: Clear each carried unit's standing review rows at plan time, so the close never meets one

- **Added:** 2026-10-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `sprint.py` `seal_bar_unmet` (`sprint.py:5454`) and the standing-REJECT check meet carried rows only at the close, which is the cost the lesson names; `reference-sprint.md` 'The compulsory checklist' is the nearest guidance.

Clear each carried unit's standing review rows at plan time, so the close never meets one.

Recorded from retro RETRO0136.

## L-0448: Hold the batch at plan: new work joins the next run unless the operator rules an amendment, and the amendment is priced against…

- **Added:** 2026-10-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `reference-sprint.md` 'Cost regression at the close' prices a run against `COST-BASELINE.md` (`retro.py` `cost_baseline_rows`, `retro.py:2549`) after the fact; nothing refuses a mid-run batch amendment.

Hold the batch at plan: new work joins the next run unless the operator rules an amendment, and the amendment is priced against COST-BASELINE.md before it is accepted.

Recorded from retro RETRO0136.

## L-0447: Write a documentation unit's criteria against structured content a test can compare exactly, such as a table cell's set read from the…

- **Added:** 2026-10-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the mutant BEFORE writing the test' (`testing.md:92`) and its mechanism table row 'A whole-file assertion', which prefer exact structured comparison to a substring.

Write a documentation unit's criteria against structured content a test can compare exactly, such as a table cell's set read from the source, never as a negative claim about prose.

Recorded from retro RETRO0135.

## L-0446: Before every brief, mutate my own tests as the QA seat does, with paraphrases, swapped clauses and a negation elsewhere in the sentence…

- **Added:** 2026-10-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py` `check_self_check` (`critic.py:2915`) refuses a unit that declares a test file but records no mutant, and `critic.py brief` is refused without that record (`review.author_self_check: block`). It does not check that paraphrase or negation mutants were tried; no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the mutant BEFORE writing the test' (`testing.md:92`).

Before every brief, mutate my own tests as the QA seat does, with paraphrases, swapped clauses and a negation elsewhere in the sentence, and repair a finding by testing its class with wordings the reviewer did not give (CR0650).

Recorded from retro RETRO0135.

## L-0445: Date a fixture from today whenever the code under test reads the real clock, and pin the boundary day as BG1047's reviewer did

- **Added:** 2026-10-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `reference-test-best-practices.md` 'Good' example of controlling the clock instead of hard-coding a date (near line 641). A hard-coded date against the real clock still rots a fixture.

Date a fixture from today whenever the code under test reads the real clock, and pin the boundary day as BG1047's reviewer did.

Recorded from retro RETRO0134.

## L-0444: Before a review, put each changelog claim through the shipped entry point against its strongest negative, and name every mutant a message…

- **Added:** 2026-10-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py` `check_self_check` (`critic.py:2915`) requires a claim for the commit message and each changelog fragment the unit's Affects declares, and refuses a FALSE claim; `AGENTS.md` 'Exercise every claim through the shipped entry point'.

Before a review, put each changelog claim through the shipped entry point against its strongest negative, and name every mutant a message counts.

Recorded from retro RETRO0134.

## L-0443: Re-derive the review tier at every brief and record, and name an under-depth APPROVE the moment it exists (BG1052)

- **Added:** 2026-10-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py` `tier_for` (`critic.py:3082`) is called afresh at each brief (`critic.py:4066`) and rejoinder brief (`critic.py:4036`). Naming an under-depth APPROVE the moment it exists is NOT built: BG1052 is Open, so only `sprint.py` `seal_bar_unmet` (`sprint.py:5454`) finds it, at the close.

Re-derive the review tier at every brief and record, and name an under-depth APPROVE the moment it exists (BG1052).

Recorded from retro RETRO0134.

## L-0442: Run each user-facing sentence in a changelog fragment through the CLI before asking for review, as the paperwork reviews already do

- **Added:** 2026-10-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py` `check_self_check` (`critic.py:2915`) refuses a self-check with no claim for each changelog fragment the unit declares; that the sentences were run through the CLI is the author's claim, checked at review (`AGENTS.md` 'Exercise every claim').

Recorded from retro RETRO0133.

## L-0441: Probe a premise with an input whose result differs under each hypothesis, such as a key whose code fallback differs from its shipped…

- **Added:** 2026-10-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the ENTRY POINT before writing the test' (`testing.md:66`); choosing an input that splits the hypotheses is judgement.

Probe a premise with an input whose result differs under each hypothesis, such as a key whose code fallback differs from its shipped default.

Recorded from retro RETRO0133.

## L-0440: A builder that adds a widened env scrub to satisfy a guard test should reuse the pinned list it already has: US0971's `GIT_*` scrub broke…

- **Added:** 2026-10-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` `_REPO_LOCATING_GIT_VARS` (`verify_ac.py:3951`) is still the pinned list, used by `_git_env` (`verify_ac.py:3958`); `tools/tests/test_skill_tests_env.py` holds the copies equal. A second, narrower scrub would still drift from it.

A builder that adds a widened env scrub to satisfy a guard test should reuse the pinned list it already has: US0971's `GIT_*` scrub broke fixture isolation until it imported `verify_ac._REPO_LOCATING_GIT_VARS`.

Recorded from retro RETRO0129.

## L-0439: Settle every permission rule and eval harness at plan time, and run the evals each sprint for any guidance that changed

- **Added:** 2026-09-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `tools/eval_run.py` docstring: the eval gate runs at the release gate, rc checklist and epic close, not per sprint, and no `sprint plan` row settles permission rules.

Recorded from retro RETRO0126.

## L-0438: Give the review cap a recorded per-unit exception (BG0841), so an operator-granted round lands without a forced transition

- **Added:** 2026-09-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py` `round_refusal` (`critic.py:1777`) allows a delivery round past `review.max_rounds` when an accepted ruling authorises it (`authorised`, `critic.py:1797`; the recorded round at `critic.py:931`), with no forced transition.

Recorded from retro RETRO0126.

## L-0437: Ship the loop as one command with automatic token capture (CR0602), so a run needs no orchestrator scripts and its report measures tokens

- **Added:** 2026-09-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py` is the one lifecycle command (`autosprint.py` is a deprecated alias, `autosprint.py:2-5`), and the report measures tokens from the transcript (`reference-sprint.md` Appetite: 'transcript-measured').

Recorded from retro RETRO0126.

## L-0436: Open a unit when its lane starts, not at plan time, so per-unit time and tokens measure the work

- **Added:** 2026-09-23
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py` lane brief opens the unit span beside `record_lane_start` (`sprint.py:8926-8940`; `lib/run_state.py` `record_lane_start`, `run_state.py:1804`), not at plan time.

Recorded from retro RETRO0121.

## L-0435: Hand lane agents their shared contracts as code stubs, not prose: the one integration break and the orchestrator's token-sum error both…

- **Added:** 2026-09-23
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `reference-sprint.md` Delivery mode hands lanes disjoint `Affects` (`sprint.py` `_full_partition`, `sprint.py:2291`), but nothing requires shared contracts as code stubs.

Hand lane agents their shared contracts as code stubs, not prose: the one integration break and the orchestrator's token-sum error both came from prose contracts.

Recorded from retro RETRO0121.

## L-0434: Sprint 2 deletes the gate lanes that cost the most and caught nothing here: the spec-claims timing claim, evidence-drift with the mutation…

- **Added:** 2026-09-23
- **Review-by:** 2026-12-22

Sprint 2 deletes the gate lanes that cost the most and caught nothing here: the spec-claims timing claim, evidence-drift with the mutation ledger, and module-alone at push (560 of 668 seconds).

Recorded from retro RETRO0121.

- **Status:** Closed - the plan was delivered: the spec-claims and evidence-drift lanes were deleted (US0920 commit a71a9577, `scripts/tests/test_lean_no_mutation_gates.py` docstring; CHANGELOG 'A commit runs only the checks that have caught real defects' lists `spec-claims`), and `module-alone` runs at the release boundary only (`.githooks/pre-push:7`), not at push. The statement no longer describes the tree.

## L-0433: **A test moved to accommodate a defect is worse than the defect.** It converts a caught error into a permanent blind spot, and only an

- **Added:** 2026-09-22
- **Review-by:** 2026-12-21

**A test moved to accommodate a defect is worse than the defect.** It converts a caught error into a permanent blind spot, and only an independent reader will find it.

Recorded from retro RETRO0120.

- **Status:** Closed - duplicate of L-0425 (body identical, confirmed by script); L-0425 stays open and carries the judgement.

## L-0432: **When a corpus-coupled ceiling breaches, fix what it measures, not the number.** The census ceiling broke because this run filed seven

- **Added:** 2026-09-22
- **Review-by:** 2026-12-21

**When a corpus-coupled ceiling breaches, fix what it measures, not the number.** The census ceiling broke because this run filed seven findings; it is now a ratio that falls as findings are groomed, and it still kills the over-reach mutant it names.

Recorded from retro RETRO0120.

- **Status:** Closed - duplicate of L-0424 (body identical, confirmed by script); L-0424 stays open and carries the judgement.

## L-0431: **Assert that a mutation applied before trusting its verdict.** A mutant that silently fails to apply reports as killed and is evidence of

- **Added:** 2026-09-22
- **Review-by:** 2026-12-21

**Assert that a mutation applied before trusting its verdict.** A mutant that silently fails to apply reports as killed and is evidence of nothing. Two of this run's reported kills were that.

Recorded from retro RETRO0120.

- **Status:** Closed - duplicate of L-0423 (body identical, confirmed by script); L-0423 stays open and carries the judgement.

## L-0430: **A derivation is not delivered until something consumes it.** Three units in this run shipped a correct derivation that no caller, no

- **Added:** 2026-09-22
- **Review-by:** 2026-12-21

**A derivation is not delivered until something consumes it.** Three units in this run shipped a correct derivation that no caller, no template, or no template branch reached. Ask what READS this before calling a unit done, and pin that reader, not the function.

Recorded from retro RETRO0120.

- **Status:** Closed - duplicate of L-0422 (body identical, confirmed by script); L-0422 stays open and carries the judgement.

## L-0429: **A test moved to accommodate a defect is worse than the defect.** It converts a caught error into a permanent blind spot, and only an

- **Added:** 2026-09-22
- **Review-by:** 2026-12-21

**A test moved to accommodate a defect is worse than the defect.** It converts a caught error into a permanent blind spot, and only an independent reader will find it.

Recorded from retro RETRO0120.

- **Status:** Closed - duplicate of L-0425 (body identical, confirmed by script); L-0425 stays open and carries the judgement.

## L-0428: **When a corpus-coupled ceiling breaches, fix what it measures, not the number.** The census ceiling broke because this run filed seven

- **Added:** 2026-09-22
- **Review-by:** 2026-12-21

**When a corpus-coupled ceiling breaches, fix what it measures, not the number.** The census ceiling broke because this run filed seven findings; it is now a ratio that falls as findings are groomed, and it still kills the over-reach mutant it names.

Recorded from retro RETRO0120.

- **Status:** Closed - duplicate of L-0424 (body identical, confirmed by script); L-0424 stays open and carries the judgement.

## L-0427: **Assert that a mutation applied before trusting its verdict.** A mutant that silently fails to apply reports as killed and is evidence of

- **Added:** 2026-09-22
- **Review-by:** 2026-12-21

**Assert that a mutation applied before trusting its verdict.** A mutant that silently fails to apply reports as killed and is evidence of nothing. Two of this run's reported kills were that.

Recorded from retro RETRO0120.

- **Status:** Closed - duplicate of L-0423 (body identical, confirmed by script); L-0423 stays open and carries the judgement.

## L-0426: **A derivation is not delivered until something consumes it.** Three units in this run shipped a correct derivation that no caller, no

- **Added:** 2026-09-22
- **Review-by:** 2026-12-21

**A derivation is not delivered until something consumes it.** Three units in this run shipped a correct derivation that no caller, no template, or no template branch reached. Ask what READS this before calling a unit done, and pin that reader, not the function.

Recorded from retro RETRO0120.

- **Status:** Closed - duplicate of L-0422 (body identical, confirmed by script); L-0422 stays open and carries the judgement.

## L-0425: **A test moved to accommodate a defect is worse than the defect.** It converts a caught error into a permanent blind spot, and only an

- **Added:** 2026-09-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: independence is the control: `AGENTS.md` 'Review is independent of the author' and `critic.py brief`; `verify_ac.py` `revert_check` (`verify_ac.py:4088`) also catches a test that stays green with the production change reverted. No gate refuses a moved test as such.

**A test moved to accommodate a defect is worse than the defect.** It converts a caught error into a permanent blind spot, and only an independent reader will find it.

Recorded from retro RETRO0120.

## L-0424: **When a corpus-coupled ceiling breaches, fix what it measures, not the number.** The census ceiling broke because this run filed seven

- **Added:** 2026-09-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the principle stands: `backlog_triage.py` `_unruled_findings` (`backlog_triage.py:266`) records the sibling failure, a ceiling that fired on every commit gets switched off; the named census ceiling was repaired in commit 3c493a1e. no gate holds it; nearest guidance for the general rule.

**When a corpus-coupled ceiling breaches, fix what it measures, not the number.** The census ceiling broke because this run filed seven findings; it is now a ratio that falls as findings are groomed, and it still kills the over-reach mutant it names.

Recorded from retro RETRO0120.

## L-0423: **Assert that a mutation applied before trusting its verdict.** A mutant that silently fails to apply reports as killed and is evidence of

- **Added:** 2026-09-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `mutation.py` `applied` (`mutation.py:849`) refuses a mutation that does not change the file ('refusing to run a no-op mutant', `mutation.py:867`), so a silent no-op cannot report killed.

**Assert that a mutation applied before trusting its verdict.** A mutant that silently fails to apply reports as killed and is evidence of nothing. Two of this run's reported kills were that.

Recorded from retro RETRO0120.

## L-0422: **A derivation is not delivered until something consumes it.** Three units in this run shipped a correct derivation that no caller, no

- **Added:** 2026-09-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` mechanism table row 'Testing the helper, not the caller' and the 'name its writer' rule (`testing.md:92` section); `verify_ac.py` `lane_check` (`verify_ac.py:1331`) reports verifiers that never enter the shipped entry point.

**A derivation is not delivered until something consumes it.** Three units in this run shipped a correct derivation that no caller, no template, or no template branch reached. Ask what READS this before calling a unit done, and pin that reader, not the function.

Recorded from retro RETRO0120.

## L-0421: A guard built to stop a state rebuilding must be run against the state that actually accumulated, the same day, before the run claims its

- **Added:** 2026-09-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `AGENTS.md` 'Exercise every claim through the shipped entry point'; no lane runs a new guard over the accumulated corpus.

A guard built to stop a state rebuilding must be run against the state that actually accumulated, the same day, before the run claims its goal.

Recorded from retro RETRO0119.

## L-0420: A backlog count is a claim about state, and `In Progress` is the weakest link in it: in one cluster of eleven, not a single commit naming

- **Added:** 2026-09-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `backlog_triage.py` `_abandoned_findings` (`backlog_triage.py:297`, In Progress requests whose children nothing touched) and `_unruled_findings` (`backlog_triage.py:266`) exist because status alone misleads; reading the commits is still manual, no gate holds it; nearest guidance.

A backlog count is a claim about state, and `In Progress` is the weakest link in it: in one cluster of eleven, not a single commit naming any request was a `feat` or a `fix`. Read the commits, not the status.

Recorded from retro RETRO0119.

## L-0419: Splitting one command into two halves is a claim about what each half WRITES

- **Added:** 2026-09-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint sign` is a separate verb from the close (`AGENTS.md` gate table) and `sprint_report.py` excludes the facts signing writes from the fingerprint (`sprint_report.py:2790`). Stating a split as what each half WRITES is guidance only.

Splitting one command into two halves is a claim about what each half WRITES. Stating it that way made every criterion falsifiable by a production change; stating it as "close prepares and sign seals" would have been unfalsifiable prose, and the gate that catches the difference is the mutant, not the review.

Recorded from retro RETRO0118.

## L-0418: A content-keyed evidence ledger has an ordering rule, not a preference: register a unit's mutants AFTER the last edit to their target

- **Added:** 2026-09-18
- **Review-by:** 2026-12-17

A content-keyed evidence ledger has an ordering rule, not a preference: register a unit's mutants AFTER the last edit to their target. A stale row survives another unit's registration but is DROPPED by its own unit's next one, so a partial re-registration silently destroys the evidence it was meant to complete.

Recorded from retro RETRO0118.

- **Status:** Closed - the content-keyed mutation evidence ledger is retired: `mutation.py` module docstring (`mutation.py:31`) retires `register`, `retract`, `retractions` and `audit` (the per-target ledger nothing reads) and `RETIRED` refusals at `mutation.py:2144`. No rows exist to be dropped by a later registration.

## L-0417: A test that searches a whole page passes on somebody else's output

- **Added:** 2026-09-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` mechanism table row 'A whole-file assertion' (`testing.md:92` section).

A test that searches a whole page passes on somebody else's output. US0834 AC1's mutant survived because the assertion looked for a unit id anywhere in stdout, and the close pre-flight prints the same ids for its own reasons. Assert against the line the code under test wrote, not the transcript it wrote it into.

Recorded from retro RETRO0118.

## L-0416: A page cannot be signed over facts the signature itself writes

- **Added:** 2026-09-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint_report.py` excludes facts the signature writes from the fingerprint (`sprint_report.py:2790`) and counts delivered by the terminal gate PREPARE recorded (`sprint_report.py:3515`); `sprint sign` refuses a page that no longer re-derives (`AGENTS.md` gate table).

A page cannot be signed over facts the signature itself writes. Three figures in this report's digest - each unit's Status, the run's end time and a delivered count taken from statuses - are set BY sealing, so every signed report re-derived to a different fingerprint and read INVALIDATED from the moment it was signed. The digest has to cover what is true when the page is derived: here, that each unit CLEARED ITS TERMINAL GATE. Found by running `sign` then `check` on a throwaway fixture, with 33 criteria and 2,036 tests green.

Recorded from retro RETRO0118.

## L-0415: A harness stub lands on the module object it names, which is not always the one the code under test reads from

- **Added:** 2026-09-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` heuristic 1 'Production-state-shape integration tests' (`testing.md:10`); `scripts/tests/test_autosprint.py:177` still patches through `cmd_close.__globals__`, the repair the lesson names.

A harness stub lands on the module object it names, which is not always the one the code under test reads from. `test_autosprint`'s stub patched `sys.modules["sprint"]`; a sibling suite loads sprint.py through `spec_from_file_location` and REPLACES that entry, so once both ran the stub landed where nothing looked for it. Invisible module-alone and invisible in isolation - it appears only in discovery order. Patch the function's own `__globals__`.

Recorded from retro RETRO0118.

## L-0414: A verifier that stands in for a lane protects nothing, and the test that does protect it must be BOUND to a criterion

- **Added:** 2026-09-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` `lane_check` (`verify_ac.py:1331`) reports a unit whose verifiers never enter the shipped entry point, and `best-practices/testing.md` 'Name the ENTRY POINT before writing the test' (`testing.md:66`). The `stamps-staged` guard named in the lesson no longer exists; binding the lane test to a criterion is manual.

A verifier that stands in for a lane protects nothing, and the test that does protect it must be BOUND to a criterion. US0844 AC1's When named PREPARE building the report; its verifier called the library function directly. The lane test was written, observed to fail when the call was removed, and then attached to no criterion - so `verify_ac` never ran it for that criterion and the `stamps-staged` guard would not have refused its deletion. Writing the right test is half the job; binding it is the other half.

Recorded from retro RETRO0118.

## L-0413: Verify the field exists before you report the state it implies

- **Tags:** reporting, verification, run-state, false-state
- **Added:** 2026-09-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `lib/run_state.py` `FIELDS` (`run_state.py:94`) has no `closed_at`, so the trap stands; the reader that refuses an unknown key (CR0588) was Rejected, so no gate holds it; nearest guidance: `best-practices/testing.md` 'name its writer' rule (`testing.md:92` section).

At the RUN-01M2JA6J close I read closed_at from the run state, saw None, and told the operator four times that the run had not sealed. run_state.FIELDS has no closed_at: the closed signal is outcome in run_state.CLOSED plus ended_at, both of which had been set since 12:51Z. The run had been closed for over an hour. Three further close attempts were spent on a condition that was already true, one of them burning the loop guard last round, which produced a cap refusal I then took to the operator as a decision to rule. The record was right the whole time; the reader was wrong, and a dict get cannot tell an absent field from a field the schema never had.

The rule: before reporting a STATE from a data structure, confirm the field is one the structure defines - read the schema, the FIELDS tuple, the writer - not just its value. A None that means nothing at all looks exactly like a None that means not yet. This is the same class as a criterion whose words outrun its fixture: the query looked like it asked the question and did not. Filed as CR0588 for the tooling half, a reader that refuses an unknown key.

## L-0412: **Evidence hashed against whole-file bytes is voided by a neighbour's edit, not just your own.** Mutant rows and coverage rulings on

- **Added:** 2026-09-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the coverage half: `verify_ac.py` `live_rulings` (`verify_ac.py:2640`) keys a coverage ruling on the whole-file hash, so a neighbour unit's edit to a shared file still makes it stale. The mutant-row half is gone: `mutation.py` module docstring (`mutation.py:31`) retires `register`, `retract`, `retractions` and `audit` (the per-target ledger nothing reads) and `RETIRED` refusals at `mutation.py:2144`.

**Evidence hashed against whole-file bytes is voided by a neighbour's edit, not just your own.** Mutant rows and coverage rulings on critic.py and sprint.py were voided by other units' commits four times this run (LL0053's shape, now crossing units). Register and rule after the last edit ANY unit makes to a shared file, and re-run every unit's done-gate dry-run after the final code commit.

Recorded from retro RETRO0117.

## L-0411: **An uncapped review loop converges on wording, not defects.** Plan review ran to five rounds on one unit and drew 47 REJECTs

- **Added:** 2026-09-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py` `DEFAULT_REVIEW_CEILING = 2` (`critic.py:1761`, read via `review.max_rounds` by `round_refusal`, `critic.py:1777`) caps rounds, and `REJECT_EXITS` (`critic.py:1828`) forces a carry at the cap.

**An uncapped review loop converges on wording, not defects.** Plan review ran to five rounds on one unit and drew 47 REJECTs. Delivery review, capped at two rounds (D0146), drew four REJECTs, and all four were real regressions. A cap plus a complete written repair is cheaper than a sixth round (D0204).

Recorded from retro RETRO0117.

## L-0410: **Seats judge the build against the author's criteria; only a stakeholder judges the criteria against the need.** Seventy plan-review

- **Added:** 2026-09-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `reference-consult.md` (stakeholder consult before freezing the design); nothing refuses a plan whose criteria no stakeholder has read.

**Seats judge the build against the author's criteria; only a stakeholder judges the criteria against the need.** Seventy plan-review verdicts approved a stop-ship rule that the session doing the work could release itself. One stakeholder consult found it in a single pass (CR0571). If the criteria encode the wrong intent, every seat approves a well-built wrong thing. Consult before freezing the design (RFC0058).

Recorded from retro RETRO0117.

## L-0409: **Attribution by blame turns one commit into a shared charge.** The coverage gate charged all 455 of US0626's added sprint.py lines to

- **Added:** 2026-09-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` `_unit_added_lines` (`verify_ac.py:2415`) still blames added lines to the unit's commits with `git blame`, so a shared omnibus commit still shares the charge; BG0706 is Won't Fix, so no gate holds it; nearest guidance: commit per unit, per `AGENTS.md` pre-commit lanes.

**Attribution by blame turns one commit into a shared charge.** The coverage gate charged all 455 of US0626's added sprint.py lines to BG0674, because both units declare the file and one omnibus commit carried both. Split into per-group commits, the charge fell to BG0674's own lines. Commit per unit, or per group whose Affects files are disjoint, before any gate that attributes lines by `git blame` and the `Refs:` trailer runs. Filed as BG0706.

Recorded from retro RETRO0117.

## L-0408: **Two readers of one rule will disagree, and the one that blocks is the one nobody tested.** `row_staleness` shipped with no production

- **Added:** 2026-09-10
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the named `row_staleness` is gone with the mutation ledger (`mutation.py` module docstring (`mutation.py:31`) retires `register`, `retract`, `retractions` and `audit` (the per-target ledger nothing reads) and `RETIRED` refusals at `mutation.py:2144`), but the rule holds: `critic.py` `_unanswered_rejects` (`critic.py:831`) is now the one reader that `standing_rejects` (`critic.py:873`) shares. no gate holds it; nearest guidance: 'name its writer' (`testing.md:92` section).

**Two readers of one rule will disagree, and the one that blocks is the one nobody tested.** `row_staleness` shipped with no production caller while the lane re-implemented it inline and the terminal gate used the old rule. Wire the new rule into the reader that refuses, or the cost you removed is still being paid.

Recorded from retro RETRO0116.

## L-0407: **A guard's reach is the spelling its fixture used.** BG0660's scan could not see this repository's own `subprocess.run([sys.executable

- **Added:** 2026-09-10
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` heuristic 1 'Production-state-shape integration tests' (`testing.md:10`) and mechanism table row 'A fixture shape the product cannot produce'.

**A guard's reach is the spelling its fixture used.** BG0660's scan could not see this repository's own `subprocess.run([sys.executable, str(scripts / "gate.py"), ...])`; widening it to read joined strings for every callee then produced four false positives from fixture text. Probe a new detector against every shape the corpus actually contains, in both directions, before believing it.

Recorded from retro RETRO0116.

## L-0406: **A mutant aimed at the wrong site is not weak evidence, it is none.** Three retractions this run

- **Added:** 2026-09-10
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py` `check_self_check` (`critic.py:2915`) requires each mutant to name a test in a declared test file with a killed or survived result and an answer for a survivor; whether the edit is the criterion's site is the QA seat's judgement (`critic.py brief --seat qa`). no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the mutant BEFORE writing the test' (`testing.md:92`).

**A mutant aimed at the wrong site is not weak evidence, it is none.** Three retractions this run. Before recording a verdict, confirm the edit is the one the criterion is about and that the node dies on the criterion's own assertion rather than on an import error, a TypeError or a sibling's clause.

Recorded from retro RETRO0116.

## L-0405: **A criterion's words are law and its fixture is the measurement; when they differ, the fixture wins silently.** Nine of this run's

- **Added:** 2026-09-10
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` `lane_check` (`verify_ac.py:1331`) and `best-practices/testing.md` 'Name the ENTRY POINT before writing the test' (`testing.md:66`) check part of this (door versus claim); `critic.py brief` carries the canonical criteria as law (`AGENTS.md`). The fixture-versus-words check is the reviewer's.

**A criterion's words are law and its fixture is the measurement; when they differ, the fixture wins silently.** Nine of this run's blocking findings were that shape - AC5 naming three grep cases and testing none of them, AC8 saying "judged by RUNNING" while reading source, AC7 requiring a round trip and asserting a substring, AC4's control built on a class the code never emits. The check is cheap: read the criterion, then ask what the test would still pass with removed.

Recorded from retro RETRO0116.

## L-0404: **Re-measure by target, not by unit.** Before porting a patch, list every delivered unit with live rows on each file it touches and chain

- **Added:** 2026-09-08
- **Review-by:** 2026-12-07

**Re-measure by target, not by unit.** Before porting a patch, list every delivered unit with live rows on each file it touches and chain their runners after it. `AGENTS.md` alone carries rows for four units.

Recorded from retro RETRO0115.

- **Status:** Closed - the mechanism is retired: it chains runners for 'live rows' of delivered units on each file, but the per-target ledger is gone (`mutation.py` module docstring (`mutation.py:31`) retires `register`, `retract`, `retractions` and `audit` (the per-target ledger nothing reads) and `RETIRED` refusals at `mutation.py:2144`), so no unit has live rows to re-measure.

## L-0403: **A tool failing between two calls is not an absence of findings.** Coverage's own `combine` and `json` verbs failing read as no data and

- **Added:** 2026-09-08
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` coverage path runs `coverage combine` with `must_succeed=True` (`verify_ac.py:2547`; comment at `verify_ac.py:2528`), so an instrument failure refuses by name rather than reading as no data.

**A tool failing between two calls is not an absence of findings.** Coverage's own `combine` and `json` verbs failing read as no data and therefore as zero added statements at exit 0 - the gate satisfied by the instrument breaking. Every such path now refuses by name.

Recorded from retro RETRO0115.

## L-0402: **A message that claims to be runnable must be RUN by its test.** The refusal US0818 ships printed a `retract` command that a shell

- **Added:** 2026-09-08
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the `retract` command named is retired (`mutation.py:2144`) but the rule holds; no gate holds it; nearest guidance: `best-practices/testing.md` heuristic 6 'A message and its verdict are driven by one test' (`testing.md:55`).

**A message that claims to be runnable must be RUN by its test.** The refusal US0818 ships printed a `retract` command that a shell mangles, because 67 of the ledger's 430 live rows carry a backtick and a pasted argument is command substitution. The test now splits the printed line with `shlex` and executes it.

Recorded from retro RETRO0115.

## L-0401: **A criterion that says "X, or Y" needs a fixture for both.** Six of the eight rejections were one clause of a criterion with no case

- **Added:** 2026-09-08
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the mutant BEFORE writing the test' (`testing.md:92`) and its stated limit that a plan-time mutant table cannot name a branch that does not exist yet.

**A criterion that says "X, or Y" needs a fixture for both.** Six of the eight rejections were one clause of a criterion with no case reaching it: an uncommitted edit to a TRACKED file where the fixture used an untracked one, a stale data file the fixture wrote as prose that `coverage combine` cannot read, a ledger that cannot be parsed, a missing target beside a stale one. The mutant table written at plan time cannot name a branch that does not exist yet.

Recorded from retro RETRO0115.

## L-0400: When the build departs from the plan-reviewed design, amend the criterion before the brief renders, or the seat judges the code against a

- **Added:** 2026-09-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `AGENTS.md` ('the canonical acceptance criteria as law', `critic.py brief`); nothing detects a build that departs from its criteria before the brief.

When the build departs from the plan-reviewed design, amend the criterion before the brief renders, or the seat judges the code against a law it no longer meets.

Recorded from retro RETRO0114.

## L-0399: A structural pin beats a string: the worker count printed from the pool survived; the sleepers' own overlap did not

- **Added:** 2026-09-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` mechanism table row 'Asserting text the code supplies for free' (`testing.md:92` section).

Recorded from retro RETRO0114.

## L-0398: Mutants come from the delivered code's branches, not only from the plan table: every survivor a seat found sat on a branch the unit's own

- **Added:** 2026-09-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py` `check_self_check` (`critic.py:2915`) asks mutants against a declared test file but does not require them to come from delivered branches; no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the mutant BEFORE writing the test' (`testing.md:92`); `mutation.py` `enumerate_mutations` (`mutation.py:135`) derives mutants from the code.

Mutants come from the delivered code's branches, not only from the plan table: every survivor a seat found sat on a branch the unit's own selectors never executed.

Recorded from retro RETRO0114.

## L-0397: A number in prose needs the command that produced it beside it; a figure copied from a budget constant or an old bug report shipped twice

- **Added:** 2026-09-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the `spec-claims` lane that checked such figures was deleted (CHANGELOG 'A commit runs only the checks that have caught real defects'), so no gate holds it; nearest guidance: `AGENTS.md` 'Exercise every claim' and the claims `critic.py` `check_self_check` (`critic.py:2915`) requires.

A number in prose needs the command that produced it beside it; a figure copied from a budget constant or an old bug report shipped twice and was refuted by measurement both times.

Recorded from retro RETRO0114.

## L-0396: Fixture-green is not real-target-green: a gate lane, a hook or a command must be run where the hook runs it, on this repository, before a

- **Added:** 2026-09-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `.githooks/pre-push` runs `gate.py --boundary push` on the real repository (`.githooks/pre-push:5-7`), where path differences show; no gate holds it; nearest guidance before review: `AGENTS.md` 'Exercise every claim through the shipped entry point'.

Fixture-green is not real-target-green: a gate lane, a hook or a command must be run where the hook runs it, on this repository, before a brief is rendered; the environment differences (a relative versus absolute PYTHONPATH) live only there.

Recorded from retro RETRO0114.

## L-0395: The disclosure page is derived from statuses: regenerate it once, after the last transition, or every commit in between is refused by its

- **Added:** 2026-09-06
- **Review-by:** 2026-12-05

The disclosure page is derived from statuses: regenerate it once, after the last transition, or every commit in between is refused by its own paperwork.

Recorded from retro RETRO0113.

- **Status:** Closed - no longer true: the page is `docs/known-issues.md`, derived by `tools/known_issues.py` and checked at the tag only (its docstring: 'between releases... filing or closing a finding moves neither'; `.githooks/pre-push:71-83`), so commits between transitions are not refused by it.

## L-0394: A test fixture that inherits the caller's environment is a defect even when green: an unscrubbed enable-hooks fixture wrote

- **Added:** 2026-09-06
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` `_git_env` (`verify_ac.py:3958`) drops inherited repo-locating variables and `tools/tests/test_skill_tests_env.py` holds the scrub lists equal; a new fixture that skips them is not caught by a gate.

A test fixture that inherits the caller's environment is a defect even when green: an unscrubbed enable-hooks fixture wrote `core.hooksPath` into a decoy repository, and an unscrubbed PATH reached the live forge (BG0641 qa r1, BG0642 qa/engineering r1).

Recorded from retro RETRO0113.

## L-0393: Register mutation evidence after the LAST edit to a target, and re-check every earlier unit whose target a later unit touches: BG0641's

- **Added:** 2026-09-06
- **Review-by:** 2026-12-05

Register mutation evidence after the LAST edit to a target, and re-check every earlier unit whose target a later unit touches: BG0641's thirty rows were dropped by BG0642's edit to the same hook, and BG0643's two by BG0603's edit to verify_ac.py, both found only at the close dry-run.

Recorded from retro RETRO0113.

- **Status:** Closed - the registered-mutants ledger that dropped rows on another unit's edit is retired: `mutation.py` module docstring (`mutation.py:31`) retires `register`, `retract`, `retractions` and `audit` (the per-target ledger nothing reads) and `RETIRED` refusals at `mutation.py:2144`.

## L-0392: A depth field carries two counts, the total after the word and the entry-point denominator before it; a census that takes the first `<n>

- **Added:** 2026-09-06
- **Review-by:** 2026-12-05

A depth field carries two counts, the total after the word and the entry-point denominator before it; a census that takes the first `<n> criteria` reads the wrong one, and the first artefact with a manual criterion exposes it (BG0650).

Recorded from retro RETRO0113.

- **Status:** Closed - the derived `Verification depth` field is retired: `verify_ac.py` `RETIRED_VERBS` (`verify_ac.py:4325`) refuses `depth` and `depth-check` ('no `Verification depth` is derived any more'), so no census reads its counts.

## L-0391: A hook's stdout never reaches the pusher: git shows a pre-push hook's stderr only, so a refusal that says "see the lane named above" must

- **Added:** 2026-09-06
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `.githooks/pre-push` prints every refusal to stderr (`>&2`, `.githooks/pre-push:55-83`), the stream git shows the pusher.

A hook's stdout never reaches the pusher: git shows a pre-push hook's stderr only, so a refusal that says "see the lane named above" must put the lane on stderr, and a fixture that merges the streams cannot tell (BG0641 engineering r1, proved under a real `git push`).

Recorded from retro RETRO0113.

## L-0390: **The vacuous case is where a per-item rule fails, and it is the largest population.** "Every criterion carries a verifier" is TRUE over an

- **Added:** 2026-09-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `transition.py` `_pre_write_gates` (`transition.py:948`) refuses a terminal target with no acceptance criteria, `verify_ac.py` reports a file that parses to none (`verify_ac.py:2923-2936`), and `file_finding.py` `report_unverifiable_criteria` (`file_finding.py:1438`) scopes its rule to authored criteria. The quantifier-over-empty rule itself has no gate.

**The vacuous case is where a per-item rule fails, and it is the largest population.** "Every criterion carries a verifier" is TRUE over an empty list, and 61 bug files parse to no criteria at all - more than the 51 the rule was written for. Any rule quantified over a collection needs an explicit answer for the empty collection, or its biggest sub-population passes without ever being wrong.

Recorded from retro RETRO0112.

## L-0389: **A schema-widening test built on the shape YOUR repo holds cannot see the shape everyone else holds.** Two ledger columns were appended at

- **Added:** 2026-09-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` heuristic 3 'Contract changes ship a rejects-old-shape test' (`testing.md:30`) and `best-practices/testing.md` heuristic 1 'Production-state-shape integration tests' (`testing.md:10`). The ledger it concerned is retired; `critic.py` still reads 6-or-5-cell verdict rows (supersession comment above `SUPERSEDE_HEADING`).

**A schema-widening test built on the shape YOUR repo holds cannot see the shape everyone else holds.** Two ledger columns were appended at once, and the reader tolerated a row short by exactly one - so every pre-column ledger stopped parsing and a gate began refusing units whose evidence was on record. This repository had migrated its own header, so its tests were all written on the migrated shape and every one of them passed. The failure is invisible from inside the repo that did the migration, and it lands on every consumer at upgrade. Fixture the OLDEST supported shape, not the current one.

Recorded from retro RETRO0112.

## L-0388: **A tool that cannot author its evidence produces units nobody can check.** `file_finding.py` could write an acceptance criterion but not

- **Added:** 2026-09-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `file_finding.py` `report_unverifiable_criteria` (`file_finding.py:1438`) reports an authored criterion with no verifier and `--verify` pairs with `--ac` (`file_finding.py:2488-2489`).

**A tool that cannot author its evidence produces units nobody can check.** `file_finding.py` could write an acceptance criterion but not its verifier, and nothing downstream noticed: grooming asked whether a criterion was WRITTEN, never whether it could be CHECKED, so 51 bug files reached a terminal status on criteria that were never tests. A gate that inspects the shape of work rather than its checkability certifies the wrong thing.

Recorded from retro RETRO0112.

## L-0387: **Narrow the licence, not the pattern.** A lint error in three code spans was fixed by a regex over every code span in two directories

- **Added:** 2026-09-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `artifact.py` overwrites only an unambiguous level-one heading (`_H1_LINE_RE`, `artifact.py:1987`; `_first_h1_line`, `artifact.py:2010`): the narrowed licence is the shipped design. The general rule (enumerate instances) has no gate.

**Narrow the licence, not the pattern.** A lint error in three code spans was fixed by a regex over every code span in two directories, rewriting 57 files to change three. The same session had already recorded that lesson from BG0623, where three review rounds each widened the licence to overwrite and each destroyed the next shape along. Knowing the lesson did not prevent it; the tell is the same both times - reaching for a rule that matches a CLASS when the job names specific INSTANCES. When the target is enumerable, enumerate it.

Recorded from retro RETRO0112.

## L-0386: Verify against the INPUT SPACE, not against the criterion

- **Added:** 2026-08-29
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` heuristic 1 'Production-state-shape integration tests' (`testing.md:10`).

Verify against the INPUT SPACE, not against the criterion. Four of ten units were rejected at delivery review and three were regressions: a case-sensitive `choices` against a corpus holding 21 lowercase spellings, `str()`-then-emptiness against `0`/`0.0`/`[]`/`{}`, and a test asserting a parsed intermediate rather than the resolved state its criterion named. Each had been checked against the cases its own criteria listed.

Recorded from retro RETRO0111.

## L-0385: A positive control asserting that an error string is ABSENT proves nothing, because a command that fails for an unrelated reason also omits

- **Added:** 2026-08-29
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` mechanism table row 'A positive control already passing' (`testing.md:92` section).

A positive control asserting that an error string is ABSENT proves nothing, because a command that fails for an unrelated reason also omits it. Both severity suites passed against a guard mutated to refuse every input; asserting `returncode == 0` instead then revealed the fixture had been failing its grooming gate all along, so the accept half had never run.

Recorded from retro RETRO0111.

## L-0384: A repair that keeps moving is a scoping error, not a coding error

- **Added:** 2026-08-29
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `artifact.py` ships the narrowed licence (`_first_h1_line`, `artifact.py:2010`). The meta-rule (stop enumerating shapes after two repairs) has no gate; nearest guidance: `reference-sprint.md` 'A unit that will not go green'.

A repair that keeps moving is a scoping error, not a coding error. BG0623 shipped three times, each fixing the shapes its criterion named and destroying the next shape along - a fenced comment, a `#hashtag`, an indented code line, `## Summary`, a `#` in an HTML comment, a `#` in front matter. The fix that held was not a longer list of shapes but a NARROWER LICENCE TO ACT: only an unambiguous level-one heading outside every container is overwritten, everything else is inserted. When a class of defect survives two repairs, stop enumerating cases and make the dangerous operation harder to reach.

Recorded from retro RETRO0111.

## L-0383: **A test that drives the library while its mutant changes the CLI cannot fail.** This happened twice in one run - BG0618 AC5 and BG0621 AC7

- **Added:** 2026-08-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md` 'Name the ENTRY POINT before writing the test' (`testing.md:66`) names this class and `verify_ac.py` `lane_check` (`verify_ac.py:1331`) reports verifiers that never enter the CLI; re-executing the mutant is the author's step, and no gate holds it.

**A test that drives the library while its mutant changes the CLI cannot fail.** This happened twice in one run - BG0618 AC5 and BG0621 AC7 - and both were found by re-executing the mutant rather than by reading the test. Re-execution is the only thing that distinguishes a passing test from a test that cannot fail.

Recorded from retro RETRO0110.

## L-0382: **A gate the run is measured on must be hardened before the run is measured on it.** BG0621 shipped first for that reason, and its first

- **Added:** 2026-08-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `AGENTS.md` 'Exercise every claim through the shipped entry point'; hardening a gate before measuring on it is a sequencing choice.

**A gate the run is measured on must be hardened before the run is measured on it.** BG0621 shipped first for that reason, and its first execution over real data found a finding invisible to both readers since 2026-07-14. A guard whose first run over the real corpus finds nothing has not been shown to look.

Recorded from retro RETRO0110.

## L-0381: **When a model changes, the assumptions built on the old one become invisible rather than wrong.** `repair_state` read the single standing

- **Added:** 2026-08-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the named `repair_state` is gone (`critic.py` `RETIRED_VERBS` refuses `repair`, `critic.py:4510`; `REJECT_EXITS`, `critic.py:1828`), but the rule stands; no gate holds it; nearest guidance: 'name its writer' (`testing.md:92` section).

**When a model changes, the assumptions built on the old one become invisible rather than wrong.** `repair_state` read the single standing rejection. That was correct while a unit could carry only one live rejection, and the fingerprint-keyed roll-up ends that silently - 118 findings on six units became unreachable by the gate that decides whether a rejection was answered. Nothing failed. Ask, of any model change, which callers assumed the property you just removed.

Recorded from retro RETRO0110.

## L-0380: **A criterion whose subject is the CORPUS cannot be pinned by a mutant on the CODE.** AC5 asserted nineteen units were completely answered

- **Added:** 2026-08-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the mutant BEFORE writing the test' (`testing.md:92`); a corpus-subject criterion needs a document mutant.

**A criterion whose subject is the CORPUS cannot be pinned by a mutant on the CODE.** AC5 asserted nineteen units were completely answered, and its declared code mutant survived: on a corpus where every unit is already complete, removing the completeness check changes nothing. Its mutant had to be a LEDGER mutant - delete a repair row. Three of BG0607's seven mutants ended up being document mutants for this reason, and that is a property of the criteria rather than a weakness in them.

Recorded from retro RETRO0110.

## L-0379: **A repair that cites, as its evidence, the very thing the fix declares invalid has made the record prettier rather than truer.** BG0607

- **Added:** 2026-08-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: the repair ledger it was found in is retired (`critic.py:4510`), but the 'would the sentence read identically' test applies to any free-text reason, including this log's.

**A repair that cites, as its evidence, the very thing the fix declares invalid has made the record prettier rather than truer.** BG0607 replaces a roll-up so that one seat's APPROVE cannot retire another seat's REJECT. Its backfill then closed 24 findings by citing exactly that: a later approval whose brief fingerprint differs from the rejection's. Nothing in the checker caught it, because a per-unit constant reads as evidence to anything looking for non-empty text. The test is not "is there evidence?" but "would this sentence read identically if the finding said something else?" - if yes, it is a formula.

Recorded from retro RETRO0110.

## L-0378: A pre-code review that re-verifies premises is worth more than one that critiques a plan

- **Added:** 2026-08-25
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `reference-sprint.md` 'What the plan critic cannot see'; re-verifying premises is the plan reviewer's charter.

A pre-code review that re-verifies premises is worth more than one that critiques a plan. This one found six false premises in a 24-unit sample - two of them load-bearing for the plan itself - and cut the batch from 24 units and 89 mutants to 13 units, twelve of which closed.

Recorded from retro RETRO0109.

## L-0377: A repair believed shipped can be withdrawn by the review that judges it, and that is the gate working - and the review that judged the

- **Added:** 2026-08-25
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `AGENTS.md` 'Review is independent of the author' and `critic.py` `REJECT_EXITS` (`critic.py:1828`) keep a REJECT standing until the same reviewer approves; measuring a withdrawal against the corpus is by hand.

A repair believed shipped can be withdrawn by the review that judges it, and that is the gate working - and the review that judged the WITHDRAWAL then refuted its stated reason. This one shipped, was measured against the whole corpus by an independent pass, came out, and its re-scope was wrong until a second independent pass computed the counter-example. The cost of finding it at the close rather than at the commit is one revert; the cost of not finding it is a release lane that blocks for everyone downstream, and a re-scope that would have pointed the next run at the most expensive available option.

Recorded from retro RETRO0109.

## L-0376: **Two rules agreeing is corroboration only if they are INDEPENDENT, and mine were nested.** BG0607's roll-up was keyed on the reviewer

- **Added:** 2026-08-25
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the repair-keyed rule is retired (`critic.py:4510`); the surviving roll-up `_unanswered_rejects` (`critic.py:831`) states its keying in its docstring ((unit, reviewer, round); fingerprint only before `ROUND_RULE_SHIPPED`). The general question has no gate.

**Two rules agreeing is corroboration only if they are INDEPENDENT, and mine were nested.** BG0607's roll-up was keyed on the reviewer string and then on a recorded repair; both flipped the same units, and I read that agreement as proof the data was missing and the fix needed a schema change. The repair-keyed rule's unanswered set CONTAINS the reviewer-keyed one by construction - the distinguishing allowance retired two rows and changed no unit-level answer - so the agreement was guaranteed before either rule ran. An adversarial review then found the third rule in the ledger's own `Brief` column, a content hash that identifies the seat and the round together: keyed on it, the unanswered set falls from 81 units to 49, a strict superset recovering 32 and losing none. Two measurements had made me confident in a conclusion one command refutes. Before treating agreement as evidence, state what would have to be true for the two rules to disagree - if nothing could, they are one rule counted twice.

Recorded from retro RETRO0109.

## L-0375: A criterion about an ARTEFACT cannot be verified by a test over CODE

- **Added:** 2026-08-25
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md` 'Name the ENTRY POINT before writing the test' (`testing.md:66`) and `verify_ac.py` `lane_check` (`verify_ac.py:1331`) address verifier-versus-subject mismatch; an artefact criterion needs an artefact check by hand. No gate holds it.

A criterion about an ARTEFACT cannot be verified by a test over CODE. Three mutants survived BG0606's first cut for that reason, and the bug they were pinning was itself about criteria whose verifiers cannot reach what they claim.

Recorded from retro RETRO0109.

## L-0374: Order a batch by what compounds over the run, not by severity

- **Added:** 2026-08-25
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `reference-sprint.md` 'The Two Instruments'; `sprint plan` does not order by what the run's own instruments depend on.

Order a batch by what compounds over the run, not by severity. Four of this run's thirteen units repair instruments the run itself uses - the ledger it appends to, the annotate verb it calls, the roll-ups it writes into. Fixing them first made every later unit cheaper and its evidence more trustworthy; fixing them last would have meant delivering twelve units on instruments known to be wrong.

Recorded from retro RETRO0109.

## L-0373: A fixture that cannot reach the branch is a fixture that proves the fail-open path

- **Added:** 2026-08-25
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` mechanism table row 'A fixture shape the product cannot produce' (`testing.md:92` section).

A fixture that cannot reach the branch is a fixture that proves the fail-open path. Two mutants survived here not because the code was unguarded but because the check is deliberately silent when git cannot answer, and the fixture gave it nothing to answer with. When a guard has a documented fail-open, every test of it must first prove the guard was ASKED.

Recorded from retro RETRO0109.

## L-0372: A gate's behaviour must be read for the POPULATION you care about, not in general

- **Added:** 2026-08-25
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `AGENTS.md` ('Decide which by execution'); reading a gate for the population is by hand.

A gate's behaviour must be read for the POPULATION you care about, not in general. Two change requests and eight days rested on the belief that bugs pay an independent plan review; measured across all 23 open bugs, none does. The two functions that refuse a missing test plan carry byte-identical messages, so the refusal a bug hits looks exactly like the refusal a story hits and comes from a different gate with different rules. D0151 records the rule; this run then broke it once more within the hour, which is the honest measure of how weak a prose rule is.

Recorded from retro RETRO0109.

## L-0371: A repair for unpinned behaviour can itself ship unpinned, and did

- **Added:** 2026-08-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` `revert_check` (`verify_ac.py:4088`) refuses a unit whose verifiers stay green with its production change reverted, the 'what fails if the repair is removed' question for declared files; otherwise no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the mutant BEFORE writing the test' (`testing.md:92`).

A repair for unpinned behaviour can itself ship unpinned, and did. `_first_three` was added to fix a finding that the lane truncated its output silently - and it shipped with no test and no plan row, so the fix for "this is not pinned" was not pinned. An independent review found it one round later. The check is mechanical: after writing a repair, ask what test fails if the repair is removed, and if the answer is none, the repair is a claim.

Recorded from retro RETRO0108.

## L-0370: The plan review took FOUR rounds, and the biggest single cause was a rule already written down: I hand-edited test-plan tables that

- **Added:** 2026-08-24
- **Review-by:** 2026-11-22

The plan review took FOUR rounds, and the biggest single cause was a rule already written down: I hand-edited test-plan tables that `verify_ac.py testplan derive` owns. That produced a FUSED table row inside US0674's AC4 Title cell - a row a human reads and `testplan_rows_by_criterion` cannot see, so the unit's own derived field said "plan rows 8; executed 8; not-run 0" and every one of those numbers was computed over a table missing a row - and Title cells on two US0676 criteria stating a different criterion's claim. Running the tool repaired all of it in one command and then reported "unchanged". AGENTS.md's rule is "always look for a tool before doing anything by hand", the runbook names this exact command, and the failure mode it prevents is not sloppiness but a table that parses differently from how it reads.

Recorded from retro RETRO0108.

- **Status:** Closed - the tool is gone: `verify_ac.py` `RETIRED_VERBS` (`verify_ac.py:4325`) refuses `testplan` ('no `## Test Plan` is derived... the criteria and their Verify selectors are the plan'), so there are no derived test-plan tables to hand-edit.

## L-0369: The derived field caught its own run's stale evidence, which is the first time an instrument this project built reported against the

- **Added:** 2026-08-24
- **Review-by:** 2026-11-22

The derived field caught its own run's stale evidence, which is the first time an instrument this project built reported against the session that built it. Registering the newly-executed mutants invalidated every earlier registration for the same targets - registration is keyed on the target's content hash, and the close had edited `verify_ac.py` and `gate.py` - so `depth` went from "executed 5" to "executed 3" and named the rows that no longer had support. Nothing else in the toolchain would have said a word: the suite was green, the criteria all passed, and the old counts sat in the fields looking exactly as they had. Twenty-two rows were re-executed against the current tree as a result, and every unit now reads `not-run 0`. LL0053 says register AFTER the last edit; what this adds is that the FIELD is what tells you when you did not.

Recorded from retro RETRO0108.

- **Status:** Closed - the derived field and its ledger are gone: `verify_ac.py` `RETIRED_VERBS` (`verify_ac.py:4325`) retires `depth`, and `mutation.py` module docstring (`mutation.py:31`) retires `register`, `retract`, `retractions` and `audit` (the per-target ledger nothing reads) and `RETIRED` refusals at `mutation.py:2144`.

## L-0368: A repair whose test can be satisfied by EITHER of two guards pins neither, and I shipped that shape while repairing this very defect

- **Added:** 2026-08-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the mutant BEFORE writing the test' (`testing.md:92`); one mutant per guard is the author's discipline.

A repair whose test can be satisfied by EITHER of two guards pins neither, and I shipped that shape while repairing this very defect. The widened path pattern grew two arms - any extension once a `/` is present, and an allowlist for bare filenames - and my first test used one fixture, `config/settings.yaml`, which BOTH arms match. Deleting either arm left the test green. Two mutants survived my own repair, and I found them only because I executed them rather than trusting the green. The fix was two tests, each with a fixture only one arm can see: a bare `settings.yaml` and a `config/values.jsonnet`. Name the mutant first is not enough - name one mutant PER GUARD.

Recorded from retro RETRO0108.

## L-0367: A plan row can be killed by a test the criterion does not name, and the toolchain will call that covered

- **Added:** 2026-08-24
- **Review-by:** 2026-11-22

A plan row can be killed by a test the criterion does not name, and the toolchain will call that covered. `plan_execution` joins rows to the ledger on (criterion, row) and never asks WHICH node did the killing, though the ledger records it and the `Verify:` line states which node was supposed to. An independent plan review found SIX such rows in this six-unit batch - in the batch whose whole subject was that a unit's own evidence must be honest - and found them by reading the ledger against the Verify: lines by hand. Filed as BG0606, with CR0554 to make the comparison the tooling already has the data for.

Recorded from retro RETRO0108.

- **Status:** Closed - `plan_execution` and the plan-row-to-ledger join are gone: `verify_ac.py` `RETIRED_VERBS` (`verify_ac.py:4325`) retires `testplan` and `depth`, and `mutation.py` module docstring (`mutation.py:31`) retires `register`, `retract`, `retractions` and `audit` (the per-target ledger nothing reads) and `RETIRED` refusals at `mutation.py:2144`; the criteria and Verify selectors are now the plan.

## L-0366: A partial disposition recorded twice reads as two partial dispositions forever

- **Added:** 2026-08-24
- **Review-by:** 2026-11-22

A partial disposition recorded twice reads as two partial dispositions forever. `critic.py repair` computes the outstanding set from the closures in that invocation alone, so four units whose findings were fully closed across two calls each left two rows stamped PARTIAL, each naming as outstanding what the other row closed. Filed as BG0605.

Recorded from retro RETRO0108.

- **Status:** Closed - `critic.py repair` is retired (`critic.py` `RETIRED_VERBS`, `critic.py:4510`: 'the repair ledger is gone'), so no PARTIAL disposition rows are written.

## L-0365: A gate lane that mutates the shared working tree corrupts whatever else is reading it

- **Added:** 2026-08-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` `revert_check` (`verify_ac.py:4088`) still reverts the working tree but restores from a byte snapshot in a `finally`; `mutation.py` `open_window` (`mutation.py:693`) and `dirty_targets` (`mutation.py:800`) make the gate refuse while a window is open. The shared-tree risk is reduced, not removed.

A gate lane that mutates the shared working tree corrupts whatever else is reading it. `revert-check` reverted this repository's own `verify_ac.py` underneath a parallel test worker. The same shape destroyed a reviewer's uncommitted work through the manual oracle. One defect, two victims, filed as CR0552 and BG0604.

Recorded from retro RETRO0108.

## L-0364: A fixture whose counts are EQUAL cannot detect a swap, and the REPAIR for it moved the defect rather than closing it

- **Added:** 2026-08-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the derived-depth fixture is gone (`verify_ac.py` `RETIRED_VERBS` (`verify_ac.py:4325`)) but the rule holds; no gate holds it; nearest guidance: `best-practices/testing.md` 'Name the mutant BEFORE writing the test' (`testing.md:92`).

A fixture whose counts are EQUAL cannot detect a swap, and the REPAIR for it moved the defect rather than closing it. The derived-depth fixture used 2 criteria, 2 rows and 2 executions, so four of five counts survived being exchanged. It was rebuilt as 3 criteria, 4 rows, 3 executed - and the round-2 QA seat proved that still degenerate: criteria(3) EQUALS executed(3), and killed, survived, equivalent and not-run are ALL 1. The test docstring asserting "every count is a different number" was false, and so was the same claim in the commit message and in the first draft of this retro. Two mutants survive against the final file - swapping the killed and survived counts, and sourcing the criteria count from the ledger's executed rows instead of the artefact's ACs. The lesson is not the original defect but the repair: a fix aimed at ONE equality restored one number and left four, and nobody re-checked the property, only the number that had been complained about.

Recorded from retro RETRO0108.

## L-0363: Absent and could-not-ask must be different answers, and this run needed the lesson TWICE

- **Added:** 2026-08-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` `_base_blob` (`verify_ac.py:3975`) raises `_BaseUnreadable` rather than reading a git failure as absent, and the coverage path refuses by name when `combine` fails (`verify_ac.py:2547`).

Absent and could-not-ask must be different answers, and this run needed the lesson TWICE. `_base_blob` read any git failure as "absent at base" and deleted the production file, manufacturing the red it was looking for. Separately, a verifier that never RAN was counted as green evidence that the tests reached the change. Both are the same error: an unmeasured state collapsed into a measured one.

Recorded from retro RETRO0108.

## L-0362: A staging decision that puts a unit LAST also puts it outside the review that already ran

- **Added:** 2026-08-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it; nearest guidance: `reference-sprint.md` 'The loop'; nothing refuses a staging order that puts a unit outside a review that already ran.

A staging decision that puts a unit LAST also puts it outside the review that already ran. D0149 required wave 2 to land last in its own commit so the oracle stayed honest; the effect was that US0674 and US0676 - the two gate lanes, the highest-blast-radius units in the batch - were never in front of delivery round 1. Round-1 briefs exist for US0671, US0672, US0673 and US0675 and for no others. The review hole was created by the ordering, not by an omission anybody noticed.

Recorded from retro RETRO0108.

## L-0361: Marginal review yield decays, and a round cap should be set from that rather than from batch size

- **Added:** 2026-08-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py` `DEFAULT_REVIEW_CEILING = 2` (`critic.py:1761`) sets the cap, with `review.max_rounds` in `reference-config.md`; D0132's cap of 6 is superseded but the yield-based principle holds.

Marginal review yield decays, and a round cap should be set from that rather than from batch size. D0132 raised the cap to 6 reasoning that bigger batches take more rounds; this run shows the later rounds converging on the evidence apparatus rather than on the code.

Recorded from retro RETRO0107.

## L-0360: Ceremony scaled by FILE size is not ceremony scaled by risk

- **Added:** 2026-08-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true on the current weights: `route.py:60` sets `code` 0.25 and `risk` 0.15, and both come from one call, `complexity.assess(root, resolved)` (`route.py:120`), whose `max_cognitive` is the maximum over every function in every declared file (`complexity.py:297-302`). Together that is the 0.40 the lesson names, so a small change to a large module still inherits its worst function. No gate bounds that.

Ceremony scaled by FILE size is not ceremony scaled by risk. `route.estimate` takes 0.40 of its weight from a complexity read over every function in every declared file, so a two-line change to a large module inherits that module's worst function. Measured over 603 bugs: 87% tier `full`, `code` and `risk` both saturated for 48%, and half the corpus inside a six-point score spread. A gate with that little dynamic range is a constant wearing the appearance of a gate.

Recorded from retro RETRO0107.

## L-0359: A changelog fragment written at the first commit describes the design that existed THEN

- **Added:** 2026-08-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a changelog fragment describes the design that existed at its commit. AGENTS.md:133 requires the fragment in the same commit as the code (`changelog.d/<UNIT-ID>.md`), and `critic.py:2542-2550` has the reviewer rule every CHANGELOG claim TRUE, FALSE or UNVERIFIABLE; `check_self_check` (`critic.py:2915`) requires a claim from each declared fragment. A redesign that leaves a stale fragment is caught only by that pass.

A changelog fragment written at the first commit describes the design that existed THEN. A redesign must rewrite the fragment, not only the code: BG0593's shipped for three commits describing the symlink mechanism its own AC3 forbids by name, and was caught only when a reviewer applied the fragment's own words as a mutant and watched the unit's test kill it.

Recorded from retro RETRO0107.

## L-0358: Re-registering against a file edited since the first registration DISCARDS the earlier verdicts, and that is correct

- **Added:** 2026-08-21
- **Review-by:** 2026-11-19

Re-registering against a file edited since the first registration DISCARDS the earlier verdicts, and that is correct. BG0594's four rows went to zero for exactly this reason and had to be re-executed against the current bytes. Register after the last edit, or budget for re-running.

Recorded from retro RETRO0107.

- **Status:** Closed - No longer true: re-registering a verdict against an edited file was the per-target ledger's behaviour, and that ledger is gone. `mutation.py` retired `register`, `retract` and `audit` (`RETIRED_VERBS`, `mutation.py:2142`; US0936), and a run keeps only its series row. There is no registration to discard, so register-after-the-last-edit advice no longer applies.

## L-0357: A retract-and-re-register cycle leaves the superseded row LIVE unless something withdraws it, and a join keyed on `(criterion, row)` then

- **Added:** 2026-08-21
- **Review-by:** 2026-11-19

A retract-and-re-register cycle leaves the superseded row LIVE unless something withdraws it, and a join keyed on `(criterion, row)` then silently resolves to whichever row is iterated last. Withdraw before re-registering, then audit for duplicate live rows - the audit is four lines and nothing else in the toolchain performs it.

Recorded from retro RETRO0107.

- **Status:** Closed - No longer true: the retract-and-re-register cycle it describes is gone. `mutation.py` retired `register`, `retract`, `retractions` and `audit` and keeps no per-target ledger (`RETIRED_VERBS`, `mutation.py:2142`; docstring `mutation.py:32`; US0936), so there is no superseded live row to leave behind. A duplicate-live-row audit is moot.

## L-0356: Scope a rung fix to the rung it is about, never to "not `done`"

- **Added:** 2026-08-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held where it was found: BG0582 and BG0584 are Fixed, and `sprint.py` scopes the rung to its own terminal (`sprint.py:3242` `_terminal_in_type_vocab`, `:6964` `undelivered_blockers`, 'RUNG-AWARE'). A new rung fix written as 'not done' is not gated; the correct ruling lives in those comments.

Scope a rung fix to the rung it is about, never to "not `done`". Done twice now: BG0582's siblings were rejected for it at their round two, the correct ruling was written into `sprint.py` twice, and BG0584 made the same mistake again with those comments in the file.

Recorded from retro RETRO0105.

## L-0355: A false premise RESTATED is worse than the original, because each restatement reads as verification

- **Added:** 2026-08-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a false premise restated reads as verification. no gate holds it; nearest guidance is AGENTS.md:98-101 (decide by execution) and the claim inventory (`critic.py:2542-2550`), which marks a claim TRUE only after a command settles it. BG0583 (Won't Fix) shows the premise being refuted by measurement.

A false premise RESTATED is worse than the original, because each restatement reads as verification. "Every retro carries asterisks" was corrected once to blame the generator - also false - before measurement gave 102 dash and 3 asterisk of 105.

Recorded from retro RETRO0105.

## L-0354: A fixture that makes the mutant equivalent is the commonest way a test measures nothing here

- **Added:** 2026-08-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a fixture that makes the mutant equivalent is the commonest way a test measures nothing. `best-practices/testing.md:108` and `:113` list 'A fixture shape the product cannot produce' and 'A positive control already passing', and `critic.py:2475-2483` has the reviewer mutate the tests and isolate a survivor. No gate checks a fixture can distinguish the mutant.

A fixture that makes the mutant equivalent is the commonest way a test measures nothing here. Three instances this run: a census test whose repo root resolved to `.claude/` so its glob matched nothing; a thematic-break test whose fixture put the real list ahead of the break; and a green-figure test whose every story had `manual=0`, hiding a numerator that counted manual criteria as green.

Recorded from retro RETRO0105.

## L-0353: A detector's SILENCE is evidence only once it has been shown able to speak

- **Added:** 2026-08-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a detector's silence is evidence only once it has spoken. AGENTS.md:122 requires the refusals plus a positive control, and `critic.py brief` is refused without a recorded self-check (`critic.py:2915`). `tools/gate_prereqs.py check` names each missing prerequisite (AGENTS.md:52-59), the repair for the markdownlint case; a new helper that treats a missing tool as clean is not gated.

A detector's SILENCE is evidence only once it has been shown able to speak. The markdownlint helper caught a missing binary and not a missing package, so it handed `npm ERR! 404` to an `assertNotIn` and four criteria's lint half was inert in any clone without `npm ci` - while both its docstring and the depth field said "skipped, never faked". Prove the tool detects the thing on a known-bad input before trusting a clean result.

Recorded from retro RETRO0105.

## L-0352: A false-premise filing costs more than the bug it invents

- **Tags:** measurement, filing, exit-codes
- **Added:** 2026-08-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a fabricated finding costs more than the bug it invents, and the mechanism is the L-0277 pipe-status one. BG0583 is Won't Fix, confirming the premise was false. Filing does not re-run the claim, so before-filing verification is the author's act; the nearest guidance is AGENTS.md:98-101 and :122 (exercise each claim through the entry point, refusals included).

BG0583 was filed as a High defect claiming `verify_ac run` exits 0 for a unit it never read. Every branch of that contract was correct: 0 green, 1 red, 2 could-not-read. The evidence was five exit codes read as `cmd | tail -2; echo $?`, which reports tail's status - the exact construct L-0277 already forbids in general terms. The lesson did not need widening; it was read and not followed. What makes this worth its own entry is the COST SHAPE, which is not the cost of a missed defect. A fabricated finding propagates: it was ruled not-stop-ship in a retro, written into reviews/LATEST.md as a real finding for the next session to read first, counted in the open-High set that the release-notes bar compares against, and it displaced a real fix from the queue. Refuting it took longer than filing it, and every artefact that had already quoted it needed correcting. So: before filing, re-run the reproduction through the shipped entry point with the exit code read DIRECTLY - redirect to a file, echo $? on its own line - and prefer refuting your own premise to being refuted by a reviewer. A finding is a claim about the code; measure it with the same care a criterion demands, because everything downstream treats it as measured.

## L-0351: A ledger that reads zero because nobody looked is indistinguishable from one that reads zero because it is zero

- **Added:** 2026-08-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a ledger reading zero because nobody looked is not one reading zero. `gate.py:2126-2128` degrades an unknown to RUNNING, and `sprint_report.py:396-403` words a missing record as 'not a run that found nothing'. A new ledger gets neither automatically; no gate checks a detector can report a non-zero.

A ledger that reads zero because nobody looked is indistinguishable from one that reads zero because it is zero. The only reason this was visible is that a detector asked the question that no gate asks.

Recorded from retro RETRO0104.

## L-0350: Repairs raised by a review round are new units nobody planned, and they are the systematic leak rather than the careless one

- **Added:** 2026-08-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a repair raised by a review round is an unplanned unit. `sprint batch add` (`sprint.py:12379`) is the verb that names it in the run (`help/sprint.md:328`), and nothing forces its use when the repair gets an id; no gate reports a unit that reached terminal in a run whose batch never named it. The practice rests on the operator.

Repairs raised by a review round are new units nobody planned, and they are the systematic leak rather than the careless one. Three of these twelve were round-two repairs; the moment such a repair gets its own id it needs `sprint batch --add`, or the run that caused it will not name it.

Recorded from retro RETRO0104.

## L-0349: A batch is approved once and then only read, so work agreed AFTER the approval never joins it

- **Added:** 2026-08-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a batch is approved once and then only read. `sprint batch add`, `add-epic`, `drop` and `swap` exist (`sprint.py:12379`, `help/sprint.md:501` records them) but nothing compares units that reached terminal inside the run against the batch: a grep of `sprint.py` and `sprint_report.py` found no off-batch check. The close accounts for the batch, not for everything shipped.

A batch is approved once and then only read, so work agreed AFTER the approval never joins it. Twelve units reached terminal inside runs whose batches never named them, and both runs still closed green - the close checks that the batch is accounted for, never that the account is the whole of what shipped.

Recorded from retro RETRO0104.

## L-0348: An exit condition satisfied by deleting a marker is not an exit condition

- **Added:** 2026-08-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: an exit condition cleared by deleting a marker is not one. `conformance.py` `story_is_ungroomed` (`conformance.py:195-216`) returns True on the marker token, and otherwise judges the AC section for a placeholder with no real criterion, so removing the token alone passes only a story with no placeholder left. No gate requires red-now evidence for a goal; that stays the charter's own premise.

An exit condition satisfied by deleting a marker is not an exit condition. `story_is_ungroomed` returns false the moment the placeholder token goes, so the goal needed evidence - the red-now ledger - rather than a gate that a `touch` clears.

Recorded from retro RETRO0103.

## L-0347: A charter whose declared scope has emptied does not become a licence for whatever batch is convenient

- **Added:** 2026-08-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and now gated: `sprint.py` `resolve_head_charter` (`sprint.py:1435`) refuses an `empty-scope` charter (`sprint.py:1475`, 'the work it was written for is delivered') and leaves it Queued rather than licensing an arbitrary batch, and refuses a charter with no scope query. Amending the charter on the record remains the operator's act.

A charter whose declared scope has emptied does not become a licence for whatever batch is convenient. SC0005 named 20 bug ids, all now terminal, and its scope query authorised no story at all - amend it on the record, or the run has no charter.

Recorded from retro RETRO0103.

## L-0346: A rung is a claim about what a run can reach, and stating a terminal without knowing the rung is stating an answer to a question nobody

- **Added:** 2026-08-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and repaired at its site: BG0581 (the goal review brief stating a reachable end) is Fixed, and `sprint.py` `_terminal_in_type_vocab` (`sprint.py:3242`) and `undelivered_blockers` (`sprint.py:6964`) now judge a unit against the rung's own terminal. A new brief that states a terminal without the rung is not gated.

A rung is a claim about what a run can reach, and stating a terminal without knowing the rung is stating an answer to a question nobody asked. The brief promised Review for a run that correctly ends at Ready (BG0581).

Recorded from retro RETRO0103.

## L-0345: An admission rule that asks a question whose answer moves with the tree admits entries that silently stop qualifying

- **Added:** 2026-08-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: an admission rule whose answer moves with the tree rots. The instance was repaired ('the bar is now unconditional', RETRO0103 lines 49-52; commit 734c775c) and BG0556 is Fixed. The general rule has no gate; a new inventory with a tree-dependent admission test would be caught only by the control that removed these entries.

An admission rule that asks a question whose answer moves with the tree admits entries that silently stop qualifying. Four inventory entries were removed in two days, each caught by the control rather than by anyone reading the list; none was wrong to admit, and every one passed its measurement honestly on the day it went in. Bars must be unconditional or they rot.

Recorded from retro RETRO0103.

## L-0344: Never repair the gate that is refusing your own run

- **Tags:** review-independence, gates, close, rung
- **Added:** 2026-08-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and a standing rule: never repair the gate refusing your own run. AGENTS.md:87-91 (review independent of the author) and the bypass rule (AGENTS.md:60, `--no-verify` and nothing else) hold it as policy; `sprint.py` `undelivered_blockers` is now rung-aware (`sprint.py:6964`), the repair this lesson refused to author in-session now exists in the tree. No gate prevents a self-repair; `sprint sign` refuses an author as principal.

A design-rung run finished its work and then could not close: three lanes (undelivered_blockers, the done-gate fan-out, critic signoff) all assume the delivery rung's terminal, and `critic signoff` refuses to WRITE for a unit at Ready, so the operator cannot clear the stop by hand either. The obvious move was to make the closer rung-aware - a small change, already specified in the same file's own docstring, and it would have closed the run in minutes. It was rejected, and that rejection is the lesson. Editing the gate that is refusing your run, in the session it is refusing, with no independent review, is indistinguishable from disabling it: the author is the only judge of whether the repair was correct, and the evidence that it worked is that the author's own run now passes. The circularity is total. A gate is worth exactly what it refuses when refusing is inconvenient. So: when a gate walls your close, record the wall with the exact refusal text, file it, and leave the run OPEN. An open run with a filed blocker is a true record; a closed run with a self-authored gate repair is a false one, and the falseness is invisible afterwards because the gate is green. The corollary for tool design: a rung that can be ENTERED and not EXITED is worse than one that does not exist, because the work is done before the wall is met - either the planner refuses the rung, or every lane in the close chain reads it.

## L-0343: A mutant that cannot reach the code it names proves as little as a test that cannot fail

- **Tags:** mutation, evidence, verification, testing
- **Added:** 2026-08-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true for the practice: after applying a mutant, confirm the test fails for the stated reason. `critic.py:2479-2483` ('a survivor is evidence about the harness, not about the test') and `critic.py` `check_self_check` (`critic.py:2915`) require the author's mutants to name a test and a result. The register-inside-the-branch advice is moot (`mutation.py:2142`, `register` retired); the rest holds and no gate applies it.

Declaring a mutant is not executing one, and executing one is not reaching the claim. A mutant that never reaches the behaviour its criterion names returns SURVIVED - or worse, KILLED for an unrelated reason - and either reading is evidence about the harness rather than about the test.

Six instances in one run, each of which looked like evidence at the time:

- A mutant patched the MESSAGE a function prints rather than `active()`, the resolver that decides. The command's behaviour never changed.
- A mutant patched a field MAP rather than the writer, so the record was written correctly whatever the map said.
- A mutant replaced a lane verifier with `manual`, which satisfies the lane exactly as the real verifier does - so it was not a mutant at all.
- A mutant set a key to `set()` on a path an uncovered unit never enters, so the covered case could not discriminate.
- A mutant dropped ONE row from a two-row table; the remaining row still satisfied the assertion.
- A mutant's anchor was not unique, so the patch never applied and the run reported on unmutated code.

The practice that catches all six is the same: after applying a mutant, confirm the test fails FOR THE STATED REASON before recording anything - read the assertion message, not just the exit code. And register the verdict only inside the branch that observed it. Three verdicts in this run were registered before being confirmed, and all three had to be retracted; the single cause was a `register` call sitting outside the `if killed` branch.

The reason this matters more than an ordinary test defect: a surviving mutant is normally read as a finding about the TEST. When the mutant could not reach the code, that reading is false in both directions - a survivor accuses a sound test, and a kill credits one that never ran.

## L-0342: A recorded list is a claim like any other and rots the same way

- **Added:** 2026-08-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a recorded list is a claim and rots. `critic.py` `validate_claim_inventory` (`critic.py:3666`) refuses an unruled claim, and `lessons.py revalidate` (this pass) re-checks recorded lessons against the tree. A hand-maintained list elsewhere (a debt list, a count) is re-measured only by whoever reads it; no gate does.

A recorded list is a claim like any other and rots the same way. An eight-of-twelve stale debt list, a 12% fictional backlog, and a bug whose 4.5x premise measured 0.98x were all found by re-measuring rather than by reading.

Recorded from retro RETRO0102.

## L-0341: A guard a paraphrase can defeat is weak; one the OPPOSITE statement satisfies is inverted

- **Added:** 2026-08-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a guard a paraphrase defeats is weak and one the opposite statement satisfies is inverted. `best-practices/testing.md:55-64` (heuristic 6, 'A message and its verdict are driven by one test') drives both over one battery of inputs. No gate checks that a spec-agreement guard fails on the opposite statement.

A guard a paraphrase can defeat is weak; one the OPPOSITE statement satisfies is inverted. Two spec-agreement guards were inverted, and either would have reported agreement while the specification stated the reverse of the code.

Recorded from retro RETRO0102.

## L-0340: Verification run where the author is standing is not verification

- **Added:** 2026-08-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: verification run where the author stands is not verification. `critic.py brief` demands a fresh reviewer context (AGENTS.md:87-91) and `critic.py:2488` requires an isolated checkout; the author's own pass is recorded by `check_self_check` (`critic.py:2915`) but is compulsory and not independent. No gate runs a verification in a clean worktree on the author's behalf.

Verification run where the author is standing is not verification. A tracked-file write was invisible because gitignored state made the regeneration byte-identical; a control accepted the root path as evidence and so passed on a crash. Both were found only by a clean worktree.

Recorded from retro RETRO0102.

## L-0339: A mutant that cannot reach the code it names proves as little as a test that cannot fail

- **Added:** 2026-08-15
- **Review-by:** 2026-11-13

A mutant that cannot reach the code it names proves as little as a test that cannot fail. Six were re-chosen in this run: one patched a message instead of the resolver, one a field map instead of the writer, one a `manual` verifier that satisfied the lane exactly as the real one did. Each was registered, or nearly registered, as evidence.

Recorded from retro RETRO0102.

- **Status:** Closed - Duplicate of L-0343, which carries the same claim with all six instances and the mechanical rule that prevents the false verdicts. L-0339 was extracted from RETRO0102 by the close; L-0343 was then added by hand without checking, which is the recorded-list-rots failure in L-0342 committed while recording L-0342. The richer entry survives.

## L-0338: Reviewing the PLAN catches what code review cannot: a wrong discriminator, an exemption inherited unscoped, and a missing step that makes

- **Added:** 2026-08-11
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a plan review catches what code review cannot. The `test-spec` type ships (`sdlc-studio/test-specs/`) and `best-practices/testing.md:122-126` states the honest limit of a pre-implementation design review. No gate requires a plan review before code.

Reviewing the PLAN catches what code review cannot: a wrong discriminator, an exemption inherited unscoped, and a missing step that makes the goal unreachable rather than merely late.

Recorded from retro RETRO0101.

## L-0337: A number nobody re-measures is wrong

- **Added:** 2026-08-11
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a number nobody re-measures is wrong. The tree re-measures its own figures where it can (`tools/gate_timing.py` estimates from recorded runs; `tools/check_budgets.py` records measured ceilings), and the claim inventory marks a stated figure TRUE, FALSE or UNVERIFIABLE (`critic.py:2542-2550`). A figure stated in prose and never re-run is not gated.

A number nobody re-measures is wrong. Five stated figures were re-run this sprint and five were stale - the red-criteria count, the disclosed total, both suite durations, and a bug's own account of why its repair changed nothing.

Recorded from retro RETRO0101.

## L-0336: A guard narrowed to the RIGHT question can be less safe than the wrong one it replaced

- **Added:** 2026-08-11
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and fixed at the site: `test_transition.py:53-80` `_refuse_working_tree` now asks four relations (a `.git` entry, the repository root, a parent of it, and a root inside it) rather than 'is it under /tmp', exactly the repair this lesson records. A new narrowed guard is not checked by any gate; the opposite-side fixture is the practice.

A guard narrowed to the RIGHT question can be less safe than the wrong one it replaced. The fixture guard asked "is this under /tmp", which refused a subdirectory for the wrong reason; asking "is this the repository" without the containment relation accepted it.

Recorded from retro RETRO0101.

## L-0335: A comparison is satisfied by agreement, INCLUDING agreement the defect produces

- **Added:** 2026-08-11
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a comparison is satisfied by agreement, including the defect's. `critic.py:2475-2478` ('two implementations agree by construction') and `best-practices/testing.md:55-64` (a substring check passes for an input the sentence does not describe) hold it as guidance. No gate checks a test asserts the value, not the agreement.

A comparison is satisfied by agreement, INCLUDING agreement the defect produces. Three tests this run claimed more than they could observe: one compared two results with each other, one passed under the exact mutation its own message named, and one compared a set of paths so a write to an existing file was invisible. Assert the value, not the agreement.

Recorded from retro RETRO0101.

## L-0334: A test that proves a guard works must not depend on the guard working

- **Added:** 2026-08-11
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held for the guard it names: the fixture-root guard is pinned against a fake checkout (`test_transition.py` `_fake_checkout`, the under-the-temp-directory case at `test_transition.py:2677-2690`) and asks the predicate rather than building the workspace, so the test no longer depends on the guard working. The general rule has no gate.

A test that proves a guard works must not depend on the guard working. The test written to pin the fixture root guard handed it the real checkout and relied on it to refuse - so it was safe only while the thing it tested was correct, and it ran on the day that thing was wrong, which is the day it exists for. It destroyed a reviewer's checkout.

Recorded from retro RETRO0101.

## L-0333: **A test that passes only because a sibling ran first is not passing.** US0664 AC3 held for a whole round because two tests above it warmed

- **Added:** 2026-08-10
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a test that passes only because a sibling ran first is not passing. `mutation.py` `_purge_bytecode` (`mutation.py:354`) drops cached bytecode before each mutant, and its docstring says `_run_tests` refuses to write bytecode, which closes the cache-warming path named. `critic.py:2479-2483` asks the reviewer to run a survivor's branch alone. Running a criterion cold is not gated.

**A test that passes only because a sibling ran first is not passing.** US0664 AC3 held for a whole round because two tests above it warmed the bytecode cache the harness itself wrote. Run the criterion alone, cold, which is how a reviewer will run it.

Recorded from retro RETRO0100.

## L-0332: **A declared mutant is executed by strangers - write it so it cannot destroy their work.** "Change the fixture root to the repository root"

- **Added:** 2026-08-10
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and partly mechanised: `critic.py:2488` tells a reviewer to mutate only in an isolated checkout and not use tree-wide cleanup, and `test_transition.py:53-80` (`_refuse_working_tree`) refuses a fixture root that is a checkout before anything is written. A declared mutant that destroys a stranger's work is not refused by any gate, so it rests on how the mutant is written.

**A declared mutant is executed by strangers - write it so it cannot destroy their work.** "Change the fixture root to the repository root" met a `rm -rf "$WORK"` trap and deleted a reviewer's worktree. The harness now refuses that root before the trap is armed.

Recorded from retro RETRO0100.

## L-0331: **A guard that hides a fault also hides the evidence of it.** Gitignoring the residue path stopped it being committed and stopped `git

- **Added:** 2026-08-10
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a suppression is also a blindfold. no gate holds it; nearest guidance is AGENTS.md:98-101 (decide by execution, not impression). Ignore rules and residue paths are not reviewed by any lane, and `mutation.py` `_purge_bytecode` (`mutation.py:354`) is a case of removing residue rather than hiding it.

**A guard that hides a fault also hides the evidence of it.** Gitignoring the residue path stopped it being committed and stopped `git status` seeing it, in the very criterion the ignore rule was added to harden. Every suppression is also a blindfold; ask what stopped being visible.

Recorded from retro RETRO0100.

## L-0330: **A presence check can never detect an addition.** US0663 AC3 asserted two strings were PRESENT while its own declared mutant was an

- **Added:** 2026-08-10
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a presence check cannot detect an addition. `best-practices/testing.md:113` lists 'A positive control already passing' and `critic.py:2475-2478` has the reviewer mutate the tests, including an added key. No gate checks an absence-shaped criterion has an absence-shaped assertion.

**A presence check can never detect an addition.** US0663 AC3 asserted two strings were PRESENT while its own declared mutant was an ADDITION, so adding the forbidden key made the test pass harder. An absence-shaped criterion needs an absence-shaped assertion and a control that adds the thing.

Recorded from retro RETRO0100.

## L-0329: **A repair that is correct and ungated is not a repair.** Rounds 3 and 5 each reverted the previous round's fix against a green suite and

- **Added:** 2026-08-10
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a correct but ungated repair reverts silently. `critic.py:2484-2487` tells the reviewer to report missing regression cover on a behaviour-changing repair as a finding. No gate requires a failing-if-reverted test for a repair; it is the reviewer's finding.

**A repair that is correct and ungated is not a repair.** Rounds 3 and 5 each reverted the previous round's fix against a green suite and watched nothing fail: the boundary regression, the spurious advisory, and the bytecode residue were all fixed and all unguarded. The question after any repair is not "is it right" but "what fails if it comes back".

Recorded from retro RETRO0100.

## L-0328: A tool whose blast radius is its own source must be scoped to the literal it rewrites

- **Added:** 2026-08-08
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and repaired where found: `tools/check_budgets.py` `record_ceilings` (`tools/check_budgets.py:136`) rewrites only ceiling integers and is 'SCOPED TO THE ALLOWLIST LITERAL' (`:151`) rather than line-wise over the source. The general rule for any other tool rewriting its own source has no gate; review catches it.

A tool whose blast radius is its own source must be scoped to the literal it rewrites. The demonstration cost nothing - a ceiling-shaped line in a docstring - and the failure mode is silent corruption of the file that decides what every budget is.

Recorded from retro RETRO0099.

## L-0327: Drive the claim through the COMMAND and it finds wiring the suite cannot see

- **Added:** 2026-08-08
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and still producing: AGENTS.md:122 requires each claim driven through the shipped entry point before review, and `best-practices/testing.md:66-90` states the rule. `critic.py brief` is refused until the self-check is recorded (`review.author_self_check: block`, `critic.py:2915`), so the pass is compulsory; the lane check (`verify_ac.py:1331`) is advisory.

Drive the claim through the COMMAND and it finds wiring the suite cannot see. Adding one CLI-driving verifier per unit, to satisfy an advisory lane check, found that `docgen.py references` and `surface` threaded `--root` to the file they wrote but not to the content they read, and that `nesting_depth` had zero callers. A 6348-test green suite held both.

Recorded from retro RETRO0099.

## L-0326: A criterion is only as good as the mutant its test can fail on

- **Added:** 2026-08-08
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a criterion is only as good as the mutant its test can fail on. `best-practices/testing.md:92-96` (name the mutant first) and `critic.py:2475-2478` (the reviewer mutates the tests) hold it; `critic.py brief` carries the canonical criteria as law (AGENTS.md:92-96). No gate compares a test's strength with its criterion.

A criterion is only as good as the mutant its test can fail on. Three of this sprint's four rejections were tests asserting a WEAKER claim than the criterion above them - present rather than exactly-one, a synthetic fixture rather than the corpus, an equality an empty result also satisfies. All were green from the day they were written, so no run could have surfaced them; only reading each test back against its criterion did.

Recorded from retro RETRO0099.

## L-0325: **A fixed line number in a fixture family probes past the end of the short ones.** Every severity fixture shared a probe line, and the

- **Added:** 2026-08-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a rule: a fixed probe line across a fixture family reads past the short ones. The severity-fixture example is no longer in the tree (a grep for the `module level` fallback found only unrelated code comments), and `best-practices/testing.md:108` is the nearest guidance. No gate detects a shared probe constant across fixtures.

**A fixed line number in a fixture family probes past the end of the short ones.** Every severity fixture shared a probe line, and the short one returned `module level` - a different wrong answer wearing the same green tick. The line travels with the body now.

Recorded from retro RETRO0098.

## L-0324: **A criterion whose premise is not decidable from what is stored gets satisfied by a fixture.** US0661 AC4 demanded that a registered claim

- **Added:** 2026-08-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a rule though the instance is gone: the registered-versus-measured mutant join named in US0661 AC4 died with the ledger (`mutation.py:32`, US0936). A criterion whose premise is not decidable from what is stored is still satisfied by a fixture; `best-practices/testing.md:108` ('A fixture shape the product cannot produce') is the nearest guidance and no gate holds it.

**A criterion whose premise is not decidable from what is stored gets satisfied by a fixture.** US0661 AC4 demanded that a registered claim be caught disagreeing with a measurement. A registered mutant is the author's prose and a measured one is the generator's fault class; the two join on nothing. The criterion was narrowed to what the ledger can decide and the rest filed - because the alternative was a check that refuses on a comparison nobody can make.

Recorded from retro RETRO0098.

## L-0323: **A repair relocates its defect one construct over, and the second construct is the one nobody checks.** The terminality rule learned If

- **Added:** 2026-08-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a general rule: a repair relocates its defect one construct over. The instance's code (the terminality rule) is no longer in the tree (`mutation.py` retired the mutation-evidence ledger, US0936), but `critic.py:2471-2474` requires a repair review to rule each prior finding CLOSED, OVER-CLAIMED or MOVED, and a MOVED defect counts as open (`repair_open_findings`, `critic.py:3652`). The other-side fixture is not gated.

**A repair relocates its defect one construct over, and the second construct is the one nobody checks.** The terminality rule learned If, Try, With and `while True` in round one, and was still wrong about `for`/`else`, `match`, `async with`, an inner loop's `break`, and a `break` that jumps past the `else`. Five rounds of one rule. Widening a rule is not the same as making it right, and the test for the difference is a fixture on the OTHER side - bodies that genuinely DO have the property, or the rule can be widened until it claims everything.

Recorded from retro RETRO0098.

## L-0322: **A registered mutant is a claim; clear the ledger and apply them before believing the count.** 61 registrations, 47 applied for real, two

- **Added:** 2026-08-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true for the claim, and its ledger form is gone: `mutation.py` retired `register`, `retract`, `retractions` and `audit` (`RETIRED_VERBS`, `mutation.py:2142`; US0936) so there is no registered count to clear. What remains is the author's recorded mutants, which `critic.py` `check_self_check` (`critic.py:2915`) admits as claims and `critic.py:2475-2483` has the reviewer apply. Apply them before believing a count; no gate does.

**A registered mutant is a claim; clear the ledger and apply them before believing the count.** 61 registrations, 47 applied for real, two survivors the paperwork called kills. Register AFTER the last edit to a file, and only from a script that applies, runs, restores and registers on a genuine red. (LL0053)

Recorded from retro RETRO0098.

## L-0321: **L-0314: a guard that fails in the direction of inventing work is still wrong.** The resolvability sweep inherited the runner's working

- **Added:** 2026-08-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: `verify_ac.py` `selector_resolves(expr, cwd=None)` (`verify_ac.py:868`) takes the working directory explicitly and returns None, not False, for a selector it cannot resolve this way (`:876`), so a sweep no longer invents work from the runner's directory. A new sweep inheriting the cwd is not checked by any gate.

**L-0314: a guard that fails in the direction of inventing work is still wrong.** The resolvability sweep inherited the runner's working directory and answered False for selectors that resolve perfectly well.

Recorded from retro RETRO0097.

## L-0320: **L-0313: an emergency bypass is a debt due on the NEXT commit.** Three lanes had been failing behind one `--no-verify`; the gate that

- **Added:** 2026-08-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated at the push: `--no-verify` is the sole bypass (AGENTS.md:60), and the pre-push hook runs the boundary gate over the pushed range (`gate.py:135`, `:362`) with the full suite once (`gate.py:878`), so lanes that failed behind a bypass surface at the next push. The next-commit timing is guidance; only the push is gated.

**L-0313: an emergency bypass is a debt due on the NEXT commit.** Three lanes had been failing behind one `--no-verify`; the gate that would have said so was the thing being bypassed.

Recorded from retro RETRO0097.

## L-0319: **L-0312: a fixture whose root is a PARAMETER will eventually be given the wrong one.** Writing to a real path looks exactly like writing

- **Added:** 2026-08-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and partly guarded: `test_transition.py:53-80` (`_refuse_working_tree`) refuses a fixture root that is a checkout, by four relations, and `mutation.py` `window` (`mutation.py:2014` `cmd_window`) refuses a concurrent rewrite. A fixture whose root is a parameter in any other test module is not guarded; no gate scans for a real-path write.

**L-0312: a fixture whose root is a PARAMETER will eventually be given the wrong one.** Writing to a real path looks exactly like writing to a temp path until somebody checks what changed - and the thing destroyed was gitignored, so git could not restore it.

Recorded from retro RETRO0097.

## L-0318: **L-0311: a repair judged only against its own finding can void the guarantee beside it.** Round 2 must re-run the SIBLING unit's mutants

- **Added:** 2026-08-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a repair judged only against its own finding can void the guarantee beside it. `critic.py:2471-2474` makes a repair review rule each prior finding CLOSED, OVER-CLAIMED or MOVED, and `:2484-2487` asks for regression cover on the repair. AGENTS.md:98-101 bounds a review to the unit's own diff, so re-running a sibling unit's mutants is not gated and rests on the reviewer.

**L-0311: a repair judged only against its own finding can void the guarantee beside it.** Round 2 must re-run the SIBLING unit's mutants, not just the repaired one's. Two mutants silently stopped being lethal here and nothing in the suite noticed.

Recorded from retro RETRO0097.

## L-0317: **L-0310: a criterion asking for ONE implementation cannot be verified by two agreeing.** Agreement is what two correct-today

- **Added:** 2026-08-07
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: two agreeing implementations satisfy a criterion that forbids duplication. `critic.py:2475-2478` names it (a shape list where two implementations agree by construction passes every mutant), and the structural fix (patch the shared routine, require every reader to move) is the practice behind `best-practices/testing.md:92-96`. No gate detects an agreement-only assertion.

**L-0310: a criterion asking for ONE implementation cannot be verified by two agreeing.** Agreement is what two correct-today implementations produce by construction, so the assertion is satisfied by the exact duplication the criterion forbids. This produced a FALSE `killed` in the mutation ledger - on the instrument whose own bug this was - and then produced it a second time in the same run on a different unit. The shape that works is structural: patch the shared routine and require every reader to move with it.

Recorded from retro RETRO0097.

## L-0316: **The seat that reviews the plan should not be the one that trusts the author's mutation results.** Both seats independently re-derived the

- **Added:** 2026-08-06
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: mutation results are claims until somebody else runs them. `critic.py:2475-2483` has a fresh reviewer mutate the author's tests and `:2488` demands an isolated checkout; `critic.py` `check_self_check` (`critic.py:2915`) records the author's mutants as claims (killed or survived) but cannot prove they were applied. The plan-seat versus mutation-seat split is not enforced.

**The seat that reviews the plan should not be the one that trusts the author's mutation results.** Both seats independently re-derived the author's claims, and two of them were false: a mutant asserted killed had survived 2,137 tests, and a criterion's own rationale was factually wrong about the engine it described. Mutation results are claims until somebody else runs them.

Recorded from retro RETRO0096.

## L-0315: **A guard that reports the symptom and not the cause costs a day the first time and a command the second.** BG0528 was filed at the

- **Added:** 2026-08-06
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and repaired at its site: `sprint.py` `undelivered_blockers` (`sprint.py:6964`) asks first whether a unit's code landed with its status unmoved, so the cause is named before the downstream consequences, and it is now rung-aware. BG0528 is Fixed. The general rule (report the cause, not only the symptom) has no gate for new guards.

**A guard that reports the symptom and not the cause costs a day the first time and a command the second.** BG0528 was filed at the previous close, when twenty blockers named review coverage, sign-off and Done gates while the real fault was eight units still at `Ready`. It reproduced here exactly - and cost one command, because the message named it. Filing the diagnosis gap was worth more than fixing the instance.

Recorded from retro RETRO0096.

## L-0314: **A retraction written only in prose is not a retraction.** US0632's AC3 was narrowed on a false premise, and correcting it in a comment

- **Added:** 2026-08-06
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: write the retraction where the machine looks. `transition.py` `_done_verify_gate` (`transition.py:152`) reads the recorded verifier result and `Verified` marker, so prose elsewhere does not retract; the repair is a criterion with no verifier, reported unverified by `verify_ac.py`. No gate detects a prose-only retraction beside a marker; a reviewer reading the claim finds it.

**A retraction written only in prose is not a retraction.** US0632's AC3 was narrowed on a false premise, and correcting it in a comment block left `**Verified:** yes` on the line the tooling reads - `verify_ac` re-stamped it green from a test that does not exercise the property, so every mechanical reader still saw the criterion met. Setting the marker by hand did not survive either. The honest fix was to split the undelivered limb into a criterion with NO verifier, so the tool reports it unverified because it is. Write the retraction where the machine looks, or it has not happened.

Recorded from retro RETRO0096.

## L-0313: **The seat that reviews the plan should not be the one that trusts the author's mutation results.** Both seats independently re-derived the

- **Added:** 2026-08-06
- **Review-by:** 2026-11-04

**The seat that reviews the plan should not be the one that trusts the author's mutation results.** Both seats independently re-derived the author's claims, and two of them were false: a mutant asserted killed had survived 2,137 tests, and a criterion's own rationale was factually wrong about the engine it described. Mutation results are claims until somebody else runs them.

Recorded from retro RETRO0096.

- **Status:** Closed - Duplicate of L-0316, which carries the identical plan-seat and mutation-results claim and stays open.

## L-0312: **A guard that reports the symptom and not the cause costs a day the first time and a command the second.** BG0528 was filed at the

- **Added:** 2026-08-06
- **Review-by:** 2026-11-04

**A guard that reports the symptom and not the cause costs a day the first time and a command the second.** BG0528 was filed at the previous close, when twenty blockers named review coverage, sign-off and Done gates while the real fault was eight units still at `Ready`. It reproduced here exactly - and cost one command, because the message named it. Filing the diagnosis gap was worth more than fixing the instance.

Recorded from retro RETRO0096.

- **Status:** Closed - Duplicate of L-0315, which carries the identical symptom-versus-cause claim and stays open.

## L-0311: **A retraction written only in prose is not a retraction.** US0632's AC3 was narrowed on a false premise, and correcting it in a comment

- **Added:** 2026-08-06
- **Review-by:** 2026-11-04

**A retraction written only in prose is not a retraction.** US0632's AC3 was narrowed on a false premise, and correcting it in a comment block left `**Verified:** yes` on the line the tooling reads - `verify_ac` re-stamped it green from a test that does not exercise the property, so every mechanical reader still saw the criterion met. Setting the marker by hand did not survive either. The honest fix was to split the undelivered limb into a criterion with NO verifier, so the tool reports it unverified because it is. Write the retraction where the machine looks, or it has not happened.

Recorded from retro RETRO0096.

- **Status:** Closed - Duplicate of L-0314, which carries the identical retraction-in-prose claim and stays open.

## L-0310: **The seat that reviews the plan should not be the one that trusts the author's mutation results.** Both seats independently re-derived the

- **Added:** 2026-08-06
- **Review-by:** 2026-11-04

**The seat that reviews the plan should not be the one that trusts the author's mutation results.** Both seats independently re-derived the author's claims, and two of them were false: a mutant asserted killed had survived 2,137 tests, and a criterion's own rationale was factually wrong about the engine it described. Mutation results are claims until somebody else runs them.

Recorded from retro RETRO0096.

- **Status:** Closed - Duplicate of L-0316, which carries the identical plan-seat and mutation-results claim and stays open.

## L-0309: **A guard that reports the symptom and not the cause costs a day the first time and a command the second.** BG0528 was filed at the

- **Added:** 2026-08-06
- **Review-by:** 2026-11-04

**A guard that reports the symptom and not the cause costs a day the first time and a command the second.** BG0528 was filed at the previous close, when twenty blockers named review coverage, sign-off and Done gates while the real fault was eight units still at `Ready`. It reproduced here exactly - and cost one command, because the message named it. Filing the diagnosis gap was worth more than fixing the instance.

Recorded from retro RETRO0096.

- **Status:** Closed - Duplicate of L-0315, which carries the identical symptom-versus-cause claim and stays open.

## L-0308: **A retraction written only in prose is not a retraction.** US0632's AC3 was narrowed on a false premise, and correcting it in a comment

- **Added:** 2026-08-06
- **Review-by:** 2026-11-04

**A retraction written only in prose is not a retraction.** US0632's AC3 was narrowed on a false premise, and correcting it in a comment block left `**Verified:** yes` on the line the tooling reads - `verify_ac` re-stamped it green from a test that does not exercise the property, so every mechanical reader still saw the criterion met. Setting the marker by hand did not survive either. The honest fix was to split the undelivered limb into a criterion with NO verifier, so the tool reports it unverified because it is. Write the retraction where the machine looks, or it has not happened.

Recorded from retro RETRO0096.

- **Status:** Closed - Duplicate of L-0314, which carries the identical retraction-in-prose claim and stays open.

## L-0307: A fixture that always supplies the thing under test hides the refusal that depends on its absence

- **Added:** 2026-08-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a fixture that always supplies the thing under test hides the refusal that depends on its absence. The brief-provenance interlock still exists (`critic.py:119` 'unbriefed' rows, `critic.py:864` the matched-fingerprint rule), and `best-practices/testing.md:108` lists 'A fixture shape the product cannot produce'. No gate checks each fixture family has an absent-value case.

A fixture that always supplies the thing under test hides the refusal that depends on its absence. Every panel test supplied a brief fingerprint, so the brief-provenance interlock went unpinned until a mutant deleted it and nothing reddened.

Recorded from retro RETRO0095.

## L-0306: A sample drawn from the head of a sorted corpus is not a sample of the corpus

- **Added:** 2026-08-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a head-of-corpus sample is not a sample. `triage_sampling.py` `sample` (`triage_sampling.py:76-100`) ranks the whole pool by a stable hash rather than taking the head. No gate stops a new estimator being validated on a sorted head; nearest guidance is AGENTS.md:98-101 (decide by execution over the corpus, not by impression).

A sample drawn from the head of a sorted corpus is not a sample of the corpus. Sixty bugs taken by id banded 60 of 60 the same way and reported a working gate as degenerate; the same estimator over a strided sample of the whole corpus returned four distinct bands.

Recorded from retro RETRO0095.

## L-0305: Widening a table by INSERTING a column shifts every historical row; appending one does not

- **Added:** 2026-08-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a rule and repaired for the case named: the velocity history is parsed by column name, not position (`retro.py:934` comment, `:944` `VELOCITY_COLUMNS`, `_velocity_index` `retro.py:2212`), and `Written` is documented as 'ADDED, never back-filled'. Any other positional table still shifts historical rows on insertion; no gate checks writer, header and reader agree.

Widening a table by INSERTING a column shifts every historical row; appending one does not. Adding `Written` to VELOCITY.md's header alone made the estimate column read back the actual, because the schema is written out three times - header, row writer, reader - with nothing making them agree.

Recorded from retro RETRO0095.

## L-0304: An absent value and a defaulted one must be distinguishable in the record, or a rule applied later reinterprets history

- **Added:** 2026-08-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and visible in code: absent is kept distinct from defaulted. `conformance.py` `tier_covers` (`conformance.py:382-400`) treats 'no recorded tier' as its own answer, `retro.py:934-943` (the velocity column comment) reads a row without a column as unrecorded rather than assumed, and `critic.py` `record_self_check` writes `-` for no author. No gate checks a new column does the same.

An absent value and a defaulted one must be distinguishable in the record, or a rule applied later reinterprets history. The tier column reads `-` for absent rather than `full`, and the capacity column never reads `seat` for a row that predates it - in both cases the unsafe direction is a claim nobody made being attributed to somebody.

Recorded from retro RETRO0095.

## L-0303: A guard whose deletion changes no behaviour is dead code, however reasonable it reads

- **Added:** 2026-08-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a guard whose deletion changes no behaviour is dead code. `mutation.py` `FAULT_CLASSES` (`mutation.py:50`, including `invert-guard`) is the instrument that applies the deletion, and `mutation.py:35` says plainly that 'No gate lane reads a mutation run'. `conformance.py` `tier_covers` (`conformance.py:382`) is the cited guard and remains. No gate runs the deletion automatically.

A guard whose deletion changes no behaviour is dead code, however reasonable it reads. This sprint filed exactly that defect against `gate.py:3170` while planning, and then wrote one into `conformance.tier_covers` six hours later; only mutation caught it. Apply the deletion, not the reasoning.

Recorded from retro RETRO0095.

## L-0302: **Fixing the instance leaves the class.** BG0500 added `runbook.py` to the AGENTS.md lane roster; four commits later the same batch shipped

- **Added:** 2026-08-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true in general and repaired at the site: AGENTS.md no longer carries a lane roster at all, it points at `.githooks/pre-commit --list` and `.githooks/commit-msg --list` (AGENTS.md:73-77), each lane read from the hook's own `run` calls, which is the derive-from-source repair this lesson named. The general rule (fixing the instance leaves the class) has no gate; a restated roster elsewhere would be found by review.

**Fixing the instance leaves the class.** BG0500 added `runbook.py` to the AGENTS.md lane roster; four commits later the same batch shipped a `warning-ratchet` lane and did not. The repair was to derive the roster from the hook, one subtest per lane, so lane fourteen fails when it is written rather than when a reviewer notices.

Recorded from retro RETRO0094.

## L-0301: **Reviewing the test costs two orders of magnitude less than reviewing the code.** Measured this run, by accident, on the first hand-run

- **Added:** 2026-08-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: reviewing the test plan is far cheaper than reviewing the code. The `test-spec` type ships (`sdlc-studio/test-specs/`, 3 specs) and `best-practices/testing.md:92-96` is the guidance. No gate requires a reviewed test plan before code; the measured cost figures are history and are not re-measured here.

**Reviewing the test costs two orders of magnitude less than reviewing the code.** Measured this run, by accident, on the first hand-run use of EP0207's mechanism: an independent seat rejected all three rows of US0629's test plan for 55k tokens and 3 minutes. The batch-boundary review that caught the same class - verifiers that cannot fail on what they claim - cost roughly 400k tokens and two hours, after the code had shipped.

Recorded from retro RETRO0094.

## L-0300: **A mutant derived from the implementation is the mutant the test was built to catch.** Five AC-named mutants did not kill their tests, on

- **Added:** 2026-08-05
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a mutant derived from the implementation is the one the test was built to catch. `best-practices/testing.md:92-96` states the rule (state the mutant in the test's docstring before writing the test) and `critic.py:2475-2478` has the reviewer mutate the tests; `critic.py` `check_self_check` (`critic.py:2915`) requires the author to list mutants against a declared test file. Whether a mutant came from the criterion is not gated.

**A mutant derived from the implementation is the mutant the test was built to catch.** Five AC-named mutants did not kill their tests, on units committed claiming they had. The generative defect was writing each mutant AFTER the code, from the code. The criterion already stated the mutant in every case - US0468 AC2 literally says "a key added or renamed fails the test" - and the test was written from the implementation instead. Derive the mutant from the criterion before the code exists, or the mutation check certifies nothing. (LL0044, L-0272.)

Recorded from retro RETRO0094.

## L-0299: A file-disjoint unit is not necessarily an independent one

- **Added:** 2026-08-04
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and partly gated: `refine.py` `seam_declarations` (`refine.py:960`) and `seam_findings` (`refine.py:1040`) report declared couplings between units that share no file. An undeclared coupling (a criterion reading what another unit creates, a registry each verb must join) is not detected and rests on the reviewer.

A file-disjoint unit is not necessarily an independent one. Three couplings in this epic were invisible to a seam check: criteria that read what another unit creates, a guard requiring each verb to document itself, and a shared registry every verb must declare into.

Recorded from retro RETRO0093.

## L-0298: A mutant that removes ONE of two sufficient fixes measures less than it appears to

- **Added:** 2026-08-04
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a mutant removing one of two sufficient fixes survives and reads as coverage. `critic.py:2479-2483` tells the reviewer to re-test a survivor's branch in isolation and `best-practices/testing.md:92-96` has the author name the production change; no gate or tool (`mutation.py` is an instrument, `mutation.py:35`) derives the honest multi-fix mutant.

A mutant that removes ONE of two sufficient fixes measures less than it appears to. The honest mutant reproduces the exact state that shipped; a partial one survives and reads as coverage.

Recorded from retro RETRO0093.

## L-0297: A stub is not the shipped entry point

- **Added:** 2026-08-04
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a stub is not the shipped entry point. `best-practices/testing.md:66-90` (entry point) and `:106` ('Bypassing the surface under test', a hand-built `argparse.Namespace`) hold it as guidance, and AGENTS.md:122 requires each claim run through the shipped entry point. `verify_ac.py` `lane_check` (`:1331`) flags only library-only verifiers and is advisory.

A stub is not the shipped entry point. A verifier that monkeypatches the collaborator under test proves the call happened and cannot see that it failed - which is how a verb that tracebacked on every invocation passed the suite, verify_ac, the lane-check and the gate.

Recorded from retro RETRO0093.

## L-0296: Satisfying a gate is not the same as satisfying the criterion, and when the two pull apart the criterion wins

- **Added:** 2026-08-04
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: when the gate and the criterion pull apart, the criterion wins. AGENTS.md:92-96 makes the criteria 'law' in the brief that `critic.py brief` carries, and a lane-check flag (`verify_ac.py:1331`) is advisory so clearing it is not the goal. No gate compares a moved verifier with the criterion's original claim.

Satisfying a gate is not the same as satisfying the criterion, and when the two pull apart the criterion wins. Two rejections in this run were caused by moving a verifier to clear a lane-check, each time onto ground where the criterion's own gap was invisible.

Recorded from retro RETRO0093.

## L-0295: Two readers of one file will disagree eventually, and the second one is written by whoever did not know the first existed

- **Added:** 2026-08-04
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: two readers of one file drift. The tree records the fix by sharing one reader, e.g. the velocity table parsed once by column name (`retro.py:944` `VELOCITY_COLUMNS`, `_velocity_index` `retro.py:2212`) and the single coverage authority noted at `critic.py:2240`. No gate detects a second reader added by someone unaware of the first.

Two readers of one file will disagree eventually, and the second one is written by whoever did not know the first existed. Both defects this run introduced were that shape.

Recorded from retro RETRO0092.

## L-0294: A ceiling you guessed is a ceiling that passes both cases

- **Added:** 2026-08-04
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a guessed ceiling passes both cases. `tools/check_budgets.py` (`record_ceilings`, `tools/check_budgets.py:136`) now rewrites ceilings to measured sizes with headroom (`:63`), so the budget case is held by measurement. The general rule for a test's own pinned bound has no gate; `best-practices/testing.md:92-96` (name the mutant first) is the guidance.

A ceiling you guessed is a ceiling that passes both cases. The first draft of the cache pin used a round number and survived its own mutant; measuring the two bounds (157 cached, 283 uncached) is what made it discriminate.

Recorded from retro RETRO0092.

## L-0293: A postcondition cannot express an ordering

- **Added:** 2026-08-04
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a postcondition cannot express an ordering, so an ordering claim needs the write path observed. `best-practices/testing.md:113` ('A positive control already passing') and `critic.py:2475-2478` (the reviewer mutates the tests) are the only holds; no gate checks that a test of a refusal-first claim observes the attempts rather than their aftermath.

A postcondition cannot express an ordering. "Nothing landed" holds equally when every write was attempted and every write failed; if the claim is that the refusal arrives FIRST, the write path has to be observed, not its aftermath.

Recorded from retro RETRO0092.

## L-0292: A test that opens the mechanism itself proves the mechanism and never its CALLER

- **Added:** 2026-08-04
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and visible in the tree: `reconcile.py` `detect_all` (`reconcile.py:2419`) opens `sdlc_md.corpus_cache()` itself (`:2438`), as do `unit_corpus` (`:1980`) and `settle` (`:3386`), so the wrapper is the caller. The general rule (a test that opens the mechanism proves the mechanism, never its caller) is `best-practices/testing.md:111` ('Testing the helper, not the caller'); no gate checks a test enters via the caller.

A test that opens the mechanism itself proves the mechanism and never its CALLER. Eleven tests each opened `corpus_cache()` inside their own fixture, so neutering the production wrapper in `reconcile.detect_all` left every one of them passing. The caller is the part a fixture-built sweep cannot see.

Recorded from retro RETRO0092.

## L-0291: **A guard reddening a fixture is evidence about the fixture as often as about the guard.** Seven rolling tests went red because they never

- **Added:** 2026-08-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a red fixture is evidence about the fixture as often as the guard. `best-practices/testing.md:108` lists 'A fixture shape the product cannot produce' as a vacuity mechanism, and `test_transition.py:53-80` (`_refuse_working_tree`) is a guard whose fixtures had to be made realistic. No gate classifies a red as fixture-side or guard-side; that is the reviewer's judgement.

**A guard reddening a fixture is evidence about the fixture as often as about the guard.** Seven rolling tests went red because they never committed their delivered work - a state no real close reaches. The guard was right; the fixtures were unrealistic, and had been for as long as they had existed.

Recorded from retro RETRO0091.

## L-0290: **Fixing the row an operator does not read is not fixing it.** `US0624` changed a checklist resolver while the preflight - the command an

- **Added:** 2026-08-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: fixing the row an operator does not read is not fixing it. AGENTS.md:122 and `best-practices/testing.md:66-90` require driving the command the criterion names, and `verify_ac.py` `lane_check` (`verify_ac.py:1331`) reports a unit whose verifiers never enter the command. The lane check is advisory, so a criterion verified through a private function can still pass.

**Fixing the row an operator does not read is not fixing it.** `US0624` changed a checklist resolver while the preflight - the command an operator actually runs - built its coverage line through an entirely different path, and the criterion's own verifier called the private function rather than the shipped one. A criterion that names a command must be driven through that command, or it certifies the wrong thing convincingly.

Recorded from retro RETRO0091.

## L-0289: **A matching rule that is convenient is a gate that is optional.** The repair record's closure-to-finding match was bidirectional substring

- **Added:** 2026-08-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and repaired at its site: the repair record's matching is now exact. `critic.py` `validate_repair_verdict` (`critic.py:3634`) looks each prior finding up by its own key and raises on an unruled one ('never taken as closed'), and `repair_open_findings` (`critic.py:3652`) counts anything not CLOSED as open. The general rule (a rule that decides a gate resolves to one answer) has no gate beyond review.

**A matching rule that is convenient is a gate that is optional.** The repair record's closure-to-finding match was bidirectional substring because that was forgiving to write against. It made a one-character closure close every finding, which turned the review gate into a formality reachable from the command line. Where a rule decides whether a gate opens, it must resolve to exactly one answer and refuse ambiguity rather than resolving it in the author's favour.

Recorded from retro RETRO0091.

## L-0288: **A mechanism verified only in fixtures is verified only in fixtures.** Two of this sprint's own deliveries were inert on the real

- **Added:** 2026-08-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a mechanism verified only in fixtures is verified only in fixtures. `best-practices/testing.md:10-18` ('Production-state-shape integration tests') and AGENTS.md:122 (exercise each claim through the shipped entry point) hold it as guidance; `critic.py brief` is refused until the author records that pass (`review.author_self_check: block`, `critic.py:2915` `check_self_check`), which makes the pass compulsory but does not judge its quality.

**A mechanism verified only in fixtures is verified only in fixtures.** Two of this sprint's own deliveries were inert on the real repository while every fixture passed, and in both cases the fixture differed from production in one detail nobody had thought about - a `.gitignore` line, and a test that stamped the value it was meant to observe. Run the new thing against the tree it ships into, and assert the OUTPUT is non-empty rather than that two computations agree, because two empty answers agree perfectly.

Recorded from retro RETRO0091.

## L-0287: **A cascade that ticks a checkbox is not a status cascade.** `_cascade_epic` ticks the story's line in its parent's Story Breakdown and

- **Added:** 2026-08-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and repaired where it was found: `reconcile.py` now detects `epic-status-stale` (`reconcile.py:85` the kind, `:1084` the detector, `:3277` its repair), the direction that masks finished work. The general rule (a cascade that ticks a box is not a status cascade) rests on `_cascade_epic`; no gate asserts a new cascade moves the parent's Status.

**A cascade that ticks a checkbox is not a status cascade.** `_cascade_epic` ticks the story's line in its parent's Story Breakdown and returns; it never touches the parent's Status. Fifteen of thirty open epics have every child Done and every box ticked and still read Draft, and `reconcile detect` reports `drift_items=0` over all of them. The direction that masks unfinished work was detected; the direction that masks finished work was not, so a delivery backlog can be overstated by half and nothing says so - `BG0503`, now the `epic-status-stale` kind. Clearing it showed the overstatement was not confined to the epic layer: closing the fifteen made 29 requests derivable, and Discovery fell 60 to 31, Delivery 106 to 89.

Recorded from retro RETRO0090.

## L-0286: **An operation the tooling advises on every run, and that nobody can commit, accumulates silently and is invisible in the advisory

- **Added:** 2026-08-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the advisory reports state, not whether its remedy works. `reconcile.py:403-425` still emits the archive advice ('Advisory only: it never blocks and never runs the archive', `reconcile.py:410`) and `status.py:820` lists it. Nothing exercises the remedy the advisory prints, so a blocked remedy accumulates silently; the practice is AGENTS.md:122 (exercise each claim through the entry point).

**An operation the tooling advises on every run, and that nobody can commit, accumulates silently and is invisible in the advisory itself.** Five indexes reached 6-15x their threshold while `reconcile detect` printed the remedy every time. The advisory reported the state correctly and could not report that taking its own advice was blocked, which is why the debt grew rather than being paid. Exercise the remedy an advisory prints, not just the detector that prints it.

Recorded from retro RETRO0090.

## L-0285: **A guard that reads the live index treats "what nobody has archived yet" as the corpus.** Both failing guards asserted floors - `> 150`

- **Added:** 2026-08-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a floor calibrated against the live, unarchived index tracks the snapshot. The archive advisory still fires on live terminal rows (`reconcile.py:403-425`, `DEFAULT_ARCHIVE_AFTER`) and the index census unions archive sub-index rows (`reconcile.py:370`, `_merge_archive_rows`), so census floors are best set on the union. No gate checks a guard's floor against the corpus population.

**A guard that reads the live index treats "what nobody has archived yet" as the corpus.** Both failing guards asserted floors - `> 150` rows, `> 100` epics - that exist to prove the sweep is not silently matching nothing. Calibrated against an unarchived snapshot, the floor tracks the snapshot rather than the corpus, so the guard reddens on a maintenance step instead of on a defect. The population, not the number, is what needed fixing.

Recorded from retro RETRO0090.

## L-0284: **A mutation-killed test proves the test can fail, not that production takes that path.** `US0604` needed four rounds

- **Added:** 2026-08-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a mutation-killed test does not prove production takes the path. `best-practices/testing.md:66-90` (name the entry point) and `:106` ('Bypassing the surface under test') hold it as guidance, and `critic.py:2475-2478` has the reviewer mutate the author's tests. No gate checks a fixture reaches a state the shipped command produces.

**A mutation-killed test proves the test can fail, not that production takes that path.** `US0604` needed four rounds. Each repair was mutation-verified and each was wrong one layer out, because the fixture handed the code a state the shipped command never produces. Killing the mutant you thought of is necessary and nowhere near sufficient: drive the entry point, or the test is measuring a path nobody walks.

Recorded from retro RETRO0089.

## L-0283: **A review exists when the ledger says so, not when it happened.** Fifteen of this run's verdicts were produced and never recorded, and

- **Added:** 2026-08-03
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held by construction: every downstream gate reads the ledger, so an unrecorded verdict is no verdict. `critic.py` `coverage_state` (`critic.py:2235`) reads only recorded rows and `sprint.py` `review_coverage` (`sprint.py:5345`) counts only ledger or frozen-batch cover, with a self-review covering nothing. 'Record the verdict in the same breath' is guidance; no gate catches a verdict produced and never recorded.

**A review exists when the ledger says so, not when it happened.** Fifteen of this run's verdicts were produced and never recorded, and twenty units were never reviewed at all, while the run's own account claimed 38 reviewed. Every gate downstream reads the ledger, so an unrecorded pass is indistinguishable from no pass - correctly, and expensively. Record the verdict in the same breath as forming it, or do not count it.

Recorded from retro RETRO0089.

## L-0282: **An advisory detector that fires on the author changes nothing.** `lane-check`'s yield is no longer a question: 7 flagged, 6 independently

- **Added:** 2026-08-02
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py` `lane_check` (`verify_ac.py:1331`) is advisory, and a grep of every script and tool found no gate lane, `critic.py` or `sprint.py` caller of it, so a flag on the author changes nothing until a reviewer acts on it. Its yield is recorded to `verify_ac.py:3182` (`_LANE_YIELD_REL`). `best-practices/testing.md:81-84` describes the same advisory.

**An advisory detector that fires on the author changes nothing.** `lane-check`'s yield is no longer a question: 7 flagged, 6 independently confirmed hollow. That is the number `CR0520` asked for.

Recorded from retro RETRO0089.

## L-0281: **"Broken" and "unproven" are different facts and want different words.** Roughly 13 of the 27 rejections were a feature that does not

- **Added:** 2026-08-02
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: broken and unproven are different facts. `critic.py` records a verdict of APPROVE or REJECT only (`critic.py:31-33`, `VERDICTS`), so a REJECT still carries both meanings; the distinction rests on the finding text. No gate separates them (CR0524 named the fix); the brief's claim inventory marks an unrunnable claim UNVERIFIABLE rather than FALSE (`critic.py:2542-2550`), which is the nearest mechanism.

**"Broken" and "unproven" are different facts and want different words.** Roughly 13 of the 27 rejections were a feature that does not work; roughly 14 were a correct feature with evidence that cannot fail. One verdict carried both, so the count read as catastrophe and gave no signal about which repairs were urgent. `CR0524`.

Recorded from retro RETRO0089.

## L-0280: **Reviewing the test is cheaper than reviewing the code.** This run spent five adversarial passes and roughly 800k tokens to discover

- **Added:** 2026-08-02
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and the artefact now ships: the `test-spec` type exists (`sdlc-studio/test-specs/` holds 3 specs) and `best-practices/testing.md:92-96` ('Name the mutant BEFORE writing the test') is the rule. Nothing gates writing a spec before code, so a plan reviewed before code is still the author's choice.

**Reviewing the test is cheaper than reviewing the code.** This run spent five adversarial passes and roughly 800k tokens to discover, after the fact, that ~14 verifiers could not fail. A reviewed test plan would have found the same thing before a line of code. The `test-spec` artefact type and the name-the-mutant-first rule ALREADY SHIP; the repository contains two test specs and this run wrote none. `CR0525`.

Recorded from retro RETRO0089.

## L-0279: **A test that asserts the shape of a change cannot fail when the change is deleted.** The weakness was not random: it clustered at the end

- **Added:** 2026-08-02
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a shape-asserting test survives deletion of the change. `best-practices/testing.md:107` lists 'Asserting text the code supplies for free' (a `def` line satisfying `assertIn`) as a vacuity mechanism, and `critic.py:2475-2478` tells the reviewer to mutate the author's tests. No gate runs a mutation over an author's new tests.

**A test that asserts the shape of a change cannot fail when the change is deleted.** The weakness was not random: it clustered at the end of units, where the feature already worked and the test felt like paperwork. `grep -q "NOT FINISHED"` exits 0 against an unreachable print; `assertIn("attribute_kill(", src)` is satisfied by the `def` line. Both shipped.

Recorded from retro RETRO0089.

## L-0278: Two copies of a rule drift apart: the coverage rule was restated in three modules and this diff falsified all three at once

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held for the instance: the review-coverage rule has one authority, `critic.py` `coverage_state` (`critic.py:2235`), which `sprint.py:5605`, `transition.py:897` and `sprint_report.py:1158` and `:1742` (via `coverage_counts`) all call. The general rule (two copies drift) has no gate; a new restatement of any rule is found by review.

Recorded from retro RETRO0088.

## L-0277: Reading a command's verdict through a pipe reports the pipe's status

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a pipe reports the last command's status, and L-0352 records it being read and not followed. no gate holds it for ad-hoc shell. `best-practices/script.md:25` and `:125` require `set -euo pipefail` in scripts, and `tools/remote-gate.sh:303` reads `PIPESTATUS[1]` correctly, but a hand-run `cmd | tail; echo $?` is unchecked.

Reading a command's verdict through a pipe reports the pipe's status. Redirect, then echo the code separately.

Recorded from retro RETRO0088.

## L-0276: A premise measured on one instance is an anecdote

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a premise measured on one instance is an anecdote. no gate holds it; the nearest guidance is AGENTS.md:98-101, which settles regression versus pre-existing by execution (`git log -S`) rather than impression. `triage_sampling.py` `sample` (`triage_sampling.py:76`) is one place the rule is honoured, sampling the whole pool by hash.

A premise measured on one instance is an anecdote. Replay it over the corpus before building on it.

Recorded from retro RETRO0088.

## L-0275: A review that fails every unit carries the same information as one that passes every unit

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a review that rejects everything says nothing. The brief bounds a review to the unit's own `Affects` against the base ref (AGENTS.md:98-101, delivered by `critic.py brief`), and only a regression or newly introduced defect blocks. That bound is guidance in the brief; no gate measures a reviewer's reject rate.

A review that fails every unit carries the same information as one that passes every unit. Bounding the scope is what makes a REJECT mean something.

Recorded from retro RETRO0088.

## L-0274: A library test cannot see a missing lane: the wiring between entry point and function is exactly the part it does not exercise, and it is

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held where it can be: `best-practices/testing.md:66-90` ('Name the ENTRY POINT before writing the test') states the rule, and `verify_ac.py` `lane_check` (`verify_ac.py:1331`, `lane-check` verb) reports a unit whose verifiers never enter the command. It is advisory (no other script calls it), so an unflagged missing lane is caught only by the reviewer.

A library test cannot see a missing lane: the wiring between entry point and function is exactly the part it does not exercise, and it is where this defect class lives. State the ENTRY POINT a test enters through before writing it.

Recorded from retro RETRO0088.

## L-0273: **Stopping is a delivery decision, and it is cheaper than half-building.** BG0448 was left untouched rather than part-built, because its

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a delivery rule: no gate holds it, and no script or doc line was found that states it (a grep of the skill docs for part-built or half-delivered wording found none). It rests on operator judgement; the nearest guidance is AGENTS.md:83, which makes work a story or bug with criteria before a diff exists.

**Stopping is a delivery decision, and it is cheaper than half-building.** BG0448 was left untouched rather than part-built, because its half-delivered form is the exact artefact it was filed to describe.

Recorded from retro RETRO0087.

## L-0272: **Check the criterion's verifier can FAIL before ticking it.** Two criteria here were `Verified: yes` over tests that passed at the commit

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a green verifier proves it ran, not that it can fail. `transition.py` `_done_verify_gate` (`transition.py:152`) refuses a red or never-run criterion but cannot tell a vacuous passing one; no gate checks a verifier can fail. The reviewer is told to mutate the author's tests (`critic.py:2475-2478`) and `best-practices/testing.md:92-96` makes the author name the mutant first.

**Check the criterion's verifier can FAIL before ticking it.** Two criteria here were `Verified: yes` over tests that passed at the commit the defect was still present. A green verifier proves the verifier ran, not that the work landed.

Recorded from retro RETRO0087.

## L-0271: **A selected test run cannot tell you the tree is green.** Six commits passed a gate that never ran the test my first commit broke

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and now gated at the push: a commit runs only its selected test modules, so a selected run still cannot show the tree is green, and the pre-push hook runs `gate.py` `_full_suite` (`gate.py:878`, 'every test module of both suites, run ONCE') under `--boundary push` (`gate.py:2048`). AGENTS.md:136 states the rule. A commit-time green claim is still unchecked.

**A selected test run cannot tell you the tree is green.** Six commits passed a gate that never ran the test my first commit broke. The rule against this shipped in the same sprint, one commit later, and I did not apply it to the work beside it. Run the full suite before the commit, or do not claim the suite is green.

Recorded from retro RETRO0087.

## L-0270: **An assertion over the set of every possible value holds nothing.** `assertIn(status, {"ok", "refuse", "unevaluated"})` cannot fail, and

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: an assertion over every possible value holds nothing. `critic.py:2459-2462` has the reviewer mutate the author's tests for exactly this; no gate detects a tautological assertion.

**An assertion over the set of every possible value holds nothing.** `assertIn(status, {"ok", "refuse", "unevaluated"})` cannot fail, and it survived mutation against 5,658 tests. If the assertion would pass under every outcome the code can produce, it is documentation with an `assert` in front of it.

Recorded from retro RETRO0087.

## L-0269: **A test asserting against a fixture it built itself proves the reader, not the file.** BG0372's criteria passed against a hand-written

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a test asserting against its own fixture proves the reader, not the file. `best-practices/testing.md:106-113` lists the vacuity mechanisms (`:108`, a fixture shape the product cannot produce). No gate checks a test pins the shipped artefact.

**A test asserting against a fixture it built itself proves the reader, not the file.** BG0372's criteria passed against a hand-written header while the shipped constant carried neither column, and both read `Verified: yes` over the gap. Pin the shipped artefact.

Recorded from retro RETRO0087.

## L-0268: **Two components that measure the same thing will disagree, and both will look green.** BG0415: the budget lane and the planner differed by

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held for the budget case: the planner's `execution_cost` (`sprint.py:12814`) prefers `measured_gate_seconds` (`sprint.py:12756`, called at `sprint.py:12833`), the measured series the budget lane also reads, and falls back to the declared `gate_budget.baseline_seconds` only when nothing is measured, so the two components now read one source; the general rule still binds any new pair that measures the same thing, and no gate checks for such a pair.

**Two components that measure the same thing will disagree, and both will look green.** BG0415: the budget lane and the planner differed by 44% about one gate, each correct within itself. One source, or they drift.

Recorded from retro RETRO0087.

## L-0267: **A guard whose only consequence is a missing record is not a guard.** BG0413's scope floor computed the right verdict for a 91% test loss

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a general rule, and repaired at its site: `tools/gate_timing.py:147-149` sets `ok` False for a test count below the floor and `:174` marks a collapse, so the verdict now has a consequence. A new verdict whose cost is only a missing record is not checked by any gate.

**A guard whose only consequence is a missing record is not a guard.** BG0413's scope floor computed the right verdict for a 91% test loss and spent it on declining to write a timing. Ask what a verdict COSTS, not whether it is correct.

Recorded from retro RETRO0087.

## L-0266: **A plan flagged as over-appetite at plan time is over-appetite.** The velocity record said 107-112 points and the previous sprint

- **Added:** 2026-08-01
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a forecast that is questioned and not acted on was not used. `sprint.py:4517` renders OVER BUDGET loudly at plan time, but nothing refuses a plan flagged over appetite; the operator's call is not gated.

**A plan flagged as over-appetite at plan time is over-appetite.** The velocity record said 107-112 points and the previous sprint delivered 57 of 150. Planning 150 again produced 27. A forecast that is questioned and then not acted on is a forecast that was not used.

Recorded from retro RETRO0087.

## L-0265: A floor tolerates the failure it was written to catch

- **Added:** 2026-07-31
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a floor tolerates the failure it was written to catch. `retro.py:603` makes an unreplaced scaffold count as nothing, which closes the retro case this lesson names; a floor over any other template's worked examples is not gated.

A floor tolerates the failure it was written to catch. `assertGreaterEqual(len(left), 6)` over the retro template's worked examples could not see a marker going missing, which is why three demonstration rows carried none and a wholly unreplaced scaffold validated as three dispositioned findings.

Recorded from retro RETRO0086.

## L-0264: The grade of authority a correction needs should scale with the direction its mistake fails

- **Added:** 2026-07-31
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and partly gated: `critic.py:726-733` drops a superseded round only when a named authoriser ruled it did not happen, and `AGENTS.md:44-50` lists the sign gate refusing a principal who authored or reviewed a unit. The weak-retirement direction is not graded separately, so that rule rests on the reviewer.

The grade of authority a correction needs should scale with the direction its mistake fails. Retiring an APPROVE weakly loses an approval and the gate refuses; retiring a REJECT weakly deletes the only record that blocks the unit. One flag tested for plain truthiness served both, and the backstop written for exactly that hand-append was consulted by only one of the two gates it should have guarded.

Recorded from retro RETRO0086.

## L-0263: A whole-file substring assertion over a document that also carries a Revision History is satisfied by the Revision History row describing

- **Added:** 2026-07-31
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a whole-file substring assertion is satisfied by a Revision History row. `best-practices/testing.md:112` lists 'A whole-file assertion' as a vacuity mechanism; no gate bounds a substring check to the section it means.

A whole-file substring assertion over a document that also carries a Revision History is satisfied by the Revision History row describing the change being asserted. Both passages stating the token premise could be gutted and the guard stayed green.

Recorded from retro RETRO0086.

## L-0262: A guard that reads a document and compares it against a projection of itself can never fail in the reverse direction

- **Added:** 2026-07-31
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a guard that compares a document against a projection of itself cannot fail in reverse. `critic.py:2459-2462` names exactly this (a shape list where two implementations agree by construction passes every mutant); no gate catches it.

A guard that reads a document and compares it against a projection of itself can never fail in the reverse direction. `named = _backticked(block) & types` then asserting `types - named == set()` makes `named` a subset by construction, so three mutants - removing a shipped lane, removing a drift kind, and inventing a fictional lane in the prose - all survived a guard whose criteria claim it "fails in either direction".

Recorded from retro RETRO0086.

## L-0261: A ratio or threshold test cannot report its own inertness, so the property that makes it meaningful needs its own assertion

- **Added:** 2026-07-31
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a ratio test cannot report its own inertness. `best-practices/testing.md:106-113` lists the vacuity mechanisms (`:113`, a positive control already passing); no gate checks that a scaling test varies the size it claims to measure.

A ratio or threshold test cannot report its own inertness, so the property that makes it meaningful needs its own assertion. US0532's corpus pin held at 2.0 with the cache live and 2.0 with it neutered - a ninefold read regression moved the asserted number by nothing - because the fixture issued a CONSTANT six lookups whatever the corpus size, making both branches linear. The scaling is a different fact from the ratio and now has its own test.

Recorded from retro RETRO0086.

## L-0260: **A speed-up test measures the wrong memo unless each is isolated.** Four mutants survived the corpus-cache work because the read-count

- **Added:** 2026-07-29
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a speed-up test measures the wrong memo unless each is isolated. `critic.py:2459-2462` tells a reviewer to mutate the author's tests and `best-practices/testing.md:92-96` makes the author name the mutant first; no gate checks that each cache layer has its own test.

**A speed-up test measures the wrong memo unless each is isolated.** Four mutants survived the corpus-cache work because the read-count test credited the by-id index for work the file memo underneath it was doing. Only per-memo tests could tell them apart.

Recorded from retro RETRO0083.

## L-0259: **Verify the premise before repairing it, and record it when it does not hold.** Three findings this sprint did not reproduce

- **Added:** 2026-07-29
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: verify the premise before repairing it. No gate holds it; the nearest guidance is `AGENTS.md:98-101`, which settles regression versus pre-existing by execution (`git log -S`) rather than impression.

**Verify the premise before repairing it, and record it when it does not hold.** Three findings this sprint did not reproduce. Checking cost minutes; the repairs they implied would have been changes to correct code, and the assertion each was actually missing is what shipped instead.

Recorded from retro RETRO0083.

## L-0258: **A guard that answers a narrower question than it claims reports the narrow answer as the broad one.** Eight of RV0024's residue bugs were

- **Added:** 2026-07-29
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a guard answering a narrower question than it claims reports the narrow answer as broad. No gate holds it; the claim inventory (`critic.py:2524-2534`) has the reviewer check each stated scope against the code, and `sprint_report.py:396-403` is an instance worded correctly.

**A guard that answers a narrower question than it claims reports the narrow answer as the broad one.** Eight of RV0024's residue bugs were one shape: `caller-check --unit` kept the last value, `index_derived_issues` read four of five keys, the seam owner matched by substring, the waiver report was built from stories only. Each returned a clean verdict over something it had not looked at.

Recorded from retro RETRO0083.

## L-0257: **An empty measurement is not a finding.** A Batch line naming no units meant "unreadable", and the report said "delivered nothing"; a

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: `sprint_report.py:396-403` reports missing mutation evidence as 'not a run that found nothing', and `gate.py:2126-2128` reads an unknown as RUNNING; a new empty measurement is not checked by any gate.

**An empty measurement is not a finding.** A Batch line naming no units meant "unreadable", and the report said "delivered nothing"; a stale cell meant "nothing checked this", and `detect` said "no drift". Both read as answers.

Recorded from retro RETRO0082.

## L-0256: **A contradicting pair is decided ONCE, in one place.** BG0356/BG0360 were satisfiable in opposite directions

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a contradicting pair is decided once, in one place. `sprint.py:2530-2536` is one instance (one parser both sites read). No gate detects a pair satisfiable in opposite directions; it is found by review.

**A contradicting pair is decided ONCE, in one place.** BG0356/BG0360 were satisfiable in opposite directions. The fix was a single shared authority both sites read, not two consistent implementations.

Recorded from retro RETRO0082.

## L-0255: **Verify the premise before filing, not just before fixing.** Two bug reports were wrong about the code they described

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: verify the premise before filing as well as before fixing. No gate holds it; the nearest guidance is `AGENTS.md:98-101`, which settles regression versus pre-existing by execution (`git log -S`) rather than impression.

**Verify the premise before filing, not just before fixing.** Two bug reports were wrong about the code they described. Both survived writing, review by their author, and a commit message, and were falsified by the first test that ran against them.

Recorded from retro RETRO0082.

## L-0254: **A guard that cannot fail is not evidence, and mutation is how you find out.** Three survivors this sprint, two of them tests I had just

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a guard that cannot fail is not evidence. `critic.py:2459-2462` tells a reviewer to mutate the author's tests and `best-practices/testing.md:92-96` makes the author name the mutant first; no gate runs mutation on the author's own new tests.

**A guard that cannot fail is not evidence, and mutation is how you find out.** Three survivors this sprint, two of them tests I had just written: the seam owner-check accepted ANY `Preserves:` line because every fixture happened to name the shared file, and the carried-file test compared two constants that DERIVE from each other, so it passed whatever they said - including the wrong name they both had.

Recorded from retro RETRO0082.

## L-0253: **Verifying the premise beat trusting it three times in one afternoon**, twice against findings this author had filed hours earlier

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: verify the premise, including your own earlier findings. No gate holds it; the nearest guidance is `AGENTS.md:98-101`, which settles regression versus pre-existing by execution (`git log -S`) rather than impression.

**Verifying the premise beat trusting it three times in one afternoon**, twice against findings this author had filed hours earlier. BG0368 and BG0370 were mis-graded in opposite directions, and BG0366's summary overstated its own defect - `_overhead_ratio` labels its bound and names what it excludes, which the finding claimed it did not.

Recorded from retro RETRO0081.

## L-0252: **In-lane verification changed what review found, not how much.** 20 majors on 33 units last sprint, 17 on 31 this sprint: the rate barely

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the seams between units are what review finds once lanes catch within-unit defects. CR0468 shipped seam declarations: `refine.py:960` (`seam_declarations`) and `refine.py:1040` (`seam_findings`). Reviewer judgement is still needed for an undeclared seam.

**In-lane verification changed what review found, not how much.** 20 majors on 33 units last sprint, 17 on 31 this sprint: the rate barely moved. The composition changed completely - last sprint roughly 17 of 20 were within-unit and mechanically catchable, this sprint essentially none were. Thirteen of seventeen were seams between units, which a lane cannot reach because a lane reads one unit. Filed as CR0468.

Recorded from retro RETRO0081.

## L-0251: **Enforcing a rule is not obeying it.** The batch that built the criteria floor put four bugs into Fixed with no criteria, and the batch

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: enforcing a rule is not obeying it. The criteria floor now bites on bugs (`transition.py:946-952`, 'no acceptance criteria; ... requires at least one'), but nothing makes the batch that builds a rule obey it first; the author must.

**Enforcing a rule is not obeying it.** The batch that built the criteria floor put four bugs into Fixed with no criteria, and the batch that built name-your-caller shipped a verb reachable from nothing. A rule the machinery does not yet enforce is not in force for the people building the machinery either - which is precisely when it fails.

Recorded from retro RETRO0081.

## L-0250: **A guard that cannot fail is not evidence, and its greenness is the tell.** `caller_resolves` approved `unknown` and `nothing at all` and

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and repaired at the site: `critic.py:3808-3815` (`caller_resolves`) now rejects `unknown` by requiring a path or command shape. The general rule (feed a check something that must fail) is held by `critic.py:2459-2462`, not a gate.

**A guard that cannot fail is not evidence, and its greenness is the tell.** `caller_resolves` approved `unknown` and `nothing at all` and no test noticed, because no test ever asked it to reject anything. Before trusting a check, feed it something that must fail; a check with no recorded refusal has never been shown to be a check.

Recorded from retro RETRO0081.

## L-0249: **One truth held in two places diverges, and the looser copy is the one that runs.** Two of the four serious findings were this shape

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: one truth held in two places diverges. `sprint.py:2530-2536` and `sprint.py:822-847` deliberately route through the runner's own `verify_ac` parser. No gate hunts a hand-maintained list or a second copy; a differential test is the author's choice.

**One truth held in two places diverges, and the looser copy is the one that runs.** Two of the four serious findings were this shape: `lane_verify` re-derived the shell and provenance rule rather than importing it, and `lane_contract` used one parser to decide and another to build. Each copy was individually tested and individually correct, which is exactly why a green suite said nothing - the defect lives in the gap, and only a differential test looks there. The enumerated-list failures this sprint (BG0331, BG0336, BG0341, and the incomplete repairs BG0373 and BG0374) are the same defect wearing a different hat: a hand-maintained list is a second copy of a truth some derivation already holds. Import the rule, derive the list, or write the test that asserts the two agree.

Recorded from retro RETRO0081.

## L-0248: **A review that only reads the diff misses what HEAD has become.** The finding that mattered most in the previous sprint was a repair

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a review must judge what HEAD has become. `critic.py:2455-2458` makes a repair review rule each earlier finding CLOSED, OVER-CLAIMED or MOVED against the tree, and `AGENTS.md:98-101` requires deciding by execution. The brief carries that, not a gate.

**A review that only reads the diff misses what HEAD has become.** The finding that mattered most in the previous sprint was a repair reverted by a later commit, found only by diffing the claim against HEAD. Every review brief since carries that instruction.

Recorded from retro RETRO0080.

## L-0247: **An empty measurement is an unanswered question, not an answer of "nothing".** 57 of 162 suite modules measured an empty read set because

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: `gate.py:2126-2128` states that every unknown degrades to RUNNING because a cache answering skip on an unknown would be a false green, and `sprint_report.py:396-403` words a missing record as not a run that found nothing.

**An empty measurement is an unanswered question, not an answer of "nothing".** 57 of 162 suite modules measured an empty read set because a path built from an imported constant is invisible to a static reader, and counting that silence as "reaches no tests" excluded the very module a change reddened. The safe direction of an unknown is always more work, never less.

Recorded from retro RETRO0080.

## L-0246: **Ship the wiring in the same unit as the mechanism, or it is inert.** Twice in one sprint a correct mechanism reached nothing: the surface

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated for the case it describes: `sprint.py:8698-8704` runs `critic.caller_findings` over the batch and reports each unit shipping a mechanism with no named caller, and `critic.py:3808` (`caller_resolves`) checks the named caller exists. A caller that exists but never calls is the reviewer's question.

**Ship the wiring in the same unit as the mechanism, or it is inert.** Twice in one sprint a correct mechanism reached nothing: the surface hash could never match because a volatile directory was in the digest, and the whole selection path was computed by one hook and ignored by the one that runs tests. Both were invisible to a green suite and to the author, and both were the same defect - a feature whose value never reaches a caller. A unit's acceptance criteria should name the caller, not only the function.

Recorded from retro RETRO0080.

## L-0245: **A measured proxy is the wrong instrument for "did anything change".** The surface hash was computed over the set of files the suites were

- **Added:** 2026-07-28
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and fixed where it was found: `gate.py:2143` (`surface_files`) hashes every tracked file rather than the measured read set, and `gate.py:2126-2128` degrades any unknown to RUNNING. A new cache keyed on a proxy is not checked by any gate.

**A measured proxy is the wrong instrument for "did anything change".** The surface hash was computed over the set of files the suites were measured to read, which omitted 233 tracked files; editing SKILL.md left the digest byte-identical while three tests went red. Hashing every tracked file costs 0.04s against 2,517 files, so the precision bought nothing and the completeness was everything. When a cheap complete answer exists, do not build a clever partial one.

Recorded from retro RETRO0080.

## L-0244: **The strongest evidence a fail-loud fix works is that it refuses its own repository.** Three did

- **Added:** 2026-07-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a fail-loud fix should refuse its own repository. No gate holds it; `AGENTS.md:122` asks the author to exercise each claim through the shipped entry point, refusals included, which is where the repo's own refusal appears.

Recorded from retro RETRO0079.

## L-0243: **Put the evidence where the tooling actually reads it.** A `Verify:` line on a bug executes nothing - only a story's does

- **Added:** 2026-07-27
- **Review-by:** 2027-01-25

**Put the evidence where the tooling actually reads it.** A `Verify:` line on a bug executes nothing - only a story's does. Recording the proof under a different marker kept the evidence and avoided inflating a warning backlog by 15 in the act of satisfying a different gate.

Recorded from retro RETRO0079.

- **Status:** Closed - No longer true: a bug's Verify line now executes. `verify_ac.py:2087-2090` lists BG as a verifiable prefix with `bugs` as its directory and `verify_ac.py:3200` walks `sdlc-studio/bugs`; `transition.py:139-148` (`_bug_verify_gate`) refuses Fixed or Verified on a red recorded run (US0934, commit `c672232b`). The advice to record bug proof under another marker is now wrong.

## L-0242: **Per-lane green is not suite green.** Parallel file-disjoint delivery removes file collisions, not semantic ones: a lane that changes a

- **Added:** 2026-07-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: per-lane green is not suite green. `AGENTS.md:44` and `AGENTS.md:136-139` make the pre-push hook run the whole suite on the pushed range, which is the gate that catches a fan-out's cross-lane break.

**Per-lane green is not suite green.** Parallel file-disjoint delivery removes file collisions, not semantic ones: a lane that changes a rule breaks fixtures owned by lanes that never touched its files. Run the whole suite before believing a fan-out.

Recorded from retro RETRO0079.

## L-0241: **A widened check must not block on the backlog it reveals.** Widening the placeholder sweep was correct and immediately surfaced 31

- **Added:** 2026-07-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: `validate.py:610-640` reads a baseline captured from the checker's own output (`check --emit-baseline`), downgrades the known set, errors on anything new, and removal is one-way; `sdlc-studio/.placeholder-baseline.txt` is the live set.

**A widened check must not block on the backlog it reveals.** Widening the placeholder sweep was correct and immediately surfaced 31 already-terminal artefacts carrying unfilled scaffolds. A check that starts erroring on pre-existing debt gets reverted, which loses the widening too. The answer is a baseline captured from the checker's own output - not a hand-written list - that downgrades the known set and errors on anything new, with removal one-way so the count can only fall. Recorded as project debt rather than quietly tolerated.

Recorded from retro RETRO0079.

## L-0240: Meeting the user where their fingers already are (the natural CLI form) removes a friction that a help string never fully fixes - accept

- **Added:** 2026-07-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: accept the natural CLI form. `best-practices/script.md:269-271` already says a flag a user would naturally repeat uses `action="append"`, since a `store` flag silently drops all but the last. It is guidance with no gate.

Meeting the user where their fingers already are (the natural CLI form) removes a friction that a help string never fully fixes - accept the obvious invocation, keep the flags, refuse only genuine ambiguity.

Recorded from retro RETRO0078.

## L-0239: A regression test for an exemption must assert the input trips the rule WITHOUT the exemption, in the test itself - or a benign fixture

- **Added:** 2026-07-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a regression test for an exemption must show the input trips the rule without it. `best-practices/testing.md:106-113` lists the vacuity mechanisms, and `:113` (a positive control already passing proves nothing). No gate checks it.

A regression test for an exemption must assert the input trips the rule WITHOUT the exemption, in the test itself - or a benign fixture passes vacuously and the mutation survives.

Recorded from retro RETRO0076.

## L-0238: Evidence is a PASSING verdict, not a marker's presence: a gate that accepts "any `**Verified:**` line" accepts a human recording failure

- **Added:** 2026-07-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: `transition.py:113-118` accepts only a PASSING human verdict as evidence (`no`, `stale` and a missing marker all block), symmetric with the executable path.

Evidence is a PASSING verdict, not a marker's presence: a gate that accepts "any `**Verified:**` line" accepts a human recording failure. Check the value, never the label - the recurring scar, hit again here in the gate's own fix.

Recorded from retro RETRO0076.

## L-0237: A directive assembled from a conditional (brownfield adds "detected stack") needs the NEGATIVE case pinned too - the mutation making it

- **Added:** 2026-07-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a conditional directive needs its negative case pinned. No gate holds it; `best-practices/testing.md:92-96` and `critic.py:2459-2462` (mutate the author's tests) catch the missing negative case at review.

A directive assembled from a conditional (brownfield adds "detected stack") needs the NEGATIVE case pinned too - the mutation making it unconditional passed every test until the greenfield-omits-stack assertion was added.

Recorded from retro RETRO0075.

## L-0236: A read on the orientation hot path (`status`/`hint`) must never crash on a hand-mangled runtime file: degrade to absent and self-heal

- **Added:** 2026-07-27
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a read on the hot path must degrade, not crash. `lib/sdlc_md.py:452-458` (`read_json`) returns the default on a missing or malformed file, but a reader that bypasses it is not checked by any gate, so the rule remains the author's.

A read on the orientation hot path (`status`/`hint`) must never crash on a hand-mangled runtime file: degrade to absent and self-heal. Adding a new reader of a `.local` file silently widens that file's blast radius to every command that reads it.

Recorded from retro RETRO0075.

## L-0235: An "offer the exit" affordance must be honest about what the exit actually does: `--file-and-close` refuses hard correctness lanes, so

- **Added:** 2026-07-26
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: `sprint.py:7723-7727` limits `--file-and-close` to ceremony debt and says a red gate lane, a refused Done gate, a broken run state or a missing goal are correctness signals that are not filed away; offering the exit for those would still dangle.

An "offer the exit" affordance must be honest about what the exit actually does: `--file-and-close` refuses hard correctness lanes, so offering it for a set of `gate` blockers dangles a dead-end. The independent review caught this where the author's tests (which used synthetic non-deferrable stages) asserted only that the string appeared.

Recorded from retro RETRO0074.

## L-0234: A batch-scoping or record-based "make-it-pass-here" gate change must be proven it cannot make a genuinely-broken close pass

- **Added:** 2026-07-26
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a close-passing gate change must not mask a real failure. `gate.py:2032-2038` scopes the close lane to the batch while holding the release swap (a tag judges everything); the exact-delta test is the author's obligation, not a gate.

A batch-scoping or record-based "make-it-pass-here" gate change must be proven it cannot make a genuinely-broken close pass. The safe shape is a narrowing that only ever makes things MORE current / smaller-scoped while the repo-global and in-batch strength is held constant - and a test that asserts the exact count delta, so a scope that silently dropped a global failure would fail.

Recorded from retro RETRO0074.

## L-0233: **A `Verify:` line is not verified until it is run.** Three delivered units carried `Verify:` references to test nodes that did not exist

- **Added:** 2026-07-26
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: a broken Verify reference is caught at authoring time by the pre-commit `stamps-staged` lane and at plan time by `sprint.py:822-847`, which builds each Verify through `verify_ac._build_command`; `verify_ac` itself still runs at close and in the Done gate (`transition.py:112-118`).

**A `Verify:` line is not verified until it is run.** Three delivered units carried `Verify:` references to test nodes that did not exist or paths pytest could not parse - invisible until the close ran `verify_ac`. Run `verify_ac` at delivery, not only at close, so a broken verifier fails the unit that authored it rather than the sprint that closes it.

Recorded from retro RETRO0073.

## L-0232: **A destructive default must be opt-in.** `changelog compose` folded and DELETED the whole pending fragment set by default; run out of

- **Added:** 2026-07-26
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: `changelog.py:401-402` makes compose a dry run unless `--apply` is passed, and `changelog.py:464-466` says without it nothing is consumed.

**A destructive default must be opt-in.** `changelog compose` folded and DELETED the whole pending fragment set by default; run out of habit while adding one fragment it destroyed 115. Dry-run by default, consume only on `--apply`.

Recorded from retro RETRO0073.

## L-0231: **Verify the premise before building the fix.** BG0296 was filed blaming the mutation tool for being blind to guard clauses; checking it

- **Added:** 2026-07-26
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: verify the premise before building the fix. No gate holds it; the nearest guidance is `AGENTS.md:98-101`, which settles regression versus pre-existing by execution (`git log -S`) rather than impression.

**Verify the premise before building the fix.** BG0296 was filed blaming the mutation tool for being blind to guard clauses; checking it first disproved that (the tool mutates guards fine) and the real defect was a gitignored-worktree scan. A fix built on the filed premise would have been a fix for a defect that did not exist.

Recorded from retro RETRO0073.

## L-0230: **A measurement instrument that always reads the same is off, whatever it says.** The capacity ceiling reported OVER BUDGET on every plan

- **Added:** 2026-07-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held: `sprint.py:4517` renders the capacity verdict as either 'OVER BUDGET (...)' or 'within budget' from the computed over-list, so the check can tell a batch that fits from one that does not; no gate asserts it distinguishes on a given plan.

**A measurement instrument that always reads the same is off, whatever it says.** The capacity ceiling reported OVER BUDGET on every plan for months and nobody read it. One decision made from four measured rows restored the distinction between a batch that fits and one that does not - the fix was not a better warning, it was a threshold anyone had chosen against evidence.

Recorded from retro RETRO0072.

## L-0229: **A pre-check is an enumeration, and an enumeration is a lower bound.** Testing the anchors before writing them reduced three vacuous

- **Added:** 2026-07-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a pre-check is a lower bound. No gate holds it; `verify_ac.py:3838-3842` (revert-check) is the complete check, and the lesson's advice to keep both stands.

**A pre-check is an enumeration, and an enumeration is a lower bound.** Testing the anchors before writing them reduced three vacuous verifiers to one - real value, and not a substitute for the exhaustive check. The pre-check can only test the anchors someone thought of; the ledger tests all of them. Use both, and never let the cheap one create confidence that retires the complete one.

Recorded from retro RETRO0072.

## L-0228: **Deciding a request is not the same as reducing the backlog.** Four rulings converted 9 discovery items into 17 delivery units

- **Added:** 2026-07-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: deciding a request is not reducing the backlog. No gate holds it; the nearest guidance is `AGENTS.md:83-85` (a CR or RFC is not work until `refine` decomposes it into sized units), so a count of decided items is not a delivery count.

**Deciding a request is not the same as reducing the backlog.** Four rulings converted 9 discovery items into 17 delivery units. A backlog count is not a progress measure while any decisions are outstanding.

Recorded from retro RETRO0071.

## L-0227: **A wrong diagnosis does not fail loudly - it produces a workaround that fails silently.** BG0290's first diagnosis was plausible, fitted

- **Added:** 2026-07-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a wrong diagnosis produces a silent workaround. No gate holds it; the nearest guidance is `AGENTS.md:98-101`, which settles regression versus pre-existing by execution (`git log -S`) rather than impression; the lesson's remedy (find the case the diagnosis predicts differently) is not gated.

**A wrong diagnosis does not fail loudly - it produces a workaround that fails silently.** BG0290's first diagnosis was plausible, fitted the evidence available, and sent 13 stories through a fix that could not work. Before building on a diagnosis, find the case it predicts will behave differently and check that it does.

Recorded from retro RETRO0071.

## L-0226: **A verifier that matches text already in the tree proves nothing, and reading it will not tell you.** Three of 41 passed here and a fourth

- **Added:** 2026-07-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a verifier matching text already in the tree proves nothing. `verify_ac.py:3838-3842` (revert-check) tests a unit's verifiers against the change, the detector this lesson named. It is available at any rung, not only a design rung, but no gate forces it.

**A verifier that matches text already in the tree proves nothing, and reading it will not tell you.** Three of 41 passed here and a fourth passed after being repaired. The only reliable detector is running every verifier at the moment the behaviour is absent and requiring pass=0 - which is free exactly once, at a design rung, and impossible afterwards.

Recorded from retro RETRO0071.

## L-0225: **Scoping a check to a diff disables it wherever there is no diff.** An empty changed-set is not an empty scope; a clean tree must judge

- **Added:** 2026-07-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: `gate.py:160-165` states that with no diff to scope to (a clean tree) the WHOLE workspace is judged, and `gate.py:2032-2038` scopes the close lane to the batch only after that, leaving a tag judging everything.

**Scoping a check to a diff disables it wherever there is no diff.** An empty changed-set is not an empty scope; a clean tree must judge everything, or CI silently judges nothing.

Recorded from retro RETRO0070.

## L-0224: **Fixing an ordering defect can create its mirror image.** The BG0268 repair moved `open_run` first and invented the opposite leak

- **Added:** 2026-07-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a repair to an ordering can create its mirror image. No gate holds it; the nearest guidance is `critic.py:2455-2458`, where a repair review marks a MOVED defect as survived, and `best-practices/testing.md:113` (a positive control) for testing both sides.

**Fixing an ordering defect can create its mirror image.** The BG0268 repair moved `open_run` first and invented the opposite leak. A repair to an ordering must be tested on BOTH sides of the step it moves.

Recorded from retro RETRO0070.

## L-0223: **An acceptance criterion can specify a vulnerability, and a passing test will then defend it.** US0375 asked for the sign-off gate to

- **Added:** 2026-07-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: an acceptance criterion can specify a vulnerability. `critic.py:726-733` drops a superseded round only when a named authoriser ruled it did not happen, narrowing the bypass this lesson found. No gate asks what an adversary gains from a criterion; that stays with the reviewer.

**An acceptance criterion can specify a vulnerability, and a passing test will then defend it.** US0375 asked for the sign-off gate to ignore superseded rows; that IS the bypass. When a test asserts a security-relevant behaviour, ask what an adversary gains from it, not only whether it matches the AC.

Recorded from retro RETRO0070.

## L-0222: My tests verify the piece I just wrote, not the system it lives in

- **Tags:** testing, false-green, review, mutation, bug-class
- **Added:** 2026-07-24
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: tests written against one's own piece miss the system. `AGENTS.md:122` requires putting each claim through the shipped entry point, refusals included, and `best-practices/testing.md:66` ('Name the ENTRY POINT') holds the same rule; `critic.py brief` refuses an unrecorded self-check (`review.author_self_check: block`).

Every defect found in my own work across two sprints has one shape: the test exercised the component I had just written, and nothing exercised the path it sits on.

Three instances, one class. US0400 asserted the rate LABEL (rate_source) and never the value, so a design rung that still computed the full build-rate tokens passed green - the review's only MAJOR. BG0276's ungroomed count tested that refine WRITES a marker and conformance READS it, a closed loop that never asked what was already on disk; it reported zero while 16 stories were ungroomed. BG0279's three tests all called the post-transition conformance helper directly, so a mutant DELETING the call from the close path survived - the check was never wired in, and the suite was green.

The author cannot close this gap by writing more tests of the same kind, because the blind spot is structural: I write the code and its test from one mental model, so the test inherits that model's gaps. Only two things caught these - an independent adversarial review, and mutation that removed the CALL rather than breaking the logic.

Rule: for every unit write at least one test that drives the REAL entry point - the CLI, the close chain, the gate lane - not the function. And mutate by DELETING THE CALL SITE, not only by breaking the function body: a suite that stays green under a deleted call site is telling you the feature is not wired in.

## L-0221: **A library function that prints leaks into every test that calls it.** refine's SEEDED note printed from the library; 69 leaks

- **Added:** 2026-07-23
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: `tools/test_noise.py:1-6` detects diagnostics that reach the console during a passing run and `tools/test-noise-baseline.json` records the known set, so a library function that prints is found. `refine.py:700` now returns the SEEDED note rather than printing it.

**A library function that prints leaks into every test that calls it.** refine's SEEDED note printed from the library; 69 leaks. Return the notes, let the CLI layer report them.

Recorded from retro RETRO0069.

## L-0220: **A `--no-verify` commit in a worktree defers the gate to whoever merges it.** Two agents' bypassed leaks became the first full-tree hook's

- **Added:** 2026-07-23
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a --no-verify commit defers the gate to the merger. `AGENTS.md:44` has the pre-push hook run the full boundary gate on every push, which is where a bypassed worktree commit is caught; the lesson's advice (fix the blocker, do not route around it) is `AGENTS.md:60`.

**A `--no-verify` commit in a worktree defers the gate to whoever merges it.** Two agents' bypassed leaks became the first full-tree hook's red ratchet. A ratchet only holds if every writer runs it - so fix the environmental blocker (BG0271) rather than routing around it.

Recorded from retro RETRO0069.

## L-0219: **A test that asserts a label, not the value, proves the tool named its state - not that it reached it.** US0400 relabelled the marginal

- **Added:** 2026-07-23
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a label assertion proves the tool named its state, not that it reached it. `best-practices/testing.md:106-113` lists the vacuity mechanisms (`:107`, asserting text the code supplies for free). No gate checks that a test asserts a value.

**A test that asserts a label, not the value, proves the tool named its state - not that it reached it.** US0400 relabelled the marginal rate UNMEASURED and still priced the build; the label-only test passed. Assert the number, not the tag.

Recorded from retro RETRO0069.

## L-0218: **A parallel fan-out is worth offering by default, but only when a real file-disjoint decomposition exists** - CR0411, the operator's

- **Added:** 2026-07-23
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: `sprint.py:2321` states parallel is offered ONLY when the batch decomposes into two or more file-disjoint groups, and `sprint.py:2372` words that offer.

**A parallel fan-out is worth offering by default, but only when a real file-disjoint decomposition exists** - CR0411, the operator's request, with this run as its evidence.

Recorded from retro RETRO0068.

## L-0217: **A guard that forces --no-verify trains the bypass it exists to prevent.** A tree-walking test must anchor its exclusions to the repo

- **Added:** 2026-07-23
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a guard that forces --no-verify trains the bypass. `tools/gate_timing.py:152-155` records the same reasoning for a lane, and `AGENTS.md:60` limits the bypass to an emergency. The rule to anchor exclusions to the repo root has no gate; the author must apply it.

**A guard that forces --no-verify trains the bypass it exists to prevent.** A tree-walking test must anchor its exclusions to the repo root, not to a bare path-component name, or it breaks the moment it runs from inside the thing it excludes.

Recorded from retro RETRO0068.

## L-0216: **Mutation-proving at build time is what let the delivery code pass review in two waves, not ten rounds.** The rigour the design rung

- **Added:** 2026-07-23
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: mutating at build time keeps review short. No gate forces it; `best-practices/testing.md:92-96` ('Name the mutant BEFORE writing the test') and `critic.py:2459-2462` are the held guidance.

**Mutation-proving at build time is what let the delivery code pass review in two waves, not ten rounds.** The rigour the design rung discovered by rejection, delivery front-loaded.

Recorded from retro RETRO0068.

## L-0215: **Count test files as coupling before fanning out.** File-disjoint means disjoint including tests; two agents editing one test file

- **Added:** 2026-07-23
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: `sprint.py:2255` treats shared tooling as coupling and `sprint.py:2372` states test files are counted as coupling when a batch is offered a parallel build.

**Count test files as coupling before fanning out.** File-disjoint means disjoint including tests; two agents editing one test file conflict exactly as two editing one module do.

Recorded from retro RETRO0068.

## L-0214: **Check whether the tool you are about to build already exists.** CR0405 asserted CHANGELOG had no helper; `changelog.py` had been there

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: check whether the tool already exists. No gate holds it; `AGENTS.md:103` ('Always look for a tool before doing anything by hand') is the nearest rule, and `changelog.py` is still the helper the lesson found.

**Check whether the tool you are about to build already exists.** CR0405 asserted CHANGELOG had no helper; `changelog.py` had been there all along, and three of its four criteria were already met.

Recorded from retro RETRO0067.

## L-0213: **The plan gate belongs before the repair, and the evidence is now in this repo.** Round 1's plan was refuted in full

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the plan gate belongs before the repair. No gate holds it; the nearest guidance is `AGENTS.md:83`, which requires the story or bug with criteria before any diff, and `AGENTS.md:92-97`, which has the reviewer briefed by the shipped tool.

**The plan gate belongs before the repair, and the evidence is now in this repo.** Round 1's plan was refuted in full. Every previous sprint's rounds 3-10 manufactured the next round's defect, and each flaw was in the approach.

Recorded from retro RETRO0067.

## L-0212: **A counterfactual bar cannot be checked by any run, so it needs a ledger beside it.** The goal asked whether criteria "would fail if the

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a counterfactual bar needs a ledger beside it. `verify_ac.py:3838-3842` ships a revert-check that asks whether a unit's own verifiers reach its production change, and it is the standing practice for a design rung. No gate forces every design rung to run it.

**A counterfactual bar cannot be checked by any run, so it needs a ledger beside it.** The goal asked whether criteria "would fail if the behaviour were absent". At a design rung the behaviour IS absent, so running them is free and settles it. Two seats found this independently and it should be the standing practice for any design rung.

Recorded from retro RETRO0067.

## L-0211: **Derive the whole behaviour, not the half you were looking at.** Round 2 derived the parse from the runner and left the walk restated

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: derive the whole behaviour, not one half. `sprint.py:2530-2536` parses lane criteria with `verify_ac.parse_story`, the runner's own parser, and says a second parser would diverge; nothing checks a new lane for it, and `best-practices/testing.md:106-113` lists the vacuity mechanisms.

**Derive the whole behaviour, not the half you were looking at.** Round 2 derived the parse from the runner and left the walk restated; round 3's escape lived in the half left behind. A guard that shares one of a tool's two behaviours is still a restatement.

Recorded from retro RETRO0067.

## L-0210: **A -k selector matching nothing reports NO TESTS RAN, which is not a pass.** Hit by the author directly, and it is also how BG0256's story

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: `verify_ac.py:531-545` marks a pytest run with exit code 4 or 5 (no tests collected or selected) vacuous, so a `-k` selector matching nothing is attributed rather than read as a pass.

**A -k selector matching nothing reports NO TESTS RAN, which is not a pass.** Hit by the author directly, and it is also how BG0256's story read `Verified: yes` for two days.

Recorded from retro RETRO0066.

## L-0209: **Check what a two-point fit cannot tell you** - see Estimate vs actual

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a pointer lesson whose target exists. Its pointer resolves to `## Estimate vs actual` at `RETRO0066-every-number-names-what-it-covers-and-the.md:81`, and `RETRO0066-every-number-names-what-it-covers-and-the.md:162-163` give the caveat itself: a two-point fit always fits a line exactly, so its figures carry no confidence and only its falsifiable prediction is usable. No gate stops a two-point fit being read as evidence.

Recorded from retro RETRO0066.

## L-0208: **`grep` cannot verify a claim about meaning.** Four ACs passed on prose asserting the exact opposite of their criteria, because `grep` is

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: grep cannot verify a claim about meaning. `verify_ac.py:357-359` still exempts `file`, `grep` and `http` from the vacuity judgement by design, so a grep verifier passes on text that contradicts its criterion; only the reviewer's reading of the criterion catches it.

**`grep` cannot verify a claim about meaning.** Four ACs passed on prose asserting the exact opposite of their criteria, because `grep` is exempt from the vacuity gate by design.

Recorded from retro RETRO0066.

## L-0207: **An estimator's identity is the parameters it takes, not the values they were measured at.** `sample_class` compared constants by value

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: `sprint.py:431-440` (`sample_class`) classifies a row by which estimator produced the forecast, never by the calibration constants it was measured at, derived at read time.

**An estimator's identity is the parameters it takes, not the values they were measured at.** `sample_class` compared constants by value, so shipping a re-measured rate would have silently emptied the whole-sprint proving term the moment a sibling fix landed.

Recorded from retro RETRO0066.

## L-0206: **A repair can mask the defect beside it.** If a mutant survives, test that branch in ISOLATION before believing it

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: if a mutant survives, test that branch in isolation. `critic.py:2463-2467` tells the reviewer to re-test a survivor's branch alone because a sibling guard masked survivors three times. No gate holds it beyond the brief.

Recorded from retro RETRO0066.

## L-0205: **A library test is not a lane test.** The author fixed the engagement floor's false clean, mutation-tested it, and wrote "mutation-proven"

- **Added:** 2026-07-22
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a library test is not a lane test. `AGENTS.md:122` requires each claim through the shipped entry point, refusals included, and `best-practices/testing.md:66` is headed 'Name the ENTRY POINT before writing the test'. No gate checks the lane is mutated.

**A library test is not a lane test.** The author fixed the engagement floor's false clean, mutation-tested it, and wrote "mutation-proven" into BG0251. The three mutants stopped at the library functions and never entered the lane the pre-commit hook actually runs; mutating that guard to `if False:` left 3,891 tests green while the lane printed the original defect verbatim. Pin the surface a user meets: exit code AND printed text.

Recorded from retro RETRO0066.

## L-0204: **An operator ruling before the build is cheaper than a review rejection after it.** Three forks were ruled in advance; one of the rulings

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a ruling before the build is cheaper than a rejection after it. No gate holds it; the nearest guidance is `AGENTS.md:83`, which makes work a story or bug with criteria before any diff, the point at which the forks are decided.

**An operator ruling before the build is cheaper than a review rejection after it.** Three forks were ruled in advance; one of the rulings carried a constraint the author had not seen, and it shaped the implementation rather than being discovered as a defect.

Recorded from retro RETRO0065.

## L-0203: **A number that looks like a successful measurement is more dangerous than an obvious absence.** Three closes reported not-attributable and

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a plausible figure is more dangerous than an obvious absence. `retro.py:925` and `retro.py:2932` label a partly supplied figure `harness+supplied` as a lower bound rather than a clean measurement, and `sprint_report.py:396-403` keeps an absence worded as an absence. No gate checks a new figure.

**A number that looks like a successful measurement is more dangerous than an obvious absence.** Three closes reported not-attributable and everyone knew where they stood. The first close to report a figure was the first at risk of being believed.

Recorded from retro RETRO0065.

## L-0202: **Check what a measurement EXCLUDES before drawing a conclusion from it.** The first attributable token figure this project ever produced

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: check what a measurement excludes. `retro.py:891-897` names exactly what each token source includes (main thread and subagents versus main thread only) and `retro.py:925` says the sum bounds the sprint from below, so the exclusion is printed beside the figure.

**Check what a measurement EXCLUDES before drawing a conclusion from it.** The first attributable token figure this project ever produced was 2.2% from the seed rate, which reads as a textbook validation. It excluded every delegated agent, and the true rate is about 2.7x the seed. The conclusion was drawn first and the exclusion checked second.

Recorded from retro RETRO0065.

## L-0201: **Do not diagnose from a diff taken while another process is mid-edit.** A transient mutation window looked exactly like a reviewer failing

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: do not diagnose from a diff taken mid-edit. `mutation.py:693` (`open_window`) and `mutation.py:800` (`dirty_targets`) record a mutation window so another process can tell a transient mutant from a real change. No gate covers other mid-edit writers; `AGENTS.md:98-101` (decide by execution) is the guidance.

**Do not diagnose from a diff taken while another process is mid-edit.** A transient mutation window looked exactly like a reviewer failing to restore two units' work, and was announced as such before being checked. The file was identical to HEAD moments later. Verify the current state, then describe it - the same order this project keeps failing to use.

Recorded from retro RETRO0065.

## L-0200: **Check the incentive a new reporting path creates, not just its correctness.** Registering a SURVIVED mutant moves a file from "no

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a general rule, though the survivor-registration path it describes is gone (`mutation.py:2143` retires `register`, `mutation.py:22` keeps no ledger). A reporting path that makes bad news quieter than silence is still a design risk for any new evidence lane. No gate checks the incentive; `sprint_report.py:396-403` at least keeps no-evidence visible.

**Check the incentive a new reporting path creates, not just its correctness.** Registering a SURVIVED mutant moves a file from "no evidence" to "covered" while the survivor itself is never displayed, so reporting bad news makes the gate quieter than reporting nothing. A mechanism that rewards silence will get silence.

Recorded from retro RETRO0065.

## L-0199: **A fix that rescues the value can leave the reason with the original defect.** BG0244 taught the velocity row to preserve a measured

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a rescued value can leave its reason with the original defect. No gate holds it; the nearest guidance is `critic.py:2455-2458` (a MOVED defect is one that survived), which is where a half-fixed row is caught.

**A fix that rescues the value can leave the reason with the original defect.** BG0244 taught the velocity row to preserve a measured `actual_tokens` across a re-record, and left the Note column - created specifically to explain a blank - regenerated unconditionally. The bug it was filed to end was "the correction was overwritten by the ceremony that rewrote the row", and that is still true of the reason. Fixing half a row is not fixing the row.

Recorded from retro RETRO0065.

## L-0198: **Say "not applied" rather than counting it as survived.** One mutant in the repair round hit an ambiguous two-occurrence anchor and did

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and now enforced: `mutation.py:861-866` raises ValueError for a patch that changes nothing, because counting a no-op as SURVIVED understates the tests, so the lane no longer reports a not-applied mutant as a survivor.

**Say "not applied" rather than counting it as survived.** One mutant in the repair round hit an ambiguous two-occurrence anchor and did not change the file. A mutation that does not apply is indistinguishable from a surviving mutant unless the harness asserts the bytes changed, and this project has recorded that near-miss before.

Recorded from retro RETRO0065.

## L-0197: **Fix the prose AND the thing the prose was wrong about.** MINOR 4 was a docstring claiming a bound the code did not provide

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: fix the prose AND the thing the prose was wrong about. `critic.py:2524-2534` makes the claim inventory (`CLAIM_SURFACES`: Resolutions, docstrings, comments, CHANGELOG) the first pass of every brief; the author's repair of the code behind a false claim is the reviewer's to confirm under the repair-review rule (`critic.py:2455-2458`). No gate checks it.

**Fix the prose AND the thing the prose was wrong about.** MINOR 4 was a docstring claiming a bound the code did not provide. Correcting only the sentence would have been honest and would have left 500 registrations producing one 76KB entry. The repair measured that first, then bounded it, so the claim became true rather than merely withdrawn.

Recorded from retro RETRO0065.

## L-0196: **Repeating someone else's unverified claim makes it yours.** The reviewer reported that `raw capture 5,672,289` existed nowhere else, and

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: repeating an unverified claim makes it yours. `critic.py:2524-2534` makes the claim inventory (`CLAIM_SURFACES`: Resolutions, docstrings, comments, CHANGELOG) the first pass of every brief, marking a claim no command can settle UNVERIFIABLE; `AGENTS.md:122` asks the author to put each claim through the entry point. Nothing checks commit messages for inherited claims.

**Repeating someone else's unverified claim makes it yours.** The reviewer reported that `raw capture 5,672,289` existed nowhere else, and that went into two commit messages before anyone grepped for it. It appears in five other files. A claim inherited from a source you trust is still a claim you published.

Recorded from retro RETRO0065.

## L-0195: **A self-report is not a measurement, and a ledger that cannot tell them apart is worse than one that holds neither.** Recording provenance

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a self-report is not a measurement. `retro.py:891-897` and `retro.py:2932` label token provenance (`harness+supplied` is the meter plus self-reported totals) and `retro.py:925` says that sum bounds the sprint from below, so the ledger can tell the two apart.

**A self-report is not a measurement, and a ledger that cannot tell them apart is worse than one that holds neither.** Recording provenance was the constraint that made BG0245 safe rather than a quiet downgrade of every entry in the ledger.

Recorded from retro RETRO0065.

## L-0194: **Fixing a column obliges you to look at the one beside it.** `Actual` and `Estimate` are written by the same code in the same row from the

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: fixing a column obliges a look at its neighbour. No gate holds it; the nearest guidance is `critic.py:2455-2458`, which has a repair review rule each earlier finding CLOSED, OVER-CLAIMED or MOVED so a half-fixed row is not read as closed.

**Fixing a column obliges you to look at the one beside it.** `Actual` and `Estimate` are written by the same code in the same row from the same wrong source; fixing one and shipping without reporting the other would have left a defect the fix had just proved exists.

Recorded from retro RETRO0065.

## L-0193: **Prove containment against a fixture that can actually fail.** The first victim repo had a worktree matching its index, so `git add -A`

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a containment proof needs a victim with something to lose. `tools/repo_writes.py:1-25` guards the real tree, but no gate checks that a fixture can fail; `best-practices/testing.md:106-113` lists the vacuity mechanisms, including a positive control already passing (`:113`).

**Prove containment against a fixture that can actually fail.** The first victim repo had a worktree matching its index, so `git add -A` was a no-op and the hash survived the damage. A containment proof needs a victim with something to lose.

Recorded from retro RETRO0065.

## L-0192: **Count before sizing, and count with a pattern that survives an alias.** A naive `subprocess.run(["git"` grep found 24 of 35 sites because

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: count before sizing, with a pattern that survives an alias. `tools/repo_writes.py:1-25` now holds the tree-modification invariant on the whole suite rather than caller by caller, but nothing checks a sweep's count method; no gate holds it, and `best-practices/testing.md:111` (helper versus caller) is the nearest guidance.

**Count before sizing, and count with a pattern that survives an alias.** A naive `subprocess.run(["git"` grep found 24 of 35 sites because one module aliases the import. The sweep would have reported done with a third of the hole open.

Recorded from retro RETRO0065.

## L-0191: **A gate whose input is derived from history cannot judge the commit that creates the history.** The engagement floor reads `git log

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true, and gated for the case it describes: a history-derived gate cannot judge the commit creating the history. `engagement_floor.py:320-340` reads the INDEX at pre-commit time and the pre-commit `floor-pending` lane (`.githooks/pre-commit --list`) runs it. A new history-derived lane still has to be given the same treatment by its author.

**A gate whose input is derived from history cannot judge the commit that creates the history.** The engagement floor reads `git log --grep`, so a pre-commit run is blind to the units the pending commit will ship. A PASS meant "nothing already shipped violates", while everyone read it as "this commit is compliant".

Recorded from retro RETRO0065.

## L-0190: **Two numbers that look related can come from different sources, and "obviously connected" is not evidence.** The measured-rate counter and

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: two related-looking numbers can come from different sources. No gate holds it; the nearest guidance is `AGENTS.md:98-101`, which settles regression versus pre-existing by execution (`git log -S`) rather than impression; for the budget case the single source is now the `gate_budget` config key read by both `gate.py:1843` and `sprint.py:12827`.

**Two numbers that look related can come from different sources, and "obviously connected" is not evidence.** The measured-rate counter and the plan's cost history both describe what sprints cost, so it was assumed fixing one moved the other. They read different logs. The assumption was written into a bug and a decision before anyone ran it.

Recorded from retro RETRO0065.

## L-0189: **When a gate reports an absence, check whether the absence is real before filling it.** The first reflex at this close was a blanket

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: when a gate reports an absence, check it is real before filling it. `sprint_report.py:396-403` reports missing mutation evidence as 'not a run that found nothing' and leaves the gap visible rather than filled. No gate stops a blanket fill; the operator and reviewer catch it.

**When a gate reports an absence, check whether the absence is real before filling it.** The first reflex at this close was a blanket mutation sweep to make 0/4 go green - which would have mutated code no changed test pins, sampled under 1% of the enumerated mutants, and buried good per-unit evidence under weaker aggregate evidence. The operator caught it.

Recorded from retro RETRO0064.

## L-0188: **A lane that reads red when the policy was followed will be ignored**, and is indistinguishable from a broken one

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a lane that reads red when the policy was followed is ignored. `tools/gate_timing.py:152-155` states that blocking an ordinary event would train the bypass and so grades the collapse separately from the floor, and `AGENTS.md:60` limits bypass to an emergency. No gate checks a new lane for this.

**A lane that reads red when the policy was followed will be ignored**, and is indistinguishable from a broken one. The remedy is a way for the practice to record itself, never a quieter lane.

Recorded from retro RETRO0064.

## L-0187: **Building the recorder is not the same as recording.** BG0238 made mutation evidence able to accumulate, and the sprint still closed with

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a general rule, though the mutation ledger it describes is gone: `mutation.py:22` says no per-target ledger is kept and `mutation.py:2143` retires `register`. The rule that a recorder is not the practice still holds for any evidence store: the evidence must be produced where the work happens. No gate checks it.

**Building the recorder is not the same as recording.** BG0238 made mutation evidence able to accumulate, and the sprint still closed with none: the ledger is written by `mutation.py`, while the practice is a builder hand-applying a mutant. 75 mutants were applied and the lane reported 0/4. Ask where the evidence is PRODUCED before deciding where it is stored.

Recorded from retro RETRO0064.

## L-0186: **Reproduction steps are executable content and must never be passed through a shell.** The field most likely to contain commands is the

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: reproduction steps are executable content. `file_finding.py:1056-1066` records that the `--steps` and `--fix` flags ran backtick and `$(` text through the shell, and the `--fields-file` document route (a file no shell expands) is the held remedy; the flags still exist for compatibility and gain a report.

**Reproduction steps are executable content and must never be passed through a shell.** The field most likely to contain commands is the field most likely to be executed.

Recorded from retro RETRO0064.

## L-0185: **Prose that justifies code is the least-reviewed code in the repo** - four sprints running now

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: prose that justifies code is the least reviewed code. `critic.py:2524-2534` makes the claim inventory (`CLAIM_SURFACES`: Resolutions, docstrings, comments, CHANGELOG) the first pass of every brief, which exists because of this recurrence.

**Prose that justifies code is the least-reviewed code in the repo** - four sprints running now. Every comment asserting "this is equivalent", "nothing is lost" or "the fallback takes over" is an untested claim until something executes it.

Recorded from retro RETRO0064.

## L-0184: **A literal count in prose rots.** "206 tests" was true when written, wrong when the reviewer read it, and wrong again an hour later

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: a literal count in prose goes stale. No lint rejects a number in a comment; `critic.py:2524-2534` makes the claim inventory (`CLAIM_SURFACES`: Resolutions, docstrings, comments, CHANGELOG) the first pass of every brief, so a stated count is marked TRUE, FALSE or UNVERIFIABLE by the reviewer.

**A literal count in prose rots.** "206 tests" was true when written, wrong when the reviewer read it, and wrong again an hour later. Put the count in the runner's output, not in a claim nobody re-runs.

Recorded from retro RETRO0064.

## L-0183: **Refuse a total rather than return a short one.** A skipped malformed record yields a quietly low sum, and a low baseline inflates every

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: refuse a total rather than return a short one. `retro.py:312-314` returns every row including malformed ones with the reason, and `gate.py:2126-2128` degrades any unknown to RUNNING, both refusing to read a gap as a smaller answer. No gate checks a new total for the same fault; the author must.

**Refuse a total rather than return a short one.** A skipped malformed record yields a quietly low sum, and a low baseline inflates every delta measured against it. Missing is cheap, wrong is expensive - the sprint goal, applied to the sprint's own fixes.

Recorded from retro RETRO0064.

## L-0182: **Do not judge a measurement by the history of that same measurement.** BG0239's filed fix suggested a duration band to validate a

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: judge a measurement by what the run did, not by that measurement's own history. `tools/gate_timing.py:147-149` now grades a gate timing by the test count that ran against the recorded peak, not by a duration band, so the real speed-up is not rejected. Nothing generalises it beyond that lane.

**Do not judge a measurement by the history of that same measurement.** BG0239's filed fix suggested a duration band to validate a duration; it is circular, and it would have rejected the real 196.7s -> 99s improvement as implausible. Judge a measurement by what the run DID.

Recorded from retro RETRO0064.

## L-0181: **A guard every caller already short-circuits is not covered by its callers' tests.** Hit twice this sprint, by different authors

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a general rule: a guard no caller reaches stays uncovered. No gate runs it; `critic.py:2459-2462` tells a reviewer to mutate the author's tests and `best-practices/testing.md:92-96` makes the author name the mutant first, so deleting a guard and watching the suite stay green is the reviewer's check.

**A guard every caller already short-circuits is not covered by its callers' tests.** Hit twice this sprint, by different authors. If deleting a guard leaves the suite green, the guard is either dead or untested - decide which, and never leave it reading as coverage.

Recorded from retro RETRO0064.

## L-0180: **Deleting a guard requires evidence from the surface the guard protects.** The `if not refused` check was removed because the ledger

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a general rule, though the mutation ledger it came from is gone: this tree still removes guards on a claimed redundancy, and the guards it keeps were proven where they sit. `sprint.py:1606-1611` records that an `is_file()` probe was measured redundant against the real `IsADirectoryError` and removed, and `tools/gate_timing.py:161-164` and `:175-179` record two guards shown unreachable by a surviving mutant. Nothing gates it; the proof is the author's and the reviewer's.

**Deleting a guard requires evidence from the surface the guard protects.** The `if not refused` check was removed because the ledger already excluded refused targets. That was verified against the ledger and never against the report. A guard's redundancy must be proven where it sits.

Recorded from retro RETRO0064.

## L-0179: **A rule enforced in the producer is not enforced in the consumer.** BG0238's ledger applied the verdict rule correctly and the gate then

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a general rule, though its BG0238 example is gone with the mutation ledger: the review ledger under `sdlc-studio/reviews/` is written by `critic.py` and read by several consumers that each apply their own test of it - `review_rounds_across_ledgers` (`critic.py:1636`, called at `sprint.py:1603`), `is_independent` (`critic.py:2344`, applied at `critic.py:2230` and `sprint.py:5393`) and `_principal_refusals` (`sprint.py:9951`) - so a rule about what counts as evidence has to be checked in each reader. No gate does that.

**A rule enforced in the producer is not enforced in the consumer.** BG0238's ledger applied the verdict rule correctly and the gate then overlaid the raw report on top of it, so the careful rule was bypassed by the surface that reads it. When you write a rule about what counts as evidence, go and check every reader of that evidence, not just the writer.

Recorded from retro RETRO0064.

## L-0178: **The harness token capture (5,672,289 -> 472,691/pt) is NOT this sprint's cost and was blanked from the VELOCITY row as

- **Added:** 2026-07-21
- **Review-by:** 2027-01-25

**The harness token capture (5,672,289 -> 472,691/pt) is NOT this sprint's cost and was blanked from the VELOCITY row as not-attributable.** This is the THIRD sprint closed in one session (transcript opens 2026-07-20T15:36Z; this run started 2026-07-21T08:22Z), and `--tokens-from-harness` sums the whole session transcript - so it re-counts RETRO0061 and RETRO0062's sprints and four adversarial review rounds, then divides by only these 12 points. The result is ~19x the measured ~25,000/pt rate. Same finding as RETRO0062's, now recurring: BG0236 (a session-token baseline recorded at plan time, so the close captures a delta) is not a nice-to-have - every close in a long session publishes a false rate until it lands. Recorded as not-attributable rather than published, so the series stays honest. The generated `Sprint tokens/point` line above is the raw capture and is superseded by this paragraph.

Recorded from retro RETRO0063.

- **Status:** Closed - Fixed by BG0236 (Status Fixed): `retro.py:2054-2059` refuses to attribute tokens to a run with no session-token baseline and `retro.py:2112` records the delta, so a long session no longer publishes the false per-point rate.

## L-0177: **A protection built for one suite does not cover the suite beside it.** `skill-tests.sh` has scrubbed 11 git variables since the

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a general rule: a protection built for one suite does not reach another. What holds the known copies now is a pin, not the lane fixes. `tools/skill-tests.sh:50-52` says the scrub list is written out in four places and that `tools/tests/test_skill_tests_env.py` holds them equal and sweeps the repo for an unregistered fifth copy; a new lane beside `.githooks/commit-msg:265-268` and `.githooks/pre-push:332-338` still has to be given the scrub by its author.

**A protection built for one suite does not cover the suite beside it.** `skill-tests.sh` has scrubbed 11 git variables since the index-wipe incident, and `test_skill_tests_env.py` pins the list. The hook's tool-tests lane, invoked on the very next line, ran unscrubbed - so the first `tools/` test to build a git fixture could write ITS tree into the real repo's pending commit under `git commit -a`. Reproduced on three victim repos. A fix recorded as a lesson is not a fix applied everywhere it holds.

Recorded from retro RETRO0063.

## L-0176: **Restoring a global you patched can cost the guarantee the patch was for.** A `tearDownModule` was added so an unrelated module would not

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `scripts/tests/test_gate.py:178-182` states the one-real-run guard is deliberately NOT torn down and records the 59-module doubling that taught it.

**Restoring a global you patched can cost the guarantee the patch was for.** A `tearDownModule` was added so an unrelated module would not fail with this file's message. It handed back the one-real-run guard: 59 of this suite's 98 test modules sort after `test_gate` (2 import it today), and a full run in any of them took the suite 7.9s -> 14.8s, green - the exact doubling the story removed. When a guard's value IS its process-wide scope, the fix for a confusing message is a better message, not a narrower guard.

Recorded from retro RETRO0063.

## L-0175: **A correction has to be propagated to the decision of record, not just the file it was found in.** Retiring the 93.1s baseline in

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true, with a live instance: `sdlc-studio/.config.yaml:207-218` re-declared `gate_budget` on 2026-09-20 at 480s against a 400s baseline, while the decision of record `sdlc-studio/rfcs/RFC0048-make-the-test-suite-cost-effective-without-lowering.md:131` (D6) still reads 120s against a 99s baseline. No script compares a resolved RFC decision with the config value it names, so propagation to the decision of record is still left to the author.

**A correction has to be propagated to the decision of record, not just the file it was found in.** Retiring the 93.1s baseline in `.config.yaml` left RFC0048's D6 row asserting it, so the resolved decision was literally false about the file it pointed at - and US0287's AC4 ("Resolved with the chosen number AND the baseline it was measured against") silently became untrue. Spec rot created by accepting a finding halfway.

Recorded from retro RETRO0063.

## L-0174: **A test can look behavioural and still never enter the branch it names.** Round 2 killed the two hook tests written to close round 1's

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tools/tests/test_precommit_window_guard.py:78` asserts on the hook's own branch marker, `:354` and `:435` carry positive controls, as `best-practices/testing.md:113` requires.

**A test can look behavioural and still never enter the branch it names.** Round 2 killed the two hook tests written to close round 1's MAJOR: their fixture carried only the hook, so every cheap guard died on a missing file, `fail` was already 1, and both cases took the BLOCKED branch instead of the docs-only one they were named for. A mutant restoring the live bug for docs-only commits alone kept them green. Running the real thing is necessary and not sufficient - assert the branch marker, and carry a positive control, or "we ran it for real" becomes its own kind of vacuity.

Recorded from retro RETRO0063.

## L-0173: **Prose written to justify code is code that has not been reviewed - for the third sprint running.** Two of this review's three MAJORs were

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py:2527-2534` claim inventory covers comments and docstrings first in every brief; the lesson recurs, so it is held by the brief rather than closed.

**Prose written to justify code is code that has not been reviewed - for the third sprint running.** Two of this review's three MAJORs were comments asserting a property the code did not have ("same answer as before"; "the expensive lanes ran either way"). Both read as reassuring and both were false.

Recorded from retro RETRO0063.

## L-0172: **A baseline the check cannot itself reproduce is not a baseline.** 93.1s was a hand-sum of three separately timed runs; the hook's own

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sdlc-studio/.config.yaml:192-195` records that 93.1 was a hand sum and the baseline is the hook's own measurement, and `gate.py:1856` reads the baseline the gate recorded itself.

**A baseline the check cannot itself reproduce is not a baseline.** 93.1s was a hand-sum of three separately timed runs; the hook's own measurements of the same work were 99s and 83s. Measure the thing with the instrument that will do the measuring.

Recorded from retro RETRO0063.

## L-0171: **A guard must be tested for the MECHANISM, not the spelling that prompted it.** The structural check matched one literal call form; the

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:66-90` (name the entry point) and `critic.py:2461-2463` require testing the mechanism; the structural-check-versus-runtime-refusal choice is still the reviewer's call.

**A guard must be tested for the MECHANISM, not the spelling that prompted it.** The structural check matched one literal call form; the regression it existed to prevent used another, and walked straight back in. Where a guard can be a runtime refusal on the path everything shares, prefer that to a source-text match.

Recorded from retro RETRO0063.

## L-0170: **Narrowing an exception clause is a behaviour change, not a tidy-up.** Moving a read out of a broad `except` and catching only `OSError`

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate catches it. The repo carries no `pyproject.toml`, `ruff.toml` or `.ruff.toml`, so no lint flags a narrowed `except`. `critic.py:2468-2470` asks for a regression test only once a reviewer already counts the repair as behaviour-changing, and this lesson records the misreading where the narrowing looked like a cost change, so the rule rests on the author naming a narrowed `except` as a behaviour change.

**Narrowing an exception clause is a behaviour change, not a tidy-up.** Moving a read out of a broad `except` and catching only `OSError` let `UnicodeDecodeError` - a `ValueError` - escape a function documented as never raising. The refactor looked like it only changed cost.

Recorded from retro RETRO0063.

## L-0169: **A trend against a dated baseline catches what a ceiling cannot.** `test_gate.py` grew 28% in two days while under every threshold in

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `gate.py:1905-1912` reports the run against a dated recorded baseline (`level with the ... baseline`) rather than a bare pass or fail, and `sdlc-studio/.config.yaml:218-219` holds `baseline_seconds` and `baseline_date`.

**A trend against a dated baseline catches what a ceiling cannot.** `test_gate.py` grew 28% in two days while under every threshold in force. A budget that reports only pass or fail would have stayed green throughout.

Recorded from retro RETRO0063.

## L-0168: **Ask where the data lives before deciding where the check lives.** A check placed away from the data it reads is not wrong so much as

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `gate.py:1856` `read_gate_cost_baseline` and `gate.py:1905-1912` compare a run to the baseline recorded by the same gate, so the check sits where its data lives.

**Ask where the data lives before deciding where the check lives.** A check placed away from the data it reads is not wrong so much as inert: it degrades to permanent silence, which reads identical to permanent success.

Recorded from retro RETRO0063.

## L-0167: **Read the binding rules of the thing you intend to inject before designing a test around injecting it.** A default argument binds at

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:108` lists a fixture shape the product cannot produce as a vacuity mechanism and `scripts/tests/loader.py:25-35` keeps one module identity per name, so patching a captured default is still ineffective.

**Read the binding rules of the thing you intend to inject before designing a test around injecting it.** A default argument binds at definition time, so patching the module constant it was defaulted from changes nothing - and the resulting test passes whether or not the behaviour is present. Making a test cheaper is exactly when vacuity is easiest to introduce, because the change looks like a simplification.

Recorded from retro RETRO0063.

## L-0166: **Profile inside the file before optimising it.** The file-level table said "attack test_gate.py"; the profile said "two tests"

- **Added:** 2026-07-21
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `gate.py:943-945` and `tools/run-suite.sh:214` record per-module wall-clock findings (the slowest module sets the total), measured rather than assumed from a file-level table.

**Profile inside the file before optimising it.** The file-level table said "attack test_gate.py"; the profile said "two tests". The same table said "three lanes re-walk the corpus"; the profile said "842 git subprocesses and 4,495 YAML parses". A cost attributed to the wrong cause produces a plausible plan that fixes nothing.

Recorded from retro RETRO0063.

## L-0165: **Vacuity is not gated on exit 0.** A runner that ran nothing proves nothing whatever its exit code; pytest signals it with codes 4 and 5

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py:538-546` marks pytest exit codes 4 and 5 as vacuous (attributed, not failure) and sets `ok` false for a clean exit that ran nothing.

**Vacuity is not gated on exit 0.** A runner that ran nothing proves nothing whatever its exit code; pytest signals it with codes 4 and 5, and those must be attributed, not read as code failure.

Recorded from retro RETRO0062.

## L-0164: **A point-in-time acceptance criterion is manual by nature.** An executable check that re-asserts a snapshot state ('zero advisories at

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: No gate detects it: `readiness.py:866-875` `_weak_ac` judges tautology and placeholders only; the groomer's reading of the Given clause is still the only guard.

**A point-in-time acceptance criterion is manual by nature.** An executable check that re-asserts a snapshot state ('zero advisories at HEAD') is a category error - it re-runs forever and un-Dones the story on unrelated drift. The Given clause naming a snapshot is the tell.

Recorded from retro RETRO0062.

## L-0163: **A characterisation test still needs mutation to earn its keep.** BG0232's 15 tests all passed on first write because the code was already

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:92-126` and `critic.py:2461-2463` require mutating even tests written against right code, and `verify_ac.py:3842` revert-check proves a unit's verifiers reach the change.

**A characterisation test still needs mutation to earn its keep.** BG0232's 15 tests all passed on first write because the code was already right; only mutating the fingerprint proved they pin it rather than decorate it.

Recorded from retro RETRO0062.

## L-0162: **An AC's freshness must cover whether its verifier still exists.** US0097 read `Verified: yes` for weeks after the test it named was

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py:878` and `verify_ac.py:1161-1162` separate an unresolvable verifier from a stale one, so a deleted test is reported rather than left reading `Verified: yes`.

**An AC's freshness must cover whether its verifier still exists.** US0097 read `Verified: yes` for weeks after the test it named was deleted by an unrelated change; the AC text never changed, so nothing looked stale.

Recorded from retro RETRO0061.

## L-0161: **A test-selection filter is part of the test harness and can silently exclude the tests you are relying on.** A `-k` pattern that matches

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py:538-539` marks a pytest run with exit code 4 or 5 vacuous, and `mutation.py:1770-1773` warns when a selection excludes a referencing test file.

**A test-selection filter is part of the test harness and can silently exclude the tests you are relying on.** A `-k` pattern that matches one of three new tests reports survivors that are artefacts of the filter.

Recorded from retro RETRO0061.

## L-0160: **Scope a mutation run to product code with a scoped test command.** Mutating test files produces expected-vacuous survivors, and a

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `mutation.py:1288-1289` records the test command with the result and `reference-review.md:534-543` has mutation run in an isolated checkout, never the author's tree.

**Scope a mutation run to product code with a scoped test command.** Mutating test files produces expected-vacuous survivors, and a full-suite command multiplies every mutant by the slowest lane. Same technique, 5x the cost, none of the extra yield.

Recorded from retro RETRO0061.

## L-0159: **A guard unreachable through the public path cannot be tested through it.** It still reads as coverage

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:66-90` (name the entry point) and `verify_ac.py:3842` revert-check keep tests on the reachable surface; an unreachable guard is still untestable through the public path.

**A guard unreachable through the public path cannot be tested through it.** It still reads as coverage. Drive the mechanism directly or delete the guard.

Recorded from retro RETRO0061.

## L-0158: **A bug about environment pollution must never be reproduced next to a live repo.** The filed reproduction was followed literally and

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tools/skill-tests.sh:20-32` documents the index-wipe incident and scrubs the variables, and `tools/tests/test_precommit_window_guard.py:82` carries the outer-index hazard into its fixtures.

**A bug about environment pollution must never be reproduced next to a live repo.** The filed reproduction was followed literally and emptied the index. Reproduce in a throwaway clone, and assert the parent's index hash is unchanged afterwards - that assertion is the evidence, not the test count.

Recorded from retro RETRO0061.

## L-0157: A mutant that lands in a test file and survives is expected, not a finding: stubbing a test's body makes the suite pass vacuously by

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `mutation.py:1650` and `mutation.py:1770-1773` separate test files from targets and warn when survivors are read against a selection that misses them, so test-file survivors are not read as product findings.

A mutant that lands in a test file and survives is expected, not a finding: stubbing a test's body makes the suite pass vacuously by construction - scope the evidence run's survivor reading to product files

Recorded from retro RETRO0060.

## L-0156: An upsert that rewrites the whole record can erase the very field it was told not to overwrite: "do not overwrite" must be implemented as

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `lessons.py:1781-1783` writes `Added` only when it is not already a valid date, reusing the existing value rather than omitting it, and `lessons.py:697-712` `upsert_field` replaces in place.

An upsert that rewrites the whole record can erase the very field it was told not to overwrite: "do not overwrite" must be implemented as "reuse the existing value", never as "omit it"

Recorded from retro RETRO0060.

## L-0155: The hook environment is part of the test environment: a suite green in a shell can fail under `git commit -a` because the hook inherits

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tools/skill-tests.sh:53` unsets `GIT_DIR GIT_COMMON_DIR GIT_WORK_TREE GIT_INDEX_FILE` and `.githooks/commit-msg:265-268` scrubs the same variables for its lanes.

The hook environment is part of the test environment: a suite green in a shell can fail under `git commit -a` because the hook inherits GIT_INDEX_FILE, and every git call inside a test's temp fixture then acts on the outer repo - sanitise the lane's env, or the failure reads as flaky tests

Recorded from retro RETRO0060.

## L-0154: A root-relative defect found in one writer must be swept across every sibling writer before the run closes: BG0219 (`lessons.py`) had an

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tests/test_lessons.py:1426-1432` runs from a cwd that is not the root to catch root-relative defects, and `tests/test_confinement.py:444` sweeps every writer on disk.

A root-relative defect found in one writer must be swept across every sibling writer before the run closes: BG0219 (`lessons.py`) had an identical twin in `verify_ac.py`, caught only because the sweep was actually done and filed as BG0220

Recorded from retro RETRO0059.

## L-0153: A pre-flight is worth building where a gate is a chain: the information is nearly always available before the first attempt, and serial

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tools/gate_prereqs.py:59-75` checks gate prerequisites before the first attempt (named in `AGENTS.md` via `tools/enable-hooks.sh`), so serial discovery of a missing tool is avoided.

A pre-flight is worth building where a gate is a chain: the information is nearly always available before the first attempt, and serial discovery reads as the tool moving the goalposts.

Recorded from retro RETRO-0058.

## L-0152: A fixture missing a config key can silently disable the whole branch under test

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:92-97` requires naming the mutant before writing the test, which is how a fixture missing a config key is found; `critic.py:2461-2463` repeats it for reviewers.

A fixture missing a config key can silently disable the whole branch under test. If a test passes, mutate the code it names and confirm it fails for the reason claimed.

Recorded from retro RETRO-0058.

## L-0151: When a defect is fixed, the tests that were passing because of it will fail

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py:2468-2470` demands regression cover for a repair, and `lessons/LL0051-apply-the-fix-as-a-mutant-if-tests-fail-they-were-pinning-the-defect.md:1` states the practice: tests that fail when a defect is fixed were pinning it.

When a defect is fixed, the tests that were passing because of it will fail. Those failures are the fix working, not a regression - read each one before changing it, and correct the fixture rather than the assertion.

Recorded from retro RETRO-0058.

## L-0150: A plan's premises decay

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py:2203-2214` `probable_duplicates` was added because a plan sized on an unexamined backlog inherits expired premises; the order-determining constraint is still unchecked by any gate.

A plan's premises decay. Re-verify the constraint that determines the ORDER of a plan before following it, because a stale premise silently costs the whole sequence.

Recorded from retro RETRO-0058.

## L-0149: Check whether the work is already done before building it

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `readiness.py:1081` flags `already-satisfied` when verifiers pass, and `sprint.py:4367` tells the operator it is a close, not a build, when executable ACs already pass.

Check whether the work is already done before building it. A request left open is not evidence that it is outstanding, and the cheapest delivery is discovering the thing already shipped.

Recorded from retro RETRO-0058.

## L-0148: **A drift kind whose advertised remedy cannot clear it is worse than no hint** - it sends the operator round a loop with no exit

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `reconcile.py:2337-2344` and `reconcile.py:2397-2412` give the spawned-column drift kind an `apply_spawned_column` writer and a remedy that names which direction it can act in.

**A drift kind whose advertised remedy cannot clear it is worse than no hint** - it sends the operator round a loop with no exit. Where a later gate refuses, name that gate.

Recorded from retro RETRO-0057.

## L-0147: **Fixture noise hides vacuous assertions.** The shared story fixture wrote an unrewritable placeholder status, so every apply in the class

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:107-108` lists asserting text the code supplies and a fixture shape the product cannot produce as mechanisms, and `critic.py:2461-2463` has reviewers mutate the author's tests.

**Fixture noise hides vacuous assertions.** The shared story fixture wrote an unrewritable placeholder status, so every apply in the class emitted a spurious unapplied row - which meant the exit-code test would have passed on fixture noise rather than on the refusal it names. It was changed for tidiness and bought correctness by accident.

Recorded from retro RETRO-0057.

## L-0146: **Prose written to justify code is code that has not been reviewed.** Three sessions running, the surviving defect has been in a comment or

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py:2527-2534` makes the claim inventory over comments, docstrings, Resolutions and CHANGELOG the first pass of every brief and author self-check (`critic.py:2608-2615`).

**Prose written to justify code is code that has not been reviewed.** Three sessions running, the surviving defect has been in a comment or a claim rather than in behaviour. A wrong reason attached to right behaviour is more dangerous than no reason: it is what the next person acts on.

Recorded from retro RETRO-0057.

## L-0145: **A test-runner error is not a test failure.** `FAILED (errors=1)` from a mis-named test class looks exactly like a kill

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `mutation.py:1255` keeps an `error` verdict distinct from `killed` and `mutation.py:1155-1160` records a killer only when the runner output names a test.

**A test-runner error is not a test failure.** `FAILED (errors=1)` from a mis-named test class looks exactly like a kill. Any mutation result that does not name the specific test it killed is unverified.

Recorded from retro RETRO-0057.

## L-0144: **Establish the baseline before the mutant, and restore from a source the mutant cannot have touched.** A timed-out mutation harness leaves

- **Added:** 2026-07-20
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `mutation.py:1228-1233` runs the unmutated baseline first and refuses on red, and `mutation.py:313-343` restores from a recorded copy taken before the first mutation, not a copy mutants can touch.

**Establish the baseline before the mutant, and restore from a source the mutant cannot have touched.** A timed-out mutation harness leaves the mutant on disk; a `cp` restore then captures it, and every subsequent run measures the mutant while reporting on the code. Restore from git or a copy taken before the first mutation, and re-run the unmutated baseline first - a baseline that does not come back green means the harness is lying, not the code.

Recorded from retro RETRO-0057.

## L-0143: **The gate cost is concentrated, not diffuse.** Three test files are 62 per cent of the suite runtime and 14 per cent of the tests

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `gate.py:943-945` still records that the suite wall-clock is the slowest module (`test_gate`) rather than the serial sum, so cost stays concentrated in few files.

**The gate cost is concentrated, not diffuse.** Three test files are 62 per cent of the suite runtime and 14 per cent of the tests. Optimising "the tests" in general would have addressed the cheap 38 per cent.

Recorded from retro RETRO0056.

## L-0142: **Rebuild structure from data, never from prose.** `requirements` re-parsed a sentence the ladder had just built from a list

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `transition.py:1704-1709` passes the resolved child TYPE through from `_breakdown_units` instead of re-deriving it from the id prefix, which is this lesson applied.

**Rebuild structure from data, never from prose.** `requirements` re-parsed a sentence the ladder had just built from a list. Passing the list removed the whole defect class; a better regex would only have moved it.

Recorded from retro RETRO0056.

## L-0141: **A fixture can satisfy an assertion for a reason unrelated to the property under test.** The round-1 test asserted "two items" against a

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:106-113` lists a fixture shape the product cannot produce and a positive control already passing as vacuity mechanisms, and `critic.py:2461-2463` mutates the author's tests.

**A fixture can satisfy an assertion for a reason unrelated to the property under test.** The round-1 test asserted "two items" against a fixture where one block carried the suffix, so the wrong delimiter still produced two. Choose the fixture that discriminates, not the one to hand.

Recorded from retro RETRO0056.

## L-0140: **A test that cannot fail is worse than no test, because it reads as coverage.** The round-2 test named the exact defect in its docstring

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:92-97` states the test's mutant first, and `verify_ac.py:3842` revert-check flags a unit whose verifiers do not reach its change.

**A test that cannot fail is worse than no test, because it reads as coverage.** The round-2 test named the exact defect in its docstring and could not reach it. Before trusting a new test, re-introduce the defect it claims to pin and watch it go red - if it stays green, the test is decoration.

Recorded from retro RETRO0056.

## L-0139: **Round 2's findings are made by round 1's repair, and this is now three runs in a row.** Every new finding this round was created by the

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py:2456-2458` and `critic.py:2468-2470` make a repair a unit of new review with per-item verdicts and regression cover; the pattern recurs, so the practice is still carried in every brief.

**Round 2's findings are made by round 1's repair, and this is now three runs in a row.** Every new finding this round was created by the previous round's fix, twice inside the very lines written to fix the previous finding. Treat a repair as new code needing its own adversarial pass, never as the closing of a loop.

Recorded from retro RETRO0055.

## L-0138: **A new guard needs a test of its MECHANISM, not just of the case that prompted it.** The line that closed this review's MAJOR could be

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:92-97` requires the production change a test must fail on to be named first, and `critic.py:2461-2463` has the reviewer mutate the author's tests.

**A new guard needs a test of its MECHANISM, not just of the case that prompted it.** The line that closed this review's MAJOR could be deleted with 3,205 tests still green. A guard is code, it rots like code, and "the suite is green" says nothing about a guard nothing exercises. Write the fixture that makes it fire.

Recorded from retro RETRO0055.

## L-0137: **Forgiving an unsatisfiable demand must surface its cause.** Dropping a dead id silently would trade a false debt for a hidden defect

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `close_owed.py:634-641` reports dead ids only for epics whose coverage depended on forgiving them, which is this lesson's scoping.

**Forgiving an unsatisfiable demand must surface its cause.** Dropping a dead id silently would trade a false debt for a hidden defect; reporting it unconditionally would restore the noise the forgiveness existed to remove. Scope the report to the cases where the forgiveness changed the answer.

Recorded from retro RETRO0055.

## L-0136: **A finding is a hypothesis, not a fact.** Two of six bugs in this batch were wrong in their specifics and both were worth more once

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `reference-bug.md:71` and `reference-bug.md:148-161` keep reproduction steps as a required part of a bug, the check that corrects a wrong finding; no gate refuses an unreproduced one.

**A finding is a hypothesis, not a fact.** Two of six bugs in this batch were wrong in their specifics and both were worth more once investigated. Reproduce before fixing, and correct the record when the premise falls.

Recorded from retro RETRO0055.

## L-0135: **A sweep that checks many things in one process can be satisfied by the first one.** Shared interpreter state - `sys.path`, `sys.modules`

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tests/loader.py:25-35` registers modules in `sys.modules` and refuses a foreign holder of the name, and `tests/test_affects_resolvable.py:405` documents the shared-state hazard; per-case isolation is still the rule.

**A sweep that checks many things in one process can be satisfied by the first one.** Shared interpreter state - `sys.path`, `sys.modules`, caches - makes later cases pass on the back of earlier ones. Isolate per case, or the sweep proves nothing about all but the first.

Recorded from retro RETRO0055.

## L-0134: **A narrow test command over-reports absence.** A mutation run scoped below its target's real coverage manufactures survivors, which then

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `mutation.py:1288-1289` records the selected test command and `mutation.py:1770-1773` `_selection_warnings` warns on a referencing test file outside the selection, so a narrow command cannot stay silent.

**A narrow test command over-reports absence.** A mutation run scoped below its target's real coverage manufactures survivors, which then get filed as bugs. Widen the command to the module's actual tests before believing a survivor, and record the test command beside the result.

Recorded from retro RETRO0055.

## L-0133: **When two checks answer the same question, the stricter one silently wins.** A presence check looser than the mutation regex meant a field

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `lib/sdlc_md.py:1013-1019` and `reconcile.py:951-956` each hold one authority for a rule two callers need, rather than two readers that agree today.

**When two checks answer the same question, the stricter one silently wins.** A presence check looser than the mutation regex meant a field could be seen but not updated. Extract one authority rather than keeping two that agree today.

Recorded from retro RETRO0054.

## L-0132: **A close that performs every step except the record still leaves no record.** CR0322's close ran a two-role review, a repair round, a

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py:9390` `cmd_close` runs the close as one chain and `close_owed.py:407-418` counts a run closed only from its recorded start and end, so a ceremony without its record still reads as owed.

**A close that performs every step except the record still leaves no record.** CR0322's close ran a two-role review, a repair round, a re-verification and an operator sign-off, and produced no retro - so none of that reached the lessons digest, and `close_owed` counted the units as unclosed for two days. Completeness of ceremony is not the same as the output the ceremony exists to produce.

Recorded from retro RETRO0054.

## L-0131: **A checker that passes on input it cannot parse reports coverage it does not have** (US0179's `personas.md`-only vacuous pass)

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `validate.py:1353-1358` routes the flat personas file through `_check_legacy_personas_md`, which emits a `persona-layout` warning (`validate.py:1368`) rather than a silent pass.

**A checker that passes on input it cannot parse reports coverage it does not have** (US0179's `personas.md`-only vacuous pass). Prefer an explicit advisory over a silent green.

Recorded from retro RETRO0053.

## L-0130: **A detector firing on a real gap is only worth what the response to it is worth.** The close-owed detector correctly reported this sprint

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `status.py:487` and `status.py:655` surface the close-owed advisory via `close_owed_advisory` (`status.py:687`) in `status`, which `AGENTS.md` makes step 2 of every session, and `sprint.py:8084` lists it as a closing condition.

**A detector firing on a real gap is only worth what the response to it is worth.** The close-owed detector correctly reported this sprint as unclosed on the day it shipped. The debt then sat for three days across four subsequent sprints. Building the instrument is the cheap half.

Recorded from retro RETRO0053.

## L-0129: **A fix's own argument constrains its implementation.** BG0208's case is that the archive is the permanent record - so re-stamping

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py:6602-6613` skips re-stamping an already stamped outcome and restores the original `ended_at` after `close_run`, so the correction never moves when the run ended.

**A fix's own argument constrains its implementation.** BG0208's case is that the archive is the permanent record - so re-stamping `ended_at` while correcting `outcome` corrupted the thing the fix existed to protect. Read the justification back against the diff.

Recorded from retro RETRO0052.

## L-0128: **When two code paths answer the same question, extract before the second answer drifts.** The H1-strip rule had three private copies and

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `lib/sdlc_md.py:1011-1019` `heading_title` is stated to be the ONE definition shared by every heading generator, and `reconcile.py:951-956` shares the breakdown reader between two subsystems.

**When two code paths answer the same question, extract before the second answer drifts.** The H1-strip rule had three private copies and the child-resolution rule had two. Both drifted, and both were found by someone else asking whether the "one definition" claim was true.

Recorded from retro RETRO0052.

## L-0127: **A test that passes for an incidental reason is not coverage.** Twice this sprint a guard looked covered because the path around it

- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `best-practices/testing.md:92-126` names the mutant before the test and lists eight vacuity mechanisms, and `verify_ac.py:3842` revert-check detects verifiers that miss the change.

**A test that passes for an incidental reason is not coverage.** Twice this sprint a guard looked covered because the path around it happened to be green: `_ac_heading`'s strip (every test used a long criterion, where truncation removes the punctuation anyway) and `close_owed`'s type guard (every test used childless non-epics). Mutating the guard is the only way to find this; reading the test cannot.

Recorded from retro RETRO0052.

## L-0126: A fail-closed fallback is not the main path with one rule removed

- **Tags:** review, gate, fail-safe, test-coverage, mutation
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `transition.py:362-372` `_rfc_open_decisions_unstructured` drops every structural signal in the fallback and records the earlier fail-open version.

A fallback written to fail closed was built by copying the main scan and disabling ONE of its two structural rules. The rule it kept (a heading ends the decisions section) was the very rule an earlier round had already found to be unsafe inside a fence, so the fallback re-introduced that bypass in the path meant to prevent it, and the gate advertised fail-closed while failing open. Two lessons. First: a fail-safe path is not a copy of the primary path with one line removed; decide what the safe answer IS when the input is untrustworthy, and compute that directly. Here every structural signal is suspect at once, so the safe reading drops them all and over-reports. Second: a fallback that blocks makes every block-asserting test on the primary path pass, so the primary guard silently loses its coverage the moment the fallback lands. Reverting the CommonMark matcher to a naive toggle left all 107 tests green. A guard shadowed by a safety net needs a test whose correct answer is PASS, because that is the only answer the net cannot produce.

## L-0125: Round 2 findings are usually created by the round 1 repair

- **Tags:** review, repairs, mutation
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py:2456-2458` makes a repair review rule each prior finding CLOSED, OVER-CLAIMED or MOVED and `critic.py:2468-2470` demands regression cover for a repair.

Two adversarial rounds this sprint, REJECT both times, and both of round 2's MAJORs were introduced by round 1's fixes - matching the previous sprint exactly. Widening the RFC heading match to close four bypasses created a fifth (a shell comment in a fenced block ended the section). A test written to defend an untested branch re-implemented the branch in its own body and passed with the production code deleted. When repairing a review finding, attack the repair with the same energy as the original defect, and never describe a repair as tested without mutating the production code to prove it.

## L-0124: File the friction, not just the blockers

- **Tags:** dogfooding, friction, filing
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `AGENTS.md:118` tells agents to file findings with `file_finding.py`; no gate forces the filing of friction, so it stays a known-weak rule.

Across this run I filed defects that BLOCKED me promptly (a readiness gate certifying templates, a mutation gate reporting unrun mutants) but silently worked around friction that merely cost time: a scaffolder mis-distributing criteria, four wrong Affects lines, a collision analysis built on them, a lint lane that hides latent failures, an appetite flag that erases the over-commitment it records, a token actual nobody supplies. Six items, none of which would have been captured without being asked. A blocker files itself because you cannot proceed; friction has to be filed deliberately, and it is the half that tells you what the product is like to USE.

## L-0123: **L-0113** An AC asserting the committed state cannot be green in the working tree

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0113, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0122: **L-0112** The author cannot close the loop: build-to-Done needs the reviewer of record

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0112, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0121: **L-0111** Story points size the diff, not the discovery

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0111, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0120: **L-0110** A new writer must join the atomicity and confinement rosters, not just work

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0110, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0119: **L-0109** Delegating by `Affects` reproduces whatever is wrong with the `Affects`

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0109, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0118: **L-0108** Build the gate first, then let it tell you the size of the backlog it guards

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0108, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0117: **L-0107** An AC that runs the repo's standing guards is green before the work starts

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0107, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0116: **L-0106** A same-length mutant is the mutation check's own blind spot

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0106, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0115: **L-0105** Suppressing a cache write does not stop a cache read

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0105, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0114: **L-0104** A readiness gate that recognises one hardcoded placeholder recognises none

- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

Recorded from retro RETRO-0051.

- **Status:** Closed - Duplicate of L-0104, a bodiless copy of that entry; the original carries the judgement and stays.

## L-0113: An AC asserting the committed state cannot be green in the working tree

- **Tags:** acceptance-criteria, grooming, git
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: Still true and ungated: `readiness.py:866-875` `_weak_ac` tests only for missing, tautology or placeholder criteria, nothing flags a working-tree-versus-HEAD criterion, so grooming judgement remains the only guard.

US0251 AC2 runs 'command_audit --write' followed by 'git diff --exit-code' over the report. The story's own job is to regenerate that report, so before the commit the diff is non-empty BY CONSTRUCTION and the AC is red; after the commit it is green. It is a post-commit invariant wearing a pre-commit criterion's clothes. The delegated agent correctly refused to stage the file to force it green - that manufactures the evidence instead of producing it. When grooming, an AC that compares working tree to HEAD should either be stated as a post-commit guard or replaced by the property it is really after: here, that repeated regeneration is byte-identical, which IS checkable before committing and was proven (three identical runs).

## L-0112: The author cannot close the loop: build-to-Done needs the reviewer of record

- **Tags:** two-role-gate, autonomy, close
- **Added:** 2026-07-19
- **Review-by:** 2027-01-25

This run built 19 units; 4 reached Done. The 13 stories sit at Review because two_role_after is set and critic.record_signoff refuses a principal equal to the author OR matching any reviewer already recorded on the unit - explicitly including the authoring session's own subagents. That is the gate working, not an obstruction: an autonomous run can drive a batch to BUILT and verified, and the terminal transition is deliberately outside its reach. Plan and report in those terms - a sprint goal of 'all units Done' is unreachable by the agent alone by design, so state the reachable end state (built, ACs green, at Review) and name the sign-off as the remaining step.

- **Status:** Closed - Its premise changed: `reference-config.md:240` retires `review.two_role_after`, one independent APPROVE now decides a unit and the operator signs once at `sprint sign`; the advice that Done is out of an agent run's reach is wrong, and independence is held by `sprint.py:9951-9979`.

## L-0111: Story points size the diff, not the discovery

- **Tags:** estimation, points, discovery
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py:21` defines the forecast as points times a measured rate and the surrounding text says decompose rather than trust an estimate; points still price the edit, not discovery.

Across this run every epic cost more than its points implied, and the overrun was never typing - it was measurement contradicting a written claim. US0256 (3pts) needed a detector, an applier, two CLI paths, a refine integration and three roster registrations. US0244 (3pts) found its own gate had a false negative on real data and that the parent CR undercounted its tranche by three. US0253 (5pts) found the gate it was wiring had never run and its detector matched 0 of 68 real leaks. Points estimated from a written decomposition price the edit; they cannot price finding out that the decomposition was wrong. Treat a points figure over unverified specs as a lower bound with wide error bars, and say so at plan time rather than at the close.

## L-0110: A new writer must join the atomicity and confinement rosters, not just work

- **Tags:** invariants, writers, rosters
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tests/test_confinement.py:444` reads the writer roster off disk and `tests/test_reconcile.py:2398-2404` pins `DRIFT_KINDS` to the true emission vocabulary, so a new writer joins the rosters.

apply_linked_epics passed all seven of its own tests while writing an index with write_text instead of atomic_write, and while emitting a drift kind absent from DRIFT_KINDS. Neither was visible from the story's own ACs; both were caught by standing cross-cutting suites (write-confinement, drift-kind vocabulary) that a sibling story happened to be extending at the same moment. When adding a writer or a detector, check the project's roster-style invariants explicitly - the unit tests of a new feature systematically cannot see them.

## L-0109: Delegating by Affects reproduces whatever is wrong with the Affects

- **Tags:** parallelism, affects, collisions
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py:2432-2434` still states that lane disjointness is only as good as the declared `Affects`, and an undeclared file can collide; the file sets of test files remain undeclared.

US0252 and US0256 were flagged by the planner as colliding on reconcile.py. Measuring showed US0252's real surface was elsewhere, so the Affects was corrected and the recorded collision dissolved - but both units still wrote tests/test_reconcile.py, which nobody had recorded. A concurrent agent and the author then edited one file and the suite failed with an import error belonging to neither piece of work. Collision analysis inherits the accuracy of the Affects lines, and those had already been proven unreliable three times in the same run. Before parallelising, diff the ACTUAL file sets, including test files, not the declared ones.

## L-0108: Build the gate first, then let it tell you the size of the backlog it guards

- **Tags:** gates, enumeration, census
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `reference-sprint-toolchain.md:72` names `status.py points` for the backlog census and `reference-sprint.md:716` the read-only `sprint.py breakdown` census, so counts are derived rather than enumerated.

CR0295 enumerated 5 RFCs needing decision rows closed. Implementing the standing check and running it found 8. The CR was written by reading; the gate was written by measuring. Where a remediation story carries a list of affected files, treat the list as a hypothesis and re-derive it from the check once the check exists - and prefer a census-based AC (scan the workspace) over an enumerated one, because only the census stays true as the workspace changes.

## L-0107: An AC that runs the repo's standing guards is green before the work starts

- **Tags:** acceptance-criteria, vacuous-green, grooming
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py:3842` revert-check asks whether a unit's verifiers reach its production change, and `readiness.py:1081` flags `already-satisfied` when verifiers pass before the work.

Two groomed stories were verified by 'validate_skill && lint-style' and 'check_links && validate_skill && doc_coverage'. Those are pre-commit lanes that pass on a clean tree, so both ACs were green before a line was written, and one had already been machine-annotated Verified: yes on an unimplemented story. Sweep a freshly groomed batch with verify_ac BEFORE implementation and require every AC to be RED: a criterion that passes on the unbuilt code is measuring the repo, not the story.

## L-0106: A same-length mutant is the mutation check's own blind spot

- **Tags:** mutation, test-fixtures, fixture-validity
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tests/test_mutation.py:744-763` pins both mtime (`os.utime`) and size and asserts the fixture invalid if the lengths differ, which is this lesson's rule.

CPython invalidates a .pyc on (source mtime, source size). A mutation-check fixture that changes the file LENGTH invalidates the cache by accident and therefore cannot detect a staleness bug - the first version of the pre-existing-cache test passed against unfixed code for exactly this reason. When testing anything keyed on (mtime, size), pin both, and assert in the fixture that you did.

## L-0105: Suppressing a cache write does not stop a cache read

- **Tags:** mutation, caching, test-fixtures
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tests/test_mutation.py:770-811` starts from a pre-existing cache and asserts the purge, and `mutation.py:396` sets `PYTHONDONTWRITEBYTECODE`; both halves of the defence remain tested.

The mutation gate's stale-bytecode fix needed two guards, not one. PYTHONDONTWRITEBYTECODE stops the runner adding to **pycache**; it does nothing about a **pycache** already on disk from an ordinary test run before the gate started - which is the normal order of work. The first mutation-check of the fix showed the purge half SURVIVING, because the only test covering it started from a clean tempdir. A defence against stale state needs a test that starts from the stale state.

## L-0104: A readiness gate that recognises one hardcoded placeholder recognises none

- **Tags:** gates, vacuous-green, audit
- **Added:** 2026-07-19
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `readiness.py:866-875` `_weak_ac` now judges the whole AC section for an unexpanded `{{...}}` span (`readiness.py:42-44`), which the scaffolder actually emits, and is called at `readiness.py:1040`.

audit._weak_ac claimed to flag 'the tautology placeholder' but matched exactly one literal phrase, so the {{...}} spans the scaffolder actually emits passed it. The gate certified 28 pure-template stories as ready for implementation. When a check names a CLASS of defect in its docstring, it must detect the class, not one instance of it - and the instance it detects should be the one the local toolchain actually produces. Test a gate against the output of the generator it is meant to police.

## L-0103: A no-result signal from a per-unit runner (`go` per package, `jest` per project) means "the whole run was empty" only when every unit says

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py:300-309` explains that only `go` and `jest` report per unit and so need a counter-signature, while `unittest` and `pytest` print one exclusive summary.

A no-result signal from a per-unit runner (`go` per package, `jest` per project) means "the whole run was empty" only when every unit says so; a single-summary runner needs no such reconciliation.

Recorded from retro RETRO0050.

## L-0102: A frequency threshold over "how widely is this shared" must exclude the owner, or the owner's own correct usage suppresses detection of

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `ac_scope.py:120-121` skips the owning epic's own stories when counting spread (`if own_eid == owner_eid: continue`), which is this lesson applied.

A frequency threshold over "how widely is this shared" must exclude the owner, or the owner's own correct usage suppresses detection of everything that borrows from it.

Recorded from retro RETRO0050.

## L-0101: A comment justifying a mechanism is a claim, and it needs the same evidence as the code: two false claims about frequency suppression

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `critic.py:2527-2534` runs a claim inventory over comments and docstrings first in every brief, and `ac_scope.py:36-43` now documents with evidence why the frequency suppression was removed.

A comment justifying a mechanism is a claim, and it needs the same evidence as the code: two false claims about frequency suppression survived into review, and one was the stated reason to accept a repair.

Recorded from retro RETRO0050.

## L-0100: Stale bytecode silently invalidates a mutation check when the mutant is the same byte length: purge `__pycache__` and run `python3 -B`, or

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `mutation.py:355-364` purges the target's cached bytecode and `mutation.py:386-396` runs suites with `PYTHONDONTWRITEBYTECODE`; `verify_ac.py:4029-4035` reuses the purge for its revert-check.

Stale bytecode silently invalidates a mutation check when the mutant is the same byte length: purge `__pycache__` and run `python3 -B`, or the kill/survive verdict is about the cache.

Recorded from retro RETRO0050.

## L-0099: A guard that unrelated output can switch off is worse than the false alarm it replaced: prefer a narrow false positive to a silent false

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `lib/sdlc_md.py:268-273` exempts a process only by the inherited `MUTATION_RUN_ENV` marker set at `mutation.py:396`, so unrelated output cannot switch the guard off.

A guard that unrelated output can switch off is worse than the false alarm it replaced: prefer a narrow false positive to a silent false negative, and never let a foreign process speak for the one under test.

Recorded from retro RETRO0050.

## L-0098: A `-k` test filter that matches nothing exits 0 having run zero tests, so a renamed class silently converts an executable AC into a green

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py:538-539` treats pytest exit codes 4 and 5 (a filter matching nothing) as vacuous, so a renamed class no longer yields a green no-op.

A `-k` test filter that matches nothing exits 0 having run zero tests, so a renamed class silently converts an executable AC into a green no-op (filed BG0193).

Recorded from retro RETRO0049.

## L-0097: Monkeypatching a module reached through `sys.modules` leaks across the whole test process; patch and register the undo together

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `tests/test_close_owed.py:1371` registers the `sys.modules` undo with `addCleanup` beside the patch, and `tests/loader.py:25-30` shows the registry is shared, so the leak risk is live.

Monkeypatching a module reached through `sys.modules` leaks across the whole test process; patch and register the undo together (`addCleanup`) so the two cannot drift apart.

Recorded from retro RETRO0049.

## L-0096: A truthiness guard on a scope filter (`if wanted and ...`) fails open: an empty scope silently becomes an unbounded one

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py:6402` applies the scope filter unconditionally (`declared & wanted`, an empty scope derives nothing), and a grep of `scripts/` for `if wanted and` finds no truthiness guard left.

A truthiness guard on a scope filter (`if wanted and ...`) fails open: an empty scope silently becomes an unbounded one. Scope filters should be unconditional, with emptiness handled explicitly.

Recorded from retro RETRO0049.

## L-0095: Deriving a terminal status is an assertion about work, so it must be scoped to what the run actually touched and must refuse on incomplete

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py:6402` skips an epic whose breakdown does not intersect the run's wanted ids, and `sprint.py:6405-6408` refuses on unreadable children, so derivation is scoped and refuses on incomplete evidence.

Deriving a terminal status is an assertion about work, so it must be scoped to what the run actually touched and must refuse on incomplete evidence. "No children" and "no readable children" are both different from "all children complete".

Recorded from retro RETRO0049.

## L-0094: A helper that SKIPS what it cannot resolve is safe for detection and unsafe for derivation: `_breakdown_units` silently drops an

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `reconcile.py:951-956` keeps a separate all-ids reader because `_breakdown_units` skips unresolvable children, and `sprint.py:6405-6408` refuses to derive an epic when a child is unreadable.

A helper that SKIPS what it cannot resolve is safe for detection and unsafe for derivation: `_breakdown_units` silently drops an unresolvable child, and reusing it to decide completion turned "the only child I could read is done" into "all children are done". Before reusing a census helper to make a CLAIM, check what it drops.

Recorded from retro RETRO0049.

## L-0093: Build a close-ceremony feature by orchestrating the existing tested primitives (sign-off, close, transition, velocity), not a parallel path

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `sprint.py:9390` `cmd_close` is documented as one deterministic, resumable chain over the existing primitives and `sprint.py:6365` derives epic status through them; no parallel close path exists.

Build a close-ceremony feature by orchestrating the existing tested primitives (sign-off, close, transition, velocity), not a parallel path - the feature inherits their gates (AC-verify, independence, idempotent re-close) for free.

Recorded from retro RETRO0048.

## L-0092: Correcting a wrong constant can activate dead code that only ever "worked" because the constant was wrong

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: no gate holds it. Nothing in `scripts/` or `tools/` detects a guard that was a no-op only because a constant was wrong, and a corrected constant reads as a one-line data change. `critic.py:2468-2470` asks for a test of a behaviour-changing repair, but only when the reviewer sees the constant change as changing behaviour, so the general rule on the author is the only cover.

Correcting a wrong constant can activate dead code that only ever "worked" because the constant was wrong. When a `max(x, CONST)` or `x < CONST` guard exists only to be a no-op, fixing CONST turns it live - re-derive what the guard should actually compare against, do not just change the number.

Recorded from retro RETRO0048.

## L-0091: Verify lines must use the DSL verbs (`grep`/`shell`/`pytest`/`file`/`http`/`eval`), never a backtick-wrapped raw `python3 ...`; the `grep`

- **Added:** 2026-07-18
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: `verify_ac.py:20` says an unrecognised expression is an invalid verifier (exit 2) and `verify_ac.py:564` lists the DSL verbs, so a non-DSL Verify line still fails every run.

Verify lines must use the DSL verbs (`grep`/`shell`/`pytest`/`file`/`http`/`eval`), never a backtick-wrapped raw `python3 ...`; the `grep` verb takes `pattern file` with NO flags, and a shell command needs an explicit `shell` prefix. A groomed AC with a non-DSL Verify line passes grooming but fails every verify_ac run.

Recorded from retro RETRO0048.

## L-0090: **A create-only `Affects` is a real grooming gap, not a gate bug.** Name at least one existing file the unit also touches (here

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: artifact.py:1095 and :1276 refuse an Affects that resolves to nothing, and sprint.py:2432 says disjointness is only as good as declared Affects; a create-only Affects still gives the collision check no anchor.

**A create-only `Affects` is a real grooming gap, not a gate bug.** Name at least one existing file the unit also touches (here `CHANGELOG.md`, which the changelog AC writes) so the collision check has an anchor.

Recorded from retro RETRO0047.

## L-0089: **Machine-guard every vocabulary a self-describing contract claims to cover.** The v3 `inbox` lane shipped as prose the guard did not check

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and guarded: tests/test_schema_contract.py:185 test_added_status_is_the_code_inbox_status and :192 test_inbox_applies_to_exactly_the_finding_types machine-guard the inbox lane against sdlc_md.INBOX_STATUS.

**Machine-guard every vocabulary a self-describing contract claims to cover.** The v3 `inbox` lane shipped as prose the guard did not check - latent rot under a doc that promises the guard covers "the vocabularies below". Encode it as data and guard it, or do not claim coverage.

Recorded from retro RETRO0047.

## L-0088: **A public contract's version stamp must anchor to what new consumers actually meet.** Tying the masthead to the fallback file made the

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and guarded: tests/test_schema_contract.py:210 test_masthead_matches_new_project_seed and :220 test_fallback_default_does_not_lead_current anchor the masthead to the new-project seed, not the fallback.

**A public contract's version stamp must anchor to what new consumers actually meet.** Tying the masthead to the fallback file made the guard cement the wrong invariant while staying green. Anchor a drift guard to the source that governs the real artefact (the new-project seed), not a lookalike.

Recorded from retro RETRO0047.

## L-0087: **Verify which file a "default" actually comes from before documenting it as the default.** New projects are seeded from

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: templates/config.yaml seeds new projects with schema_version 3 (line 9) while templates/config-defaults.yaml:12 still holds the fallback schema_version 2, and its comment (lines 6-7) says so; tracing the copied path remains necessary.

**Verify which file a "default" actually comes from before documenting it as the default.** New projects are seeded from `templates/config.yaml` (3), not the `config-defaults.yaml` fallback (2); reading the copy site (`init.py`) without checking the copied path produced a confident, wrong contract. Trace the value to the file the running code reads.

Recorded from retro RETRO0047.

## L-0086: A bounded mutation run with a low ceiling on a large multi-function file samples early-file lines (peripheral helpers), not the diff -

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: critic.py enumerates claims and refuses an inventory with unruled claims (critic.py:2596, :3651), and a bounded mutation sample on a large file still samples early lines unless line-targeted; recording N/M enumerated stays the rule.

A bounded mutation run with a low ceiling on a large multi-function file samples early-file lines (peripheral helpers), not the diff - uninformative unless line-targeted. Record the sample honestly (`N/M enumerated`), never as clean coverage.

Recorded from retro RETRO0045.

## L-0085: A worktree subagent branches from a base SHA, so `git diff main..branch` shows the other side "reverted" and misleads; a three-way merge is

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: reference-delivery.md:52 has a parallel build give each agent its own git worktree, merged afterwards (disjointness check at :18-25), so a reviewer reading git diff main..branch of such a branch still sees the other side reverted; git show <commit> --name-only remains the scope check.

A worktree subagent branches from a base SHA, so `git diff main..branch` shows the other side "reverted" and misleads; a three-way merge is still clean when the groups are file-disjoint. Verify scope with `git show <commit> --name-only`, not the full-tree diff.

Recorded from retro RETRO0045.

## L-0084: The `documented` conformance stage is a GLOBAL floor: one uncatalogued command fails it for every unit

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: doc_coverage.py:150 emits a blocking command-uncatalogued finding for any SKILL.md Type Reference command lacking a help/help.md entry, and conformance.py:547 runs it as a repo-global stage.

The `documented` conformance stage is a GLOBAL floor: one uncatalogued command fails it for every unit. A command added to the Type Reference must also land in the help catalogue, or the whole gate reads as 100+ non-conformant units.

Recorded from retro RETRO0045.

## L-0083: A fix's test must exercise the failure mode the fix could *introduce*, not only the one it removes: BG0181's fix passed its

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: best-practices/testing.md#name-the-mutant-first (named under AGENTS.md 'Before you write') requires stating the production change a test must fail on, which covers the failure a fix could introduce.

A fix's test must exercise the failure mode the fix could *introduce*, not only the one it removes: BG0181's fix passed its trailing-parenthetical test while silently dropping units after a mid-line one - trading harmless over-reporting for worse silent under-reporting. See [[review-model-two-roles]].

Recorded from retro RETRO0045.

## L-0082: A composed evidence line must carry its source report's failure state (baseline/errors/truncation), not only its successes - otherwise the

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: critic.py:3651 refuses a claim inventory unless every enumerated claim carries a ruling, and the verify report carries its own failure state; laundering a failed report into a neutral lane remains the hazard.

A composed evidence line must carry its source report's failure state (baseline/errors/truncation), not only its successes - otherwise the ceremony launders a worthless report into a neutral-looking lane. (Validity: 2026-10-17)

Recorded from retro RETRO0044.

## L-0081: When a gate's requirement has independently-downgradable halves, compose them independently and test the partial-tag matrix, not just

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: critic.py:2596 requires all four CLAIM_SURFACES enumerated rather than an all-on or all-off check, the same independently-composed design; the partial-tag matrix remains the right test for a gate with downgradable halves.

When a gate's requirement has independently-downgradable halves, compose them independently and test the partial-tag matrix, not just all-on/all-off - the two-role disarm hid in the untested middle row. (Validity: 2026-10-17)

Recorded from retro RETRO0044.

## L-0080: Never run two tree-mutating verifiers concurrently: a mutation harness owns the working tree while it runs, a kill mid-mutant strands a

- **Added:** 2026-07-17
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: sprint.py near :405 documents that a concurrent process left staged mutants and `git add -A` committed them, and critic.py mutation runs own the working tree; single-writer for tree-mutating verifiers stands.

Never run two tree-mutating verifiers concurrently: a mutation harness owns the working tree while it runs, a kill mid-mutant strands a live mutant, and every other verifier then measures a lie - single writer, and re-verify the tree after any kill. (Validity: 2026-10-17)

Recorded from retro RETRO0044.

## L-0079: Backticks in shell-quoted artifact text are command substitutions

- **Tags:** tooling, shell, filing
- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true, partly mitigated: artifact.py:1720 --fields-file ARTEFACT.json (and lessons.py revalidate --fields-file, used in this pass) keeps prose out of the shell, but inline double-quoted backticks are still command substitutions, so the rule stands.

Filing CR0328/CR0329 through a bash heredoc-free inline call executed the backtick spans in their summaries as commands, silently punching holes in the filed text (caught because stderr printed 'sprint: command not found'). House rule: pass artifact bodies to the creators via single-quoted heredocs or files, never double-quoted inline strings with backticks; the creators could also grow a --summary-file input (fold into CR0316/CR0328 territory if it recurs).

## L-0078: A CLI flag is only shipped when a test exercises the CLI path: API-level tests stayed green while `--parent` was silently dropped at the

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: AGENTS.md 'Exercise every claim through the shipped entry point' says a library test cannot see a missing lane, the wiring being the part it does not exercise; this lesson at project-rule level.

A CLI flag is only shipped when a test exercises the CLI path: API-level tests stayed green while `--parent` was silently dropped at the argparse mapping - every new flag needs one main()-path test.

Recorded from retro RETRO0043.

## L-0077: Text that flows into `re.sub` is data, never a template: the same replacement-expansion class surfaced twice in one sprint (AC seeding, and

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and applied: artifact.py:422 and :2199 use callable replacements in re.sub (lambda mm: mm.group(1) + new_title), so text is never expanded as a template; the house rule is in the code.

Text that flows into `re.sub` is data, never a template: the same replacement-expansion class surfaced twice in one sprint (AC seeding, and historically the -G fix) - callable replacement is the house rule now.

Recorded from retro RETRO0043.

## L-0076: A reviewer must execute the mutant, not admire the test: two "killing tests" in one unit were proven vacuous by running the actual mutants

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: critic.py self-check requires mutants recorded against the unit's current diff and AGENTS.md 'Before you write' (testing.md#name-the-mutant-first) requires naming the mutant first; the vacuous-test class is what these target.

A reviewer must execute the mutant, not admire the test: two "killing tests" in one unit were proven vacuous by running the actual mutants (wrong section targeted, wrong sort order) - a test that cannot fail its mutant is the false-assurance class with a green badge.

Recorded from retro RETRO0043.

## L-0075: A sign-off request must carry the evidence it asks the principal to judge

- **Tags:** review, sign-off, ceremony, honesty
- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: sprint.py:4735 and :6735 compose the sign-off decision brief from committed records, and sprint sign refuses a principal who authored or reviewed a unit (AGENTS.md gate table); the request carries its evidence.

The RUN-01KXGPBN close asked the operator to sign off a retro written moments earlier and not yet shown: the prompt carried counts (6/6, gates green) but none of the content - the reviewer of record was structurally unable to review, converting the independent-principal gate into approval theatre. Any ceremony that requests a human decision must embed the decision brief (what shipped, what the critics rejected and how it was repaired, gate and cost evidence) in the request itself, and offer hold and delegate paths. Counts are not evidence; the operator caught it (CR0318, RFC0044 D2/D3).

## L-0074: A shared measurement helper (`flow.terminal_date`) grown for one status class (terminal) needs its assumptions re-checked per caller: the

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and applied: flow.py:114-125 terminal_date takes allow_revision_fallback, and its docstring says the fallback is wrong for a transient status like Blocked, so those callers opt out.

A shared measurement helper (`flow.terminal_date`) grown for one status class (terminal) needs its assumptions re-checked per caller: the revision-row fallback that is sound for Done is a guess for Blocked - the fallback became opt-out per call site.

Recorded from retro RETRO0042.

## L-0073: A reporting cap is a refusal in disguise: any bounded simulation/measurement that can hit its bound must refuse or flag at the bound, never

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and enforced: flow.py:285 MC_WEEK_CAP states a percentile AT the cap is refused, never reported; the cap is a refusal in code.

A reporting cap is a refusal in disguise: any bounded simulation/measurement that can hit its bound must refuse or flag at the bound, never present the capped value as measured (the MC_WEEK_CAP catch - same class as the RFC0041 reporting-honesty MAJORs).

Recorded from retro RETRO0042.

## L-0072: Calibrate an instrument's units to the measured process, not the literature's default: the MC forecast shipped with ISO-week buckets from

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and applied: flow.py:286-295 defaults the forecast to a day bucket because an agent-speed project's median cycle time is 0 days, keeping the ISO-week bucket as an option; reference-sprint.md:572 states it.

Calibrate an instrument's units to the measured process, not the literature's default: the MC forecast shipped with ISO-week buckets from human-team Kanban canon while this repo's own measured cycle time is 0 days and sprints are hour-scale sessions - the operator caught it at the close (CR0314: sprint-session and day buckets).

Recorded from retro RETRO0042.

## L-0071: Dogfooding a measurement feature on real project data finds confounders a fixture never will: the stale-run-state elapsed (43h from an

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: this repo dogfoods every measurement on its own sdlc-studio tree (AGENTS.md 'This repo dogfoods the skill') and the pre-push gate runs against real history, which is where confounders surface.

Dogfooding a measurement feature on real project data finds confounders a fixture never will: the stale-run-state elapsed (43h from an unrelated open run) only showed because the live repo HAD an old open run-state. Run a new measurement against the real repo before trusting it.

Recorded from retro RETRO0041.

## L-0070: A configured number is an input, not a fact: a price from config must be range-checked (a negative price subtracts, a zero is

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and enforced: telemetry.py:481 refuses a non-positive configured price (returns None, UNPRICED) instead of honouring it; the configured-number-is-an-input rule is in code.

A configured number is an input, not a fact: a price from config must be range-checked (a negative price subtracts, a zero is indistinguishable from unpriced) exactly as a user-supplied size is. The estimator's whole discipline is refusing to let an unchecked number wear the authority of a measurement - pricing is no exception.

Recorded from retro RETRO0041.

## L-0069: When two subsystems each claim to be the honest one (here: the estimate-vs-actual ratio and the spend report), they must read the SAME

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and applied: retro.py:1385-1389 falls back to the summed attempts via telemetry.attempts_of so the ratio reader sees the new shape, and the spend report reads the same telemetry; the same-source rule is held.

When two subsystems each claim to be the honest one (here: the estimate-vs-actual ratio and the spend report), they must read the SAME source for the same quantity, or they will contradict on exactly the interesting case (an escalation). A new richer schema (`attempts`) is a fork in the data until EVERY reader is taught to read it; reconcile them in the same change, and test a record in the new shape through BOTH readers.

Recorded from retro RETRO0041.

## L-0068: A "last-touched" date read as `max(every date in the file)` is defeated by any future or prose date (a deadline in the summary)

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and applied: reconcile.py:1984 computes today = date.today() with the comment that a future deadline is not a last-touched date, which is this lesson's clamp in code.

A "last-touched" date read as `max(every date in the file)` is defeated by any future or prose date (a deadline in the summary). Anchor a staleness date on the metadata fields and the revision-history region only, and clamp to today - a date in the future is not a date the artefact was touched.

Recorded from retro RETRO0040.

## L-0067: A grandfather/coherence check that resolves ids against a PARTIAL set (only the triage-type, non-terminal backlog) will false-flag anything

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: reconcile.py and sdlc_md.py resolve ids per artefact type through sdlc_md.artifact_files and status_vocab (status.py:198), keeping terminal distinct from absent; the whole-namespace-then-classify rule is the design.

A grandfather/coherence check that resolves ids against a PARTIAL set (only the triage-type, non-terminal backlog) will false-flag anything outside that set. An orphaned-dependency lens must resolve against ALL artefact types and distinguish terminal (resolved) from absent (mistyped), or it calls a live dependency broken and gives wrong advice. Resolve against the whole namespace, then classify.

Recorded from retro RETRO0040.

## L-0066: But fixing ONE enumerator is not fixing the invariant: sibling code paths (`reconcile.file_census` and a dozen direct `read_text` calls)

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: sdlc_md.py:2020 guards the enumerator but sibling readers such as reconcile.py:120 file_census remain separate code paths, so the end-to-end front-door verification advice stays necessary.

But fixing ONE enumerator is not fixing the invariant: sibling code paths (`reconcile.file_census` and a dozen direct `read_text` calls) bypass the enumerator entirely, so the crash relocated past the write and left a partial write - strictly worse. A robustness invariant ("one bad file never crashes a scanner") must be verified END-TO-END on the real public entry point, not on the helper in isolation: a test that exercises only the guarded function passes while the unguarded sibling on the same call path still crashes. When you claim "every scanner is now safe", grep every `read_text` on that path and drive the invariant through the front door.

Recorded from retro RETRO0040.

## L-0065: A crash inside a shared file-walk (`iter_artifact_files`) is not a local bug in the feature that tripped it - it is a latent fault in every

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and applied: sdlc_md.py:176 and :2020 catch (OSError, UnicodeDecodeError) in the shared walker and keep the bad file visible for a checker to name; the library-level hardening is in place.

A crash inside a shared file-walk (`iter_artifact_files`) is not a local bug in the feature that tripped it - it is a latent fault in every consumer. When a review finds "feature X breaks on a bad file", check whether the shared enumerator, not X, is the thing that should tolerate it: fixing it once at the library hardens every scanner rather than patching one call site and leaving the rest exposed. A `read_text` in a shared walker must catch `UnicodeDecodeError` as well as `OSError`.

Recorded from retro RETRO0040.

## L-0064: When an external contract is ambiguous (the Stop hook's `stop_hook_active` / exit codes), write to the intersection of the plausible

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: AGENTS.md records the pre-push hook reads an unreadable forge answer as not green yet does not block an offline push, an intersection-of-readings fail-safe; the ambiguous-contract rule stands for the Stop hook.

When an external contract is ambiguous (the Stop hook's `stop_hook_active` / exit codes), write to the intersection of the plausible readings and fail safe, rather than picking one and hoping. A hook that blocks a turn on its own uncertainty is worse than one that misses a reminder.

Recorded from retro RETRO0039.

## L-0063: A test suite that passes is evidence only about the cases it runs

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: best-practices/testing.md and AGENTS.md 'Exercise every claim' require the boundary-crossing case; a passing suite remains evidence only about the cases it runs.

A test suite that passes is evidence only about the cases it runs. This sprint's detector passed its own tests while carrying a BLOCKER, because every test exercised the *higher-id-closed-later* path and none the *lower-id-in-flight* one - the blind spot and the defect coincided. When a feature grandfathers on a boundary, test an item on **both** sides AND one that crosses it.

Recorded from retro RETRO0039.

## L-0062: A grandfather baseline for "work done before adoption" must be the **set** of ids that existed, not a highest-id/date cutoff

- **Added:** 2026-07-16
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: close_owed.py:14 and :67 and conformance.py:459 grandfather by dated or recorded baseline, with conformance.adopt_after as the remedy cutoff (conformance.py:782); the set-versus-cutoff boundary hazard is real for any new grandfather lane.

A grandfather baseline for "work done before adoption" must be the **set** of ids that existed, not a highest-id/date cutoff. A cutoff assumes id (or time) order tracks the state being grandfathered; whenever items can cross the boundary in a different order than they were created (a low-id unit still in flight at adoption), the cutoff silently forgives real debt. It also couples the mechanism to numeric ids, breaking on ULID/opaque id schemes. Set membership has neither hole and costs a list.

Recorded from retro RETRO0039.

## L-0061: A mandated ceremony with no mechanical enforcement is a silent control - it fires only when someone remembers, which under delivery

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: sprint.py:10751 BOUNDARY_STEPS includes close-down and sprint.py:10963 stops the run when the close-down chain does not complete (close-gate); the ceremony is mechanically enforced.

A mandated ceremony with no mechanical enforcement is a silent control - it fires only when someone remembers, which under delivery pressure is never. The close-down needs the same un-skippable treatment the quality gate got (RFC0042); the machine version of this bug was a whole sprint in a consuming project.

Recorded from retro RETRO0038.

## L-0060: A silence in one measurement path is not proof the quantity is unmeasurable

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: retro.py:44 states UNMEASURED means not-yet-captured, not unmeasurable, which is this lesson held in the reporting text.

A silence in one measurement path is not proof the quantity is unmeasurable. "Interactive = UNMEASURED" hardened a telemetry-capture gap into a false claim of unknowability, blocking the velocity loop for the exact sprints being run. Name the gap (not-yet-captured), then close it.

Recorded from retro RETRO0038.

## L-0059: A false negative in a test suite is a fixture-coverage gap, not proof of correctness: BG0151 shipped because every fixture used the NEW

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: sdlc_md.py:1177 extract_field handles standalone, plain and inline-run field shapes precisely because real projects carry legacy conventions; fixturing both conventions remains the rule for any reader of a convention.

A false negative in a test suite is a fixture-coverage gap, not proof of correctness: BG0151 shipped because every fixture used the NEW link style, so no test exercised the old-flow linking a real consuming project uses. When a feature reads a convention, fixture BOTH conventions - the new one you are building and the legacy one real projects still carry.

Recorded from retro RETRO0038.

## L-0058: Orchestrate existing, tested primitives before building new ones

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: scripts/migrate.py is glue over project_upgrade, migrate_v3 and reconcile, and AGENTS.md 'always look for a tool before doing anything by hand' states the same orchestration preference.

Orchestrate existing, tested primitives before building new ones. `migrate` is almost entirely glue over `project_upgrade` + `migrate_v3` + reconcile; the value was the aggregation and the honest deterministic-vs-needs-human split, not new migration logic. The reused pieces carried their own tests, so the new surface to test was thin.

Recorded from retro RETRO0037.

## L-0057: Monkeypatch through the module under test, not a re-import

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: scripts/tests/loader.py loads scripts by importlib, creating distinct module instances, so patching the module under test remains the safe form; the push gate runs the whole suite where isolation-green can fail.

Monkeypatch through the module under test, not a re-import. A test that patches `import version_check` can miss when the code under test holds a different instance of that module (the full suite's importlib loads create distinct instances). Patch `<module_under_test>.dependency`, which is the exact object the code will look up. A green run in isolation is not proof under the suite.

Recorded from retro RETRO0037.

## L-0056: Compute-once, read-many on a hot path: the hint recomputed a full-repo scan the dashboard had already done

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: status.py:544 takes the dashboard's awaiting value when passed in (awaiting if awaiting is not None else discovery_awaiting) so the hint does not rescan; compute-once-and-thread is applied.

Compute-once, read-many on a hot path: the hint recomputed a full-repo scan the dashboard had already done. When two callers in one command both need an expensive value, compute it once and thread it, or the most-run command pays double.

Recorded from retro RETRO0036.

## L-0055: A generated artefact must only assert what it verified

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and held in code: command_audit.py:844-848 builds the tool note from the checked flag (broken tools or 'tooling not checked') and :904 writes 'every tool runs' only when checked, so the persisted audit asserts only what was verified.

A generated artefact must only assert what it verified. The audit doc claimed "every tool runs" while the tool check was off by default; a persisted, unverified certification is a lie with a long half-life. Thread a `checked` flag and phrase the claim from it.

Recorded from retro RETRO0036.

## L-0054: A predicate that looks like an existing one may need DIFFERENT exemptions - do not copy the exemption set

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: status.py:187 discovery_awaiting keeps its own exemption set (intake counted, parked skipped) distinct from reconcile.py:1819 which exempts the intake state and inbox lane; the two predicates still differ on purpose.

A predicate that looks like an existing one may need DIFFERENT exemptions - do not copy the exemption set. `discovery_awaiting` and reconcile's `undecomposed` both find "childless discovery items", but the first must count intake (it awaits refinement) and skip parked, while the second skips intake. Name the exemption from the predicate's own purpose, not from the neighbour's.

Recorded from retro RETRO0036.

## L-0053: Wiring dormant machinery is a real deliverable

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: persona_resolve.py:236 resolve_consult and frame (:239, :288) are now called, and triage.py:183 calls persona_resolve.consult; wiring existing primitives remains the pattern.

Wiring dormant machinery is a real deliverable. `resolve_consult`/`frame` existed and were correct but callerless since the seats convergence; the value was latent until a ceremony ran it. Prefer wiring an existing, tested primitive to building a parallel one - the sprint was small precisely because the primitive was already sound.

Recorded from retro RETRO0035.

## L-0052: Text written into a structurally-delimited section must be sanitised against the delimiter

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: user text written into a ## delimited section can still forge a heading; triage.py:204-206 writes the consult audit onto the Issue from persona_resolve.consult output, so single-line collapsing of free text remains necessary there.

Text written into a structurally-delimited section must be sanitised against the delimiter. The consult audit section is bounded by `^##`; a question carrying `\n## ...` forged a heading inside it, breaking the in-place idempotent update. Collapsing user text to a single line before rendering closes it. Any "write user input into a markdown section" path has this shape.

Recorded from retro RETRO0035.

## L-0051: Extract a shared definition before the second caller: the `Parent:`/`Decomposed-into:` link writers moved to `lib.sdlc_md`

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: sdlc_md.py:3156 insert_after_status and :3181 write_decomposed are the shared link writers that refine and triage both call; no copy of either has reappeared.

Extract a shared definition before the second caller: the `Parent:`/`Decomposed-into:` link writers moved to `lib.sdlc_md` (`insert_after_status`/`write_decomposed`) the moment triage became refine's second caller, rather than copied - LL0016 applied prospectively for once, not after the drift.

Recorded from retro RETRO0034.

## L-0050: A dry-run pre-flight is only a safety net if it takes the SAME branch as the real mint on every configuration the real mint branches on

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: triage.py:161-173 pre-flights every bug through a dry-run mint with consolidate=False so it mirrors the real mint; the same-branch requirement is explicit in the pre-flight comments.

A dry-run pre-flight is only a safety net if it takes the SAME branch as the real mint on every configuration the real mint branches on. Here the real `artifact.new` routed a v3 Low-severity finding through consolidation while the dry-run did not, so triage's pre-flight passed and the real mint corrupted a CR. Test the pre-flight on each schema/config the create path forks on, not just the default.

Recorded from retro RETRO0034.

## L-0049: A migration must report what it cannot convert, never guess

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: migrate_v3.py:294-297 writes Size where sound and flags a story or bug carrying Effort without Points for human re-sizing rather than guessing; the report-never-guess behaviour is in the code.

A migration must report what it cannot convert, never guess. Effort predicts cost far worse than points, so there is no honest Effort->Points map; the migration writes a Size where the mapping is sound (Effort/points on a container) and FLAGS a delivery unit's Effort for human re-sizing rather than inventing a number the estimator would then be judged on.

Recorded from retro RETRO0033.

## L-0048: Extract a shared definition BEFORE writing the second caller, not after

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: sdlc_md.py:1029 size_for_points is the shared definition that refine and the migration both call; AGENTS.md 'use the deterministic tooling' and LL0016 keep the extract-first rule.

Extract a shared definition BEFORE writing the second caller, not after. The point->size band was copied into the migration and immediately became an LL0016 drift risk (two paths, one meaning); the fix was to move it to `sdlc_md.size_for_points` and have both `refine` and the migration call it. A helper worth copying is a helper worth sharing.

Recorded from retro RETRO0033.

## L-0047: Fix the friction the last retro logged, and log the new friction you hit

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: reference-sprint.md carries the friction-logging step and the project rule is to file every defect or friction as a Bug/CR; the retro still takes the last retro's friction as input.

Fix the friction the last retro logged, and log the new friction you hit. This sprint delivered the `refine add` that RETRO0031 flagged as a blocker, and it surfaced its own tiny friction (the missing import) - caught by tests, not worth a ticket, but named here.

Recorded from retro RETRO0032.

## L-0046: Reusing a hardened core is how a new feature inherits fixes instead of re-introducing bugs

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: refine.py `cmd_add` (refine.py:1181) shares `_decompose` (:262) with apply, so the shared core is the design; sharing the core is how the variant inherits validation and rollback.

Reusing a hardened core is how a new feature inherits fixes instead of re-introducing bugs. `add` got apply's up-front validation, rollback and atomic_write for free by sharing `_decompose`, and the review found nothing - where the two earlier refine reviews each found a real bug. Extract the shared core BEFORE adding the variant.

Recorded from retro RETRO0032.

## L-0045: The independence gate earns its cost on exactly the bugs the author cannot see: both this sprint's blocking bugs were invisible to the

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: AGENTS.md requires one independent reviewer per unit in a fresh context via critic.py brief, and sprint sign refuses a principal who authored or reviewed a unit (AGENTS.md gate table).

The independence gate earns its cost on exactly the bugs the author cannot see: both this sprint's blocking bugs were invisible to the author (one a cross-repo CWD read, one an orphan invisible to reconcile in the very projects the tool targets), and both were caught by a reviewer attacking the claim rather than re-reading the code.

Recorded from retro RETRO0031.

## L-0044: A multi-step create is atomic only if EVERY input is validated before the first write

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: refine.py `_decompose` (refine.py:262) and `_decompose_into` (:361) still validate up front and roll back; the all-inputs-before-first-write rule is the design of the create path.

A multi-step create is atomic only if EVERY input is validated before the first write. refine validated points up front but titles mid-loop, so a bad title orphaned an epic; the fix validates all titles (and the request's Status line) up front and rolls back on a residual IO error. Split validation is a half-promise of atomicity.

Recorded from retro RETRO0031.

## L-0043: A gate on a live workflow must default OFF for existing projects and be opt-in, or an upgrade breaks them

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: sdlc_md.py:1497 two_backlog_enforced defaults False (config-defaults.yaml:127-128 enforce: false) with this repo opting in via its own .config.yaml:175; the default-off-for-upgrades rule is in code.

A gate on a live workflow must default OFF for existing projects and be opt-in, or an upgrade breaks them. `two_backlog_enforced` (default off, one config line to turn on) is the pattern: ship the discipline, but let each project adopt it when ready, and never through a defaults-merge that flips it on globally.

Recorded from retro RETRO0031.

## L-0042: A bug's stated scope can be overtaken by an earlier change: BG0145 part (1) named a CLI restriction that RFC0038 had already removed

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: AGENTS.md 'Decide which by execution (git log -S), not by impression' and transition -> Fixed requiring a Verify line or ticked criterion mean a bug is confirmed to reproduce before it is closed; overtaken scope remains a live case.

A bug's stated scope can be overtaken by an earlier change: BG0145 part (1) named a CLI restriction that RFC0038 had already removed. Verify the defect still reproduces before fixing the described symptom; decline with the reason when it does not.

Recorded from retro RETRO0030.

## L-0041: A gate on the canonical creation path ripples into every test that used the old creation shortcut as a fixture (the Affects-resolve gate

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: artifact.py:1095 and :1276 refuse an Affects that resolves to nothing at the one creation seam, so a test creating an artefact with a dummy Affects still needs a real file; the fixture ripple persists.

A gate on the canonical creation path ripples into every test that used the old creation shortcut as a fixture (the Affects-resolve gate hit 12 files, ~140 cases). Budget the fixture migration as part of the gate.

Recorded from retro RETRO0030.

## L-0040: The migration story for a breaking model change is part of the change, not an afterthought

- **Added:** 2026-07-15
- **Review-by:** 2027-01-25

The migration story for a breaking model change is part of the change, not an afterthought. This session shipped a universal, non-schema-gated two-backlog + sizing model; an existing consuming project upgrading to it would find its CR workflow refused (G1), its childless-CR completion blocked (G2), and its stale-Affects units ungroomed - with no opt-in and no data migration. Because it is all unreleased (freeze until ~2026-07-21) there is a window to build the migration before it ships, and a breaking change earns a semver-major bump.

Recorded from retro RETRO0030.

- **Status:** Closed - Time-boxed advice that is complete: it asked for a migration before the 2026-07-21 freeze, and scripts/migrate.py and scripts/migrate_v3.py now ship it (migrate_v3.py:294-297 flags Effort for re-sizing) with two_backlog default off (sdlc_md.py:1497); nothing remains to do.

## L-0039: Decomposition makes the estimate accurate (LL0038 again): a single-shot CR sized 8 decomposed to 14, the same 1.75x the prior experiment

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: sprint plan splits units over the threshold (AGENTS.md gate table) and refine decomposes; decomposed sizing remains the forecast method, per flow.py per-period counts.

Decomposition makes the estimate accurate (LL0038 again): a single-shot CR sized 8 decomposed to 14, the same 1.75x the prior experiment found. The way to a good forecast is smaller, decomposed units - not a cleverer single-shot guess.

Recorded from retro RETRO0029.

## L-0038: A gate that changes the canonical creation path ripples into every test that used the old path as a generic fixture

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: L-0041 repeated the ripple and the pre-commit lanes select test modules by touched file; the fixture migration cost of a creation-path gate remains a plan-time item.

A gate that changes the canonical creation path ripples into every test that used the old path as a generic fixture. Budget the migration as part of the gate, not as a surprise: the ripple is the measure of how load-bearing the old behaviour was.

Recorded from retro RETRO0029.

## L-0037: A worked-around symptom is a bug you have not found yet

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: AGENTS.md 'Review is independent of the author' and the rule to file findings with file_finding.py; hand-editing a triggering artefact to dodge a defect is the workaround this forbids.

A worked-around symptom is a bug you have not found yet. US0120's parenthetical defect was first met by hand-editing the artefact that triggered it (stripping the annotation off CR0271); an independent reviewer, not the author, is what turned that workaround into a root-cause fix. Verify by an independent actor attacking the claim, not the author re-reading it.

Recorded from retro RETRO0029.

## L-0036: A cross-cohort figure must be refused, not pooled - now enforced in code (`collate` refuses a rate across `(project, model)` cells), so the

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and enforced: retro.py:2850 states pooling per-(project, model) rows is the cohort confound and refuses it, as the lesson itself says.

A cross-cohort figure must be refused, not pooled - now enforced in code (`collate` refuses a rate across `(project, model)` cells), so the confound that produced two withdrawn findings this week cannot recur through the tooling.

Recorded from retro RETRO0028.

## L-0035: A single-estimator one-shot size read off an artefact is a weak input

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: reference-sprint.md:272 sizes by relative points with the measured batch rate, and refine decomposes before sizing; a single-estimator one-shot read is still not the input.

A single-estimator one-shot size read off an artefact is a weak input. The method that predicts is relative, decomposed and multi-estimator; it converges (independent estimators agree) and it is honest (nobody sees the outcome).

Recorded from retro RETRO0028.

## L-0034: Decomposition makes the estimate accurate, not only the Done checkable

- **Added:** 2026-07-15
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: sprint plan refuses a batch whose units lack Affects or Points or exceed the split threshold (AGENTS.md gate table), and refine sizes decomposed units; decomposed estimates remain the method.

Decomposition makes the estimate accurate, not only the Done checkable. A blind decomposed estimate hit the batch to 1.00x where a whole-unit single-shot guess missed by half. Break a request into the stories you would actually create, and the hidden work - and the honest size - surfaces.

Recorded from retro RETRO0028.

## L-0033: Counting is not a worse estimator than modelling; it is the honest one when no signal exists

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: flow.py:194 and :374 count delivered items per period and the forecast simulates over those counts, the honest counting method this lesson endorses; no modelled predictor replaced it.

Counting is not a worse estimator than modelling; it is the honest one when no signal exists. The forecast that gives up on prediction is currently outperforming everything built to predict.

Recorded from retro RETRO0027.

## L-0032: Merging units to dodge a file collision destroys per-unit measurement

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: sprint.py:2205 detects identical-Affects pairs and :2432 states disjointness is only as good as declared Affects, so the plan sequences colliding units instead of merging them; per-unit Points stay the measured base.

Merging units to dodge a file collision destroys per-unit measurement. Two units of this sprint are UNMEASURED because they were delivered inside a third's agent - and merging also makes units bigger and less uniform, which is the opposite of what the evidence says to do.

Recorded from retro RETRO0027.

## L-0031: Setting the bar BEFORE measuring is what makes a negative result possible

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: retro.py:838-841 requires the Points to be the sizes the PLAN recorded, never sizes revised after the outcome, because the column matters only if it was written down before anyone knew; the estimate-versus-actual bar is fixed before the measurement.

Setting the bar BEFORE measuring is what makes a negative result possible. CR0262 could drop the forecast only because it had written down, in advance, what "good enough" meant.

Recorded from retro RETRO0027.

## L-0030: The presence of a field is not a measurement

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: retro.py:44 and :1116 report an absent value as UNMEASURED, not zero, so a missing field is not scored as a measurement; the rule is held in the reporting code.

The presence of a field is not a measurement. Scoring a missing value as zero turns "when this field was invented" into a predictor, and the calendar will happily correlate with anything that grew over time.

Recorded from retro RETRO0027.

## L-0029: A signal that flips sign between cohorts is not a predictor, however good its pooled correlation looks

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: retro.py:2802 records a field that flipped sign between cohorts as a withdrawn finding and retro.py:2850 refuses pooled (project, model) rows; the rule is in code.

A signal that flips sign between cohorts is not a predictor, however good its pooled correlation looks. Check WITHIN the groups before trusting an average ACROSS them.

Recorded from retro RETRO0027.

## L-0028: A plausible story fitted to a real pattern is not a finding

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: this is the lesson that replaced the retracted L-0021; retro.py:3277 still warns that before/after is a cohort split and a fitted story is not a finding.

Recorded from retro RETRO0026.

## L-0027: Before tuning a coefficient, check that its input correlates with the target at all

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: complexity.py:288-362 still emits max_cognitive with applicable, and retro.py reports correlation floors (retro.py:3184) before any coefficient is trusted; the check-the-input-first rule stands.

Recorded from retro RETRO0026.

## L-0026: A resolved-but-inapplicable signal is more dangerous than an absent one

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and guarded in code: retro.py:44 treats UNMEASURED as not-yet-captured and complexity.py:288 tells readers to read applicable before max_cognitive for exactly this reason (a resolved but inapplicable score).

Recorded from retro RETRO0026.

## L-0025: A decoy field beats a correct one: `templates/core/cr.md` carried a placeholder `**Effort:**` above the real one, and `extract_field` takes

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: sdlc_md.py:1177 extract_field still captures the first matching field, so a placeholder above the real one still wins; templates/core/cr.md no longer carries the decoy Effort line (grep finds none), removing the instance but not the hazard.

Recorded from retro RETRO0026.

## L-0024: The tool that measures a sprint cannot be built by that sprint

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: retro.py reads committed records after the close (retro.py:92), so the measuring tool stays outside the sprint it measures; the circularity hazard is unchanged for any new instrument.

Recorded from retro RETRO0026.

## L-0023: A record kept in a gitignored working directory is not a record

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: .gitignore:15-16 keeps sdlc-studio/ committed with only .local ignored, and retro.py:92 and :3982 move a legacy gitignored lessons log into the committed one; the rule is applied in the tree.

Recorded from retro RETRO0026.

## L-0022: Verify a fix by ATTACKING it, not by re-reading it

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: AGENTS.md 'Exercise every claim' and the QA seat's mutant execution via critic.py brief hold the attack-not-reread rule; critic.py self-check requires claims and mutants against the current diff.

Recorded from retro RETRO0026.

## L-0021: RETRACTED - A calibration fitted to work delivered under one standard does not survive a change in the standard

- **Added:** 2026-07-14
- **Retracted:** 2026-07-14
- **Review-by:** 2027-01-25

Recorded from retro RETRO0025. **Refuted by measurement the same day, and kept here retracted
rather than deleted, because a lesson that was wrong is itself the lesson.**

The claim was that the estimator failed because the briefs got harder each sprint, so the work per
unit grew beneath it. The data says otherwise. Tokens PER ACTION are flat across all three sprints
(2,868 / 2,294 / 2,302 tokens per tool-use), so nothing about the cost of doing the work moved. What
rose was the NUMBER of actions, which is a property of the units, not of the standard they were held
to.

The real cause is simpler and was sitting in the same data: the forecast seed is INERT.
`max_cognitive` correlates with actual cost at r = -0.006 and with actual work at r = -0.001 across
16 measured units. It carries no signal, so no coefficient could ever have worked. See CR0262.

**The lesson that replaces it:** a plausible story fitted to a real pattern is not a finding. The
moving-standard narrative explained the misses, was written up as a lesson, and was wrong - because
it was never tested against the data that was already on disk. Before recording WHY something failed,
check whether the number that would falsify the explanation is already in reach. Here it was one
correlation away.

- **Status:** Closed - Retracted the day it was filed: the lesson records it was refuted by measurement and kept only as a record; its replacement L-0028 stays open, so this stub carries no live advice.

## L-0020: When two tools judge the same artefact, they must agree on what a COMPLETE one is

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: conformance.py:71 DONE_STAGES and transition.py's Done gate judge the same artefact, and a shared definition of complete is still needed; two separate readers remain.

Recorded from retro RETRO0025.

## L-0019: A gate belongs in the command people actually run, not in a step they are told to run

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and now gated: promoted to LL0027 in lessons/_index.md; the pre-commit and commit-msg hooks and the pre-push gate (AGENTS.md 'What will refuse you') put the gate in the command people run.

Recorded from retro RETRO0025.

## L-0018: Reporting a model's fit against the same data it was fitted to is training error, not validation

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: retro.py:3184 floors cohorts and the velocity history is kept as committed evidence (retro.py:92); reporting in-sample fit as validation remains a hazard for any new calibration, so the rule stands.

Recorded from retro RETRO0025.

## L-0017: An estimate re-derived at judgement time from the constants it is meant to be judging is not a prediction, and a loop built on one cannot

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: sprint plan prices from Points and the measured batch rate (reference-sprint.md:272) rather than re-deriving an estimate from the constants it is judged against; the rule against self-referential estimates stands.

Recorded from retro RETRO0025.

## L-0016: Verify a subagent's work through the public path before trusting the report

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: AGENTS.md 'Exercise every claim through the shipped entry point' and critic.py brief refusing an unrecorded self-check (review.author_self_check: block) hold this rule.

Recorded from retro RETRO0024.

## L-0015: Sweep for the class, do not fix the enumerated list

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the class-sweep rule recurs in L-0065 and L-0066 on read_text, and the sdlc_md.py:176 and :2020 handlers were applied to the class; AGENTS.md hook lanes are class-wide guards, not enumerated fixes.

Recorded from retro RETRO0024.

## L-0014: A narrow sample can make a variable look constant; widen the RANGE before concluding

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a measurement rule: retro.py:3184 sets a units floor below which a cohort says nothing and retro.py:2850 refuses pooling; widening the range before concluding is the stated practice.

Recorded from retro RETRO0024.

## L-0013: When two code paths express the same filter (`review_prep`'s two persona-index excludes), give them one shared definition or they drift -

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and visibly so: PERSONA_INDEX_NAMES is still defined twice (review_prep.py:33 and status.py:119) with the same value, so the drift risk the lesson names remains in the tree.

Recorded from retro RETRO0023.

## L-0012: A gate that enforces a ceremony should be run against its own delivery as the acceptance test: CR0253 flagging its own sprint's stale

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the repo runs its gates over its own delivery (pre-push gate.py --boundary push on every pushed commit, per AGENTS.md); no ceremony gate is exempt from being its own acceptance test.

Recorded from retro RETRO0023.

## L-0011: A false finding is not free: under a disposition gate that turns findings into work, a confident wrong one manufactures work for everyone

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: critic.py:4638 undispositioned_plan_findings still turns findings into work needing a disposition, so a confident wrong finding still manufactures work; AGENTS.md 'only a regression blocks' limits but does not remove the cost.

Recorded from retro RETRO0022.

## L-0010: Marking a work item Complete while part of its acceptance criteria is unwired is the same failure as a tool reporting a success it did not

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true and gated: transition -> Done refuses a story whose executable ACs have not passed (AGENTS.md gate table), the mechanical form of this rule; a CR is Complete only when its children are resolved (transition.py:443).

Recorded from retro RETRO0022.

## L-0009: A guard that branches on invocation mode must be tested in every invocation mode; assert on output, not the exit code, when the failure

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the repo's gates run in distinct modes (pre-commit, commit-msg and pre-push per AGENTS.md) and the 'exercise every claim through the shipped entry point' rule demands each mode be driven; the multi-mode hazard is unchanged.

Recorded from retro RETRO0022.

## L-0008: A gate that checks an artefact exists, not what is in it, is satisfied by `touch`

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: verify_ac.py:300 treats an all-skipped run as empty rather than green, and transition -> Done needs executed ACs (AGENTS.md gate table); a lane that checks presence only is still satisfiable by touch, so the rule stands.

Recorded from retro RETRO0022.

## L-0007: A hazard found by calling a private helper directly may already be guarded at the only call site that matters - reproduce through the

- **Added:** 2026-07-14
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true as a review rule: AGENTS.md 'Exercise every claim through the shipped entry point before asking for review' states the reproduce-through-the-call-site rule that this lesson records.

Recorded from retro RETRO0022.

## L-0006: A security fix needs a leading/trailing/interior placement matrix, not just a character list

- **Tags:** security, injection, testing, review
- **Added:** 2026-07-13
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: the check-versus-write bypass class is unchanged (sdlc_md.py holds the shared writers; values are still checked and written in separate steps); the placement-matrix advice holds and no change removed the surface.

BG0115 refused a complete character class (every str.splitlines character plus NUL) at the guard, passed a green 1863-test suite, and still shipped its headline RCE - because the guard checked the STRIPPED value while the writers emitted the RAW value, so a LEADING newline slipped through. The character class was exhaustive; the placement matrix was not. When hardening an injection surface, the value that is CHECKED must be byte-identical to the value that is WRITTEN - any normalisation (strip, casefold, collapse) between check and write is a bypass waiting to be found. Test the payload at every position (leading, trailing, interior) against every writer, and drive it END TO END (does the injected content actually reach the sink and execute), not just 'the guard raised'. The green suite was green because every test used interior breaks - the tests encoded the same false assumption as the code. An independent reviewer caught it; a self-review would have re-run the interior-break tests and signed off.

## L-0005: Editing a shared template obliges you to run its renderer's tests

- **Tags:** testing, templates, shared-surface
- **Added:** 2026-07-13
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: artifact.py:958 still substitutes RETRO-{{retro_id}} at the sites it knows, so a new placeholder site in a template still leaks; the pre-commit hook selects test modules by staged file and the pre-push gate runs the full suite.

A unit edited templates/reviews/retro.md and added a second {{retro_id}} site. The renderer (artifact.py_render_meta) substitutes that placeholder only at the sites it knows about, so the new one leaked into every rendered retro - caught only by the full suite, because the author ran only their own targeted modules per their file boundary. A narrow test boundary is right for avoiding collisions, but a template is not a leaf: it has a consumer. If you edit a template, run the tests of whatever renders it, even when that renderer is outside your surface. The corollary bit too: the obvious fix (make the renderer substitute the placeholder globally) would have been WRONG - the renderer emits the display form RETRO-0001 while the flag globs the file form RETRO0001*.md, so a global replace would have baked a silently-matching-nothing command into every retro. Read the render output before choosing the fix.

## L-0004: Add a closing full-diff pass when units share a file

- **Epic:** EP0014
- **Tags:** review, composition, sprint-close
- **Added:** 2026-07-13
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: units sharing a file still interact; sprint.py:2205 detects identical-Affects pairs and :2432 states disjointness is only as good as declared Affects, and the push gate runs the whole tree (AGENTS.md), which is the closing full-diff pass.

When several stories touch the same creation path (artifact.py/status.py here), a per-unit critic that sees only one story's diff cannot see cross-unit interactions. The closing full-diff pass caught a tranche silently dropped by US0067 consolidation x US0068 pass-through - invisible to both per-unit reviews by construction.

## L-0003: Read every creation path, not the one the design note names

- **Epic:** EP0014
- **Tags:** review, creation-paths, era-gating
- **Added:** 2026-07-13
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: file_finding.py and artifact.py new/batch remain separate creation entry points, so a gate on one still needs its siblings checked; AGENTS.md 'use the deterministic tooling' names both.

US0065's design note said 'artifact.py files findings into inbox', but the primary agent finding-filer was file_finding.py - which the note never mentioned. The independent critic caught the bypass. A design note names the tidy path; grep for every code path that does the thing (here: every artefact-creation entry point) and gate all of them, or one is a silent bypass.

## L-0002: Forward-port via install.sh, not per-file cp

- **Context:** Determinism sprint - this repo dogfoods the skill against its own source
- **Symptom:** Each delivered unit was synced to `~/.claude/skills/...` with hand-picked `cp`; drift was only caught by an end-of-sprint `diff -rq`
- **Root cause:** Reconstructing the changed-file set from memory misses a file
- **Fix:** Sync with `install.sh --local` (whole-tree, deterministic), then `diff -rq` to verify
- **Applies to:** Any change touching `.claude/skills/sdlc-studio/` in this repo
- **Added:** 2026-07-13
- **Review-by:** 2027-01-25
- **Status:** Closed - Advice is now wrong: AGENTS.md:173 says never run install.sh from the dev repo because its sweep clobbers the git-tracked tree, and tools/forward-port.sh (--check, --yes) is the guarded mirror that replaced per-file cp and bare install.sh.

## L-0001: Amend the AC in the same unit when the implementation deviates

- **Context:** Determinism sprint - CR0008 and CR0007
- **Symptom:** The build deviated from the AC (config "scripts read it"; resume "reads the WF table") and the AC silently went false; the independent critic caught both
- **Root cause:** Better engineering shipped without updating the contract it was measured against
- **Fix:** When deviating, reword the AC + add a revision-history note in the same commit; the critic checks AC-vs-delivered-behaviour
- **Applies to:** Every CR/story whose delivery differs from its written AC
- **Added:** 2026-07-13
- **Review-by:** 2027-01-30
- **Revalidated:** 2026-11-01 - Still true: AGENTS.md 'Review is independent of the author' and critic.py brief carry the canonical ACs as law, so a deviation from the written AC is what the reviewer flags; no rule or gate has relaxed it.
