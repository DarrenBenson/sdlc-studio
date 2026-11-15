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
is never ambiguous. Two clones can still mint the same id, as lesson ids can; the reader refuses
a duplicate in one file, and `add`, `set_field` and the close's listing refuse an id two files
hold, naming both, rather than picking one.

| Field | Written by | Meaning |
| --- | --- | --- |
| Persona | `add` | The key the entry belongs to |
| Evidence | `add` | Ids that resolve on disk: an artefact, a decisions row, a run a report names, or `<unit> r<round>` the review ledger holds |
| Added | `add` | The date it was recorded |
| Review-by | `add` | Added plus `personas.memory.validity_days` (default 90) |
| State | `add`, then approval and revalidation | proposed, approved, rejected, retired, or observed |
| Approved-by, Addresses, Listed-in, Struck, Retired | later verbs, through `set_field` | Who approved it, what it addresses, the close that listed it, a strike, a retirement |
| Run, Retro | `propose` | The run the learning looks back on, and the retro whose seat record supplied its evidence |
| Rejected-by, Reason, Decided | `approve` | Who rejected it, the reason given for a rejection or for addressing nothing, and the date of the decision |

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

A body holding a level-two heading line (`##` then a space) or a `- **Field:** value` line is refused: the first would read
back as a new entry and the second as the entry's own field, so a learning could set its own
State or Evidence. Whatever its shape, `add` refuses a learning its reader would not read back
as exactly the entry stamped: one new entry, its id and title, every field it set and no other,
and the body as its prose.

---

## From a retro {#from-a-retro}

Each seat writes what it will do differently in its own words, while its evidence comes from
the ledger, so a seat cannot excuse itself with its own account.

```bash
python3 scripts/persona_memory.py learn-brief --persona qa --retro RETRO0002
python3 scripts/persona_memory.py propose --persona qa --retro RETRO0002 \
  --from-file sdlc-studio/.local/persona-learning/RETRO0002-qa.md [--title "..."] [--run RUN-...]
```

`learn-brief` carries the seat's own record from `retro.py seats --id <retro> --format json`
and nothing of another seat's, then its adverse items, each with the key an approval cites:
every keyed item the record lists outside its verdicts (`round:<unit>r<k>` for a defect found
after its approval, and any later kind such as `bug:<id>`), and each round a blocking finding
stopped on a unit it built. It says a learning cannot change the card's Non-Negotiables or
Authority, names the file to write under `sdlc-studio/.local/persona-learning/` and the
`propose` command, and ends with the seat's card framed with its live learnings.

`propose` stores the file's text as the body as written, less its outer blank space, and
its first line as the title unless `--title` is given. Evidence is the ids the record lists (its verdicts as `<unit> r<round>`,
the units it built, its adverse items' ids), never ids the text names. Run is the run the
retro's close names: `--run`, else the open run, else the retro. It exits 2, writing nothing,
for a seat with no record in the retro (no verdict, no unit built, no adverse item) and while
that seat's earlier proposal for the same run is still proposed.

### Approval {#approval}

Another seat checks each proposed learning against the ledger and the card before it can go
live.

```bash
python3 scripts/persona_memory.py approve-brief --id M-0001 --seat product
python3 scripts/persona_memory.py approve --id M-0001 --reviewer "Lena Marsh (product)" \
  --addresses round:US0001r2[,bug:BG0002]
python3 scripts/persona_memory.py approve --id M-0001 --reviewer "Lena Marsh (product)" \
  --addresses none --reason "keeps a habit that held"
python3 scripts/persona_memory.py approve --id M-0001 --reviewer "Lena Marsh (product)" \
  --reject --reason "..."
```

`approve-brief` carries the learning verbatim, the adverse items its seat's record lists in the
retro it was proposed from, with their keys, that card's Non-Negotiables and Authority
sections, the question whether the learning contradicts or loosens them, and the three commands
above, then frames the approving seat's card. An approval writes State approved, Approved-by,
Decided and Addresses; a rejection writes State rejected, Rejected-by, Decided and Reason, and a
rejected learning never reaches a brief. Both exit 2, writing nothing, for the learning's own
seat, judged by the `(<role>)` group the reviewer names, never by name, so a second holder of
that card is refused too. `approve` also refuses a reviewer naming no `(<role>)` group or a role
no card declares, an entry that is not proposed, and an approval that names no adverse item
the record lists and is not `none` with a reason.

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
