# SDLC Studio v6.3.0

**SDLC Studio 6.3.0 is the current release: a run's cost is now measured on whichever harness ran
it and stated in US dollars, and a lane can run headless in any of five harnesses' CLIs.**

Every entry is in [the CHANGELOG's 6.3 section](../CHANGELOG.md#unreleased). From 6.2, the
"Upgrading from 6.2" section below is the whole path, and
[the existing-users page](existing-users.md#from-62-to-63) walks it too; from an earlier
release, start with [that page](existing-users.md).

## What changed for you

- **A run's cost is measured on whichever harness ran it.** The token meter reads the store of
  the harness that is running, and that one alone: Claude Code's transcripts, the Codex CLI's
  state store, the Copilot CLI's session events, OpenCode's database, or Cursor's CLI store,
  or its cloud usage API when `CURSOR_API_KEY` and `SDLC_STUDIO_CURSOR_AGENT_ID` are both set.
  `SDLC_STUDIO_HARNESS` names the harness. Left unset, the meter takes the one harness the
  environment signals, else the one whose store is present, else Claude Code. A reading that
  cannot be taken reads not measured and says why, never zero. Each reading names its harness,
  carries cache reads apart from its tokens, and says whether the spend of the agents it
  delegated to is inside it. A Codex reading keeps each model's tokens apart, so a model new to
  the run no longer books the workspace's earlier history as dollars, and a lane run under Codex
  is counted once, not twice. Delivered by US0986, US0987, US0988, US0989 and US1127.
- **The report states the run's cost in US dollars and shows where it went.** A dated price
  table, `templates/model-prices.json`, prices each reading model by model from each provider's
  list prices: Anthropic's Claude models, the OpenAI models the Codex meter reads, and
  OpenCode's free model. The sprint report gains a Dollar cost row, a Dollars per point row and
  each unit's dollars, and a Premium requests row that prices Copilot premium requests apart,
  never in the Dollar cost. A model the table lacks is named as not priced, never counted as
  free. RPT0027, the report of the last run before this release, states $118.38 over 41
  delivered points, $2.89 a point. `sprint.py cost --anatomy` breaks the open run's spend down by
  role (orchestrator, builder, reviewer, repair and other) and names the ten tool outputs that
  cost most, and the report's cost appendix carries its table. Delivered by US1122, US1123,
  US1124 and US1135.
- **A lane runs headless in any harness's CLI, lands in one command and spawns lean agents.**
  `sprint.py lane run --harness <h> --units <id>` runs one unit's brief in a fresh headless
  session of Claude Code, Cursor, Codex, Copilot or OpenCode, in the lane's own worktree, and a
  later `lane return` prices the unit from that session's own usage record. The builder stages its Affects, writes its
  self-check and commit message under `sdlc-studio/.local/lane/`, and stops; `sprint.py lane
  land` then commits the lane through the hooks, records its self-check and writes its review
  brief; a repair round that hands in no self-check is reported as not recorded, never given an
  earlier round's. `sprint.py lane accept` refuses to record a verdict for a unit whose latest
  landing wrote no brief, and quotes why it wrote none. Lanes and reviews spawn the lean `sdlc-builder` and `sdlc-reviewer` agents that `init`
  drafts into `.claude/agents/`, so a builder or reviewer starts without the skill listing and
  tool catalogue it never uses. Delivered by US1126, US1120 and US1132.
- **The gates and commit checks are faster and truer.** The release verify lane runs its pytest
  batch on every core where pytest-xdist is installed, under its own ceiling,
  `SDLC_VERIFY_BATCH_TIMEOUT`. It then runs the criteria the batch leaves on a pool of
  `SDLC_VERIFY_WORKERS` workers, and its cost line says how many criteria the batch resolved.
  The batch splits its phases by each test's own `serial_only` mark, so a criterion that is red
  on its own run no longer reads green in the batch. The commit-msg check, given
  `--write-trailers`, writes the `Refs:` and `Mentions:` trailers a commit naming two or more
  ids owes, read from the staged files' `Affects`, where it used to refuse the commit for them.
  Delivered by US1112, US1113 and US1133.

## Changed defaults and new refusals

No 6.3 fragment is filed under Breaking or Removed. These are the changes a 6.2 habit meets as a
new refusal or a changed default, each with what to do instead:

- **`release_strategy` now ships as `trunk`.** Under it an agent commits each unit to `main`
  when its gate passes and pushes `main`, with no branch and no pull request, where 6.2's
  `pr-required` default had it open a pull request per change. A 6.2 project whose
  `.config.yaml` does not set the key reads `trunk` once upgraded.
  Instead: set `release_strategy: pr-required` in `sdlc-studio/.config.yaml` to keep a branch
  and a pull request per change.
- **`sprint.py lane land`, not the builder, commits a lane.** `sprint.py lane brief` no longer
  prints a commit step or a `critic.py self-check record` command. It tells the builder to stage
  exactly its Affects, write its claims, mutants and commit message under
  `sdlc-studio/.local/lane/`, and stop.
  Instead: run `sprint.py lane land --worktree <path> --units <id>` to commit the lane through
  the hooks and record its self-check, then `sprint.py lane accept` once the reviewer answers.
- **A sized unit's brief sets a tool-call budget.** The brief states a budget of 25 calls plus
  13 per point; at the budget the builder writes `HANDOFF.md` with what is done, stages what it
  has and returns.
  Instead: resume a builder only while its context is below 100k tokens, as the agent prompt
  template advises; otherwise start a fresh builder from its `HANDOFF.md`.
- **`init` drafts the `sdlc-builder` and `sdlc-reviewer` agent definitions.** It writes them to
  `.claude/agents/` beside `AGENTS.md` and `CLAUDE.md`, each only if absent, and lanes and
  reviews spawn them by name.
  Instead: in an existing project, run `init.py run` again to add them. It leaves a definition
  you have edited alone; to take the shipped one back, delete it and run `init.py run` again,
  which changes no other file. Do not pass `--force` for this: it rewrites every file `init`
  writes, `.config.yaml`, `AGENTS.md`, `CLAUDE.md` and `decisions.md` among them. A harness with
  no agent config falls back to `general-purpose`.
- **`gate.py --run-tests` refuses a stale selector.** A path that does not exist, or a node id
  whose test does not exist, is refused by name and exits 2 before any test runs, where under
  pytest-xdist it could let a failing module beside it read green.
  Instead: correct or remove the selector; a directory or a whole module still runs.
- **The token meter no longer guesses between harnesses.** Two harness signals, or two harness
  stores and no signal, read not measured and name every candidate, where 6.2 read Claude
  Code's transcript. An `SDLC_STUDIO_HARNESS` value it does not know reads nothing, and an
  `opencode.db` at the default path that cannot be read is a candidate, not an absence.
  Instead: set `SDLC_STUDIO_HARNESS` to `claude`, `codex`, `copilot`, `opencode` or `cursor`.
- **Security fix: the Cursor meter sends its key over https alone.** An
  `SDLC_STUDIO_CURSOR_API` base that is not https is refused before any request, unless it is
  http on a loopback IP address, so a mistyped `http://` override no longer sends
  `CURSOR_API_KEY` in cleartext. A host name, `localhost` among them, is refused rather than
  resolved, and the reason names the variable, never its value.
  Instead: use an https base, or `http://127.0.0.1:<port>` for a local stub.
- **The release verify lane runs criteria side by side.** At most `SDLC_VERIFY_WORKERS`
  stories run at once, so a criterion bound by wall-clock time, or one close to the
  per-verifier ceiling, can read red beside other work where one at a time it read green.
  Instead: set `SDLC_VERIFY_WORKERS=1` to run one story at a time, and mark a wall-clock test
  `serial_only` so it runs after the pool.
- **A commit-msg hook given `--write-trailers` refuses a `Refs:` line no staged file supports.**
  The hook `help/gate.md` gives a project runs `--strict` alone, so it meets no new refusal. Add
  `--write-trailers` and, on a subject naming two or more ids, the check writes the `Refs:` and
  `Mentions:` lines the staged files' `Affects` attribute, and under `--strict` refuses a `Refs:`
  line naming a unit that owns none of the staged files.
  Instead: write `Mentions: <id>` for an id the commit only mentions, or leave the trailers out
  and let the flag write them.
- **A verifier that outruns its timeout loses its whole process group.** Its children are
  killed with it, and importing `verify_ac` on the main thread installs SIGTERM, SIGINT and
  SIGHUP handlers that kill every running verifier's group. The fix's review found a regression,
  listed under Known issues: a signal sent to the caller's process group no longer reaches a
  running verifier.
  Instead: do not rely on a verifier's background children outliving it.
- **A light APPROVE stops counting once the unit's own Affects grow.** Conformance owes the
  full-tier review when the unit's Affects gained a file since its light APPROVE, or when the
  tier was forced with `--tier light`, and `critic.py record` warns on stderr when a unit's latest
  APPROVE is shallower than the tier its risk band now derives.
  Instead: re-brief and review the unit at the full tier the warning names.
- **The sprint report has new cost rows.** It gains a Priced column, Dollar cost, Dollars per
  point and Premium requests rows, and the anatomy table in its cost appendix; a page filed
  before re-derives unchanged.
  Instead: add or replace a model's prices under `pricing.models` in `.config.yaml` when the
  report names it as not priced.
- **The shipped `AGENTS.md` starter is shorter.** Its working habits moved to
  `reference-doctrine.md#working-habits`, and an `AGENTS.md` that exists is not rewritten.
  Instead: read the working habits there, and copy any you want into your own `AGENTS.md`.
- **The shipped lesson runs the full suite before each push, not each commit.**
  Instead: let a commit run the tests its change reaches, and run the project's own full test
  command before each push, from a pre-push hook or by hand.

## Upgrading from 6.2

Reinstall, then carry each project across:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py"            # dry run: lists what it would change, writes nothing
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py" --apply    # restamps the project version, and nothing else
python3 "$CLAUDE_SKILL_DIR/scripts/init.py" run           # adds the two agent definitions, changes no file you have
```

**Reinstall.** A plain `install.sh` or `install.ps1` fetches the latest published release; pass
`main` as the version for the moving branch.

**`migrate`** is the dry run: it writes nothing. For a 6.2 project it reports one deterministic
upgrade, the version stamp (`sdlc-studio/.version stale (skill 6.2.0 -> 6.3.0)`), beside
anything it leaves to you, such as a seat role with no card.

**`migrate --apply`** writes that stamp to `sdlc-studio/.version` and changes nothing else: no
6.3 fragment retires a config key or a command, so there is nothing for it to remove. It does
not write `release_strategy` to your `.config.yaml`, so a project that never set it now reads
`trunk`; set `release_strategy: pr-required` to keep a pull request per change.

**`init.py run`**, run again, adds the files a 6.3 project has and yours lacks, among them
`.claude/agents/sdlc-builder.md` and `.claude/agents/sdlc-reviewer.md`, and leaves every file
you have as it is.

## Known issues

Every open finding this release ships is listed by id on [the disclosure page](known-issues.md),
which `tools/known_issues.py write` generates from the bug corpus at the cut, together with the
count below, so the two cannot disagree.

BG1190 stays open: a verifier that times out now has its children killed with it, and the fix's
review found that a signal sent to the caller's process group no longer reaches a running
verifier.

**v6.3.0 discloses 245 open defects: 61 Medium, 184 Low.**

## For contributors to this repository

This repository's own tooling, which does not ship, changed too: `tools/remote-gate.sh` runs the
pre-tag release gate on the gate host and checks its prerequisites first, the benchmark runner
runs other harnesses' CLIs, authenticates Claude Code and Codex CLI from the operator's login
file and refuses a `--dest` inside a git work tree, the suite's root `conftest.py` points `HOME`
and the XDG directories at a private directory so no test opens the operator's harness stores,
the commit-msg hook prints the trailers a refused commit needs ready
to paste, and the PRD, TRD and TSD were corrected against the code. The CHANGELOG lists each
change.

## Sources

Unit ids behind each passage, in this repository.

| Passage | Ids |
| --- | --- |
| Figures | RPT0027 (`sdlc-studio/reports/`), its Estimates table; `LANE_CALLS_FIXED` and `LANE_CALLS_PER_POINT` in `sprint.py`; `reference-agent-prompt-template.md` |
| A run's cost is measured on whichever harness ran it | US0986, US0987, US0988, US0989, US0990, US0991, US1121, US1125, US1127, BG1122, BG1236, BG1240, BG1244, BG1246, BG1280, BG1288 |
| The report states the run's cost in US dollars | US1117, US1122, US1123, US1124, US1135, BG1242, BG1252, BG1254 |
| A lane runs headless in any harness's CLI | US1118, US1119, US1120, US1126, US1129, US1130, US1131, US1132, BG1114, BG1245, BG1289, BG1290 |
| The gates and commit checks are faster and truer | US1112, US1113, US1115, US1133, BG1160, BG1167, BG1183, BG1187, BG1217 |
| Changed defaults and new refusals | BG1224, US1120, US1131, US1132, BG1160, BG1217, US0986, US1127, BG1240, US1112, US1113, US1115, US1133, BG1190, BG1167, US1117, US1123, US1135, US1129, US1130, BG1116 |
| Security fix | BG1213 |
| Upgrading from 6.2 | BG1224, US1131 |
| For contributors | US1114, US1116, US1128, BG1090, BG1248, BG1249, BG1147, BG1163, BG1197, BG1210, BG1212, BG1216, BG1220, BG1221, BG1223, BG1226 |
