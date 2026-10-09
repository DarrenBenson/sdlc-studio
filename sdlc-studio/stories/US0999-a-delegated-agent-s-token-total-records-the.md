# US0999: A delegated agent's token total records the model that spent it

> **Status:** Draft
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_delegated_tokens_model.py, changelog.d/US0999.md
> **Epic:** EP0276
> **Points:** 2
> **Depends on:** US0997
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose sprints spend most of their tokens in delegated agents
**I want** each delegated agent's reported total to record the model it ran on, as the agent reports it
**So that** the delegated spend, which is most of what I pay for, can be priced on the report instead of reading unpriced

## Acceptance Criteria

- **AC1:** Given an open run, when a builder's total is returned with `sprint lane return --units <unit> --tokens 120000 --model claude-sonnet-4-6` and another is recorded with `retro.py accuracy --delegated-tokens 80000 --delegated-model claude-opus-5-5`, then each delegated entry on the run record carries the model it was given and each command prints it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_tokens_model.py::DelegatedModelTests::test_both_recorders_store_the_model
- **AC2:** Given a delegated total returned with no `--model`, when the entry is recorded, then it carries no model and nothing is filled in for it, and a page filed for that run reads exactly as it would before this change.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_tokens_model.py::DelegatedModelTests::test_a_missing_model_is_never_guessed

## Notes

- Release: 6.2 (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the new flag parsed but never passed to run_state.record_delegated_tokens, so the entry carries no model
- AC2 must fail on: defaulting a missing model to the main thread's model, which would price a smaller model's subagent at the session's larger model's rate
- Serves Maya's scenario, 'priced from her own rates' (maya-okafor-founder-engineer.md:62-63), and makes the money story's headline mostly priced rather than mostly unpriced.
- Delegated entries carry no model today (run_state.py:1700). Two recorders write them: `sprint lane return --tokens` (sprint.py:8191) and `retro.py accuracy --delegated-tokens` (retro.py:3140).
- Evidence for the scope (panel, product): RPT0006-RPT0011 have a `mixed` main thread and the rest delegated, so nothing would be priced; RPT0016-RPT0019 are 81 to 88% delegated (RPT0019: 456,035 of 558,755 tokens).
- Recording only: the report changes in the money story, so earlier pages are untouched here. Shares run_state.py and retro.py with US0991; no behavioural overlap found.
- Conditional on the operator taking money scope (a); with (b) this story is deferred with the money story.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
