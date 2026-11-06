# AGENTS.md

Guidance for coding agents here; Claude Code reads it via `@AGENTS.md` in [CLAUDE.md](CLAUDE.md).
It is loaded on every call, so it holds nothing a command prints and is held to 7,000 chars;
the detail is in [CONTRIBUTING.md](CONTRIBUTING.md#agent-detail-moved-from-agentsmd).

## Start here, every session

Do these four before acting, including after a context reset or compaction.

1. `sdlc-studio/reviews/LATEST.md` - what the last run landed and left owed.
2. `/sdlc-studio status` - pipeline state and the next step.
3. `.claude/skills/sdlc-studio/lessons/_index.md` - read the lessons before any design decision.
4. `git fetch` - a stale clone mints ids the remote already used.

The [failure mode](CONTRIBUTING.md#the-failure-mode) here is rules read and not followed, so a
rule that matters is gated in the command people run (LL0027); one stated here alone is weak.

## What will refuse you

| Gate | Refuses |
| --- | --- |
| pre-commit + commit-msg hooks | any lane `.githooks/pre-commit --list` or `.githooks/commit-msg --list` prints |
| pre-push hook | a red boundary gate (`gate.py --boundary push`, or `release` for a tag); `python3 tools/gate_timing.py estimate --suite boundary-push --warn-seconds 0` prints its cost |
| `sprint plan` | a batch whose units lack `Affects:` or `Points:`, or exceed the split threshold |
| `transition -> Done` | a story whose executable ACs have not passed |
| `transition -> Fixed` | a bug nothing speaks for, or whose recorded `verify_ac` run is red |
| `sprint close` | an uncommitted change to a file a batch unit declares |
| `critic.py brief` | a unit whose author recorded no self-check of its current diff |
| `sprint sign` | a report not the run's, a changed page or tree, or a principal who authored or reviewed a unit |

**Enable the hooks once per clone: `bash tools/enable-hooks.sh`.** It installs the
three tracked hooks and an ssh keepalive, and names any missing prerequisite
([hooks and the push](CONTRIBUTING.md#hooks-and-the-push)). Without them the gates are off. The only bypass is `git commit --no-verify` or
`git push --no-verify`. Pushes go straight to main; a red main is read before the next push
(D0181). Each hook lists its lanes (`--list` above); `.githooks/pre-push` runs the full suite once.

## Non-negotiable rules

**No ad-hoc coding.** Work becomes a story or bug with acceptance criteria before it becomes a
diff; a CR or RFC is not work until `refine` decomposes it into sized units.

**Review is independent of the author.** Each unit gets one reviewer, a fresh context that did
not write the code, briefed with `critic.py brief`, recording with `critic.py record`. The
operator signs the run once, after the close, with `sprint sign`.

**Brief a reviewer with the shipped tool, never by hand.** `critic.py brief --unit <id> --seat
engineering|product|qa` carries the seat charter, the unit's `Affects` as scope, the criteria as
law and the claim-inventory pass; a hand-written prompt carries none of them.

**A review judges the unit's own diff.** Only a regression or a new defect blocks; what is
already true of the tree, or in an open Bug or CR, is reported with its id. Decide by execution
(`git log -S`), not impression.

**Always look for a tool before doing anything by hand.** Read your step's row in the
[toolchain runbook](.claude/skills/sdlc-studio/reference-sprint-toolchain.md) before starting
it; a step with no command is a finding to file ([tools before hand-rolling](CONTRIBUTING.md#tools-before-hand-rolling)).

**Use the deterministic tooling; never hand-roll what it wires.** `artifact.py new`/`batch`,
`next_id.py`, `file_finding.py`, `transition.py`; `_index.md` is derived and `reconcile` syncs
it. Read `reference-scripts.md`, the catalogue, before hand-doing anything mechanical.

**Exercise every claim through the shipped entry point before asking for review.** Put each
claim in the fragment and criteria through the CLI in a throwaway fixture, refusals with a
positive control beside each ([exercising claims](CONTRIBUTING.md#exercising-claims)). This repo
sets `review.author_self_check: block`: record the pass with `critic.py self-check record`.

**Ship the paperwork in the same commit as the code.** Every behaviour or doc change carries
its `changelog.d/<UNIT-ID>.md` fragment (`lessons/LL0004`).

**The push gate is the full-suite check.** A commit runs only the test modules its change
selects; the pre-push hook runs the whole suite on the commit each pushed ref points at, on the
gate host when `sdlc.gateHost` is set (D0382), so a commit beneath a ref's tip is not judged by
it. `tools/run-suite.sh all` runs it on demand, there too; `run-suite.sh --check` reads it.

## Where things live

| Path | Purpose |
| --- | --- |
| `.claude/skills/sdlc-studio/` | The skill source; this repo dogfoods it ([project overview](CONTRIBUTING.md#project-overview-and-layout)) |
| `.claude/skills/sdlc-studio/reference-scripts.md` | The script catalogue |
| `.claude/skills/sdlc-studio/templates/personas/amigos/` | The shipped amigo seats; this repo's cards in `sdlc-studio/personas/seats/` override them |
| `tools/` | Repo-only CI guards, not shipped |

## Forward-porting

Never run `install.sh` here; mirror with `bash tools/forward-port.sh` (dry-run, `--yes` to
apply) and gate drift with `bash tools/forward-port.sh --check`; a copy holding a
`.local/forward-port.pin` marker is reported, not failed ([forward-porting](CONTRIBUTING.md#forward-porting)).

## Testing

`npm run lint` and `npm test`; without npm every check but markdownlint is a plain command.
Give a commit a 10-minute timeout ([test budgets](CONTRIBUTING.md#test-budgets)).

## Soft dependencies

| Feature | Requires |
| --- | --- |
| `cr sync`, `story sync`, `project sync` | `gh` CLI, authenticated |
| `reconcile --verify` | the tools your Verify lines invoke |
| `repo map build` | Python 3.10+ |
| `verify_ac run --coverage`, `review.line_coverage` | `coverage` 7.10 or later ([soft dependencies](CONTRIBUTING.md#soft-dependencies-in-full)) |

## Style

`tools/lint-style.sh` enforces British English, no em dashes, no corporate jargon, no provenance
tags in consuming-facing pages, and `{{placeholder}}` in templates. Before writing code, docs or
a test, read [before you write](CONTRIBUTING.md#before-you-write).
