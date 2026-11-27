# BG1768: The builder's diff-coverage mutation pass refuses uncommitted work, so the pass the lane brief asks for never runs before review

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py, changelog.d/BG1768.md
> **Evidence:** run twenty-eight wave one hand-backs (COST, CARRY, SPEND, CACHE, SEAT, RELREC): each reported the --since main pass refused
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** orchestrator; agent; claude-opus-5-5
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-26T08:21:55Z

## Summary

A builder in run twenty-eight was asked (by the run's own builder prompt; the shipped lane brief uses `--edits`) to run `mutation.py run --since main` over its changed lines before hand-in, but a builder's work is uncommitted by design, and the runner refuses a surface carrying uncommitted work. Every builder in run twenty-eight's first wave reported the refusal and relied on its own chosen mutants, and the reviewers then found the mutants the enumerating pass exists to surface (US1233's four, US1332's raw-token swap).

## Steps to Reproduce

In a lane worktree with staged, uncommitted changes to a script, run `python3 .claude/skills/sdlc-studio/scripts/mutation.py run --files <script> --since main --test 'python3 -m pytest -q <test>' --dry-run`; it refuses with the uncommitted-surface route instead of enumerating the changed lines.

## Proposed Fix

Let `--since` judge the staged diff (index against the base) when the surface carries staged work, mutating a private copy so the working tree is never touched, or have the brief name a route that works on uncommitted work; keep refusing unstaged edits the runner cannot attribute.

## Acceptance Criteria

### AC1: a staged target is mutated in a private copy of the index under --since

- **Given** a repository whose configuration sets `quality.mutation_max: 2` and whose `pkg/calc.py` has a staged, uncommitted change adding lines 4 and
  5 (`if x > hi: return hi`), nothing unstaged, and a staged test that does not test the upper
  bound
- **When** `mutation.py run --files pkg/calc.py --since main --test 'python3 -m pytest -q tests'`
  is run
- **Then** it applies mutants only on lines 4 and 5, reports the survivor on line 5 by the
  repository's path, prints no `TREE UNESTABLISHED` line, and leaves the index, the working tree
  and `git status --porcelain` byte for byte as they were. Fails on: HEAD, which refuses with
  exit 2, `uncommitted changes on pkg/calc.py`.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py::StagedSinceTests::test_a_staged_target_is_mutated_in_a_private_copy_of_the_index

### AC2: unstaged and untracked work is still refused, and the refusal names the staged route

- **Given** the same file with an unstaged edit on top of its staged one, and an untracked
  target
- **When** the same run is made on each
- **Then** each exits 2 with refusal kind `uncommitted-surface`, applies no mutant, and its
  route names staging the work and re-running with `--since` beside `git worktree add` and
  committing or stashing. Fails on: HEAD, whose route is "Mutate an ISOLATED CHECKOUT instead
  (`git worktree add`), or commit or stash the work first." and names no staged route.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py::StagedSinceTests::test_unstaged_and_untracked_work_is_still_refused_naming_the_staged_route

### AC3: the JSON report states the run was isolated and names repository paths

- **Given** the AC1 repository
- **When** the run is made with `--format json`
- **Then** `refused` is false, `summary.tree.isolated` is true with a reason naming a private copy
  of the index, every `targets` entry and every mutation's `file` is the repository's path, and
  no scratch copy remains after the run. Fails on: HEAD, which refuses; and the same mutants run
  by hand in an exported copy report `isolated: None` and the copy's paths.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py::StagedSinceTests::test_the_report_states_isolation_and_names_repository_paths

### AC4: the review reference states the staged route at no cost in lines

- **Given** reference-review.md's mutation isolation section
- **When** it is read
- **Then** its author-side rule says the runner refuses a target with unstaged or untracked
  changes and judges a fully staged target under `--since` in a private copy of the index, it
  still says `mutation.py` refuses uncommitted changes and names the isolated checkout, and the
  page is the same number of lines. Fails on: HEAD, where the section has 0 mentions of staged
  work or `--since`.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_staged_since.py::StagedSinceTests::test_the_review_reference_states_the_staged_route

## Notes

- Ran: the refusal at HEAD in a fixture, and the private-copy prototype (`git checkout-index -a
  --prefix=<scratch>/` then `mutation.py run` there) with index and status digests before and
  after (Evidence BG1768).
- Compute changed lines from the real repository (`git diff --cached -U0 --src-prefix=a/
  --dst-prefix=b/ <since>`, as `changed_lines` already parses), map scratch paths back to
  repository paths in every report field, and set `tree_isolation` to isolated for the copy.
- Narrow by design: without `--since`, a staged target is refused as now.
- Beside the existing tests: mutation.py is read by 35 modules. test_mutation's
  `test_mutation_refuses_a_dirty_file` and both `test_an_uncommitted_surface_is_reported_as_that_
  reason` tests write the target without staging it, so they stay refused under AC2;
  `test_the_refusal_names_the_isolated_checkout_route` requires `worktree add` in the route, which
  AC2 keeps; `test_since_includes_untracked_files` selects an untracked file under `--since`, which
  AC2 then refuses as now. test_doc_claims.MutationIsolationTests holds the section to "isolated
  checkout", "never the author's (working) tree", "silently reverted", `mutation.py[^.]*refus`
  and "uncommitted changes", and mutation.py to exposing `dirty_targets`; AC4's wording keeps all
  five.
- Budget: reference-review.md is at its ceiling (859 lines; 819 base, 4.88% over), so the
  rewrite of lines 539-541 must be net zero. US1339 and its carry BG1769 also edit this page.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | orchestrator | Filed |
| 2026-11-26 | orchestrator (D0545) | Groomed: criteria with Fails on run at HEAD and Verify nodes, from the engineering seat's draft; default and this repository's setting per D0647 (product seat). |
| 2026-11-26 | orchestrator (D0545) | AC1's Given names `quality.mutation_max`: 2: the approach review ruled that --since keeps its ceiling rule (changed lines first, then the rest of the ceiling), so only lines 4 and 5 are mutated at a ceiling of 2. |
