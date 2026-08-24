# BG0609: transition.py annotate has no --fields-file, so a value carrying backticks is EXECUTED by the shell and its output silently replaces the text

> **Status:** Open
> **Severity:** High
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

- [ ] **AC1** Given an annotate value carrying a backticked command, when it is supplied through --fields-file, then the artefact stores the text verbatim including the backticks and nothing is executed
- [ ] **AC2** Given the same value supplied through --value from a shell, when the annotation is written, then the stored text matches what the shell passed - the flag path is not made safe by this change and the point is that a file path exists beside it
- [ ] **AC3** Given `transition.py annotate --help`, when it is read, then --fields-file is named as the recommended path in the same terms the sibling verbs use
- [ ] **AC4** Given a --fields-file document carrying a key annotate does not read, when it is supplied, then it is REFUSED rather than ignored, matching `file_finding.py`'s behaviour

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
