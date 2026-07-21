# BG0246: batch_history excludes every interactive sprint, so the plan's 'real cost input' silently shows only old runner-era sprints

> **Status:** Fixed
> **Verification depth:** functional - the exclusion was reproduced from the two velocity rows the bug names (RETRO0060 and RETRO0061, both `Measured` 0), the block was then re-rendered against this repo's real VELOCITY.md and both now appear with their per-unit cost and a `sprint-level` label. Seven mutants hand-applied across `batch_history` and `_render_token_forecast`; all seven killed.
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`sprint.batch_history` requires BOTH a non-zero `actual_tokens` AND a non-zero `measured` column, where `measured` counts units carrying PER-UNIT telemetry. An interactive sprint has no runner and therefore no per-unit records, so measured is 0 even when the sprint-level harness capture recorded a real total. Every interactive sprint is dropped. Observed planning the follow-up batch on 2026-07-21: the plan printed 'batch history (what sprints ACTUALLY cost - the real planning input)' listing RETRO0025 through RETRO0028 at 128,471 to 188,022 tokens per unit, and silently excluded RETRO0060 (2,390,624 tokens over 9 units = 265,625/unit) and RETRO0061 (1,265,392 over 13 units = 97,338/unit) - the two most recent sprints with measured totals. RETRO0060 alone is 1.4x the per-unit cost of the most expensive sprint shown. The rows the planner does display are the OLDEST measured data in the file, from the runner era, and nothing in the output says two newer measured sprints were left out. This is the project's recurring defect class - a number presented as authoritative that quietly omits the most relevant evidence - and it sits in the one block the docstring calls 'what the operator should plan against'. It also interacts with the stalled calibration: the plan says 'this project has 3 unit(s) of its own evidence so far; the rate becomes ITS measurement at 5', and that counter cannot advance while the same filter discards the sprints that would advance it.

## Acceptance Criteria

- [x] **AC1:** A sprint with a real total but no per-unit telemetry appears in the plan's batch history, deriving per-unit cost from the total.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint.py
- [x] **AC2:** Every row states its basis, `per-unit` or `sprint-level`, so the two kinds of evidence cannot be read as one.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint.py
- [x] **AC3:** The hidden-variance caveat is printed when, and only when, a derived row is actually shown, so it is neither missing nor noise.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint.py

## Steps to Reproduce

1. Ensure the velocity history contains at least one interactive sprint with a sprint-level actual and measured=0 (RETRO0060 and RETRO0061 both qualify today). 2. Run sprint.py plan --bugs Open. 3. Read the 'batch history' block. Observed: only RETRO0025-0028 are listed. Expected: the most recent measured sprints, or an explicit statement that N measured sprints were excluded and why. Confirm the cause directly: `batch_history` skips a row unless isinstance(r['measured'], (int,float)) and r['measured'] is truthy, and every interactive sprint records measured=0.

## Proposed Fix

Decide what the block is for. If it is per-unit cost, then a sprint with only a sprint-level total can still contribute tokens/unit as total/units, and `measured` is the wrong gate - use the units column and mark the row as sprint-level rather than per-unit. If per-unit telemetry is genuinely required, then the block must SAY how many measured sprints it excluded and why, because silence here reads as 'this is all the evidence there is'. Either way it must not present the oldest data as the current cost picture. Guard it with a test that puts an interactive-shaped row (actual set, measured 0) in the history and asserts it is either included or explicitly reported as excluded - never simply absent.

## Resolution

Fixed per operator ruling D0047: interactive sprints are INCLUDED, their per-unit cost derived as
total/units, and every row carries a `basis` of `per-unit` or `sprint-level` which the renderer
prints. The divisor stays the measured-unit count where there is one - a runner-era sprint that
delivered 7 and recorded telemetry for 5 is evidence about those 5 - and falls back to the
delivered-unit count otherwise. With neither, no row is made: the numerator was never the problem,
and a total with no divisor cannot yield a per-unit figure.

D0047's accepted risk is stated on screen, not only in the decision record. A sprint-level figure
hides the variance between units, so a 9-unit sprint where one unit ate half the budget looks
identical to nine even ones. The block prints that caveat under the rows, and only when a
sprint-level row is actually on screen - a caveat printed over a block it is not about is noise,
and noise on a line that is usually fine is how a real caveat stops being read.

On this repo the block now shows RETRO0027 and RETRO0028 (per-unit) alongside RETRO0060 at
265,624/unit and RETRO0061 at 97,337/unit (sprint-level), where before it ended at RETRO0028.

WHAT THIS DID NOT FIX, contrary to the last sentence of the Summary and of D0047's rationale. The
stalled counter is NOT this filter. `tokens_per_point` still reports "3 unit(s) of its own
evidence", unchanged, because it reads a different source: the join of the plan-time forecast log
against the PER-UNIT actuals log, not the velocity table's `Measured` column. This project has 208
units with plan-time Points recorded and only 3 with a per-unit actual (CR0268-CR0270), so the
counter is stuck for want of per-unit actuals, which an interactive sprint never writes. Moving it
means changing where the rate is measured from, which D0047 did not rule on. Filed separately
rather than done quietly here.

### Repair round 1: a typed total could pass as a measured one

The independent review raised a MINOR the inclusion created. Before it, `measured > 0` was the
entry condition, so every row in "what sprints ACTUALLY cost" was machine-measured. A
sprint-level row can now reach the block from two very different places - the harness meter, or
an operator typing `accuracy --tokens N` - and `basis` cannot tell them apart, because `basis`
is a fact about the DIVISOR. A keyed-in figure rendered as `sprint-level`, indistinguishable
from a capture, in the block the plan quotes as its cost picture. This is the same
claim-versus-measurement distinction BG0245 spent most of its effort establishing for the
mutation ledger, left unmade for the token ledger in the same sprint.

The velocity history now records a `Source` for the Actual cell, decided where the figure is
fetched rather than inferred afterwards: `per-unit` (summed from per-unit telemetry),
`harness` (read off the transcript meter by `--tokens-from-harness`), `supplied` (typed into
`accuracy --tokens N`). Re-using an already-recorded actual keeps the provenance that actual
was recorded under, so a close re-run cannot relabel a capture as a claim. `batch_history`
carries it through and the renderer prints it on the row, with one caveat under the block
naming `supplied` as the only row kind nothing measured.

A row written before the column existed carries no Source, and unrecorded is what it stays.
Back-filling one would invent the very distinction the column exists to record, and the table
is parsed by column NAME precisely so a column can be added without rewriting a historical row.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed per D0047: interactive sprints included, per-unit derived from the sprint total, every row labelled per-unit or sprint-level, and the hidden-variance caveat printed when a derived row is on screen. 7 mutants applied, 7 killed. The rate counter is a DIFFERENT filter and is unchanged at 3 - stated in the Resolution rather than left implied. |
| 2026-07-21 | claude | Review REJECT, repair round 1. MINOR: the inclusion admitted operator-TYPED totals into "what sprints actually cost" with no provenance mark, so a keyed-in number rendered identically to a harness capture. The velocity history now records a `Source` (`per-unit` / `harness` / `supplied`, absent = unrecorded), `batch_history` carries it and the renderer names a typed total as a claim. 3 mutants applied by hand, 3 killed; a 4th SURVIVED (the per-row mark was pinned only by the caveat line beneath it) and the test was strengthened until it died. |
