# US1149: The sprint entry names the projected re-read cost when the orchestrating session holds more than 80k tokens, under sprint.fresh_session warn or block, and the cost anatomy flags a run whose orchestrator averages over 150k a call

> **Status:** Ready
> **Delivers:** CR0670
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/US1149.md
> **Epic:** EP0302
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** the sprint entry to say what carrying a large session into a wave will cost before the wave starts, and the cost anatomy to flag a run whose orchestrator averaged over 150k tokens a call
**So that** each wave starts from a small context, a run that did not is visible at its close, and I can hold each team's cost per point to its budget

## Acceptance Criteria

- **AC1:** Given an open fixture run, a resume brief written by `sprint.py handoff`, `sprint.fresh_session` unset, and a session transcript in the directory `SDLC_STUDIO_TRANSCRIPTS` names whose newest call's context (its input + cache write + cache read, as the cost anatomy counts a context) is 120,000 tokens, when `sprint.py resume` runs, and when `sprint.py plan --write` opens a run over the same transcript, then each prints one warning on stderr naming the session's context (120,000 tokens), the 80,000-token threshold, the projected re-read cost (that context priced as a cache read under `TOKEN_WEIGHTS`: 12,000 input-equivalent tokens a call and 1,200,000 over the next 100 calls, about one wave, since run six's orchestrator made 323 calls over three) and the remedy (`sprint.py handoff`, then `sprint.py resume` in a fresh session), and each does the rest of its work and exits as it does without the check. At a context of exactly 80,000 tokens neither prints the warning; at 80,001 both do. Fails on: a warning at 80,000 or below; none above it; a projection other than the context x 0.1 a call and x 100 over 100 calls; the warning on stdout, where it would break `plan --format json` and move the next-step line `plan --write` ends on.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::FreshSessionTests::test_warn_names_the_projected_re_read_above_80k_and_nothing_at_or_under_it
- **AC2:** Given the same fixture with `sprint.fresh_session: block`, when `sprint.py resume` runs over a session whose newest call's context is above 80,000 tokens, then it exits 2 with nothing on stdout, naming on stderr the session's context, the threshold and the remedy (start a fresh session and run `sprint.py resume` there); at 80,000 or below it resumes as under `warn`. `sprint.py plan --write` under `block` warns as under `warn` and still opens the run, because `sprint.py handoff` cannot write a brief without an open run. Under `off` neither entry reads the session or prints a line about it, and any other value reads as `warn`. Fails on: `block` resuming above the threshold, or refusing at or below it; `plan --write` refused under `block`, leaving no run to hand off; a line under `off`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::FreshSessionTests::test_block_refuses_resume_above_80k_and_plan_write_still_opens_the_run
- **AC3:** Given no transcript in the meter's directory, a transcript whose newest usage record gives no per-call context, or a harness other than Claude Code chosen by the token meter (`SDLC_STUDIO_HARNESS=cursor`), when either entry runs, then under `warn` it prints nothing about the session, and under `block` it prints one stderr line saying the session's size is not available, with the reason, and goes on without refusing. Fails on: an unreadable size read as 0, or as under the threshold without saying so under `block`; a refusal for a size that could not be read; any line under `warn`, which would land in every fixture plan that names no transcript.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::FreshSessionTests::test_an_unreadable_session_size_is_named_under_block_and_never_refuses
- **AC4:** Given a fixture run whose main-thread (orchestrator) calls in the run's window average more than 150,000 tokens of context a call, when `sprint.py cost --anatomy` runs, then after the role table it prints a line flagging the orchestrator's average context against the 150,000-token threshold and naming the remedy (hand off at each wave boundary with `sprint.py handoff` and `sprint.py resume`), and `--format json` carries the same as `orchestrator_context_budget` and `orchestrator_over_context_budget`. At an average of exactly 150,000 or below it says the orchestrator stayed within 150,000; with no per-call record it reads not available. Fails on: an average of exactly 150,000 flagged; one above it not flagged; a missing average read as 0 or as within the threshold.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_an_orchestrator_averaging_over_150k_a_call_is_flagged
- **AC5:** Given the shipped configuration and docs, then `templates/config-defaults.yaml` declares `fresh_session: warn` under `sprint:` beside `affects_check`, with a comment naming `warn`, `block` and `off`; help/sprint.md's section on handing off and resuming names the 80,000-token check, what each of `warn`, `block` and `off` does, and that `plan --write` never refuses on it; and the cost anatomy paragraphs in help/sprint.md and reference-sprint.md name the 150,000-token orchestrator flag. Fails on: the key read by `sprint.py` but not declared in the defaults; a mode the docs name that the code does not honour, or one it honours that they omit; the orchestrator flag undocumented.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::HelpTests::test_the_fresh_session_check_and_the_orchestrator_flag_are_declared_and_documented

## Summary

CR0670's AC4 and AC5, deferred from run nine's first slice (D0435): the fresh-session warning at the sprint entry, and the cost anatomy's flag on a run whose orchestrator averaged over 150k tokens a call. CR0670's before-and-after figure (the orchestrator's average context per call against run six's 407k) is a measurement of the run that follows, read off that run's `sprint cost --anatomy` at its close, not a criterion here. Delivers: CR0670.

## Planning notes

- Evidence for the threshold, 2026-11-10: a consuming project delivering with Grok 4.7 through Cursor ran a whole sprint in one agent, and requests over 200k tokens made up about 58% of its bill. A fresh agent every five or so units, from one short handoff file, with one blocking CI watch in place of polling (CR0697), brought it to about $2.58 a unit by its first estimate (the measured figures are in the next note). Groom the warning's threshold and its default against this, and against the 200k price step some models charge above (xAI's long-context rate; BG1331).
- A consuming project's measured cost, delivering with Grok 4.7 through Cursor and priced at xAI's API rates (double for a prompt of 200k tokens or more), from its usage exports of 6 to 10 November 2026 (supplied by the operator, 2026-11-10). One agent running the whole sprint: $282.09 over 2,181 requests for 79 points ($3.57 a point). Prompts of 200k tokens or more were 29% of its requests and 57% of its cost, and $157.11 (56%) could not be tied to any unit, because the export stamped whole runs with one time until 9 November. A fresh agent per batch: batch A cost $25.72 for 8 points ($3.22 a point; 32% of the cost in long prompts). Batch B cost $23.08 for 5 points ($4.62 a point) counting the run that prepared its units, or $12.98 ($2.60 a point) for its delivery run alone, where long prompts were still 72% of the cost. Coordinator usage ($82.54 across all batches) is outside these figures, and batch C waits on an export past 11:41 GMT on 2026-11-10. The samples are small (8 and 5 points).

The data is in `sdlc-studio/change-requests/evidence/consumer-sprint-cost-2026-11-10.tar.gz`: per-request and per-unit CSVs, batch summaries, and the time windows and script that built them (the script imports a pricing module the bundle does not include). It is a scrubbed copy of the bundle supplied (SHA-256 fc960de33f14a39f; the copy 1d814234b30c426f): the project's repository name, two other project names, the operator's name and two local paths were replaced, and every figure is unchanged.

## Grooming notes (run ten)

Checked at HEAD 508e2408.

- **The 80,000 threshold and the `warn` default stay.** The evidence above shows the cost lives in prompts of 200k tokens or more, and that even a fresh agent's session grows into them (batch B's delivery run, 72%). A wave that starts under 80,000 has room to grow before the 200k step. A higher threshold would let a session start most of the way there. `block` stays opt-in, so a consuming project is not refused by default. Pricing above 200k is BG1331's, not this unit's.
- **The check sits at two entries.** `sprint.py resume` (`sprint.py:12320`) starts every wave and the close, so it is the one entry that refuses. `sprint.py plan --write` only warns: its next-step line (`PLAN_NEXT_STEP`, `sprint.py:12277`, printed at `:10971`) already sends the build to a fresh session, and it cannot refuse, because a run must be open before `sprint.py handoff` can write a brief.
- **The session's size is the cost anatomy's per-call context.** The size is the newest call's context in the transcript the meter reads, taken from the cost anatomy's per-call contexts (`lib/cost_anatomy.py:267-288` and `anatomy()` at `:414`) through `run_state._newest_transcript` and `_harness_transcript_dir`. The anatomy flag sits beside the subagent start check (`start_budget` at `:292`, `render` at `:451`) and reads the orchestrator row's `avg_context`. `lib/run_state.py` leaves Affects, because nothing in it changes.
- **The mode follows `sprint.affects_check`.** It is read the way `affects_check_mode` reads that key (`sprint.py:4015-4021`). Like that key, it is stated in help/sprint.md and declared in config-defaults.yaml rather than in reference-config.md.
- **The 100-call projection is a constant.** It is about one wave (run six: 323 orchestrator calls over three waves, CR0670), not a forecast of this run's calls.
- **Every message goes to stderr.** That leaves unchanged the stdout that existing tests read from `plan --write` and `resume`, and the JSON from `plan --format json`. Under the default `warn`, a fixture whose session size cannot be read prints nothing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-10 | Darren Benson (operator) | Planning note: a consuming project's cost evidence for the session budget |
| 2026-11-10 | Darren Benson (operator) | Evidence: a consuming project's batch cost figures |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: user story and five criteria with Verify selectors authored (the warning and its projection, block at resume only, an unreadable size, the anatomy's 150k orchestrator flag, the key and docs); Affects gains lib/cost_anatomy.py, test_cost_anatomy.py, config-defaults.yaml, help/sprint.md and reference-sprint.md and drops lib/run_state.py; Depends on US1141; Points stay 5 |
