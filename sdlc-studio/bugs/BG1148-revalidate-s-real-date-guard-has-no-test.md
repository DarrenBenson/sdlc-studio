# BG1148: revalidate's real-date guard has no test, its refusal prefix names --extend for any bad fields file, and the gate hint and four docs show --extend with no --reason

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-agentic-lessons.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, changelog.d/BG1148.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, BG1139 APPROVE by qa-seat-BG1139-r1 (brief b512bde79689).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T02:48:17Z

## Summary

qa-seat-BG1139-r1's APPROVE of BG1139 (2026-11-01) left three follow-ups. (1) The real-date guard in `revalidated_of` (lessons.py:157-159) has no test: the mutant `if not stamp` survives every RevalidationRecordTests case, so a hand-written `Revalidated: TBD` would count as judged and the US1105-US1109 verifiers would pass on it. (2) The refusal prefix at lessons.py:183 wraps every ValueError from `resolve_prose`, so a bad --fields-file on `--close` prints 'error: --extend records why the lesson still holds: ...' with no --extend given. BG1139 introduced this; at daf2f295 the message was plain. It still exits 2 naming the real cause. (3) The close-gate refusal at lessons.py:1075 says 'extend them (revalidate --extend)', and help/gate.md:229, reference-config.md:266, reference-agentic-lessons.md:428 and reference-scripts-verify.md:34 show `--extend` with no `--reason`. Followed as written, each is now refused.

## Steps to Reproduce

1. Apply `if not stamp` at lessons.py:157 and run `test_lean_lesson_lifecycle.py`: green.
2. `revalidate --close L-0001 --fields-file bad.json` with an unknown key: the message names --extend.
3. Follow the hint at lessons.py:1075 as written: refused.

## Proposed Fix

Add a fixture with a malformed Revalidated value that must still be listed. Scope the prefix to the missing-reason refusal only. Add `--reason` to the hint and to the four doc lines.

## Acceptance Criteria

- [ ] **AC1** A lesson whose Revalidated value is not a real date is listed by --unjudged-since, and the mutant that accepts any non-empty value fails a test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py
- [ ] **AC2** A bad --fields-file on --close is refused without naming --extend, and the missing-reason refusal on --extend still names --reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py
- [ ] **AC3** The close-gate hint and the four doc lines show `--extend` with `--reason`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py

## Impact

A verifier five stories rely on could pass a record with no date, and two places tell the operator to run a command that is refused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
