# BG0245: The mutation ledger can only be populated by mutation.py, but the per-unit practice is hand-applied mutants, so the coverage lane reads 0/N after a correctly-run sprint

> **Status:** Fixed
> **Verification depth:** functional - `mutation.py register` was driven end to end in a throwaway git fixture and the resulting lane line read against three states (self-report only, self-report beside a measured entry, self-report gone stale on an edit). 15 mutants hand-applied across `register_mutant`, `append_ledger` and the gate's coverage lane; 14 killed first time, 1 SURVIVED and drove a second test.
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py,.claude/skills/sdlc-studio/scripts/gate.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0238 made mutation evidence accumulate in a ledger keyed on each target's content hash, so per-unit runs survive to the close. It fixed half the problem. The ledger is written only by mutation.py, and the per-unit practice this project actually follows - the RETRO0061 lesson, and option G as resolved in RFC0048 D3 - is a builder hand-applying a mutant to the code a new test pins, confirming RED, and restoring. That never touches mutation.py, so it leaves no trace. RUN-01KY2K5R is the proof: 75 per-unit mutants were applied during the build with 5 survivors found and fixed, 12 more across repair and re-verification, and the close-time lane still reported 'mutation evidence covers 0/4 file(s) of the changed surface'. That reading is literally true about the ledger and badly false about the sprint. The consequence is worse than a missing number: a lane that reports 0/N precisely when the policy WAS followed teaches everyone to scroll past it, and an advisory lane that is always red is indistinguishable from one that is broken. Note the wrong remedy, attempted and abandoned at this sprint's own close: a blanket close-scoped mutation.py sweep over the whole diff does populate the ledger, but it mutates code no changed test pins and samples under 1% of the enumerated mutants (24 of 3,153), which is the shape RFC0049 explicitly argues against and produces weaker evidence than the per-unit practice it would be papering over.

## Acceptance Criteria

- [x] **AC1:** `mutation.py register` records an already-applied mutant against the target's content hash, so the per-unit hand-mutation practice leaves a trace without changing the practice.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_mutation.py
- [x] **AC2:** Every ledger entry carries its provenance, and a registered entry is reported as SELF-REPORTED by the gate lane rather than presented as a measured run.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_gate.py
- [x] **AC3:** A registered and a measured entry for the same target are separate records, so neither erases the other, and an edit to the target starts a fresh entry.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_mutation.py
- [x] **AC4:** Verdicts only a runner can observe (error, unviable) are REFUSED from a self-report, so a builder cannot claim what they did not measure.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_mutation.py

## Steps to Reproduce

1. Run a sprint following the per-unit policy: for each new or changed test, hand-apply a mutant to the code it pins, see RED, restore. 2. Close the sprint. 3. Run gate.py --only mutation. Observed on RUN-01KY2K5R: 'mutation evidence covers 0/4 file(s) of the changed surface; no evidence: gate.py, `run_state.py`, mutation.py (+1 more)', with sdlc-studio/.local/mutation-runs.json absent entirely, despite 75 mutants having been applied and 5 survivors found and repaired during that sprint.

## Proposed Fix

Give the per-unit practice a way to record itself, rather than making the recorder the only way to practise. Options worth weighing: a mutation.py subcommand that registers an already-performed mutant against a target (mutant description, the test that killed it, the target's content hash at the time) so a builder logs what they just did in one line; or a narrowly-scoped per-unit mutation.py invocation cheap enough to be the default way a builder proves a new test can fail, which CR0377 (derive the minimal covering test command) is the prerequisite for. Whichever is chosen, the acceptance test is that a sprint following the policy ends with a non-zero coverage reading, and one that skipped it does not - today those two are indistinguishable. Do NOT close this by making the lane silent: the lane is right that it has no evidence, and the defect is that the evidence had nowhere to go.

## Resolution

Fixed per operator ruling D0048: `mutation.py register --target --mutant --test --verdict` records
a mutant a builder ALREADY applied by hand, against the target's content hash at the time. The
practice is unchanged - apply a mutant to the code a new test pins, see RED, restore - and it now
leaves a trace in one line. The wrong remedy the bug names, a blanket close-scoped sweep, is not
what was built.

D0048's critical constraint is what most of the work went into. A registered entry is
SELF-REPORTED: nothing here applies a mutant, runs a test, or checks the claim. So:

- Every ledger entry carries `provenance`. A run stamps `measured`; registration stamps
  `registered`. An entry written before provenance existed reads as `measured`, because only a run
  could write one then and reading it as a claim would retro-actively weaken real evidence.
- The two kinds are separate entries, so neither can erase the other. A run supersedes its own
  kind only; one `register` call cannot displace a measurement of the same file, and a re-run
  cannot delete a hand-registered claim it never gathered.
- The gate lane reports a file covered only by a self-report as exactly that: `mutation evidence
  covers 2/2 file(s) of the changed surface; 1 of those is self-reported (mutants registered by
  hand, not a measured run): app.py`. A measured entry outranks a registered one on the same
  content, and the clause is printed only when a self-report is actually on screen.
- The register command says it at the moment of recording: "Nothing was re-run here, so the ledger
  holds this as a claim, not a measurement".

Provenance changes how an entry is WEIGHTED, never whether it expires: a self-report goes STALE on
an edit exactly as a measured entry does, because a claim about bytes the file no longer has is
not weaker evidence, it is evidence about different code. Registrations on unchanged content
accumulate, since a builder applies many mutants to one file across a sprint and overwriting per
call would have left the ledger permanently reading 1 - the same silence in a new place.

The bug's own acceptance test holds: a sprint that follows the policy and registers what it
applied ends with a non-zero coverage reading, and one that skipped it still reads 0/N. What the
two are NOT is indistinguishable from a measured sweep, which is the property D0048 required and
the reason the lane names them.

Refused, because they cannot be self-reported honestly: `error` and `unviable` verdicts (things a
runner observes about a mutant it tried to execute), a target that cannot be read (no content
hash, so the entry could never go stale), and an entry naming neither what was mutated nor what
judged it (unauditable against the diff).

The missing-target refusal SURVIVED its first mutant: `cmd_register` also catches OSError, so
deleting the guard produced the same exit code from a later `FileNotFoundError` and the CLI test
could not tell the difference (L-0159). It is now pinned at the library boundary, on the
ValueError and its message, and the mutant is killed.

NOT DONE HERE, and deliberately: `reference-sprint.md` still describes the per-unit practice
without mentioning `register`, and the scripts catalogue does not list the subcommand. Both are
outside this unit's permitted file set.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed per D0048: `mutation.py register` records an already-applied mutant; every ledger entry carries `provenance`; measured and registered entries coexist and neither supersedes the other; the gate lane names a self-reported cover and a measured entry outranks a registered one. 15 mutants applied, 14 killed, 1 survivor (the missing-target refusal, bypassed by `cmd_register`'s OSError catch) fixed by pinning the guard at the library boundary. Docs left for a follow-up - outside this unit's file set. |
