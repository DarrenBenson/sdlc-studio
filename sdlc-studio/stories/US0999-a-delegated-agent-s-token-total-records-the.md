# US0999: A delegated agent's token total records the model that spent it

> **Status:** Draft
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_delegated_tokens_model.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_totals_said.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, changelog.d/US0999.md
> **Epic:** EP0276
> **Points:** 2
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

- Release: 6.4, run ten (D0461); was 6.3 (D0388) (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the new flag parsed but never passed to run_state.record_delegated_tokens, so the entry carries no model; or `lane accept` not handing it to the return it ends with
- AC2 must fail on: defaulting a missing model to the main thread's model, which would price a smaller model's subagent at the session's larger model's rate
- Serves Maya's scenario, 'priced from her own rates' (maya-okafor-founder-engineer.md:65-66).
- Checked at HEAD 508e2408 (2026-11-12): neither criterion is met, and the premise has narrowed. A SUPPLIED total carries no model (`record_delegated_tokens`, lib/run_state.py:2561, entry at :2610). A total read from the agent's own transcript (`lane return --agent`) or from a `lane run` session (`_lane_run_totals`, sprint.py:8644) already lands with its per-model split (lib/run_state.py:2616-2625, since US1123 and BG1252), and `unit_agent_totals` prices those per model (:2522-2534).
- The recorders this story changes: `_lane_agent_totals` (sprint.py:8558, record call at :8599-8606, printed at :9243-9249) and `retro.py accuracy` (`cmd_accuracy`, retro.py:3551, record call at :3564-3567, printed at :3576-3579, flags at :4178-4196). `lane accept` hands `--agent`, `--tokens` and `--minutes` to the return it ends with (sprint.py:9099-9101), so `--model` joins that list.
- `sprint lane` already parses `--model` (sprint.py:12772, help "(run)") for `lane run`; `lane return --model X` is accepted today and silently dropped. Reuse that flag for `return` and `accept` and update its help, rather than adding a second one.
- What it buys: the model names a supplied total; it does not price it. `prices.cost` prices five components (lib/prices.py:358), and a supplied total is one number, so the report still cannot put a dollar figure on it. The Dollar cost on RPT0028 already covers 100% of the priced tokens, because the Claude meter reads every subagent transcript.
- Evidence for the original scope (panel, product): RPT0006-RPT0011 have a `mixed` main thread and the rest delegated; RPT0016-RPT0019 are 81 to 88% delegated (RPT0019: 456,035 of 558,755 tokens). Those pages predate the per-model meter and the dollar rows.
- Recording only: earlier pages are untouched. US0991 is Done.
- Overlaps BG1330 (run eleven), which makes `lane land` record the builder's transcript-read return so every unit is priced; both change how a builder's spend reaches `_lane_agent_totals`. Not absorbed.
- The depends-on US0997 was dropped on 2026-11-12: this story touches no report code and cites nothing. It shares sprint.py, lib/run_state.py and help/sprint.md with US0998, so the two land one after the other.
- Conditional on the operator taking money scope (a). D0461 takes EP0276 whole at 15 points, this story included, but CR0610's consult question has no recorded answer.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Notes make it conditional on the operator taking CR0610's money scope (a); CR0610's Amigo Consult still lists that question as 'Settle before building' with no recorded answer (D0356 took the 6.2 set wholesale without naming it). Confirm before planning.
- Release note stale: the story says 'Release: 6.2' but D0382 (2026-10-20, supersedes D0381) sets the path to the 6.2.0 tag as run three plus run four's doc refreshes only, so this lands after 6.2.0; re-tag when a run takes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: line references corrected; notes record that transcript-read and lane-run totals already carry their model, that `lane --model` exists and is dropped by `return`, and that a supplied total stays unpriced with its model; Affects gains test_run_state.py, test_retro.py, test_lean_lane_delegated_tokens.py, test_lean_lane_totals_said.py and test_lane_accept.py; Depends on US0997 removed (no shared surface); release set to 6.4 (D0461); criteria unchanged |
