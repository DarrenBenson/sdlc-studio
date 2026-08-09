# BG0558: a greenfield project cannot plan its first sprint: every Affects path is unresolvable because the code does not exist yet, and the blocking grooming lane calls that a fictional Affects

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
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

- [ ] **AC1** The shipped `sprint plan --write` accepts a unit whose declared Affects paths do not exist on disk when the unit creates them, on a fixture project containing none of those paths, and writes the run
- [ ] **AC2** A unit whose Affects is a genuine typo against an existing tree is still refused, proving the repair did not delete the rule (positive control, same fixture family)
- [ ] **AC3** The refusal message for a unit that declares Affects never says the unit `lacks: Affects`, and names the real condition and its remedy
- [ ] **AC4** One reader decides whether an unresolvable path is fictional, and the test proves the sharing by changing that reader and asserting BOTH the blocking lane and the advisory lane follow

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Filed |
