# BG0562: _then_clause strips the bold markers off a non-bulleted Then line before testing for them, so the criterion falls back to its whole block and the overlap check reports the author's own mutant as a 100% restatement

> **Status:** Fixed
> **Verification depth:** functional (executed: _then_clause over a non-bulleted Then line returned the whole criterion block before and the clause after, with the bulleted form unchanged as the control; mutation: 1 declared mutant, anchor asserted unique, bytecode purged, python3 -B, KILLED, restore byte-exact)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Hit while repairing BG0558's test plan in RUN-01KZM49Y, 2026-08-09. `verify_ac.py testplan derive --unit BG0558 --dry-run` refused five of five criteria with `restates its own criterion - 100% of its substance is the Then clause`, for mutants whose token overlap with the Then clause is close to zero. Probed directly: `_then_clause(lines, s, e)` returns 877, 869, 865, 979 and 635 characters for AC1 to AC5 - the whole criterion block each time, beginning `### AC1  **Given** ...` - rather than the Then sentence.
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_then_clause` scans for the criterion's `Then` line with:

```python
stripped = line.strip().lstrip("-*").strip()
if stripped.lower().startswith("**then**")
```

`lstrip("-*")` removes every leading `-` and `*`. On a BULLETED line (`- **Then** x`) it stops at the space after the dash, the bold markers survive, and the test matches. On a plain paragraph line (`**Then** x`) it eats the `**` itself, leaving `Then** x`, which cannot start with `**then**`. So the one shape it must not miss is the one shape it always misses.

The fallback is what makes this expensive: `return " ".join(lines[start:end])` - the entire criterion block. That block contains the criterion's own `- **Mutant:**` bullet, so the mutant is measured for overlap against a string that CONTAINS the mutant, and the ratio saturates. Every affected criterion is refused with a message accusing the author of restating the criterion, which is the opposite of what happened.

The direction is the bad one twice over. It refuses correct work while blaming the author, and the message sends them to rewrite a mutant that was already fine - the fix that appears to work is to make the mutant progressively less descriptive until the ratio falls, which degrades exactly the field US0629 exists to make substantive. And a criterion carrying NO mutant bullet inside it gets its overlap measured against Given and When as well, so the ceiling means something different for every criterion depending on prose shape.

The function's own docstring records that its first version returned an empty string and 'every overlap measured 0% and the restatement limb accepted everything', caught only by a test that drove the CLI. This is the same defect with the sign reversed, and the CLI-driving test did not catch it because the fixtures are all bulleted.

## Steps to Reproduce

1. Write a criterion whose Given/When/Then are plain bold paragraph lines rather than list bullets - the shape several shipped bug artefacts use - and give it a `- **Mutant:**` bullet. 2. Add a Test Plan row whose mutant names a file and an edit and shares almost no vocabulary with the Then clause. 3. `verify_ac.py testplan derive --unit <id> --dry-run`. 4. It refuses with `restates its own criterion - 100% of its substance is the Then clause`. 5. Call `verify_ac._then_clause(lines, start, end)` directly and observe it returns the whole block rather than the Then sentence.

## Proposed Fix

Test for the marker before stripping it: match `**then**` on the line with only whitespace and an optional list bullet removed, never with the emphasis characters removed. `re.match(r'^\\s*(?:[-*]\\s+)?\\*\\*then\\*\\*', line, re.I)` covers both shapes and cannot eat the markers it is looking for. Separately, the fallback must not be the whole block: a criterion whose Then cannot be found should be reported as unparseable rather than silently measured against a superset of itself, because a fallback that includes the mutant guarantees the check fires on correct input. Pin BOTH shapes - bulleted and paragraph - through `verify_ac.py testplan derive` in one fixture family, since every existing fixture is bulleted and that is precisely why the suite is green on this.

## Acceptance Criteria

- [x] **AC1** Given a criterion whose `Then` line is a plain paragraph (`**Then** ...`) rather than a bullet, when `_then_clause` reads it, then it returns the clause itself - not the whole criterion block, which carries the criterion's own `Mutant:` bullet and makes every honest mutant read as a restatement of itself.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k then_clause

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in verify_ac.py `_then_clause`, revert the bullet strip to `line.strip().lstrip("-*").strip()` so the bold markers are eaten off a non-bulleted Then line | Given a criterion whose `Then` line is a plain paragraph (`**Then** ...`) rather than a bullet, when `_then_clause` reads it, then it returns the clause itself - not the whole criterion block, which carries the criterion's own `Mutant:` bullet and makes every honest mutant read as a restatement of itself. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Filed |
