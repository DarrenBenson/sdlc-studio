# BG0628: conformance reports a unit NON-CONFORMANT when it could not run the verifier at all, so the same corpus scores 304, 671 or 732 depending only on which directories were copied

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Evidence:** Measured 2026-08-27 against RUN-01M11MEP's tree, exit code read separately from the output on every run, never through a pipe. Real tree: `732/814 conformant, 0 not, 82 exempt`, exit 0, twice. `--root` at a copy holding only `sdlc-studio/` and `.config.yaml`: `304/814, 428 not`, exit 1. Adding `changelog.d/`: unchanged at 304. Adding `.claude/skills/sdlc-studio/`: `671/814, 61 not`, exit 1. Every non-conformant unit in both copies fails on the same stage, `missing verified`. Two independent review subagents, working in their own copies as this project's safety rule requires, reported `625/814, 107 not` and `583/814, 149 not` to the authoring session as facts about the real tree.
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`verified` is one of `DONE_STAGES`, and a unit misses it when its criteria's `Verify:` selectors do not pass. The check does not distinguish a selector that RAN AND FAILED from one that could not be resolved because the files it names are not in the tree. Both read `missing verified`, and both are counted as non-conformant.

So the figure is a function of tree completeness rather than of the corpus. The same 814 units score 304, 671 or 732 conformant depending only on which directories were copied, and nothing in the output says which reading you are looking at. The summary line names remedies - `backfill`, a cutoff - that are the correct advice for genuine debt and useless advice for an incomplete tree.

This project's own review doctrine tells every adversarial reviewer to copy the tree to their own directory before running anything, so the wrong reading is the one an independent reviewer is instructed to produce. Two did, in one session, and both reported it as fact. A third figure then had to be defended by re-measuring - which is the cost this bug imposes even when someone notices.

## Steps to Reproduce

1. Run `conformance.py check` in a complete checkout; note the figure and the exit code, read separately. 2. Copy `sdlc-studio/` and `.config.yaml` alone to another directory. 3. Run `conformance.py check --root <copy>`. 4. The conformant count falls by hundreds and the exit code flips to 1, with no line saying the verifiers could not be resolved. Measured 2026-08-27: 732/0/exit-0 against 304/428/exit-1 for the same 814 units.

## Proposed Fix

Separate UNRESOLVABLE from FAILED. When a criterion's selector names a path the tree does not hold, the honest answer is `could not be evaluated here`, not `failed`. Report those units in their own bucket, keep them out of the non-conformant count, and print one line naming how many there are and what is missing - the same shape `scope_detail` already uses to say what a run narrowed itself to before any verdict is read.

The exit code should follow the same rule: a tree that cannot be evaluated is not a tree that failed. Whether an unevaluable tree exits 0 or a distinct third code is the decision to record; what must not survive is silently scoring it as debt.

## Acceptance Criteria

- [ ] **AC1** Given a tree in which a criterion's `Verify:` selector names a path that does not exist, when the conformance check runs, then that unit is reported as UNEVALUABLE and is NOT counted in the non-conformant total - a verifier that could not run is not a verifier that failed
- [ ] **AC2** Given a tree in which a selector resolves and genuinely fails, when the check runs, then the unit IS non-conformant - the paired control, so separating the two cannot become a way to make real debt disappear
- [ ] **AC3** Given a tree with one or more unevaluable units, when the check runs, then it prints a line naming how many and what is absent, before any verdict - an operator reading a figure hundreds lower than they expect must be told why by the tool, not by re-deriving it
- [ ] **AC4** Given this repository's own tree copied WITHOUT `.claude/skills/sdlc-studio/`, when the check runs through the shipped CLI, then the non-conformant count is unchanged from the complete tree and the difference appears entirely in the unevaluable bucket - the corpus is where this was found, and 304 against 732 is the instance it is measured on

## Impact

The conformance figure is quoted in sprint goals, release bars, retros and review findings - this run's own goal has a clause built on it. A number that changes by 428 with no change to the corpus, and no warning, is one every reader has to re-derive before trusting, and the readers most likely to hit the wrong value are the independent reviewers whose whole job is to report facts the author cannot check.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Filed |
