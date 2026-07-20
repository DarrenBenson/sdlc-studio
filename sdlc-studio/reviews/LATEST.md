# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXZHGD** (the close and its pre-flights tell
> the truth, 2026-07-20, RETRO-0058). Supersedes the RETRO-0057 picture.

## Where the pipeline is (2026-07-20)

**RUN-01KXZHGD is built, verified and reviewed**: 6/6 units, 14 points, closing review
**APPROVED at round 2** (one REJECT, one repair round, plus two follow-ups fixed without a
further round). This is **Phase 0 of the approved v5.0 backlog plan**.

Operator decision on the plan: **v5.0 holds for the full backlog**, enablers first, CR0347 before
any parallel fan-out. Roughly 250-270 points remain across 28 requests, 3 RFCs and the delivery
backlog.

## What shipped

- **BG0214** - `artifact.py close --dry-run` runs the same gate ladder as the real close. It
  returned a synthesised target before `transition` was reached, so it previewed closes the real
  run refused and exited 0 where the real path exits 1.
- **BG0216** - the blocking `lessons-summary` lane can be satisfied again. Proven by restoring the
  exact wording that deadlocked the RETRO-0057 close: the lane is green with no reword.
- **US0272** - the retrospective record closing **CR0342**, which shipped in `d046ae8` and was
  never closed.
- **US0273-US0275** - `sprint preflight` reports every unmet close prerequisite in one read-only
  pass, including the per-unit sign-off prerequisites that previously surfaced last.

Suite **3,291 skill + 243 tools green**.

## The correction that changed the plan

**CR0342 was already delivered.** It was the stated reason Phase 0 had to precede bulk refinement
("refine output cannot pass the gate"); that constraint had been lifted months of commits earlier.
The plan's own founding premise was stale. **Phase 4 can therefore start earlier than the approved
plan assumes.** A sweep of all 26 open CRs for the same built-but-not-closed pattern found no
others, so the backlog estimate holds.

## The CODE leg - two rounds

| Round | Findings | Outcome |
| --- | --- | --- |
| 1 | 3 MAJOR + 3 MINOR | REJECT |
| 2 | 2 MINOR (fixed, no further round) | APPROVE |

**Two of round 1's three MAJORs were the exact defect this sprint exists to remove, in the code
that removes it.** The pre-flight reported READY for a unit the close then refused, because it
checked the critic prerequisites and never the AC-verify gate. And `close` did not report
everything first: the call sat below refusals that return early, so an unjudged goal hid every
other blocker - serial discovery, reintroduced by placement.

The third is worse. The BG0214 fix introduced the **inverse** divergence, and **my own test worked
around it** by annotating by hand before the dry run. The workaround shipped; the defect went
unnoticed until the reviewer read it.

Round 2 verified the repairs independently, re-derived the mutation table on pristine copies, and
proved `pending_fields` write-safety **statically** rather than empirically. It then found a
regression the repair itself introduced: the done-gate preview caught too narrow an exception, and
because the placement fix moved the report above every refusal, that escape took down closes which
would otherwise have refused cleanly.

**Recurring:** the surviving defect has now been in prose or a test rather than in behaviour for
four consecutive rounds.

## Next steps

- **Phase 1** - **BG0215** (a timed-out mutation harness leaves the mutant on disk and the restore
  captures it), **CR0363** (a mutation run scoped below its target over-reports absence),
  **CR0350** (record interactive token actuals). Make the measurements trustworthy before
  spending on optimisation, since RFC0048 D3 would make mutation a blocking gate.
- **Phase 2** - **RFC0048** (close the decision table first: **D3 and D6 are settled by the
  operator but were never written back**, so all six rows still read Open) and **EP0085 / CR0358**
  (bound the review loop). Ends with a falsifiable checkpoint: re-measure points per sprint
  against the ~10 baseline and stop if it has not moved.
- **BG0218** (new, High) - the velocity record wrote Points `-` for a sprint that delivered 14.
  Unforecast units are excluded from the points series as well as the ratio columns. **The Phase 2
  checkpoint is measured in points per sprint, and that number is currently not being written
  down.**
- **CR0369** (new, High) - a sprint needing an operator decision should ask a structured question
  rather than stop in prose. Operator-reported.
- Filed this run: **CR0367** (the commit-message check runs after the ~140s gate), **CR0368**
  (conformance says `missing critiqued` without naming which half), **BG0217** (validate prints
  warnings its own counter reports as zero).
- **CR0351** (M) - a backtick in a shell argument silently empties the field it documents.
  **Still unbuilt**; artefacts filed this run deliberately avoided backticks to work around it.
- Standing: **RFC0046** needs D1 closed or an override; **CR0355** is a launch-day action;
  **CR0319** is the release cut itself. Release freeze holds.

## Lessons this run paid for

L-0149 to L-0153. **Check whether the work is already done before building it.** **A plan's
premises decay** - re-verify the constraint that fixes a plan's ORDER before following it. **When
a defect is fixed, the tests that were passing because of it will fail** - that is the fix
working. **A fixture missing a config key can silently disable the whole branch under test.** **A
pre-flight is worth building where a gate is a chain.** And one from the mutation harness: a
mutation that does not apply is indistinguishable from a mutant that survives.
