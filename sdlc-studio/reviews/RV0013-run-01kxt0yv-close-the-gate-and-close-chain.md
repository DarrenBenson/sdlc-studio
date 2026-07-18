# RV-0013: RUN-01KXT0YV close: the gate and close chain report their own state honestly

> **Date:** 2026-07-18
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Scope

The closing review of sprint RUN-01KXT0YV (EP0072 close-and-gate ergonomics + BG0190), covering
`3376648..HEAD` - 9 delivered units, 37 files, ~1,750 insertions. One CODE leg: an independent
adversarial full-diff pass under refute framing, run as a separate instance from the author, with
every finding required to carry a reproduction the reviewer had actually executed.

Document legs: `reference-verify.md` (the AC-fingerprint freshness model), `help/mutation.md` (the
diff-biased ceiling), `AGENTS.md` (gate timing expectations), and `CHANGELOG.md`. Each is consistent
with the shipped code and enforced by the gate.

## Findings

Three rounds: **REJECT, REJECT, APPROVE.**

**Round 1 - BLOCKING (F1a).** `_derive_parent_epics` evaluated `all(terminal)` over only the units
`reconcile._breakdown_units` could RESOLVE. That helper silently skips a breakdown id with no
backing file and a unit file with no `Status` - correct for drift detection, wrong for deriving
completion. An unresolvable child was therefore treated as absent rather than incomplete, marking
an incrementally-written epic Done off its one delivered story. It also iterated every epic in the
repo rather than the run's own units, writing false completion onto epics the close never touched.
Reproduced with cases B and C against the shipped tree. The four delivered tests covered
all-terminal, live-child, no-children and already-terminal - never an unreadable child.

**Round 2 - BLOCKING (F1b).** The repair left `wanted and not (...)` in the scope filter, so an
empty `units` list disabled scoping and restored the full-repo sweep. Reachable in production:
`_batch_story_units` is story-scoped by design, so a bug/CR-only batch reaches the tail with
`units=[]` - the shape of the 29-bug audit sprint RUN-01KXQH64. Reproduced as case D.

**Round 3 - APPROVE.** Both halves re-verified against the reviewer's own reproductions, correctly
re-scoped. Mutation established the regression tests fail on the true defect. The reviewer also
corrected the author's account of the fix: the guard and the unconditional filter mask each other,
and the filter is what does the work - the guard is belt-and-braces, not the mechanism.

**Non-blocking, accepted and fixed.** `review_prep`'s "index row written" reported on any backfilled
meta row rather than this RV.

**Non-blocking, documented.** The AC fingerprint deliberately excludes AC body prose: editing the
Given/When/Then narrative changes what an AC means to a reader without changing what the verifier
executes, so the mechanical gate cannot judge it and the critic owns that drift. Recorded in
`reference-verify.md`.

**Latent, filed as BG0194.** `ID_SEARCH_RE` has no trailing-digit boundary, so `US01010` truncates
to `US0101`. Unreachable by construction here (ids are minted `%04d`; the repo has 260 stories) and
bounded in harm, so not blocking.

**Probed and could not break.** US0217's enforcement (old and new run side by side on the real repo
with `doc_coverage` forced red - both exit 1; no state found where a previously-failing gate now
passes); US0215 (both branches still blocking, only the remedy text differs); US0216 (the lane was
already advisory); US0220 (the selection regex is byte-identical to the prior inline grep);
fingerprint attacks (fence-wrapping, AC reordering, duplicate ids, deletion, verifier edits,
`Provenance: external`); all six new behaviours mutation-tested and caught by genuine assertion
failures; all seven `-k` filters confirmed to select real tests; `changed_lines` deleted-file
header parsing.

## Verdict

**APPROVE** at round 3, after two blocking defects were found, repaired, and re-verified by the same
reviewer re-running its own reproductions.

Suites at approval: 2,899 skill tests OK, 219 tool tests OK, `gate.py` PASS, reconcile drift 0.

The independent review earned its cost twice over. Both blocking findings were in code the author's
own tests passed straight over, and both were in the same direction: claiming completion on
incomplete evidence. The sprint goal - that the chain reports its own state honestly - was very
nearly missed by the one unit meant to deliver it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Created via `new` (deterministic) |
