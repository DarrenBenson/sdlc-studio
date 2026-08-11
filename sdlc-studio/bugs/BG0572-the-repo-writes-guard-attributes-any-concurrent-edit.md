# BG0572: The repo-writes guard attributes any concurrent edit to the test run, so editing during a 15-minute background commit refuses it and names the author's own files as fixture damage

> **Status:** Open
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/repo_writes.py, .githooks/pre-commit, .githooks/commit-msg
> **Severity:** Medium
> **Points:** 3

## Summary

Hit within an hour of the guard shipping, on the commit that shipped it. The guard snapshots the tree in `pre-commit` and compares in `commit-msg`, so its window is the whole hook run - measured here at 829s. Everything that changes inside that window is reported as `the test run changed N path(s)`, including edits the author made in another terminal while waiting.

The refusal is then actively misleading. It names the author's own source files, says `a fixture that writes into the repository is writing over real work`, and sends them looking for a helper that took `.` as its root. There is no such helper. Three of the ten paths it named were gitignored `.local/` records, carrying the strongest wording in the message - `nothing can restore it` - for records that were written by a deliberate foreground `verify_ac` run.

This is not an argument against the guard, which is worth its cost and caught four real instances in two days. It is that the guard measures a DELTA and attributes it to one cause. The repository's own workflow makes the collision likely rather than exotic: the hook takes about fifteen minutes, AGENTS.md budgets for that, and a long commit is therefore normally run in the background while work continues.

**A second instance, an hour later, and sharper than the first.** The same commit was refused
again with two paths, and neither was an author's stray edit. `sdlc-studio/.local/allocation.lock`
was written by `artifact.py new` - filing THIS bug. `sdlc-studio/.local/test-execution.json` was
written by `sprint.py preflight`, run by an independent reviewer who had been asked to check a
plan, because the pre-flight records the seconds its own gate cost.

That is the finding worth having. It is not that an author might edit a file while waiting; it is
that **this repository's own review ceremony runs shipped commands that write to `.local/`**, and
the two-role model means those commands run in a DIFFERENT session from the one committing. So a
commit cannot be made while a review is in flight, and the message names the reviewer's writes as
fixture damage the committer should go and find. The exemption roster is not the problem: both
paths are legitimate records written deliberately by shipped verbs. The window is the problem.

One smaller thing found alongside it: `sprint close --dry-run` is documented as writing nothing,
and `sprint preflight` writes one row to the execution ledger. Both are reasonable; a caller
reading the dry-run's promise and generalising it to the pre-flight is not unreasonable either.

## Steps to Reproduce

1. Start a commit in the background; the pre-commit hook snapshots the tree. 2. While the suites run, edit any tracked file - or run any command that writes to `sdlc-studio/.local/`, such as `verify_ac.py run`. 3. The commit is refused by `repo-writes`, naming those files as changed by the test run, with a remedy that does not apply.

## Proposed Fix

Narrow the attribution to what the suite can actually be blamed for. Options, in rough order of preference: record a digest per path at snapshot time and compare against the process's own start, so a file the AUTHOR touched after the snapshot is distinguishable from one a test wrote during it; or bound the window to the suite subprocess rather than the whole hook, snapshotting immediately before it starts and comparing immediately after it exits, which is a much smaller target; or, cheapest and weakest, keep the check but soften the message to state that it cannot tell a concurrent edit from a fixture write, and name the concurrent-edit case first because it is the more common one.

Whatever is chosen, the `.local/` wording needs care: `nothing can restore it` is the right thing to say about a fixture that clobbered a mutation ledger and the wrong thing to say about a record a foreground command just wrote on purpose.

## Impact

A guard that names innocent files and prescribes a remedy that does not apply is a guard people learn to bypass, and the bypass here is `--no-verify`, which switches off every other lane too. Medium rather than High because the check itself is sound, the refusal is safe rather than destructive, and the workaround (do not edit while a commit runs) is available once understood - but it is not discoverable from the message, which is the part that makes it a defect rather than a footnote.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
