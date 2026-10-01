# US0971: A fresh project's first plan is quiet and correct

> **Status:** Done
> **Delivers:** CR0592
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/blocker_sweep.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py, changelog.d/US0971.md
> **Epic:** EP0270
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the first `sprint plan` on a freshly initialised project to print only what needs my attention, and to print it correctly
**So that** I do not learn to skim past warnings about states `init` chose for me

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0592 bullets 47, 48, 61 and 69, 3 points. No warning that names a real defect is removed; each fix corrects a wrong statement or stops reporting a default as a divergence.

- #47 `goal_review_status` offers only project seats, so a fresh project is told `no seat can review it`, though `persona_resolve` and `critic.py brief` fall back to the shipped product, engineering and qa seats.
- #48 after guided init skips the TSD, the plan prints `test strategy: UNAVAILABLE` and `execution policy DIVERGES ... UNRECONCILED`; init installs no commit hook while the default policy declares a per-commit lane, so the divergence is the default state.
- #61 `blocker_sweep.sweep` never checks for a terminal status, so a retired unit with a historical `Blocked by:` line is proposed for Blocked -> Ready.
- #69 `goal-review record --amend-from <prior> --requesting-seat <seat>` carries the requesting seat's NOT-achievable verdict forward onto the wording that seat asked for.

## Premise at HEAD

Executed at `85042135` in this repository:

```text
$ python3 .claude/skills/sdlc-studio/scripts/sprint.py plan --stories Ready 2>&1 | grep 'blocker sweep'
blocker sweep: 14 newly-unblocked unit(s) (US0677, US0678, US0679, US0680, US0681, US0682, US0683, US0684, US0685, US0686, US0687, US0688, US0689, US0690) - propose Blocked -> Ready via the gated transition, then re-plan to include them
```

All 14 are Won't Implement or Superseded.

## Acceptance Criteria

- [ ] **AC1** Given a project after `init.py run` with no `sdlc-studio/personas/seats/`, when `sprint.py plan --goal <text>` runs, then it does not print `no seat can review it` and names the shipped seats that would review the goal. Fails on: HEAD prints `goal review: UNREVIEWED - this project declares no review seats of its own`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py::FreshPlanQuietTests::test_a_fresh_project_is_offered_the_shipped_seats
  - **Verified:** yes (2026-10-01)
- [ ] **AC2** Given a project after `init.py guided --skip` of the TSD stage and with no commit hook installed, when `sprint.py plan` runs, then it prints neither `test strategy: UNAVAILABLE` nor `execution policy DIVERGES`. Fails on: HEAD prints both on that project's first plan
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py::FreshPlanQuietTests::test_init_chosen_states_are_not_reported_as_divergence
  - **Verified:** yes (2026-10-01)
- [ ] **AC3** Given a Superseded story carrying `Blocked by:` a Done story, beside a Blocked story with the same blocker, when `sprint.py plan` runs its blocker sweep, then only the Blocked story is proposed. Fails on: HEAD proposes the terminal unit (premise: 14 terminal units here)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py::FreshPlanQuietTests::test_the_blocker_sweep_skips_terminal_units
  - **Verified:** yes (2026-10-01)
- [ ] **AC4** Given engineering judged a goal NOT achievable and the goal was amended with `sprint.py goal-review record --amend-from <prior> --requesting-seat engineering`, when `sprint.py plan --write` runs, then it prints no `judged the goal NOT achievable` advice from engineering. Fails on: HEAD carries engineering's verdict forward onto its own wording
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fresh_plan_quiet.py::FreshPlanQuietTests::test_the_requesting_seats_verdict_is_discharged_by_its_amendment
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
