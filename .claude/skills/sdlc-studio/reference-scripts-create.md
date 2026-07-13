# Script Catalogue - Creation & mutation

<!-- Load when: you need the full detail for a script in this group. The lean
     index with all groups is reference-scripts.md. -->

Detail pages for the **creation & mutation** scripts. See
[reference-scripts.md](reference-scripts.md) for the full index across all groups.

## Scripts

### `artifact.py`

- `new --type retro|review`: the meta-artifacts are tool-created too
  (allocated id, template scaffold, index row where a meta index exists) - they stay
  outside the status machinery (`transition` refuses them by design).

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
`--summary --option --recommendation` for an RFC. Batch items take the same keys in the
spec JSON. Omit them and you get a scaffold: the `{{placeholder}}` slots stay for the
agent to fill, and `validate.py check` reports them as unfilled until it does - a scaffold
is not yet a specified artefact, and the creator does not pretend otherwise.

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
question with a back-link (one record, two views). Append-only and greppable, so the spine lives
in one place and feeds the handoff context delegated agents read - distinct from the
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

Index archival for large boards. `archive --type <t> --release <r>` moves a
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

Required fields per type are the ones the validator demands of a filed artefact: a bug
carries its evidence (`--severity --summary --steps --fix`), a CR its criteria, impact
and effort (`--priority --ctype --summary --ac --impact --effort S|M|L`), an RFC its
options (`--summary --option`). `--author "Name; type; version"` (type is
`human|persona|agent`) is stamped as `Raised-by` and names the Revision History row it
opens; with no author given, the invoking agent is stamped (`SDLC_AUTHOR` when set). A
Low-severity finding that consolidates carries the same authorship into the consolidation
CR. What the filer writes passes `validate.py check` as written - a creator never emits an
artefact its own validator rejects.

Full methodology: `reference-audit.md`.

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
