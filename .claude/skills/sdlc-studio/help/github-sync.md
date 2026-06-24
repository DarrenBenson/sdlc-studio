<!-- Load when: user runs /sdlc-studio cr sync / story sync / project sync cascade -->
<!-- Dependencies: reference-github-sync.md, reference-cr.md, scripts/github_sync.py -->

# /sdlc-studio github-sync - Help

> **Source of truth:** `reference-github-sync.md` - Full design, label convention, conflict policy

Two-way sync between local CRs, Stories, and Epics and GitHub Issues
via the `gh` CLI. Teams that live in GitHub Issues get SDLC Studio
value without abandoning their tracker.

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Push our change requests up to GitHub Issues" | `/sdlc-studio cr sync push --type cr` |
| "Show me what would sync without changing anything" | `/sdlc-studio cr sync --dry-run` |
| "Sync everything - CRs, stories and epics - with GitHub" | `/sdlc-studio project sync` |
| "Which merged PRs are ready to mark stories done?" | `/sdlc-studio project sync cascade` |
| "Pull in any GitHub issues we don't have locally yet" | `/sdlc-studio project sync pull --type all` |
| "Show me the current sync state" | `/sdlc-studio project sync state` |

## Quick Reference

```bash
/sdlc-studio cr sync                                # Push + pull CRs
/sdlc-studio cr sync --dry-run                      # Preview, no writes
/sdlc-studio story sync                             # Push + pull Stories
/sdlc-studio project sync                           # All three (cr, story, epic)
/sdlc-studio project sync push --type all           # Push only
/sdlc-studio project sync pull --type cr            # Pull only
/sdlc-studio project sync cascade                   # Merged-PR cascade candidates
/sdlc-studio project sync cascade --since <iso>     # Limit PR window
/sdlc-studio project sync state                     # Print sync state file
```

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- A GitHub repo with write access to Issues
- Python 3.10 or later
- Labels created once via the snippet in `reference-github-sync.md#gh-setup`

## Actions

### push

Create issues for local files without a `GitHub Issue:` field; for
files that already have one, reconcile labels against the current
metadata.

**What happens:**

1. Walks `sdlc-studio/change-requests/`, `stories/`, and `epics/`
   according to `--type`
2. For each unlinked record, runs `gh issue create` with
   `title = [ID] Title`, `body = local file contents`, and derived
   labels (`sdlc:cr`, `sdlc:status:*`, `sdlc:priority:*`,
   `sdlc:type:*`)
3. Writes `> **GitHub Issue:** #<N>` into the local file
4. For linked records whose content hash has changed, runs
   `gh issue edit` to add/remove `sdlc:*` labels
5. Updates `sdlc-studio/.local/github-sync-state.json`

**Usage:**

```text
/sdlc-studio cr sync push --dry-run
/sdlc-studio cr sync push --type cr
/sdlc-studio project sync push --type all
```

### pull

Finds GitHub Issues labelled `sdlc:*` that do not yet have a local
counterpart and emits TODOs pointing at the right create workflow.
The script deliberately refuses to invent template field values;
the create workflow runs with human review.

**Usage:**

```text
/sdlc-studio cr sync pull --dry-run
/sdlc-studio project sync pull --type all
```

**Output example:**

```text
[TODO] pull: issue #42 labelled sdlc:cr has no local cr file.
Run the matching `/sdlc-studio cr create` workflow with
--from-issue 42 to ingest the body into the correct template,
then re-run `github_sync.py push` to write the mapping.
```

### cascade

Lists merged PRs since the last cascade run, parses bodies for
`Closes #N` / `sdlc:story USNNNN` / `sdlc:cr CR-NNNN` references,
and prints the candidates that should trigger the Story Completion
Cascade.

**Usage:**

```text
/sdlc-studio project sync cascade
/sdlc-studio project sync cascade --since 2026-04-14T00:00:00Z
```

**Output example:**

```text
cascade candidates (trigger Story Completion Cascade via reconcile):
  - US0023
  - CR-0007
next step: `/sdlc-studio reconcile --story <id>` (or --scope stories)
to mark these Done after PR merge.
```

### state

Prints the state file so you can inspect mappings and timestamps.

**Usage:**

```text
/sdlc-studio project sync state
```

## Arguments

### push / pull

| Flag | Effect | Default |
| --- | --- | --- |
| `--type cr\|story\|epic\|all` | Which local records to sync | cr |
| `--dry-run` | Preview, no writes, no gh calls | false |

### cascade

| Flag | Effect | Default |
| --- | --- | --- |
| `--since <iso>` | Only consider PRs merged after this timestamp | last_cascade_ref from state |
| `--dry-run` | Do not update state | false |

## Examples

**First-time setup for a new repo:**

```text
# Create the labels (one-time)
gh label create sdlc:cr --color 0366D6
gh label create sdlc:story --color 0E8A16
gh label create sdlc:epic --color 5319E7
gh label create sdlc:status:proposed --color FBCA04
# ... (see reference-github-sync.md#gh-setup for the full list)

# Push existing CRs to GitHub
/sdlc-studio cr sync push --type cr
```

**Daily flow: push any new local CRs:**

```text
/sdlc-studio cr sync --dry-run      # Preview
/sdlc-studio cr sync                # Apply
```

**After a PR lands:**

```text
/sdlc-studio project sync cascade
/sdlc-studio reconcile --story US0023
```

## Related Commands

- `/sdlc-studio cr create` - Creates a local CR; `--from-issue <N>`
  ingests an existing GitHub issue body
- `/sdlc-studio cr action --cr CR-0001` - Turns a synced CR into
  epics and stories
- `/sdlc-studio reconcile` - The Story Completion Cascade that
  cascade-identified records are passed to

## See Also

- `reference-github-sync.md` - Full design, label convention, conflict policy
- `reference-cr.md#cr-sync-workflow` - The CR-side workflow documentation
- `scripts/github_sync.py` - The implementation
- `best-practices/script.md` - Shared script conventions
