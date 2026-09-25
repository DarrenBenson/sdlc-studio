# US0934: A bug reaches Fixed without a depth gate, and the retired --depth flags are refused

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_integrity.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth_gate.py, changelog.d/US0934.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, AGENTS.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer closing a bug fix
**I want** a bug to reach Fixed on green Verify selectors alone, with no depth tier to stamp, no parity check and no reopen retraction
**So that** a field that read `functional` on 636 of 637 units stops costing a stamp and a refusal on every fix

## Acceptance Criteria

- **AC1:** Given a fixture bug with green executable criteria, an independent delivery APPROVE and no `Verification depth` field, when `transition.py set <id> Fixed` runs, then it succeeds; the same bug with a red criterion is still refused naming that criterion. Fails on: HEAD's depth gate refusing the missing field, and on a deletion that takes the verify gate with it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth_gate.py::DepthGateGoneTests::test_a_bug_without_a_depth_reaches_fixed
  - **Verified:** yes (2026-09-25)
- **AC2:** Given `artifact.py close <id> --depth <v>` and `transition.py set <id> <status> --depth <v>`, when invoked, then each exits 2 naming the retired flag; `artifact.py close <id>` without it still closes a green fixture story. Fails on: removing only the `close` flag and leaving `set --depth` accepted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth_gate.py::DepthGateGoneTests::test_both_depth_flags_are_retired_and_close_still_works
  - **Verified:** yes (2026-09-25)
- **AC3:** Given a fixture project setting `quality.depth_parity_gate: block` and a story whose `Verification target` names a tier its criteria do not reach, when it is moved to Done, then no parity refusal fires; and when a Fixed bug carrying a `Verification depth` line is reopened, the line is left as written with no retraction, and no shipped script calls `sdlc_md.depth_retracted`. Fails on: deleting the parity check but leaving the reopen retraction and `critic.py`'s `depth_retracted` read
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth_gate.py::DepthGateGoneTests::test_no_parity_refusal_or_reopen_retraction
  - **Verified:** yes (2026-09-25)
- **AC4:** Given `artifact.py new bug` in a fixture, then the created bug and `templates/core/bug.md` carry no `Verification depth` field. Fails on: dropping the field from the template while `artifact.py` still writes it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_depth_gate.py::DepthGateGoneTests::test_a_new_bug_carries_no_depth_field
  - **Verified:** yes (2026-09-25)

## Notes

- Split from the original US0910 as its "b" half: the bug depth gate, parity, retraction and both `--depth` flags (old AC1, AC3 as amended, the parity half of AC4 and the template half of AC5).
- Stamps: none measured. DepthTierGateTests, StoryTargetParityTests and AReopenRetractsTheGreenItOverturnsTests carry no stamped selector. Two stamped tests are edited, not deleted, and must keep their names: `test_artifact.py`'s close tests that pass `--depth` (US0116 among them) and `CoverageGateTests::test_a_ruled_line_passes_and_the_ruling_is_in_the_depth_field` (US0816).
- `test_lean_verdict_integrity.py` and `test_lean_review_cap.py` pass `set --depth`, so drop the flag from both.
- Engineering call: this story deletes `sdlc_md.depth_retracted` and removes `critic.py`'s read of it (about line 5039). It is not kept alive until US0917 or US0919.
- Lands before US0911 and US0935, which share `_pre_write_gates` and whose fixtures the depth gate shapes. Must not share a wave with US0910.
- `Verification target` on story criteria becomes meaningless here. US0924 removes it from the templates.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: the US0910b half (5 points); user story written; takes old US0910 AC1, AC3 amended to name `transition.py set --depth`, the parity and retraction half of AC4 and the template half of AC5; stamps measured at none, with the edited stamped tests named; new module test_lean_no_depth_gate.py and changelog fragment added to Affects |
