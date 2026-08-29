# BG0622: a goal review can record ACHIEVABLE through --fields-file but not NOT-ACHIEVABLE, because a JSON false is read as a missing field

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Encountered 2026-08-26 recording the goal review for the zero-open-High run. Guard quoted from sprint.py:10150-10155 per D0151. Asymmetry confirmed by running both encodings.
> **Verification depth:** functional [[derived: criteria 3; plan rows 3; executed 3; killed 3; survived 0; not-run 0; entry point 1 of 3 criteria through the shipped CLI, 2 in-process | fp e4b9a44a7ced ]] (three criteria, each mutant applied to the real file with bytecode purged and the tree restored. One drives `sprint.py goal-review record --fields-file` as the shipped command, and its polarity clause is the load-bearing half: unwiring the helper leaves the CLI exiting 0 while it stores a raw false that reads unclear. All five values were also exercised end to end before the tests were written - false, true, no, empty and null.)
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_seat_from_dict` (sprint.py:10150-10155) validates each seat field with `val = str(d.get(f) or "").strip()` and refuses when the result is empty. A JSON boolean `false` collapses through the `or` to the empty string, so `"achievable": false` is reported as `seat 'qa' in --fields-file is missing 'achievable'`, while `"achievable": true` passes as the string `True`. The refusal is asymmetric: the recommended path can record that a goal IS achievable and cannot record, in the same encoding, that it is NOT. Hit on 2026-08-26 recording a genuine NOT-ACHIEVABLE verdict from a pre-code goal review. The workaround is to write the value as the string `no`, which nothing in the help or the error message says.

## Steps to Reproduce

1. Write a --fields-file whose seat carries `"achievable": false` as a JSON boolean. 2. `sprint.py goal-review record --fields-file <file>`. 3. It refuses with `missing 'achievable'`. 4. Change the value to `true` and it is accepted. The field is present in both cases and the message is false in the first.

## Proposed Fix

Test for PRESENCE, not truthiness - `if f not in d` - and then coerce. A boolean is the natural JSON encoding of a yes-or-no field, and both of its values must reach the record. Coerce, then test the COERCED value for non-emptiness - not for truthiness and not for presence alone. Presence alone is worse than the bug: `if f not in d` admits an empty string, a null and a zero, and `verdict_polarity` reads all three as `unclear`, so the guard whose job is to refuse an incomplete verdict would start passing three of them.

The identical `or ""` shape sits on 11 other fields-file consumers across `ledger.py`, `decisions.py`, `handoff.py`, `validate.py` and `file_finding.py` - roughly 20 guards. That sweep is NOT this unit: it is out of this unit's declared `Affects`, so it would land unreviewed and outside the revert-check lane, and it needs a different rule for prose fields, where accepting a falsey value would store the string `False` as a rationale. It is filed separately as BG0627.

## Acceptance Criteria

- [x] **AC1** Given a `--fields-file` seat verdict carrying `achievable: false` as a JSON boolean, when the goal review is recorded, then it is ACCEPTED - a recorder that takes the positive verdict and refuses the negative one biases the record toward approval
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FieldsFilePresenceTests::test_a_false_boolean_is_recorded_not_refused
  - **Verified:** yes (2026-08-27)
- [x] **AC2** Given a seat verdict whose field is PRESENT but carries no verdict - an empty string, or a JSON null - when it is read, then it is REFUSED naming that field, while `false` and the string `no` are both ACCEPTED and both read as polarity `no`. Presence alone is the over-correction the Proposed Fix invites: `if f not in d` still refuses a missing key, so a control asserting that would survive it, while empty, null and zero all become admissible and `verdict_polarity` reads each as `unclear` - an incomplete verdict let through the guard whose whole job is to refuse one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FieldsFilePresenceTests::test_a_present_but_verdictless_field_is_still_refused
  - **Verified:** yes (2026-08-27)
- [x] **AC3** Given a `--fields-file` carrying `achievable: false`, when `sprint.py goal-review record --fields-file` is run as the SHIPPED COMMAND, then it exits 0 and the stored round carries a seat whose `verdict_polarity` reads `no`. The symptom is a CLI exit 2, and `_seat_from_dict` is reached only through `load_fields_file(..., allowed=("goal", "seats", "brief"))` - an in-process test of the helper passes even if that path stops calling it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FieldsFilePresenceTests::test_the_shipped_command_records_a_false_boolean
  - **Verified:** yes (2026-08-27)

## Impact

The whole point of a pre-code goal review is that it can say NO - it is what makes a negative result possible, which is LL0036 in the registry. A recorder that accepts the positive verdict and refuses the negative one, through the path its own help calls recommended, biases the record toward approval and does it silently enough that an author under time pressure will flip the value rather than investigate. Found while recording a verdict that a run should not proceed as worded.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, rewrite `_seat_from_dict`'s guard as `if not d.get(f):` - a presence-SHAPED name over the same truthiness test. It still refuses `false`, and it survives a diff read, which is why a bare revert is not enough | Given a `--fields-file` seat verdict carrying `achievable: false` as a JSON boolean, when the goal review is recorded, then it is ACCEPTED - a recorder that takes the positive verdict and refuses the negative one biases the record toward approval |
| AC2 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, change `_seat_from_dict` to test `if f not in d`, dropping the emptiness check | Given a seat verdict whose field is PRESENT but carries no verdict - an empty string, or a JSON null - when it is read, then it is REFUSED naming that field, while `false` and the string `no` are both ACCEPTED and both read as polarity `no`. Presence alone is the over-correction the Proposed Fix invites: `if f not in d` still refuses a missing key, so a control asserting that would survive it, while empty, null and zero all become admissible and `verdict_polarity` reads each as `unclear` - an incomplete verdict let through the guard whose whole job is to refuse one |
| AC3 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, remove `_seat_from_dict` from `cmd_goal_review`'s fields-file path so the seats are stored unvalidated - the wiring a library test cannot see | Given a `--fields-file` carrying `achievable: false`, when `sprint.py goal-review record --fields-file` is run as the SHIPPED COMMAND, then it exits 0 and the stored round carries a seat whose `verdict_polarity` reads `no`. The symptom is a CLI exit 2, and `_seat_from_dict` is reached only through `load_fields_file(..., allowed=("goal", "seats", "brief"))` - an in-process test of the helper passes even if that path stops calling it |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
