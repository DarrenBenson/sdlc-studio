# BG0569: nothing stops a tool or fixture writing into the working tree, and it happened three times in two days - each caught by a gate rather than by its author

> **Status:** Fixed
> **Severity:** High
> **Points:** 5
> **Affects:** tools/repo_writes.py, tools/tests/test_repo_writes.py, .githooks/pre-commit, .githooks/commit-msg
> **Evidence:** Three instances, 2026-08-09 to 2026-08-11, all in this repository. (1) BG0536: a fixture helper took its root as a parameter, a placeholder passed `.`, and every run wrote `src/thing.py`, a fake bug and `sdlc-studio/.local/mutation-runs.json` into the real tree - destroying 23 mutation registrations that `.local/` being gitignored made unrecoverable. (2) US0664: a rehearsal harness's own declared mutant pointed its work root at the repository; one run wrote 41 fixture files that `git add -A` swept onto main, in the commit whose criterion asserts nothing is written inside the repository, and a later run deleted a reviewer's git worktree. (3) 2026-08-11: `verify_ac run --batch` started without `--dry-run` back-annotated seven stories nobody had touched, refused by the conformance lane. Every one was caught by a gate, never by the author. (4) And a FOURTH, found while repairing BG0536 an hour later: a stray `sdlc-studio/bugs/BG0001-x.md` from a test fixture sat untracked in the tree and was caught by the duplicate-id lane, not by anything watching for writes - and the guard test written that same hour asserted only over top-level entries, so it could not have seen it either.
> **Verification depth:** functional (unit: 15 cases, 8 over the two readings and 3 over the command line, all in throwaway repos under `tempfile`; wiring: 4 cases driving the REAL hook pair over a real `git commit`, one refusing a stub suite that writes a nested artefact and one landing the identical commit with a clean suite; mutation: 6 declared mutants applied across the guard, both hooks and the roster, each killed by its own criterion's verifier, with bytecode purged between runs)
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Three different mechanisms, one shape: something that takes a root, or defaults to one, writes where the author did not intend, and a real path looks exactly like a temp path until somebody checks what changed.

Each was repaired locally and each repair is right. `SurvivorGateTests._repo` refuses a non-temp root. The rehearsal harness refuses a work root inside the repository before its cleanup trap is armed. But those are two guards on two callers, and the third instance had neither because nobody had thought of it yet. The pattern is now established well enough to be worth a rule rather than three fixes.

What is missing is a check that the SUITE leaves the tree unchanged. The suite is the population where this happens - fixtures are where roots are parameters - and the invariant is cheap to state: running the tests must not modify a tracked file, create an untracked one, or touch `sdlc-studio/.local/`. The last is the one that hurts most, because it is gitignored and therefore unrecoverable.

## Steps to Reproduce

1. Note the working tree state, including gitignored `sdlc-studio/.local/`. 2. Run the full suite. 3. Compare. There is no check that answers this, so a fixture that writes into the tree is discovered only when a later gate refuses a commit for reasons that look unrelated.

## Proposed Fix

Add a lane that snapshots the working tree - tracked, untracked AND `sdlc-studio/.local/` - runs the suite, and refuses on any difference, naming the paths. It belongs at the push boundary rather than per commit, on the same reasoning as the release rehearsal: it costs a full suite run. Pin it by deliberately writing a file from a fixture and asserting the lane reddens, with a clean run beside it as the positive control - a lane that reddens on everything is the same failure as one that reddens on nothing.

## Acceptance Criteria

> **Grooming note - AC4 is deliberately changed, and this is the reason.** The filed criterion
> put the lane at the push boundary "on the same reasoning as the release rehearsal: it costs a
> full suite run". It does not have to. The suites already run per commit, in `commit-msg`, so
> the lane WRAPS the run that was going to happen anyway: `pre-commit` takes the snapshot at the
> moment it selects them, `commit-msg` compares once they finish. The cost is two directory
> reads, and the coverage is every commit rather than every push. What AC4 must still hold is
> the thing that reasoning protected - that the lane never CAUSES a suite run - so it now says
> that, and is verified by a docs-only commit paying nothing.

### AC1

- **Given** a throwaway git repository, and a write into it after the snapshot is taken - a
  nested untracked artefact three directories down, a file under gitignored
  `sdlc-studio/.local/`, one nested deeper still under `.local/`, a rewritten tracked file, and
  a deleted tracked file
- **When** the two snapshots are compared
- **Then** every one is reported with its FULL repo-relative path. The nested cases are the
  criterion, not decoration: the guard test written for the previous instance asserted only
  over TOP-LEVEL entries, so it could not have seen the `sdlc-studio/bugs/BG0001-x.md` that
  prompted it, and a path with no separator in it is the signature of that mistake repeated.

- **Verify:** pytest tools/tests/test_repo_writes.py -k a_nested_untracked_file_is_seen_not_only_a_top_level_entry
- **Verified:** yes (2026-08-11)
- **Mutant:** in `tools/repo_writes.py`, drop `--untracked-files=all` from the git reading. The
  default collapses an untracked directory to its top entry, which is the earlier blindness
  restored exactly.

### AC2

- **Given** a throwaway repository carrying BOTH real hooks, every other guard stubbed to pass,
  and a stub `tools/` suite whose one passing test writes `sdlc-studio/bugs/BG0001-x.md` into
  the tree it runs in
- **When** a real `git commit` is made over a test-relevant staged file
- **Then** the commit is REFUSED, the output names the `repo-writes` lane and the path the suite
  wrote, and `git log` shows the commit did not land - the last clause because a refusal that
  prints and still commits is the shape three of these four instances shipped in.

- **Verify:** pytest tools/tests/test_repo_writes.py -k a_suite_that_writes_into_the_tree_refuses_the_commit_and_names_the_path
- **Verified:** yes (2026-08-11)
- **Mutant:** in `.githooks/commit-msg`, disable the `repo-writes` lane's guard so it never
  runs. The stray stays in the tree and the commit lands green, which is the state all four
  instances shipped in.

### AC3

- **Given** the identical fixture and identical staged content, with a stub suite that writes
  nothing
- **When** the same commit is made
- **Then** it LANDS, the output still names the `repo-writes` lane - a lane that never ran
  cannot have been green - and the snapshot record is gone, because it is one-shot and one left
  behind would charge the next `commit-msg`-only operation against a run that never happened.

- **Verify:** pytest tools/tests/test_repo_writes.py -k a_clean_suite_leaves_the_lane_green
- **Verified:** yes (2026-08-11)
- **Mutant:** in `tools/repo_writes.py`, make `check` return 1 whatever it found. A lane that
  reddens on everything is the same failure as one that reddens on nothing, and only this
  criterion separates them.

### AC4

- **Given** a docs-only commit - no test-relevant file staged, so no suite is selected
- **When** it is committed through the real hook pair
- **Then** the `repo-writes` lane does not appear at all and the commit lands, because a
  snapshot with no suite run between its two halves is evidence of nothing. The lane's cost is
  therefore bounded by construction: it is one `git status` and one walk of `.local/`, taken
  twice, only on a commit already paying for the suites.

- **Verify:** pytest tools/tests/test_repo_writes.py -k a_docs_only_commit_pays_nothing_because_no_suite_ran
- **Verified:** yes (2026-08-11)
- **Mutant:** in `.githooks/pre-commit`, move the snapshot step outside the suite-selection
  block, so every commit takes a reading of a tree no suite touched.

### AC5

- **Given** the lane exists in two hooks and in no single command a reader would think to grep
- **When** the roster in `AGENTS.md` and the two hooks are read
- **Then** the roster names `repo_writes.py`, `commit-msg` carries `run "repo-writes"`, and
  `pre-commit` carries the snapshot call. A guard nobody has written down is one nobody notices
  losing, and the hook-derived sweep that keeps the roster honest reads `pre-commit` only, so
  this lane is invisible to it.

- **Verify:** pytest tools/tests/test_repo_writes.py -k the_roster_names_this_lane_and_both_hooks_that_carry_it
- **Verified:** yes (2026-08-11)
- **Mutant:** delete the `repo-writes` paragraph from `AGENTS.md`'s lane roster.

### AC6

- **Given** a `.local/` directory holding, from one run, a record the GATE writes inside the
  comparison window (`gate-timings.json`, and a file under `suite-logs/`) beside a record a
  stray write would destroy (`mutation-runs.json`)
- **When** the two snapshots are compared
- **Then** ONLY the last is reported. The exemption is a named list, never a wildcard on
  `.local/`: the registrations that were destroyed live in the same directory the gate writes
  its own timing into, so a directory-wide exemption would reopen the hole this closes, and no
  exemption at all would refuse every commit for the gate's own bookkeeping.

- **Verify:** pytest tools/tests/test_repo_writes.py -k the_harness_records_are_exempt_by_name_and_their_neighbours_are_not
- **Verified:** yes (2026-08-11)
- **Mutant:** in `tools/repo_writes.py`, widen `_exempt` from the named records to any path
  under `sdlc-studio/.local/`.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `tools/repo_writes.py`, drop `--untracked-files=all`, so a wholly untracked directory collapses to its top entry | |
| AC2 | in `.githooks/commit-msg`, disable the `repo-writes` lane's guard so it never runs | |
| AC3 | in `tools/repo_writes.py`, make `check` return 1 whatever it found | |
| AC4 | in `.githooks/pre-commit`, move the snapshot step outside the suite-selection block | |
| AC5 | delete the `repo-writes` paragraph from `AGENTS.md`'s lane roster | |
| AC6 | in `tools/repo_writes.py`, widen the harness exemption to any path under `sdlc-studio/.local/` | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Filed |
| 2026-08-11 | sdlc-studio | Criteria regroomed with a named mutant each; AC4 rebound from the push boundary to the suite run it wraps, since that costs nothing extra and covers every commit |
