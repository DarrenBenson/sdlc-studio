# US1353: A seat agent's spend on a unit's solution review is recorded against the unit, so its tokens per unit count every seat

> **Status:** Done
> **Risk-class:** high
> **Delivers:** CR0757
> **Created:** 2026-11-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_spend.py, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel_brief.py, changelog.d/US1353.md
> **Epic:** EP0386
> **Points:** 1
> **Depends on:** US1351
> **Persona:** Abena Osei

## User Story

As a head of engineering who holds delivery to a monthly budget, I want each seat agent's spend on a unit's solution review recorded against that unit, so that the unit's tokens per unit count every seat and the step's cost is judged on what it cost.

## Acceptance Criteria

### AC1: each seat agent's priced spend is added to the unit, once

- **Given** `panel: [qa, product, persona]`, a 3-point story whose three seats have recorded their
  verdicts, an open run, a harness store (`test_meter_reads_true`'s) holding a transcript for the
  builder and one for each seat's agent, and the builder priced through `sprint.py lane return
  --units <id> --agent <builder>`
- **When** `critic.py approach spend --unit <id> --seat <seat> --agent <agent id>` is run once for
  each seat's agent, then again for the qa agent after its transcript has grown
- **Then** `run_state.unit_agent_totals(state)[<id>]` has `priced` equal to the sum of the builder's
  and the three seat agents' priced readings and `priced_agents` 4; each seat record reads
  provenance `transcript`, agent `agent-<id>` and a note naming the seat; the second qa run leaves
  one qa record, carrying the later reading; `sdlc-studio/reviews/solution-reviews.md` is
  byte-equal before and after; the unit's `unit_actuals` entry is unchanged; and stdout names the
  unit, the seat and the priced figure
- **Fails on:** HEAD plus US1344, where `critic.py approach spend` is an invalid choice (E5); the one
  command that reads an agent's transcript into a unit's priced total, `sprint.py lane return
  --units US0101 --agent qa1`, also verified the unit's criteria, printed "US0101: fixed (claimed
  fixed)", noted the record "sprint lane return (fixed)" and closed the unit's actuals window,
  though no code had been written; and `retro.py accuracy --delegated-tokens` records a supplied
  total that is never priced (E14)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_spend.py::SolutionReviewSpendTests::test_each_seat_agent_s_spend_is_added_to_the_unit_once
- **Verified:** yes (2026-11-28)

### AC2: an agent with no readable transcript records nothing

- **Given** the same run and store
- **When** `approach spend --unit <id> --seat product --agent nobody1` is run, then `--agent
  <product agent id>`, and, with no run open, `--agent <persona agent id>`
- **Then** the first exits 1 with nothing on stdout, stderr naming `nobody1` and the directory
  searched, and the run's delegated records unchanged; the second is recorded (the control); and the
  third exits 1 saying no run is open, recording nothing
- **Fails on:** HEAD plus US1344, where `approach spend` is an invalid choice (E5)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_spend.py::SolutionReviewSpendTests::test_an_agent_with_no_readable_transcript_records_nothing
- **Verified:** yes (2026-11-28)

### AC3: the panel and the catalogue name the spend command

- **Given** the same panel and story, and reference-scripts-review.md's critic.py entry
- **When** `critic.py approach panel --unit <id> --note <path>` is run, the catalogue is read and
  `docgen.py surface --check` is run
- **Then** each seat's line names `critic.py approach spend --unit <id> --seat <seat> --agent <agent
  id>`, to run when that seat's agent returns; the catalogue names `approach spend`, that it reads
  the agent's own transcript and that it writes no verdict row; and the surface check passes
- **Fails on:** HEAD plus US1344, where `approach panel` and `approach spend` are invalid choices
  (E5), and the catalogue and the surface page have 0 matches for "approach spend" (E17)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_spend.py::SolutionReviewSpendTests::test_the_panel_and_the_catalogue_name_the_spend_command
- **Verified:** yes (2026-11-28)

## Notes

- Depends on: S3 (critic.py, reference-scripts-review.md, reference-scripts-surface.md; the panel
  verb). Runs beside S4; they share no file.
- Persona: Abena Osei, End goal 3: "Know what each team's delivery costs per point and hold it to a
  monthly budget, whichever harness a team uses".
- Ran: the verb probe (E5), the lane return route and its side effects, the transcript reader and
  the record rules (E14), the report's per-unit priced source (E15).
- The verb: read with `run_state.agent_transcript_tokens(root, agent)`, taking the id with or
  without its `agent-` prefix as `lane return` does; record with
  `run_state.record_delegated_tokens(root, reading["tokens"], agent=f"agent-{id}",
  note=f"solution review ({seat})", unit=uid, reading=reading,
  provenance=run_state.READ_FROM_TRANSCRIPT)`. A second reading of the same transcript for the same
  unit replaces the earlier record by the rule already in `record_delegated_tokens`; no new
  replacement code is needed. Leave the record untagged by harness, as `lane return` leaves its
  builder's, so the run total treats a seat agent as it treats a builder.
- It writes no ledger row and does not check that the seat recorded a verdict: an agent that
  failed to record still cost what it cost.
- It records no minutes. The per-unit row then names how many of the unit's agents supplied minutes,
  as `unit_agent_totals` and the report's agent minutes rule already do; that is true and needs no
  report change.
- The records reach the report with no report change: US1348's `sr_priced` is the mean of the
  units' `eu_priced` (E16), and `eu_priced` is the unit's `unit_agent_totals` priced figure (E15).
- Add the verb's row to reference-scripts-surface.md with `docgen.py surface`, never by hand.
- Readers beside the new module: critic.py 221; reference-scripts-review.md 2;
  reference-scripts-surface.md 17 (E18).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-27 | engineering seat; product seat (D0648) | Groomed for run twenty-eight from the CR0757 breakdown: engineering draft with the product seat's six rulings and changes C1-C23 folded in |
