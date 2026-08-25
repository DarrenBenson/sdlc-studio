# BG0609: transition.py annotate has no --fields-file, so a value carrying backticks is EXECUTED by the shell and its output silently replaces the text

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional [[derived: criteria 4; plan rows 4; executed 4; killed 4; survived 0; not-run 0; entry point 4 of 4 criteria through the shipped CLI, 0 in-process | fp c39a01f6d775 ]] (the file path stores backticks verbatim, the flag path still works, an unknown key is refused and a non-string value is refused - four criteria, four mutants, each killed by its own verifier)
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01M0JD1W close, 2026-08-24. The re-triage rationale for BG0604 was silently truncated at the backtick and had to be rewritten by hand after the corruption was noticed by reading the artefact back.
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Every other prose-taking verb in this toolchain offers --fields-file and its help calls it THE RECOMMENDED PATH, because backticks and dollar-parenthesis are command substitution inside a shell argument. `transition.py annotate` takes --value and offers no such path. A value quoting a command in backticks is therefore RUN, and whatever it printed is stored in place of the text the author wrote. Nothing reports it: the annotation succeeds, the artefact is written, and the record simply has a hole where the quoted command was.

## Steps to Reproduce

Run `transition.py annotate --id BG0000 --field Note --value "the brief that <backtick>critic.py brief<backtick> generates carries the guard"` from a shell. Observed on RUN-01M0JD1W, 2026-08-24, re-triaging BG0604: the command executed, printed 'critic.py: command not found' to stderr, and the artefact was written with the quoted command replaced by its empty output, leaving the two spaces that had flanked it closed up against each other (not reproduced here: the shell-hazard detector reads that collapsed pair as evidence of a completed substitution, and quoting it verbatim makes this artefact trip the guard it describes). The annotation was reported as successful.

## Proposed Fix

Give annotate the same --fields-file path every sibling has, and name it in the help the same way. The filer's own help already states the rule and the precedent: a filing once ran `git commit -a` against the live repository, which is why `file_finding.py`, artifact.py, sprint.py goal-verdict, critic.py repair and sprint.py review-batch all take a file. annotate is the one that was missed.

## Acceptance Criteria

- [ ] **AC1** Given an annotate value carrying a backticked command supplied through `--fields-file`, when the artefact is written, then the text is stored VERBATIM including the backticks, and nothing is executed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::AnnotateFieldsFileTests::test_a_value_carrying_backticks_is_stored_verbatim
- [ ] **AC2** Given the same annotation supplied through `--field` and `--value`, when it is written, then it still works - the file is the recommended path, not the only one, and breaking the flag path would break every caller in the toolchain
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::AnnotateFieldsFileTests::test_the_flag_path_still_works
- [ ] **AC3** Given a `--fields-file` document carrying a key annotate does not read, when it is supplied, then it is REFUSED naming the key - a key nobody reads is a field that silently went missing, which is the rule the sibling filer already states for this contract
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::AnnotateFieldsFileTests::test_an_unknown_key_in_the_document_is_refused
- [ ] **AC4** Given a `--fields-file` whose `value` is not a string, when it is supplied, then it is REFUSED - a scalar supplied where a string is expected is iterated rather than stored, which is BG0610's shape one contract over
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::AnnotateFieldsFileTests::test_a_non_string_value_is_refused

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `transition.py`, read the flags in `_annotate_fields` and ignore `--fields-file` | Given an annotate value carrying a backticked command supplied through `--fields-file`, when the artefact is written, then the text is stored VERBATIM including the backticks, and nothing is executed |
| AC2 | in `transition.py`, delete the flag branch from `_annotate_fields` | Given the same annotation supplied through `--field` and `--value`, when it is written, then it still works - the file is the recommended path, not the only one, and breaking the flag path would break every caller in the toolchain |
| AC3 | in `transition.py`, drop the unknown-key check from `_annotate_fields` | Given a `--fields-file` document carrying a key annotate does not read, when it is supplied, then it is REFUSED naming the key - a key nobody reads is a field that silently went missing, which is the rule the sibling filer already states for this contract |
| AC4 | in `transition.py`, drop the string check on `value` from `_annotate_fields` | Given a `--fields-file` whose `value` is not a string, when it is supplied, then it is REFUSED - a scalar supplied where a string is expected is iterated rather than stored, which is BG0610's shape one contract over |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
