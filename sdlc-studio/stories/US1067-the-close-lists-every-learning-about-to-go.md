# US1067: The close lists every learning about to go live on the retro, with what it addresses and who approved it

> **Status:** Done
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_retro_persona_learnings.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_output_vocabulary.py, .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py, .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/US1067.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1058
> **Persona:** Abena Osei

## User Story

**As a** Maya Okafor, signing the run once at the end
**I want** the close to list on the retro every approved learning not yet live, whatever wrote it, with its seat, approver and the adverse items it addresses, and to name each seat with adverse evidence and no learning and how many verdict rows name no seat
**So that** every learning about to go live is in front of me on the retro I sign, and 'no learnings' can never read as 'nothing to learn'

## Acceptance Criteria

- **AC1:** Given qa's learning proposed in this run and approved by `Lena Marsh (product)`, and a product learning written with `persona_memory.py add` and approved by qa outside any retro, when `sprint.py close` runs, then the retro gains a delimited `## Persona learnings` block listing both with their approvers and addressed items, each entry is stamped Listed-in with the run, and the run record names both ids.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_persona_learnings.py::RetroLearningsTests::test_the_close_lists_every_approved_learning_not_yet_live
  - **Verified:** yes (2026-11-15)
- **AC2:** Given a batch where product has a later-bug item and no learning, qa has no adverse item and no learning, and two of five verdict rows name no seat, when `sprint.py close` runs, then the close output and the block name product as a seat with adverse evidence and no learning, do not name qa, and say two of five verdict rows name no seat, with the close's outcome unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_persona_learnings.py::RetroLearningsTests::test_the_close_names_unlearned_adverse_evidence_and_unattributed_rows
  - **Verified:** yes (2026-11-15)
- **AC3:** Given that block and prose the author wrote around it, when the close runs again after another learning is approved, then the block is replaced in place, lists all three, and the author's prose is byte-identical.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_persona_learnings.py::RetroLearningsTests::test_a_reclose_refreshes_the_block_in_place
  - **Verified:** yes (2026-11-15)

## Notes

- Run thirteen grooming (D0479):
  - Persona: change Maya Okafor to Abena Osei (Primary). Serves End goal 1 (evidence at the change board: what is about to go live, who approved it); End goal 2.
  - Dependencies US1066 and US1060 are SOFT. US1066: the listing reads Approved-by/Addresses fields that US1058's schema defines; fixtures write them with `set-field`. US1060: it only supplied the `persona-memory` close stage; this story creates that stage itself (add it to `sprint._CLOSE_CHAIN` after retro-accuracy; close output vocabulary and the cost-regression test pin the chain length, hence the extra tests). US1060 itself is not in the run (cannot expire for 90 days; panel's cut order).
  - Build after US1066 where the lane allows, but it must not wait on it.
  - Line numbers in this story's notes are stale at HEAD (critic.py brief 2527->3755, `_lessons_block` 2358->3283, sprint.py `_CLOSE_CHAIN` 5668->5906, `cmd_sign` 9708->10474, retro.py extract 3535->4045, `lessons.phase_digest` 1864->1999, validate.py `check_personas` 1342->1278/1391); builder re-greps by name.
- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: only the run's own proposals listed, so `add` then `approve` puts a learning live with no retro listing and no chance to strike it
- AC2 must fail on: every quiet seat named on every close (noise under one reviewer per unit, D0341), or unattributed rows left out so an empty block reads as a clean run (LL0009)
- AC3 must fail on: a second block appended, or the author's text rewritten
- Serves: Maya Okafor #3.
- Checked at HEAD: the retro has no persona section and the close chain (sprint.py:5668) has no persona step.
- Writes through `retro.py learnings --id <retro> --write`, the accuracy block's delimited pattern (`write_accuracy`, retro.py:1890), called from the `persona-memory` close stage; the listed ids go on the run state (`persona_learnings_listed`), which the signature seals.
- Panel self-flattery guard (a): whatever wrote an approved learning, it waits for a signed close to list it. Listed, never refused (CR0633).
- Re-sized 3 to 5: listing every not-yet-live learning, the Listed-in stamp and the two counts.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1066 and US1060 (Draft)
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-15 | Claude Opus 5.5 (run thirteen grooming, D0479) | Groomed for run thirteen: Persona Abena Osei, Affects with the existing tests that pin what it changes, Depends-on reduced to real dependencies, notes |
