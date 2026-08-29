# BG0633: transition.py annotate is a THIRD writer of Severity and carries no vocabulary, so the class BG0624 closed at two entry points is still open at the third

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-08-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0624 put a severity vocabulary on both writers it knew about - `file_finding.py file` and `artifact.py new` - and its own claim inventory said "nothing else writes it". A delivery review falsified that by execution: `transition.py annotate --id <bug> --field Severity --value major` exits 0 and writes `> **Severity:** major`, because `severity` is absent from `_ANNOTATE_DENYLIST`. The finding then leaves `barred_open()` and joins the disclosure page, which is the exact harm BG0624 was filed for, arriving through the entry point nobody checked.

## Steps to Reproduce

1. Create a bug fixture with `> **Severity:** Medium`.
2. Run `transition.py annotate --id <id> --field Severity --value major`.
3. Observe exit 0 and `> **Severity:** major` in the file.
4. Run `known_issues.py --bar`: the finding is now named as residue rather than classified.

## Proposed Fix

Route `annotate`'s Severity writes through the same `normalise_severity` the other two writers use, or add `severity` to `_ANNOTATE_DENYLIST` so the field can only be set by a writer that carries the vocabulary. The first is preferable: annotate exists to correct a field, and refusing to correct a severity would be a worse tool. Whichever is chosen, the third writer must be pinned by a test - stopping the class beats catching the instance, and this is the third instance of the same class in one unit.

## Acceptance Criteria

- [ ] **AC1** Given a bug fixture whose Severity is Medium, when `transition.py annotate --field Severity --value major` is run as a SUBPROCESS, then it is REFUSED naming the accepted set and the file is unchanged ||| pytest .claude/skills/sdlc-studio/scripts/tests/`test_transition.py`::AnnotateSeverityVocabularyTests::`test_an_unrecognised_severity_is_refused`
- [ ] **AC2** Given the same fixture, when a RECOGNISED severity is annotated in any case - `high`, `High` - then it is accepted and written in its canonical spelling. The positive control: a guard refusing every severity satisfies the row above ||| pytest .claude/skills/sdlc-studio/scripts/tests/`test_transition.py`::AnnotateSeverityVocabularyTests::`test_a_recognised_severity_is_written_canonically`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-28 | sdlc-studio | Filed |
