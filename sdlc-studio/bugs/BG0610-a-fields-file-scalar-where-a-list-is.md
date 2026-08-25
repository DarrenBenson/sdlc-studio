# BG0610: A --fields-file scalar where a list is expected is iterated CHARACTER BY CHARACTER, so one Verify line becomes one letter per criterion

> **Status:** Open
> **Severity:** High
> **Premise narrowed 2026-08-25:** the `acs` character-by-character limb was already closed under 4f276b31. What stands is the untyped path: `artifact.py:154` still reads `for i, v in enumerate((f.get("verify") or []), 1)`, so a scalar supplied for a list-valued field is still iterated per character. Build the type check; do not re-fix `acs`. Found by an independent goal review before any code was written.
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** artifact.py:154, `for i, v in enumerate((f.get("verify") or []), 1)`. Reproduced by inspection of the artefact it produced: sdlc-studio/stories/US0684 as first written carried six Verify lines of one character each. The criteria themselves rendered in a non-canonical bullet form at the same time, so the file needed rewriting by hand.
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The fields-file path validates that every KEY is one the writer reads and refuses an unknown one, but it does not validate TYPES. A list-valued field supplied as a scalar string reaches `enumerate(f.get("verify") or [])` and Python iterates its characters, so a single Verify expression is distributed one LETTER per acceptance criterion. The artefact is written, indexed and reported as created. Nothing refuses, and the damage is only visible by reading the rendered file.

## Steps to Reproduce

Write a fields-file with a list of three `acs` and a scalar string `verify`. Run `artifact.py new --type story --fields-file <it>`. Observed on 2026-08-24 creating US0684: six criteria were written with Verify lines reading p, y, t, e, s and t - the letters of the word pytest, one per criterion. The command reported `created US0684 ... (indexed=True, epic_linked=True)` and exited 0. The same shape reaches any list-valued field on this path.

## Proposed Fix

Validate the TYPE of every field beside its name, with the same refusal the unknown-key check already uses. A scalar supplied where a list is expected should be refused naming the field - or coerced to a one-element list, which is what a writer means - but never iterated. Refusing is the better fit here: the filer already argues that a key nobody reads is a field that silently went missing, and a character-sliced value is the same failure one level down. `file_finding.py` shares the fields-file contract and should be held to the same rule.

## Acceptance Criteria

- [ ] **AC1** Given a fields-file supplying a scalar string for a list-valued field, when the artefact is created, then the command REFUSES naming the field and the type it expected, and no artefact is written
- [ ] **AC2** Given a fields-file supplying a proper list for that field, when the artefact is created, then it is written exactly as today - the paired control, so the refusal is shown to discriminate rather than to reject every fields-file
- [ ] **AC3** Given a fields-file supplying a scalar for a scalar field, when the artefact is created, then it is accepted, so the check does not simply demand lists everywhere
- [ ] **AC4** Given the same scalar-for-list shape supplied to `file_finding.py`, when the finding is filed, then it is refused on the same rule, because the two share the fields-file contract

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
