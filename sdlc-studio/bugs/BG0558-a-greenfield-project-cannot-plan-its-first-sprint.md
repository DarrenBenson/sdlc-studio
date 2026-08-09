# BG0558: a greenfield project cannot plan its first sprint: every Affects path is unresolvable because the code does not exist yet, and the blocking grooming lane calls that a fictional Affects

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py, .claude/skills/sdlc-studio/scripts/tests/test_bug_regressions.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Probed through the shipped CLI on a throwaway fixture, 2026-08-09, during a v5 release-readiness sweep. `init.py run` on a clean git repo, one story with `Affects: src/auth/signup.py, tests/test_signup.py` and `Points: 3`, then `sprint.py plan --write`: exit 2, no run written, `US0001 lacks: Affects (no declared path resolves: ...)`. Replacing one path with a file that exists on disk makes the same unit groom clean, which isolates the cause to path resolution rather than to the field being absent.
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The grooming lane at sprint.py:2110 refuses a unit when EVERY declared `Affects` path fails to resolve on disk. Its own comment states the intent: "All declared paths unresolvable = a fictional Affects. Named so the author can fix the typo." That is the brownfield typo case BG0144 was filed for. In a greenfield project every path is legitimately unresolvable, because the story describes code that has not been written yet - so the rule refuses the first sprint plan of every new project, which is the one path a first-time user is guaranteed to take.

The refusal is hard, not advisory: `sprint.breakdown` defaults to `enforce` and the config comment states "Omission is not an escape - an absent config BLOCKS". `init run` writes no override, so a project created by the shipped initialiser is in the blocking state from the moment it exists.

Two further problems make it worse than a wrong rule. The message misdiagnoses: it prints `lacks: Affects` and then explains how to add an `Affects` line the story already carries, so the author is sent to fix a field that is present and correct. And the only remedy offered is a config opt-out, which teaches a new user to switch off a grooming gate on day one.

The same command already holds the opposite rule one lane over. The advisory `Affects contradicted by the unit's own content` lane prints `declared but not on disk - changelog.d/US0469.md (a file the unit CREATES is fine)`. Two lanes in one command, one field, contradictory rules, and the blocking one holds the rule that is wrong.

## Steps to Reproduce

1. `git init` a clean directory and commit anything. 2. `python3 scripts/init.py --root <dir> run`. 3. Write a story with `Status: Ready`, `Points: 3` and `Affects: src/auth/signup.py, tests/test_signup.py` (neither file exists - the story is about writing them). 4. `python3 scripts/sprint.py plan --root <dir> --worklist <story-id> --write --sprint-goal "..."`. 5. Exit 2, no plan printed, no run written, and the reason given is that the unit lacks an Affects it in fact declares. Read the exit code directly, not through a pipe: `| tail` reports tail's status.

## Proposed Fix

A declared path that does not resolve should be distinguished by whether the unit CREATES it. The advisory lane beside this one already draws that distinction and should be the single reader, on the same reasoning the AC-grooming code gives for reading `verify_ac` rather than writing a second parser: a second definition disagrees with the first. Minimum: an unresolvable path whose parent directory is absent, or whose unit's own criteria describe creating it, is not a fictional Affects. The message must also stop reporting a declared field as absent - `lacks: Affects` and `Affects names only paths that do not exist yet` have different fixes, and sending the author to the wrong one is the defect this bug is mostly made of. Pin the greenfield case through the COMMAND, in a fixture whose tree contains none of the declared paths, with the brownfield typo case beside it as the positive control - the rule must still catch a real typo.

## Acceptance Criteria

> **Plan repaired after a REJECT at plan review (2026-08-09, qa seat, brief `6673725b2331`).**
> The first plan was rejected on six blocking findings, and two of them changed what this unit
> IS rather than how it is tested. Both rulings are stated here so the repair is not read as a
> widening of convenience.
>
> **Ruling 1 - the discriminator is a basename match, not "does the path exist".** The rule was
> written to catch a typo against an existing tree (BG0144). A typo and a creation are already
> distinguishable by shipped code: `file_finding.affects_suggestions` answers `did you mean X?`
> when the declared basename exists elsewhere in the repository, and `no file named X found in
> the repo` when it does not. The first is a typo and must still refuse; the second is a file
> the unit will create and must not. The decision and the message therefore come from ONE
> computation (LL0042), and no new heuristic is invented.
>
> **Ruling 2 - the invariant HOLDS and two shipped fixtures MOVE.**
> `test_affects_resolvable.py::test_the_predicate_and_the_grooming_gate_never_disagree` pins the
> writer check and the grooming gate to one verdict. It must keep passing: both sides read the
> same predicate and move together, which is the whole point of it. But two shipped fixtures -
> `src/does-not-exist.py` and `nowhere/ghost.py` - have no basename anywhere in their tree, so
> under the corrected rule they are creations rather than typos and stop being refused. Those
> fixtures encode `unresolvable` where the rule means `typo`, which is this bug one level down.
> They are replaced with genuine typos and carry a comment naming BG0558. A fixture changed to
> keep a suite green is the thing this repository files bugs about, so the change is stated as a
> ruling here before it is made, not explained afterwards.
>
> The advisory lane is deliberately NOT given a fictional-versus-creates verdict. It computes
> none today, it is advisory by construction (`affects_mismatch`'s own docstring says a path to a
> file the unit will create is legitimate), and forcing a verdict into it to satisfy a symmetry
> would add a second decider of the thing this repair exists to have one decider of.

### AC1

- **Given** a project created by `init run` in an empty tree, on the shipped configuration with no
`sprint.breakdown` override and no `definition-of-ready.md` (so the grooming lane is ENFORCING,
which the fixture asserts before it asserts anything else), holding one story sized with `Points`
and an `Affects` naming only files whose basenames exist nowhere in that tree
- **When** `sprint.py plan --worklist <story> --write` is run as a subprocess
- **Then** the exit status is 0, a run is written to `sdlc-studio/.local/run-state.json`, and the
  story is in the batch.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py -k greenfield_creation_plans
- **Verified:** yes (2026-08-09)
- **Mutant:** in `file_finding.py`, make `fictional_affects` return every unresolvable path (the rule as it stands today) - the greenfield fixture must go from a written run to exit 2.

### AC2

- **Given** ONE tree containing a real file, and two units in it - one declaring a path whose
  basename exists elsewhere in that tree (a typo), one declaring a path whose basename exists
nowhere (a creation)
- **When** each is put through `sprint.py plan --write` as a subprocess
- **Then** the typo is REFUSED with a non-zero exit and no run written, and the creation is
  accepted - the two verdicts differing within one tree, so no repair keyed on "is this project
empty" can satisfy this criterion.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py -k typo_and_creation_differ_in_one_tree
- **Verified:** yes (2026-08-09)
- **Mutant:** widen `fictional_affects` to return nothing at all (accept every unresolvable path) - the typo half must fail, which is the OVER-WIDENING this repair actually risks and which deleting the rule entirely would also produce.

### AC3

- **Given** the typo fixture from AC2, whose refusal is the only one left after this repair
- **When** the refusal is read
- **Then** it names the unresolvable path and the basename match that makes it a typo, and it does
NOT report the unit as lacking a field the unit declares: the substring `lacks: Affects` does not
appear for a unit whose `Affects` is present.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py -k refusal_names_the_typo_not_a_missing_field
- **Verified:** yes (2026-08-09)
- **Mutant:** in `sprint.py`'s `_breakdown_detail` render, put the bare `Affects` entry back into `missing` beside the detail - the assertion on the absent-field wording must fail. And separately, strip the `did you mean` suggestion from the refusal - the assertion that the message names the match must fail, so both clauses of this criterion carry a mutant.

### AC4

- **Given** the three writers that refuse a declared-but-unresolvable `Affects` -
`file_finding.check_affects_resolvable` (which `file_finding.file`, `artifact new` and `refine
apply` all call) and the grooming gate `sprint.py` reads
- **When** the shared predicate `file_finding.fictional_affects` is replaced in-process
- **Then** every one of them follows, and
`test_the_predicate_and_the_grooming_gate_never_disagree` still passes unchanged - the invariant
holds because both sides read one predicate.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py -k one_predicate_decides_for_every_writer
- **Verified:** yes (2026-08-09)
- **Mutant:** give the grooming gate its own inline basename check instead of calling `fictional_affects` - replacing the shared predicate must then stop moving the gate, and the test must fail. A faithful copy is not a valid mutant here, so the copy is DIVERGENT: it compares the basename case-sensitively where the shared one does not.

### AC5

- **Given** the greenfield fixture from AC1
- **When** a story is created through `refine.py apply` with an `Affects` naming only files it will
  create
- **Then** the story is minted - the second call site that refused CR0542's own rehearsal stories
  and is the reason this criterion exists.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py -k refine_apply_mints_a_creating_story
- **Verified:** yes (2026-08-09)
- **Mutant:** restore the all-unresolvable refusal inside `check_affects_resolvable` only, leaving the grooming gate repaired - the test must fail, proving this criterion is not satisfied as a side effect of AC1.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `file_finding.py`, delete the basename-match branch of `fictional_affects` so it returns every path that does not resolve | |
| AC2 | in `file_finding.py`, change `fictional_affects` to return an empty list unconditionally | |
| AC3 | in `sprint.py`, re-add the bare `Affects` token to the `missing` list in `_breakdown_detail`; and separately drop the `affects_suggestions` call from the refusal string | |
| AC4 | in `sprint.py`, replace the `fictional_affects` call with an inlined case-sensitive basename comparison | |
| AC5 | add an early `return declared` guard to `check_affects_resolvable` in `file_finding.py`, bypassing the shared predicate for writers only | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Filed |
