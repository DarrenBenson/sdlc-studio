# BG0334: EP0163 init-stage AC verifiers under-assert their own ACs (US0442, US0438), and stage_agents silently skips a missing te

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

Two dedicated verifiers on Done stories cannot fail on the behaviour their AC states: US0442's test asserts only the bare substrings 'epic' (satisfied by prose) and 'sprint plan', never the story command; US0438's test asserts AGENTS.md only, never the CLAUDE.md import its AC claims. The US0438 gap is live because `stage_agents` skips a missing template with 'if not st.exists(): continue', reporting it in neither created nor skipped.

## Steps to Reproduce

Evidence (`test_decompose_and_plan_stages_direct` (lines 453-458), `test_agents_stage_drafts_the_instructions` (lines 334-343); init.py `stage_agents` lines 255-273): `test_init.py` 456-458 assert only 'epic'/'sprint plan' substrings while init.py line 338 prose contains 'epics' before the backticked commands, so removing both commands stays green; `test_init.py` 334-343 has no CLAUDE.md assertion; init.py `stage_agents` silently continues past a missing template file.

## Proposed Fix

Strengthen both tests to assert the exact backticked commands (`epic generate`, `story generate`, `sprint plan`) and the CLAUDE.md import file/content respectively, and change `stage_agents` to report a missing template loudly (list it in skipped or fail) rather than continue silently.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
