# BG0627: eleven other fields-file consumers carry the same `or ""` guard, so a falsey value is reported as a missing field across five more modules

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/ledger.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** Enumerated 2026-08-27 by an independent plan review of BG0622, which was asked to list the set rather than assert one: 12 non-test call sites across 10 modules, of which 5 modules carry the identical `str(x.get(k) or "").strip()` guard - ledger.py:86, decisions.py:468, handoff.py:764, validate.py:1063, and roughly 16 field validators in file_finding.py between lines 1442 and 1932. `verdict_polarity` behaviour confirmed by execution: "True" reads yes, "False" reads no, while "", "None" and "0" all read unclear.
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0622 repairs `_seat_from_dict` in `sprint.py`, where `str(d.get(f) or "").strip()` makes a JSON `false` indistinguishable from a missing field. The same shape sits on eleven other fields-file consumers across five modules, so the same class of value is mis-reported there too: `str(0 or "")` is empty, and so is `str(False or "")`.

This is deliberately NOT one blanket repair. The right rule differs by field TYPE, and applying one rule to both is how a fix becomes a defect:

- a TYPED field - a yes/no verdict, a count - must be tested for PRESENCE and then coerced, so both `false` and `0` reach the record;
- a PROSE field - `rationale`, `note`, `title`, `reason` - must be tested for presence AND for being non-empty after coercion, because accepting `"rationale": false` would store the string `False` as a rationale, which is worse than refusing it.

The enumeration above is a lower bound, not a boundary - LL0043. So the deliverable is not only the edits: it is a mechanical check that no NEW `or ""` reaches a fields-file consumer, without which the list silently exempts whatever the next author adds.

## Steps to Reproduce

1. In any of the five modules, pass a fields-file whose typed field carries a JSON `false` or a `0`. 2. The loader reports it as a missing field, naming a key the document plainly contains. 3. Change the value to `true` and it is accepted. Measured on `sprint.py` as BG0622; the same guard shape was then enumerated at ledger.py:86, decisions.py:468, handoff.py:764, validate.py:1063 and across `file_finding.py`'s field validators.

## Proposed Fix

Split the guard by field type rather than sweeping one rule across all of them. Give the shared loader two helpers - one that tests presence and coerces (typed fields), one that tests presence and non-emptiness (prose fields) - and route each existing guard to whichever its field is. Then add the boundary: a check that refuses a new `\.get\([^)]*\) or ""` on a fields-file consumer, so the module list stops being a lower bound. Without that check this unit fixes five modules and exempts the sixth nobody has written yet.

## Acceptance Criteria

- [ ] **AC1** Given a TYPED field carrying a JSON `false` or `0` in each of the five named modules' fields-file loaders, when the document is read, then the value is ACCEPTED and reaches the record - one criterion per module would be five near-identical rows, so this is asserted over the named set with the module named in each failure
- [ ] **AC2** Given a PROSE field carrying `false`, an empty string or a null, when the document is read, then it is REFUSED naming that field - the paired control, and the reason this is not one blanket rule: storing the string `False` as a rationale is worse than the bug being fixed
- [ ] **AC3** Given a NEW `or ""` guard added to a fields-file consumer, when the repository's own check runs, then it REFUSES - the enumeration in this bug is a lower bound and the check is what makes it a boundary, per LL0043
- [ ] **AC4** Given each of the five modules' shipped COMMANDS rather than their loaders, when a typed field carries `false`, then the command exits 0 - the symptom is a CLI refusal, and a library test cannot see a command that stops calling the loader

## Impact

Every one of these loaders is on the recommended `--fields-file` path, which exists precisely so prose carrying shell metacharacters is stored verbatim. An operator who takes the recommended path and writes a boolean gets an error naming a field their file contains, and the workaround - write the string - is documented nowhere. On a verdict field the bias has a direction: the positive value records and the negative one refuses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Filed |
