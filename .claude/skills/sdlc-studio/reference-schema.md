# Artefact Schema Contract

> **Schema version 3.** This document is the public artefact-format contract for a
> `sdlc-studio/` workspace: the on-disk format that external tooling may read and
> build against. It describes what exists today and invents nothing. New workspaces are
> stamped schema v3 at init; a project created before v3, or one that has not upgraded,
> is v2 - both eras are described below and the two differ only in the id scheme and a
> few v3-only enforcement lanes.

The `sdlc-studio/` workspace was designed as the skill's private working state, but it
is now read by tooling outside the skill: dashboards, orchestrators and sync tools that
browse, search, score and execute against the artefact tree. That makes the format an
interface whether or not it is declared as one. This document gathers the guarantees so
a consumer can parse the tree against a promised contract instead of vendoring field
knowledge and chasing every release.

## Binding rules

Three rules govern the contract:

1. **`validate.py` is the executable definition.** The prose here describes the format;
   `scripts/validate.py` is the machine-checkable authority. Where the two ever disagree,
   the validator wins and the disagreement is a bug in this document. A drift guard
   (`scripts/tests/test_schema_contract.py`) fails the build if the vocabularies below
   diverge from what the code enforces, so the doc cannot rot silently.
2. **Health judgements stay upstream.** `validate.py`, `audit.py` and `reconcile.py`
   define what a healthy workspace means. A consumer should run the skill's conformance
   tooling (or a future published descriptor), never re-implement those rules, because a
   re-implementation will drift from the definition it copied.
3. **The index is derived output.** Each `_index.md` is generated from the artefact files,
   not authored. The contract documents its format so a reader can parse it, but the only
   write path is the skill's own scripts (`artifact.py`, `reconcile.py`); a consumer treats
   it as read-only and never a source of truth over the files it summarises.

## Scope

**Contracted (schema v2 and v3):** the on-disk artefact format only - the six surfaces below,
plus the compatibility policy for changing any of them.

**Uncontracted:** `.local/` runtime evidence JSON (sprint plan, verify reports, telemetry)
is explicitly **uncontracted** in every schema version to date. Its shape may change without a
version bump. A future separately versioned annex is the intended path for evidence consumers; until
it ships, treat everything under `sdlc-studio/.local/` as private runtime state. Also out of
scope: any consumer-specific concern, any push or notification mechanism, any API surface
beyond files on disk, and the skill's internal script interfaces (those remain free to change).

## Id Grammar

Every artefact carries a type-prefixed id, unique within its type. Two id eras coexist,
selected per project by `schema_version`.

**Type prefixes** (the leading letters of every id):

| Prefix | Type |
| --- | --- |
| `EP` | epic |
| `US` | story |
| `PL` | plan |
| `BG` | bug |
| `CR` | change request |
| `RFC` | RFC |
| `IS` | issue |
| `TS` | test-spec |
| `WF` | workflow |

**v2 sequential form (schema version 2, legacy projects):** a prefix, an optional dash, then a
four-digit zero-padded number - `US0001`, `EP0042`, `CR-0007`, `BG0182`. `CR` and `RFC`
display with the dash (`CR-0007`); the others display without (`US0001`). Filenames may be
lower-case (`cr0001.md`); ids parse case-insensitively and normalise to upper-case. The
number is allocated as the next free integer for that type, remote-aware so a stale local
checkout does not re-mint an id the remote already used.

**v3 short-ULID form (schema version 3, new projects):** a prefix, a dash, then eight or more
Crockford base32 characters - `BG-01JQK3F8`. The Crockford alphabet is
`0123456789ABCDEFGHJKMNPQRSTVWXYZ` (no `I`, `L`, `O`, `U`). The suffix extends beyond eight
characters only on a rare directory clash. A four-digit numeric tail is too short to be a
v3 id, so the two eras never collide.

A filename is `<id>-<kebab-slug>.md` (for example `US0258-author-reference-schema-md.md`);
the id is the stem up to the first slug separator.

## Directory Layout

Each artefact type lives in a fixed directory under `sdlc-studio/`:

| Type | Directory |
| --- | --- |
| epic | `sdlc-studio/epics/` |
| story | `sdlc-studio/stories/` |
| plan | `sdlc-studio/plans/` |
| bug | `sdlc-studio/bugs/` |
| change request | `sdlc-studio/change-requests/` |
| RFC | `sdlc-studio/rfcs/` |
| issue | `sdlc-studio/issues/` |
| test-spec | `sdlc-studio/test-specs/` |
| workflow | `sdlc-studio/workflows/` |

Each directory holds one markdown file per artefact plus a derived `_index.md`. Singleton
documents live at the workspace root, not in a per-type directory: `prd.md`, `trd.md`,
`tsd.md`, `personas.md`, `decisions.md`, `constitution.md`. Terminal artefacts may be moved
to an `archive/` subdirectory of their type directory; this keeps the live index bounded and
does not change the format of the files themselves.

## Header Fields

Every artefact opens with an H1 (`# US0258: Title`) followed by a blockquote metadata block,
one field per line in the form `> **Field:** value`. `Status` is the only field common to all
types and is always present. The remaining vocabulary is per type; the fields a type may carry:

| Type | Header fields (beyond `Status`) |
| --- | --- |
| epic | `Owner`, `Reviewer`, `Created`, `Target Release`, `GitHub Issue` |
| story | `Epic`, `Persona`, `Serves`, `Owner`, `Reviewer`, `Estimated-by`, `Delivered-by`, `Created`, `GitHub Issue`, `Affects`, `Points`, `Depends on` |
| bug | `Severity`, `Priority`, `Points`, `Estimated-by`, `Delivered-by`, `Reporter`, `Assignee`, `Created`, `Verification depth`, `Affects` |
| change request | `Priority`, `Type`, `Size`, `Requester`, `Estimated-by`, `Delivered-by`, `Date`, `Affects`, `Depends on`, `GitHub Issue` |
| RFC | `Priority`, `Size`, `Author`, `Date`, `Spans`, `Related`, `Supersedes / Superseded by`, `Cross-repo note` |

Fields are additive: a consumer must tolerate an unknown field rather than reject the
artefact, because a new optional field is a minor-version change (see Compatibility Policy).
Link fields (`Epic`, `Depends on`, `Serves`, `Parent`, `Decomposed-into`) carry artefact ids
and are how the graph is traversed.

## Status Vocabulary

Every artefact's `Status` field holds one value from its type's vocabulary. The **terminal**
states are absorbing: a unit at one is a closed outcome whose index row carries no live signal.
States that can still re-activate (`Blocked`, `Deferred`, `Planned`, `Paused`) are deliberately
not terminal. Transitions are gated by `scripts/transition.py`, which also cascades the change
into the index and any parent epic; a status is never edited into a file by hand.

| Type | Status vocabulary (lifecycle order) | Terminal states |
| --- | --- | --- |
| epic | Draft, Ready, Approved, In Progress, Done | Done |
| story | Proposed, Draft, Ready, Planned, In Progress, Review, Blocked, Done, Won't Implement, Deferred, Superseded | Done, Won't Implement, Superseded |
| plan | Draft, In Progress, Complete, Superseded | Complete, Superseded |
| bug | Open, In Progress, Fixed, Verified, Closed, Won't Fix, Superseded | Fixed, Verified, Closed, Won't Fix, Superseded |
| cr | Proposed, Approved, In Progress, Complete, Rejected, Deferred, Superseded, Blocked | Complete, Rejected, Superseded |
| rfc | Draft, In Review, Accepted, Superseded, Withdrawn | Accepted, Superseded, Withdrawn |
| issue | Open, Triaging, Triaged, Resolved, Closed, Won't Fix, Superseded | Resolved, Closed, Won't Fix, Superseded |
| test-spec | Draft, Ready, In Progress, Complete, Superseded | Complete, Superseded |
| workflow | Created, Planning, Testing, Implementing, Verifying, Reviewing, Checking, Done, Paused, Superseded | Done, Superseded |

The table above is the base vocabulary, shared by both schema eras. A project may extend a
type's vocabulary with its own statuses via `status_vocab.<type>` in `sdlc-studio/.config.yaml`;
those are additive to the base.

### Schema v3 additions

Schema v3 adds one status - a leading `inbox` triage lane - to the finding types only: an
agent-filed finding lands in `inbox`, and a different seat triages it into the workflow proper.
It is prepended to the base vocabulary for these types; it is dormant under schema v2.

| v3-only status | Applies to types |
| --- | --- |
| inbox | bug, cr, rfc |

## Verify DSL

A story's acceptance criteria may carry executable `Verify:` lines that `scripts/verify_ac.py`
runs to prove the criterion holds. The format is a bullet under the AC:

```markdown
- **Verify:** <command>
```

The command is the executable proof. Supported verbs:

- **`shell <command>`** - run the command; a zero exit is a pass. The general escape hatch;
  the `shell` keyword is optional for a bare command line.
- **`grep <pattern> <path>`** - assert the pattern is present in the file. Takes no flags; the
  pattern and path are positional.
- **`pytest <target>`** / **`jest <target>`** / other test-runner invocations - run under
  `shell`; the runner's exit code is the verdict.

A back-annotation records the last result: `- **Verified:** yes | no | stale | manual`,
optionally with a note in parentheses. `verify_ac.py` writes this; `transition.py` gates a
story reaching `Done` on its verifiers passing. Only a story's `- **Verify:**` line is
executed - a command-shaped `Verify:` on a bug or CR is documentation, not an executed check.

## Index Format

Each type directory carries a derived `_index.md` - a registry generated from the artefact
files, never authored. It opens with a `**Last Updated:**` line and a Summary table counting
artefacts by status, then lists the artefacts (grouped by parent epic for stories). A row:

```markdown
| ID | Title | Status | Points | Owner |
| --- | --- | --- | --- | --- |
| [US0258](US0258-author-reference-schema-md.md) | Title | Ready | 5 | - |
```

The ID cell links to the file; the Status cell mirrors the file's `Status` field. Because the
index is derived, `reconcile.py` recomputes it from a file census and any drift between a row
and its file is a reconcile finding, resolved in favour of the file. A consumer reading the
index for a quick overview is fine; a consumer treating it as authoritative over the files is
not - the files are the source of truth.

## Compatibility Policy

A consumer pins a workspace's format by reading `schema_version` from that project's
`sdlc-studio/.config.yaml`. Where the value comes from:

- **A new workspace is stamped `schema_version: 3` at init** (from the skill's
  `templates/config.yaml`). This is the current schema version, and it is what this document's
  masthead states.
- **A project that declares no `schema_version` reads `2`** - the skill's fallback default
  (`config-defaults.yaml`), which is why a legacy workspace created before the stamp is treated
  as v2. A project is never auto-flipped between versions; it moves only when it is upgraded
  explicitly (`project upgrade` / `migrate_v3`).

The version moves under one rule:

- **Additive change = minor bump.** A new optional header field, a new status value, or a new
  artefact type is backward-compatible: existing files stay valid and existing consumers keep
  working. This is why a consumer must tolerate unknown fields and statuses rather than reject
  them.
- **Rename, removal, or semantic change = major bump, with a `migrate` path shipped in the
  same release.** Renaming a field, dropping a status, or changing what an existing surface
  means can break a consumer, so it requires a major version increment and a migration the
  skill ships alongside the change - never a silent break.

The worked example is the schema v2 to v3 change: v3 renames the id scheme (sequential to
short ULID) and adds enforcement lanes, so it is a major step with `migrate_v3` as its shipped
path. A legacy v2 project moves to v3 only by running the migration, which stamps
`schema_version: 3` into its config after converting the tree. Hand-editing the stamp migrates
nothing; only `migrate` changes the format on disk.

## See Also

- `reference-config.md` - the `schema_version` key and every other project configuration option
- `reference-verify.md` - the full executable AC verifier DSL
- `reference-outputs.md` - status transitions and the completion cascades
- `reference-reconcile.md` - how the derived index is kept in sync with the files
