# SDLC Studio v6.1.0

**SDLC Studio 6.1.0 is the current release: a run now ends with the sprint report you sign, and
that report states what it measured rather than what it could see.**

Every entry is in [the CHANGELOG's 6.1 section](../CHANGELOG.md#610---2026-10-03). If you run SDLC
Studio on a project already, [the existing-users page](existing-users.md) is the whole upgrade
path, and its "From 6.0 to 6.1" section is the part that is new.

## What changed for you

- **A run ends with its signed report.** The handoff page is gone. `sprint.py close` files the
  sprint report, puts its rendered page in front of you before it asks for the signature, and
  `sprint.py sign` seals it. The report's known-issues section already lists every open finding
  raised in the run and every carried unit, and the next `sprint.py plan` names the last signed
  report and its open items; `sprint.py plan --worklist RPTxxxx` plans them. The HO files you
  already have stay readable, and `handoff.py show` still prints the remaining work without
  writing anything.
- **The report states what it measured.** A unit built through `sprint.py lane brief` and
  `lane return` is now measured: in RPT0014, 29 of 34 units read NOT MEASURED because lane-built
  units never opened a span. `lane return --tokens N --minutes M` records the builder agent's own
  totals against its unit, so a delegated agent's spend counts: RPT0014's token actual was the
  main thread's meter alone and read 0.2x of its forecast, where RPT0016's adds 53 agent totals.
  The minutes ratio compares like with like: RPT0016 sets 37 units' measured active minutes
  against their forecast, where RPT0015 compared the run's wall-clock span with active work. A
  ratio the page cannot derive is withheld and the units that left it short are named.
- **A plain install is the latest verified release.** `install.sh` with no `--version` installs
  the latest published release and checks it against its `.sha256`, instead of the unverified
  `main` branch. Copilot CLI installs globally, to the `~/.agents/skills` folder it reads, and
  the default install names a tool on your machine that finds no copy and the `--target` that
  adds one. Install and upgrade no longer damage a project's own files.
- **`migrate` tells you more of what it leaves you.** It names each line of your markdown docs
  that still names a retired command, in code or in plain prose, with what replaced it; a line
  that only talks about handoffs is not named.
  Its report now agrees with the gate: each item that speaks for a gate lane carries the lane's
  name and count, it names the engagement-floor and conformance cutoffs, seeds the `.gitignore`
  `init` writes, and names a file it cannot read rather than stopping with a traceback.
- **Fewer hand moves at the close.** `sprint.py sign` moves the approved units to Done or Fixed
  without invalidating the page it has just sealed, so nothing is moved by hand before the
  close. The reviewer whose REJECT carried a unit at the review cap can discharge it with an
  APPROVE, the carried bug is filed ready for the next plan, and a lesson class finishes its
  lifecycle at the close with no hand edit to `lessons.jsonl`.

## Upgrading from 6.0

Reinstall, then carry each project across:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py"            # dry run: lists what it would change, writes nothing
python3 "$CLAUDE_SKILL_DIR/scripts/migrate.py" --apply    # removes review.policy, restamps the project version
```

**Reinstall.** A plain `install.sh` or `install.ps1` now fetches the latest verified release;
pass `main` as the version for the moving branch.

**`migrate`** is the dry run: it writes nothing, and lists what `--apply` would change and what
it leaves to you.

**`migrate --apply`** removes `review.policy` from `sdlc-studio/.config.yaml`, the one config key
6.1 retires, keeping every other byte. Both runs name each line of your markdown docs that uses
a retired handoff command (`handoff.py generate`, `artifact.py new --type handoff`,
`gate.py --require-handoff`), with what replaced it, except that in the root `AGENTS.md` and
`CLAUDE.md` they name only `handoff.py generate`. Neither reads your CI files or scripts:
search those yourself, since a CI job that runs `gate.py --require-handoff` is refused by the
gate rather than named by `migrate`.

The HO files already in `sdlc-studio/handoffs/` stay readable: they resolve by id, reconcile
cleanly and are never rewritten. [The existing-users page](existing-users.md) has the same path
with each retired name beside its replacement.

## Breaking changes

Each change a 6.0 user meets by being refused or surprised, with what to use instead:

- **`handoff.py generate` and `artifact.py new --type handoff` are gone.** The signed sprint
  report hands over the remaining work: `sprint.py sign` seals it, and
  `sprint.py plan --worklist RPTxxxx` plans its open items as the next run.
- **`gate.py --require-handoff` is gone.** The signed report from `sprint.py sign` is the run's
  hand-over, and the close's gate runs without it.
- **The `review.policy` key is retired.** `migrate --apply` removes it. Every project now
  carries a unit whose REJECT stands at the review cap (`review.max_rounds`), filing its
  findings as a bug.
- **A plain install no longer tracks `main`.** `install.sh` with no `--version` installs the
  latest published release; pass `--version main` to keep the moving branch (`-Version main`
  for `install.ps1`).
- **Copilot CLI's global target moved to `~/.agents/skills`.** `--target copilot` writes the
  personal folder Copilot CLI reads, where it wrote the current directory's `.github/skills`;
  `--local` still writes the repository's `.github/skills`.
- **The release gate's `revert-check` lane is gone.** A tag runs `release-rehearsal` and
  `module-alone` beside the full suite. The per-unit `verify_ac.py revert-check --unit <id>`
  stays, for an author to run on one unit.
- **`validate.py check` exits 1 where there is no `sdlc-studio/` workspace**, and says so, where
  it printed a clean count at exit 0. A script that ran it outside a workspace now fails.

## Known issues

Every open finding this release ships is listed by id on [the disclosure page](known-issues.md),
which `tools/known_issues.py write` generates from the bug corpus at the cut, together with the
count below, so the two cannot disagree.

**v6.1.0 discloses 13 open defects: 3 Medium, 10 Low.**

## Sources

Unit ids behind each passage, in this repository.

| Passage | Ids |
| --- | --- |
| Figures | RPT0014, RPT0015 and RPT0016 (`sdlc-studio/reports/`), each figure from its Estimates table |
| A run ends with its signed report | US0967, US0978, BG0912 |
| The report states what it measured | CR0605, CR0606, BG0898, BG0900, BG0901, BG0905, BG0924 |
| A plain install is the latest verified release | US0968, BG0852, BG0855, BG0856, US0976 |
| `migrate` tells you more | US0975, BG0896, BG0925, BG0929, BG0842, BG0843, BG0844, BG0845, BG0854, BG0858, US0974 |
| Fewer hand moves at the close | BG0848, BG0850, BG0829, US0977, BG0849 |
| Breaking changes | US0978, BG0831, US0968, BG0852, US0784, US0969 |
