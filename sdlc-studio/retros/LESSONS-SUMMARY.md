# Lessons Summary

Rolling digest of still-valid project lessons, read at sprint start. The full log with closed entries lives in the project tier (`.local/lessons.md`); regenerate this with `lessons summary`.

- **L-0016: Verify a subagent's work through the public path before trusting the report. Every one of the six**
- **L-0015: Sweep for the class, do not fix the enumerated list. I named three non-atomic index writes; there**
- **L-0014: A narrow sample can make a variable look constant; widen the RANGE before concluding. The failure**
- **L-0013: When two code paths express the same filter (`review_prep`'s two persona-index excludes), give**
- **L-0012: A gate that enforces a ceremony should be run against its own delivery as the acceptance test:**
- **L-0011: A false finding is not free: under a disposition gate that turns findings into work, a**
- **L-0010: Marking a work item Complete while part of its acceptance criteria is unwired is the same**
- **L-0009: A guard that branches on invocation mode must be tested in every invocation mode; assert on**
- **L-0008: A gate that checks an artefact exists, not what is in it, is satisfied by `touch`.**
- **L-0007: A hazard found by calling a private helper directly may already be guarded at the only call**
- **L-0006: A security fix needs a leading/trailing/interior placement matrix, not just a character list**
- **L-0005: Editing a shared template obliges you to run its renderer's tests**
- **L-0004: Add a closing full-diff pass when units share a file**
- **L-0003: Read every creation path, not the one the design note names**
- **L-0002: Forward-port via install.sh, not per-file cp** - Sync with `install.sh --local` (whole-tree, deterministic), then `diff -rq` to verify
- **L-0001: Amend the AC in the same unit when the implementation deviates** - When deviating, reword the AC + add a revision-history note in the same commit; the critic checks AC-vs-delivered-behaviour
