# Lessons Summary

Rolling digest of still-valid project lessons, read at sprint start. The full log with closed entries lives in the project tier (`.local/lessons.md`); regenerate this with `lessons summary`.

- **L-0028: A plausible story fitted to a real pattern is not a finding.**
- **L-0027: Before tuning a coefficient, check that its input correlates with the target at all.**
- **L-0026: A resolved-but-inapplicable signal is more dangerous than an absent one.**
- **L-0025: A decoy field beats a correct one: `templates/core/cr.md` carried a placeholder `**Effort:**` above the real one, and `extract_field` takes...**
- **L-0024: The tool that measures a sprint cannot be built by that sprint.**
- **L-0023: A record kept in a gitignored working directory is not a record.**
- **L-0022: Verify a fix by ATTACKING it, not by re-reading it.**
- **L-0021: RETRACTED - A calibration fitted to work delivered under one standard does not survive a change in the standard.**
- **L-0020: When two tools judge the same artefact, they must agree on what a COMPLETE one is.**
- **L-0019: A gate belongs in the command people actually run, not in a step they are told to run.**
- **L-0018: Reporting a model's fit against the same data it was fitted to is training error, not validation.**
- **L-0017: An estimate re-derived at judgement time from the constants it is meant to be judging is not a prediction, and a loop built on one cannot...**
- **L-0016: Verify a subagent's work through the public path before trusting the report.**
- **L-0015: Sweep for the class, do not fix the enumerated list.**
- **L-0014: A narrow sample can make a variable look constant; widen the RANGE before concluding.**
- **L-0013: When two code paths express the same filter (`review_prep`'s two persona-index excludes), give them one shared definition or they drift -...**
- **L-0012: A gate that enforces a ceremony should be run against its own delivery as the acceptance test: CR0253 flagging its own sprint's stale...**
- **L-0011: A false finding is not free: under a disposition gate that turns findings into work, a confident wrong one manufactures work for everyone...**
- **L-0010: Marking a work item Complete while part of its acceptance criteria is unwired is the same failure as a tool reporting a success it did not...**
- **L-0009: A guard that branches on invocation mode must be tested in every invocation mode; assert on output, not the exit code, when the failure...**
- **L-0008: A gate that checks an artefact exists, not what is in it, is satisfied by `touch`.**
- **L-0007: A hazard found by calling a private helper directly may already be guarded at the only call site that matters - reproduce through the...**
- **L-0006: A security fix needs a leading/trailing/interior placement matrix, not just a character list**
- **L-0005: Editing a shared template obliges you to run its renderer's tests**
- **L-0004: Add a closing full-diff pass when units share a file**
- **L-0003: Read every creation path, not the one the design note names**
- **L-0002: Forward-port via install.sh, not per-file cp** - Sync with `install.sh --local` (whole-tree, deterministic), then `diff -rq` to verify
- **L-0001: Amend the AC in the same unit when the implementation deviates** - When deviating, reword the AC + add a revision-history note in the same commit; the critic checks AC-vs-delivered-behaviour
