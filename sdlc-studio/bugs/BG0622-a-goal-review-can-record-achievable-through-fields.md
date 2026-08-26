# BG0622: a goal review can record ACHIEVABLE through --fields-file but not NOT-ACHIEVABLE, because a JSON false is read as a missing field

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Encountered 2026-08-26 recording the goal review for the zero-open-High run. Guard quoted from sprint.py:10150-10155 per D0151. Asymmetry confirmed by running both encodings.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_seat_from_dict` (sprint.py:10150-10155) validates each seat field with `val = str(d.get(f) or "").strip()` and refuses when the result is empty. A JSON boolean `false` collapses through the `or` to the empty string, so `"achievable": false` is reported as `seat 'qa' in --fields-file is missing 'achievable'`, while `"achievable": true` passes as the string `True`. The refusal is asymmetric: the recommended path can record that a goal IS achievable and cannot record, in the same encoding, that it is NOT. Hit on 2026-08-26 recording a genuine NOT-ACHIEVABLE verdict from a pre-code goal review. The workaround is to write the value as the string `no`, which nothing in the help or the error message says.

## Steps to Reproduce

1. Write a --fields-file whose seat carries `"achievable": false` as a JSON boolean. 2. `sprint.py goal-review record --fields-file <file>`. 3. It refuses with `missing 'achievable'`. 4. Change the value to `true` and it is accepted. The field is present in both cases and the message is false in the first.

## Proposed Fix

Test for PRESENCE, not truthiness - `if f not in d` - and then coerce. A boolean is the natural JSON encoding of a yes-or-no field, and both of its values must reach the record. The same `or ""` shape should be swept for across the other fields-file loaders, since any of them reading a boolean or a zero has the identical hole: `str(0 or "")` is also empty.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_seat_from_dict` (sprint.py:10150-10155) validates each seat field with `val = str(d.get(f) or "").strip()` and refuses when the result is empty.
- [ ] **AC2** The proposed fix lands, pinned by a test: Test for PRESENCE, not truthiness - `if f not in d` - and then coerce.

## Impact

The whole point of a pre-code goal review is that it can say NO - it is what makes a negative result possible, which is LL0036 in the registry. A recorder that accepts the positive verdict and refuses the negative one, through the path its own help calls recommended, biases the record toward approval and does it silently enough that an author under time pressure will flip the value rather than investigate. Found while recording a verdict that a run should not proceed as worded.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
