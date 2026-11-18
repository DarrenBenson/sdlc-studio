# BG1580: The v6.1 docs test refuses a spec naming a .local file only a git hook reads, so BG1518's TSD row reddened the push

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_lean_docs_v61.py
> **Evidence:** Push gate on devserver1, 2026-11-18, log boundary-suite-last.log line 286.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T03:04:33Z

## Summary

`Docs61Tests.test_the_specs_describe_the_shipped_code` (tools/tests/`test_lean_docs_v61.py)` requires each `.local/<file>` a spec names to be read or written by a shipped or tools/ script. BG1518 (run sixteen) documented `.local/push-ack.json` in tsd.md; .githooks/pre-push reads and writes it, but the test does not scan .githooks, so the push boundary refused commit 3777e27e.

## Steps to Reproduce

python3 -m pytest tools/tests/`test_lean_docs_v61.py`::Docs61Tests::`test_the_specs_describe_the_shipped_code` at 3777e27e.

## Proposed Fix

Count the tracked hooks under .githooks as readers.

## Acceptance Criteria

- [ ] **AC1** Given tsd.md naming `.local/push-ack.json`, which .githooks/pre-push reads and writes, when the docs test checks that each `.local` file a spec names has a reader, then the tracked hooks count as readers and the test passes. Fails on: .githooks left out of the readers.
  - **Verify:** pytest tools/tests/test_lean_docs_v61.py::Docs61Tests::test_the_specs_describe_the_shipped_code
- [ ] **AC2** Given a spec naming a `.local` file that no script, tools/ file or hook reads, when the same check runs, then it still fails naming the file. Fails on: the widened readers accepting any name.
  - **Verify:** pytest tools/tests/test_lean_docs_v61.py -k unread_local

## Impact

A spec cannot name a file the hooks own without reddening the push.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
