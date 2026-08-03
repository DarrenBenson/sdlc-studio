# BG0492: the suite verdict binds to HEAD rather than the tree, and --check ignores which suite ran

> **Status:** Fixed
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/run-suite.sh, tools/tests/test_run_suite.py, tools/tests/test_test_census.py
> **Severity:** Medium
> **Points:** 3
> **Verification depth:** functional

## Summary

Two fail-opens in the verdict mechanism, both outside US0610/US0611's ACs as written and both real.

The verdict records `head_sha` only, so it authorises the COMMIT rather than the tree. Since a verdict is necessarily taken at the parent commit, any subsequent edit is covered by it: with a green verdict at HEAD, staging a syntactically broken .py and running the commit-msg hook on a 'Both suites green.' message returns rc=0. That is the stale-green-looking-current case the epic exists for; AC2 defines staleness by commit only.

And `--check` never reads the `suite` field, so a verdict from `run-suite.sh scripts` satisfies a claim of 'both suites green' - which is the exact phrasing the commit-msg lane's own regex matches.

## Steps to Reproduce

1. `tools/run-suite.sh all`, commit. Verdict is green at HEAD.
2. Stage a file with a syntax error. Run `bash .githooks/commit-msg` on a message saying 'Both suites green.' -> rc=0.
3. `SUITE_CMD_OVERRIDE='exit 0' tools/run-suite.sh scripts` then `tools/run-suite.sh --check` -> GREEN, though only one suite ran.

## Proposed Fix

Record a hash of the tracked working tree beside `head_sha` and refuse when it moves. Record and check the `suite` field, so a claim naming both suites needs a verdict from `all`. Both are cheap; the second is a one-line comparison.

## Acceptance Criteria

- [x] **AC1: an edit made after the verdict was taken makes it stale, at the same commit.**
  - **Given** a green `all` verdict, then any edit to a tracked file - unstaged, staged, or a
    new untracked module - with `HEAD` unmoved
  - **When** `run-suite.sh --check` runs
  - **Then** it refuses, naming the tree, because the existing `head_sha` comparison is green on
    this case by construction and cannot see it
  - **Verify:** python3 -m unittest discover -s tools/tests -p test_run_suite.py -k VerdictBindsToTheTreeTests
  - **Verified:** yes (2026-08-03) - six tests, covering unstaged, staged and untracked

- [x] **AC2: the verdict does not expire itself.**
  - **Given** the verdict is written INTO the tree it describes
  - **When** it is recorded and then checked with nothing else changed
  - **Then** the check passes - ignored files are excluded and the verdict's own directory is
    excluded on top of that, because a guard that refuses always is one that gets switched off
  - **Verify:** python3 -m unittest discover -s tools/tests -p test_run_suite.py -k test_the_verdicts_own_output_does_not_expire_it
  - **Verified:** yes (2026-08-03)

- [x] **AC3: a narrower suite does not satisfy an unqualified claim, and `all` still answers a narrower question.**
  - **Given** a verdict from `run-suite.sh scripts`
  - **When** a bare `--check` runs - the form the commit-msg lane uses for "Both suites green."
  - **Then** it refuses and names the suite that did run; and conversely `--check scripts`
    against an `all` verdict PASSES, because coverage is the test rather than equality
  - **Verify:** python3 -m unittest discover -s tools/tests -p test_run_suite.py -k test_a_narrower_suite_does_not_satisfy_a_whole_tree_claim
  - **Verified:** yes (2026-08-03)

## Verification evidence

Functional, driven through the shipped script as a subprocess rather than through any library -
every test in `VerdictBindsToTheTreeTests` invokes `tools/run-suite.sh` itself. Four mutants
executed, `__pycache__` purged and re-run under `python3 -B`, source restored afterwards:

| Mutant | Result |
| --- | --- |
| drop the tree-hash comparison from `--check` | killed by 3 tests |
| drop the suite-coverage check | killed by 1 |
| compare suite names by equality instead of coverage | killed by 1 |
| hash `git diff` without `HEAD`, so staged edits are invisible | killed by 1 |

Also driven on the real repository: `run-suite.sh --check` against the tree at delivery refuses
with the STALE message, the head comparison firing before the tree comparison as intended.

**One regression this diff caused, and how it was repaired.** `test_test_census` asserted that
`tools/tests/test_commit_msg_hook.py` is unattributed, and BG0489's fixture in that file has to
stub `tools/skill-tests.sh` - one incidental mention of a sibling module's stem moved the file to
attributed-by-reference, so a test about the census's WORDING failed for a reason unrelated to
wording. The example is now derived from whichever files are unattributed today rather than
hard-coded, which is the selection-bias shape LL0044 names. The census's own behaviour is
unchanged; only the test's choice of example was pinned to one file's content.

## Round 2: what the independent review rejected, and what changed

REJECTed at the lane boundary with two blocking findings, both reproduced by execution.

**The digest was wrong, not merely under-tested.** It hashed three inputs - HEAD, `git diff
HEAD`, and untracked file hashes - and so held two representations of the same bytes: an
untracked file contributed a `sha256  path` line, the same file staged contributed a new-file
patch. `git add -A` alone therefore moved the digest with no edit at all, and because the
commit-msg lane calls a bare `--check` on any message claiming greenness, the ordinary
sequence of writing a module, running the suite, staging it and committing was refused and
told to re-run a nine-minute suite for no information. That is the guard-that-refuses-always shape AC2 exists to
prevent, arriving through a door AC1 did not describe.

The digest is now a real git TREE OBJECT, built in a throwaway index: read HEAD, stage the
working tree, write the tree. A tree object is a function of CONTENT alone, so it cannot tell a
staged change from an unstaged one and `git add` can never move it. Ignore handling becomes
git's own rather than a second rule this script passes, and the verdict's own directory is
excluded by PATH, which also fixes the reviewer's fourth finding - a COMMITTED verdict used to
be unable to match its own tree and refused permanently, advising a re-run that never converged.
Verified: three consecutive record-then-check cycles over a committed verdict now return zero.

**A mutant the docstring named had SURVIVED.** `test_the_verdicts_own_output_does_not_expire_it`
wrote a `.gitignore` naming the very path the pathspec also excluded, so the two masked each
other and `--exclude-standard` shipped unpinned. The fixture no longer writes a `.gitignore`, so
only the pathspec can make it pass, and a separate test pins ignore handling with an ignored
file appearing after the verdict.

Also repaired from the non-blocking set: `--check <unknown-suite>` was silently accepted, so
`--check nonsense`, `--check ALL` and `--check --help` all printed GREEN against an `all`
verdict. It is now refused on the same terms the run path already refuses an unknown suite.

Round-2 mutants, all killed: drop the `.local` pathspec (8 tests), stage ignored files with
`-f` (1 - the mutant that had survived), accept any `--check` suite name (3).

## Impact

The verdict is the repo's answer to 'was it green', and both holes let it answer yes for a state it never observed. The first is the more dangerous: it authorises uncommitted edits, which is the normal state of a working tree mid-session.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
