# US1058: persona_memory.py keeps each persona's evidenced learnings in a committed memory file beside its card

> **Status:** Draft
> **Delivers:** CR0632
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/personas/memory-template.md, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/help/references.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py, changelog.d/US1058.md
> **Epic:** EP0287
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose review seats forget everything when each brief ends
**I want** `persona_memory.py add`, `list` and `recall` to keep each persona's learnings, with evidence, a date, a validity horizon and a state, in `sdlc-studio/personas/memory/<persona>.md`
**So that** what a seat learns is a committed record every clone reads, never a note in one machine's .local

## Acceptance Criteria

- **AC1:** Given a project with a qa seat card and Maya Okafor's card, when `persona_memory.py add --persona qa --title ... --body ... --evidence US0001` and then the same with `--persona maya-okafor-founder-engineer` run, then `sdlc-studio/personas/memory/qa.md` holds `## M-0001` and `memory/maya-okafor-founder-engineer.md` holds `## M-0002`, each with Persona, Evidence, Added, a Review-by 90 days on and State proposed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py::PersonaMemoryStoreTests::test_add_writes_a_stamped_proposed_learning_with_a_unique_id
- **AC2:** Given an add with no `--evidence`, one whose evidence cites only ids that resolve to nothing on disk, one whose `--persona` names neither a declared seat role nor a persona card, and one whose key is both a role and a card stem, when `persona_memory.py add` runs, then each exits 2 naming its reason and no file is written.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py::PersonaMemoryStoreTests::test_an_unevidenced_unknown_or_ambiguous_persona_is_refused
- **AC3:** Given a `.gitignore` rule matching `sdlc-studio/personas/memory/`, when `persona_memory.py add` runs, then it exits 2 naming the ignore rule and writes nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py::PersonaMemoryStoreTests::test_a_memory_git_ignores_is_refused
- **AC4:** Given entries for qa and product in several states, when `persona_memory.py list --persona qa --query race` runs as text and as `--format json`, then only qa's entries whose title or body mention race are listed, each with its state and horizon.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py::PersonaMemoryStoreTests::test_list_and_recall_read_one_personas_memory
- **AC5:** Given a project with seat cards, no design persona cards and a memory file `personas/memory/qa.md`, when `validate.py personas` runs, then it prints no persona-layout warning naming the memory file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py::PersonaMemoryStoreTests::test_memory_files_are_never_read_as_misplaced_persona_cards

## Notes

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
