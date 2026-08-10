# BG0564: a creation whose basename is a common one - `__init__.py`, `README.md` - is still refused as a typo, so the greenfield repair is incomplete for exactly the files new packages create

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** Round-2 delivery review of RUN-01KZM49Y, 2026-08-10, established by execution in a throwaway fixture: `Affects: src/newpkg/__init__.py` in a tree holding any other `__init__.py`, and `guide/README.md` in a tree holding any other `README.md`, are both classified as typos and refuse the plan. Refused at the base ref too, so it is not a regression - it is the residual of the greenfield repair rather than damage from it.
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`fictional_affects` distinguishes a typo from a creation by asking whether the declared basename exists anywhere in the tree. That is right for a distinctive name and wrong for a common one. `__init__.py`, `README.md`, `index.ts`, `main.go` and `conftest.py` exist in almost every repository, so a unit creating a NEW package or a NEW document is told it has mistyped a path to a file it has never seen.

The direction is the tolerable one - it refuses honest work rather than admitting a mistake - but it lands on precisely the work a growing project does most: adding a package. And the remedy an author will reach for is the config opt-out, which stands the whole grooming lane down.

The signal that would separate them is already available and unused: a basename match in a DIFFERENT directory from the declared one is a typo only if the directories are plausibly confusable. `src/auth/signupp.py` beside `src/auth/signup.py` shares a parent; `src/newpkg/__init__.py` beside `src/other/__init__.py` does not, and nobody typing the first meant the second.

## Steps to Reproduce

1. Build a tree holding any `__init__.py`. 2. Write a unit declaring `Affects: src/newpkg/__init__.py`, a file it will create. 3. `sprint.py plan --worklist <unit> --write`. 4. Refused as a typo, naming a file in an unrelated package as the one that was meant.

## Proposed Fix

Narrow the typo signal: a basename match counts only when it is plausibly the same file - the same parent directory, or a small edit distance on the path - rather than any occurrence anywhere in the tree. Pin BOTH shapes in one fixture: a mistyped sibling refuses, and a new package's `__init__.py` beside an unrelated one is accepted. The measured hazard the rule exists for is a wrong DIRECTORY PREFIX on a file that really exists, so scoping the match to the path rather than to the basename alone stays true to it.

## Acceptance Criteria

- [ ] **AC1** A unit creating `src/newpkg/__init__.py` in a tree holding other `__init__.py` files plans successfully through the shipped CLI
- [ ] **AC2** A unit declaring a mistyped sibling of an existing file is still refused, proving the signal was narrowed rather than removed (positive control, same tree)
- [ ] **AC3** Both shapes are asserted in ONE tree, so no repair keyed on a property of the whole project can satisfy them

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Filed |
