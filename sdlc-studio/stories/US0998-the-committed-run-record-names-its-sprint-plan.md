# US0998: The committed run record names its sprint plan by digest, not by a .local path

> **Status:** Done
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py, .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_rolling.py, changelog.d/US0998.md
> **Epic:** EP0276
> **Points:** 2
> **Persona:** Graham Doyle

## User Story

**As** a team lead reading a teammate's committed run record
**I want** the record to identify the plan the run was opened from by a content digest under its own key
**So that** the record carries no pointer into a .local/ directory I do not have, and a plan file produced later can be matched to the run

## Acceptance Criteria

- **AC1:** Given a run opened with `sprint plan --write` and closed with `sprint close`, when the tracked run record is read, then `plan_digest` holds `sha256:` and the full 64-hex digest of the sprint-plan.json that plan wrote, `plan` is null, and no value in the record names a path under `.local/`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py::PlanDigestTests::test_plan_write_records_a_content_digest
  - **Verified:** yes (2026-11-12)
- **AC2:** Given a run whose batch a second `sprint plan --write` grows before its goal is judged, when the run is closed, then `plan_digest` is the digest of the plan the second write left, not the first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py::PlanDigestTests::test_a_replan_moves_the_digest_to_the_last_write
  - **Verified:** yes (2026-11-12)
- **AC3:** Given a rolling run whose next cycle is opened by `sprint boundary`, when that cycle's run record is filed, then its `plan_digest` is the digest of that cycle's own plan, not the previous cycle's and not a path.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py::PlanDigestTests::test_the_next_cycle_records_its_own_plan_digest
  - **Verified:** yes (2026-11-12)

## Notes

- Release: 6.4, run ten (D0461); was 6.3 (D0388) (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: open_run(plan=str(out)) left as it is (sprint.py:10816-10817, `out` set at :10806), which the portable projection turns into sdlc-studio/.local/sprint-plan.json; or the digest written into `plan` in the 12-hex form portable already uses for a path
- AC2 must fail on: recording the digest only when open_run opens the run, so a re-plan that rewrites the plan leaves the record naming a plan that no longer exists
- AC3 must fail on: fixing only cmd_plan's call and leaving `_open_next_cycle`'s plan=str(out) (sprint.py:11169-11170; the plan is written at :11156-11158)
- Serves Jonah's End goal 3 (jonah-reyes-team-lead.md:28).
- Checked at HEAD 508e2408 (2026-11-12): nothing is met. None of the 22 committed records carries `plan_digest`, and in scripts/ the name belongs only to `lessons.plan_digest` (lessons.py:1084), an unrelated function a new run-record key must not be confused with.
- Legacy values, which the annex (CR0609) documents and nothing rewrites: the five records before RUN-01M3HR74 hold `plan: sha256:2e2f8b72a73b`, portable's 12-hex digest of an absolute path outside the repository (`portable`, lib/run_state.py:581), the same value on five different plans; every record from RUN-01M3HR74 to RUN-01M7061X (17 records) holds `plan: sdlc-studio/.local/sprint-plan.json`. Neither is a content digest, hence the separate key and the full-length digest.
- From RUN-01M3VF2J to RUN-01M7061X, that plan path is the only .local value in a committed record (checked on RUN-01M3VF2J, RUN-01M6RZQZ and RUN-01M7061X); RUN-01M3HR74 to RUN-01M3T8N1 also carry `handoff_worklist` under .local, which nothing at HEAD writes.
- One reader of the record's plan field now exists: `_waves` in lib/resume_brief.py:134 (US1140, run nine) reads `state.get("plan")` and falls back to PLAN_REL, sdlc-studio/.local/sprint-plan.json (:48), the one path both writers use. A null `plan` therefore still reads the waves; pin that with a case in test_resume_brief.py, whose fixture (:59) sets the field, as test_sprint_handoff.py:66 does. Only lib/run_state.py:2106 writes it; what a reviewer needs from the plan is already committed as plan_snapshot (`record_plan_snapshot`, sprint.py:320).
- test_lean_tracked_run_record.py:160 (`test_sign_files_a_portable_sealed_record`) pins a fixture's `plan`, an absolute path outside the repository, projected to `sha256:<12 hex>`. It stays green if only the two callers stop passing `plan`; it breaks if the projection itself nulls `plan`, so change the callers, not `portable`.
- cmd_plan writes the plan after open_run (the run opens first so a refused plan leaves nothing; the write is at sprint.py:10846-10847), so the digest is recorded with run_state.update after each write; `_open_next_cycle` writes first and can record it at open. Its rolling fixture is in test_sprint_rolling.py (the US0870 case at :832 drives `_open_next_cycle`).
- Shares sprint.py, lib/run_state.py and help/sprint.md with US0999, so the two land one after the other.
- The panel's engineering seat answered that a content digest is enough for CR0610 (no plan breakdown on the record).

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Persona field names Maya Okafor, but the User Story is 'As a team lead' and Notes say it serves Jonah Reyes's End goal 3 (sdlc-studio/personas/jonah-reyes-team-lead.md:24-29); either set '> **Persona:** Jonah Reyes' or record Jonah as the served Secondary, so the product seat judges it against the goal it names (D0380).
- Release note stale: the story says 'Release: 6.2' but D0382 (2026-10-20, supersedes D0381) sets the path to the 6.2.0 tag as run three plus run four's doc refreshes only, so this lands after 6.2.0; re-tag when a run takes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: line references corrected; the note that nothing reads `plan` corrected (lib/resume_brief.py reads it since US1140, with a fallback a null keeps working); Affects gains test_lean_tracked_run_record.py, test_resume_brief.py and test_sprint_rolling.py, which pin the field or drive the next cycle; legacy record range extended to RUN-01M7061X; release set to 6.4 (D0461); criteria unchanged |
