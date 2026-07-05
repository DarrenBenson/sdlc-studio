# RETRO-0011: Token-optimisation tranche - the anchor window, the self-recommending archive, and Sam takes the seat

> **Date:** 2026-07-05
> **Batch:** CR0160-CR0165 (operator-approved token-optimisation plan + two mid-tranche operator filings)
> **Goal:** highest process quality at lowest token cost before v3.5.0
> **Delivered:** 6 / 6   **Blocked:** 0

## Delivered

- CR0160 - index-bloat advisory; the dormant archive process now recommends
  itself. First live run: 265 rows archived, live indexes 332 -> 83 lines.
- CR0161 - LATEST.md is a window, not a ledger (165 -> ~55 lines, ~1.2k tokens
  saved at every session start) with a doc_freshness ceiling so it cannot regrow.
- CR0162 - `artifact.py revision`: deterministic close-out appends (used for
  this tranche's own close).
- CR0163 - slice-read rule in SKILL.md; epic/story Reading Guides anchored.
- CR0164 - `reconcile apply` appends missing index rows (operator field
  transcript: an agent hand-authored 23 rows because the class was report-only).
- CR0165 - the critic is a seat: recorder warns on undeclared reviewers; the
  close pass runs AS the QA seat's review render (operator observation).

## What went well

- Two operator interjections landed mid-tranche and both shipped inside it:
  the CR0164 field transcript and the CR0165 persona question.
- The critic loop ran three rounds (anonymous, then Sam-framed): 1 HIGH
  (alias column got `--` - apply planting drift it could not repair), 2 MEDIUM
  (trailing-view capture, then its tie residual), assorted LOWs - every fix
  seen RED first, every repro re-run by the same instance before APPROVE.
- Sam's review render proved sharper than the anonymous framing: the tie
  finding was expressed as "that green cannot fail" - the seat card's own line.
- CR0165 live-proved itself at close: six verdicts recorded under the seat,
  silently; an anonymous string would now warn.

## What was hard

- My first tie test pinned the implementation, not the demanded behaviour
  (strict-majority fixture, blind to the 1-vs-1 tie). The seat lens caught it.
- The master-table disambiguator had to respect a shipped layout that
  legitimately ties (single-epic story index) - structural ranking with
  position as the LAST resort, and a loud refusal for true mirrors.

## Lessons

- Reaffirmed L-0004/Sam's line: a fixture that proves the majority case can
  still be blind to the boundary the finding named - re-run the CRITIC'S
  fixture, not a friendlier cousin.
- Process observation (CR0165's origin): a discipline can hold mechanically
  while its framing drifts out - encode the framing in a deterministic check
  the moment you notice.

## Metrics

- Duration: ~2.5h plan-approval to close · Units: 6/6, green commit each ·
  Critic rounds: 3 (Sam-framed final), verdicts recorded under the QA seat ·
  Suite: 1160 green (1162 static) · Mutation: reconcile surface clean at close ·
  Live: detect 0 drift, advisories silent post-archive, LATEST.md fresh.
