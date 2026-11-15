# US1058: persona_memory.py keeps each persona's evidenced learnings in a committed memory file beside its card

> **Status:** Ready
> **Delivers:** CR0632
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/personas/memory-template.md, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/help/references.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py, tools/tests/test_lean_trd_refresh.py, changelog.d/US1058.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, sdlc-studio/reviews/root-census.md, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_surface.py, sdlc-studio/reviews/command-audit.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0287
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Maya Okafor, whose review seats forget everything when each brief ends
**I want** `persona_memory.py add`, `list` and `recall` to keep each persona's learnings, with evidence, a date, a validity horizon and a state, in `sdlc-studio/personas/memory/<persona>.md`
**So that** what a seat learns is a committed record every clone reads, never a note in one machine's .local

## Acceptance Criteria

- **AC1:** Given a project with a qa seat card and Maya Okafor's card, when `persona_memory.py add --persona qa --title ... --body ... --evidence US0001` and then the same with `--persona maya-okafor-founder-engineer` run, then `sdlc-studio/personas/memory/qa.md` holds `## M-0001` and the other file holds `## M-0002`, each with Persona, Evidence, Added, a Review-by 90 days on and State proposed, and every field the later stories write (Approved-by, Addresses, Listed-in, Struck, Retired) is accepted by a `set-field` helper that reuses `lessons.upsert_field`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py::PersonaMemoryStoreTests::test_add_writes_a_stamped_proposed_learning_with_a_unique_id
- **AC2:** Given an add with no `--evidence`, one citing only ids that resolve to nothing on disk, one whose `--persona` names neither a seat role nor a card, one whose key is both, and one run under a `.gitignore` rule matching `sdlc-studio/personas/memory/`, when `persona_memory.py add` runs, then each exits 2 naming its reason (the ignore rule included) and no file is written.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py::PersonaMemoryStoreTests::test_an_unevidenced_unknown_ambiguous_or_ignored_add_is_refused
- **AC3:** Given entries for qa and product in several states, when `persona_memory.py list --persona qa --query race` runs as text and as `--format json`, then only qa's entries whose title or body mention race are listed, each with its state and horizon.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py::PersonaMemoryStoreTests::test_list_and_recall_read_one_personas_memory
- **AC4:** Given seat cards, no design persona cards and a memory file `personas/memory/qa.md`, when `validate.py personas` runs, then it prints no persona-layout warning naming the memory file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py::PersonaMemoryStoreTests::test_memory_files_are_never_read_as_misplaced_persona_cards

## Notes

- Run thirteen grooming (D0479):
  - AC1 must fail on: ids numbered per file, no Review-by stamped, or the later stories' fields not round-tripped through one parser (US1066/US1067/US1068 would each hand-roll one)
  - AC2 must fail on: evidence optional or never resolved, role checked before stem, or the write made where git never holds it
  - AC3 must fail on: list globs every memory file, so another persona's learnings leak into qa's listing
  - AC4 must fail on: personas/memory/ left out of the nested-layout exclusions beside seats/ and stakeholders/ in `validate.check_personas`
  - Persona: change Maya Okafor to Abena Osei (Primary). Serves End goal 4 (a cause is recorded and not repeated); also 2 via the evidence every entry carries.
  - Gaps: no ADR-012 trd.md edit in Affects (the note in the story says to add it); no existing pinning tests in Affects `(test_validate.py`, `test_lessons.py` for the `parse_project_lessons` entry-pattern parameter, `test_doc_coverage.py` for the new script's catalogue row); five ACs, brief wants 2-4 (AC2 and AC3 merged); the entry schema must name the fields US1066-US1068 write so those stories can be built from fixtures without 1066/1067 (this is what lets the chain be broken).
  - Line numbers in this story's notes are stale at HEAD (critic.py brief 2527->3755, `_lessons_block` 2358->3283, sprint.py `_CLOSE_CHAIN` 5668->5906, `cmd_sign` 9708->10474, retro.py extract 3535->4045, `lessons.phase_digest` 1864->1999, validate.py `check_personas` 1342->1278/1391); builder re-greps by name.
- From US1101 (2026-11-01): tools/tests/test_lean_trd_refresh.py's ADR-012 test fails if a path named in the TRD's ADR-012 'Not yet built' paragraph comes to exist. When this unit lands its script, edit sdlc-studio/trd.md's ADR-012 in the same commit; add trd.md to this unit's Affects when it is planned.
- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: ids numbered per file, so two personas' first learnings are both M-0001 and an approval or a strike naming one is ambiguous, or no Review-by stamped
- AC2 must fail on: evidence optional or never resolved, or the role checked before the stem, so an ambiguous key silently writes one persona's memory
- AC3 must fail on: the write made wherever the path points, so a memory git never holds is reported as recorded (LL0029)
- AC4 must fail on: list globs every memory file, so another persona's learnings leak into qa's listing
- AC5 must fail on: personas/memory/ left out of the nested-layout exclusions beside seats/ and stakeholders/ (validate.py:1342), so every seats-only project with memory is told its personas are misplaced
- Serves: Maya Okafor #2 (never lose the thread).
- Checked at HEAD (fixture probe): no persona_memory.py, no personas/memory/, no memory template; neither persona_resolve nor critic carries any persona-scoped record. `check_personas`' persona-layout advisory (validate.py:1342) excludes only seats/ and stakeholders/ from its nested scan, so memory/ would trip it.
- Key (panel Q3: confirmed): a seat's declared role (`qa`), so the memory follows the seat the ledger attributes verdicts to and a project briefing on the shipped default card still has one; a user persona's card stem. A key that is both is refused.
- Entry shape reuses the project-lessons log: `## M-NNNN: <title>`, `- **Field:** value` bullets, the learning as body. This story adds an entry-pattern parameter to `lessons.parse_project_lessons` (lessons.py:107 hard-codes `L-\d{4}`); `upsert_field`, `horizon_of` (:711) and `add_days` are reused, not copied (RFC0061: Option B on Option C's mechanics).
- States: proposed, approved, rejected, retired, and observed for usage evidence. Only add writes proposed; approve and revalidate move the rest. Whether an approved learning is live is read from the run record that listed it (see the signature story), never stamped here.
- Evidence resolves: an artefact id (`find_by_id`), a decisions row, a run with a tracked record, or a verdict reference `<unit> r<round>` the ledger holds.
- `recall` is `list --query`: CR0632 names both, one reader serves them. No `prune` (out of scope).
- Creates reference-persona-learning.md (memory, the learning loop, user-persona learning and promotion), indexed in help/references.md with its generated reading guide, so the loop's docs stay off reference-persona.md (522/600) and reference-workflow-personas.md (566/600).
- Config `personas.memory.validity_days`, default the lessons' 90, in reference-config.md (676 of its 695-line budget; two rows in this group).
- Ids `M-NNNN` are unique across every memory file; clones can collide as lesson ids can (LL0002), and the parser reports a duplicate.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-15 | Claude Opus 5.5 (run thirteen grooming, D0479) | Groomed for run thirteen: Persona Abena Osei, Affects with the existing tests that pin what it changes, Depends-on reduced to real dependencies, criteria rewritten to four or fewer, notes |
| 2026-11-15 | Claude Opus 5.5 (run thirteen planning, D0479) | Affects gains the registry files a new verb and a new script imply (the mechanics-verb list, the command surface, the root census, parser coverage, confinement and the command audit): run twelve lost five lands to their absence |
| 2026-11-15 | Claude Opus 5.5 (run thirteen) | Affects gains test_artifact.py: a script taking free prose on the command line must offer `--fields-file` and be listed in the prose-writer sweep's safe set (the land was refused for it) |
