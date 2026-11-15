# SDLC Studio Reference - Persona Learning

<!-- Load when: recording, reading or briefing a persona's learnings (persona_memory.py) -->

How a persona keeps what it learns between briefs: the memory file, its entries, and how a
learning reaches the next brief.

---

## Memory {#memory}

Each persona's learnings live in one committed file beside its card:
`sdlc-studio/personas/memory/<key>.md`. The key is a seat's declared role (`qa`, `engineering`,
`product`, or a role a project seat card declares), so the memory follows the seat the review
ledger attributes verdicts to, and a project still briefing on the shipped default card has
one. A user persona's key is its card stem (`maya-okafor-founder-engineer`). A key that is
both a seat role and a card stem is refused, because whose memory it is cannot be told.

The file is committed, never kept under `.local/`: a learning held on one machine is lost to
every other clone. `persona_memory.py add` refuses to write when a gitignore rule matches the
memory directory, and names the rule.

### Entry shape {#entry-shape}

An entry has the project lessons log's shape and is read by the same parser:

```markdown
## M-0001: A retry loop hides a race

- **Persona:** qa
- **Evidence:** US0001, D0123
- **Added:** 2026-11-15
- **Review-by:** 2027-02-13
- **State:** proposed

The learning, in prose.
```

Ids are `M-NNNN`, unique across every memory file, so an approval or a strike that names one
is never ambiguous. Two clones can still mint the same id, as lesson ids can; the reader
refuses a file holding a duplicate rather than picking one.

| Field | Written by | Meaning |
| --- | --- | --- |
| Persona | `add` | The key the entry belongs to |
| Evidence | `add` | Ids that resolve on disk: an artefact, a decisions row, a run a report names, or `<unit> r<round>` the review ledger holds |
| Added | `add` | The date it was recorded |
| Review-by | `add` | Added plus `personas.memory.validity_days` (default 90) |
| State | `add`, then approval and revalidation | proposed, approved, rejected, retired, or observed |
| Approved-by, Addresses, Listed-in, Struck, Retired | later verbs, through `set_field` | Who approved it, what it addresses, the close that listed it, a strike, a retirement |

### Commands {#commands}

```bash
python3 scripts/persona_memory.py add --persona qa --title "A retry loop hides a race" \
  --body "..." --evidence US0001
python3 scripts/persona_memory.py list --persona qa [--query race] [--format json]
python3 scripts/persona_memory.py recall --persona qa --query race
```

`add` writes the entry as proposed and exits 2, writing nothing, when it has no evidence, a
cited id resolves to nothing, the key is unknown or ambiguous, or the repository would ignore
the file. `list` and `recall` read the one persona's file, each learning with its state and
horizon.

---

## Into the brief {#into-the-brief}

A review brief (`critic.py brief --seat <seat>`) and every `persona_resolve.py` framing
(`resolve --seat <seat> --render build|review`, `resolve-consult --role <role>`) carry the
seat's own live learnings in a block labelled with the render. Another seat's file is never
read.

- **Live** means State approved, the Review-by date not yet passed, and listed by a close
  whose run is signed and did not strike it. A proposed learning is not carried; an approved
  one past its horizon, one whose run awaits its signature and one no signed close has listed
  are not carried, and the block counts each.
- **Ranked** by relevance, then recency. A learning is relevant to a unit when a unit its
  evidence cites shares an Affects path with the unit being briefed; no field records it, so
  nothing can set it wrongly. A brief with no unit ranks by recency alone.
- **Capped** at `personas.memory.inject_max` (default 5). The block says how many more live
  learnings the cap withheld.
- **Bounded**: each learning is carried as its id, its title and a gist of at most 200
  characters, so one long entry cannot crowd out the criteria the brief exists to carry.

A memory file that cannot be parsed is reported in the block as unreadable, naming the file,
so a brief that lost its learnings is never mistaken for one that has none. A seat with no
memory file is told none are recorded.

### Listed at the close, struck at the signature {#listed-and-struck}

`sprint.py close` lists every approved learning not yet live on the retro, whatever wrote it,
and stamps each Listed-in with the run; the run record names the ids. `sprint.py sign
--strike M-NNNN --strike-reason "..."` strikes any of them as it seals the run, recording the
principal, the date and the reason on the entry and on the run record; `list` shows the
strike. A strike naming an id no memory file holds, or one this run's close did not list, is
refused with every reason named, and nothing is sealed or written. Signed is read from the
run's tracked record in `sdlc-studio/reports/runs/`, never written into memory, so `sprint.py
reopen` holds the run's learnings until it is signed again: at once in the checkout that
reopened it, and in every clone once the re-close files the record.

---

## See Also

- `reference-persona.md` - persona cards and their schema
- `reference-scripts-review.md` - the `persona_memory.py` catalogue entry
- `reference-config.md` - the `personas.memory` settings
