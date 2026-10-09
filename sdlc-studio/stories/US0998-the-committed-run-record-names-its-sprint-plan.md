# US0998: The committed run record names its sprint plan by digest, not by a .local path

> **Status:** Draft
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py, changelog.d/US0998.md
> **Epic:** EP0276
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As** a team lead reading a teammate's committed run record
**I want** the record to identify the plan the run was opened from by a content digest under its own key
**So that** the record carries no pointer into a .local/ directory I do not have, and a plan file produced later can be matched to the run

## Acceptance Criteria

- **AC1:** Given a run opened with `sprint plan --write` and closed with `sprint close`, when the tracked run record is read, then `plan_digest` holds `sha256:` and the full 64-hex digest of the sprint-plan.json that plan wrote, `plan` is null, and no value in the record names a path under `.local/`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py::PlanDigestTests::test_plan_write_records_a_content_digest
- **AC2:** Given a run whose batch a second `sprint plan --write` grows before its goal is judged, when the run is closed, then `plan_digest` is the digest of the plan the second write left, not the first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py::PlanDigestTests::test_a_replan_moves_the_digest_to_the_last_write
- **AC3:** Given a rolling run whose next cycle is opened by `sprint boundary`, when that cycle's run record is filed, then its `plan_digest` is the digest of that cycle's own plan, not the previous cycle's and not a path.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py::PlanDigestTests::test_the_next_cycle_records_its_own_plan_digest

## Notes

- Release: 6.2 (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: open_run(plan=str(out)) left as it is (sprint.py:10251), which the portable projection turns into sdlc-studio/.local/sprint-plan.json; or the digest written into `plan` in the 12-hex form portable already uses for a path
- AC2 must fail on: recording the digest only when open_run opens the run, so a re-plan that rewrites the plan leaves the record naming a plan that no longer exists
- AC3 must fail on: fixing only cmd_plan's call and leaving `_open_next_cycle`'s plan=str(out) (sprint.py:10598)
- Serves Jonah's End goal 3 (jonah-reyes-team-lead.md:28).
- Legacy values, which the annex (CR0609) documents and nothing rewrites: the five records before RUN-01M3HR74 hold `plan: sha256:2e2f8b72a73b`, portable's 12-hex digest of an absolute path outside the repository (run_state.py:516-537), the same value on five different plans; the records from RUN-01M3HR74 to RUN-01M45FV6 hold `plan: sdlc-studio/.local/sprint-plan.json`. Neither is a content digest, hence the separate key and the full-length digest.
- From RUN-01M3VF2J on, that plan path is the only .local value in a committed record; RUN-01M3HR74 to RUN-01M3T8N1 also carry `handoff_worklist` under .local, which nothing at HEAD writes.
- Nothing reads the record's plan field (in scripts/, only run_state.py:1224 writes it); what a reviewer needs from the plan is already committed as plan_snapshot.
- cmd_plan writes the plan after open_run (the run opens first so a refused plan leaves nothing), so the digest is recorded with run_state.update after each write; `_open_next_cycle` writes first and can record it at open.
- The panel's engineering seat answered that a content digest is enough for CR0610 (no plan breakdown on the record).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
