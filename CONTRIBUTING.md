# Contributing to SDLC Studio

Thank you for your interest in contributing to SDLC Studio.

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or suggest features
- Include clear steps to reproduce any bugs
- Provide context about your environment and use case

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run any relevant tests
5. Commit with a clear message
6. Push to your fork
7. Open a Pull Request

### Code Style

This project follows specific writing and code conventions:

#### Writing Style

- **British English** throughout (analyse, colour, behaviour)
- **No em dashes** - use en dash with spaces or restructure sentences
- **No corporate jargon** - avoid words like synergy, leverage, robust, journey
- **Dense, economical writing** - be concise

#### Documentation

- Follow the best practices in `.claude/skills/sdlc-studio/best-practices/`
- Use Markdown with consistent header hierarchy
- Include examples for complex concepts

#### Skill Structure

When modifying the skill:

- Keep SKILL.md under 500 lines
- Use progressive disclosure (reference-*.md files for detailed docs)
- Maintain the `{{placeholder}}` syntax in templates
- Update help files when changing commands

### Best Practices

Before submitting changes, review the relevant best practice guide:

| Changing... | Check |
| ------------- | ------- |
| Main skill file | `best-practices/claude-skill.md` |
| Documentation | `best-practices/documentation.md` |
| README | `best-practices/readme-guide.md` |
| Templates | Template conventions in claude-skill.md |

### Testing Changes

- Test the skill locally before submitting
- Verify commands work: `/sdlc-studio help`, `/sdlc-studio status`
- Check that templates render correctly
- Ensure all internal links work

## Development Workflow

SDLC Studio dogfoods itself - it is built with its own lifecycle. A few non-negotiables:

- **Setup:** Node (for the markdown lint suite) + Python 3.10+ (for the scripts and their tests).
  Run `npm install` once; the Python scripts are pure stdlib (nothing to pip install). Then
  **`bash tools/enable-hooks.sh`** to turn on the pre-commit gate.
- **Gate every commit - automated by the hook.** `bash tools/enable-hooks.sh` installs three
  hooks - `pre-commit`, `commit-msg` and `pre-push` - that run the gate and block a breaking
  commit, explaining each failure in detail (what it enforces, the offending line, the fix). It
  also sets this clone's `core.sshCommand` to an ssh carrying a keepalive: the pre-push gate runs
  for minutes before git writes a byte, and a connection idle that long is dropped before the
  push starts - so the gate passes, the push fails, and the retry pays the gate again. An
  `core.sshCommand` you have already set at any scope is left exactly as you set it, and the
  script names the scope it found it in; if yours carries no keepalive, add one, because the
  script will not write over your choice. To run it by hand, all three must pass:
  `npm run lint && npm test && python3 .claude/skills/sdlc-studio/scripts/gate.py --root .`
  Lint covers markdown, house style, links, SKILL.md, versions, budgets, and the neutrality guard;
  the gate covers conformance, reconcile drift, validation, integrity, duplicate ids, and docs. The
  hook runs every guard except markdownlint without Node; bypass in an emergency with
  `git commit --no-verify`.
- **Judge pushes on a gate host (optional).** The push gate pays the full suite, which on a
  workstation shared with agent sessions can take most of an hour. Name a host this clone reaches
  over ssh, and each push is judged there instead, against exactly the commit being pushed:
  `git config sdlc.gateHost <host>`. The host needs git on the PATH an ssh command sees there,
  and Python 3.10+ with the packages in `requirements-dev.txt` and Node, which it may put on the
  gate's PATH with `~/sdlc-gate/gate-env.sh`. `bash tools/remote-gate.sh doctor` asks the host
  whether it has all of that, naming each gap with its install route, and `tools/enable-hooks.sh`
  runs it whenever a host is configured. `sdlc.gateSsh` replaces the default ssh transport. A host that cannot be reached refuses
  the push rather than running the gate here, and `SDLC_GATE_LOCAL=1 git push` runs it on this
  machine for one push.
- **Trunk-based, small green units.** Commit to `main` in small, individually-green increments; CI
  re-runs the same gate on push, plus a coverage floor (>= 80% of the runtime scripts) and a
  `bandit` security scan. Branches are for isolation, not ceremony.
- **Paperwork in the same commit.** Every behaviour or doc change carries its
  `changelog.d/<UNIT-ID>.md` fragment and any help/reference update in the same commit. The
  release cut composes the fragments into `CHANGELOG.md`.
- **Bug to CR to RFC lifecycle.** Track work as artifacts created and closed with
  `scripts/artifact.py` (`BG` bugs, `CR` change requests, `RFC` design exploration; globally
  numbered). A change request implements a concrete improvement; a bug fixes something broken; an
  RFC explores an unsettled design before either.
- **Every bug ships a regression test.** A fix is not done until a test would catch the bug's return.
- **Forward-port skill edits.** Changes under `.claude/skills/sdlc-studio/` are mirrored to each
  install target (see `install.sh --list-targets`); verify the installed copy matches the repo.

## Architecture

Start with `AGENTS.md` (the operating doctrine) and
`.claude/skills/sdlc-studio/best-practices/architecture.md`. The skill is a lean always-loaded
router (`SKILL.md`) plus on-demand `reference-*.md` workflows, `help/` command docs, `templates/`,
and stdlib Python helpers in `scripts/` (sharing `scripts/lib/sdlc_md.py`). Repo CI checks live in
`tools/`. Volatile project state lives in `sdlc-studio/reviews/LATEST.md` - read it first.

## Agent detail moved from AGENTS.md

`AGENTS.md` is loaded on every call of every agent in this repository, so it is held to 7,000
chars by `tools/check_budgets.py` (US1129). The detail it points at lives here, each block
linked from the line in `AGENTS.md` that names its subject.

### The failure mode

Not ignorance. **Rules that were read and then not followed.** One session produced five
instances: the lessons index went unread while the plan printed its digest; review prompts
were hand-written though the shipped seat briefs exist; findings were not sorted into
regression versus pre-existing; a backlog census was hand-scripted rather than taken from
the tooling; and the full-suite-before-commit rule was broken one commit after being
shipped, leaving `main` red for six commits.

So: **when a rule matters, gate it in the command people actually run** - LL0027 in the
[lessons registry](.claude/skills/sdlc-studio/lessons/_index.md). Adding a line to `AGENTS.md`
is the weakest available fix, and a rule stated there with no gate behind it should be read as
a known-weak one.

### Hooks and the push

`bash tools/enable-hooks.sh` installs the three tracked hooks (pre-commit, commit-msg,
pre-push), names each, and sets this clone's `core.sshCommand` to an ssh carrying a keepalive -
the pre-push gate runs for minutes before git writes a byte, and a connection idle that long is
dropped before the push starts, so the gate passes, the push fails and the retry pays the gate
again. It also names each gate prerequisite this machine lacks, what breaks without it and an
install route for this interpreter (`python3 tools/gate_prereqs.py check` alone re-checks). A
`core.sshCommand` already in force at ANY scope - local, global or system - is left as you set
it, and the script names the scope it found it in; if yours carries no keepalive, add one,
because the script will not write over it.

A push runs the full suite once plus the core gate lanes, and a tag adds the slow release
lanes. The gate prints each lane it runs and its cost.

**Pushes go straight to main and a red main is read before the next push (D0181).** The
pre-push hook asks the forge for the latest push-triggered Lint run on main before it runs the
gate; on any conclusion but success it refuses until that run's id is acknowledged once per
clone with `SDLC_PUSH_ACK_RED=<run id> git push`. A red answer is read once more before it
refuses, and the second answer is judged: the forge's ordering is eventually consistent, and a
stale first row once named a two-month-old red (BG0709). An unreadable or empty answer is named
and never read as green, and it does not block an offline push. The required status check a
direct push can never satisfy was removed from branch protection under the same ruling on
2026-09-06, and the protection read-back shows none.

The refusals the table in `AGENTS.md` abbreviates, in full: `transition -> Fixed` refuses a bug
nothing speaks for (no ticked criterion, no `Verify:` line); `sprint close` records uncovered
units, unanswered items and failing lanes as known issues on the report rather than refusing;
`critic.py brief` refuses under `review.author_self_check: block`; `sprint sign` refuses a page
that no longer re-derives to what was filed and a tree changed since the close.

### Exercising claims

A review should CONFIRM your work, not discover that it does not run. A library test cannot see
a missing lane, because the wiring is the part it does not exercise: `brief_fingerprint(brief(
...))` passed in-process for a whole sprint while `critic.py brief` printed nothing and the
paperwork said it did. Needing a second review round to learn that is not thoroughness, it is
verification handed to somebody else.

### Tools before hand-rolling

The [toolchain runbook](.claude/skills/sdlc-studio/reference-sprint-toolchain.md) is ordered by
SPRINT STEP - plan, groom, batch, deliver, review, in-flight, close - and each row names the one
command that performs the step beside the hand-rolled shape it replaces.

RUN-01KYZKY5 paid for that rule: the close was hand-authored first, and running the shipped
commands afterwards caught four defects the hand version had missed - example scaffold rows left
in a retro, a Batch field that parsed to zero units, a header claiming a delivered count the
batch contradicted, and a lessons digest that no longer matched its log. The runbook already
named the command that would have caught them.

### Project overview and layout

SDLC Studio is an agent skill (the [Agent Skills](https://agentskills.io) open format) for
managing the full software development lifecycle - PRD, epics, stories, planning, tests. It
enables **Goal-Driven Development**: set a goal and acceptance criteria, and the agent drives
the proven lifecycle to it (TDD, BDD, Eval-Driven, Goal-Driven). `sprint` runs it and closes
every run with a reconcile and review. The skill source installs to each tool's skill directory
(`install.sh --list-targets`). Durable guidance lives in `AGENTS.md`; volatile state lives in
`sdlc-studio/reviews/LATEST.md`, so the two do not drift.

| Path | Purpose |
| --- | --- |
| `.claude/skills/sdlc-studio/SKILL.md` | Always-loaded router (~300 lines, CI-budgeted under 500) |
| `.claude/skills/sdlc-studio/reference-philosophy.md` | Create vs Generate modes - read first |
| `.claude/skills/sdlc-studio/reference-doctrine.md` | Project-agnostic operating doctrine |
| `.claude/skills/sdlc-studio/reference-*.md` | Domain workflows (50+ files); `help/references.md` indexes them |
| `.claude/skills/sdlc-studio/help/` | Type-specific help (~45 files) |
| `.claude/skills/sdlc-studio/scripts/` | 40+ helpers sharing `lib/sdlc_md.py` |
| `.claude/skills/sdlc-studio/templates/` | Documents and code, incl. `agent-instructions.md` (the starter `AGENTS.md`'s shape follows) |
| `.claude/skills/sdlc-studio/best-practices/` | Quality guidelines (19 files) |

`persona_resolve.py resolve --seat <s> --path-only` names the seat card in force.

### Forward-porting

Never run `install.sh` from the dev repo - its sweep clobbers the git-tracked tree. Mirror with
the guarded wrapper instead:

```bash
bash tools/forward-port.sh          # itemised diff, dry-run
bash tools/forward-port.sh --yes    # apply (.local and __pycache__ untouched)
bash tools/forward-port.sh --check  # drift gate; non-zero when the copy has drifted
```

The installed copy is what every other project on this machine loads, so the window between a
fix landing here and the mirror running is a window in which a fix believed shipped is in force
nowhere. Two states are reported rather than failed: no installed copy, and a copy holding a
`.local/forward-port.pin` marker.

### Test budgets

A commit runs only the test modules its staged change reaches, in parallel, and reports its time
against a 90-second budget; a docs or artefact commit runs only the modules whose
`test-census-subject` names a file it stages. A change to a hub script still selects large
modules, so give a commit a 10-minute timeout. The full suite runs at push.

The gate spans two hooks, cheapest first. `pre-commit` runs the cheap guards and decides
whether the suites are needed; `commit-msg` checks the message rules and only then runs them.
Git creates the commit message after `pre-commit`, so this is the only order in which a message
defect is refused before the suites run rather than after them.

A passing commit prints one summary line from each hook, its last, and holds back the per-lane
list, the SKIP and note lines and the 90-second budget report. Above the summary it still
prints the stamps-staged lane's re-read list and the settle step's report of the drift it
restaged or left unstaged, which an author reads nowhere else. A refusal prints the whole
per-lane list with the failing lane's rule, detail and fix. Set `SDLC_GATE_VERBOSE=1` to see the
lanes and the budget report on a pass.

One lane is deliberately outside the gate: `npm run lint:corpus` lints every tracked markdown
file under the strict root rules, attributing findings against the latest tag. It runs from a
scheduled job and by hand before a release, because a guard whose cost is paid on every commit
gets switched off.

Manual verification: `./install.sh --local`, then `/sdlc-studio help`, `status`,
`repo map build`, and `reconcile --verify --dry-run` against a fixture story.

### Soft dependencies in full

| Feature | Requires |
| --- | --- |
| `cr sync`, `story sync`, `project sync` | `gh` CLI, authenticated |
| `reconcile --verify` | whichever of `pytest`, `jest`, `vitest`, `go`, `curl`, `jq`, `rg` your Verify lines invoke |
| `repo map build` | Python 3.10+ (pure stdlib) |
| `verify_ac run --coverage` and the `review.line_coverage` gate | `coverage` 7.10 or later on the interpreter that runs the selectors (`SDLC_COVERAGE_PYTHON`, else the current one); absent, the run refuses under `block` and reports under `report` |

### Before you write

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

## Questions?

If you have questions about contributing, open an issue for discussion.
