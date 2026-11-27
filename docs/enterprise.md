# Adopting SDLC Studio in an enterprise

This page is for the reviewer who decides whether a team may use SDLC Studio: an architect, a
security reviewer, or the engineering lead who answers for the team's releases. Each section
answers one question, and each claim links the script, reference section or record that shows
it, so you can check it rather than take it on trust. People own the intent and the sign-off;
the agent does the work in between. For how one run's record reads at a change board, see
[SDLC Studio for engineering leaders](engineering-leaders.md).

## Harness and models

SDLC Studio is an Agent Skill: a folder of markdown instructions and standard-library Python
scripts that runs inside the coding agent your organisation already approves. The installer
copies it into the skills directory each supported tool reads: Claude Code, OpenAI Codex,
Gemini CLI, opencode, GitHub Copilot, and Cursor through the shared `.agents/skills` directory
([where each tool reads skills](INSTALL.md#where-each-tool-reads-skills)).

The skill never calls a model API. Every model call is your harness's own, on the models it
offers under your organisation's contract, so no separate subscription or vendor account is
needed ([model-tier routing](../.claude/skills/sdlc-studio/reference-config.md#routing)).

Which model does which work is yours to set. `routing.models` maps five difficulty tiers to
your own model ids, `routing.critic_tier` sets the reviewer's tier against the builder's, and
`routing.effort.builder` and `routing.effort.reviewer` set each one's reasoning effort,
and `routing.effort.docs`, `routing.effort.bug` and `routing.effort.code` set it per kind of unit.
Routing is advisory and off by default: the plan recommends a model for each unit and your harness
starts it. A delegated build, `sprint lane run --harness <name> --model <id>`, passes the model
to that harness's own CLI ([lanes.py](../.claude/skills/sdlc-studio/scripts/lib/lanes.py)).

## Data

SDLC Studio sends no telemetry. Its scripts read and write files in your repository and run git
on your machine. The table lists every network call in the installers and the installed skill,
what each contacts and when. `telemetry.py`, despite its name, writes run figures to files
committed in your own repository and makes no network call
([telemetry.py](../.claude/skills/sdlc-studio/scripts/telemetry.py)).

| File | What it contacts | When |
| --- | --- | --- |
| `install.sh` | `https://api.github.com` for the latest release tag, then `https://github.com` for the release archive and its sha256 digest, with `curl` or `wget` | When you run it. `--version <tag>` skips the latest-release lookup, and `--from <dir>` installs a local copy and downloads nothing |
| `install.ps1` | The same `https://api.github.com` and `https://github.com` addresses, with `Invoke-RestMethod` and `Invoke-WebRequest` | When you run it |
| `scripts/version_check.py` | `https://api.github.com` for the latest release tag; the request carries no project data | The first `status` or `hint` of a session, at most once a day by default; off with `version_check.enabled: false` |
| `scripts/sprint.py` | Your own git remote, with `git fetch origin`, to warn when your branch is behind it | `sprint plan` and `sprint boundary`; skipped with `--no-fetch` |
| `scripts/sprint_report.py` | Your repository's CI runs, read with `gh run list` | When `sprint close` files a run's report, and for a preview of the open run's report |
| `scripts/release_cut.py` | Your repository's CI runs on the commit to be tagged, read with `gh run list` | `release_cut.py tag-check`, before a release tag |
| `scripts/github_sync.py` | Your repository's GitHub Issues, through `gh`: an artefact's title and body go into an issue on push, and labelled issues are read on pull | Only when you run `github_sync.py push` or `pull`; without `--allow-secrets`, a record holding a secret-shaped string is not pushed to a public repository, or to one whose visibility `gh` cannot read |
| `scripts/lib/meter_cursor.py` | `https://api.cursor.com` for a Cursor cloud agent's token usage | Only when `CURSOR_API_KEY` and `SDLC_STUDIO_CURSOR_AGENT_ID` are both set |
| `scripts/verify_ac.py` | The `http://` or `https://` address a story's `http` Verify line names, with `curl` | When `verify_ac.py run` runs that criterion; `SDLC_VERIFY_HTTP_HOSTS` limits the hosts it may reach |

Two more paths leave your machine only through tools you already run. `sprint lane run` starts
your harness's own CLI on a brief, and what that CLI sends is your harness's traffic under your
contract ([lanes.py](../.claude/skills/sdlc-studio/scripts/lib/lanes.py)). No script runs
`git push`: pushing is yours. This repository's `tools/` directory holds its own maintenance
scripts, which the installer does not copy. A test scans the installers and the installed skill
for HTTP libraries, `curl`, `wget`, `gh` and git remote operations, and fails when a file it
finds is missing from this table ([the scan](../tools/tests/test_enterprise_doc.py)).

## Adopting without forking

- **Pin a release.** `install.sh --version v6.4.0`, or `-Version v6.4.0` in PowerShell,
  installs that tag, and `SDLC_STUDIO_REQUIRE_CHECKSUM=1` refuses a download with no published
  sha256 digest ([verifying the download](INSTALL.md#verifying-the-download)). A `--local`
  install sits in the project, so pinning one project never moves the copy other projects load
  ([updating](INSTALL.md#updating-and-uninstalling)).
- **Keep your configuration in your own repository.** A project's settings live in
  `sdlc-studio/.config.yaml`, its review seats in `sdlc-studio/personas/seats/`, which override
  the shipped seats, and its PRD, TRD and TSD under `sdlc-studio/`. The skill folder stays
  unmodified, so an upgrade replaces it whole
  ([configuration files](../.claude/skills/sdlc-studio/reference-config.md#configuration-files)).
- **Upgrade with two commands.** `skill-update` compares the installed version with the latest
  release and, once you confirm, runs the installer; `migrate` then reports what a project's
  artefacts need for the new version in one pass, and `migrate --apply` applies it
  ([the upgrade commands](../.claude/skills/sdlc-studio/reference-upgrade.md#three-upgrades)).
  `skill-update` always offers the latest release, so to move a pinned install, re-run the
  installer with the new `--version`. Where installs are managed centrally,
  `version_check.enabled: false` stops the update notice
  ([skill-update](../.claude/skills/sdlc-studio/help/skill-update.md)).
- **Share one approved copy.** A shared skills repository can hold a released version's skill
  folder, taken from the release asset at a pinned tag and checked against its digest. Each team
  then installs from a clone of it with `install.sh --from <clone>/.claude/skills/sdlc-studio`,
  which downloads nothing and applies the same identity and downgrade checks
  ([installing from a local copy](INSTALL.md#installing-unreleased-work-dev-testing)). The
  installer supports this pattern; this repository does not run one itself.

## Fitting existing controls

Each change carries its evidence in the same repository as its code: requirements, design, test
plans and results, an independent review, and sign-off by someone who neither wrote nor reviewed
the unit. Every record is a file under `sdlc-studio/` committed beside the code, so the commit or
pull request that carries a change carries its evidence too. The map below is generic, and its
links show this repository's own records. It describes evidence only: SDLC Studio holds no
certification, and nothing here is a claim of compliance with any standard.

| Control gate | Evidence each change carries |
| --- | --- |
| Requirements approved | The [PRD](../sdlc-studio/prd.md) and each story's acceptance criteria, written before the code ([a story](../sdlc-studio/stories/US1317-docs-enterprise-md-answers-an-enterprise-reviewer-harness.md)). A change request is not work until `refine` breaks it into sized stories, and `sprint plan` refuses a unit with no `Affects:` or `Points:` ([definition of ready](../sdlc-studio/definition-of-ready.md)) |
| Design reviewed | The [TRD](../sdlc-studio/trd.md) and the [decision log](../sdlc-studio/decisions.md), and a plan reviewer who is not the plan's author checking the criteria against the specification before any code ([plan-review verdicts](../sdlc-studio/reviews/plan-review-verdicts.md)) |
| Tests evidenced | The [TSD](../sdlc-studio/tsd.md) and [test specifications](../sdlc-studio/test-specs/_index.md), each criterion's Verify command run by `verify_ac.py`, and the Done gate, which refuses a story while any executable criterion is failing or has never run ([transition.py](../.claude/skills/sdlc-studio/scripts/transition.py)) |
| Independent review | A fresh reviewer who did not write the unit, briefed by `critic.py brief` with the criteria as the contract, its verdict written to a committed ledger beside the author's name ([verdict ledger](../sdlc-studio/reviews/critic-verdicts.md), [the review brief](../.claude/skills/sdlc-studio/reference-review.md#closing-review-brief)) |
| Approval before release | The run's report, signed by someone who neither wrote nor reviewed a unit in it, and the release's evidence pack, built from signed reports alone ([a signed report](../sdlc-studio/reports/RPT0035-sprint-report-run-01m7nty5.md), [evidence_pack.py](../.claude/skills/sdlc-studio/scripts/evidence_pack.py)) |

[SDLC Studio for engineering leaders](engineering-leaders.md) walks one run's record as a change
board reads it: change approval, separation of duties, and the signed report and its
fingerprint.

## Cost

Every run reports its own token use and cost. When a run closes, its report states the priced
tokens, the Dollar cost, the Dollars per point and each unit's dollars, with the forecast beside
each actual. `sprint report` re-reads a past run's page, `sprint cost` prints the open run's
spend so far, and `sprint cost --anatomy` breaks it down by role
([how dollars are priced](../.claude/skills/sdlc-studio/reference-sprint.md#dollar-cost)).
Dollars are estimates from a dated table of list prices, not an invoice. Set your contract rates
with `pricing.models` and the report prices at them
([model prices](../.claude/skills/sdlc-studio/reference-config.md#pricing)).

Before a run starts, `sprint plan` forecasts its minutes, priced tokens and dollars from the
project's own measured cost per point once three priced runs exist, and the report then states
the forecast, the actual and the actual over the forecast. Forecasts describe; they do not
promise ([forecast and actual](../.claude/skills/sdlc-studio/reference-sprint.md#dollar-cost)).
One of this repository's own runs forecast $3.37 a point and came in at $2.00 a point, $102.01
in all, as its signed report RPT0035 records
([RPT0035](../sdlc-studio/reports/RPT0035-sprint-report-run-01m7nty5.md),
[its JSON](../sdlc-studio/reports/RPT0035.json)).

There is no dollar budget setting. A run is bounded by `capacity.minutes`, `capacity.units` and
`capacity.spend`, the last in priced input-equivalent tokens and 0, unbounded, by default, which
its breaker enforces, while `capacity.tokens` is a plan-time warning only; `appetite.spend` sets
one run's spend, and `sprint plan --appetite-minutes`, `--appetite-units` and `--appetite-spend`
set one run's bounds
([sprint capacity](../.claude/skills/sdlc-studio/reference-config.md#capacity)). To hold a
monthly budget, add up the Dollar cost rows of that month's signed reports.

The meter reads the harness running the session: Claude Code, Codex, Copilot CLI, opencode or
Cursor. There is no reader for Gemini CLI
([token meters](../.claude/skills/sdlc-studio/reference-sprint.md#token-meters)). Under GitHub
Copilot it reads the token counts the Copilot CLI writes to its own session events file,
`session-state/<id>/events.jsonl` under `COPILOT_HOME` (by default `~/.copilot`), and no
premium-request count
([meter_copilot.py](../.claude/skills/sdlc-studio/scripts/lib/meter_copilot.py)).
`pricing.copilot_billing` says how your plan bills: `tokens`, the default, prices Copilot's
tokens, and `requests`, for a plan still billed per premium request, prices the premium requests
at `pricing.premium_request` and leaves those tokens unpriced, so a run is never billed twice. A
premium-request count, where a reading carries one, is your harness's own figure, shown on a row
of its own and never worked out from tokens; the count on your bill is GitHub's.

## Verification for less experienced engineers

- **People own the test contract.** Each story's acceptance criteria, each with a Verify
  command, are agreed before the code, and the test specifications are your team's documents,
  changed by review like code. A story reaches Done only when its executable criteria pass
  ([the Done gate](../.claude/skills/sdlc-studio/reference-scripts-create.md#transitionpy)).
- **An agent cannot quietly change the contract.** On a schema 3 project, the default for new
  ones, an edit to a requirements or specification document that the story does not name is a
  blocking review finding
  ([spec-edit guard](../.claude/skills/sdlc-studio/reference-config.md#spec-guard)).
- **Every unit gets a reviewer who did not write it.** A script briefs a fresh reviewer with the
  unit's criteria and scope, and the reviewer tries to break it; the signature stops at a unit
  with no approval from a reviewer other than its author
  ([the review brief](../.claude/skills/sdlc-studio/reference-review.md#closing-review-brief)).
- **The author checks their own work first.** Each claim in the change's prose is ruled true,
  false or unverifiable, and its tests are mutated to show they fail when they should;
  `review.author_self_check: block` refuses the review until that is recorded
  ([the author's self-check](../.claude/skills/sdlc-studio/reference-review.md#author-self-check)).

So a less experienced engineer's change meets the same contract, the same independent review and
the same sign-off as anyone else's, and the record shows which checks ran.
