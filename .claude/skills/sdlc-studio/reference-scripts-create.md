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
refuses a hollow stub), appends the index row, and recomputes the index counts
(reusing reconcile's pass).

- `file --type bug|cr|rfc --title ... <fields>`: write one artifact
- `rebuild --type <t>`: recompute a type's index summary counts

Full methodology: `reference-audit.md`.

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
