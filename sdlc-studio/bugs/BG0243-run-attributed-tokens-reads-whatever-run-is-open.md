# BG0243: run_attributed_tokens reads whatever run is open, so a token delta can be stamped on an unrelated retro

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by the adversarial review of RUN-01KY2K5R while verifying BG0236. `run_attributed_tokens` derives its delta from whatever run happens to be in run-state.json, and `cmd_accuracy` passes it only args.root - never the retro id it is recording against. The two are therefore not tied together. `retro accuracy --id <an older retro> --tokens-from-harness --write`, run after a later `sprint plan --write` has opened a new run, would stamp the NEW run's delta onto the OLD retro's velocity row. It is not reachable through `sprint close`, which always operates on the open run, so this is latent rather than live. It is the same family as BG0236 itself and as BG0218: a number that is correct about something, attributed to something else. Note the existing precedent for the fix - the elapsed-hours path already requires the run-state batch to cover the retro's units, and that check was deliberately not extended to the token path.

## Steps to Reproduce

1. Close a sprint and record its retro, RETRO-A. 2. Run `sprint plan --write` to open a new run, which stamps a fresh session-token baseline. 3. Run `retro.py accuracy --id RETRO-A --tokens-from-harness --write`. 4. The delta computed is the NEW run's spend since its own baseline, and it is written to RETRO-A's row in VELOCITY.md. Nothing in the output states that the number came from a different run than the retro names.

## Proposed Fix

Tie the capture to the retro the way the elapsed path already is: require the open run's batch to cover the units the retro records, and report not-attributable when it does not, naming both the retro and the run so the mismatch is legible. Reuse the existing batch-coverage helper rather than writing a second one. Guard it with a test that opens a second run and then asks for the first retro's tokens, asserting no number is produced and that the reason names the run/retro mismatch.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
