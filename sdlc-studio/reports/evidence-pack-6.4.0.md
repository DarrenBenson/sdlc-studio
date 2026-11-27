# Evidence pack: release 6.4.0

Built by `release_cut.py evidence-pack` from the records committed at `f5ac4de15dd4`, over the signed reports RPT0028, RPT0029, RPT0030, RPT0031, RPT0032, RPT0033, RPT0034. Uncommitted edits and the tool's local state are not read.

Passed criteria are each unit's ticked criteria and their Verify lines, as its committed file holds them. A verify run is recorded only in local state, which is not a committed record, so this pack does not read one.

An independent review is the latest verdict of each reviewing seat whose reviewer is not the unit's recorded author, never a self-review or a unit closed before the review gate.

## Changes

### BG1205: US0986 did not converge in review: round 2 REJECT findings

- What changed: US0986 did not converge in review: round 2 REJECT findings (5 points).
- Criteria passed:
  - AC7: US0986 AC1 still passes: Given a fixture Claude transcript and either `SDLC_STUDIO_HARNESS=claude` or no selection with only Claude signalled, when the meter is read, then the reading equals today's `session_tokens` figure for that transcript (input + output + cache creation, cache reads excluded, the main-thread basis), and a malformed usage record still refuses the read. Fails on: the dispatcher re-implementing the Claude sum and counting cache reads, or skipping the malformed record Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_claude_reading_is_unchanged`
  - AC8: US0986 AC2 still passes: Given `SDLC_STUDIO_HARNESS` set to cursor, copilot or opencode and a readable Claude transcript in the same fixture, when the meter is read, then only the chosen harness's reader is consulted, the Claude transcript is never opened, and a harness with no reader installed returns tokens None with a reason naming the harness, never zero. Fails on: falling back to the Claude transcript when the chosen reader returns nothing Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_a_chosen_harness_never_reads_another_store`
  - AC9: US0986 AC3 still passes: Given no `SDLC_STUDIO_HARNESS`, when exactly one harness is signalled by the environment (`CLAUDECODE`; `CURSOR_AGENT` or a Cursor run id; `COPILOT_HOME`; `OPENCODE` or `OPENCODE_DB`), then that harness is selected even when another harness's store sits on disk; when two are signalled, or none is and two stores are present, the reading is tokens None with a reason naming every candidate and no total is formed. Fails on: choosing by a fixed precedence order, a store on disk outranking an environment signal, or adding two readings Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_two_unselected_harnesses_name_the_candidates`
  - AC10: US0986 AC4 still passes: Given any reader's result, then the reading and every stamp `open_run` or `stamp_tokens` writes name the harness, carry cache reads as a separate figure outside `tokens` (D0346), and a run total never subtracts a reading of one harness from a reading of another. Fails on: stamps keyed by source alone with no harness recorded, or cache reads folded into the headline Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_readings_and_stamps_name_the_harness`
  - AC11: US0986 AC5 still passes: Given a fixture repository with an open run and `SDLC_STUDIO_HARNESS=opencode` where only a Claude transcript exists, when `retro.py accuracy --id <retro> --tokens-from-harness` runs, then no token figure is recorded and the output names opencode and the reason. Fails on: the library honouring the selection while the CLI path still reads the Claude transcript through the `harness_tokens` alias Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessLaneTests::test_accuracy_names_the_harness_it_could_not_read`
- Criteria not ticked: AC1, AC2, AC3, AC4, AC5, AC6.
- Independent review: qa-seat-BG1205-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### BG1264: US1133's trailer check skips a single-id subject though its docs say it does not, refuses this repository's paperwork-commit convention, and leaves two ownership rules unpinned

- What changed: US1133's trailer check skips a single-id subject though its docs say it does not, refuses this repository's paperwork-commit convention, and leaves two ownership rules unpinned (2 points).
- Criteria passed:
  - AC1: The hook and its prose agree on a single-id subject: in a fixture staging a file only US0001 owns, `fix(US0002): x` with body `Refs: US0002` lands, and the `tools/enable-hooks.sh` header and the `derive_trailers` docstring each say the `Refs:` contradiction refusal judges only a subject naming two or more ids. The positive control: the two-id subject `fix(US0001, US0002): x` with the same `Refs: US0002` is refused, naming US0002. Fails on: either text stating the refusal with no multi-id qualifier, or the two-id case landing. Verify: `pytest tools/tests/test_commit_msg_mentions.py::DerivedMentionsTests::test_a_single_id_refs_lands_and_a_multi_id_one_is_refused`
  - AC2: Following recorded step (2) no longer reproduces the defect: a two-id paperwork commit whose `Refs:` names the unit a staged `sdlc-studio/reviews/critic-verdicts.md` or `sdlc-studio/reviews/author-self-checks.md` records, or whose staged file is that unit's own artefact, lands at its first attempt through the real hook (the ledger read as owned by that unit, or the id written `Mentions:`), with no line to rewrite. The positive control: a `Refs:` naming a unit that owns none of a staged source file is still refused. Verify: `pytest tools/tests/test_commit_msg_mentions.py::DerivedMentionsTests::test_a_paperwork_commit_refs_lands_and_a_source_contradiction_is_refused`
  - AC3: Recorded steps (3) and (4) now turn a test red: a two-id commit staging only `changelog.d/US0001.md` with `Refs: US0001` lands, so removing `_path_owner(f) == rid` from `owns()` makes it refused; and a `Refs:` naming an id with no artefact in the workspace is not reported contradicted, so removing `i in fp` makes it contradicted. The positive control in each: a `Refs:` for a unit with an artefact that owns none of the staged files is contradicted. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CommitMsgCheckTests::test_a_file_named_for_its_unit_is_owned_by_that_unit .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CommitMsgCheckTests::test_a_refs_id_with_no_artefact_is_not_contradicted`
- Independent review: qa-seat-BG1264-r1 APPROVE (2026-11-09).
- Known issues:
  - BG1323 (Low): The commit-msg hook misses git's scissors line under a non-default `core.commentChar`, the multi-id rule still reads trailers below it, and `_ledger_rows` and BG1264's fragment say an edited ledger row owns nothing - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US0986: The token meter reads the running harness's store, chosen by SDLC_STUDIO_HARNESS or the environment, and never sums two

- What changed: The token meter reads the running harness's store, chosen by SDLC_STUDIO_HARNESS or the environment, and never sums two (5 points).
- Criteria passed:
  - AC1: Given a fixture Claude transcript and either `SDLC_STUDIO_HARNESS=claude` or no selection with only Claude signalled, when the meter is read, then the reading equals today's `session_tokens` figure for that transcript (input + output + cache creation, cache reads excluded, the main-thread basis), and a malformed usage record still refuses the read. Fails on: the dispatcher re-implementing the Claude sum and counting cache reads, or skipping the malformed record Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_claude_reading_is_unchanged`
  - AC2: Given `SDLC_STUDIO_HARNESS` set to cursor, copilot or opencode and a readable Claude transcript in the same fixture, when the meter is read, then only the chosen harness's reader is consulted, the Claude transcript is never opened, and a harness with no reader installed returns tokens None with a reason naming the harness, never zero. Fails on: falling back to the Claude transcript when the chosen reader returns nothing Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_a_chosen_harness_never_reads_another_store`
  - AC3: Given no `SDLC_STUDIO_HARNESS`, when exactly one harness is signalled by the environment (`CLAUDECODE`; `CURSOR_AGENT` or a Cursor run id; `COPILOT_HOME`; `OPENCODE` or `OPENCODE_DB`), then that harness is selected even when another harness's store sits on disk; when two are signalled, or none is and two stores are present, the reading is tokens None with a reason naming every candidate and no total is formed. Fails on: choosing by a fixed precedence order, a store on disk outranking an environment signal, or adding two readings Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_two_unselected_harnesses_name_the_candidates`
  - AC4: Given any reader's result, then the reading and every stamp `open_run` or `stamp_tokens` writes name the harness, carry cache reads as a separate figure outside `tokens` (D0346), and a run total never subtracts a reading of one harness from a reading of another. Fails on: stamps keyed by source alone with no harness recorded, or cache reads folded into the headline Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_readings_and_stamps_name_the_harness`
  - AC5: Given a fixture repository with an open run and `SDLC_STUDIO_HARNESS=opencode` where only a Claude transcript exists, when `retro.py accuracy --id <retro> --tokens-from-harness` runs, then no token figure is recorded and the output names opencode and the reason. Fails on: the library honouring the selection while the CLI path still reads the Claude transcript through the `harness_tokens` alias Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessLaneTests::test_accuracy_names_the_harness_it_could_not_read`
- Independent review: qa-seat-US0986-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1130: Trim the shipped agent-instructions template to 5,000 chars and name the start context a delivery session pays

- What changed: Trim the shipped agent-instructions template to 5,000 chars and name the start context a delivery session pays (3 points).
- Criteria passed:
  - AC1: Given `templates/agent-instructions.md`, then it is at most 5,000 chars (from 10,893), keeps its `## Operating doctrine` and `## Non-negotiable gates` sections with the gate list and commands, and points at `reference-doctrine.md` for the text it moves. Fails on: a size cap above 5,000, or a cut that drops a gate from the list. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_the_template_fits_and_keeps_its_gates`
  - AC2: Given the trimmed template, then the lines tests read survive: the `agent-instructions.md#operating-doctrine` anchor (`test_status.py`), the trunk-integration rule stated on one line with its commit clause, its `pr-required` opt-in and the words push `main` (`test_trunk_integration.py`), the CR-sizing claim (`test_lean_cr_filing.py`), and `test_init.py`, `test_validate.py`, `test_lean_guided_stage_confirm.py`, `test_lean_migrate_config.py` and `tools/tests/test_check_neutrality.py` pass unedited; a project initialised from it passes `validate`. Fails on: the trunk rule line or the doctrine heading cut. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_an_initialised_project_s_agents_md_still_validates`
  - AC3: Given `reference-sprint.md#cost-anatomy`, then it recommends a project `.claude/settings.json` that disables the plugins and connectors a delivery session does not use, and says claude.ai connectors may not be switchable per project. Fails on: the recommendation absent or stated as already enforced. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_instructions_budget.py::AgentInstructionsBudgetTests::test_reference_sprint_recommends_the_settings_file`
  - AC4: Given a session transcript whose first main-thread call carries a known input and cache, when `sprint.py cost --anatomy` renders, then its header names the main thread's start context as that first call's input plus cache. Fails on: the header omitting it, or reading the largest call's context instead of the first. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_the_main_thread_start_context_is_named`
- Independent review: qa-seat-US1130-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1133: Write the Refs and Mentions trailers the commit-msg hook now refuses for

- What changed: Write the Refs and Mentions trailers the commit-msg hook now refuses for (3 points).
- Criteria passed:
  - AC1: Given a subject naming two ids that each own a staged file by their Affects and no trailer, when the commit-msg hook runs, then it writes one `Refs: <id>` per owning id into the message and the commit lands at the first attempt (a replay of the BG1213 landing). Fails on: `message-refs` still refusing a message the staged-file map can attribute. Verify: `pytest tools/tests/test_commit_msg_hook.py::DerivedTrailerTests::test_owning_ids_get_refs_written_and_the_commit_lands`
  - AC2: Given a subject naming an id that owns none of the staged files, then the hook writes `Mentions: <id>` for it, never `Refs:`. Fails on: writing `Refs:` for every id the subject names. Verify: `pytest tools/tests/test_commit_msg_mentions.py::DerivedMentionsTests::test_a_non_owning_id_gets_mentions`
  - AC3: Given a message whose existing `Refs:` trailer names an id that owns none of the staged files, then `message-refs` refuses naming that id; a trailer that matches ownership passes unchanged and is never written twice. Fails on: the lane deleted outright, or a correct trailer duplicated. Verify: `pytest tools/tests/test_commit_msg_hook.py::DerivedTrailerTests::test_a_trailer_that_contradicts_ownership_is_refused`
  - AC4: Given a consuming project's commit message file, when `engagement_floor.py check-commit-msg --write-trailers <file>` runs, then it appends the derived trailers by the same rule, and `AGENTS.md`'s refusals table and `tools/enable-hooks.sh` describe the hook as writing them. Fails on: the derivation living only in this repository's hook. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CommitMsgCheckTests::test_write_trailers_appends_from_ownership`
- Independent review: qa-seat-US1133-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1140: The run's next action and a resume brief of at most 8k tokens are derived from disk alone

- What changed: The run's next action and a resume brief of at most 8k tokens are derived from disk alone (5 points).
- Criteria passed:
  - AC1: Given a fixture run in each of four states (a lane in flight; a landed unit with a QA brief and no APPROVE; every landed unit approved with a later wave unbriefed; every batch unit terminal), then `resume_brief.next_action(root)` returns one step per state by a fixed ladder in this order of precedence: await the in-flight lane, review the landed unit (or repair it after a REJECT), `sprint.py lane brief --units <that wave's unbriefed ids>`, then `sprint.py close` in its own fresh session. It reads only the tree and `sdlc-studio/.local/`, so two calls on one tree return the same step. Fails on: a state falling to a later rung while an earlier one holds, a step read from process state, or the close named while a batch unit is not terminal. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::NextActionTests::test_each_fixture_state_yields_its_rung_of_the_ladder`
  - AC2: Given an open run, then `resume_brief.at_wave_boundary(root)` is true only when every lane of the current wave is accepted and none is in flight, and otherwise false with the blocking unit named. Fails on: true with a lane in flight, or true with a landed unit still awaiting its verdict. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::NextActionTests::test_the_wave_boundary_holds_only_with_every_lane_accepted_and_none_in_flight`
  - AC3: Given an open run, then `resume_brief.build(root, agents=..., issues=...)` renders a markdown brief naming the run id and Sprint Goal, each batch unit's lane state (unbriefed, in flight, landed awaiting a verdict, accepted, or terminal), each in-flight lane's agent id where the caller supplied one, each pending QA brief by path and each pending verdict, the run's rulings from the run state's `rulings`, the known issues (the caller's, and each open bug or CR whose `Raised-in-batch` names the run), whether the run stands at a wave boundary, and the next action from AC1. Fails on: a batch unit absent from the brief, a pending QA brief or verdict not named, or an in-flight lane listed without the agent id the caller supplied. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::ResumeBriefTests::test_the_brief_names_every_unit_and_each_pending_item`
  - AC4: Given a brief whose estimate (characters divided by four, rounded up, the rule the module states) exceeds 8,000 tokens, then `build` raises an error naming the estimate and the budget instead of returning a truncated brief; given a 30-unit fixture batch with ten rulings, the brief fits the budget. Fails on: a silently truncated brief, an over-budget brief returned, or the 30-unit brief refused. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::ResumeBriefTests::test_an_over_budget_brief_is_refused_and_a_thirty_unit_brief_fits`
  - AC5: Given a built brief, then `resume_brief.parse(text)` returns the run id and next action it was built with, and a schema-3 unit spelt `US-01M6XQJF` in one place and `US01M6XQJF` in another is read as one unit under `sdlc_md.norm_id`. Fails on: a round trip that changes the next action, or the two spellings read as two units (the BG1302 shape). Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::ResumeBriefTests::test_the_brief_round_trips_and_a_schema3_id_is_one_unit`
- Independent review: qa-seat-US1140-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1141: The sprint hands off to a resume brief and resumes from it in a fresh session at the same next action

- What changed: The sprint hands off to a resume brief and resumes from it in a fresh session at the same next action (3 points).
- Criteria passed:
  - AC1: Given an open fixture run, then `sprint.py handoff [--agent <unit>=<agent-id> ...] [--issue "<text>" ...]` writes the brief to `sdlc-studio/.local/resume-brief.md` and prints its path, its estimated tokens against the 8,000 budget and the next action; with no open run, a brief over budget or an `--agent` value without `=`, it exits 2 naming why and writes nothing. It writes nothing under `sdlc-studio/handoffs/` and sets no `handoff` key in the run state. Fails on: a brief written with no open run or over budget, a malformed `--agent` accepted, or an HO file or `handoff` key written (the surface US0978 retired). Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::HandoffCliTests::test_handoff_writes_the_bounded_brief_and_refuses_without_a_run_or_over_budget`
  - AC2: Given a fixture run handed off with `sprint.py handoff`, then `sprint.py resume`, run as a separate process holding only the tree, prints the brief and the same next action the handoff recorded; given a tree that moved after the handoff (a lane landed), it prints the next action the tree now yields and names the brief's as stale; with no brief on disk, or a brief naming a run other than the open one, it exits 2. Fails on: a next action that differs from the handoff's on an unchanged tree, a stale action printed as current, or a resume over another run's brief. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::ResumeCliTests::test_resume_in_a_fresh_process_reaches_the_handoffs_next_action_and_names_drift`
  - AC3: Given a plannable fixture batch, then `sprint plan --write` ends its output by naming its next step as `sprint.py handoff`, then wave 1 started in a fresh session with `sprint.py resume`; a plan without `--write` prints no such line. Fails on: the line missing after `--write`, or printed by a preview that opened no run. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::PlanNextStepTests::test_plan_write_names_a_fresh_session_as_its_next_step`
  - AC4: Given the shipped docs, then help/sprint.md shows `sprint.py handoff` and `sprint.py resume` as fenced invocations the sprint parser accepts, and the generated command surface (`docgen.py surface`) lists both verbs. Fails on: either verb missing from either page, or a documented flag the parser does not own. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::HelpTests::test_help_and_the_command_surface_list_handoff_and_resume`
- Independent review: qa-seat-US1141-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1142: The sprint reference defines a wave boundary and runs the close in its own fresh session

- What changed: The sprint reference defines a wave boundary and runs the close in its own fresh session (2 points).
- Criteria passed:
  - AC1: Given the shipped reference-sprint.md, then a section anchored `{#wave-boundary}` defines a wave boundary as every lane of the wave accepted and none in flight, states that a hand-back reaches only the session that spawned its agent so no boundary falls with a lane in flight, and names `sprint.py handoff` at the boundary and `sprint.py resume` in the fresh session, each a verb the sprint parser owns. Fails on: the section absent, the definition missing either condition, or a named verb the parser does not own. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py::WaveBoundaryDocTests::test_the_reference_defines_the_boundary_and_names_parser_verbs`
  - AC2: Given the same reference, then it routes the close (retro, report, close and sign) through its own fresh session started from the resume brief, and the loop under `#the-loop` stays six steps. Fails on: the close left in the last wave's session, or a seventh loop step. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py::WaveBoundaryDocTests::test_the_close_runs_in_its_own_fresh_session_and_the_loop_stays_six_steps`
  - AC3: Given the reference's "The handoff and the run object" section and reference-sprint-toolchain.md, then the section tells the resume brief (run-local under `sdlc-studio/.local/`, read by `sprint.py resume`) apart from the retired handoff record the signed report replaced, and the runbook carries one row for `sprint.py handoff` and one for `sprint.py resume`. Fails on: the section still saying no command writes a handoff with no word on the resume brief, or either runbook row missing. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py::WaveBoundaryDocTests::test_the_resume_brief_is_told_apart_from_the_retired_handoff_and_the_runbook_names_both`
- Independent review: qa-seat-US1142-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1143: A run on an xAI Grok or Cursor Composer model reads a dollar cost from dated provider prices, not "not priced"

- What changed: A run on an xAI Grok or Cursor Composer model reads a dollar cost from dated provider prices, not "not priced" (2 points).
- Criteria passed:
  - AC1: Given the shipped `templates/model-prices.json`, then it prices each xAI Grok and each Cursor Composer model a supported harness's reading names, under the id that reading carries: the `--model` slug `sprint lane run --harness cursor` passes to `cursor-agent` and records as the reading's model (Cursor CLI prints none, so `harness_usage.parse` takes the caller's), and OpenCode's `<provider>/<model>` id (such as `xai/<model>`). Each entry carries input, `cache_read` (cached input) and output rates and both cache-write slots, a component the provider does not bill separately at the rate it bills it at, said in `note`; and each entry's `source` is the provider's own published pricing page (xAI's for Grok, Cursor's for Composer) naming the day it was read (`read YYYY-MM-DD`), no earlier than its `effective` date. The builder reads those pages; no rate is typed from memory or an aggregator. Fails on: no Grok or no Composer entry, an entry whose source is another provider's page or a reseller's, an undated read, or an id no harness's reading carries. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_every_grok_and_composer_price_names_its_provider_page_and_the_day_read`
  - AC2: Given, for each Grok and Composer entry, a captured reading of the harness that names it (`tests/fixtures/harness_usage/cursor.json` parsed by `harness_usage.parse` with the Cursor slug as `model`, `opencode.jsonl` with the OpenCode id), then `prices.cost` on that reading's components returns a US dollar figure equal to each component's tokens times the entry's rate per million, summed, with `unpriced` None, the expected figure typed in the test from the entry's rates. Fails on: the reading read as not priced, priced at another model's rate, or at $0. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_a_recorded_grok_and_composer_reading_is_priced_in_dollars`
  - AC3: Given a Grok id and a Composer id the table does not hold, each a listed id with a suffix (as `opencode/deepseek-v4.1-flash` stands beside the listed `-free` entry), then `prices.cost` returns `usd` None with `unpriced` naming the id, and `run_state.usd` lists it under `unpriced` with its share, never summed in at the listed sibling's rate or at $0; beside it, in the same test, the listed sibling is priced (the positive control). Fails on: prefix or nearest-name matching, or an unlisted id read as free. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_an_unlisted_grok_or_composer_id_is_not_priced_beside_a_listed_one`
  - AC4: Given `reference-config.md#pricing` and the table's `about` text, then each names xAI's and Cursor's own pricing pages among those a non-Claude model is listed from, and the id form each harness's reading carries for them (the Cursor `--model` slug, the OpenCode `<provider>/<model>` id). Fails on: either still naming only OpenAI and OpenCode as the non-Claude sources. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_the_configuration_reference_names_the_grok_and_composer_sources`
- Independent review: qa-seat-US1143-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1144: A Copilot run on token billing is priced per token from Copilot's dated AI-credit rates and the dollar value of a credit

- What changed: A Copilot run on token billing is priced per token from Copilot's dated AI-credit rates and the dollar value of a credit (3 points).
- Criteria passed:
  - AC1: Given the shipped `templates/model-prices.json`, then it carries a Copilot token-billing block of its own, apart from the provider-API `models` entries: the US-dollar value of one AI credit, its `effective` date and a `source` on GitHub's own Copilot billing page naming the day it was read (`read YYYY-MM-DD`), and, for each model Copilot's token billing prices, its five component rates in AI credits per million tokens under the id the Copilot CLI records (the `modelMetrics` key `lib/meter_copilot.py` and `lib/harness_usage.py` read, dotted, such as `claude-sonnet-5.5` or `gpt-5.5`, not the Anthropic API's `claude-sonnet-5-5`), a component Copilot does not bill separately at the rate it bills it at, said in `note`. No id in the block is also a `models` id, so a lookup by id alone is never ambiguous. The builder reads GitHub's page; no rate is typed from memory. Fails on: rates in dollars with no credit value, an undated or unsourced block, a Copilot rate filed under a provider-API id, or an id both blocks hold. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_copilot_credit_rates_are_dated_sourced_and_keyed_by_the_copilot_id`
  - AC2: Given the captured Copilot CLI output (`tests/fixtures/harness_usage/copilot.jsonl`, model `claude-sonnet-5.5`) parsed by `harness_usage.parse`, then `prices.cost` on its components, called as `sprint lane run`'s return line calls it, returns each component's tokens times that model's credit rate per million times the credit's dollar value, summed, with `unpriced` None, the figure typed in the test from the block's rates; and `run_state.usd` over a split naming that model gives the same figure. Fails on: the reading read as not priced, priced at an Anthropic API rate, or its credit count reported as dollars. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_a_recorded_copilot_reading_is_priced_from_credits_in_dollars`
  - AC3: Given a Copilot block missing the credit's dollar value, its `effective` date or its `source`, or a model rate missing one component, then `prices.load` raises `PriceTableError` naming the block and the field, never reading the gap as zero; beside each, the shipped block loads and prices AC2's reading (the positive control). Fails on: a missing rate read as 0, or the block dropped silently. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_a_partial_copilot_block_is_refused_by_name_and_the_shipped_one_loads`
  - AC4: Given a Copilot reading naming a dotted id the Copilot block does not hold, then `prices.cost` returns `usd` None with `unpriced` naming the id, never priced at the provider-API entry of a similar name (`claude-sonnet-5-5`) or at $0; beside it, in the same test, a listed Copilot id is priced (the positive control). Fails on: dot-to-hyphen or nearest-name matching onto the API table. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_an_unlisted_copilot_id_is_not_priced_beside_a_listed_one`
- Independent review: qa-seat-US1144-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1145: A project on Copilot request billing says so in its config, and only then are its premium requests priced in dollars

- What changed: A project on Copilot request billing says so in its config, and only then are its premium requests priced in dollars (2 points).
- Criteria passed:
  - AC1: Given a project config with no `pricing.copilot_billing`, then a Copilot run's sprint report prices its Copilot-block models' tokens from the credit rates in the Dollar cost row, and states its premium requests on their own row, counted but not priced, the row's basis naming token billing and the key that switches it. Fails on: the premium requests priced at the `premium_request` price under token billing, or summed into the Dollar cost row. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_token_billing_prices_copilot_tokens_and_counts_premium_requests_unpriced`
  - AC2: Given `pricing.copilot_billing: requests`, then the report prices the premium requests at the table's `premium_request` price, with its date, on their own row, and the Copilot-block models' tokens read not priced with the reason that the plan bills by request, never $0 and never at the credit rates; `prices.cost` on such a reading, as the lane return line calls it, gives the same reason. Fails on: both bases priced at once (the run billed twice), or the tokens read as free. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_request_billing_prices_premium_requests_and_leaves_copilot_tokens_unpriced`
  - AC3: Given one Copilot run carrying tokens and premium requests, priced once under each basis, then the two reports state different dollar figures, each the one the test types: the tokens times the credit rates under `tokens`, the premium requests times the request price under `requests`. Fails on: the basis ignored, so both reports state the same figure. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_one_copilot_run_prices_differently_under_each_basis`
  - AC4: Given `pricing.copilot_billing` set to anything other than `tokens` or `requests`, then `prices.load` raises `PriceTableError` naming the key and the two values it takes; beside it, each of the two values loads (the positive control). Fails on: an unknown value read as either basis. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_copilot_billing_takes_tokens_or_requests_and_refuses_anything_else`
  - AC5: Given `reference-config.md#pricing`, then its key table states `pricing.copilot_billing` with its default `tokens`, says `requests` is for a Copilot Pro or Pro+ annual plan kept on request-based billing and `tokens` for every other plan, and names 1 June 2026 as the day GitHub moved Copilot to token billing in AI credits. Fails on: the key undocumented, or the plans or the date missing. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_the_configuration_reference_states_the_copilot_billing_basis`
- Independent review: qa-seat-US1145-r1 APPROVE (2026-11-09).
- Known issues:
  - BG1324 (Low): No test replays a page filed before the Copilot billing basis existed, a mixed run's page drops the 'plan bills by request' reason, and US1145's lane-return test copies the call instead of running it - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1146: Abena Osei becomes the shipped skill's Primary and Maya Okafor moves to Secondary

- What changed: Abena Osei becomes the shipped skill's Primary and Maya Okafor moves to Secondary (5 points).
- Criteria passed:
  - AC1: Given `sdlc-studio/personas/abena-osei-head-of-engineering.md`, then it is headed `# Abena Osei`; its Quick Reference rows read Cast role `Primary`, Role `Head of engineering in an audited organisation` and Context `Leads several three-person teams (product owner, engineer, QA) directing agents the organisation already licenses; every release passes a change approval board`; and its `## End Goals` are these six, in order, each on one line: 1 `Every release passes the change board on the evidence the run produced, with no separate write-up`; 2 `Every specification and every change names an accountable person, not 'the agent'`; 3 `Know what each team's delivery costs per point and hold it to a monthly budget, whichever harness a team uses`; 4 `A defect that escapes to production is traced to where it got through, and the mistake is not repeated`; 5 `People who never open a terminal can follow progress without someone translating for them`; 6 `The process stays small enough to serve the work; every step earns its place`. Its `## Evidence` section has one `End goal N:` line per End goal (1: D0436, EP0275 and EP0276; 2: D0436 and RFC0063 WS2, the owner field; 3: D0436, CR0685 and CR0690; 4: D0436, RFC0061 and RFC0063 WS6, the escape loop; 5: D0436 and D0441; 6: D0443) and a closing line for the card itself citing D0436, D0443 and RFC0063. The test holds the six End goals word for word, as `END_GOAL_5` holds Maya's fifth. Fails on: an End goal reworded, reordered, wrapped onto a second line or missing; an End goal with no Evidence line; any id on the card that resolves to nothing. Verify: `pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_the_shipped_primarys_six_end_goals_stand_with_evidence`
  - AC2: Given the persona cards, then Abena's card carries every section a Primary needs (Quick Reference, Who They Are, End Goals, Experience Goals, Behaviours & Context, Frustrations, Scenario) and an `Interface` row that begins `The shipped skill:` and names `.claude/skills/sdlc-studio/` in a code span; Maya's card declares Cast role `Secondary` and carries no `Interface` row; and `validate.py personas` reports nothing for the cast. Both cards change in this one commit. Fails on: Maya's card still declaring `Primary` beside Abena's (two Primaries on one interface, the check's one error); a required section missing from Abena's card. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::PersonaWellFormedTests::test_shipped_personas_are_well_formed`
  - AC3: Given `sdlc-studio/personas/index.md`, then `## Primary` lists `[Abena Osei](abena-osei-head-of-engineering.md)` first and Rowan Achterberg second, `## Secondary` lists Maya Okafor above Jonah Reyes, and Rowan's bullet says every other unnamed mint names Abena; Rowan's card opens by naming Abena Osei as Primary for the shipped skill and says a unit that touches a shipped path (`.claude/skills/sdlc-studio/`) is judged against Abena; an unnamed mint whose Affects pick no interface names Abena Osei. Fails on: Rowan listed first; Rowan's card still judging a shipped-path unit against Maya; an unnamed mint naming Maya. Verify: `pytest tools/tests/test_persona_coherence.py::TwoPrimaryCastTests`
  - AC4: Given Maya's and Abena's cards, then Maya's opens with the quote `A specific person, not a type. The Secondary is served fully, but never at the Primary's expense.` and keeps End goals 1 to 5 word for word; each card's `## Boundaries` links every Primary's card and tables `The shipped skill | Abena Osei`, `Repository tooling | Rowan Achterberg` and `Both interfaces | Abena Osei`; Abena's Scenario has one of her teams run `/sdlc-studio sprint --crs Proposed --goal done`, then Abena sign the run with `sprint.py sign`, then the release pass the change approval board on the signed report's evidence with no separate write-up; Trevor's Boundaries names `[Abena Osei](abena-osei-head-of-engineering.md)` as the shipped skill's Primary. The three `test_mayas_*` tests keep their names, which US1081's Verify lines cite: the End goal test reads Maya's card by name, and the commands and Boundaries tests check both Maya's card and the shipped Primary's card. Fails on: an End goal of Maya's reworded; either table naming Maya for the shipped skill or for both; Abena's Scenario signing before the sprint runs; Trevor's card not linking Abena's. Verify: `pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests`
  - AC5: Given the PRD's `### Target Users`, then its Primary bullet for the shipped skill reads `**Primary for the shipped skill (the design target):** Abena Osei, head of engineering in an audited organisation, who leads several three-person teams directing the agents the organisation licenses and answers for every release at a change approval board.` and its Secondary bullet reads `**Secondary (served, never at the shipped skill's Primary's expense):** Maya Okafor, a solo founder-engineer who wants a disciplined, trustworthy lifecycle driven by an agent rather than vibe-coding, and the way in for a builder who starts alone; Jonah Reyes, a small-team lead adopting sdlc-studio on an inherited brownfield repo.`, with Rowan's and Trevor's bullets unchanged. Fails on: the shipped-skill label naming Maya; a registry persona the section does not name. Verify: `pytest tools/tests/test_persona_coherence.py::PrdTargetUsersTests`
  - AC6: Given the index's Revision History, then it gains a row dated the day it is committed whose Change reads `Abena Osei added as the shipped skill's Primary on the operator's pick (D0436), listed first so an unnamed mint names her; Maya Okafor moves to Secondary and is now less well served on her End goal 3, driving a whole batch to done autonomously (D0443 narrowed D0436's list to that one); Rowan's card and line, and Trevor's Boundaries, name Abena as the shipped skill's Primary`; the rows stay in date order and `Last updated` equals the latest row's date. Fails on: no row for the commit's date; `Last updated` left at 2026-11-01. Verify: `pytest tools/tests/test_persona_coherence.py::RegistryRecordTests`
  - AC7: Given Jonah Reyes's card, then its closing cast lines name Abena Osei as the shipped skill's Primary in place of Maya Okafor, its `- **Primary:**` line pointing at `abena-osei-head-of-engineering.md` and saying Jonah is served, but never at Abena's expense, and a feature that helps Jonah by adding ceremony for Abena is declined; and nothing else on his card changes: his End goals stay word for word against `GOALS_BASE` (7f3e91a9), so O6-O9 keep their citations. Fails on: his card still naming Maya as the Primary; any other line of his card changed. Verify: `pytest tools/tests/test_persona_coherence.py::TwoPrimaryCastTests::test_jonahs_cast_lines_name_the_declared_primary_and_nothing_else_changes`
- Independent review: qa-seat-US1146-r1 APPROVE (2026-11-09).
- Known issues:
  - BG1314 (Low): Two US1146 persona checks cannot catch a swapped Primary, and `validate.py personas` compares the whole Interface cell, so a card reverted to Primary passes AC2's own Verify - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### US1148: The PRD leads with human in the lead and its outcomes cite Abena Osei and Graham Doyle

- What changed: The PRD leads with human in the lead and its outcomes cite Abena Osei and Graham Doyle (3 points).
- Criteria passed:
  - AC1: Given `sdlc-studio/prd.md`, then the first non-blank line under `## Mission` is `**Human in the lead, not just in the loop.**`, and the Mission's existing paragraphs follow it unchanged. Fails on: the line missing, or placed after the first paragraph. Verify: `shell awk '/^## Mission$/{m=1;next} m&&NF{print;exit}' sdlc-studio/prd.md | grep -qxF '**Human in the lead, not just in the loop.**'`
  - AC2: Given the PRD's `## Outcomes`, then O10 to O13 follow O9, each a single `- **On:**` line reading word for word: O10 `A change that reaches a change board carries one evidence pack, built from what the run recorded rather than written afterwards and readable without running the tool: what changed, which criteria passed, who reviewed it independently, what is known to be wrong, and the person accountable for it, never 'the agent'; every specification it rests on names its accountable owner the same way (Abena Osei, End goal 1; Abena Osei, End goal 2; Graham Doyle, End goal 1; Graham Doyle, End goal 2)`; O11 `Each team sees what its delivery costs per point, in money, against a monthly budget it declares, whichever harness ran the work (Abena Osei, End goal 3)`; O12 `A defect that escapes to production is traced to the unit and the verdict that let it through, and the next plan, build and review carry what it taught, so the same mistake does not ship twice (Abena Osei, End goal 4; Graham Doyle, End goal 3)`; O13 `The committed record of reports, run records, verdicts and lessons is versioned and complete, so people who never open a terminal follow progress, evidence and cost on the read-only companion dashboard, without the operator's machine or anyone to translate (Abena Osei, End goal 5)`. The test holds the four texts word for word. Fails on: any word changed; an outcome missing or placed before O9; an outcome naming Rowan Achterberg (D0380). Verify: `pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_o10_to_o13_read_as_ruled`
  - AC3: Given O5, then it reads `The process stays small enough to serve the work: a repeated failure is fixed in the code path, and a check that catches nothing is deleted (Maya Okafor, End goal 5; Abena Osei, End goal 6)`, and `O5_CITES` in `tools/tests/test_lean_prd_refresh.py` holds the pair `("Maya Okafor", "5")` and `("Abena Osei", "6")`, so O5 citing exactly that pair, in either order, passes. Fails on: O5 citing either End goal alone; O5 re-pointed to another End goal; a third citation beside the pair; a card that no longer states End goal 5 or End goal 6. Verify: `pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_o5_and_jonahs_upgrade_goal_are_cited`
  - AC4: Given the outcomes and the cards, then every End goal of Maya Okafor (1 to 5), Jonah Reyes (1 to 4), Abena Osei (1 to 6) and Graham Doyle (1 to 3) is cited by exactly one outcome, and O1 to O4 and O6 to O9 keep their citations. Fails on: O12 losing `Graham Doyle, End goal 3`, so no outcome cites it; O11 also citing `Abena Osei, End goal 1`, so it is cited twice. Verify: `pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_every_end_goal_is_cited_once`
  - AC5: Given a temporary root holding copies of `sdlc-studio/prd.md` and `sdlc-studio/personas/`, when `sprint.py plan --root <tmp> --stories Ready --sprint-goal "One evidence pack per change" --serves O10 --no-fetch` runs, then it prints a line starting `goal serves: O10 -` and naming both `Abena Osei` and `Graham Doyle`, and no `goal serves: NONE` line; with O10's line removed from the copy, it prints `the PRD lists no outcome O10` and `goal serves: NONE`. Fails on: O10 missing, or citing neither persona. Verify: `pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_a_goal_serving_o10_names_the_primary_and_the_approver`
  - AC6: Given the changed registry and PRD, then `tools/tests/test_persona_coherence.py` and `tools/tests/test_lean_prd_refresh.py` pass in full. Fails on: any test in either module red. Verify: `shell python3 -m pytest -q tools/tests/test_persona_coherence.py tools/tests/test_lean_prd_refresh.py`
- Independent review: qa-seat-US1148-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### BG1302: `sprint lane brief --units US-01M6XQJF` tells the builder it shares a seam with a nameless unit, because the seam scope keeps the run state's `US01M6XQJF` and the asked-for `US-01M6XQJF` as two units

- What changed: `sprint lane brief --units US-01M6XQJF` tells the builder it shares a seam with a nameless unit, because the seam scope keeps the run state's `US01M6XQJF` and the asked-for `US-01M6XQJF` as two units (1 point).
- Criteria passed:
  - AC1: `lane_dispatch` (.claude/skills/sdlc-studio/scripts/sprint.py:2628) normalises every id with `sdlc_md.norm_id`, the function the run state uses, before deduplicating the seam scope, so a schema-3 unit the run state holds as `US01M6XQJF` and the command line names as `US-01M6XQJF` enters the scope once. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneSeamScopeTests::test_a_schema3_unit_named_with_its_hyphen_enters_the_scope_once`
  - AC2: Following the recorded steps no longer reproduces the defect: in a schema-3 project with a one-story run opened by `sprint plan --worklist <file> --write`, `sprint.py lane brief --units <that id as written> --format json` prints an empty `seams` list. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_a_one_unit_schema3_batch_briefed_by_its_hyphenated_id_has_no_seam`
  - AC3: No brief reports a seam between a unit and itself: `_batch_seams` drops a seam whose units name one unit under `sdlc_md.norm_id`, so the text brief prints no `Seam with` line for it, while a two-unit schema-3 batch whose stories share a file still names its seam with the other unit by id. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeamBriefTests::test_a_schema3_unit_has_no_seam_with_itself_and_a_real_seam_is_still_named`
- Independent review: qa-seat-BG1302-r1 APPROVE (2026-11-09).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### BG1303: `sprint lane brief` names a schema-3 unit's hand-in files by its normalised id (US01M6XQJF-claims.json) while `lane land --units US-01M6XQJF` reads them by the id as typed, so the self-check is never recorded at landing

- What changed: `sprint lane brief` names a schema-3 unit's hand-in files by its normalised id (US01M6XQJF-claims.json) while `lane land --units US-01M6XQJF` reads them by the id as typed, so the self-check is never recorded at landing (1 point).
- Criteria passed:
  - AC1: The hand-in names the lane brief prints (`_lane_hand_in_files`, .claude/skills/sdlc-studio/scripts/sprint.py:2809-2811) and the names `lane land` reads (`_record_and_brief`, .claude/skills/sdlc-studio/scripts/lib/lanes.py:200) are keyed by one spelling, `sdlc_md.norm_id`, whichever spelling `--units` was given: for `US-01M6XQJF` both name `US01M6XQJF-claims.json` and `US01M6XQJF-mutants.json`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneHandInSpellingTests::test_the_briefs_hand_in_names_are_the_names_land_reads_for_a_schema3_unit`
  - AC2: Following the recorded steps no longer reproduces the defect: in a schema-3 project, a hyphenated story briefed with `sprint.py lane brief --units <id as written>`, handed in under the names that brief prints and landed with `sprint.py lane land --worktree <wt> --units <id as written>`, has its self-check recorded and its QA brief written, and land prints no `self-check NOT RECORDED` line. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_schema3_unit_landed_by_its_hyphenated_id_records_its_self_check_and_writes_its_qa_brief`
  - AC3: The existing refusal still holds under the normalised key: a schema-3 unit landed by its hyphenated id whose hand-in lacks the claims or mutants file is still named `self-check NOT RECORDED`, with the missing file named by the spelling land looked for. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_schema3_hand_in_missing_its_files_is_still_named_by_the_spelling_land_read`
- Independent review: qa-seat-BG1303-r1 APPROVE (2026-11-09).
- Known issues:
  - BG1315 (Low): `help/sprint.md` still names a lane hand-in `<unit>-claims.json` under the id as typed, which BG1303's landing now keys by the normalised id, and `refine seams` still pairs a schema-3 unit with itself - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0654, on 2026-11-10 over fingerprint 15154fd97f127085.
- Report: RPT0028.

### BG1300: conftest's `_move_home` writes the test identity to whatever HOME names, overwriting, so a mutant that leaves HOME unmoved replaced the operator's ~/.gitconfig and 23 commits on main took the test author

- What changed: conftest's `_move_home` writes the test identity to whatever HOME names, overwriting, so a mutant that leaves HOME unmoved replaced the operator's ~/.gitconfig and 23 commits on main took the test author (2 points).
- Criteria passed:
  - AC1: A pytest session started with HOME naming a temporary home that holds a real-looking `.gitconfig` (a `[user]` block with another name and email, beside another section) leaves that file byte-identical, while the session's own private home holds `TEST_IDENTITY` and a fixture commit takes that identity. Fails on: the identity written to the path `os.environ["HOME"]` names. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py::PrivateHomeTests::test_the_operator_gitconfig_is_byte_identical_after_a_session`
  - AC2: Following the recorded steps no longer reproduces the defect: with a fixture copy of conftest.py that leaves HOME unmoved (`"HOME"` dropped from `PRIVATE_HOME`, and, separately, `_move_home` skipping the HOME assignment) and HOME naming a temporary home holding a `.gitconfig`, that file is byte-identical after the session, whether the session passes or fails to start. Beside it, a control session that does write over the file is seen as changed, so the probe can detect an overwrite. No case runs with HOME naming the operator's real home. Whoever runs these tests or any mutant of `conftest.py`, builder or reviewer, runs them only as `HOME=$(mktemp -d) python3 -m pytest <node> [<node> ...]`, the one form the operator's allow rule permits (D0454), and never with HOME unset or naming the operator's home. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py::PrivateHomeTests::test_a_session_with_home_left_unmoved_leaves_the_gitconfig_untouched`
  - AC3: `_move_home` writes the identity to `Path(private, PRIVATE_HOME["HOME"], ".gitconfig")`, built from `private` and never from the environment, and refuses to replace a file already there: a private home already holding a `.gitconfig` keeps it byte-identical and the session stops naming the path; the positive control, a fresh private home, is seeded with `TEST_IDENTITY` and a fixture commit takes it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py::PrivateHomeTests::test_the_seed_refuses_to_replace_an_existing_gitconfig .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py::PrivateHomeTests::test_a_fixture_commit_has_an_identity`
- Independent review: qa-seat-BG1300-r1 APPROVE (2026-11-12).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US0997: A report the close files cites the committed run record, never .local/run-state.json

- What changed: A report the close files cites the committed run record, never .local/run-state.json (3 points).
- Criteria passed:
  - AC1: Given a run closed through `sprint close`, when the filed RPT JSON is read, then every figure derived from the run record cites `sdlc-studio/reports/runs/<RUN-ID>.json`, and none cites `sdlc-studio/.local/run-state.json`, including the not-measured reasons the Markdown twin prints as the source it consulted. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_close_cites_the_tracked_run_record`
  - AC2: Given a run whose CI runs the close froze on its record, when the filed page is read, then each DORA figure derived from those runs cites the tracked run record first, followed by the forge reading that filled it (`gh run list`, or its failure reason), while the figures counted from git history keep citing it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_frozen_ci_figures_cite_the_tracked_record`
  - AC3: Given that run signed with `sprint sign` and committed, when a fresh clone holding no `.local/` reads the page, then the run-record path its figures cite exists in that clone and carries the signature the page carries, and `sprint_report check` there reads VALID. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_the_cited_record_opens_in_a_fresh_clone`
  - AC4: Given a signed page whose figures cite `sdlc-studio/.local/run-state.json`, as every page filed before this change does, and a page filed after the change, when `sprint_report check` runs on each in a fresh clone, then both read VALID and only the later page cites the tracked record. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CommittedRecordCitationTests::test_a_page_citing_local_still_checks_valid`
- Independent review: qa-seat-US0997-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1358 (Low): US0997's changelog and reference-scripts.md say the close commits the run record, but it files it - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US0998: The committed run record names its sprint plan by digest, not by a .local path

- What changed: The committed run record names its sprint plan by digest, not by a .local path (2 points).
- Criteria passed:
  - AC1: Given a run opened with `sprint plan --write` and closed with `sprint close`, when the tracked run record is read, then `plan_digest` holds `sha256:` and the full 64-hex digest of the sprint-plan.json that plan wrote, `plan` is null, and no value in the record names a path under `.local/`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py::PlanDigestTests::test_plan_write_records_a_content_digest`
  - AC2: Given a run whose batch a second `sprint plan --write` grows before its goal is judged, when the run is closed, then `plan_digest` is the digest of the plan the second write left, not the first. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py::PlanDigestTests::test_a_replan_moves_the_digest_to_the_last_write`
  - AC3: Given a rolling run whose next cycle is opened by `sprint boundary`, when that cycle's run record is filed, then its `plan_digest` is the digest of that cycle's own plan, not the previous cycle's and not a path. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py::PlanDigestTests::test_the_next_cycle_records_its_own_plan_digest`
- Independent review: qa-seat-US0998-r1 APPROVE (2026-11-12).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1000: The cost section states the run's cost in money from a pricing snapshot frozen at the close

- What changed: The cost section states the run's cost in money from a pricing snapshot frozen at the close (5 points).
- Criteria passed:
  - AC1: Given a project `pricing.models` entry for `claude-opus-5-5` whose input price is 15 (its other four component prices, `effective` and `source` set) and a run metered on that model, when `sprint close` files the report, then the cost section and its Markdown twin list each model the Dollar cost row priced with its five component prices in US dollars per million tokens, the entry's effective date and its source, all read from the page's own `price_table`, beside that model's dollars. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_close_freezes_prices_and_states_money`
  - AC2: Given a run whose meter reading leaves delegated agents' spend out (so the Tokens row adds the delegated totals), one delegated total read from an agent's transcript with a per-model split on `claude-opus-5-5` and one supplied `--tokens` total with no split, when `sprint close` files the report, then the Dollar cost row adds the read total's dollars at its model's rates, names the supplied total as unpriced with its token count, and says how many tokens the dollars leave unpriced; no money figure reads $0 or an estimate for it; and over a meter that reads the subagent transcripts no delegated total is priced a second time. An unpriced model and a `mixed` row read as they do at HEAD: named with their share, never $0. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_unpriced_tokens_are_named_never_zero_or_estimated`
  - AC3: Given that page signed and committed, when the `pricing.models` entry's input price for `claude-opus-5-5` is changed to 20 and `sprint_report check` runs in a fresh clone, then it reads VALID and the page still states 15 and the dollars it was filed with. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_a_price_change_after_the_close_moves_nothing`
  - AC4: Given a signed page filed before this change (dollars under USD_RULE, no price rows and no delegated dollars, as RPT0028) and a page filed after it, when a price is configured and `sprint_report check` runs on each, then both read VALID with their Markdown twins and only the later page carries the price rows and the delegated dollars. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_a_page_without_a_snapshot_is_unchanged`
- Independent review: qa-seat-US1000-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1356 (Low): US1000's AC2 test holds one read record per model, so replacing components across records survives - not-stop-ship, ruled by orchestrator.
  - BG1363 (Low): The US1000 report's price rows cite the config while their values come from the page's own price table - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1134: Print one line on success from the hooks and the commands agents filter, and emit lint-clean markdown

- What changed: Print one line on success from the hooks and the commands agents filter, and emit lint-clean markdown (5 points).
- Criteria passed:
  - AC1: Given a commit whose lanes all pass, then `pre-commit` and `commit-msg` each print one summary line, the last line each prints, and no `ok <lane>` line; the only lines a pass prints above it are the two an author learns from nowhere else: the stamps-staged lane's re-read list (printed by the hook's `verdict()` on a pass since BG0779) and the settle step's report of the drift it restaged or left unstaged (US0899). Given a failing lane, or `SDLC_GATE_VERBOSE=1`, they print the per-lane list with the failing lane's rule, detail and fix. CONTRIBUTING.md's paragraph on the commit gate names `SDLC_GATE_VERBOSE=1` as the way to see the lanes and the 90-second budget report on a pass. Fails on: the summary printed on failure too, hiding the failing lane; the `ok <lane>` lines still printed on success; a pass that hides the re-read list or the settle report. Verify: `pytest tools/tests/test_quiet_hooks.py::QuietHookTests::test_success_is_one_line_and_failure_is_verbose tools/tests/test_quiet_hooks.py::QuietHookTests::test_a_pass_still_shows_the_re_read_list_and_the_settle_report`
  - AC2: Given a fixture where each succeeds, then `critic.py self-check record`, `verify_ac.py run`, `docgen.py surface`, `docgen.py reading-guides` and `sprint.py lane return` print at most two lines; given a refusal, each prints its full reason. Fails on: any success path over two lines, or a refusal path cut to the same two lines. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py::QuietSuccessTests::test_each_command_is_quiet_on_success_and_verbose_on_refusal`
  - AC3: Given an argument carrying a URL, then the markdown `file_finding.py`, `critic.py record` and the retro write passes the markdown lane's rules unedited, with no bare URL. Fails on: a producer writing a bare URL (the BG1227 shape) or a line the markdown lane refuses. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py::QuietSuccessTests::test_the_producers_write_lint_clean_markdown`
  - AC4: Given the 17 existing modules that drive the real hooks over a commit (under `tools/tests/`: `test_commit_msg_hook`, `test_commit_msg_mentions`, `test_pre_commit_docgen`, `test_precommit_stamps_advisory`, `test_lean_precommit_parallel`, `test_precommit_window_guard`, `test_lean_commit_lanes`, `test_lean_index_drift`, `test_lean_tsd_script_pin`, `test_message_first_gate`, `test_precommit_scope_collapse_lane`, `test_precommit_budget_recording`, `test_precommit_floor_pending`, `test_repo_writes` and `test_lean_refusal_log`; under the skill's `scripts/tests/`: `test_lean_advisory_warnings` and `test_lean_test_selection`), then each passes, and each assertion it makes on a passing hook's per-lane, SKIP, note, budget or advisory output either runs that hook with `SDLC_GATE_VERBOSE=1` or asserts the summary line; the re-read list and the settle report AC1 keeps are asserted without it. Fails on: any of them red; a pass-path `assertNotIn` left reading the summary line alone, where it holds whatever the hook does (`test_lean_refusal_log.py:119`, `test_repo_writes.py:332`); an assertion on a refusal removed or loosened. Verify: `pytest tools/tests/test_precommit_window_guard.py tools/tests/test_lean_commit_lanes.py tools/tests/test_lean_tsd_script_pin.py tools/tests/test_precommit_scope_collapse_lane.py tools/tests/test_precommit_stamps_advisory.py .claude/skills/sdlc-studio/scripts/tests/test_lean_advisory_warnings.py .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py tools/tests/test_message_first_gate.py tools/tests/test_lean_refusal_log.py tools/tests/test_lean_index_drift.py tools/tests/test_commit_msg_hook.py tools/tests/test_commit_msg_mentions.py tools/tests/test_pre_commit_docgen.py tools/tests/test_lean_precommit_parallel.py tools/tests/test_precommit_budget_recording.py tools/tests/test_precommit_floor_pending.py tools/tests/test_repo_writes.py`
- Independent review: qa-seat-US1134-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1378 (Low): US1134's AC3 skips markdownlint without saying so when the binary is missing - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1147: Graham Doyle joins the registry as Served and Trevor Hale narrows to what the skill declines

- What changed: Graham Doyle joins the registry as Served and Trevor Hale narrows to what the skill declines (3 points).
- Criteria passed:
  - AC1: Given `sdlc-studio/personas/graham-doyle-change-approver.md`, then it is headed `# Graham Doyle`; its Quick Reference rows read Cast role `Served`, Role `Chairs the change approval board in an audited organisation` and Context `Approves each release from the evidence put in front of him; never runs the tool or opens a terminal`; it carries no `Interface` row; and its `## End Goals` are these three, in order, each on one line: 1 `Approve a change from one document showing what changed, which criteria passed, who reviewed it independently, what is known to be wrong, and who is accountable`; 2 `Trust that the evidence came from the process, not written after the fact`; 3 `See fewer surprises in production over time`. The test holds the three word for word. Fails on: an End goal reworded, reordered, wrapped onto a second line or missing; a Cast role other than Served; an `Interface` row. Verify: `pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_the_change_approvers_card_states_the_three_ruled_end_goals`
  - AC2: Given the persona cards, then Graham's card carries the sections a Served card needs (Quick Reference, Who They Are, End Goals, Behaviours & Context, Frustrations; Experience Goals and Scenario optional) and `validate.py personas` reports nothing for the cast. Fails on: a required section missing from his card. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::PersonaWellFormedTests::test_shipped_personas_are_well_formed`
  - AC3: Given the index and the PRD, then the index carries `## Served (affected by the product without using it)` between `## Secondary` and `## Negative`, listing `- [Graham Doyle](graham-doyle-change-approver.md) - chairs the change approval board; approves a release from the evidence it carries and never runs the tool (D0437).`; `ROLES` in `tools/tests/test_persona_coherence.py` includes `Served` and the derived-names fixture parses a Served entry; and `### Target Users` gains, after the Secondary bullet, `**Served (affected by the product without using it):** Graham Doyle, who chairs the change approval board and approves a release from the evidence it carries, without running the tool.` Fails on: Graham left out of Target Users while the index lists him; `Served` missing from `ROLES`, so the check reads past him. Verify: `pytest tools/tests/test_persona_coherence.py::PrdTargetUsersTests`
  - AC4: Given a temporary root holding copies of `sdlc-studio/prd.md` and `sdlc-studio/personas/`, when `sprint.py plan --root <tmp> --stories Ready --sprint-goal "Approve a release from one document" --serves "Graham Doyle" --no-fetch` runs, then it prints `goal serves: Graham Doyle (Served)` and no `goal serves: NONE` line; the same command with `--serves "Trevor Hale"` prints `goal serves: NONE`. Fails on: Graham's card missing or its Cast role not Served; the Trevor control not printing NONE. Verify: `pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_a_goal_serving_the_change_approver_is_not_flagged`
  - AC5: Given Trevor's card, then its `## End Goals (stated to exclude)` are exactly these four, in order: 1 `Drive delivery from a rich GUI with boards, swimlanes, and portfolio dashboards`; 2 `Enforce multi-stage human approval and sign-off gates on every change`; 3 `Have non-technical staff operate the tool`; 4 `Sync the work to Jira, Azure Boards or another enterprise tracker`; its Quick Reference Role reads `GUI-first delivery manager` and Context `Runs delivery from a GUI work-tracker and wants non-technical staff operating the tool and a human approval on every change`; its `## Why We Are Not Designing For Him` names Abena Osei, not Maya, as the Primary those wants would cost, and says audit evidence and the running of several teams are served through her (D0436); the index's Trevor bullet reads `- [Trevor Hale](trevor-hale-enterprise-pm.md) - a GUI-first operator wanting non-technical staff to run the tool and a human approval on every change. A signal to decline, not a backlog. Well-formed.` and the PRD's Negative bullet reads `**Negative (deliberately not designed for):** Trevor Hale, a GUI-first operator wanting non-technical staff to run the tool and a human approval on every change. A signal to decline, not a backlog.`; D0213, `sprint.py sign` and the links to each Primary's card stay. Fails on: a fifth excluded End goal left (SSO and compliance reporting from the corporate stack, or governing many teams centrally); tracker sync missing from the excluded End goals; his card naming Maya as the Primary; the index or the PRD still saying central governance. Verify: `pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_trevor_is_narrowed_to_the_three_wants_the_skill_declines`
  - AC6: Given the index's Revision History, then it gains a row dated the day it is committed whose Change reads `Graham Doyle added as Served, the change approver (D0437); Trevor Hale narrowed to a GUI-first operator, non-technical staff running the tool and a human approval on every change (D0436)`; the rows stay in date order and `Last updated` equals the latest row's date. Fails on: no row for the commit's date; a row out of date order. Verify: `pytest tools/tests/test_persona_coherence.py::RegistryRecordTests`
  - AC7: Given Trevor's `## Scenario`, then it no longer points him at an enterprise tool that fits: it points his wants for boards and dashboards at the read-only companion dashboard over the committed record (RFC0063 D6), and still declines a human approval on every change, non-technical staff running the tool and sync to an enterprise tracker. Fails on: the Scenario still naming an enterprise tool; the companion dashboard named as anything but read-only; any of the three declined wants offered. Verify: `pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_trevors_scenario_points_boards_and_dashboards_at_the_read_only_companion_dashboard`
- Independent review: qa-seat-US1147-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1321 (Low): Trevor Hale's Scenario check misses a capitalised offer and a negation outside its word list, so changelog.d/US1147.md claims more than the AC7 test holds - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1149: The sprint entry names the projected re-read cost when the orchestrating session holds more than 80k tokens, under sprint.fresh_session warn or block, and the cost anatomy flags a run whose orchestrator averages over 150k a call

- What changed: The sprint entry names the projected re-read cost when the orchestrating session holds more than 80k tokens, under sprint.fresh_session warn or block, and the cost anatomy flags a run whose orchestrator averages over 150k a call (5 points).
- Criteria passed:
  - AC1: Given an open fixture run, a resume brief written by `sprint.py handoff`, `sprint.fresh_session` unset, and a session transcript in the directory `SDLC_STUDIO_TRANSCRIPTS` names whose newest call's context (its input + cache write + cache read, as the cost anatomy counts a context) is 120,000 tokens, when `sprint.py resume` runs, and when `sprint.py plan --write` opens a run over the same transcript, then each prints one warning on stderr naming the session's context (120,000 tokens), the 80,000-token threshold, the projected re-read cost (that context priced as a cache read under `TOKEN_WEIGHTS`: 12,000 input-equivalent tokens a call and 1,200,000 over the next 100 calls, about one wave, since run six's orchestrator made 323 calls over three) and the remedy (`sprint.py handoff`, then `sprint.py resume` in a fresh session), and each does the rest of its work and exits as it does without the check. At a context of exactly 80,000 tokens neither prints the warning; at 80,001 both do. Fails on: a warning at 80,000 or below; none above it; a projection other than the context x 0.1 a call and x 100 over 100 calls; the warning on stdout, where it would break `plan --format json` and move the next-step line `plan --write` ends on. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::FreshSessionTests::test_warn_names_the_projected_re_read_above_80k_and_nothing_at_or_under_it`
  - AC2: Given the same fixture with `sprint.fresh_session: block`, when `sprint.py resume` runs over a session whose newest call's context is above 80,000 tokens, then it exits 2 with nothing on stdout, naming on stderr the session's context, the threshold and the remedy (start a fresh session and run `sprint.py resume` there); at 80,000 or below it resumes as under `warn`. `sprint.py plan --write` under `block` warns as under `warn` and still opens the run, because `sprint.py handoff` cannot write a brief without an open run. Under `off` neither entry reads the session or prints a line about it, and any other value reads as `warn`. Fails on: `block` resuming above the threshold, or refusing at or below it; `plan --write` refused under `block`, leaving no run to hand off; a line under `off`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::FreshSessionTests::test_block_refuses_resume_above_80k_and_plan_write_still_opens_the_run`
  - AC3: Given no transcript in the meter's directory, a transcript whose newest usage record gives no per-call context, or a harness other than Claude Code chosen by the token meter (`SDLC_STUDIO_HARNESS=cursor`), when either entry runs, then under `warn` it prints nothing about the session, and under `block` it prints one stderr line saying the session's size is not available, with the reason, and goes on without refusing. Fails on: an unreadable size read as 0, or as under the threshold without saying so under `block`; a refusal for a size that could not be read; any line under `warn`, which would land in every fixture plan that names no transcript. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::FreshSessionTests::test_an_unreadable_session_size_is_named_under_block_and_never_refuses`
  - AC4: Given a fixture run whose main-thread (orchestrator) calls in the run's window average more than 150,000 tokens of context a call, when `sprint.py cost --anatomy` runs, then after the role table it prints a line flagging the orchestrator's average context against the 150,000-token threshold and naming the remedy (hand off at each wave boundary with `sprint.py handoff` and `sprint.py resume`), and `--format json` carries the same as `orchestrator_context_budget` and `orchestrator_over_context_budget`. At an average of exactly 150,000 or below it says the orchestrator stayed within 150,000; with no per-call record it reads not available. Fails on: an average of exactly 150,000 flagged; one above it not flagged; a missing average read as 0 or as within the threshold. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_an_orchestrator_averaging_over_150k_a_call_is_flagged`
  - AC5: Given the shipped configuration and docs, then `templates/config-defaults.yaml` declares `fresh_session: warn` under `sprint:` beside `affects_check`, with a comment naming `warn`, `block` and `off`; help/sprint.md's section on handing off and resuming names the 80,000-token check, what each of `warn`, `block` and `off` does, and that `plan --write` never refuses on it; and the cost anatomy paragraphs in help/sprint.md and reference-sprint.md name the 150,000-token orchestrator flag. Fails on: the key read by `sprint.py` but not declared in the defaults; a mode the docs name that the code does not honour, or one it honours that they omit; the orchestrator flag undocumented. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::HelpTests::test_the_fresh_session_check_and_the_orchestrator_flag_are_declared_and_documented`
- Independent review: qa-seat-US1149-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1351 (Low): US1149's tests have no fixture with two synthetic records in a row - not-stop-ship, ruled by orchestrator.
  - BG1364 (Low): fresh_session: no or false reads as off, though the help and US1149's AC2 say any other value reads as warn - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### BG1010: sprint_report.py build --run resolves the named run and then builds the page from the default run

- What changed: sprint_report.py build --run resolves the named run and then builds the page from the default run (1 point).
- Criteria passed: none ticked.
- Criteria not ticked: AC1.
- Independent review: qa-seat-BG1010-r1 APPROVE (2026-11-12).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1001: The lane-yield appendix is read from the committed run record, as the close froze it

- What changed: The lane-yield appendix is read from the committed run record, as the close froze it (3 points).
- Criteria passed:
  - AC1: Given a clone whose refusal log holds a refusal inside the run and whose run archive holds an earlier run, when `sprint close` files the report, then the lane-yield rows are recorded on the run record, every lane-yield figure cites the tracked run record ahead of `git log`, and no figure anywhere on the page names a path under `.local/`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_yield_frozen.py::FrozenLaneYieldTests::test_close_freezes_the_tally_on_the_run_record`
  - AC2: Given that run signed and committed, when `sprint_report.py build --run <RUN-ID> --id <RETRO> --format json` runs in a fresh clone holding no refusal log and no run archive, then the lane-yield section is present with the rows the filed page carries. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_yield_frozen.py::FrozenLaneYieldTests::test_a_fresh_clone_reads_the_frozen_tally`
- Independent review: qa-seat-US1001-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1361 (Low): US1001's note says 'this clone's refusal log', which misleads in a fresh clone - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### BG1030: Prose after `BLOCKING: none`, or a trailing `RULINGS:` line, is folded into BLOCKING and refused, so an APPROVE carrying rulings cannot be recorded unedited

- What changed: Prose after `BLOCKING: none`, or a trailing `RULINGS:` line, is folded into BLOCKING and refused, so an APPROVE carrying rulings cannot be recorded unedited (3 points).
- Criteria passed:
  - AC1: Given a block whose BLOCKING is `none` followed by a sentence, when it is recorded, then it records with no blocking finding and the sentence is not lost Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_prose_after_blocking_none_records`
  - AC2: Given a block with a `RULINGS:` line after `BLOCKING: none`, when it is recorded, then it records, and the rulings are kept on the row or the contract names where they go Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_a_rulings_line_records`
  - AC3: Given a rejoinder brief, its return contract names the RULINGS line, and a round-2 verdict that rules each earlier finding CLOSED, OVER-CLAIMED or MOVED there is recorded without re-emitting, with the rulings stored as rulings and not as a [new] finding Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_the_rejoinder_contract_names_rulings_and_they_record_as_rulings`
- Independent review: qa-seat-BG1030-r1 APPROVE (2026-11-12).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1011: A review brief names the file the reviewer writes its verdict to

- What changed: A review brief names the file the reviewer writes its verdict to (2 points).
- Criteria passed:
  - AC1: Given a fixture unit and a working directory that is not the repository root, when `critic.py brief --unit US0001 --seat qa --root <root>` runs, then after the unchanged return contract the brief names an absolute path under `<root>/sdlc-studio/reviews/verdicts/US0001/`, with the `UNIT: US0001` and `BRIEF: <file stem>` lines the file must open with, and the record command the footer prints reads that path with `--from-verdict`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py::BriefVerdictPathTests::test_the_brief_names_an_absolute_verdict_path_and_records_from_it`
  - AC2: Given two briefs of the same unit and seat, when both are printed, then they name different verdict paths and print the same fingerprint, and `critic.py record --brief-file` on either saved brief stores that fingerprint. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py::BriefVerdictPathTests::test_two_briefs_share_a_fingerprint_and_not_a_path`
  - AC3: Given a round-1 REJECT recorded from the file its brief named, when the rejoinder brief for round 2 is printed, then it names a new path and never the round-1 file. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py::BriefVerdictPathTests::test_a_rejoinder_never_names_an_earlier_rounds_file`
- Independent review: qa-seat-US1011-r1 APPROVE (2026-11-12).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1012: A recorded verdict is bound to the bytes of the file its brief issued

- What changed: A recorded verdict is bound to the bytes of the file its brief issued (5 points).
- Criteria passed:
  - AC1: Given a block at a path the brief issued, opening with its UNIT and BRIEF lines and carrying prose beyond the VERDICT, ISSUES and BLOCKING fields, when `critic.py record --from-verdict <path>` runs, then the new row's `Source` cell is `sha256:<first 16 hex digits of the file's exact bytes> <file basename>`, and the file is byte-identical afterwards. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::VerdictFileBindingTests::test_an_issued_file_is_hashed_as_written`
  - AC2: Given the same verdict given by `--verdict` and `--issues`, by `--from-verdict -`, from a file outside `sdlc-studio/reviews/verdicts/`, or from `sdlc-studio/reviews/verdicts/US0001/mine.txt`, which no brief issued, when `record` writes it, then the row's `Source` cell is `-` and `record` prints that the verdict was transcribed. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::VerdictFileBindingTests::test_a_verdict_from_no_issued_file_is_marked_transcribed`
  - AC3: Given an eight-column ledger and the row identities a run record froze from it, when `critic.py record` writes the first verdict after the change, then a ninth `Source` column is added, every earlier row is padded with `-` and keeps its cells, the `Verdict` column still parses as APPROVE or REJECT, and every frozen identity is still found among the ledger's rows. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::VerdictFileBindingTests::test_the_source_column_moves_no_frozen_row_identity`
  - AC4: Given one row recorded from an issued file and one transcribed row, when `critic.py show` runs, then the first row's line reads 'from the brief's verdict file (writer unread)' and names the file, the second reads 'transcribed', and `--format json` carries the same as a field. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::VerdictFileBindingTests::test_show_says_where_each_verdict_came_from_and_claims_no_writer`
- Independent review: qa-seat-US1012-r1 APPROVE (2026-11-12).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1013: A verdict that differs from its issued file, or was recorded before, is named

- What changed: A verdict that differs from its issued file, or was recorded before, is named (3 points).
- Criteria passed:
  - AC1: Given an issued, unrecorded file for US0001 and a block recorded for US0001 with `--brief <fp>` by `--from-verdict -` or by `--verdict` and `--issues`, when `record` runs, then a block that drops or changes a finding is written as transcribed with a warning naming the issued file and the first finding that differs, and a block with the same findings in the same order, reflowed only, is written with no warning. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py::VerdictDriftTests::test_a_transcription_that_differs_from_the_issued_file_warns_and_a_reflow_does_not`
  - AC2: Given bare `VERDICT: APPROVE` / `ISSUES: none` / `BLOCKING: none` blocks for US0001 and US0002, each at its own issued path under its own header, when both are recorded, then both rows are written; and given a file whose hash an earlier row carries, or whose UNIT or BRIEF line names another unit or another issued file, `record` refuses with exit 2, names the earlier row or the mismatch, and writes nothing. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py::VerdictDriftTests::test_a_replayed_or_misheaded_file_is_refused_and_bare_approves_are_not`
  - AC3: Given one recorded issued file edited afterwards and another deleted, when `critic.py show` runs, then it names the first as changed since it was recorded and the second as missing. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py::VerdictDriftTests::test_show_names_a_verdict_file_changed_or_missing_since_it_was_recorded`
- Independent review: qa-seat-US1013-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1352 (Low): US1013's in-order comparison of a verdict and its issued file has no pinning test - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1014: A recorded verdict names the agent that was briefed and wrote it, read from the harness transcript

- What changed: A recorded verdict names the agent that was briefed and wrote it, read from the harness transcript (5 points).
- Criteria passed:
  - AC1: Given fixture Claude Code transcripts in which subagent `r1` received the issued verdict path and wrote that file with its Write tool, when `critic.py record --from-verdict <path>` runs with `SDLC_STUDIO_HARNESS=claude` and that session id, then the row's `Source` cell carries `session:<id> agent:r1` after the hash, and `show` labels the verdict as written by agent r1. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py::VerdictProvenanceTests::test_the_briefed_agent_that_wrote_the_file_is_named_on_the_row`
  - AC2: Given that the file's bytes differ from the content `r1`'s write carried, or that a later write to the path sits in another context's transcript (the main thread's), when `record` runs, then it writes the row and warns, naming the briefed agent and the context that last wrote the file. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py::VerdictProvenanceTests::test_a_file_rewritten_by_another_context_warns`
  - AC3: Given a harness whose store is not read (`SDLC_STUDIO_HARNESS=cursor`), or Claude transcripts holding no write of the path, when `record` runs, then the row's provenance reads `unknown`, `record` says why, and the row never names an agent. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py::VerdictProvenanceTests::test_an_unread_store_records_unknown_provenance`
- Independent review: qa-seat-US1014-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1355 (Low): Four branches US1014's claims name have no test - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1015: A verdict written by the context that edited the unit is a self-review, whatever seat it names

- What changed: A verdict written by the context that edited the unit is a self-review, whatever seat it names (5 points).
- Criteria passed:
  - AC1: Given fixture transcripts in which the main thread edited `src/unit.py` (the unit's Affects) and then wrote the issued verdict file, when `critic.py record --reviewer "Tomas Reinholt (qa)" --author engineering` runs, then the row is written with `self-review:src/unit.py` in its `Source` cell, `show` says so, and the row is no independent review where independence is judged: `critic.is_independent` reads it False, `sprint.uncovered_units` (the close's review-coverage step) names US0001, and `sprint.seal_bar_unmet` (the review bar `sprint.py sign` stops on) is unmet for it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_the_editing_context_is_a_self_review_whatever_the_seat_name`
  - AC2: Given the same editing main thread, when it runs `transition.py set US0001 --status Done --verdict APPROVE --reviewer "Tomas Reinholt (qa)" --author engineering`, then the verdict row it writes carries `self-review:src/unit.py` in its `Source` cell and the command warns naming the edited file; the transition is not refused for it (D0388 adds no gate at Done), and `sprint.uncovered_units` and `sprint.seal_bar_unmet` name US0001 as not independently reviewed. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_the_one_call_close_from_the_editing_thread_records_a_self_review`
  - AC3: Given reviewer subagent `r1`, which received the brief and afterwards applied a mutant with its Edit tool to `src/unit.py` in its own worktree, reverted it, and wrote the issued verdict file, when `record` runs, then the row is independent and carries no self-review token. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_a_reviewer_mutating_its_own_worktree_after_the_brief_stays_independent`
  - AC4: Given author subagent `a1`, which edited `src/unit.py` inside its worktree at `.claude/worktrees/agent-a1` and was never briefed, when `a1` writes a verdict file for the unit, then the row is a self-review naming `src/unit.py`; and in the same test, subagent `r1`, which edited nothing, writing the next round's file records as independent. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_a_worktree_author_is_matched_to_the_units_files`
- Independent review: qa-seat-US1015-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1375 (Low): US1015's run-state floor and its Write, MultiEdit, NotebookEdit, Read and Bash evidence cases have no tests - not-stop-ship, ruled by orchestrator.
  - BG1376 (Low): US1015's brief bound counts any round's issued path, not the round being recorded - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### US1016: critic.py brief --rejoinder with no file quotes the seat's standing REJECT from the ledger

- What changed: critic.py brief --rejoinder with no file quotes the seat's standing REJECT from the ledger (3 points).
- Criteria passed:
  - AC1: Given a round-1 REJECT recorded from an issued file, when `critic.py brief --unit US0001 --seat qa --rejoinder` runs with no value, then the brief quotes that file's bytes verbatim beneath the RE-REVIEW mark, found through the row's `Source` cell, and its fingerprint equals the one `--rejoinder <that file>` prints. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_the_ledger_rejoinder_quotes_the_issued_file_verbatim`
  - AC2: Given a REJECT recorded by `--verdict` and `--issues` with no file, when the ledger rejoinder is printed, then it rebuilds VERDICT, ISSUES and BLOCKING from the row's cells with every finding as recorded, and labels the quotation as rebuilt from the ledger's fields. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_a_transcribed_reject_is_rebuilt_from_its_cells_and_labelled`
  - AC3: Given no unanswered REJECT in the unit's current delivery from a reviewer of the briefed seat (none recorded, or every one answered by that reviewer's APPROVE), when `brief --rejoinder` runs with no file, then it exits 2, names the unit and the seat, and prints nothing on stdout. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_no_unanswered_reject_for_the_seat_is_refused`
- Independent review: qa-seat-US1016-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1353 (Low): Two branches of US1016's rejoinder selection have no test - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0467, on 2026-11-12 over fingerprint 92ed4ae3b01b2bf2.
- Report: RPT0029.

### BG1190: A verifier that times out is killed alone, so its children run on and load every verifier after it

- What changed: A verifier that times out is killed alone, so its children run on and load every verifier after it (2 points).
- Criteria passed:
  - AC1: A shell verifier that times out leaves no process of its group running once `verify_ac.run_verifier` returns, and still reads red as a timeout. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_timeout_reaps.py`
- Independent review: qa-seat-BG1190-r1 APPROVE (2026-11-12); qa-seat-BG1190-r3 APPROVE (2026-11-12).
- Known issues:
  - BG1401 (Low): BG1190's unpinned reap and BG1262/BG1261's watchdog SIGKILL after its grace are covered by no test - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1190: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1190 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1228: BG1190 did not converge in review: round 2 REJECT findings

- What changed: BG1190 did not converge in review: round 2 REJECT findings (2 points).
- Criteria passed:
  - AC7: BG1190 AC1 still passes: A shell verifier that times out leaves no process of its group running once `verify_ac.run_verifier` returns, and still reads red as a timeout. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_timeout_reaps.py`
- Criteria not ticked: AC1, AC2, AC3, AC4, AC5, AC6.
- Independent review: qa-seat-BG1228-r1 APPROVE (2026-11-12).
- Known issues:
  - unpriced (close gap): BG1228: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1228 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1112: verify_ac's timeout kills only the shell it started, so a timed-out shell or eval verifier leaves its real test runner (npx, vitest, pytest) running as an orphan that keeps writing into the workspace

- What changed: verify_ac's timeout kills only the shell it started, so a timed-out shell or eval verifier leaves its real test runner (npx, vitest, pytest) running as an orphan that keeps writing into the workspace (1 point).
- Criteria passed:
  - AC1: When a shell or eval verifier times out, `verify_ac` reports exit 124 and no process from that verifier's tree is still running when it returns Verify: `shell python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests -k timed_out_verifier_leaves_no_process`
- Independent review: qa-seat-BG1112-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1384 (Low): The changelog's 6.3.0 text and the BG1112 fragment still over-state what the group kill does - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1112: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1112 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1005: A pytest Verify that PARTLY skips is stamped green - BG0317 closed only the all-skipped case

- What changed: A pytest Verify that PARTLY skips is stamped green - BG0317 closed only the all-skipped case (2 points).
- Criteria passed:
  - AC1: A pytest Verify whose run passes some tests and skips others is not stamped `Verified: yes`, and `verify_ac run` names each skipped test and why Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py::PartialSkipTests::test_a_partly_skipped_run_is_not_verified`
  - AC2: The same holds on the batch path that reads a JUnit report, so neither route stamps a partly skipped run Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py::PartialSkipTests::test_the_junit_path_reads_a_partial_skip_as_unverified`
- Independent review: qa-seat-BG1005-r1 APPROVE (2026-11-13).
- Known issues:
  - BG1395 (Medium): BG1005 makes a criterion whose pytest target partly skips on the running machine read red, including Done criteria the release gate re-runs, and the count is not measured - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1005: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1005 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1009: revert-check reads a timed-out verifier as red and an empty revert as green, so it passes a unit it never measured and refuses one it never reverted

- What changed: revert-check reads a timed-out verifier as red and an empty revert as green, so it passes a unit it never measured and refuses one it never reverted (3 points).
- Criteria passed:
  - AC1: A revert-check whose verifier times out reports that criterion as not measured, and never passes a unit on it Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_unmeasurable.py::UnmeasurableRevertTests::test_a_timed_out_verifier_is_not_red`
  - AC2: A revert-check whose revert changes no byte reports the unit as not judged and never refuses it Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_unmeasurable.py::UnmeasurableRevertTests::test_an_empty_revert_is_not_judged`
  - AC3: help/verify.md states revert-check's verdicts and exit codes (pass 0, refused 1, not judged 3, error 1), including that a directory in Affects reads as no production file and the unit is not judged, and each example command it shows returns the code it states Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_unmeasurable.py::UnmeasurableRevertTests::test_the_help_verdicts_match_the_exit_codes`
  - AC4: A paired control: the same unit, judged from an earlier base whose file differs, is still refused or passed as it was before the fix, so a change that reports every unit as not judged cannot pass AC2 Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_unmeasurable.py::UnmeasurableRevertTests::test_a_differing_base_is_still_judged`
- Independent review: qa-seat-BG1009-r1 APPROVE (2026-11-13).
- Known issues:
  - unpriced (close gap): BG1009: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1009 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG0991: verify_ac attaches a **Verify:** line from a LATER section (history, update notes) to the last criterion and executes it, because a criterion block never closes at a ## heading

- What changed: verify_ac attaches a **Verify:** line from a LATER section (history, update notes) to the last criterion and executes it, because a criterion block never closes at a ## heading (2 points).
- Criteria passed:
  - AC1: A **Verify:** line under a later ## section is not attached to any criterion and is not executed Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_section_boundary.py -k verify_in_later_section_not_attached`
  - AC2: `verify_ac` lint names a **Verify:** line that sits outside the Acceptance Criteria section Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_section_boundary.py -k lint_names_verify_outside_criteria`
- Independent review: qa-seat-BG0991-r1 APPROVE (2026-11-13).
- Known issues:
  - unpriced (close gap): BG0991: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG0991 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1336: The lane brief's verify_ac step writes into the unit's own artefact outside its Affects, and lane land's rebase then fails on that unstaged edit while exiting 0 under a pipe

- What changed: The lane brief's verify_ac step writes into the unit's own artefact outside its Affects, and lane land's rebase then fails on that unstaged edit while exiting 0 under a pipe (2 points).
- Criteria passed:
  - AC1: Given a lane worktree whose only unstaged change is `verify_ac`'s edit to the unit's own artefact, when `sprint lane land` runs, then it lands the staged Affects (discarding or carrying that edit as the main tree's verify will rewrite it) instead of refusing the rebase. Fails on: the land refused with 'cannot rebase: You have unstaged changes'. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_verify_acs_artefact_edit_does_not_block_the_land`
- Independent review: qa-seat-BG1336-r1 APPROVE (2026-11-13).
- Known issues:
  - BG1336 (Medium): The lane brief's verify_ac step writes into the unit's own artefact outside its Affects, and lane land's rebase then fails on that unstaged edit while exiting 0 under a pipe - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1336: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1336 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1337: sprint.py lane land commits a lane at its worktree's old base and rebases afterwards, so the hook judges it against code main has already fixed

- What changed: sprint.py lane land commits a lane at its worktree's old base and rebases afterwards, so the hook judges it against code main has already fixed (2 points).
- Criteria passed:
  - AC1: Given a lane worktree behind main, where main fixed a test that fails at the worktree's base, when `sprint lane land` runs, then the commit hook judges the lane on main's code and the land succeeds. Fails on: the land refused for a failure present only at the old base. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_lane_behind_main_is_judged_on_mains_code`
- Independent review: qa-seat-BG1337-r1 APPROVE (2026-11-13).
- Known issues:
  - BG1337 (Medium): sprint.py lane land commits a lane at its worktree's old base and rebases afterwards, so the hook judges it against code main has already fixed - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1337: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1337 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1339: sprint.py lane accept has no path for a round-2 verdict given against a rejoinder brief, so the orchestrator records it by hand

- What changed: sprint.py lane accept has no path for a round-2 verdict given against a rejoinder brief, so the orchestrator records it by hand (2 points).
- Criteria passed:
  - AC1: Given a unit with a recorded round-1 REJECT and a round-2 verdict file its rejoinder brief named, when `sprint lane accept --unit <id> --verdict <file> --reviewer <same seat>` runs, then it records the verdict against the rejoinder brief's fingerprint and, on APPROVE, runs the criteria and moves the unit. Fails on: the verdict bound to the round-1 saved brief. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_a_round_two_verdict_records_against_its_rejoinder_brief`
- Independent review: qa-seat-BG1339-r1 APPROVE (2026-11-13).
- Known issues:
  - BG1339 (Medium): sprint.py lane accept has no path for a round-2 verdict given against a rejoinder brief, so the orchestrator records it by hand - not-stop-ship, ruled by orchestrator.
  - BG1405 (Low): Nothing pins critic's 'live rows' filter, the carried-refusal wording or the stacked-criterion naming, and the BG1339 rejoinder path guards are untested - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1339: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1339 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1344: A unit whose tests must run under a temporary HOME cannot be built in a worktree lane, and the lane brief offers no other path

- What changed: A unit whose tests must run under a temporary HOME cannot be built in a worktree lane, and the lane brief offers no other path (2 points).
- Criteria passed:
  - AC1: Given a unit that declares it needs a temporary HOME, when its lane brief is printed, then the brief names the non-worktree path (a main-checkout lane run last, with other commits held) instead of the worktree lane. Fails on: a worktree lane briefed for it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py::BriefHandoverTests::test_a_home_isolated_unit_is_briefed_for_the_main_checkout`
- Independent review: qa-seat-BG1344-r1 APPROVE (2026-11-13).
- Known issues:
  - BG1344 (Medium): A unit whose tests must run under a temporary HOME cannot be built in a worktree lane, and the lane brief offers no other path - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1344: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1344 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1330: 15 of RPT0028's 19 units have no priced cost of their own, because only a hand-run `lane return --agent` prices a unit, and the close counts no gap

- What changed: 15 of RPT0028's 19 units have no priced cost of their own, because only a hand-run `lane return --agent` prices a unit, and the close counts no gap (3 points).
- Criteria passed:
  - AC1: Given a lane worktree named `agent-<id>` whose builder transcript is readable in a fixture harness store (CLAUDE_CONFIG_DIR set to a temporary directory), when `sprint lane land` lands it, then each landed unit has a return recorded and priced from that transcript, as `lane return --agent <id>` records one; beside it, a worktree whose transcript cannot be read still lands and names the unit as unpriced. Fails on: a landed unit with a readable transcript left with no priced return. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandPricesTheBuilderTests`
  - AC2: Given a closed run whose report reads a unit as NOT MEASURED for want of a priced return, the close counts that unit among the gaps it reports and names it. Fails on: the close reporting 0 gaps while a unit's cost is not measured. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::UnpricedUnitIsAGapTests`
- Independent review: qa-seat-BG1330-r1 APPROVE (2026-11-13).
- Known issues:
  - BG1410 (Low): BG1330's re-pointed clean-run test lost its known-issues assertion, unpriced_units' filter is untested, and lane land with no run open names lane return's --tokens flag - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1330: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1330 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1279: A close after `sprint reopen` keeps the first close's token reading, so the reopened work is missing from the report's cost

- What changed: A close after `sprint reopen` keeps the first close's token reading, so the reopened work is missing from the report's cost (2 points).
- Criteria passed:
  - AC1: Given a run closed, then reopened with `sprint reopen`, with meter readings dated after the first close, when it is closed again, then the report's Priced cost covers the run's whole window from its open to the second close, and the report says the meter was re-read after a reopen. Fails on: the second report carrying the first close's figure unchanged. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ReopenedRunCostTests`
- Independent review: qa-seat-BG1279-r1 APPROVE (2026-11-13).
- Known issues:
  - unpriced (close gap): BG1279: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1279 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1331: A Grok request of 200k tokens or more is priced at xAI's short-context rate, so the meter understates the requests that cost a consuming project most

- What changed: A Grok request of 200k tokens or more is priced at xAI's short-context rate, so the meter understates the requests that cost a consuming project most (3 points).
- Criteria passed:
  - AC1: templates/model-prices.json records xAI's Long context rates beside the Short context ones for grok-4.7, grok-4.6, grok-4.5 and their xai/ ids, dated and sourced: input 4.00, cached input 1.00 (0.60 for grok-4.5) and output 12.00 US dollars per million tokens, for a request whose prompt is 200k tokens or more, billed at that rate for all its tokens (docs.x.ai/developers/pricing, Text API, read 2026-11-12). Fails on: a long-context rate missing, or differing from those figures. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::GrokLongContextRatesTests`
  - AC2: Where a reading carries each request's prompt size, a Grok request of 200k prompt tokens or more is priced at the long-context rate for all its tokens and one under 200k at the short rate; where a reading carries only a session total, its Grok dollar figure is labelled a lower bound rather than presented as exact. Fails on: a request of 200k or more priced at the short rate, or a session-total Grok figure shown without the lower-bound label. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::GrokLongContextPricingTests`
- Independent review: qa-seat-BG1331-r1 APPROVE (2026-11-13).
- Known issues:
  - unpriced (close gap): BG1331: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1331 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1305: The Cursor meter drops the model the Cursor usage hook records on each ledger line, so a run metered from the ledger is never priced by model, and Composer pricing reaches only `sprint lane run` readings

- What changed: The Cursor meter drops the model the Cursor usage hook records on each ledger line, so a run metered from the ledger is never priced by model, and Composer pricing reaches only `sprint lane run` readings (2 points).
- Criteria passed:
  - AC1: Given a Cursor usage ledger whose lines name a priced model, when the Cursor meter reads it, the reading carries a per-model split in the shape the other meters produce and `lib/prices.py` prices it; beside it, a ledger line naming no model still reads as not priced. Fails on: a model-bearing ledger read as not priced, or a line with no model priced. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::LedgerCarriesTheModelTests`
- Independent review: qa-seat-BG1305-r1 APPROVE (2026-11-12).
- Known issues:
  - unpriced (close gap): BG1305: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1305 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1371: The retro's dollar line prices only the meter's split, so the retro and the report state different dollars for one run

- What changed: The retro's dollar line prices only the meter's split, so the retro and the report state different dollars for one run (1 point).
- Criteria passed:
  - AC1: Given the case the review named, the behaviour matches the documented rule. Fails on: the case as the review probed it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::Run10FollowUpTests`
- Independent review: qa-seat-BG1371-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1371 (Medium): The retro's dollar line prices only the meter's split, so the retro and the report state different dollars for one run - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1371: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1371 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG0965: retro.py validate ignores '## Actions raised' in a Keep/Stop/Try retro, so it reports '0 findings, all dispositioned' over rows it never read

- What changed: retro.py validate ignores '## Actions raised' in a Keep/Stop/Try retro, so it reports '0 findings, all dispositioned' over rows it never read (2 points).
- Criteria passed:
  - AC1: A three-line retro whose Actions raised table holds an undecided row fails validate, naming the row Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_three_line_actions.py -k undecided_row_fails`
  - AC2: validate and dispose report the same findings for a three-line retro that carries an Actions raised table Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_three_line_actions.py -k validate_and_dispose_agree`
- Independent review: qa-seat-BG0965-r1 APPROVE (2026-11-12).
- Known issues:
  - unpriced (close gap): BG0965: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG0965 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1340: critic.py brief --rejoinder with no file reads only the unit's current delivery, so a unit carried across runs has no ledger rejoinder

- What changed: critic.py brief --rejoinder with no file reads only the unit's current delivery, so a unit carried across runs has no ledger rejoinder (2 points).
- Criteria passed:
  - AC1: Given a carried unit whose seat's REJECT is in an earlier delivery and unanswered, when `critic.py brief --unit <id> --seat <seat> --rejoinder` runs, then it quotes that REJECT. Fails on: the refusal naming no unanswered REJECT while sprint plan reports one. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_a_carried_units_earlier_reject_is_quoted`
- Independent review: qa-seat-BG1340-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1340 (Medium): critic.py brief --rejoinder with no file reads only the unit's current delivery, so a unit carried across runs has no ledger rejoinder - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1340: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1340 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1341: reconcile.blocking_findings lists a REJECT row's RULINGS item as a blocking defect in a lane brief's file history

- What changed: reconcile.blocking_findings lists a REJECT row's RULINGS item as a blocking defect in a lane brief's file history (1 point).
- Criteria passed:
  - AC1: Given a REJECT row carrying a RULINGS item beside one blocking finding, when `blocking_findings` reads it, then only the blocking finding is listed. Fails on: the rulings text listed as a defect. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::BlockingFindingsTests::test_a_rulings_item_is_not_a_blocking_finding`
- Independent review: qa-seat-BG1341-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1341 (Medium): reconcile.blocking_findings lists a REJECT row's RULINGS item as a blocking defect in a lane brief's file history - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1341: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1341 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG0990: reconcile's field sync reads a '·'-joined metadata run to end of line, writing 'P2 · **Type:** ...' into index cells and dropping the later fields

- What changed: reconcile's field sync reads a '·'-joined metadata run to end of line, writing 'P2 · **Type:** ...' into index cells and dropping the later fields (2 points).
- Criteria passed:
  - AC1: A metadata line joining several fields with `·` projects each field to its own value, identical to `sdlc_md.extract_field` for every field on the line Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile_inline_field_run.py -k each_field_projected`
  - AC2: `reconcile apply` over an index whose cells hold a swallowed run rewrites them to the single field value Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile_inline_field_run.py -k apply_repairs_swallowed_cells`
- Independent review: qa-seat-BG0990-r1 APPROVE (2026-11-12).
- Known issues:
  - unpriced (close gap): BG0990: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG0990 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1343: Moving a story to Ready does not refuse a criterion with several stacked Verify lines, which then turns main red at StackedVerifierTests

- What changed: Moving a story to Ready does not refuse a criterion with several stacked Verify lines, which then turns main red at StackedVerifierTests (1 point).
- Criteria passed:
  - AC1: Given a story whose criterion has two Verify lines, when it is moved to Ready, then the move is refused naming the criterion. Fails on: Ready reached with stacked verifiers. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ReadyGateTests::test_stacked_verifiers_refuse_ready`
- Independent review: qa-seat-BG1343-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1343 (Medium): Moving a story to Ready does not refuse a criterion with several stacked Verify lines, which then turns main red at StackedVerifierTests - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1343: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1343 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1333: A project set up before 6.3.0 never learns to integrate on trunk: project upgrade leaves its AGENTS.md without the rule, and no hygiene check notices

- What changed: A project set up before 6.3.0 never learns to integrate on trunk: project upgrade leaves its AGENTS.md without the rule, and no hygiene check notices (3 points).
- Criteria passed:
  - AC1: Given a project whose AGENTS.md lacks the integration rule that templates/agent-instructions.md carries ('Integrate continuously. ...'), when `validate.py check` runs, then it reports a hygiene finding naming AGENTS.md and the exact line to add, read from the template; beside it, a project whose AGENTS.md carries the line, and a project with no AGENTS.md, report no such finding. Fails on: no finding for the missing line, or a finding on a project that carries it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::IntegrationRuleHygieneTests`
  - AC2: Given the same project, when `project_upgrade.py` runs, its report names the missing integration rule with the exact line to add, and AGENTS.md is left byte for byte unchanged. Fails on: an upgrade report silent on the rule, or AGENTS.md rewritten. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::IntegrationRuleReportTests`
- Independent review: qa-seat-BG1333-r1 APPROVE (2026-11-12).
- Known issues:
  - BG1402 (Low): The BG1333 integration rule counts as present if 'Integrate continuously' appears anywhere in AGENTS.md, so a sentence negating it passes - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1333: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1333 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1261: After BG1245 a hard kill of `sprint.py`'s process group no longer reaches a running lane, whose CLI runs on in the worktree with no timeout over it

- What changed: After BG1245 a hard kill of `sprint.py`'s process group no longer reaches a running lane, whose CLI runs on in the worktree with no timeout over it (2 points).
- Criteria passed:
  - AC1: Given `sprint.py lane run` running a unit whose fake CLI sleeps and then stages a file, when `sprint.py` itself is killed with SIGKILL, then the lane's CLI and every process it started are gone within the watchdog's grace and the file is never staged; beside it, a control run in which `sprint.py` lives lets the same CLI finish and stage its file. Fails on: the CLI or a child still running, or the file staged, after `sprint.py` died. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneDiesWithItsCallerTests`
- Independent review: qa-seat-BG1261-r1 APPROVE (2026-11-13).
- Known issues:
  - BG1401 (Low): BG1190's unpinned reap and BG1262/BG1261's watchdog SIGKILL after its grace are covered by no test - not-stop-ship, ruled by orchestrator.
  - BG1414 (Low): The BG1262/BG1261 changelog headline is too broad, the help line reads as SIGTERM-first for every death of sprint.py, and lanes._reaping sends SIGKILL first - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1261: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1261 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1262: `sprint lane run` kills a timed-out lane with no `SIGTERM` first, leaving `index.lock` behind, and leaves four further lane rules unhandled or unpinned

- What changed: `sprint lane run` kills a timed-out lane with no `SIGTERM` first, leaving `index.lock` behind, and leaves four further lane rules unhandled or unpinned (3 points).
- Criteria passed:
  - AC1: Given a lane that times out while its CLI's child traps SIGTERM and writes a marker, when the timeout fires, then the group is sent SIGTERM first and the marker is written before any SIGKILL; and a timed-out lane whose CLI loops `git add` leaves no `index.lock` in its worktree. Fails on: SIGKILL with no SIGTERM first, or the grace mutant `deadline = time.monotonic() - 1` passing the test. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneTimeoutTermsFirstTests`
  - AC2: Given a CLI that exits 0 while a background child it started is still running, when the lane records, then that child is killed before the staged set is read and no file it would stage is in the index afterwards. Fails on: a file staged after the record. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneLeftoverChildTests`
  - AC3: Given a CLI that cannot be executed (a shebang naming a missing interpreter), `lane run` refuses naming the CLI path and the unit is no longer in flight; and the test module's PATH holds only the fake bin and the system directories git and Python need, so a missing fake fails in setUp rather than reaching a real harness CLI. Fails on: a traceback with the unit left in flight, or the operator's PATH reaching a test. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneExecFailureTests`
- Independent review: qa-seat-BG1262-r1 APPROVE (2026-11-13).
- Known issues:
  - BG1401 (Low): BG1190's unpinned reap and BG1262/BG1261's watchdog SIGKILL after its grace are covered by no test - not-stop-ship, ruled by orchestrator.
  - BG1414 (Low): The BG1262/BG1261 changelog headline is too broad, the help line reads as SIGTERM-first for every death of sprint.py, and lanes._reaping sends SIGKILL first - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1262: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1262 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1372: GitHub reports 5 Dependabot alerts on the default branch (1 high, 2 moderate, 2 low)

- What changed: GitHub reports 5 Dependabot alerts on the default branch (1 high, 2 moderate, 2 low) (2 points).
- Criteria passed: none ticked.
- Criteria not ticked: AC1.
- Independent review: qa-seat-BG1372-r1 APPROVE (2026-11-13).
- Known issues:
  - BG1372 (Medium): GitHub reports 5 Dependabot alerts on the default branch (1 high, 2 moderate, 2 low) - not-stop-ship, ruled by orchestrator.
  - unpriced (close gap): BG1372: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1372 --agent A`.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0472, on 2026-11-14 over fingerprint 82ced251b004932d.
- Report: RPT0030.

### BG1019: artifact.py retitle refuses in every consuming project: it loads tools/check_links.py from the operated repo or the skill's own source checkout, and an installed skill has neither

- What changed: artifact.py retitle refuses in every consuming project: it loads tools/check_links.py from the operated repo or the skill's own source checkout, and an installed skill has neither (3 points).
- Criteria passed:
  - AC1: retitle succeeds in a consuming project with the installed skill layout and no tools/`check_links.py`, still rewriting inbound references Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retitle_installed_layout.py::RetitleInstalledLayoutTests::test_retitle_rewrites_inbound_links_without_tools_check_links`
- Independent review: qa-seat-BG1019-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### BG1268: No shipped command writes a row to `sdlc-studio/lessons.jsonl`, the store the lane brief reads, and its build digest is full at five, so the next build lesson drops one US1132's AC3 needs

- What changed: No shipped command writes a row to `sdlc-studio/lessons.jsonl`, the store the lane brief reads, and its build digest is full at five, so the next build lesson drops one US1132's AC3 needs (2 points).
- Criteria passed:
  - AC1: Given a project store `sdlc-studio/lessons.jsonl`, when `lessons.py class-add --class <name> --rule <text> --behaviour <text> --phase build [--phase review] --source <text>` runs, then one validated active row is appended with the next `LC-` code, the run id when a run is open, and the source; `lessons.py classes` lists it; and the lane brief's build digest can select it. Fails on: the row written to the `lessons/` registry instead of the store, a missing code, or a malformed row the digest skips. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_class_add.py::ClassAddTests::test_a_class_row_reaches_the_store_and_the_digest`
  - AC2: Given a store that already holds a class of that name, or a `--phase` the digest does not know, when `class-add` runs, then it refuses with the reason, exits non-zero and leaves the store byte-identical; a positive control with a new class and a known phase succeeds. Fails on: a duplicate class appended, an unknown phase stored, or a partial write. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_class_add.py::ClassAddTests::test_a_duplicate_class_or_unknown_phase_is_refused`
  - AC3: Given `help/lessons.md` and `reference-scripts.md`, when a reader looks for how to record a class outside a retro, then both name `class-add` beside `retro.py extract` (which records a `[new: class]` Try item at the close) and say the lane brief reads the store, not the `lessons/` registry. Fails on: either page silent on the store, or `class-add` documented with flags the parser does not take. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_class_add.py::ClassAddDocsTests`
- Independent review: qa-seat-BG1268-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### BG1391: The report's Dollar cost row does not carry the lower-bound label for a Grok figure priced from a session total, so a lower bound reads as exact

- What changed: The report's Dollar cost row does not carry the lower-bound label for a Grok figure priced from a session total, so a lower bound reads as exact (2 points).
- Criteria passed:
  - AC1: Given a Grok session total merged into a booked split, when the report's Dollar cost row prints, then it carries the lower-bound label. Fails on: the row showing the figure unlabelled. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_grok_lower_bound_row.py::GrokLowerBoundRowTests`
- Independent review: qa-seat-BG1391-r1 APPROVE (2026-11-15).
- Known issues:
  - BG1391 (Medium): The report's Dollar cost row does not carry the lower-bound label for a Grok figure priced from a session total, so a lower bound reads as exact - not-stop-ship, ruled by orchestrator.
  - BG1428 (Low): The per-unit dollars cell prices a unit's Grok agent read from a session total with no lower-bound label, and BG1391's changelog says the label holds wherever models are summed - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### BG1393: A project that replaces grok-4.7 under pricing.models loses grok-4.7@long-context from its own table, so run_state.usd prices only part of the reading

- What changed: A project that replaces grok-4.7 under pricing.models loses grok-4.7@long-context from its own table, so run_state.usd prices only part of the reading (2 points).
- Criteria passed:
  - AC1: Given a project pricing.models entry replacing grok-4.7, when a Cursor ledger holds long-context responses, then `run_state.usd` prices the whole reading or says plainly it cannot. Fails on: a part priced and the long-context id listed as unpriced. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_replaced_grok_long_context.py::ReplacedGrokLongContextTests`
- Independent review: qa-seat-BG1393-r1 APPROVE (2026-11-15).
- Known issues:
  - BG1393 (Medium): A project that replaces grok-4.7 under pricing.models loses grok-4.7@long-context from its own table, so run_state.usd prices only part of the reading - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### BG1394: A re-close after a reopen whose meter cannot be read drops the first window, takes no reading and says nothing on the page

- What changed: A re-close after a reopen whose meter cannot be read drops the first window, takes no reading and says nothing on the page (2 points).
- Criteria passed:
  - AC1: Given a reopened run whose meter cannot be read at the second close, when the close runs, then the first window is kept and the page says the second reading is missing. Fails on: the window dropped silently. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_re_close_unreadable_meter.py::ReCloseUnreadableMeterTests`
- Independent review: qa-seat-BG1394-r1 APPROVE (2026-11-15).
- Known issues:
  - BG1394 (Medium): A re-close after a reopen whose meter cannot be read drops the first window, takes no reading and says nothing on the page - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### BG1397: sprint lane return --agent refuses a multi-unit lane, so a multi-unit lane's builder is never priced per unit

- What changed: sprint lane return --agent refuses a multi-unit lane, so a multi-unit lane's builder is never priced per unit (2 points).
- Criteria passed:
  - AC1: Given a lane of three units and one agent total, when `sprint lane return --agent` runs, then the total is split by points, each unit is priced and the page says it was split. Fails on: the refusal. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_multi_unit_lane_split.py::MultiUnitLaneSplitTests`
- Independent review: qa-seat-BG1397-r1 APPROVE (2026-11-15).
- Known issues:
  - BG1397 (Medium): sprint lane return --agent refuses a multi-unit lane, so a multi-unit lane's builder is never priced per unit - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### BG1425: BG1420 did not converge in review: round 2 REJECT findings

- What changed: BG1420 did not converge in review: round 2 REJECT findings (3 points).
- Criteria passed:
  - AC1: Given a caller whose SIGTERM handler drains its own pool with `pool.shutdown(wait=True)`, when a one-worker verifier pool running `shell sleep 3`, `shell echo one` and `shell echo two` receives SIGTERM, then the process exits within a bound (the stop grace plus a few seconds), the queued verifiers are refused, and a second SIGTERM is not needed. Run the caller as a child process with its own timeout so a hang fails the test rather than the suite. Fails on: an unbounded `_RELAY_SETTLED.wait()` (verify_ac.py:649), a bound longer than the driver's timeout, or a handler that raises between the relay count's increment and its `try:` leaving the event clear (the round-2 remark; the same bound closes it). Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_relay_bounded_wait.py::DrainingHandlerTests`
  - AC2: BG1420 AC1 still passes: Given main after the fix, when the five named tests run, then each passes: BareArtefactReadSweepTests::`test_no_bare_artefact_body_reads_in_scanners`, PoolEdgeTests::`test_an_interrupt_cancels_the_stories_still_queued` (only the three running stories ever start), LockfileTests::`test_package_json_was_not_widened_to_clear_the_advisory`, ReleaseNotesTests::`test_every_changed_behaviour_names_what_to_do` and FrozenNotesTests::`test_filing_a_finding_reddens_no_test.` Fails on: any of the five red, or a test deleted or skipped to make it pass. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py::BareArtefactReadSweepTests::test_no_bare_artefact_body_reads_in_scanners .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py::PoolEdgeTests::test_an_interrupt_cancels_the_stories_still_queued tools/tests/test_dependency_advisories.py::LockfileTests::test_package_json_was_not_widened_to_clear_the_advisory tools/tests/test_lean_release_notes_v63.py::ReleaseNotesTests::test_every_changed_behaviour_names_what_to_do tools/tests/test_lean_release_notes.py::FrozenNotesTests::test_filing_a_finding_reddens_no_test`
- Independent review: qa-seat-BG1425-r1 APPROVE (2026-11-15).
- Known issues:
  - BG1425 (Medium): BG1420 did not converge in review: round 2 REJECT findings - not-stop-ship, ruled by orchestrator.
  - BG1431 (Low): Two release-notes tests take 120 s to over 300 s under load, past verify_ac's default per-verifier timeout, so BG1420's and BG1425's recorded runs fail on time unless given --timeout - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US0992: A consumer parses the report of record against a published, versioned annex

- What changed: A consumer parses the report of record against a published, versioned annex (5 points).
- Criteria passed:
  - AC1: Given a report filed by `sprint close` in a fixture run carrying every section (metered cost, a refusal log, a not-measured close item, a ruling and a waiver), when the conformance test parses the annex's catalogue tables by their headings and reads the report against them, then every envelope key, section key, figure key and row key the report holds is in those tables, and every section the tables mark always emitted is present. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py::ReportAnnexTests::test_a_filed_report_conforms_to_the_annex`
  - AC2: Given two fixture runs closed through `sprint close`, one with a refusal log and a not-measured close item and one with neither, when the sections each filed page carries are compared with the annex's catalogue, then their union equals the catalogue, and the sections the bare run lacks are exactly those the catalogue marks conditional, each naming the condition under which it is absent. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py::ReportAnnexTests::test_the_section_catalogue_matches_what_the_builder_emits`
  - AC3: Given the four schema-1 pages this repository holds (RPT0002-RPT0005), copied into a fixture, when the test reads their section and envelope keys and runs `sprint_report.py check` on each, then the union of their sections equals the annex's schema-1 catalogue with `waivers` marked optional and `window_end` an optional envelope key, and each check answers that the page stands as filed, as the annex says. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py::ReportAnnexTests::test_schema_one_is_documented_as_it_stands`
- Independent review: qa-seat-US0992-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US0993: A consumer recomputes a report's fingerprint from the annex alone

- What changed: A consumer recomputes a report's fingerprint from the annex alone (2 points).
- Criteria passed:
  - AC1: Given the reference implementation the annex states for the schema-2 fingerprint, when the test extracts it and runs it with `python3 -I` from a temporary working directory with no skill scripts on the path, over a report filed by `sprint close` in a fixture and over every committed schema-2 page (RPT0006 onward, found by glob so each later page joins the check), then it returns the fingerprint each page records. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_fingerprint.py::FingerprintAnnexTests::test_the_annex_procedure_recomputes_filed_fingerprints_in_isolation`
  - AC2: Given the annex's lists of figures and sections left out of the digest, when they are compared with OUTSIDE_THE_DIGEST and SECTIONS_OUTSIDE_THE_DIGEST, then they are equal, and both the annex and reference-sprint.md state that the signature block, the generation time and each figure's source are not signed. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_fingerprint.py::FingerprintAnnexTests::test_the_annex_exclusions_match_the_code`
- Independent review: qa-seat-US0993-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US0994: A consumer reads the committed run record, awaiting signature, sealed or stopped, against the annex

- What changed: A consumer reads the committed run record, awaiting signature, sealed or stopped, against the annex (3 points).
- Criteria passed:
  - AC1: Given a run closed with `sprint close` and signed with `sprint sign` in a fixture, when the conformance test reads the tracked record after each command, then every key the annex contracts for that state is present with its documented type, and a key the annex does not contract is tolerated rather than failed. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_run_record.py::RunRecordAnnexTests::test_the_tracked_record_holds_its_contracted_keys`
  - AC2: Given three tracked records from fixture runs, one closed, one closed and signed, and one closed and then ended with `sprint stop`, when the test evaluates the annex's own awaiting-signature predicate, extracted from the annex, on each record, then it reads only the first as awaiting, and `sprint plan --write` in a fresh clone opens the next run over all three (D0503, US1290; restated in run sixteen, when the plan stopped refusing over an awaiting record). Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_run_record.py::RunRecordAnnexTests::test_the_annex_awaiting_rule_reads_only_the_signable_record`
- Independent review: qa-seat-US0994-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US0995: A consumer reads the lesson class store, the evidence logs and the four ledgers against the annex

- What changed: A consumer reads the lesson class store, the evidence logs and the four ledgers against the annex (3 points).
- Criteria passed:
  - AC1: Given an actuals line written by `telemetry.py record`, a forecast line written by `telemetry.py forecast`, an audit-cost line written by `audit_cost.py record` and a lesson row written by `retro.py extract`, when the conformance test reads each against the annex, then every field each holds is documented and every field the annex marks required is present. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_ledgers.py::LedgerAnnexTests::test_written_lines_conform_to_the_annex`
  - AC2: Given the critic, velocity, decisions and deploy ledgers as `critic.py record`, `retro.py accuracy --write`, `decisions.py add` and `deploy.py record` create them in a fixture, when their header rows are compared with the annex's table layouts, then each column list is equal, in order, the critic table's with nine columns. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_ledgers.py::LedgerAnnexTests::test_ledger_headers_match_the_annex`
- Independent review: qa-seat-US0995-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US0996: Each committed report and run record states the evidence-schema version it was written under

- What changed: Each committed report and run record states the evidence-schema version it was written under (2 points).
- Criteria passed:
  - AC1: Given a run closed and signed through `sprint close` and `sprint sign` and committed, when a fresh clone reads the filed report JSON and the tracked run record, then each carries `evidence_schema` equal to the version the annex masthead states. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_report_and_run_record_carry_the_annex_version`
  - AC2: Given a run closed while the annex version is 1.0 and signed after the version moves to 1.1, when the sealed run record is read, then it carries 1.0, the version its page was stamped with. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_the_record_keeps_its_pages_version_across_an_upgrade`
  - AC3: Given a signed page filed before the stamp and a page filed after it, when `sprint_report check` runs on each, then both read VALID and only the later page carries `evidence_schema`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_an_unstamped_page_still_checks_valid`
  - AC4: Given the annex's compatibility policy, when the test reads it, then the masthead version parses as major.minor and the policy states that an added field is a minor bump, a removed or renamed field is a major bump carrying a migration note in the annex, and a consumer must tolerate unknown keys. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_the_annex_states_its_compatibility_policy`
- Independent review: qa-seat-US0996-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US0999: A delegated agent's token total records the model that spent it

- What changed: A delegated agent's token total records the model that spent it (2 points).
- Criteria passed:
  - AC1: Given an open run, when a builder's total is returned with `sprint lane return --units <unit> --tokens 120000 --model claude-sonnet-4-6` and another is recorded with `retro.py accuracy --delegated-tokens 80000 --delegated-model claude-opus-5-5`, then each delegated entry on the run record carries the model it was given and each command prints it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_tokens_model.py::DelegatedModelTests::test_both_recorders_store_the_model`
  - AC2: Given a delegated total returned with no `--model`, when the entry is recorded, then it carries no model and nothing is filled in for it, and a page filed for that run reads exactly as it would before this change. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_tokens_model.py::DelegatedModelTests::test_a_missing_model_is_never_guessed`
- Independent review: qa-seat-US0999-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US1150: The plan records a priced, dollar and wall-clock forecast beside tokens and minutes

- What changed: The plan records a priced, dollar and wall-clock forecast beside tokens and minutes (3 points).
- Criteria passed:
  - AC1: Given a project whose velocity history holds three or more runs with a priced-per-point figure, when `sprint plan --write` opens a run, then the run's plan snapshot records a `priced_per_point` rate with its source naming the runs it was fitted from, and each unit's row carries a priced forecast of its points times that rate. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanPricedRateTests::test_plan_write_records_priced_rate_with_source`
  - AC2: Given a priced forecast and a price table listing the planned model, when the plan is written, then the snapshot records a dollar forecast equal to the priced forecast times that model's input price per million, naming the table's effective date. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanDollarForecastTests::test_dollar_forecast_names_model_and_effective_date`
  - AC3: Given delivered runs with a recorded elapsed span and points, when the plan is written, then it records a wall-clock forecast in minutes from points per elapsed hour, kept apart from the active-minutes forecast. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanWallClockForecastTests::test_wall_clock_forecast_is_separate_from_active_minutes`
  - AC4: Given a project with no measured rate for a row, when `sprint plan` runs (preview or --write), then it prints one line per unforecast row reading 'not forecast: <reason>' and exits 0. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanUnforecastRowTests::test_plan_names_each_row_it_cannot_forecast`
- Independent review: qa-seat-US1150-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US1151: The report's Estimates table shows forecast, actual and ratio for every cost row

- What changed: The report's Estimates table shows forecast, actual and ratio for every cost row (3 points).
- Criteria passed:
  - AC1: Given a run whose snapshot holds a priced forecast, when `sprint_report.py show` renders its page, then the Priced cost and Priced per point rows show forecast, actual and an actual-over-forecast ratio. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_estimates_cost_rows.py::PricedRowsTests::test_priced_rows_show_forecast_actual_ratio`
  - AC2: Given a snapshot with a dollar forecast, when the page renders, then Dollar cost and Dollars per point show a ratio, and the basis names the price table's effective date. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_estimates_cost_rows.py::DollarRowsTests::test_dollar_rows_show_ratio_and_price_date`
  - AC3: Given a wall-clock forecast, when the page renders, then the Wall-clock span row shows its forecast and ratio, and the Minutes row is still never compared with the span. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_estimates_cost_rows.py::SpanRowTests::test_span_row_has_ratio_and_minutes_row_unchanged`
  - AC4: Given a run with no rate for a row, when the page renders, then that row reads 'not forecast: <reason>' (never bare), the page states beside the table that forecasts are descriptive, and a page filed before this change re-derives with its old rows unchanged. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_estimates_cost_rows.py::UnforecastRowTests::test_reason_text_descriptive_note_and_old_page_replay`
- Independent review: qa-seat-US1151-r1 APPROVE (2026-11-15).
- Known issues:
  - BG1443 (Low): Four cost-forecast behaviours are correct but unpinned, the Minutes row's reason reads 'not forecast: not measured', and US1151's criteria name a command that never renders the rows - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US1152: A declared component map gives each story a risk and compliance class at refine

- What changed: A declared component map gives each story a risk and compliance class at refine (3 points).
- Criteria passed:
  - AC1: Given a project whose committed config declares a component map (path prefixes to a class: standard, elevated or high), when `refine apply` mints a story, then the story carries a Risk-class field equal to the highest class among the components its Affects touch. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_risk_class_map.py::RefineStampsClassTests::test_story_takes_highest_class_of_its_affects`
  - AC2: Given no component map, when `refine apply` runs, then every story is standard, one line says no map is declared, and the command exits 0. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_risk_class_map.py::NoMapTests::test_no_map_means_standard_one_line_exit_zero`
  - AC3: Given a map entry naming an unknown class, when `refine apply` runs, then it reports the entry in one line, treats it as standard, and still mints the stories. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_risk_class_map.py::BadMapTests::test_unknown_class_is_reported_not_refused`
- Independent review: qa-seat-US1152-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US1153: sprint plan shows each unit's class and flags a unit that touches a higher class than its tag

- What changed: sprint plan shows each unit's class and flags a unit that touches a higher class than its tag (2 points).
- Criteria passed:
  - AC1: Given a map and a batch, when `sprint plan` runs, then the plan lists each unit's class and the second review seat each high-class unit will need. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag.py::PlanShowsClassTests::test_plan_lists_class_per_unit_and_second_seat`
  - AC2: Given a unit tagged standard whose Affects touch a high-class component, when `sprint plan` runs, then it flags the unit, naming the file, the component and both classes, and exits 0 with no per-unit sign-off asked. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag.py::PlanFlagsHigherClassTests::test_flag_names_file_component_and_classes_and_never_refuses`
  - AC3: Given no component map, when `sprint plan` runs, then it prints exactly one line saying every unit is standard, and nothing refuses. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_risk_flag.py::PlanNoMapTests::test_no_map_prints_one_line`
- Independent review: qa-seat-US1153-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US1154: A high-class unit gets a second independent review seat, and the retro reports what that seat found

- What changed: A high-class unit gets a second independent review seat, and the retro reports what that seat found (3 points).
- Criteria passed:
  - AC1: Given a high-class unit, when `critic.py brief --unit <id> --seat <second seat>` runs, then the brief is the shipped seat brief (charter, Affects scope, criteria) and names the unit's class and that it is the second independent seat. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py::SecondSeatBriefTests::test_brief_names_class_and_second_seat_role`
  - AC2: Given a high-class unit with two seats' delivery verdicts in the ledger, when `retro.py` composes the run's retro, then it reports, per second seat, the units where it rejected or raised issues after the first seat approved. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py::RetroSecondSeatYieldTests::test_retro_reports_second_seat_catches`
  - AC3: Given a high-class unit with no second-seat verdict, or a run whose second seats caught nothing, when the retro is composed, then it says so in one line each and nothing refuses. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py::RetroSecondSeatNothingTests::test_missing_and_empty_yield_are_stated_not_refused`
- Independent review: qa-seat-US1154-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US1155: One command writes a release's evidence pack from committed records

- What changed: One command writes a release's evidence pack from committed records (3 points).
- Criteria passed:
  - AC1: Given committed signed reports, when `release_cut.py evidence-pack --version 6.4.0 --reports RPT0001,RPT0002` runs, then it writes one markdown pack under sdlc-studio/reports/ listing each delivered unit of those reports, and exits 0. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::BuildPackTests::test_pack_lists_delivered_units_of_signed_reports`
  - AC2: Given an unsigned or unknown report, when the command runs, then it exits non-zero naming the report and writes no pack. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::BuildPackTests::test_unsigned_or_unknown_report_is_refused`
  - AC3: Given an uncommitted edit to a unit's file or the verdict ledger, when the pack is built, then the pack reads the committed copy and is byte-identical to one built before the edit. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::CommittedOnlyTests::test_working_tree_edits_do_not_change_the_pack`
  - AC4: Given a delivered unit, when the pack is built, then its entry states what changed (title and points), which criteria passed (its ticked criteria and their Verify lines) and who reviewed it independently (the latest verdict per seat whose reviewer differs from the author). Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::UnitEntryTests::test_entry_has_change_criteria_and_independent_reviewer`
- Independent review: qa-seat-US1155-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US1156: Each change in the pack states what is known wrong and names the accountable person, never the agent

- What changed: Each change in the pack states what is known wrong and names the accountable person, never the agent (2 points).
- Criteria passed:
  - AC1: Given a signed report whose known-issues rows name open findings, when the pack is built, then each change lists the known issues that name it, and the pack carries the report's remaining known issues in one list. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::KnownWrongTests::test_known_issues_listed_per_change_and_for_the_release`
  - AC2: Given a signed report, when the pack is built, then each change names the accountable person recorded on that report's signature, with the signing date. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::AccountableTests::test_each_change_names_the_signing_principal`
  - AC3: Given a report whose signature principal is blank or reads as an agent (for example 'the agent' or 'agent-<id>'), when the pack is built, then the command exits non-zero and no pack names the agent as accountable. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::AccountableTests::test_agent_or_blank_principal_is_refused`
- Independent review: qa-seat-US1156-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0475, on 2026-11-15 over fingerprint 41f6af509193a323.
- Report: RPT0031.

### US1059: A persona's brief carries its own live learnings, capped and ranked, and never another persona's

- What changed: A persona's brief carries its own live learnings, capped and ranked, and never another persona's (5 points).
- Criteria passed:
  - AC1: Given qa memory holding seven approved learnings (one with a 5,000-character body), one proposed and one past its Review-by, and product memory holding two approved, when `critic.py brief --unit US0001 --seat qa` runs, then the brief carries five qa learnings and none of product's, omits the proposed and the expired one, says two more were withheld by the cap and one is past its horizon, and carries the long learning as its id, title and a gist of at most 200 characters. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_the_review_brief_carries_its_own_seats_capped_bounded_learnings`
  - AC2: Given two approved qa learnings, an older one whose evidence cites US0005 (Affects `scripts/a.py`) and a newer one citing US0006 (Affects `docs/x.md`), when `critic.py brief --unit US0001` runs for a unit whose Affects include `scripts/a.py`, with `personas.memory.inject_max: 1`, then the older, relevant one is carried. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_a_learning_whose_evidence_shares_the_units_files_outranks_a_newer_one`
  - AC3: Given the same memory files, when `persona_resolve.py resolve --seat qa --render build` and `resolve-consult --role qa` run, then each carries qa's learnings in a block labelled with its render and neither carries another seat's. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_every_persona_resolve_framing_carries_its_own_seats_learnings`
  - AC4: Given a qa memory file that cannot be parsed, and a project with no qa memory file, when `critic.py brief --seat qa` runs on each, then the first brief says qa's learnings could not be read, naming the file, and the second says none are recorded. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_unreadable_and_absent_memory_are_told_apart`
- Independent review: qa-seat-US1059-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1061: A unit's review record names the seat that built it, so an author's repairs can be scored

- What changed: A unit's review record names the seat that built it, so an author's repairs can be scored (3 points).
- Criteria passed:
  - AC1: Given a project whose engineering card is held by Dani Okafor and whose qa card by Sam Eriksson, when `sprint.py lane brief --units US0001` runs and then `critic.py brief --unit US0001 --seat product` runs, then the lane brief names Dani Okafor (engineering) as the building seat and the review footer's record command carries `--author "Dani Okafor (engineering)"`, and after `lane brief --units US0002 --seat qa` the footer for US0002 carries `--author "Sam Eriksson (qa)"`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py::ReviewAuthorSeatTests::test_the_record_command_names_the_seat_that_built_the_unit`
  - AC2: Given a project that declares seats, when `critic.py record --unit US0001 --verdict APPROVE --reviewer "Lena Marsh (product)" --author "engineering-seat build worker"` runs, then the row is written and stderr names the `<holder> (<role>)` form the author lacks, and with `--author "Dani Okafor (engineering)"` nothing is printed about the author. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py::ReviewAuthorSeatTests::test_a_seatless_author_is_named_and_recorded`
  - AC3: Given a brief for `--seat qa` on a project where qa's card is held by Sam Eriksson, when `critic.py brief --unit US0001 --seat qa` runs, then the footer's record command carries `--reviewer "Sam Eriksson (qa)"` (the US1030 AC3 shape), and with an explicit `--seat engineering` it carries the engineering holder, so a recorded Reviewer cell always names its seat in the form `critic.recorded_seat` reads. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_review_author_seat.py::ReviewAuthorSeatTests::test_the_footer_names_the_seat_as_reviewer`
- Independent review: qa-seat-US1061-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1062: retro.py seats scores each seat on its own verdicts and authored units from the ledger

- What changed: retro.py seats scores each seat on its own verdicts and authored units from the ledger (5 points).
- Criteria passed:
  - AC1: Given a retro whose Batch is US0001 and US0002, and ledger rows by `Sam Eriksson (qa) re-checking the product finding` (REJECT, then APPROVE, on US0001), `Lena Marsh (product)` (APPROVE on US0002) and `independent-critic` (APPROVE on US0002), when `retro.py seats --id RETRO0001` runs, then it lists qa with one REJECT, one APPROVE and US0001 converging in two rounds, product with one APPROVE, and says one of four verdict rows names no seat, naming independent-critic. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py::SeatEvidenceTests::test_each_seat_is_scored_on_the_rows_that_name_it`
  - AC2: Given US0001 approved in round 1 by `Lena Marsh (product)` and rejected in round 2 by `Sam Eriksson (qa)` with a blocking finding citing `scripts/a.py:12` that no round-1 finding cites, and US0002 rejected by qa in round 1 and again in round 2 with a new finding, when `retro.py seats` runs, then product's record lists the US0001 finding as found only after its approval, saying whether `scripts/a.py` changed between the two rows' dates or that it cannot be told, and qa is charged nothing for US0002's round-2 finding. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py::SeatEvidenceTests::test_only_an_earlier_approval_is_charged_with_a_later_rounds_defect`
  - AC3: Given a qa APPROVE later superseded with `critic.py supersede` as recorded against the wrong reviewer, when `retro.py seats` runs, then the row is left out of qa's verdicts and listed as recorded in error with the supersession's reason. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py::SeatEvidenceTests::test_a_superseded_row_is_recorded_in_error_not_overturned`
  - AC4: Given US0001 whose Author cell is `Dani Okafor (engineering)`, rejected twice and then approved, when `retro.py seats` runs, then engineering's record lists US0001 as a unit it built, converging in three rounds, with each round's blocking findings. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py::SeatEvidenceTests::test_an_authoring_seat_is_scored_on_the_rounds_its_units_took`
- Independent review: qa-seat-US1062-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1064: The seat record charges a later bug to the approval that missed it, by the narrow rule

- What changed: The seat record charges a later bug to the approval that missed it, by the narrow rule (5 points).
- Criteria passed:
  - AC1: Given RETRO0001 dated 2026-10-01 and RETRO0002 dated 2026-10-08, US0001 approved by `Lena Marsh (product)` on 2026-09-20 with Affects `scripts/a.py`, and bugs dated within the window: BG0002 (cites US0001, affects scripts/a.py), BG0003 (cites US0001, affects only docs/x.md), BG0004 (affects scripts/a.py, cites nothing), BG0006 (cites US0001 and four other ids, affects scripts/a.py), BG0007 ('US0001 did not converge in review'), and BG0005 dated 2026-09-25, when `retro.py seats --id RETRO0002` runs, then product's record lists BG0002 alone as a miss, with its basis. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_later_bug_is_charged_by_the_narrow_rule`
  - AC2: Given product's APPROVE of US0001 carrying a non-blocking finding and BG0008, in the window, whose Evidence names US0001's product review, when `retro.py seats` runs, then product's record lists BG0008 as approved over its own finding, not as a miss. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_bug_the_approver_raised_reads_approved_over_its_own_finding`
  - AC3: Given US0003 approved by qa in an earlier run and BG0009, in this retro's window, charged to it by the narrow rule, when `retro.py seats --id RETRO0002` runs on a batch qa did not review, then qa appears in the record with BG0009. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_seat_outside_the_batch_is_charged_its_misses`
- Independent review: qa-seat-US1064-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1065: Each seat writes its learning in its own words from a brief carrying its record, and it is recorded as proposed

- What changed: Each seat writes its learning in its own words from a brief carrying its record, and it is recorded as proposed (3 points).
- Criteria passed:
  - AC1: Given a retro whose batch qa and product reviewed, when `persona_memory.py learn-brief --persona qa --retro RETRO0002` runs, then the brief frames the qa card, carries qa's record from `retro.py seats` with each adverse item and its key and qa's live learnings, says the learning cannot change the card's Non-Negotiables or Authority, and names the file to write, and no line of product's record appears. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_propose.py::ProposeLearningTests::test_the_learning_brief_carries_only_its_own_seats_record`
  - AC2: Given a file holding the qa seat's learning, when `persona_memory.py propose --persona qa --retro RETRO0002 --from-file <path>` runs, then qa's memory gains one entry with State proposed, Run the retro's run, the body the file's text verbatim and Evidence the ids `retro.py seats` lists for qa rather than ids the file names. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_propose.py::ProposeLearningTests::test_a_proposal_keeps_the_seats_words_and_the_ledgers_evidence`
  - AC3: Given a seat with no record in the retro (no verdict, no unit built, no adverse item), or a second proposal while qa's first for that run is still proposed, when `persona_memory.py propose` runs, then it exits 2 and memory is unchanged, and once the first is rejected a new proposal is accepted. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_propose.py::ProposeLearningTests::test_one_open_proposal_per_seat_and_run`
- Independent review: qa-seat-US1065-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1066: Another seat approves or rejects each proposed learning against its evidence and its card

- What changed: Another seat approves or rejects each proposed learning against its evidence and its card (5 points).
- Criteria passed:
  - AC1: Given a proposed qa learning M-0001, when `persona_memory.py approve --id M-0001 --reviewer "Lena Marsh (product)" --addresses round:US0001r2` runs, then it reads approved with Approved-by, the date and the item it addresses, while `--reviewer "Kit Devane (qa)"` exits 2 naming that a seat never approves its own learning, whoever holds it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py::ApproveLearningTests::test_another_seat_approves_and_the_same_seat_is_refused`
  - AC2: Given qa's record listing adverse items round:US0001r2 and bug:BG0002, when `approve` runs with `--addresses bug:BG0099`, with no `--addresses`, and with `--addresses none --reason "keeps a habit that held"`, then the first two exit 2 naming the listed items and the third is recorded with its reason. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py::ApproveLearningTests::test_an_approval_names_what_the_learning_addresses_or_says_why_not`
  - AC3: Given a proposed learning, when `persona_memory.py approve-brief --id M-0001 --seat product` runs, then it carries the learning verbatim, qa's adverse items with their keys, the qa card's Non-Negotiables and Authority sections, the question whether the learning contradicts or loosens them, the product card to adopt and the approve and reject commands, while `--seat qa` exits 2. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py::ApproveLearningTests::test_the_approval_brief_carries_the_evidence_and_the_subject_card`
  - AC4: Given a proposed qa learning, when `approve --id M-0001 --reviewer "Lena Marsh (product)" --reject --reason ...` runs, then it reads rejected with the reviewer and reason, and `critic.py brief --seat qa` does not carry it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py::ApproveLearningTests::test_a_rejected_learning_never_reaches_the_brief`
- Independent review: qa-seat-US1066-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1067: The close lists every learning about to go live on the retro, with what it addresses and who approved it

- What changed: The close lists every learning about to go live on the retro, with what it addresses and who approved it (5 points).
- Criteria passed:
  - AC1: Given qa's learning proposed in this run and approved by `Lena Marsh (product)`, and a product learning written with `persona_memory.py add` and approved by qa outside any retro, when `sprint.py close` runs, then the retro gains a delimited `## Persona learnings` block listing both with their approvers and addressed items, each entry is stamped Listed-in with the run, and the run record names both ids. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_persona_learnings.py::RetroLearningsTests::test_the_close_lists_every_approved_learning_not_yet_live`
  - AC2: Given a batch where product has a later-bug item and no learning, qa has no adverse item and no learning, and two of five verdict rows name no seat, when `sprint.py close` runs, then the close output and the block name product as a seat with adverse evidence and no learning, do not name qa, and say two of five verdict rows name no seat, with the close's outcome unchanged. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_persona_learnings.py::RetroLearningsTests::test_the_close_names_unlearned_adverse_evidence_and_unattributed_rows`
  - AC3: Given that block and prose the author wrote around it, when the close runs again after another learning is approved, then the block is replaced in place, lists all three, and the author's prose is byte-identical. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_persona_learnings.py::RetroLearningsTests::test_a_reclose_refreshes_the_block_in_place`
- Independent review: qa-seat-US1067-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1068: A learning reaches a brief only once a signed close has listed it, and one the operator strikes at the signature never does

- What changed: A learning reaches a brief only once a signed close has listed it, and one the operator strikes at the signature never does (5 points).
- Criteria passed:
  - AC1: Given a closed run that listed M-0001 (qa) and M-0002 (product), when `sprint.py sign --principal <operator> --strike M-0001 --strike-reason ...` runs, then the run is sealed with M-0001 recorded as struck by the principal with the date and reason, the next qa brief does not carry M-0001, the next product brief carries M-0002, and `persona_memory.py list` shows M-0001 struck. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_a_struck_learning_never_reaches_the_brief`
  - AC2: Given an approved learning listed by a run that is closed but not signed, when `critic.py brief --seat qa` runs, then the learning is not carried and the brief says one approved learning awaits its run's signature. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_a_learning_of_an_unsigned_run_is_held`
  - AC3: Given a signed run that listed M-0002, when `sprint.py reopen --reason ...` runs, then the next product brief holds M-0002, and after the close and `sprint.py sign --strike M-0002` it is struck and never carried. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_a_reopened_run_holds_its_learnings_until_resigned`
  - AC4: Given `--strike` naming a learning another run listed and an id no memory file holds, when `sprint.py sign` runs, then it exits 2 naming both, nothing is sealed and no memory file changes. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_a_bad_strike_refuses_the_seal_and_writes_nothing`
- Independent review: qa-seat-US1068-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1157: A bug records that it escaped to production, the release it shipped in and the unit that let it through

- What changed: A bug records that it escaped to production, the release it shipped in and the unit that let it through (3 points).
- Criteria passed:
  - AC1: Given a project with a tag v1.0.0, when `artifact.py new bug --escaped --shipped-in v1.0.0 --escaped-via US0001 ...` (and the same through `file_finding.py bug --escaped ...`) runs, then the bug header carries `Escaped: yes`, `Shipped-in: v1.0.0` and `Escaped-via: US0001`, and the Root Cause section is scaffolded in the body. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_bug_escape_fields.py::BugEscapeFieldTests::test_an_escaped_bug_carries_release_and_unit`
  - AC2: Given `--escaped` with no `--shipped-in`, a `--shipped-in` naming no tag or release in the project, or an `--escaped-via` naming no unit on disk, when the command runs, then it exits 2 naming the missing or unresolved value and writes no file; a bug without `--escaped` is created exactly as before. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_bug_escape_fields.py::BugEscapeFieldTests::test_an_escape_without_a_resolvable_release_or_unit_is_refused`
  - AC3: Given an escaped bug, when `transition.py` sets it Fixed, then it is refused until the Root Cause section holds text other than the scaffold. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_bug_escape_fields.py::BugEscapeFieldTests::test_an_escaped_bug_is_not_fixed_with_an_empty_root_cause`
- Independent review: qa-seat-US1157-r1 APPROVE (2026-11-15).
- Known issues:
  - BG1486 (Low): US1157's AC1 names a file_finding.py bug verb that does not exist, so the plan's registry advice reads it as a new verb - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1158: escape.py trace proposes the unit and verdict that let an escaped bug through, from the release and the files the fix touches

- What changed: escape.py trace proposes the unit and verdict that let an escaped bug through, from the release and the files the fix touches (3 points).
- Criteria passed:
  - AC1: Given an escaped bug with `Shipped-in: v1.0.0` whose Affects name `scripts/a.py`, and two units that shipped in v1.0.0 (US0001 with Affects `scripts/a.py` approved by `Lena Marsh (product)`, US0002 with Affects `docs/x.md`), when `escape.py trace --bug BG0001` runs, then it lists US0001 first with the shared file and its recorded verdict and seat, and does not list US0002. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceTests::test_the_unit_sharing_the_fixed_file_is_proposed_with_its_verdict`
  - AC2: Given `escape.py trace --bug BG0001 --confirm US0001`, then the bug's `Escaped-via` is set to US0001 and the verdict row (round, reviewer seat) is stamped as `Escaped-verdict`; given a unit that shares no file with the fix, then `--confirm` refuses naming the unit, and no unit proposed is written without `--confirm`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceTests::test_a_confirmed_unit_is_recorded_and_an_unrelated_one_refused`
  - AC3: Given a bug with no `Shipped-in`, or a release that tags no unit, when `escape.py trace` runs, then it exits 2 naming what is missing and proposes nothing. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceTests::test_a_bug_with_no_release_or_an_empty_release_proposes_nothing`
- Independent review: qa-seat-US1158-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### US1159: An escape's root cause becomes a failure class that carries the files it applies to

- What changed: An escape's root cause becomes a failure class that carries the files it applies to (2 points).
- Criteria passed:
  - AC1: Given a confirmed escaped bug BG0001 with a filled Root Cause and Affects `scripts/a.py`, when `escape.py to-class --bug BG0001 --class "a boundary never pinned" --rule ... --behaviour ...` runs, then `lessons.py class-add` (BG1268) is called and `sdlc-studio/lessons.jsonl` gains one row inject `build` and `review`, whose `evidence` cites BG0001 and the unit, and whose `files` holds the bug's Affects paths. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_class.py::EscapeClassTests::test_a_root_cause_becomes_a_class_row_carrying_its_files`
  - AC2: Given a bug that is not escaped, one whose Root Cause is the scaffold, and a class name already in the store, when `escape.py to-class` runs, then each exits 2 naming its reason and the store is unchanged. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_class.py::EscapeClassTests::test_an_unescaped_empty_or_duplicate_class_is_refused`
- Independent review: qa-seat-US1159-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0479, on 2026-11-15 over fingerprint dfa4679614cfeb00.
- Report: RPT0032.

### BG0947: reference-outputs.md terminal-status table contradicts sdlc_md.TERMINAL_STATUS

- What changed: reference-outputs.md terminal-status table contradicts sdlc_md.TERMINAL_STATUS (2 points).
- Criteria passed:
  - AC1: Given `sdlc_md.STATUS_VOCAB` and `sdlc_md.TERMINAL_STATUS`, when the Status Vocabulary table in reference-outputs.md is parsed, then it has exactly one row per type in STATUS_VOCAB (issue and charter included) and each row's allowed and terminal sets equal the code's. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py::StatusVocabDocTests::test_the_table_matches_the_code`
  - AC2: Given a copy of the corrected table with one terminal status removed from one row, when the same comparison runs on it, then it fails naming that type and that status. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py::StatusVocabDocTests::test_a_divergence_names_the_type_and_status`
- Independent review: qa-seat-BG0947-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### BG0998: The story template ships Verified no, which verify_ac treats as an authored miss

- What changed: The story template ships Verified no, which verify_ac treats as an authored miss (2 points).
- Criteria passed:
  - AC1: Given a Draft story whose criterion is copied from templates/core/story.md with the Verify placeholder replaced by `shell true`, when `verify_ac.py run` runs on it, then it reports pass=1 fail=0 and stamps the criterion `Verified: yes`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_story_template_verified.py::StoryTemplateVerifiedTests::test_a_criterion_copied_from_the_template_is_stamped_yes`
  - AC2: Given reference-story.md and reference-verify.md, when their guidance on a new criterion is read, then neither tells an author to write `Verified: no` until reconcile runs, and both say a new criterion carries no Verified line and that `Verified: no` is a recorded miss the runner does not overwrite. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_story_template_verified.py::StoryTemplateVerifiedTests::test_the_references_say_a_new_criterion_carries_no_verified_line`
  - AC3: Given an existing criterion carrying a hand-written bare `Verified: no` and a passing selector, when `verify_ac.py run` runs, then it still reports fail=1 and leaves the line as written (BG0733's sticky rule holds). Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_story_template_verified.py::StoryTemplateVerifiedTests::test_a_hand_written_bare_no_stays_sticky`
- Independent review: qa-seat-BG0998-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### BG1260: `init run` and `init guided` exit 1 and leave a half-built project when `.claude` is a regular file, which the base initialised cleanly

- What changed: `init run` and `init guided` exit 1 and leave a half-built project when `.claude` is a regular file, which the base initialised cleanly (2 points).
- Criteria passed:
  - AC1: Given a fixture whose `.claude` is an empty regular file, when `init.py run` runs on it, then it exits 0, writes AGENTS.md, CLAUDE.md and every later scaffold file (the decisions log among them), and reports each agent definition under `.claude/agents/` as skipped with its OSError reason. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_init_claude_not_a_directory.py::ClaudeIsAFileTests::test_init_run_finishes_and_names_each_skipped_definition`
  - AC2: Given the same fixture, when `init.py guided` drafts its agents stage, then the stage writes the instruction files, exits 0 and names each skipped definition with its reason; with `.claude` absent (the control) both definitions are written. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_init_claude_not_a_directory.py::ClaudeIsAFileTests::test_init_guided_agents_stage_finishes`
  - AC3: Given an agent definition at `.claude/agents/sdlc-builder.md` that cannot be read and an AGENTS.md without the doctrine, when the agents stage runs, then it prints no 'so the doctrine check can read it' directive for the definition and still offers the doctrine. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_init_claude_not_a_directory.py::ClaudeIsAFileTests::test_an_unreadable_definition_neither_misdirects_nor_hides_the_doctrine_offer`
- Independent review: qa-seat-BG1260-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### BG1395: BG1005 makes a criterion whose pytest target partly skips on the running machine read red, including Done criteria the release gate re-runs, and the count is not measured

- What changed: BG1005 makes a criterion whose pytest target partly skips on the running machine read red, including Done criteria the release gate re-runs, and the count is not measured (2 points).
- Criteria passed:
  - AC1: Given two stories, one whose pytest Verify target passes with one test skipped and one whose target fails outright, when `verify_ac.py run` covers both, then each story's summary line and the total line report the partial skip as its own count (for example `partly_skipped=1`) beside `fail=2`, and name the partly-skipped criterion. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py::PartialSkipReleaseGateCountTests::test_the_summary_counts_partial_skips_apart_from_other_failures`
  - AC2: Given a target whose every selected test is skipped and a target that runs clean with no skip, when the same run covers them, then neither adds to the partial-skip count, and the all-skipped target keeps its own vacuous verdict. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py::PartialSkipReleaseGateCountTests::test_an_all_skipped_or_clean_target_is_not_counted`
- Independent review: qa-seat-BG1395-r1 APPROVE (2026-11-15).
- Known issues:
  - BG1395 (Medium): BG1005 makes a criterion whose pytest target partly skips on the running machine read red, including Done criteria the release gate re-runs, and the count is not measured - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### BG1396: A Verify line with its own -q makes pytest run at -qq with no summary, so a partial skip is stamped pass, and -s and an unpinned _PYTEST_SKIP_NODE add edge cases

- What changed: A Verify line with its own -q makes pytest run at -qq with no summary, so a partial skip is stamped pass, and -s and an unpinned _PYTEST_SKIP_NODE add edge cases (2 points).
- Criteria passed:
  - AC1: Given a Verify line `pytest <file> -q` whose target has one passing and one skipped test, and another whose target is entirely skipped, when `verify_ac.py run` runs them, then neither criterion is stamped yes: the first fails naming the skipped test and the second gets the all-skipped verdict. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py::QuietFlagSkipReadTests::test_a_q_on_the_verify_line_still_reads_the_skips`
  - AC2: Given a Verify line with `-s` whose passing test prints a line shaped like a pytest summary (`1 passed, 1 skipped in 0.01s`), when it runs, then the criterion passes. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py::QuietFlagSkipReadTests::test_a_summary_like_line_under_s_is_not_read_as_a_skip`
  - AC3: Given a run report holding `SKIPPED path::Class::test - reason` lines, when the partial-skip verdict is built, then it names each as `path::Class::test (reason)`. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py::QuietFlagSkipReadTests::test_a_skip_node_line_names_its_test`
- Independent review: qa-seat-BG1396-r1 APPROVE (2026-11-15).
- Known issues:
  - BG1396 (Medium): A Verify line with its own -q makes pytest run at -qq with no summary, so a partial skip is stamped pass, and -s and an unpinned _PYTEST_SKIP_NODE add edge cases - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### US1160: `sprint_report.py evidence` renders the signed reports of record as one evidence table, and `--check` names a page that has drifted from them

- What changed: `sprint_report.py evidence` renders the signed reports of record as one evidence table, and `--check` names a page that has drifted from them (3 points).
- Criteria passed:
  - AC1: Given a fixture of signed reports of record (one achieved, one partial with a verdict note, one holding a Dollars per point row and one without, two signed reports for the same run, and one unsigned report), when `sprint_report.py evidence --out <page>` runs, then the table between the page's generated markers has one row per run from that run's latest signed report, showing the goal verdict, a partial verdict's note, dollars per point where the report holds it and 'not recorded' where it does not, and the hours from `generated_at` to `signature.signed_at`; the unsigned report is left out. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_one_row_per_signed_run_from_its_latest_report`
  - AC2: Given a page with hand-written text outside its markers, when the verb regenerates it, then that text is left byte for byte, and every figure inside the markers traces to a named field of a committed report. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_hand_text_is_kept_and_every_figure_is_a_report_field`
  - AC3: Given a page whose table differs from the reports it names (a hand-edited cell), when `sprint_report.py evidence --out <page> --check` runs, then it exits 1 naming the run that differs; given a report signed after the newest report the page names, it exits 0 and prints that the run is not yet on the page. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_check_names_a_drifted_run_and_only_notes_a_newer_report`
  - AC4: Given the new verb and its flags, when the command registries are read, then `docgen.py surface --check` is clean, `sprint_report.NON_CEREMONY_VERBS` lists `evidence`, command-audit.md judges `--out` and `--check`, and the `### sprint_report.py` section of reference-scripts-domain.md names the verb. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_the_verb_is_in_every_registry_a_new_verb_implies`
- Independent review: qa-seat-US1160-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### US1161: docs/evidence.md is generated from this repository's signed reports and explains a partial verdict, the wait for a signature and how to regenerate it

- What changed: docs/evidence.md is generated from this repository's signed reports and explains a partial verdict, the wait for a signature and how to regenerate it (2 points).
- Criteria passed:
  - AC1: Given this repository's committed reports, when `sprint_report.py evidence --out docs/evidence.md --check` runs, then it exits 0, and the page names the newest report it covers. Verify: `pytest tools/tests/test_evidence_page_committed.py::CommittedEvidencePageTests::test_the_committed_page_matches_the_reports`
  - AC2: Given docs/evidence.md, when its hand-written part is read, then it has a section on what 'Judged partial' means and where its reason comes from, one on how the wait for a signature is measured (report built to report signed), and one naming the command that regenerates the page, and every link in them resolves to an existing file and heading. Verify: `pytest tools/tests/test_evidence_page_committed.py::CommittedEvidencePageTests::test_the_page_explains_partial_verdicts_waiting_and_regeneration`
- Independent review: qa-seat-US1161-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### US1162: docs/engineering-leaders.md explains change approval, separation of duties, the signed report and cost in dollars a point, each claim linked to the mechanism that enforces it

- What changed: docs/engineering-leaders.md explains change approval, separation of duties, the signed report and cost in dollars a point, each claim linked to the mechanism that enforces it (3 points).
- Criteria passed:
  - AC1: Given docs/engineering-leaders.md, when its sections are read, then it has one each for change approval, separation of duties (author, reviewer and signer), the signed report, and cost in dollars a point, and the page is at most 1,200 words as `wc -w` counts them. Verify: `pytest tools/tests/test_engineering_leaders_page.py::EngineeringLeadersPageTests::test_the_four_sections_are_present_and_the_page_is_short`
  - AC2: Given each paragraph and bullet in those four sections, when its links are read, then each carries at least one link to a script, a reference page heading or a committed record in this repository, and every link resolves to an existing file and, where anchored, an existing heading. Verify: `pytest tools/tests/test_engineering_leaders_page.py::EngineeringLeadersPageTests::test_every_claim_links_a_mechanism_that_exists`
  - AC3: Given the cost section, when it states a dollar figure, then the same paragraph links the committed report that holds it. Verify: `pytest tools/tests/test_engineering_leaders_page.py::EngineeringLeadersPageTests::test_every_dollar_figure_cites_its_report`
- Independent review: qa-seat-US1162-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### US1163: SUPPORT.md says what support exists, where to ask and what is not supported, naming only channels the repository has

- What changed: SUPPORT.md says what support exists, where to ask and what is not supported, naming only channels the repository has (2 points).
- Criteria passed:
  - AC1: Given SUPPORT.md, when its sections are read, then it has one for what support exists, one for where to ask and one for what is not supported. Verify: `pytest tools/tests/test_support_page.py::SupportPageTests::test_the_three_sections_are_present`
  - AC2: Given every channel SUPPORT.md names, when each is checked against the repository, then a GitHub link names only the repository's issues or its security policy (backed by .github/ISSUE_TEMPLATE/ and SECURITY.md), each issue template it names exists under .github/ISSUE_TEMPLATE/, and it gives no install command of its own but links docs/INSTALL.md. Verify: `pytest tools/tests/test_support_page.py::SupportPageTests::test_every_channel_named_exists`
  - AC3: Given tools/check_links.py, when it scans the root docs, then SUPPORT.md is among them and a SUPPORT.md link to a missing file is reported. Verify: `pytest tools/tests/test_check_links.py::RootDocsTests::test_support_md_is_a_root_doc`
- Independent review: qa-seat-US1163-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### US1165: A project sets builder and reviewer reasoning effort; the plan stamps it on each unit, the lane brief names it, and a reviewer below its builder is refused without a recorded decision

- What changed: A project sets builder and reviewer reasoning effort; the plan stamps it on each unit, the lane brief names it, and a reviewer below its builder is refused without a recorded decision (3 points).
- Criteria passed:
  - AC1: Given a project that sets no `routing.effort`, when `sprint.py plan` runs and a lane brief is printed, then each unit's plan row carries `effort: {builder: inherit, reviewer: inherit}` and the brief says to dispatch at the session's own effort, which is today's behaviour. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py::EffortSettingTests::test_the_default_inherits_the_session_effort`
  - AC2: Given `routing.effort: {builder: low, reviewer: medium}`, when `sprint.py plan` runs and `sprint.py lane brief --units <id>` is printed, then the plan row carries both values and the brief names the effort to dispatch the builder at and the effort for its reviewer. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py::EffortSettingTests::test_a_set_effort_reaches_the_plan_and_the_lane_brief`
  - AC3: Given a reviewer effort below its builder's (builder high, reviewer low), when `sprint.py plan` runs, then it refuses naming both values, unless `routing.effort.reviewer_below_builder` names a decision id present in sdlc-studio/decisions.md, in which case it plans and prints that id. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py::EffortSettingTests::test_a_reviewer_below_its_builder_is_refused_without_a_decision`
  - AC4: Given an effort value outside inherit, low, medium, high, xhigh and max, when `sprint.py plan` runs, then it refuses naming the key and the allowed values. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_effort_setting.py::EffortSettingTests::test_an_unknown_effort_value_is_refused`
- Independent review: qa-seat-US1165-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### US1166: Each run's report of record states the effort each builder and reviewer was dispatched at, read from the run record

- What changed: Each run's report of record states the effort each builder and reviewer was dispatched at, read from the run record (3 points).
- Criteria passed:
  - AC1: Given a run record whose plan stamped builder low and reviewer medium on its units, when `sprint_report.py build` composes the report of record and it is rendered, then the cost section carries an effort figure per role sourced from the run record, and the page shows it. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py::ReportEffortTests::test_the_report_states_each_roles_effort_from_the_run_record`
  - AC2: Given a run record planned before the setting existed (no effort stamped), when the report is built, then the effort figure reads NOT MEASURED with its reason, never inherit and never blank. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py::ReportEffortTests::test_a_run_without_effort_reads_not_measured`
  - AC3: Given reference-evidence-schema.md, when its report-of-record figure table is read, then it lists the new figure key with its section and meaning, and a run whose units carried two effort values reports each value with its unit count. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py::ReportEffortTests::test_the_annex_documents_the_figure_and_mixed_effort_is_counted`
- Independent review: qa-seat-US1166-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### US1167: A test module or class marked `# test-selection: sweep` joins every commit's selection, within a 30-second budget

- What changed: A test module or class marked `# test-selection: sweep` joins every commit's selection, within a 30-second budget (3 points).
- Criteria passed:
  - AC1: Given a repository with a module carrying `# test-selection: sweep` that imports nothing changed, when `gate.select_tests` answers for a change to scripts/sprint.py, and again for a docs-only change, then the sweep is selected in both beside whatever the change reaches, and the reason names it as a sweep. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sweep_selection.py::SweepSelectionTests::test_a_sweep_joins_every_commits_selection`
  - AC2: Given a module where only one class is the sweep, when the marker names that class, then the selection carries that class's node id and not the whole module. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sweep_selection.py::SweepSelectionTests::test_a_class_marker_selects_only_that_class`
  - AC3: Given this repository's markers, when they are read, then test_doc_claims, test_precommit_floor_pending, test_root_census, the test_skill_tests_env scrub sweep, the test_gitutil raw-git sweep (UnconfinedRawGitCallSweepTests) and the commit-hook hermeticity tests (HookInvocationHermeticityTests) are marked, tools/tests/test_test_census.py is not, and the marked set's recorded run times total at most 30 seconds, an unrecorded time being named rather than counted as zero. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_sweep_selection.py::SweepSelectionTests::test_the_repositorys_sweeps_are_marked_and_fit_the_budget`
- Independent review: qa-seat-US1167-r1 APPROVE (2026-11-16).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### US1169: sprint plan reports, per unit, every registry file its new script, verb or flag implies, and every page threshold it nears, that its Affects omits

- What changed: sprint plan reports, per unit, every registry file its new script, verb or flag implies, and every page threshold it nears, that its Affects omits (5 points).
- Criteria passed:
  - AC1: Given a unit whose Affects names a not-yet-existing `.claude/skills/sdlc-studio/scripts/<name>.py`, when `sprint.py plan` runs, then it reports each registry that new script implies and the Affects omits: sdlc-studio/reviews/root-census.md, a reference-scripts page for its `### <name>.py` heading, reference-scripts-surface.md, sdlc-studio/reviews/command-audit.md, and lib/surface.py when the script has no parser. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py::PlanRegistryAdvisoryTests::test_a_new_script_names_its_registries`
  - AC2: Given a unit whose criteria name `<script>.py <verb>` for a verb that script's parser does not expose, or a `--flag` it does not take, when the plan runs, then it reports reference-scripts-surface.md and sprint_report.py (NON_CEREMONY_VERBS) for the verb, command-audit.md for the flag, and scripts/tests/test_artifact.py when the flag is `--fields-file` or the script is a free-prose writer; a verb or flag the parser already has is not reported. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py::PlanRegistryAdvisoryTests::test_a_new_verb_or_flag_names_its_registries`
  - AC3: Given a unit whose Affects names a reference page within 20 lines below the 400-line reading-guide threshold, past 600 lines with no ALLOWLIST entry, or within 10 lines of its ALLOWLIST ceiling plus 5%, when the plan runs, then it reports the threshold, the page's size and the file to add (the regenerated guide, or tools/check_budgets.py). Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py::PlanRegistryAdvisoryTests::test_a_page_near_a_threshold_names_the_guide_or_ceiling`
  - AC4: Given the same units with the implied files in their Affects, and a consuming project whose tree has none of these registries, when the plan runs, then it reports nothing for them and never refuses the plan. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_registry_advisory.py::PlanRegistryAdvisoryTests::test_a_unit_naming_its_registries_or_a_consuming_project_is_clean`
- Independent review: qa-seat-US1169-r1 APPROVE (2026-11-16).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### BG1177: README's 6.2.0 line and the notes' theme heading say a reviewer judges only self-checked work, though the shipped default only reports a missing self-check

- What changed: README's 6.2.0 line and the notes' theme heading say a reviewer judges only self-checked work, though the shipped default only reports a missing self-check (1 point).
- Criteria passed:
  - AC1: Given docs/release-notes-v6.2.0.md, when its first theme bullet and its theme table row are read, then both say a review brief can require the author's own check first, and neither says a reviewer judges only self-checked work. Verify: `pytest tools/tests/test_self_check_claim_wording.py::SelfCheckClaimWordingTests::test_the_62_notes_say_a_brief_can_require_the_self_check`
  - AC2: Given README.md, when every line naming the author's self-check is read, then none says a reviewer judges only self-checked work. Verify: `pytest tools/tests/test_self_check_claim_wording.py::SelfCheckClaimWordingTests::test_the_readme_claims_no_enforced_self_check`
  - AC3: Given the renamed theme, when the 6.2 notes' lead test runs, then it passes with THEMES keyed on the new heading and the same four units. Verify: `pytest tools/tests/test_lean_release_notes_v62.py::ReleaseNotesTests::test_the_notes_lead_with_what_changed_for_you`
- Independent review: qa-seat-BG1177-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### US1164: README.md is about 1,500 words and opens with three routes in: evaluate, try and upgrade

- What changed: README.md is about 1,500 words and opens with three routes in: evaluate, try and upgrade (5 points).
- Criteria passed:
  - AC1: Given README.md, when its words are counted as `wc -w` counts them over the whole file, then there are at most 1,800. Verify: `pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_readme_is_at_most_1800_words`
  - AC2: Given README.md, when its first section after the badges is read, then it offers three routes in the order evaluate, try, upgrade, and each links pages that exist: evaluate to docs/engineering-leaders.md and docs/evidence.md, try to docs/INSTALL.md, upgrade to docs/existing-users.md. Verify: `pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_first_section_offers_three_routes_each_to_a_page_that_exists`
  - AC3: Given the routes section first, when the v6 lead test runs, then it reads the routes section where it read 'New in 6' and still finds the current release notes link, the loop link, the FAQ upgrade answer with `migrate --apply` and at least three routes to docs/existing-users.md, none calling v6 a drop-in. Verify: `pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_readme_leads_with_v6`
  - AC4: Given text cut from the README, when the tests that pin it run, then each passes where the text now lives, and none has had an assertion removed: the 6.3 cost paragraph, the coverage sentence, the Copilot row, the release-notes list and the bolded version declaration. Verify: `pytest tools/tests/test_lean_docs_v63.py::DocsV63Tests::test_the_public_pages_name_what_63_adds`
- Independent review: qa-seat-US1164-r1 APPROVE (2026-11-15).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 47fd8b167ed17112.
- Report: RPT0033.

### BG1493: The pre-push boundary gate does not run CI's green-run noise gate, so a push that passes locally turns GitHub Lint red

- What changed: The pre-push boundary gate does not run CI's green-run noise gate, so a push that passes locally turns GitHub Lint red (5 points).
- Criteria passed:
  - AC1: Given a fixture tree whose passing skill test prints more diagnostic lines than its module's budget in tools/test-noise-baseline.json, when the push boundary gate the pre-push hook runs judges it on this machine (`SDLC_GATE_LOCAL=1`), then the push is refused, naming the noise gate and the module over its budget. Fails on: the gate passing it, as it passed 7c64bf26 while GitHub Lint counted 112 diagnostic lines against a budget of 104 (BG1489). Verify: `pytest tools/tests/test_run_suite.py::PushNoiseGateTests::test_a_passing_test_leaking_above_budget_refuses_a_local_push`
  - AC2: Given the same fixture, when the push is judged on the gate host that `sdlc.gateHost` names (`tools/remote-gate.sh push`), then the host applies the same noise gate and refuses it the same way. Fails on: a host run that passes what a local run refuses. Verify: `pytest tools/tests/test_run_suite.py::PushNoiseGateTests::test_the_gate_host_applies_the_same_noise_gate`
  - AC3: Given the fixture within its budget, then the push gate passes it on both routes. Fails on: a refusal of a tree within its budget, or a check that reads the test runner's own output as noise and refuses every push. Verify: `pytest tools/tests/test_run_suite.py::PushNoiseGateTests::test_a_suite_within_budget_passes_the_push`
- Independent review: qa-seat-BG1493-r1 APPROVE (2026-11-16).
- Known issues:
  - BG1493 (High): The pre-push boundary gate does not run CI's green-run noise gate, so a push that passes locally turns GitHub Lint red - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 2c27b3912b625cf6.
- Report: RPT0034.

### BG1487: The README's opening says a person you can name reviews and approves each step, and it no longer points agents at llms.txt or AGENTS.md

- What changed: The README's opening says a person you can name reviews and approves each step, and it no longer points agents at llms.txt or AGENTS.md (1 point).
- Criteria passed:
  - AC1: Given README.md, when its opening paragraph is read, then it claims independent review per step and a named person's signature per run, and no named person approving each step. Fails on: the old sentence. Verify: `pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_opening_claims_independent_review_and_one_signature_per_run`
  - AC2: Given README.md, when an agent reads it, then one line links llms.txt and AGENTS.md. Fails on: neither linked. Verify: `pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_one_line_points_agents_at_llms_txt_and_agents_md`
- Independent review: qa-seat-BG1487-r1 APPROVE (2026-11-16).
- Known issues:
  - BG1487 (Medium): The README's opening says a person you can name reviews and approves each step, and it no longer points agents at llms.txt or AGENTS.md - not-stop-ship, ruled by orchestrator.
  - BG1496 (Low): BG1487's README-opening guard lets a reworded approval claim through, though its docstring says it never would - not-stop-ship, ruled by orchestrator.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 2c27b3912b625cf6.
- Report: RPT0034.

### BG1494: test_the_watchdog_sends_sigterm_and_waits_its_grace reads the SIGTERM marker the moment it exists, before the trap has written TERM, and fails CI intermittently

- What changed: test_the_watchdog_sends_sigterm_and_waits_its_grace reads the SIGTERM marker the moment it exists, before the trap has written TERM, and fails CI intermittently (1 point).
- Criteria passed:
  - AC1: Given the watchdog test, when the trap creates its marker before writing to it, then the test waits for the written content and passes. Fails on: a read of an empty marker failing the assertion. Verify: `pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py -k watchdog`
- Independent review: qa-seat-BG1494-r1 APPROVE (2026-11-16).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 2c27b3912b625cf6.
- Report: RPT0034.

### US1170: The v6.4 release notes lead with what changed for the person answering for the release

- What changed: The v6.4 release notes lead with what changed for the person answering for the release (5 points).
- Criteria passed:
  - AC1: Given docs/release-notes-v6.4.0.md, then it opens with a one-sentence headline naming 6.4.0 as the current release. Its first section leads with what changed for the person using it, under four themes, each naming the units that delivered it: a release carries evidence a change board accepts (US0992, US0993, US0994, US0995, US0996, US0997, US0998, US1155, US1156, US1160, US1161); a run's cost is forecast before it starts and set beside the actual, priced at each model's own rate (US0999, US1000, US1143, US1144, US1145, US1149, US1150, US1151, US1165, US1166); each review seat has a record, an escaped defect is traced to the approval that missed it, a seat learns only from a signed run, and a high-risk unit gets a second independent seat (US1011, US1012, US1013, US1015, US1058, US1059, US1061, US1062, US1064, US1065, US1066, US1067, US1068, US1152, US1153, US1154, US1157, US1158, US1159); and the front door is written for a head of engineering (US1146, US1147, US1148, US1162, US1163, US1164). It links the CHANGELOG section that lists every change. Fails on: the 6.3.0 notes with the version changed, or a theme with no unit named. Verify: `pytest tools/tests/test_lean_release_notes_v64.py::ReleaseNotesTests::test_the_notes_lead_with_what_changed_for_you`
  - AC2: Given the notes' section on changed behaviour, then it names each change a 6.3 user meets as a new refusal or a changed default, each beside what to do instead. Among them: `critic.py record --from-verdict` refuses a verdict file whose bytes an earlier row already carries, and records a verdict written by the context that edited the unit as a self-review (US1013, US1015); the delivery verdict ledger gains a `Source` column (US1012); `pricing.copilot_billing` defaults to `tokens`, so a plan still billed per premium request sets `requests` (US1145); the report cites the committed run record `sdlc-studio/reports/runs/<RUN-ID>.json`, not `.local/run-state.json`, for each figure it reads from that record (US0997); a pytest Verify line that ran only in part fails (BG1005, BG1395); and `transition.py set <story> Ready` refuses a criterion with more than one Verify line (BG1343). It states that no 6.4 fragment is filed under Breaking, Removed or Security. Fails on: a changed default named with no replacement, or a breaking change claimed that no fragment records. Verify: `pytest tools/tests/test_lean_release_notes_v64.py::ReleaseNotesTests::test_every_changed_behaviour_names_what_to_do`
  - AC3: Given the notes' 'Upgrading from 6.3' section, then it says to reinstall, gives `migrate` before `migrate --apply` as commands, and states what each reports for a 6.3 project, each statement checked by running it on a 6.3-shaped fixture. It names the configuration keys 6.4 adds (`risk.components`, `routing.effort`, `pricing.copilot_billing` and the `personas.memory` keys), each with the default `reference-config.md` states for it. Fails on: a step naming a command the shipped CLI refuses, `--apply` given before the dry run, or a default `reference-config.md` contradicts. Verify: `pytest tools/tests/test_lean_release_notes_v64.py::ReleaseNotesTests::test_the_63_upgrade_path_is_given`
  - AC4: Given every cost figure the notes state (priced tokens, dollars, dollars per point or points), then each names the signed report it is read from, and the test reads that figure back from the report's committed JSON under `sdlc-studio/reports/`. Fails on: a figure with no report named, or one the named report does not carry. Verify: `pytest tools/tests/test_lean_release_notes_v64.py::ReleaseNotesTests::test_every_cost_figure_names_its_signed_report`
  - AC5: Given the notes, then `tools/check_links.py` and `tools/lint-style.sh` pass and the notes carry exactly one `**v6.4.0 discloses N open defects: N Medium, N Low.**` line for `known_issues.py write --release 6.4.0` to fill. Fails on: a broken CHANGELOG anchor, an em dash, or a missing count line. Verify: `shell python3 tools/check_links.py && bash tools/lint-style.sh && test "$(grep -cE '^\*\*v6\.4\.0 discloses [0-9]+ open defects: [0-9]+ Medium, [0-9]+ Low\.\*\*$' docs/release-notes-v6.4.0.md)" = 1`
- Independent review: qa-seat-US1170-r1 APPROVE (2026-11-16).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 2c27b3912b625cf6.
- Report: RPT0034.

### US1171: The help, reference and public pages describe what 6.4 ships

- What changed: The help, reference and public pages describe what 6.4 ships (5 points).
- Criteria passed:
  - AC1: Given help/review.md's section on the review brief, then it says: the brief names the verdict file the reviewer writes under `sdlc-studio/reviews/verdicts/<unit>/` (US1011); `critic.py record --from-verdict` binds the row to that file's bytes in the ledger's `Source` column and refuses a file an earlier row already carries (US1012, US1013); a verdict written by the context that edited the unit is recorded as a self-review (US1015); `--rejoinder` with no value quotes the seat's unanswered REJECT from the ledger (US1016); the brief carries the seat's own live learnings (US1059); and a high-class unit's brief names whether its seat is the first or the second of two independent seats (US1154). Each statement is checked against the code it describes. Fails on: help/review.md as it stands at EP0314's grooming, which names none of them. Verify: `pytest tools/tests/test_lean_docs_v64.py::DocsV64Tests::test_the_review_help_names_the_verdict_file_and_the_second_seat`
  - AC2: Given help/retro.md and help/sprint.md, then help/retro.md names `retro.py seats` and the bugs it charges to the approval that missed them (US1062, US1064), the close's persona-learnings step and `sprint sign --strike` (US1067, US1068), and `escape.py trace` and `to-class` for an escaped bug (US1158, US1159), each linking the reference section that holds its detail; help/sprint.md names `routing.effort` (US1165) and `pricing.copilot_billing` (US1145), each with the default `reference-config.md` states for it. Fails on: a default `reference-config.md` contradicts, or a link to a heading that does not exist. Verify: `pytest tools/tests/test_lean_docs_v64.py::DocsV64Tests::test_the_retro_and_sprint_help_name_the_seat_record_and_the_new_keys`
  - AC3: Given README.md, llms.txt and docs/why-sdlc-studio.md, then README's 'New in' line names what 6.4 adds (an evidence pack per release a change board reads, each review seat's record with escaped defects traced to the approval that missed them, and a cost forecast set beside the actual); llms.txt links docs/engineering-leaders.md and docs/evidence.md; and the evidence section of why-sdlc-studio.md names the release evidence pack and links docs/evidence.md. Fails on: README naming no 6.4 feature, or llms.txt linking neither page. Verify: `pytest tools/tests/test_lean_docs_v64.py::DocsV64Tests::test_the_public_pages_name_what_64_adds`
  - AC4: Given docs/existing-users.md, then it has a 'From 6.3 to 6.4' section, first, above 'From 6.2 to 6.3'. It says: reinstall; whether a `migrate` step is owed, checked by running `migrate` on a 6.3-shaped fixture; what a 6.3 verdict ledger without the `Source` column needs, if anything; set `pricing.copilot_billing: requests` for a Copilot plan still billed per premium request; and the configuration keys 6.4 adds are optional, each with the default `reference-config.md` states for it. Fails on: a page whose newest section is still 'From 6.2 to 6.3'. Verify: `pytest tools/tests/test_lean_docs_v64.py::DocsV64Tests::test_existing_users_has_the_63_to_64_upgrade_path`
  - AC5: Given the changed pages, then `tools/check_links.py`, `tools/lint-style.sh` and `python3 tools/check_budgets.py` pass. Fails on: a broken anchor, an em dash, or a page over its budget. Verify: `shell python3 tools/check_links.py && bash tools/lint-style.sh && python3 tools/check_budgets.py`
- Independent review: qa-seat-US1171-r1 APPROVE (2026-11-16).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 2c27b3912b625cf6.
- Report: RPT0034.

### US1172: The PRD, TRD and TSD describe what 6.4 ships

- What changed: The PRD, TRD and TSD describe what 6.4 ships (5 points).
- Criteria passed:
  - AC1: Given the PRD's feature inventory and feature-flags table, then the inventory has a row each, naming its units, for: the evidence annex and the report's committed run record (US0992, US0993, US0994, US0995, US0996, US0997, US0998, US1001); the release evidence pack and the evidence page (US1155, US1156, US1160, US1161); escaped-defect tracing (US1157, US1158, US1159); each seat's record (US1061, US1062, US1064); persona learnings (US1058, US1059, US1065, US1066, US1067, US1068); the risk class and the second seat (US1152, US1153, US1154); the plan's cost forecast and dispatch effort (US1150, US1151, US1165, US1166); and the resume brief and handoff (US1140, US1141, US1142). The flags table lists `risk.components`, `routing.effort`, `pricing.copilot_billing` and the `personas.memory` keys, each with the default `reference-config.md` states for it. Fails on: an inventory with no 6.4 row, or a flag default `reference-config.md` contradicts. Verify: `pytest tools/tests/test_lean_specs_v64.py::SpecsV64Tests::test_the_prd_inventory_and_flags_name_64s_features`
  - AC2: Given the TRD's committed evidence and records table, then it names each record 6.4 commits with its writer, read from the code: the persona memory files `sdlc-studio/personas/memory/<persona>.md` (`persona_memory.py`), the verdict files under `sdlc-studio/reviews/verdicts/<unit>/` (issued by `critic.py brief`, bound by `critic.py record`) and a release's evidence pack `sdlc-studio/reports/evidence-pack-<version>.md` (`release_cut.py evidence-pack`). Its state section names `.local/resume-brief.md` (`sprint.py handoff`), and its data architecture names `reference-evidence-schema.md`, with the annex version it states, as the contract a consumer parses a report against. The refresh scanner checks every tracked file under `sdlc-studio/reports/`, `sdlc-studio/reviews/verdicts/` and `sdlc-studio/personas/memory/` against a row. Fails on: a tracked file in one of those trees that no row's path matches, or a row whose writer the code does not name. Verify: `pytest tools/tests/test_lean_specs_v64.py::SpecsV64Tests::test_the_trd_names_every_record_64_commits`
  - AC3: Given the TSD, then it says how 6.4 tests are selected and gated: a module marked `# test-selection: sweep` joins every commit's selection (US1167); the push gate applies the green-run noise gate CI's Lint runs (BG1493); and the evidence annex's tests hold every committed report to the annex (US0992). Each statement is checked against the code or hook it describes. Fails on: a TSD that says the push gate runs the full suite and says nothing of the noise gate. Verify: `pytest tools/tests/test_lean_specs_v64.py::SpecsV64Tests::test_the_tsd_names_the_sweep_marker_and_the_push_noise_gate`
  - AC4: Given the three specs after this change, then the refresh tests and the 6.3 specs test still pass. Fails on: a refresh pin broken by the edit. Verify: `shell python3 -m pytest -q tools/tests/test_lean_prd_refresh.py tools/tests/test_lean_trd_refresh.py tools/tests/test_lean_tsd_refresh.py tools/tests/test_lean_specs_v63.py`
- Independent review: qa-seat-US1172-r1 APPROVE (2026-11-16).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 2c27b3912b625cf6.
- Report: RPT0034.

### US1173: v6.4.0 is cut: version, changelog, known issues, install pins and the specs' baseline

- What changed: v6.4.0 is cut: version, changelog, known issues, install pins and the specs' baseline (5 points).
- Criteria passed:
  - AC1: Given the release commit, then every version home carries 6.4.0: package.json, package-lock.json, templates/version.yaml, the SKILL.md frontmatter, README, and the Version fields of prd.md, trd.md and tsd.md. `check_versions.py --strict` exits 0, and the CHANGELOG holds a `## [6.4.0] - <date>` section composed by `release_cut.py changelog-cut` from every fragment present at the cut. Fails on: package.json left at 6.3.0, or a section merged by hand. Verify: `shell python3 -c 'import json,sys; core=json.load(open("package.json"))["version"].split("-"); sys.exit(tuple(map(int, core[0].split("."))) < (6, 4, 0))' && python3 tools/check_versions.py --strict && sed -n '/^## \[6\.4\.0\] - /,/^## \[6\.3\.0\] - /p' CHANGELOG.md | grep -q 'US1164'`
  - AC2: Given `known_issues.py write --release 6.4.0` run at the cut, then `known_issues.py check` exits 0 when judged at the commit that cut 6.4.0. The 6.4.0 notes carry exactly one filled `**v6.4.0 discloses N open defects: N Medium, N Low.**` line whose figures equal the page's, and the page no longer states the 6.3.0 release. Fails on: the 6.3.0 page left in place, or a count line that disagrees with the page. Verify: `pytest tools/tests/test_lean_release_cut_v64.py::ReleaseCutTests::test_the_known_issues_page_is_cut_for_640`
  - AC3: Given the bug corpus at the cut, then `python3 tools/known_issues.py bar --at v6.4.0` exits 0: no finding at a barred severity is open, BG1493 (High) having been Fixed before the cut. Fails on: a cut made while BG1493, or any other finding at a barred severity, is open. Verify: `shell python3 tools/known_issues.py bar --at v6.4.0`
  - AC4: Given README and docs/INSTALL.md, then every verified install and version example pins `--version v6.4.0`. README links the 6.4.0 notes, and its release-notes list calls 6.4.0, and only 6.4.0, the current release. The 6.4.0 notes' CHANGELOG link is re-pointed from `#unreleased` to the 6.4.0 section. Fails on: a pin left at v6.3.0, or two releases called current. Verify: `shell grep -qE '[]][(]docs/release-notes-v6[.]4[.]0[.]md[)]' README.md && python3 -m pytest -q tools/tests/test_lean_public_docs_retired.py tools/tests/test_lean_release_cut_v64.py`
  - AC5: Given the PRD, TRD and TSD after the cut, then each names v6.4.0 as the release it covers (no Coverage line reads `v6.3.0 as cut`), and the refresh tests read that baseline from the release the documents name and package.json, so they pass at 6.4.0. Fails on: a refresh test that passes with the Coverage line removed. Verify: `shell python3 -m pytest -q tools/tests/test_lean_prd_refresh.py tools/tests/test_lean_trd_refresh.py tools/tests/test_lean_tsd_refresh.py`
- Independent review: qa-seat-US1173-r1 APPROVE (2026-11-16).
- Known issues: none recorded.
- Accountable: Darren Benson, whose signature on its report was entered under delegation, authorised by decision D0493, on 2026-11-16 over fingerprint 2c27b3912b625cf6.
- Report: RPT0034.

## Known issues not tied to one change

The reports' known issues whose id and detail name none of the changes above.

- BG1310 (Medium): `tools/skill-tests.sh`, the unittest runner `npm test` uses, loads no conftest, so the harness-variable scrub BG1197 added never runs there and the meter tests fail under a Cursor session - not-stop-ship, ruled by orchestrator.
- BG1309 (Low): A Cursor Composer or Grok session in Fast mode is priced at the standard rate, because the model id a reading carries cannot tell Fast from standard - not-stop-ship, ruled by orchestrator.
- BG1311 (Low): `sprint.py lane land` removes the builder's worktree, so the builder cannot be resumed for a repair after a REJECT and a fresh builder must re-read the unit from cold - not-stop-ship, ruled by orchestrator.
- BG1313 (Low): The resume brief has three edges its tests do not pin: a batch listed out of plan order, a `-qa.none` landing marker read as in flight, and a Sprint Goal holding a newline that breaks `parse` - not-stop-ship, ruled by orchestrator.
- BG1316 (Low): `sprint.py handoff` silently drops an `--agent` naming a unit outside the batch, both new verbs crash on an unreadable run state, and the next-step line's stream is unpinned - not-stop-ship, ruled by orchestrator.
- BG1317 (Low): A Copilot `credit_usd` of 0 is accepted and prices every Copilot reading at $0, and reference-sprint.md's list of price sources omits the newer ones - not-stop-ship, ruled by orchestrator.
- BG1319 (Low): Five Copilot model ids priced from the shared OpenAI entries stay token-priced under `pricing.copilot_billing: requests`, so a request-billed Copilot run on one of them is billed twice - not-stop-ship, ruled by orchestrator.
- BG1322 (Low): The commit-msg trailer check still refuses commit 089008d5's `Refs: US1090`, whose only record is a waiver row in decisions.md - not-stop-ship, ruled by orchestrator.
- BG1325 (Low): A hand-run mutation pass can leave a stale `.pyc` that Python reuses after the source is restored, so a later test run, the commit hook's among them, judges the mutant rather than the code - not-stop-ship, ruled by orchestrator.
- BG1326 (Low): `sprint.py handoff` writes a resume brief while a lane is still in flight, so the wave boundary reference-sprint.md defines is stated but not enforced, and four files still say no command writes a handoff - not-stop-ship, ruled by orchestrator.
- BG1327 (Low): A verdict file's `\;` escape, which the review brief prescribes for a semicolon inside a finding, still splits the finding when `critic.py record --from-verdict` reads it, leaving an untagged piece the record refuses - not-stop-ship, ruled by orchestrator.
- BG1328 (Low): `artifact.py new --type story --epic <a Done epic>` leaves the epic Done, so its parent request derives Complete although the new story is Draft, and `refine apply` refuses to add the deferred slice of an already-decomposed request - not-stop-ship, ruled by orchestrator.
- BG1373 (Medium): A NUL byte in a transcript's file path makes critic.py record refuse the unit - not-stop-ship, ruled by orchestrator.
- BG1335 (Low): sprint.py decision defer --block cannot mark a bug Blocked, so an autonomous run's blocked bug reads as an ordinary open unit - not-stop-ship, ruled by orchestrator.
- BG1338 (Low): The lane brief does not tell a builder to fast-forward its worktree, and harness worktrees start at origin's commit, so builders build on a base missing the run's landed units - not-stop-ship, ruled by orchestrator.
- BG1342 (Low): sprint.py plan --write --format json prints its run-opening lines on stdout before the JSON - not-stop-ship, ruled by orchestrator.
- BG1345 (Low): The review brief does not tell a reviewer to keep tools that write under the home directory, such as npx and npm, out of its probes - not-stop-ship, ruled by orchestrator.
- BG1346 (Low): The first verdict recorded after the ledger gained its Source column pads every row, and the commit-msg hook credits that change to every unit the subject names - not-stop-ship, ruled by orchestrator.
- BG1347 (Low): A second RULINGS: line in a verdict block is silently dropped - not-stop-ship, ruled by orchestrator.
- BG1348 (Low): critic.py's 'none blocking' guard has no test - not-stop-ship, ruled by orchestrator.
- BG1349 (Low): No test pins that a verdict file stays under --root inside a larger git repository - not-stop-ship, ruled by orchestrator.
- BG1350 (Low): sprint_report._cited_record's run-archive branch has no test - not-stop-ship, ruled by orchestrator.
- BG1354 (Low): The close's re-close window_end wiring has no test - not-stop-ship, ruled by orchestrator.
- BG1357 (Low): The report's Prices NOT MEASURED reasons and _run_usd's no-split guard are unpinned - not-stop-ship, ruled by orchestrator.
- BG1359 (Low): help/sprint.md says the run record never names the plan by its .local path, but a run opened before 509850a1 still does - not-stop-ship, ruled by orchestrator.
- BG1360 (Low): reference-scripts-review.md says row_identity digests the first eight cells, but in a nine-cell row it digests every cell except Source - not-stop-ship, ruled by orchestrator.
- BG1362 (Low): BG1334's changelog and docstring claim more than the path-as-written match - not-stop-ship, ruled by orchestrator.
- BG1365 (Low): sprint_report.py build of a signed run ignores the time window saved on its signed page - not-stop-ship, ruled by orchestrator.
- BG1366 (Low): The verdict-file header check misses a byte order mark, a lower-case header or a leading prose line - not-stop-ship, ruled by orchestrator.
- BG1367 (Low): The replay refusal tells a lane accept retry to re-brief when only the verify and the move are owed - not-stop-ship, ruled by orchestrator.
- BG1368 (Low): After the rejecting reviewer's round-2 APPROVE, rebrief_notice names a bare --rejoinder that exits 2 - not-stop-ship, ruled by orchestrator.
- BG1369 (Low): verify_ac's markdown-evidence lint matches the verdicts path as written, so reviews/../reviews/ and a symlink get through - not-stop-ship, ruled by orchestrator.
- BG1370 (Low): A later rewrite of a verdict file is attributed to the reviewer when its last write was an Edit - not-stop-ship, ruled by orchestrator.
- BG1377 (Low): The hooks' replay of a refusal's stderr is not pinned - not-stop-ship, ruled by orchestrator.
- BG1379 (Low): The report's Markdown twin still prints a `www.` or upper-case-scheme price source bare - not-stop-ship, ruled by orchestrator.
- BG1380 (Low): BG1374's exclusion of a trailing comma or full stop from a linked address has no test - not-stop-ship, ruled by orchestrator.
- BG1381 (Low): A price source URL whose path ends in a closing bracket loses that bracket from its link target - not-stop-ship, ruled by orchestrator.
- checklist (close gap): tick-verification: Ticked criteria the tree supports - 7 ticked criterion/criteria unsupported.
- BG1420 (High): Run eleven's lanes turn the full suite red in five tests the per-commit runs never selected.
- BG1399 (Medium): lane land commits and lands the code, then refuses a self-check missing a required surface, when the builder can no longer be resumed - not-stop-ship, ruled by orchestrator.
- BG1400 (Medium): lane accept takes --reviewer as free text, so a carried unit's re-review under the wrong id strands an APPROVE that only an operator supersession retires - not-stop-ship, ruled by orchestrator.
- BG1406 (Medium): lane run accepts a home-isolated unit and hands its worktree builder the main-checkout brief, and 'Isolation: no home' reads as home - not-stop-ship, ruled by orchestrator.
- BG1407 (Medium): A builder's mutation probe in a scratch copy of the tests runs without the repo-root conftest.py, so without HOME confinement - not-stop-ship, ruled by orchestrator.
- BG1409 (Medium): lane land's rebase uses --empty=keep --reapply-cherry-picks, so a commit a builder made that main already holds becomes an empty commit - not-stop-ship, ruled by orchestrator.
- BG1413 (Medium): A Ctrl-C during lane run's 2 s kill grace drops the SIGKILL that follows, so a SIGTERM-ignoring child stages after the run, and nothing pins that SIGKILL - not-stop-ship, ruled by orchestrator.
- BG1417 (Medium): CI's lint.yml sets up Node 20 while markdownlint-cli and markdownlint declare node >=22, so the gap is invisible until a dependency uses a Node 22 API - not-stop-ship, ruled by orchestrator.
- BG1382 (Low): A nested run_verifier caller's own verifier can outlive it, because both levels wait the same one second grace and Ctrl-C leaks the inner verifier - not-stop-ship, ruled by orchestrator.
- BG1383 (Low): Two more group-kill helpers duplicate verify_ac's, one closure in mutation.py and one in verify_ac._run_phase - not-stop-ship, ruled by orchestrator.
- BG1385 (Low): This repo's own AGENTS.md lacks the template's 'Integrate continuously' line, so validate.py check warns here - not-stop-ship, ruled by orchestrator.
- BG1386 (Low): Timing tests fail under parallel load: test_status GatherPerformanceTests read 4.9 s against a 3 s limit and a verify_ac criterion failed once at load 8.6 - not-stop-ship, ruled by orchestrator.
- BG1387 (Low): test_cli_grammar RealTreeMarkerTests copies the whole tree into /tmp and fails with EDQUOT on a small tmpfs - not-stop-ship, ruled by orchestrator.
- BG1388 (Low): An sdlc_md root-discovery test fails when TMPDIR is inside a repository, because it assumes its temporary directory lies outside any project - not-stop-ship, ruled by orchestrator.
- BG1389 (Low): sdlc_md.extract_field reads an empty field on into the next line and returns '>', and two is_swallowed_run branches are unpinned - not-stop-ship, ruled by orchestrator.
- BG1390 (Low): test_lean_tracked_run_record test_this_repos_signed_reports_check_in_a_clean_clone fails in a harness worktree - not-stop-ship, ruled by orchestrator.
- BG1392 (Low): prices and token_meters have untested edges: `_rates()` falls back to an empty table, `_list`'s long-context pop, a true threshold read as 1, and `book()` splits labelled lower bound - not-stop-ship, ruled by orchestrator.
- BG1398 (Low): The tool-call budget in a multi-unit lane brief is printed once per unit and nothing states the lane's total - not-stop-ship, ruled by orchestrator.
- BG1403 (Low): retro's new `supplied` guard and its `declined` list have no tests - not-stop-ship, ruled by orchestrator.
- BG1404 (Low): critic.py record splits a verdict's ISSUES at every semicolon, so a semicolon inside one finding becomes an untagged finding and the record is refused - not-stop-ship, ruled by orchestrator.
- BG1408 (Low): sprint lane land's hook-refusal text and module docstring say the worktree and main are as they were, which is untrue after the replay, and _discard_own_artefacts is untested - not-stop-ship, ruled by orchestrator.
- BG1411 (Low): The unpriced-gap remedy 'lane return --units <id> --agent A' cannot work after the close - not-stop-ship, ruled by orchestrator.
- BG1412 (Low): templates/agents/sdlc-builder.md and its pinned .claude/agents copy still tell a builder to run verify_ac without --dry-run - not-stop-ship, ruled by orchestrator.
- BG1415 (Low): No test pins the line number verify_ac's lint prints - not-stop-ship, ruled by orchestrator.
- BG1416 (Low): help/verify.md's exit-3 row in the revert-check table leaves out git failing to read the base blob - not-stop-ship, ruled by orchestrator.
- BG1421 (Low): verify_ac's revert check reads a missing runner binary as red rather than as no verdict - not-stop-ship, ruled by orchestrator.
- BG1422 (Low): No test pins verify_ac's class and module skip-mark check on the decorator's name - not-stop-ship, ruled by orchestrator.
- BG1423 (Low): file_finding writes a title with bare underscores into the bug heading and index, which markdownlint then refuses as emphasis - not-stop-ship, ruled by orchestrator.
- BG1424 (Low): A bare sprint close runs its whole pre-flight report before scaffolding the retro, so the scaffold takes many minutes - not-stop-ship, ruled by orchestrator.
- checklist (close gap): known-issues: Known issues carried, each with its stop-ship ruling - 1 unruled, 0 malformed row(s).
- CR0704 (High): The change evidence pack groups changes by risk and compliance class, lists high-risk changes first with their second seat's verdict, and reads through the evidence annex.
- CR0705 (High): sprint plan names the registry files a unit implies when it adds a script, a verb or reference text, before the build.
- BG1436 (Medium): A lesson class recorded with no run open retires at the next close in a clone with more than the quiet-run count of archived runs, from class-add and from retro extract alike - not-stop-ship, ruled by orchestrator.
- BG1448 (Medium): lane land spends its full hook run before a rebase conflict, and a replayed generated page merges into drift - not-stop-ship, ruled by orchestrator.
- BG1452 (Medium): reconcile derives a request Complete when every child of a partial refine resolves, though its unrefined criteria are undelivered - not-stop-ship, ruled by orchestrator.
- CR0703 (Medium): Fit the plan's dollar forecast from measured dollars per point, not priced tokens times the input price.
- BG1429 (Low): A project Grok price entry with a lower long-context threshold is still booked at the shipped 200,000 threshold, so a long prompt is priced at the short rate and reads exact - not-stop-ship, ruled by orchestrator.
- BG1430 (Low): verify_ac's signal relay raises its running count outside the try, so a raise in that window leaves every later returning handler refused, and no test pins the per-signal refresh of the settle bound - not-stop-ship, ruled by orchestrator.
- BG1432 (Low): Three lane-pricing and re-close behaviours are pinned by no test: each split share's per-model split, the minutes split, and the lane-yield re-freeze over a kept window - not-stop-ship, ruled by orchestrator.
- BG1433 (Low): The report templates still say the wall-clock span has no ratio, which is wrong on a page filed under the cost-forecast mark - not-stop-ship, ruled by orchestrator.
- BG1434 (Low): The risk-class map reader drops an empty-prefix entry and a scalar risk value silently, and four refine stamping paths are pinned by no test - not-stop-ship, ruled by orchestrator.
- BG1435 (Low): retitle leaves a reference-style link definition and a link in the project-root README dangling, while its changelog says it finds every link to the renamed file - not-stop-ship, ruled by orchestrator.
- BG1438 (Low): The evidence annex says fingerprint strings escape all control characters while the reference implementation escapes only U+0000 to U+001F, and it omits the no-closed-sprint limit of the version stamp - not-stop-ship, ruled by orchestrator.
- BG1440 (Low): lane return --model with no total is dropped without a word, the model trim is untested, and help/sprint.md omits that a several-unit total is not split when a unit has no Points - not-stop-ship, ruled by orchestrator.
- BG1444 (Low): sprint plan reports a malformed risk map as 'no component map is declared', says nothing when a unit's risk tag is outside the vocabulary, and no test pins which component the flag names when prefixes overlap - not-stop-ship, ruled by orchestrator.
- BG1446 (Low): Three second-seat behaviours are correct but unpinned: a story's risk tag read over its Affects, the brief's no-map default, and the first seat's latest verdict rather than its first - not-stop-ship, ruled by orchestrator.
- BG1447 (Low): tools/check_budgets.py reports every file within budget while the pre-commit budgets lane fails the same tree on docgen drift - not-stop-ship, ruled by orchestrator.
- BG1449 (Low): lane accept refuses to record a REJECT when the unit's self-check is stale, though a REJECT moves nothing - not-stop-ship, ruled by orchestrator.
- BG1450 (Low): A reviewer's verdict file is refused by critic.py record over one code span with a leading space, and the review brief does not warn - not-stop-ship, ruled by orchestrator.
- BG1451 (Low): The commit-msg hook refuses git commit --amend on a lane commit because it attributes only the newly staged files - not-stop-ship, ruled by orchestrator.
- BG1453 (Low): file_finding keeps a placeholder id such as changelog.d/BGXXXX.md in Affects verbatim instead of substituting the minted id or refusing it - not-stop-ship, ruled by orchestrator.
- BG1454 (Low): sprint lane return --agent agent-<id> leaves the unit unpriced, while lane land prints the builder as agent-<id> - not-stop-ship, ruled by orchestrator.
- checklist (close gap): known-issues: Known issues carried, each with its stop-ship ruling - 3 unruled, 0 malformed row(s).
- BG1455 (Medium): escape.py trace counts a Mentions: trailer id as a unit the release shipped, so a commit that only names a unit puts it among the suspects - not-stop-ship, ruled by orchestrator.
- BG1463 (Medium): retro.py seats drops an Escaped-via bug silently when its unit's approval names no seat, has only a REJECT, or post-dates the bug - not-stop-ship, ruled by orchestrator.
- BG1465 (Medium): retro.py seat_misses reads each cited unit's file uncached, so an unbounded window does not finish in ten minutes - not-stop-ship, ruled by orchestrator.
- BG1470 (Medium): lane land runs the full commit hooks, then refuses the rebase over an unstaged author-self-checks.md the builder's self-check left in the worktree - not-stop-ship, ruled by orchestrator.
- BG1472 (Medium): Five branches of the close's learning review and the sign's strike are right by execution but no test fails without them - not-stop-ship, ruled by orchestrator.
- CR0706 (Medium): An incident is triaged into the escaped bugs it caused, the report states escapes per 100 points, and an escape's class reaches only the briefs whose files it matches - not-stop-ship, ruled by orchestrator.
- CR0707 (Medium): sprint lane offers a rebase step that carries a waiting lane's staged work onto a moved main - not-stop-ship, ruled by orchestrator.
- CR0708 (Medium): file_finding writes criteria a plan can take, or marks a bug ungroomed, instead of truncated stubs with no Verify line - not-stop-ship, ruled by orchestrator.
- BG1456 (Low): The escaped-bug Fixed gate's scaffold stripping is untested and matches the scaffold by exact string, and test_file_finding's selector reader test fails outside a git checkout - not-stop-ship, ruled by orchestrator.
- BG1457 (Low): The seat record reads any bracketed word as a seat, lane brief --seat accepts any value, and retro seats counts rounds across deliveries - not-stop-ship, ruled by orchestrator.
- BG1458 (Low): escape.py to-class records a class with no files for a hand-edited bug with no Affects, collapses whitespace inside Affects paths, and the catalogue pages lag the new verb and flags - not-stop-ship, ruled by orchestrator.
- BG1461 (Low): lane brief warns a landed unit under review never returned, and that the tree may already carry its work - not-stop-ship, ruled by orchestrator.
- BG1462 (Low): lane accept records under the self-check's agent author and critic.py record then warns that author lacks the holder (role) form - not-stop-ship, ruled by orchestrator.
- BG1464 (Low): retro.py's own-finding check matches a review word anywhere in Evidence and two of its guards have no test - not-stop-ship, ruled by orchestrator.
- BG1466 (Low): A signed report's signoff principal and signed_at figures still read not yet signed, though the evidence schema says they hold who signed and when - not-stop-ship, ruled by orchestrator.
- BG1467 (Low): A review-cap carry bug copies the carried unit's Affects verbatim, so it declares the unit's changelog fragment, not its own - not-stop-ship, ruled by orchestrator.
- BG1473 (Low): A damaged tracked run record reads on the brief as awaits its run's signature, not as damaged - not-stop-ship, ruled by orchestrator.
- BG1475 (Medium): sprint close --dry-run takes about half an hour and prints nothing until it ends, mostly one git log per artefact in the review-current check - not-stop-ship, ruled by orchestrator.
- BG1477 (Medium): lane accept --agent on a multi-unit lane charges the builder's whole transcript to each unit, overriding the land's split by points - not-stop-ship, ruled by orchestrator.
- BG1482 (Medium): A build-injected lesson class can no longer retire, so once more than INJECT_MAX build classes are live the digest cap drops the oldest builder traps - not-stop-ship, ruled by orchestrator.
- BG1483 (Medium): A run's repeat of a lesson class is counted only from a cited REJECT or retro Try item, so a repeat caught by the land or the push gate goes unrecorded - not-stop-ship, ruled by orchestrator.
- BG1491 (Medium): lane accept on an APPROVE prints that the unit moved to Fixed and then that its return is blocked, when one criterion has no Verify line - not-stop-ship, ruled by orchestrator.
- BG1492 (Medium): Nothing stops the orchestrator committing a reviewer's half-written verdict: git add of the records sweeps in a verdict file still being written - not-stop-ship, ruled by orchestrator.
- CR0710 (Medium): CR0699 remainder: the bench runner takes a builder-effort arm and reports priced tokens per point, review rounds and the held-back score per arm - not-stop-ship, ruled by orchestrator.
- CR0711 (Medium): Show each open lane's liveness, so a stalled builder is caught in minutes rather than hours - not-stop-ship, ruled by orchestrator.
- CR0712 (Medium): Prevent or retire lesson LC-010 (the push gate and CI disagree on the runner) - not-stop-ship, ruled by orchestrator.
- BG1476 (Low): file_finding stamps Raised-in-batch as none open for a finding filed while a run is open - not-stop-ship, ruled by orchestrator.
- BG1481 (Low): test_support_page lets four planted SUPPORT.md defects through: a gh skills install line, an install command in prose, and Stack Overflow or IRC named in prose - not-stop-ship, ruled by orchestrator.
- BG1485 (Low): A shell Verify line run with -s still reads all-skipped and no-tests shapes from its whole output, and a partial-skip test's docstring still says the release gate counts the skips - not-stop-ship, ruled by orchestrator.
- BG1488 (Low): reference-outputs.md still calls Deferred a story terminal status at lines 134, 745 and 755, against its own Story row and sdlc_md.TERMINAL_STATUS - not-stop-ship, ruled by orchestrator.
- BG1490 (Low): test_critic_rejoinder_from_ledger and test_critic_verdict_file_binding fail when run inside an agent session, because the harness session id reaches the verdict's source field - not-stop-ship, ruled by orchestrator.
- CR0709 (Low): Add lessons.py reinstate: put a retired class back in force with a recorded run and reason - not-stop-ship, ruled by orchestrator.
- CR0713 (Medium): Prevent or retire lesson LC-019 (a push-gate guard the per-commit run skips) - not-stop-ship, ruled by orchestrator.
- BG1497 (Low): Two config keys the code reads are undocumented: sprint.fresh_session is missing from reference-config.md and pricing.copilot_billing from config-defaults.yaml - not-stop-ship, ruled by orchestrator.
- BG1499 (Low): US1058 still reads Status Ready though run thirteen carried it at the review cap and BG1460 delivered it, and the PRD row naming it says Complete - not-stop-ship, ruled by orchestrator.
- BG1500 (Low): help/retro.md says an escaped defect is charged to the seat whose latest verdict approved, in any run, leaving out the code's limit to verdicts on or before the bug's Created day - not-stop-ship, ruled by orchestrator.
- BG1502 (Low): critic.py self-check record refuses a unit until it claims its changelog.d fragment, though the release cut has already merged that fragment into CHANGELOG.md - not-stop-ship, ruled by orchestrator.
- BG1504 (Low): The sdlc-builder agent card does not confine a builder's clean-up to paths it created, so a builder deleted every tmp.* directory in the shared test temp directory - not-stop-ship, ruled by orchestrator.
- BG1505 (Low): 6.4.0's CHANGELOG says a fragment that opens with a list item folds byte for byte, but compose bullets an ordered item, and no test pins a later list item in a prose entry - not-stop-ship, ruled by orchestrator.

## Accountability

Each change names the principal recorded on its report's signature, with the signing date and the fingerprint signed. The signature is the one the run's committed record holds, and the report's figures re-derive that fingerprint; a report they no longer re-derive, or whose own signature the run record does not hold, refuses the pack. A signature entered under delegation says so and names the decision that authorised it. No record names an accountable person per unit, so every change of a report names that report's signer; a blank principal, one that reads as an agent or one the review ledgers record as an author of that report's own units refuses the pack.
