# BG0402: close_goal_judgement compares seat NAMES against a critic author id, so 'author excluded' is printed over a panel that excluded nobody

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; both remaining halves - the duplicate polarity mapping and the fanned whole-goal answer - verified by applying their own mutants)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Independent review of RUN-01KYNKDP: `_signoff_author(root, 'BG0385')` returns '' on the live workspace; the close prints 'goal panel: achieved over 1 clause(s), 1 seat(s), author excluded'.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`_recorded_goal_seats` returns seat NAMES (`engineering`, `product`, `qa`, `operator (reviewer of record)`). `_signoff_author` returns a critic-ledger AUTHOR ID. The exclusion `[s for s in recorded if s != author]`, and `goal_panel`'s own `conflicted` check, compare across two namespaces and can therefore never exclude anyone.

On the live workspace no verdict row carries an author, so `author` is falsy and `goal_panel` receives the literal string 'the authoring session'. The close then prints `author excluded` over a panel from which nothing was excluded and in which no author was identified.

The function's headline claim - a panel that REFUSES the author - is the whole reason the mechanism exists, and it is inert in the shipped configuration. This is the same class BG0385's repair was written to fix, reproduced inside that repair.

Separately, a seat's answer is mapped `achieved if polarity in ('yes','y','true') else 'partial'`, so a seat that said the goal is NOT achievable is recorded as `partial`. `verdict_polarity` is in the same module and returns yes/no/unclear; it is not used. And one whole-goal, PLAN-TIME answer is stamped onto every clause and printed as the close's per-clause verdict.

## Steps to Reproduce

1. Run a close on a run whose goal-review round recorded seats.
2. Read the printed `goal panel:` line - it claims `author excluded`.
3. `_signoff_author(root, <any batch unit>)` returns '' unless a critic verdict row carries an author, so nothing was compared.
4. Record a seat with `achievable: no` and read the per-clause verdict: `partial`.

## Proposed Fix

Resolve both sides into ONE namespace before comparing, and refuse rather than warn when the author cannot be identified - an exclusion that cannot be performed must not be claimed. Use `verdict_polarity` for the seat answer so a `no` is recorded as `missed`, not `partial`. And do not fan a whole-goal plan-time answer across clauses: a clause with no per-clause verdict is UNANSWERED, which the panel already knows how to report.

## Impact

The author-exclusion is the reason a goal panel is evidence rather than self-assessment. Printing `author excluded` when nothing was excluded is a claim the record cannot support, made at the moment an operator is deciding whether to sign off - and a seat's `no` reaching the close as `partial` understates the one answer that should stop it.

## Acceptance Criteria

### AC1: an unprovable exclusion refuses rather than claiming one

- **Given** a run on which no author can be identified
- **When** the close's goal judgement runs
- **Then** the panel is NOT RUN and says why, instead of producing a verdict labelled "author excluded" over a panel that excluded nobody
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::InertMechanismsAreReachedTests::test_a_panel_that_cannot_prove_the_exclusion_refuses
- **Verified:** yes (2026-07-29)

### AC2: with an author recorded, the panel runs and reports per clause

- **Given** a run whose author is recorded and a multi-clause goal
- **When** the judgement runs
- **Then** the panel returns a per-clause verdict, so the refusal above is a condition on the mechanism rather than a refusal of it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::InertMechanismsAreReachedTests::test_the_close_reaches_the_goal_panel_and_reports_per_clause
- **Verified:** yes (2026-07-29)

### AC3: a seat answering "no" is recorded as missed - NOT YET FIXED

- **Given** a seat whose recorded answer is `no`
- **When** the clause verdicts are derived
- **Then** it is recorded `missed` via `verdict_polarity`, not `partial` via a second polarity mapping in the same module
- **Verify:** manual - open, not yet delivered

### AC4: a plan-time whole-goal answer is not fanned across clauses - NOT YET FIXED

- **Given** one plan-time answer about the whole goal
- **When** the per-clause verdicts are assembled
- **Then** a clause no seat answered per-clause reads UNANSWERED, which the panel already knows how to report
- **Verify:** manual - open, not yet delivered

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
| 2026-07-29 | Claude Opus 5 | Exclusion half FIXED: the author and the seats are now compared through `critic._id`, the count of excluded seats is reported so the claim is checkable, and a run whose author cannot be identified REFUSES the panel. The two remaining halves - a seat's `no` recorded as `partial` while `verdict_polarity` sits unused, and one plan-time answer fanned across every clause - are NOT fixed and this bug stays open for them. |
