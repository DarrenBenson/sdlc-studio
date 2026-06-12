# SDLC Studio Reference - GitHub Issues Sync

Two-way sync between local Change Requests, Stories, and Epics and
GitHub Issues. Uses the `gh` CLI for every GitHub interaction - no
token handling, no custom HTTP client. Teams that already live in
GitHub Issues get SDLC Studio value without abandoning their tracker;
solo developers who don't use Issues pay zero cost by leaving the
link fields blank.

<!-- Load when: running cr sync, story sync, project sync, or setting up GitHub Issues integration -->

## Reading Guide

| Section | When to Read |
| --- | --- |
| Design | When deciding whether to adopt GitHub sync |
| Setup | When enabling sync on a new project |
| Labels | When wiring labels into a GitHub repo |
| Push Workflow | When local records should appear in GitHub |
| Pull Workflow | When GitHub Issues should appear as local records |
| Cascade Workflow | When a merged PR should tick the Story Completion Cascade |
| State File | When debugging sync behaviour |
| Conflict Policy | When a conflict is reported |
| See Also | Cross-links |

## Design {#gh-design}

A Change Request, User Story, or Epic file and its matching GitHub
Issue are **two representations of the same record**. Neither owns
the other. The local file is the durable, reviewable source; the
Issue is the discussion surface. Sync is idempotent in both
directions.

The link is a single optional metadata line in the local file:

```markdown
> **GitHub Issue:** #42
```

Missing line means the record is not synced. Present line means it's
linked. Teams can adopt sync incrementally: link existing CRs one at
a time, or turn it off entirely on a per-project basis.

## Setup {#gh-setup}

**Prerequisites:**

- `gh` CLI installed and authenticated (`gh auth status`)
- A GitHub repo (the script reads `origin` from the working dir)
- Write access to the repo's Issues

**One-time label creation:**

```bash
gh label create "sdlc:cr"                --color 0366D6 --description "SDLC Change Request"
gh label create "sdlc:story"             --color 0E8A16 --description "SDLC User Story"
gh label create "sdlc:epic"              --color 5319E7 --description "SDLC Epic"
gh label create "sdlc:status:proposed"   --color FBCA04
gh label create "sdlc:status:approved"   --color FBCA04
gh label create "sdlc:status:ready"      --color 0E8A16
gh label create "sdlc:status:in-progress" --color 1D76DB
gh label create "sdlc:status:done"       --color 0E8A16
gh label create "sdlc:status:rejected"   --color D73A4A
gh label create "sdlc:status:deferred"   --color D4C5F9
```

Labels for priority and type are created on first push if absent.

## Labels {#gh-labels}

Every synced issue carries a label for its type, current status, and
optionally priority and record type. The `sdlc:` prefix is reserved
by convention so these labels do not collide with existing issue
taxonomies.

| Label | Meaning |
| --- | --- |
| `sdlc:cr` | Change Request |
| `sdlc:story` | User Story |
| `sdlc:epic` | Epic |
| `sdlc:status:<state>` | `proposed`, `approved`, `ready`, `in-progress`, `done`, `rejected`, `deferred` |
| `sdlc:priority:P1..P4` | From the CR or Story priority field |
| `sdlc:type:<kind>` | `feature-request`, `production-feedback`, `spec-gap`, `retrospective`, `design-change` |

Status labels are reconciled by `push` on every invocation: the
script adds any missing labels and removes any `sdlc:*` labels that
no longer apply. Non-`sdlc:` labels are never touched, so teams can
apply their own taxonomies freely alongside.

## Push Workflow {#gh-push}

Syncs local files to GitHub. For each CR / Story / Epic file:

1. **No GitHub Issue field:** the record is unsynced. Create a new
   issue with title `[ID] Title`, body equal to the local file
   contents, and the labels derived from the record metadata. Write
   `> **GitHub Issue:** #<N>` back into the local file.
2. **GitHub Issue field present, content unchanged since last push:**
   skip.
3. **GitHub Issue field present, content changed:** recompute labels,
   add new ones, remove stale `sdlc:*` labels. Body diffing is
   deferred to v1.7 (push mirrors metadata only for now).

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/github_sync.py" push \
  --type cr \
  [--dry-run]
```

`--type` accepts `cr`, `story`, `epic`, or `all`. Default is `cr`.
`--dry-run` prints what would change without calling `gh`.

## Pull Workflow {#gh-pull}

Finds issues labelled `sdlc:<type>` that do not yet have a local
counterpart and emits TODO instructions pointing at the matching
create workflow. The script deliberately does not create local files
itself; template fields like priority, type, and affects modules
cannot be inferred reliably from a free-form issue body, so the
workflow reference files drive the create step with human review.

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/github_sync.py" pull \
  --type cr \
  [--dry-run]
```

For each unlinked issue, the output names the command to run:

```text
[TODO] pull: issue #42 labelled sdlc:cr has no local cr file.
Run the matching `/sdlc-studio cr create` workflow with
--from-issue 42 to ingest the body into the correct template,
then re-run `github_sync.py push` to write the mapping.
```

After creating the local file, a subsequent `push` picks up the new
`> **GitHub Issue:** #42` field and records the mapping.

## Cascade Workflow {#gh-cascade}

Closes the loop between PR merge and the Story Completion Cascade.
The script lists merged PRs since the last cascade run, parses each
PR body for references to local records, and prints the candidates.

Supported references in PR bodies:

- `Closes #N`, `Fixes #N`, `Resolves #N` (and plural / past-tense
  variants) for linked issues
- `sdlc:story USNNNN` for direct story IDs
- `sdlc:cr CR-NNNN` for direct CR IDs

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/github_sync.py" cascade \
  [--since 2026-04-14T00:00:00Z] \
  [--dry-run]
```

Output:

```text
cascade candidates (trigger Story Completion Cascade via reconcile):
  - US0023
  - US0025
  - CR-0007
next step: `/sdlc-studio reconcile --story <id>` (or --scope stories)
to mark these Done after PR merge.
```

The cascade itself is still user-confirmed. The script stops at
"these are the candidates" so that merged-by-mistake PRs do not
cascade silently.

## State File {#gh-state}

`sdlc-studio/.local/github-sync-state.json`. Never committed.

```json
{
  "version": 1,
  "last_pull": "2026-04-15T12:00:00Z",
  "last_push": "2026-04-15T12:05:00Z",
  "last_cascade_ref": "2026-04-15T08:30:00Z",
  "mappings": {
    "CR-0001": {
      "type": "cr",
      "issue": 42,
      "hash": "sha256:a1b2c3d4e5f60718",
      "updated_at": "2026-04-15T12:05:00Z"
    }
  }
}
```

Hashes let `push` skip records whose local content has not changed
since the last run, avoiding redundant `gh` calls on large projects.

Print state:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/github_sync.py" state
```

## Conflict Policy {#gh-conflict}

Two-way sync has inherent conflict risk. v1.6 uses
**most-recently-updated wins** with a conflict report:

1. Fetch the issue's `updatedAt` from `gh`
2. Read the local file's mtime
3. If both changed since the last sync timestamp in the state file,
   leave both untouched and report the conflict

The `--force-local` and `--force-remote` flags are reserved for v1.7.
In practice conflicts are rare: a record is usually edited either in
the skill or in GitHub Issues, not both simultaneously.

## Scope Discipline for v1.6 {#gh-scope}

**In scope:** CR and Story two-way sync, PR merge cascade (manual
trigger), conflict report, gh CLI dependency.

**Out of scope for v1.6 (v1.7+):** webhook-driven sync,
auto-cascade on push, GitHub Projects board integration, Linear /
Jira adaptors, body diffing on push, force-local / force-remote
conflict resolution, GraphQL bulk operations.

The file layout and state file schema are designed to absorb these
later without restructuring.

## See Also

- `scripts/github_sync.py` - The implementation
- `reference-cr.md#cr-sync-workflow` - The `/sdlc-studio cr sync` workflow
- `reference-story.md#story-workflow` - Story `--from-issue` branch
- `reference-outputs.md#story-completion-cascade` - Step 12 triggers github_sync.py
- `help/github-sync.md` - User-facing help
- `best-practices/script.md` - Shared script style rules
