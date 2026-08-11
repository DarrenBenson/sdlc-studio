# BG0570: the write-time Verify guard cannot tell a typo from an ordering, so it refuses the first story of every greenfield project

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`check_verify_selectors` refuses any selector for which `verify_ac.selector_resolves` returns False. That predicate returns False for TWO different facts: a node absent from a test file that EXISTS (a typo - the recurring shape CR0508 was filed about, and the one a write-time guard must refuse), and a selector whose test file does not exist at all, where `_collect_nodes` returns None and `selector_resolves` documents its own answer as 'the file itself does not collect - the node/pattern cannot resolve'. The second is not a mistake. Writing the story before the test is ordinary test-after-story ordering, and in a greenfield project NO test file exists yet, so the guard refuses the first story anybody writes. This was invisible while only `file_finding.file` called the guard, because bugs and CRs are filed against code that already exists; wiring it into `artifact.py new` under US0667 surfaced it immediately as two suite regressions, both on fixtures whose selectors name test files absent from a temp workspace.

## Steps to Reproduce

1. In a workspace where `tests/test_gate.py` does not exist, run `artifact.py new --type story --epic EPxxxx --title x --ac 'it works' --verify 'pytest tests/test_gate.py::GateTests::test_refuses'`. 2. It is REFUSED with 'a `Verify:` selector names no test that exists', though the author is writing the story first and the test next. 3. The same refusal fires for every story in a project that has no test files yet. Observed as `test_artifact.py::PipeInAcTests::test_a_correctly_paired_ac_and_verify_is_byte_identical_and_silent` and `test_validate.py::ScopedCheckTests::test_a_single_artefact_can_be_checked` on 2026-08-11.

## Proposed Fix

Separate the two facts before deciding. A helper on `verify_ac` - the module that owns selector parsing, so the question is still answered in one place - reports the test FILE a selector targets; the guard then refuses only when that file EXISTS and does not contain the node, and treats a target file that is absent as UNJUDGED (accepted, reported), which is the same treatment an unknown runner already gets. This is the distinction `fictional_affects` already draws for declared paths under BG0558: a basename that exists elsewhere is a typo and is refused, a path that exists nowhere is a not-yet-created file and is not. The guard keeps the case it was built for - real file, real method, wrong class - and stops forbidding an ordering.

## Acceptance Criteria

### AC1: a typo is still refused

- **Given** a `Verify:` selector naming a node absent from a test file that EXISTS on disk - the
  recurring shape CR0508 was filed about: real file, real method, wrong class
- **When** the artefact is written through `file_finding.file` or through `artifact.py new`
- **Then** BOTH still REFUSE, so the fix narrows the guard without disarming it.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k a_node_absent_from_an_existing_file_is_still_refused
- **Mutant:** in `file_finding.py`, treat every False verdict as unjudged.

### AC2: an ordering is accepted, and so is a file that will not collect

- **Given** two selectors that make `selector_resolves` answer False for reasons that are NOT a
  typo: a test file that does not exist and whose basename exists nowhere (the author writing the
  story before the test, and every story in a greenfield project), and a test file that EXISTS but
  yields no node list because it will not collect (a missing import, a syntax error, a project
  whose dependencies are not installed yet)
- **When** the artefact is written through `file_finding.file` AND through `artifact.py new`
- **Then** both are ACCEPTED by both writers, and the two are REPORTED DIFFERENTLY: the
  uncollectable file carries a note naming it, because that is abnormal and the author wants to
  know; the not-yet-written file is accepted SILENTLY, because writing the story before the test
  is the normal ordering and the only one available in a greenfield project, so a note there fires
  on every story anybody writes. Both halves are asserted - the note by its text, the silence by
  its absence - because "accepted" alone is satisfied by a guard that says nothing either way, and
  "always reported" is satisfied by one that cries wolf on the normal case.

  Reported-in-both-cases was the drafted wording and the noise gate refused it: the notes pushed a
  passing suite from 119 diagnostic lines to 150. The gate was right for the product reason, not
  just the test one - the same reason `affects-unresolvable` is reported only at a terminal status.

  A third case was drafted here and withdrawn: "a selector naming no target is REFUSED". It is
  unobservable. `selector_resolves` and the classifier read the target through the SAME parser, so
  a selector with no identifiable target is answered None - unjudged - before any classification
  happens, and the branch that would refuse it cannot be reached. An independent review proved it
  by deleting that branch and watching every test still pass. The branch is kept as a documented
  fail-closed default rather than deleted, because the alternative is to let a None target raise
  and be caught, which makes the verdict depend on an exception instead of a decision - but a
  criterion asserting a behaviour nobody can observe would be a criterion that cannot fail.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k a_selector_that_is_not_a_typo_is_accepted_and_reported
- **Mutant:** in `file_finding.py`, refuse whenever the target file yields no node list, collapsing the uncollectable case back into the typo case.

### AC3: a misspelled FILENAME is still a typo

- **Given** a `Verify:` selector whose test file does not exist because the PATH was mistyped, and
  a file of that basename does exist elsewhere in the tree
- **When** the artefact is written
- **Then** it is REFUSED, naming the near miss - the same two-way split `fictional_affects` already
  draws for declared paths under BG0558, where a basename that exists elsewhere is a typo and a
  path that exists nowhere is a not-yet-created file. Without this, AC2 would launder every
  misspelled filename into "greenfield ordering", which is the hole the guard exists to close.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k a_misspelled_test_filename_is_still_refused
- **Mutant:** in `file_finding.py`, drop the basename check so an absent target file is always unjudged.

### AC4: one reader still answers

- **Given** the question "which test file does this selector target"
- **When** it is asked by the resolver, by the near-miss hint and by the write-time guard
- **Then** ALL THREE resolve through one helper on `verify_ac`, proven by replacing that helper and
  asserting the WRITER's verdict moves with it - the shape
  `test_one_reader_answers_whether_a_selector_resolves` already uses. `verify_ac` currently parses
  a selector's target in three places with two different predicates, so a fourth copy would make
  the divergence this criterion exists to prevent more likely, not less.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k one_reader_answers_which_file_a_selector_targets
- **Mutant:** in `file_finding.py`, inline a regex that splits the selector on `::` instead of calling the helper.

## Impact

Who: every greenfield project, and any author who writes a story before its test. What breaks: `artifact.py new` and `file_finding.file` refuse to create the artefact at all, so the ordinary TDD sequence is unavailable and a new project cannot write its first story with a Verify line. This is the same consumer-facing class as BG0558, which D0133 was re-scoped around: a guard correct about this repository's mature corpus and wrong about a tree that has not been written yet.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Filed |
