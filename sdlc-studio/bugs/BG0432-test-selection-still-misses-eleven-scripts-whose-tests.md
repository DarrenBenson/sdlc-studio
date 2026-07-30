# BG0432: test selection still misses eleven scripts whose tests load them under a different name

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Executed by an independent reviewer, with the full eleven-entry list enumerated from both test trees.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

The naming route added for the earlier defect matches a script's OWN convention-named test (`x.py` -> `test_x.py`) and nothing else, while that defect's summary states the broader class: no route reaches a script loaded through `spec_from_file_location`. Cross-named loaders are still missed. Enumerating every `_load(...)` in both test trees against `select_tests` gives eleven: status.py<-`test_flow`, conformance/readiness/reconcile/`repo_map`<-`test_sdlc_md`, artifact/`file_finding`<-`test_retitle_refs`, critic<-`test_repair_plan`, `command_audit`<-`test_help_structure`, retro/telemetry<-tools/`test_evidence_in_git.` Verified concretely: a change to status.py yields a resolved 88-suite selection that excludes `test_flow.py`, which loads status.py by path and asserts on `ageing_advisory`.

## Steps to Reproduce

1. `gate.select_tests('.', ['.claude/skills/sdlc-studio/scripts/status.py'])`.
2. `resolved True`, 88 selectors, `test_status` selected, `test_flow` NOT selected.
3. `test_flow.py` loads status.py and asserts on `ageing_advisory`, so a commit breaking it runs a green selection that excludes its only test.

## Proposed Fix

Derive the reverse index from the loader calls the test modules actually make (`_load("x")` / `spec_from_file_location("x", ...)`) rather than from the filename convention, and select every test module that loads the changed script.

## Acceptance Criteria

- [ ] The behaviour described is corrected: The naming route added for the earlier defect matches a script's OWN convention-named test (`x.py` -> `test_x.py`) and nothing else, while that defect's...
- [ ] The proposed fix lands, pinned by a test: Derive the reverse index from the loader calls the test modules actually make (`_load("x")` / `spec_from_file_location("x", ...)`) rather than from the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
