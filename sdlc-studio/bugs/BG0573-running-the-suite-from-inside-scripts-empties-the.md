# BG0573: Running the suite from inside scripts/ empties the checkout and replaces it with a greenfield tree, and the temp-root guard is disarmed for any clone under /tmp

> **Status:** Fixed
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_transition.py, sdlc-studio/bugs/BG0536-a-test-fixture-that-accepts-a-caller-supplied.md
> **Severity:** High
> **Points:** 5
> **Verification depth:** functional (unit: 6 cases in `FixtureRootGuardTests`, all in throwaway directories under `tempfile` - the refusal, the refusal for a checkout that IS under `/tmp`, the refusal for a checkout with no `.git`, this repository's own root refused without being written to, the destructive root proved disposable from two different working directories, and the positive control that a plain temp directory still builds; wiring: the reproduction and the repair both measured by running `python3 -m unittest discover -s tests -t .` from inside `scripts/` in an rsync copy under `/tmp` and comparing the tree; mutation: 6 declared mutants, one per criterion, each applied to the file with the anchor asserted unique, bytecode purged and `python3 -B`, each killed by its own criterion's verifier)

## Summary

Reported by an independent reviewer during the round-2 pass over this run, in a clone of this repository. Running `python3 -m unittest discover -s tests -t .` from inside `.claude/skills/sdlc-studio/scripts/` DESTROYED the working copy: the repository root was emptied and replaced with a greenfield-shaped tree - a fresh `.claude/`, `sdlc-studio/`, `src/`, a new `.git` and an empty `.gitignore`. The reviewer did not isolate which test did it, and the live repository was not touched.

Two things make this worse than the instances BG0569 repaired.

First, the guard that exists for exactly this class is DISARMED for the population most likely to hit it. `SurvivorGateTests._repo` refuses a root that is not under the temp directory, by testing `str(root).startswith(tempfile.gettempdir())`. Every reviewer in this repository's own process works in an rsync copy under `/tmp`, so for them the guard's negative case cannot be constructed and its refusal never fires. The check that is meant to stop a fixture writing over real work is inert precisely where the reviewers work.

Second, `tools/repo_writes.py` cannot see it either. That lane compares the tree before and after the suites, and a run that replaces the tree wholesale defeats a comparison as thoroughly as it defeats everything else - and in the reported instance the suite was invoked directly rather than through the hook, so no snapshot existed at all.

The invocation is not exotic. `-s tests -t .` from the scripts directory is a reasonable way to run one package's tests, and the reviewer reached it while following this repository's own instruction to work in an isolated copy.

**Two claims in the paragraph above were wrong, and the repair measured them.** The root is NOT
emptied and replaced. Every original file survives. What the first report read as a greenfield
replacement is the composite of four things: `.gitignore` truncated to zero bytes, a new `src/`,
`git init` re-run at the root, and a `git add -A` that - with the ignore file now empty - staged
the whole of gitignored `sdlc-studio/.local/`, about 120 files including the run archive. The
following `git commit` was refused by the repository's own pre-commit hook, which is the only
reason HEAD did not move. And it is NOT dependent on the working directory: the same destruction
reproduces under `pytest` from the repository root. Running from `scripts/` is only how the
`tests` package becomes importable.

**The culprit is the test written to pin the guard.** `FixtureRootGuardTests.
test_the_fixture_refuses_to_build_outside_a_temp_directory` hands the checkout root straight to
the fixture and relies on the guard to refuse it. In a copy under `/tmp` the guard's
`startswith(tempfile.gettempdir())` is TRUE, so nothing refused and the fixture built its
workspace over the checkout. A test that is safe only while the thing it tests is correct is a
test that destroys a tree the day that thing is wrong - which is the day the test exists for.

## Steps to Reproduce

1. Copy the repository to a directory under `/tmp`. 2. `cd .claude/skills/sdlc-studio/scripts`. 3. `python3 -m unittest discover -s tests -t .`. 4. Compare the tree. Reported result: the root is emptied and a greenfield workspace stands in its place. Reproduce in a THROWAWAY copy only, and never in a checkout holding work.

## Proposed Fix

Three parts, and the first is the one that matters.

Identify the test. A test that can build a greenfield workspace at the repository root is one whose work root resolves differently depending on the working directory it is invoked from - almost certainly a `Path('.')` or a `parents[n]` walk that lands somewhere else when `cwd` moves. Find it by bisecting the discovery set in a throwaway copy.

Stop the guard depending on where the checkout happens to live. `startswith(tempfile.gettempdir())` answers `is this path under /tmp`, which is not the question. The question is `is this path the repository under test`, and the discriminating fact is available: refuse any root that contains a `.git` directory, or that resolves to the same path as the repository the test file itself lives in. That refuses correctly whether the clone sits under `/tmp`, under `$HOME`, or anywhere else.

Make the suite defend itself rather than relying on each fixture. A `conftest.py` or a package-level `setUpModule` that records the tree's identity once and refuses any run whose root resolves to it would cover every fixture at once, including the ones nobody has written yet - which is the argument BG0569 already makes for a population-level check rather than a guard per caller.

## Impact

An engineer or a reviewer following this repository's own guidance can lose an entire working copy, with no warning and no refusal, including any uncommitted work and anything gitignored. That is the same loss BG0569 records as unrecoverable when it destroyed 23 mutation registrations. High rather than Critical because it is confined to the working tree of whoever runs it, git restores everything tracked, and the reported instance cost a reviewer's copy rather than a repository.

## Acceptance Criteria

> **Grooming note - what the reproduction found, and where it differs from the report.** The
> destroyer is
> `FixtureRootGuardTests.test_the_fixture_refuses_to_build_outside_a_temp_directory` in
> `.claude/skills/sdlc-studio/scripts/tests/test_transition.py`, at line 4767 of the shipped
> file. It is the test written for BG0536 to pin the guard. It computes
> `repo = Path(__file__).resolve().parents[5]` - the checkout root - and hands it to
> `SurvivorGateTests()._repo`, relying entirely on the guard to refuse it. When the guard does
> not refuse, that call BUILDS the greenfield workspace over the checkout: `src/thing.py`, a
> fake `sdlc-studio/bugs/BG0001-x.md`, an OVERWRITTEN `sdlc-studio/.local/run-state.json` and
> `sdlc-studio/.local/mutation-runs.json`, an emptied `.gitignore` from `_git_repo`, then
> `git init -q -b main` and `git add -A` over the whole tree.
>
> Two corrections to the report, both established by measurement. It is not
> cwd-dependent: `parents[5]` is taken from `__file__`, so the root is the same from every
> working directory, and the same destruction reproduces under `pytest` from the repository
> root. What makes `-s tests -t .` from inside `scripts/` the reported invocation is only that
> the `tests` package is importable from there. And the tree is not EMPTIED - every original
> file survived. What the reporter saw as a greenfield replacement is the composite of an
> emptied `.gitignore`, a new `src/`, a re-`init`ed `.git` and `git add -A` having staged
> everything the emptied `.gitignore` no longer excluded.
>
> AC5's population-level defence - a `conftest.py` or `setUpModule` covering every fixture at
> once - is NOT claimed here. It is the generalisation BG0569 already owns, and its scope is a
> corpus-wide sweep rather than this instance. `tools/repo_writes.py` is dropped from `Affects`
> for the same reason: this repair does not touch it, and saying otherwise would let a claim
> ride on work nobody did.

### AC1

- **Given** a fixture root that IS a checkout - a directory holding `.git` - and that sits
  UNDER `tempfile.gettempdir()`, which is where every rsync copy this repository's own review
  process makes ends up
- **When** the fixture guard is asked about it
- **Then** it REFUSES, naming the working tree. This is the case the shipped guard could not
  construct: `str(root).startswith(tempfile.gettempdir())` is satisfied by every such copy, so
  for the population most likely to hit the defect the refusal never fired. The verifier
  asserts the precondition - that its own fixture root is under the temp directory - before
  asking for the refusal, so a fixture that drifted out of `/tmp` would fail loudly rather than
  quietly stop testing the case.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k a_checkout_under_the_temp_directory_is_still_refused
- **Verified:** yes (2026-08-11)
- **Mutant:** in `test_transition.py`, restore the shipped condition in `_refuse_working_tree` -
  `if not str(root).startswith(tempfile.gettempdir())`.

### AC2

- **Given** the root of the repository this test file itself lives in
- **When** the guard is asked about it
- **Then** it REFUSES and the refusal names the path. The question is asked of the PREDICATE,
  which writes nothing: the shipped test answered it by building the fixture there and
  depending on the guard to stop it, which is a test that cannot be run to find out whether the
  guard works.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k this_repository_root_is_refused_without_being_written_to
- **Verified:** yes (2026-08-11)
- **Mutant:** in `test_transition.py`, delete the `if` in `_refuse_working_tree` so it returns
  the root unconditionally.

### AC3

- **Given** `FixtureRootGuardTests`, whose job is to hand the guard a root it must refuse
- **When** that root is built, from two different working directories
- **Then** it is absolute, it is under the `tempfile` directory it was given, it is neither the
  repository nor inside it, and it is the SAME path both times. This is the criterion the
  shipped test could not state about itself. It is not enough that the guard refuse the
  destructive root; the destructive root must be disposable, so that a guard regression costs a
  temp directory rather than somebody's work.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k the_destructive_root_is_disposable_and_independent_of_cwd
- **Verified:** yes (2026-08-11)
- **Mutant:** in `test_transition.py`, make `FixtureRootGuardTests._fake_checkout` return
  `REPO_ROOT` - the root the shipped test used.

### AC4

- **Given** a checkout with NO `.git` directory - an rsync copy or an export, which is exactly
  how this repository's reviewers are told to work
- **When** the guard is asked about it
- **Then** it still REFUSES, because the repository the test file lives in is known from
  `__file__` and does not need the filesystem to confirm it.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k a_checkout_with_no_git_directory_is_still_refused
- **Verified:** yes (2026-08-11)
- **Mutant:** in `test_transition.py`, drop the `root == REPO_ROOT` arm from
  `_refuse_working_tree`, leaving only the `.git` test.

### AC5

- **Given** a directory INSIDE this repository - `sdlc-studio/`, `tools/`, or the scripts
  directory a suite is commonly invoked from
- **When** it is offered as a fixture root
- **Then** it is REFUSED. A subdirectory is neither the repository nor one of its parents, so the
  first repair accepted it: measured, `_repo(".")` from the scripts directory built 444 paths
  there, including a nested `.git` and a `.gitignore` truncated to nothing. The guard this
  replaced refused it only because it refused everything outside the temp directory, so narrowing
  to the right question without this arm made the guard sharper and the tree less safe.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k a_directory_INSIDE_the_checkout_is_refused
- **Mutant:** remove the `REPO_ROOT in root.parents` clause from `_refuse_working_tree`.

### AC5 and AC6 were WITHDRAWN, and this is why

They restated two criteria BG0536 already owns and pins: that the fixture writes nothing before
it refuses, and the positive control that a genuine temporary directory still builds. Both are
`BG0536` AC1 and AC2, and both point at the same two tests.

The `verify-ratchet` lane refused the commit for exactly that: two acceptance criteria sharing
one selector cannot both discriminate, because a regression in either fails both and neither
says which. Writing a second pair of tests asserting the same properties differently would have
satisfied the lane and pinned nothing new, which is the shape this whole bug is about.

So the properties stay pinned where they belong. This repair strengthened the guard those two
criteria are written against - the discriminator moved from `is this path under the temp
directory` to `is this the repository under test` - and BG0536's criteria were re-run against
the repaired guard and still pass. What BG0573 owns is the four things BG0536 could not state:
that a checkout UNDER `/tmp` is refused, that this repository's own root is refused without
being written to, that the destructive root is disposable and independent of the working
directory, and that a checkout with no `.git` is refused too.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | {{name the production change this test must fail on}} | |
| AC2 | {{name the production change this test must fail on}} | |
| AC3 | {{name the production change this test must fail on}} | |
| AC4 | {{name the production change this test must fail on}} | |
| AC5 | {{name the production change this test must fail on}} | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-11 | sdlc-studio | Reproduced, culprit identified, criteria groomed with mutants |
