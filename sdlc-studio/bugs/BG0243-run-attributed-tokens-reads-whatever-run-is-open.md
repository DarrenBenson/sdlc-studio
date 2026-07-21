# BG0243: run_attributed_tokens reads whatever run is open, so a token delta can be stamped on an unrelated retro

> **Status:** Fixed
> **Verification depth:** functional - the latent path was reproduced end to end before the fix: with sprint A's retro and sprint B's run open, `accuracy --id RETRO9002 --write --tokens-from-harness` captured 700,000 tokens from RUN-01KY33VX and published `Sprint tokens/point: 87,500` onto sprint A's row, while the elapsed-hours path on the same state already read UNMEASURED. Fixed, re-run, then mutation-proven with 9 hand-applied mutants: 8 killed, 1 equivalent. One of the 8 SURVIVED first time and drove an extra test (see below).
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by the adversarial review of RUN-01KY2K5R while verifying BG0236. `run_attributed_tokens` derives its delta from whatever run happens to be in run-state.json, and `cmd_accuracy` passes it only args.root - never the retro id it is recording against. The two are therefore not tied together. `retro accuracy --id <an older retro> --tokens-from-harness --write`, run after a later `sprint plan --write` has opened a new run, would stamp the NEW run's delta onto the OLD retro's velocity row. It is not reachable through `sprint close`, which always operates on the open run, so this is latent rather than live. It is the same family as BG0236 itself and as BG0218: a number that is correct about something, attributed to something else. Note the existing precedent for the fix - the elapsed-hours path already requires the run-state batch to cover the retro's units, and that check was deliberately not extended to the token path.

## Acceptance Criteria

- [x] **AC1:** `run_attributed_tokens` requires the retro id it is recording against, so no caller can reach the capture without declaring which retro it is for.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_retro.py
- [x] **AC2:** When the open run's batch does not cover the retro's units, the capture reports not-attributable and names BOTH the retro and the run, rather than stamping one run's delta on another retro's row.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_retro.py
- [x] **AC3:** The coverage rule is the SAME function the elapsed path uses, not a second copy, so the two cannot drift into disagreeing about what a covering batch is.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_retro.py

## Steps to Reproduce

1. Close a sprint and record its retro, RETRO-A. 2. Run `sprint plan --write` to open a new run, which stamps a fresh session-token baseline. 3. Run `retro.py accuracy --id RETRO-A --tokens-from-harness --write`. 4. The delta computed is the NEW run's spend since its own baseline, and it is written to RETRO-A's row in VELOCITY.md. Nothing in the output states that the number came from a different run than the retro names.

## Proposed Fix

Tie the capture to the retro the way the elapsed path already is: require the open run's batch to cover the units the retro records, and report not-attributable when it does not, naming both the retro and the run so the mismatch is legible. Reuse the existing batch-coverage helper rather than writing a second one. Guard it with a test that opens a second run and then asks for the first retro's tokens, asserting no number is produced and that the reason names the run/retro mismatch.

## Resolution

The coverage rule the elapsed path already applied was EXTRACTED, not copied: `_run_covers`
now holds the strict-majority test, `_elapsed_hours` calls it, and `run_attributed_tokens`
calls the same function. There is one rule for both quantities read off a run - the hours it
was open and the tokens it spent - because either one taken from a run that is not this
sprint's is the same error.

`run_attributed_tokens(root, retro_id, transcripts_dir=None)` takes the retro id as a REQUIRED
positional argument and reads that retro's batch itself (`retro_units`). It is deliberately not
an optional parameter with a permissive default: a guard every caller can decline to trigger is
pinned by nothing while reading as coverage (L-0159), and passing the units in would let a
caller hand over a convenient list rather than the retro's own. The one production call site,
`cmd_accuracy`, passes `args.id`; the nine existing test call sites were updated, and one
existing test that opened a single-unit run against a two-unit retro was adjusted with a
comment saying which property it is still isolating.

That wiring needed a test of its own. Replacing `args.id` with the literal `RETRO9002` was a
SURVIVING mutant, because every test that drives the command uses that one retro - the mutant
substituted the exact value the fixture supplies, so no assertion could tell the difference.
`test_the_command_asks_about_the_retro_it_was_given` drives the command with a SECOND retro
whose unit the open run does not carry, and the mutant now fails it.

The refusal names both sides - the run whose spend it declined to read and the retro it was
asked about, with that retro's units listed - and states the two ways forward (record it from
the run that delivered it, or supply the figure). Placed AFTER the baseline check, so "no run
is open" still reports as a missing baseline rather than as a coverage mismatch.

Because BG0244 landed first, the refusal reason now also reaches the velocity row's Note
column, so a mismatch is legible in the published history and not only in the console output
of whoever ran the command.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed: `_run_covers` extracted from `_elapsed_hours` and shared, `run_attributed_tokens` takes a required retro id and reads that retro's batch, refusal names both retro and run. 9 mutants applied by hand, 8 killed. Hard-coding the fixture's own retro id in `cmd_accuracy` SURVIVED and drove a new test that drives the command with a second retro. The equivalent one deletes one of three mentions of the retro id in the reason: the reason still names it, so the asserted property holds; deleting every mention is killed. |
