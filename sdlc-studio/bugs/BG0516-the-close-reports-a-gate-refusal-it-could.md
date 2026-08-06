# BG0516: the close reports a gate refusal it could not attribute, where the gate named its failing lane plainly

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Observed on RUN-01KZ5YXM's close on 2026-08-04 across four consecutive attempts, each recorded in run-state `close_attempts` with `outstanding: 1, stages: [gate]`. The gate's own output at the same moment: `[FAIL] review-current [124.9s]: reviews/LATEST.md is stale - 15 artefact(s) changed since the last review (BG0513, BG0514, BG0515, CR0528, CR0529, CR0530, CR0531, SC0001, US0487, US0488 (+5 more))`.
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint close` runs `gate --require-retro <id> --require-review` and passes its output to `close_blocker_split`. When the split cannot attribute the refusal it reports `close gate: the refusal could not be attributed - its verdict named no failing lane this close can read, so it is treated as a blocker in the WORK`, and stops.

On RUN-01KZ5YXM's close this fired four times in a row while the gate's own output named the lane in terms: `[FAIL] review-current [124.9s]: reviews/LATEST.md is stale - 15 artefact(s) changed since the last review ... run review before closing`. The operator is told the refusal cannot be identified by the very command that just printed its identity.

The cost is not one message. The close's own loop guard counts attempts and the outstanding set never shrank - four rounds all recorded `outstanding: 1, stages: [gate]` - so the run hit `LOOP STOPPED: the declared round cap of 4 is reached` and quarantined itself. An unattributable refusal is unfixable by construction, so every retry looks identical to the guard and the cap is reached without a single real attempt at the actual blocker. Running `gate.py --require-retro <id>` by hand exits 0, which sends a reader looking in the wrong place; the `--require-review` form is the one that fails, and only the close passes that flag.

## Steps to Reproduce

1. Open a run, deliver its units, write and validate a retro.
2. Let `reviews/LATEST.md` go stale (any artefact change since the last review does it).
3. `sprint.py close --retro RETROxxxx` - it stops with `the refusal could not be attributed`.
4. `gate.py --require-retro RETROxxxx` alone - exit 0, every lane passes.
5. `gate.py --require-retro RETROxxxx --require-review` - `[FAIL] review-current`, named clearly.
6. Retry step 3 four times; each records `outstanding: 1, stages: [gate]` and the fourth trips the loop cap.

## Proposed Fix

Make `close_blocker_split` recognise the `review-current` lane, and - more importantly - make the unattributed branch print what the gate actually said rather than reporting that it said nothing. A refusal the close cannot classify is still a refusal whose text it holds: the honest message names the lane the gate named and says only the CLASSIFICATION failed. Consider also not counting an unattributed round against the loop cap, since a round the operator cannot act on is not an attempt.

## Acceptance Criteria

> **REWRITTEN at plan review, before any code.** The first version named the wrong mechanism.
> It claimed the close fails to recognise `review-current`; `_CLOSE_SELF_LANES` already contains
> it. A seat executed `sprint.gate_failed_lanes` and found the real defect: `_GATE_FAIL_RE`
> matches `[FAIL] <lane>:` while `gate.py` prints `[FAIL] {check}{lane_stamp(c)}: {detail}`, and
> `lane_stamp` inserts `[0.4s]` before the colon. **Every TIMED lane is dropped, not just this
> one.** The original plan was satisfiable by tests written against hand-made unstamped strings
> while the bug remained - the mutant-from-the-criterion, assertion-from-the-code failure this
> gate exists to catch, caught for the price of a plan review.

### AC1: a stamped gate failure is parsed, and the parser is fed the renderer's own output

- **Given** the exact line `gate.py` prints for a failing timed lane, `[FAIL] review-current [0.4s]: reviews/LATEST.md is stale`
- **When** `sprint.gate_failed_lanes` reads it
- **Then** it returns that lane and its detail - today it returns `[]`, because the timing stamp sits between the lane and the colon
- **Mutant:** restore `_GATE_FAIL_RE` to require the colon immediately after the lane - this reddens, and no unstamped fixture can tell the difference
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseBlockerAttributionTests::test_a_stamped_gate_failure_is_parsed
- **Verified:** no

### AC2: the test ROUND-TRIPS gate.py's own renderer, never a hand-made string

- **Given** a failing lane rendered by `gate.py`'s own formatting path rather than typed into the test
- **When** that output is fed to `gate_failed_lanes`
- **Then** the lane is recovered - the two are pinned to each other, so the next change to the lane format cannot break the close silently
- **Mutant:** assert against a hand-written `[FAIL] lane: detail` literal - it passes today, with the bug fully present, which is exactly how this defect survived
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseBlockerAttributionTests::test_the_parser_round_trips_the_renderer
- **Verified:** no

### AC3: the over-correction is refused - an advisory line is not a failure

- **Given** `[warn]` and `[PASS]` lines carrying the same timing stamp
- **When** the widened pattern reads them
- **Then** neither parses as a failure, because a regex loosened until it matches anything refuses a close on an advisory lane
- **Mutant:** widen to `\[[A-Za-z]+\]` - AC1 and AC2 stay green while every passing gate reports failures
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseBlockerAttributionTests::test_an_advisory_line_is_not_a_failure
- **Verified:** no

### AC4: an unattributable blocker QUOTES the gate rather than claiming nothing was found

- **Given** a gate failure whose lane the splitter genuinely cannot recognise
- **When** the close reports it
- **Then** it prints the gate's own failing text verbatim - "I could not attribute this" and "nothing was found" are different facts, and the second sends the reader to the wrong place
- **Mutant:** in sprint.py, drop the gate's raw failing text from the unattributable message - a lane added later is invisible to the close by default
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseBlockerAttributionTests::test_an_unattributable_blocker_quotes_the_gate
- **Verified:** no

### AC5: the positive control - a passing gate still closes

- **Given** a gate whose lanes all pass
- **When** the close reads its output
- **Then** no blocker is reported and the close proceeds - a parser that finds failures everywhere passes AC1 through AC4 and stops every close in every consuming project
- **Mutant:** in sprint.py, return every parsed line as a failing lane - this reddens alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseBlockerAttributionTests::test_a_passing_gate_still_closes
- **Verified:** no

## Impact

A gate that refuses without saying what refused you is worse than the flake it is reporting - it is the same shape as BG0513, one layer up. Here it also burns the loop guard: the close quarantines itself after four rounds that were never real attempts, and the run cannot be closed by the command built to close it.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in sprint.py, remove review-current from the recognised lane set | a stamped gate failure is parsed, and the parser is fed the renderer's own output |
| AC2 | in sprint.py, drop the gate's raw failing text from the unattributable message | the test ROUND-TRIPS gate.py's own renderer, never a hand-made string |
| AC3 | in sprint.py, remove the attribution result from the retry decision | the over-correction is refused - an advisory line is not a failure |
| AC4 | in sprint.py, drop the gate's raw failing text from the unattributable message | an unattributable blocker QUOTES the gate rather than claiming nothing was found |
| AC5 | in sprint.py, return every parsed line as a failing lane | the positive control - a passing gate still closes |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
| 2026-08-06 | sdlc-studio | Groomed for the v5 release sprint: tool-derived criteria replaced with decidable ones naming their mutants, authored in the shape verify_ac actually parses |
