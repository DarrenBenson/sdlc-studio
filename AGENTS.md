# AGENTS.md

Guidance for coding agents working on this repository. Claude Code reads this via the
`@AGENTS.md` import in [CLAUDE.md](CLAUDE.md); Codex, Copilot, Cursor, Gemini and others
read it directly.

**This file is always loaded. Keep it short enough to be read, and put nothing here that a
command already prints.** The pre-commit hook names every guard it runs, the rule it
enforces, the offending line and the fix, so this file does not restate them.

## Start here, every session

Do these four before acting, including after a context reset or compaction. They take
under a minute and each one has cost a real sprint when skipped.

1. `sdlc-studio/reviews/LATEST.md` - what the last run landed and what it left owed.
2. `/sdlc-studio status` - pipeline state and the next step.
3. `.claude/skills/sdlc-studio/lessons/_index.md` - the cross-project lessons. Read them
   before any design decision, not after.
4. `git fetch` - a stale clone mints ids the remote already used and plans over artefacts
   somebody else changed.

## The failure mode this repo actually has

Not ignorance. **Rules that were read and then not followed.** One session produced five
instances: the lessons index went unread while the plan printed its digest; review prompts
were hand-written though the shipped seat briefs exist; findings were not sorted into
regression versus pre-existing; a backlog census was hand-scripted rather than taken from
the tooling; and the full-suite-before-commit rule was broken one commit after being
shipped, leaving `main` red for six commits.

So: **when a rule matters, gate it in the command people actually run** - LL0027 in the
[lessons registry](.claude/skills/sdlc-studio/lessons/_index.md). Adding a line here is the
weakest available fix, and a rule stated here with no gate behind it should be read as a
known-weak one.

## What will refuse you

These block. Everything else in this file is guidance.

| Gate | Refuses |
| --- | --- |
| pre-commit + commit-msg hooks | any guard failure; a multi-id subject with no `Refs:` trailer; a collapsed test suite |
| `sprint plan` | a batch whose units lack `Affects:` or `Points:`, or exceed the split threshold |
| `transition -> Done` | a story whose executable ACs have not passed, or that is past `review.two_role_after` without both review halves |
| `transition -> Fixed` | a bug with no parseable `Verification depth` |
| `sprint close` | units no independent pass covers; an unanswered checklist item |
| `critic record` | a verdict carrying no brief provenance (`--brief`), unless stood down by a recorded config decision |
| `critic signoff` | a principal the authoring session controls |

**Enable the hooks once per clone: `bash tools/enable-hooks.sh`.** Without them you are
running with the gates off. Emergency bypass is `git commit --no-verify` and nothing else.

The pre-commit lanes, recorded here because a review once found the repo's own account of its
gates incomplete, and a guard nobody has written down is one nobody notices losing. The hook
prints each lane's rule and fix on failure, so this is the roster, not the manual:
`lint-style.sh`, `check_links.py`, `check_budgets.py`, `check_versions.py`,
`check_spec_claims.py`, `check_script_tests.py`, `check_neutrality.py`,
`check_action_pins.sh`, `validate_skill.py`, `verify_ac.py`, `readiness.py`, plus `gate.py`'s
own block (conformance, reconcile, validate, integrity, duplicate-id, docs) and markdownlint.
One lane is ADVISORY and cannot fail a commit: `claim-drift`, which reports where a diff's
code and the diff's own prose disagree. It ships advisory while its yield is measured,
because a new blocking check on a gate already over its ceiling earns its place on a
number rather than on assertion.
`tools/tests/test_check_spec_claims.py` pins that this roster names its checker; extend the
pinning when you add a lane, or the list silently exempts whatever it forgot - LL0013 in the
[lessons registry](.claude/skills/sdlc-studio/lessons/_index.md).

## Non-negotiable rules

**No ad-hoc coding.** Work becomes a story or a bug with acceptance criteria before it
becomes a diff. A CR or RFC is not work until `refine` decomposes it into sized units.
This repo is held to it like any consuming project.

**Review is independent of the author.** Two roles, never merged: an adversarial reviewer
(a fresh context that did not write the code) files findings as evidence, and a reviewer of
record - the operator, or a named delegate in a separate trust boundary - approves. A
delegate the author controls does not satisfy this.

**Brief a reviewer with the shipped tool, never by hand.** `critic.py brief --unit <id>
--seat engineering|product|qa` carries the seat charter, the bounded diff scope (the unit's
declared `Affects`), the canonical acceptance criteria as law, and the claim-inventory pass.
A hand-written prompt carries none of them and silently substitutes an unbounded surface for
a unit review. Resolve the panel with `persona_resolve.py panel` rather than picking seats
by judgement.

**A review judges the unit's own diff.** Scope is that unit's `Affects` against the run's
base ref. Only a regression or a newly introduced defect blocks; anything already true of
the tree, or already recorded in an open Bug or CR, is reported with its id and does not
hold the gate. Decide which by execution (`git log -S`), not by impression.

**Always look for a tool before doing anything by hand.** The
[toolchain runbook](.claude/skills/sdlc-studio/reference-sprint-toolchain.md) is ordered by
SPRINT STEP - plan, groom, batch, deliver, review, in-flight, close - and each row names the one
command that performs the step beside the hand-rolled shape it replaces. Read the row for the
step you are on BEFORE you start it, not after. If a step there has no command, that is a
finding to file, not permission to hand-roll it.

RUN-01KYZKY5 paid for this line: the close was hand-authored first, and running the shipped
commands afterwards caught four defects the hand version had missed - example scaffold rows left
in a retro, a Batch field that parsed to zero units, a header claiming a delivered count the
batch contradicted, and a lessons digest that no longer matched its log. The runbook already
named the command that would have caught them.

**Use the deterministic tooling; never hand-roll what it wires.** Create artefacts with
`artifact.py new` / `batch`, allocate ids with `next_id.py`, file findings with
`file_finding.py`, change status with `transition.py`. Never hand-author `_index.md` - it is
derived, and `reconcile` syncs it. **Read `reference-scripts.md` before hand-doing anything
mechanical**; it is the catalogue, and the answer is usually already there.

**Exercise every claim through the shipped entry point before asking for review.** A review
should CONFIRM your work, not discover that it does not run. Take each factual claim in the
changelog fragment and the criteria and put it through the CLI in a throwaway fixture -
refusals included, with the positive control beside each one. A library test cannot see a
missing lane, because the wiring is the part it does not exercise: `brief_fingerprint(brief(
...))` passed in-process for a whole sprint while `critic.py brief` printed nothing and the
paperwork said it did. Needing a second review round to learn that is not thoroughness, it is
verification handed to somebody else. Ungated until CR0520 ships `verify_ac lane-check`, so
read it as a known-weak rule and do it anyway.

**Ship the paperwork in the same commit as the code.** Every behaviour or doc change carries
its `changelog.d/<UNIT-ID>.md` fragment (`lessons/LL0004`).

**Run the full suite before a commit that touches shared surface.** The gate runs a selected
subset, so a green commit is not a green tree. This rule has been broken by the agent that
shipped it.

## Project overview

SDLC Studio is an agent skill (the [Agent Skills](https://agentskills.io) open format) for
managing the full software development lifecycle - PRD, epics, stories, planning, tests.
It enables **Goal-Driven Development**: set a goal and acceptance criteria, and the agent
drives the proven lifecycle to it (TDD, BDD, Eval-Driven, Goal-Driven). `sprint` runs it and
closes every run with a reconcile and review.

**The skill source lives at `.claude/skills/sdlc-studio/`** and installs to each tool's
skill directory (`install.sh --list-targets`). This repo dogfoods the skill against its own
source. Durable guidance lives here; volatile state lives in `sdlc-studio/reviews/LATEST.md`,
so the two do not drift.

## Where things live

| Path | Purpose |
| --- | --- |
| `.claude/skills/sdlc-studio/SKILL.md` | Always-loaded router (~200 lines, CI-budgeted under 500) |
| `.claude/skills/sdlc-studio/reference-philosophy.md` | Create vs Generate modes - read first |
| `.claude/skills/sdlc-studio/reference-doctrine.md` | Project-agnostic operating doctrine |
| `.claude/skills/sdlc-studio/reference-scripts.md` | **The script catalogue. Read before hand-doing a mechanical task** |
| `.claude/skills/sdlc-studio/reference-*.md` | Domain workflows (50+ files); `help/references.md` indexes them |
| `.claude/skills/sdlc-studio/help/` | Type-specific help (~40 files) |
| `.claude/skills/sdlc-studio/lessons/` | Cross-project lessons registry |
| `.claude/skills/sdlc-studio/personas/seats/` | The three amigo seats, in work and review renders |
| `.claude/skills/sdlc-studio/scripts/` | 40+ helpers sharing `lib/sdlc_md.py` |
| `.claude/skills/sdlc-studio/templates/` | Documents and code, incl. `agent-instructions.md` (the starter this file's shape follows) |
| `.claude/skills/sdlc-studio/best-practices/` | Quality guidelines (19 files) |
| `tools/` | Repo-only CI guards, not shipped |

## Forward-porting to the installed copy

Never run `install.sh` from the dev repo - its sweep clobbers the git-tracked tree. Mirror
with the guarded wrapper instead:

```bash
bash tools/forward-port.sh          # itemised diff, dry-run
bash tools/forward-port.sh --yes    # apply (.local and __pycache__ untouched)
bash tools/forward-port.sh --check  # drift gate; non-zero when the copy has drifted
```

The installed copy is what every other project on this machine loads, so the window between
a fix landing here and the mirror running is a window in which a fix believed shipped is in
force nowhere. Two states are reported rather than failed: no installed copy, and a copy
holding a `.local/forward-port.pin` marker.

## Testing

`npm run lint` (markdown plus all guards) and `npm test` (the script suite). **Without npm,
every check except markdownlint is a plain Python or bash command** - do not skip the gate
because npm is missing.

**Budget the time.** The unit suites take ~2.5 minutes, longer than most tooling's 2-minute
default, so give a commit at least a 10-minute timeout. The hook prints its expected duration
first and skips the suites for a commit touching no `scripts/`, `templates/` or `tools/` file.

**The gate spans two hooks, cheapest first.** `pre-commit` runs the cheap guards and decides
whether the suites are needed; `commit-msg` checks the message rules and only then runs them.
Git creates the commit message after `pre-commit`, so this is the only order in which a
message defect is refused before a 2.5-minute run rather than after it.

One lane is deliberately outside the gate: `npm run lint:corpus` lints every tracked markdown
file under the strict root rules, attributing findings against the latest tag. It runs from a
scheduled job and by hand before a release, because a guard whose cost is paid on every commit
gets switched off.

Manual verification: `./install.sh --local`, then `/sdlc-studio help`, `status`,
`repo map build`, and `reconcile --verify --dry-run` against a fixture story.

## Soft dependencies

| Feature | Requires |
| --- | --- |
| `cr sync`, `story sync`, `project sync` | `gh` CLI, authenticated |
| `reconcile --verify` | whichever of `pytest`, `jest`, `vitest`, `go`, `curl`, `jq`, `rg` your Verify lines invoke |
| `repo map build` | Python 3.10+ (pure stdlib) |

## Style

Enforced by `tools/lint-style.sh`, with no code-span or "only quoting the rule" exception:
British English; no em dashes (use a spaced hyphen, or restructure); no corporate jargon
(allowlist in `tools/style-allowlist.txt`); no internal provenance tags in consuming-facing
`reference-*.md`, `help/` or `scripts/`; dense, economical writing; `{{placeholder}}` syntax
in templates.

## Before you write

| Creating | Read |
| --- | --- |
| Python script | `best-practices/python.md`, then `script.md` |
| Bash script | `best-practices/script.md` |
| Documentation | `best-practices/documentation.md` |
| Agent skill | `best-practices/claude-skill.md` |
| A test | `best-practices/testing.md#name-the-mutant-first` - state the production change the test must fail on, before writing it |

When modifying the skill: keep SKILL.md a router (philosophy gates, the loading guide,
pointers); add a `help/` file for a new command; update the matching `reference-*.md` for a
workflow change.

## Related

- [README.md](README.md) - installation and quick start
- [CONTRIBUTING.md](CONTRIBUTING.md) - contribution guidelines
