# BG0334: EP0163 init-stage AC verifiers under-assert their own ACs (US0442, US0438), and stage_agents silently skips a missing te

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_init.py, .claude/skills/sdlc-studio/scripts/init.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

Two dedicated verifiers on Done stories cannot fail on the behaviour their AC states: US0442's test asserts only the bare substrings 'epic' (satisfied by prose) and 'sprint plan', never the story command; US0438's test asserts AGENTS.md only, never the CLAUDE.md import its AC claims. The US0438 gap is live because `stage_agents` skips a missing template with 'if not st.exists(): continue', reporting it in neither created nor skipped.

## Steps to Reproduce

Evidence (`test_decompose_and_plan_stages_direct` (lines 453-458), `test_agents_stage_drafts_the_instructions` (lines 334-343); init.py `stage_agents` lines 255-273): `test_init.py` 456-458 assert only 'epic'/'sprint plan' substrings while init.py line 338 prose contains 'epics' before the backticked commands, so removing both commands stays green; `test_init.py` 334-343 has no CLAUDE.md assertion; init.py `stage_agents` silently continues past a missing template file.

## Proposed Fix

Strengthen both tests to assert the exact backticked commands (`epic generate`, `story generate`, `sprint plan`) and the CLAUDE.md import file/content respectively, and change `stage_agents` to report a missing template loudly (list it in skipped or fail) rather than continue silently.

## Acceptance Criteria

### AC1: US0442's verifier asserts the commands, not prose that happens to contain them

- **Given** the decompose and plan directives
- **When** the verifier runs
- **Then** it asserts the backticked `epic`, `story` and `sprint plan` as the directives mark them up
  - stripping both commands out of the decompose directive turns it red, where the bare substring
  'epic' was satisfied by the word 'epics' in the surrounding prose
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_decompose_and_plan_stages_direct

### AC2: US0438's verifier asserts the CLAUDE.md import its AC claims

- **Given** the agents stage run against an empty repo
- **When** the verifier runs
- **Then** it asserts CLAUDE.md in `created`, on disk, and beginning with the `@AGENTS.md` import, so
  dropping that starter reddens it instead of leaving Claude Code with no instructions at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_agents_stage_drafts_the_instructions

### AC3: a missing starter template is refused, never skipped in silence

- **Given** an installed skill whose `templates/agent-instructions.CLAUDE.md` is absent
- **When** the agents stage runs
- **Then** it raises naming the missing starter, writes nothing at all, and the guided runner does not
  swallow it - the stage stays the first incomplete one rather than a silent no-op the operator confirms
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_a_missing_starter_template_is_refused_not_skipped_in_silence

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
| 2026-07-28 | delivery lane (RUN-01KYJZGZ) | Acceptance criteria authored; verifiers strengthened, missing starter now refused |
