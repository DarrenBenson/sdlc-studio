# Script Catalogue - Creation & mutation

<!-- Load when: you need the full detail for a script in this group. The lean
     index with all groups is reference-scripts.md. -->

Detail pages for the **creation & mutation** scripts. See
[reference-scripts.md](reference-scripts.md) for the full index across all groups.

## Scripts

### `artifact.py`

- `new --type retro|review`: the meta-artifacts are tool-created too
  (allocated id, template scaffold, index row). The meta index is bootstrapped from
  `templates/indexes/` on the first create when missing, so a project's first retro or
  review lands indexed rather than as reconcile drift. They stay outside the status
  machinery (`transition` refuses them by design).

Deterministic artifact create + close cascade. `new --type <any of the 8 numbered
types> --title ...` allocates a collision-free id, renders a valid scaffold (vocab-correct
status; a story gets a populated AC section), appends the index data-table row (built
generically from that index's own header, so it works for every type), recomputes counts,
and wires a story into its parent epic's Story Breakdown. `close --id` terminal-transitions
by id-prefix with the per-type terminal status (reusing transition). Replaces the ~10-step
hand cascade. Shares `file_finding.append_index_row`. On the empty-project first run it
creates a missing `<dir>/_index.md` from `templates/indexes/` (via
`file_finding.ensure_index`), so the first artifact of a type is indexed like every later
one; `--template full` grafts the rich `templates/core/` body onto the deterministic head.
`batch --type <t> --spec <items.json>` creates many artifacts of one type in a single
atomic pass: a reserved contiguous id block, every index row, and every story-to-
epic link wired in one go; a missing epic or id collision aborts before any write;
`--dry-run` previews the id map. Batch defaults to `--template full` (the fan-out case).

Every created artefact carries `> **Raised-by:** Name; type; version` (from `--author`,
or the invoking agent when absent - `SDLC_AUTHOR` when set), which schema v3 requires of
every artefact. The same resolved authorship names the artefact's opening Revision History
row and its index Author column - the name alone there, since the typed triple is
`Raised-by`'s job. Content the validator demands of a filled artefact can be supplied at
creation and the artefact is born clean: `--persona` and `--ac` (repeatable) for a story,
`--summary --steps --fix` for a bug, `--ac --impact --effort S|M|L` for a CR,
`--summary --option --recommendation` for an RFC. A bug and a CR also carry their
GROOMING - `--affects "a.py, b.py"` (the files the unit will touch) and `--effort S|M|L`
(the job size of the work, not its urgency) - and both creators REFUSE one without them,
because `sprint plan` refuses to plan such a unit: it cannot be sized, and two units
colliding on one file are invisible to the planner. That demand is not a second copy of the
rule: the body about to be written is handed to the planner's own breakdown predicate, so a
value it cannot read back as a path list (a bare word, a prose phrase) counts as no
`Affects` at all. A project that records `sprint.breakdown: judgement` gets a warning
instead of a refusal, exactly as its plan reports instead of blocking; omission is not an
opt-out. An RFC is exempt: it is not a unit of sprint work, and the files it touches are the
OUTPUT of the design it exists to settle - it records an `--affects` when the author has
one. Batch items take the same keys in the
spec JSON. Omit them and you get a scaffold: the `{{placeholder}}` slots stay for the
agent to fill, and `validate.py check` reports them as unfilled until it does - a scaffold
is not yet a specified artefact, and the creator does not pretend otherwise. This is by
design: a freshly created content-less scaffold is meant to fail validation until filled -
the validator doing its job, not a defect. Making it pass would mean writing filler into
the acceptance-criteria section, which satisfies the `no-ac` rule and silently promotes an
unspecified story to `specified` in conformance - the corruption the empty-scaffold check
exists to stop. So create then fill then validate; do not read the create-time report as a
failure.

A story's criteria may carry their proof: `--verify` (repeatable, positional with `--ac`)
writes the executable check on the matching AC, and `--target functional|conversational|soak|live`
writes its `Verification target`. A Verify expression is written **verbatim**, never
markdown-safed: it is a command `verify_ac` reads back and runs, and safing an underscore
rewrites it (`rg -q my_token src/` becomes ``rg -q `my_token` src/``). For a list-form verb
(`shell=False`) that is a corrupted literal argument - the check quietly stops checking what it
says it checks. For a **shell-backed verb**, which runs under `shell=True`, the same rewrite is
command substitution and the backticked token executes. A multi-line expression is refused.

Neither flag is ever invented: an AC given no Verify line gets none, because there is no
honest default - a
placeholder fails the validator and `manual` asserts a proof nobody ran. Conformance's
`verifiable` stage reports the gap out loud instead.

#### Single-line fields are refused, not stripped

A field written into a metadata line, an index cell, or a one-line bullet must be a single
line: `--title`, `--author`, `--epic`, `--persona`, `--priority`, `--ctype`, `--severity`,
`--effort`, `--affects`, `--provenance`, each `--ac`, each `--option`, each `--verify`, and the `revision`
verb's `--note`. A line break in one of them escapes the construct it is written into - the
value's tail lands as a metadata line, a table row, or an AC directive of its own, and the
tool signs it. So a title could open a second `> **Status:**` line above the real one (the
readers take the first, so the artefact is born whatever the title said), an author could
write a metadata line under the tool's provenance stamp, and an AC could inject a sibling
`- **Verify:** <command>` line that the verifier reads back and runs.

Both creators refuse such a value before anything is allocated or written, naming the field
and the character, and nothing lands on disk. The refusal covers every character that breaks
a line - newline, carriage return, vertical tab, form feed, the file/group/record separators,
NEL, U+2028, U+2029 - plus NUL, and it refuses a break wherever it sits: leading, interior or
trailing alike. That last point matters, because the writer emits the value it was handed, not
a trimmed one - a leading break renders a blank first cell and then a forged line, so it is
refused exactly like an interior one. A surrounding space is not a line break and is not
refused: the distinction is space versus line break, never position. It is a refusal, not a
repair: silently dropping the break would hand back exit 0 over a record that does not say what
the caller asked it to say. Detail that needs more than a line belongs in a body section
(`--summary`, `--steps`, `--fix`, `--impact`), which is free to be as long as it needs.

#### Template tiers

`--template` chooses scaffold richness: `minimal` (the default bare stub), `planning`, or
`full` (the whole `templates/core/<type>.md` body; `batch` defaults to it, the fan-out case).

**`planning`** is the lean pre-implementation tier for a story or epic. The full story
template has a structural floor near 170 lines once every mandated heading survives (an epic
near 150), so a pre-implementation story cannot get under it however economically it is
written - and a planning batch that has settled nothing about edge cases or rollback is
filing 170 lines of furniture per story. The planning tier carries what planning actually
settles - metadata, the user story, ACs with their `Verify:` and `Verification target:` lines,
scope, technical notes - and renders under 60 lines. The constraint chain, module views, edge
cases, test scenarios, dependencies, estimation and the rollback envelope arrive with
promotion, not before.

The tier is a contract, not just a shape. A story or epic **cannot transition to In Progress,
Review or Done while it is missing the sections the full template carries** - letting a lean
scaffold reach Done would be a lane with nothing to prove reading as proof.

**The gate reads the sections, not the stamp.** A stamp is a claim, and a gate that trusts a
marker its subject can rewrite is defeated by rewriting it. So `lib/tiers.py` - the one
authority the creator, the validator, the gate and the backstop all share - judges an artefact
this way:

- `planning`, or any tier **outside** `minimal|planning|full`, is unpromoted. Unknown **fails
  closed**: a typo must never be the thing that switches a gate off.
- a **`full` claim is checked** against the sections. Creation only ever stamps `planning`;
  `promote` alone writes `full`, and only after adding the sections - so verifying the claim
  costs no existing artefact and refuses a stamp that was rewritten without the work.
- `transition annotate` **refuses the `Template` field** (it is gate-protected, like `Status`
  and `Provenance`): annotating it to `full` would clear the gate and its backstop in one
  exit-0 line, with no waiver and no record.
- an artefact with **no stamp** is not judged by default. This is the measured boundary, not an
  oversight: an unstamped bare story is structurally identical to the pre-tier stories that
  reach Done today, and refusing it would refuse them.
  **`quality.require_full_sections: true`** drops the stamp from the decision entirely and
  judges every story and epic on its sections - the same rule, applied universally, as a
  project's choice rather than a silent breaking change.

`promote --id <ID>` is the remedy every refusal names. It grafts in each missing section in
template order, preserves everything already written, and re-stamps the tier `full`
(idempotent). Be clear about what that buys: the sections arrive as **empty
`{{placeholder}}` scaffolds** (an unfilled constraint table, an empty edge-case table), and
`validate.py`'s placeholder rule only inspects the AC section - so a promoted artefact is
validator-clean with an empty constraint chain. Promotion gives you the headings and the
obligation to fill them; it does not fill them, and it is not evidence that anyone did. The
gate is **not** `--force`-bypassable, because the remedy adds the sections rather than waiving
them. `conformance.py` backstops the whole thing with a `promoted` stage on Done stories,
sharing the same authority, so a hand-edited `Status: Done` cannot walk around it.

`planning` is defined for story and epic; for every other type, whose minimal scaffold is
already that lean, it renders the minimal shape and no gate applies.

### `init.py`

Deterministic greenfield initialiser - `init` is now an executable, not a manual
checklist. `run` creates the full `sdlc-studio/` directory tree, pre-creates every per-type
`_index.md` (reusing `file_finding.ensure_index`), seeds
`sdlc-studio/.config.yaml` and the agent-instructions starters (`AGENTS.md`/`CLAUDE.md`)
from templates, and with `--scaffold` seeds the singleton docs (prd/trd/tsd/personas).
`--detect` infers the stack; idempotent (never overwrites without `--force`); `--dry-run`
previews every write so the workflow can show the config and confirm once before applying.
It also seeds an empty `sdlc-studio/decisions.md`.

### `decisions.py`

Project decisions log - the canonical home for load-bearing decisions, both
product (scope cuts, resolved PRD open questions) and implementation conventions (error
envelope, ID scheme, token strategy, migrations, test harness). `add --decision ...
--rationale ...` appends an auto-numbered, dated row to `sdlc-studio/decisions.md`; `list`
prints it (filterable by status); `promote --from PRD-OQ3 ...` records a resolved PRD open
question with a back-link (one record, two views). `waive --leg <prd|trd|tsd|personas>
--rationale ...` (or `--subject rule:<name>` for the general case) records a machine-detectable
waiver - a decision row `waiver: <subject>` stating a required leg or rule is intentionally out
of scope here; `waiver_for(subject)` looks it up by anchored equality (a superseded waiver, or a
row that merely mentions the subject, does not hold). Append-only and greppable, so the spine
lives in one place and feeds the handoff context delegated agents read - distinct from the
sprint per-tranche ledger (`ledger.py`).

### `transition.py`

Deterministic status transition + cascade. `set --id <ID> --status <new>` sets `Status`,
syncs the index row + summary counts (`reconcile.apply_type`), and ticks/unticks a story's
checkbox in its epic's Story Breakdown; `index_synced` is the true post-state. **A story ->
Done is gated on its AC-verify result** (red or never-run executable ACs refuse the
transition; `--force` overrides; manual-only / AC-less and non-story types are never gated).
**A story or epic -> In Progress / Review / Done is refused while it is missing the sections
the full template carries** (`artifact.py promote --id <ID>`), on every entry to an
implementation status and in dry-run too. The judgement is keyed on the sections rather than
the tier stamp (`lib/tiers.py`), so an unknown tier fails closed and a rewritten `full` stamp is
refused as a claim. Unlike the AC-verify gate this one is not `--force`-bypassable, and
`annotate` refuses the `Template` field, because the remedy adds the sections rather than
waiving them. Unstamped artefacts are unaffected unless `quality.require_full_sections` is set.
**Schema v3:** a finding leaving `inbox` is gated too - a structured `--triaged-by` (refused
without one), triager != raiser (separation of duties; solo-human warns), `--triage-severity`
recorded. Dormant on v2. **A blocked transition reports EVERY unmet gate in one refusal**
(depth AND triage AND plan-review together), so clearing them costs one round-trip, not one
per gate. `annotate --id <ID> --field <Name> --value <v>` deterministically sets/updates one
metadata field (e.g. `Verification depth`) in place - the stamp verb; no more hand edits.

### `archive.py`

Index archival for large boards - **the one archive writer** (`reconcile` reads the archive,
never writes it). `archive --type <t> --release <r>` moves a
type's terminal master-table rows into `<type>/archive/{release}/{type}.md` and leaves a
bullet pointer in the live index - rows move, artifact files stay. `parse_index` unions
the archive sub-indexes so the census stays correct. Explicit, idempotent per release.

- `archive`: move terminal rows of one type by release (`--dry-run` to preview)

Convention: `reference-outputs.md#index-archival`.

### `file_finding.py`

Deterministic Bug/CR/RFC filer for audit findings. Allocates a
collision-free ID, renders a STRUCTURED artifact (required sections enforced - it
refuses a hollow stub), stamps the typed authorship of record, appends the index row,
and recomputes the index counts (reusing reconcile's pass).

- `file --type bug|cr|rfc --title ... <fields>`: write one artifact
- `rebuild --type <t>`: recompute a type's index summary counts

Required fields per type are the ones the validator demands of a filed artefact, plus the
grooming the PLANNER demands of a unit: a bug carries its evidence
(`--severity --summary --steps --fix`) and its grooming (`--affects --effort S|M|L`), a CR
its criteria, impact and effort (`--priority --ctype --summary --ac --impact --effort S|M|L`)
and its `--affects`, an RFC its options (`--summary --option`) and no grooming at all (it is
not a sprint unit). The filer refuses an ungroomed bug or CR for the same reason it refuses a
hollow one: `sprint plan` would refuse to plan it, and an artefact one end of the pipeline
writes and the other rejects is a repair handed to an operator who has less context than the
author had. `--author "Name; type; version"` (type is
`human|persona|agent`) is stamped as `Raised-by` and names the Revision History row it
opens; with no author given, the invoking agent is stamped (`SDLC_AUTHOR` when set). A
Low-severity finding that consolidates carries the same authorship into the consolidation
CR. What the filer writes passes `validate.py check` as written - a creator never emits an
artefact its own validator rejects. The filer shares the single-line refusal above: a title,
author, severity, priority or criterion carrying a line break is refused before any write,
from the same authority, so neither creation path is an escape hatch for the other.

Full methodology: `reference-audit.md`.

### `retro.py`

The retro spine: the deterministic half of the retrospective, so the close gate has
something to interrogate other than the filesystem.

- `validate --id RETROxxxx`: the CONTENT check the close gate calls. Required sections
  present, at least one real lesson (a `{{placeholder}}` is the template talking, not the
  author), and a disposition recorded for every finding. A retro that exists but says
  nothing is not a retro, and a gate that only checks the filename is satisfied by `touch`.
- `dispose --id RETROxxxx`: report each finding as **filed** (an artefact id), **declined**
  (with a reason) or **undecided**. Read-only; non-zero while any finding is undecided.
- `extract --id RETROxxxx`: lift the retro's `## Lessons` bullets into the project lessons
  log, so a lesson written in a retro reaches the digest the next sprint plan prints.
  Idempotent by content - re-running converges rather than duplicating.

**The disposition rule.** A finding is dispositioned when it is either filed as an artefact
or **declined with a reason**. Declining is a first-class answer and is equally green, so
honesty costs exactly what noise costs and there is nothing to game. What does not pass is
silence: a finding written down and left to rot. The template asks the question directly
("are there any CRs or Bugs you want to raise?"), because a gate on a question nobody was
asked is just a wall.

Related: `reference-retro.md`, `help/retro.md`, `help/lessons.md`.

### `persona_gen.py`

Deterministic floor of team/stakeholder persona generation - the model-driven flow
(`reference-persona-generate.md#team-generation`) does the judgement; this owns what must
never be improvised:

- `stamp --file <card>` - mark a just-generated card `provisional-unverified` with a
  content hash (an HTML comment beside the `role:` comment - deliberately not the
  artefact `Provenance:` field, which is a verify_ac control with different semantics)
- `classify [--file | --root]` - `authored` / `generated-pristine` / `generated-edited`;
  an operator's edit to a generated card changes its hash, so never-clobber treats it as
  authored from then on
- `accept [--file | --root]` - clear provisional labels (the flow's batch-accept close
  and the `persona review` path); a `reviewed` card refuses re-stamping

`status` surfaces the count of still-provisional cards; `validate.py seats
--require-stamp <written cards>` is the error-level schema floor the generation flow
must pass before completing (named files must carry a valid stamp or reviewed marker).

### `next_id.py` (read-only)

- `allocate`: next free ID for a type (`--remote` also scans `origin/main`)
- `scan`: list IDs in use

Covers the 8 pipeline types plus the **meta-artifacts** `review` (RV####) and `retro`
(RETRO####), so review/retro ids are allocated, never hand-picked - run `next_id.py
allocate --type review` before writing one, the same discipline as `artifact.py new`.
(Lessons `LL####` have their own manager in `lessons.py`; personas are named.) Read-only;
runs `git ls-tree` (no fetch). Backs ID assignment in `reference-cr.md` and doctrine rule 13.

### `ledger.py`

The append-only per-tranche decisions ledger. `record` appends a decision + rationale to `sdlc-studio/decisions/<tranche>.md`; survives context compaction so a reset resumes from disk.

### `rfc.py`

RFC helpers - the `rfc decide` multi-RFC decision digest (per-draft open-decision + workstream counts + ready flag) and RFC index/table helpers (escaped-pipe-aware via sdlc_md).
