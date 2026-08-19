# BG0595: the commit-msg hook test is not hermetic, so the full suite goes red whenever the working tree is dirty

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/tests/test_commit_msg_hook.py, .githooks/commit-msg, tools/tests/test_precommit_lane_order.py
> **Created:** 2026-08-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-18T20:35:22Z

## Summary

The `commit-msg` hook's two one-shot records - the suite handoff at `$GIT_DIR/sdlc-gate-suites`
and the repo-writes snapshot at `$GIT_DIR/sdlc-repo-writes` - are deleted only on the code path
that gets PAST the message-shape checks. Both `exit 1` refusals (multi-id subject with no `Refs:`
trailer, line 127; suite-claim, line 166) come BEFORE the handoff is read and removed at line 194.
So every refused commit message leaves both records on disk, and the NEXT invocation of the hook
consumes them - including an invocation made by a unit test, which then runs the full skill suite
it was never asked to run, inside itself.

CORRECTION, recorded rather than quietly dropped. This bug was filed on 2026-08-18 claiming the
trigger was a DIRTY WORKING TREE: "the full suite goes red whenever the working tree is dirty".
That does not reproduce. Re-measured 2026-08-19 with 14 uncommitted paths present:
`python3 -m pytest tools/tests/test_commit_msg_hook.py -q` gives `25 passed, 10 subtests passed in
1.84s`, exit 0. Dirtiness alone is not the trigger; a leftover handoff is. The original reading
was taken by stashing, which changes the tree AND happened to clear a leftover record, so two
variables moved together and the wrong one was named. Found by an adversarial goal review before
any code was written.

## Steps to Reproduce

Measured 2026-08-19 at f04d5870.

**The false reading, recorded so it is not taken again.** With 14 uncommitted paths in the working
tree, `python3 -m pytest tools/tests/test_commit_msg_hook.py -q` reports `25 passed, 10 subtests
passed in 1.84s` and exits 0. The tree being dirty does nothing.

**The real path**, read from `.githooks/commit-msg`:

1. Line 127 exits 1 on a multi-id subject with no `Refs:` trailer. Line 166 exits 1 on a failed
   suite-claim. Both are message-shape checks and both precede the handoff block.
2. Line 179 resolves `handoff="$(git rev-parse --git-path sdlc-gate-suites)"`; line 181 is
   `[ -r "$handoff" ] || exit 0`; line 194 is `rm -f "$handoff"`. The delete is downstream of both
   refusals, so a refused message never reaches it.
3. Line 327 resolves the `sdlc-repo-writes` snapshot and line 335 removes it, further downstream
   still.
4. Consequence: after any refused commit message, both records survive. The next hook invocation
   reads them and proceeds into the `run` block. When that invocation comes from
   `tools/tests/test_commit_msg_hook.py`, a unit test runs the full skill suite inside itself -
   the nested run does not terminate within a two-minute test budget.

Both refusals are ordinary events here: this repository's own history records commit messages
refused for exactly these two shapes during the last run.

## Proposed Fix

Run the hook against a throwaway git repository rather than the one under development, as the sibling hook tests do, or set the environment the lane reads so `repo-writes` is scoped to a fixture. The bar is that the test's result must not change when a developer has unrelated uncommitted work. Check the other tests in this file for the same coupling before assuming it is the only one - a non-hermetic test that fails only during delivery is one people learn to ignore, which is worse than not having it.

## Acceptance Criteria

- [ ] **AC1** Given a leftover `sdlc-gate-suites` handoff in the git directory, when the commit-msg hook tests run, then their verdict is identical to their verdict with no handoff present - and the test SETS UP that leftover rather than depending on whatever the developer's git directory happens to hold
- [ ] **AC2** Given both of those runs, when they are compared, then BOTH are green - equality reached by making the clean case red too is not the property this asks for, and this is the control that says so
- [ ] **AC3** Given a commit message the hook REFUSES, when the hook exits, then neither the `sdlc-gate-suites` handoff nor the `sdlc-repo-writes` snapshot survives - a one-shot record must be one-shot on every exit path, not only the happy one
- [ ] **AC4** Given a test that invokes the hook, when it runs, then it runs against a throwaway repository with its own git directory, so no record it leaves can reach the repository under development
- [ ] **AC5** Given a test invocation of the hook that does find a handoff, when it proceeds, then it does NOT enter the suite-running block - a unit test must never be able to start a full gate suite inside itself, which is the consequence that made this defect expensive rather than merely wrong
- [ ] **AC6** Given the full suite run twice - once with the git directory carrying both leftover records and once with neither - when the two verdicts are compared OUTSIDE the suite, with each exit code read from `$?` on its own line and never through a pipe, then they are identical, and any test whose result differs between the two runs is NAMED

## Impact

The full suite is the gate for push, release and close. A lane that goes red purely because work is in flight trains the operator to read a red full suite as noise, which is the state in which a real failure ships.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-18 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Criteria re-pointed by adversarial goal review: evidence taken outside the instrument under repair, and the enumerated case generalised to its class |
| 2026-08-19 | sdlc-studio | Premise CORRECTED: a dirty tree does not reproduce; the trigger is a one-shot record left behind by a REFUSED commit message, and the consequence is a nested full-suite run inside a unit test |
| 2026-08-19 | sdlc-studio | Scope widened to `.githooks/commit-msg` and re-pointed 2 -> 3: the corrected premise puts the defect in the hook's exit paths, not only in the test |
