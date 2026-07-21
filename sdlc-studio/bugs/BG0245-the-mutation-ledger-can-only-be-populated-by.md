# BG0245: The mutation ledger can only be populated by mutation.py, but the per-unit practice is hand-applied mutants, so the coverage lane reads 0/N after a correctly-run sprint

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py,.claude/skills/sdlc-studio/scripts/gate.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0238 made mutation evidence accumulate in a ledger keyed on each target's content hash, so per-unit runs survive to the close. It fixed half the problem. The ledger is written only by mutation.py, and the per-unit practice this project actually follows - the RETRO0061 lesson, and option G as resolved in RFC0048 D3 - is a builder hand-applying a mutant to the code a new test pins, confirming RED, and restoring. That never touches mutation.py, so it leaves no trace. RUN-01KY2K5R is the proof: 75 per-unit mutants were applied during the build with 5 survivors found and fixed, 12 more across repair and re-verification, and the close-time lane still reported 'mutation evidence covers 0/4 file(s) of the changed surface'. That reading is literally true about the ledger and badly false about the sprint. The consequence is worse than a missing number: a lane that reports 0/N precisely when the policy WAS followed teaches everyone to scroll past it, and an advisory lane that is always red is indistinguishable from one that is broken. Note the wrong remedy, attempted and abandoned at this sprint's own close: a blanket close-scoped mutation.py sweep over the whole diff does populate the ledger, but it mutates code no changed test pins and samples under 1% of the enumerated mutants (24 of 3,153), which is the shape RFC0049 explicitly argues against and produces weaker evidence than the per-unit practice it would be papering over.

## Steps to Reproduce

1. Run a sprint following the per-unit policy: for each new or changed test, hand-apply a mutant to the code it pins, see RED, restore. 2. Close the sprint. 3. Run gate.py --only mutation. Observed on RUN-01KY2K5R: 'mutation evidence covers 0/4 file(s) of the changed surface; no evidence: gate.py, `run_state.py`, mutation.py (+1 more)', with sdlc-studio/.local/mutation-runs.json absent entirely, despite 75 mutants having been applied and 5 survivors found and repaired during that sprint.

## Proposed Fix

Give the per-unit practice a way to record itself, rather than making the recorder the only way to practise. Options worth weighing: a mutation.py subcommand that registers an already-performed mutant against a target (mutant description, the test that killed it, the target's content hash at the time) so a builder logs what they just did in one line; or a narrowly-scoped per-unit mutation.py invocation cheap enough to be the default way a builder proves a new test can fail, which CR0377 (derive the minimal covering test command) is the prerequisite for. Whichever is chosen, the acceptance test is that a sprint following the policy ends with a non-zero coverage reading, and one that skipped it does not - today those two are indistinguishable. Do NOT close this by making the lane silent: the lane is right that it has no evidence, and the defect is that the evidence had nowhere to go.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
