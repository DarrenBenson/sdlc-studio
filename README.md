<div align="center">

<h1>SDLC Studio</h1>

**The antidote to vibe coding: a full software engineering team at your fingertips.**

Ask for software in plain language. The team plans it, builds it, tests it, and proves it is done.

**Version:** 6.4.0

[![Licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
[![Lint](https://github.com/DarrenBenson/sdlc-studio/actions/workflows/lint.yml/badge.svg)](https://github.com/DarrenBenson/sdlc-studio/actions/workflows/lint.yml)
[![Agent Skill](https://img.shields.io/badge/format-Agent%20Skill-7c3aed.svg)](https://agentskills.io)

</div>

SDLC Studio is an open, harness-agnostic [Agent Skill](https://agentskills.io) that runs your
software development lifecycle from first idea to tested, working code, with a human in the lead:
people own the intent and the sign-off, and the agent does the work in between. Each step is
reviewed independently of its author, often by another agent, and a person you name signs each
run once, over the report it ends with. Every requirement, review and sign-off is a plain file
committed beside the code, so the record the work leaves is the evidence. It runs in **Claude
Code, Codex, Cursor, Gemini CLI, GitHub Copilot and opencode**, on the models your harness
provides under your own contract, and is tied to none of them
([harness compatibility](docs/harnesses.md), [adopting it in an enterprise](docs/enterprise.md)).

If you are a coding agent, [llms.txt](llms.txt) is a machine-readable index of this repository and [AGENTS.md](AGENTS.md) is the guidance for working in it.

## Three ways in

- **Evaluate it.** If you answer for your teams' releases, start with
  [SDLC Studio for engineering leaders](docs/engineering-leaders.md): what the record a run
  leaves proves, who answers for each part of it, and what a point of delivery costs. You do not
  need to run a command to follow it. Then check it against
  [the evidence from the runs](docs/evidence.md), every signed run read from its report, with
  nothing typed by hand.
- **Try it.** Install it once ([below](#quick-start), or [the install guide](docs/INSTALL.md)
  for every tool, Windows and a verified download), then say "start a new project" or "extract
  the spec from this code". On a repository you already have, `/sdlc-studio audit --profile repo`
  audits the code without changing it and files what it finds as bugs and change requests.
- **Upgrade.** Already running SDLC Studio? Your artefacts are safe and nothing is rewritten
  without asking, but v6 is not a drop-in: it refuses the verbs, flags and config keys it
  retired, each by name with its replacement. Run `migrate`, then `migrate --apply`, and follow
  [docs/existing-users.md](docs/existing-users.md).

What changed in the current release: [the 6.4.0 release notes](docs/release-notes-v6.4.0.md).
How a run goes, step by step: [the loop](.claude/skills/sdlc-studio/reference-sprint.md#the-loop).

## What a run gives you

v6 keeps what catches defects, acceptance criteria that run and a review by someone other than
the author, and drops the ceremony around each unit that caught nothing.

- **One plan.** A Sprint Goal is one sentence. `sprint plan` orders and sizes the batch, and you
  approve it once.
- **One review per unit.** Each unit is built against its acceptance criteria and reviewed by one
  independent reviewer, in at most two rounds, recorded in one verdict ledger. The author of a
  change is never its reviewer, and a story reaches Done only when its criteria pass.
- **One signature.** `sprint close` files a one-page report that states every known issue, and
  `sprint sign` seals it once, from someone who neither built nor reviewed a unit in it.
- **It learns from its own runs.** What went wrong is recorded as a failure class and its rule is
  carried into the next plan, build and review.
- **New in 6.4: evidence a change board can read.** `release_cut.py evidence-pack` builds one
  evidence pack per release from committed records alone: for each change, what changed, which
  criteria passed, who reviewed it independently, what is known to be wrong and who signed for
  it. `retro.py seats` keeps each review seat's record, and `escape.py trace` traces an escaped
  defect to the approval that missed it, which that record then counts. `sprint plan` forecasts
  a run's cost and wall-clock span, and the signed report sets each forecast beside the actual.
- **New in 6.3: a cost you can read.** The signed report states the run's priced tokens and
  estimated US dollars per point, priced per model, read from the store of whichever harness ran
  it: Claude Code, Codex CLI, Copilot CLI, OpenCode or Cursor. `sprint cost --anatomy` names where
  the tokens went, and `sprint lane run --harness <h>` runs one unit headless in any of their
  CLIs.

People and agents work side by side: a new project mints ids that never clash, so several people
and agents on different machines can file work at once, and `persona generate --team` grows the
seats that build and review from your own project. How it fits together, with worked examples, is
in [Why SDLC Studio](docs/why-sdlc-studio.md#how-it-works).

## Quick start

Install for every harness this machine has, on macOS or Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash -s -- --target auto
```

Or name harnesses, as in `--target claude,copilot`; `--local` installs into the current project.
On Windows, use [install.ps1](docs/INSTALL.md#windows).

| Harness | `--target` | Global | Project-local | Invoke as | Verify with |
| --- | --- | --- | --- | --- | --- |
| Claude Code | `claude` | `~/.claude/skills` | `.claude/skills` | `/sdlc-studio`, or model-invoked | `/sdlc-studio status` |
| Codex | `codex` | `~/.agents/skills` | `.agents/skills` | `$sdlc-studio` | `/skills` |
| Copilot | `copilot` | `~/.agents/skills` | `.github/skills` | ask in chat | `copilot skill list` |
| Cursor | `agents` | `~/.agents/skills` | `.agents/skills` | untested | `ls ~/.agents/skills/sdlc-studio/SKILL.md` |
| Gemini CLI | `gemini` | `~/.gemini/skills` | `.gemini/skills` | automatic, from its description | `/skills` |
| opencode | `opencode` | `~/.config/opencode/skills` | `.opencode/skills` | found by its skill tool | `ls ~/.config/opencode/skills/sdlc-studio/SKILL.md` |

Copilot here is GitHub Copilot CLI; Copilot in an editor is untested. What each harness gives,
and the fallback where one lacks a feature: [harness compatibility](docs/harnesses.md).

**Installing in a sensitive environment?** Pin a tagged release and make the checksum
mandatory, so the installer refuses rather than proceed unverified:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | SDLC_STUDIO_REQUIRE_CHECKSUM=1 bash -s -- --version v6.4.0 --target auto
```

What it verifies: [Verifying the download](docs/INSTALL.md#verifying-the-download).

Then ask in plain language; each phrase also has a command. The scripts need Python 3.10 or later
and PyYAML, both required ([requirements](docs/INSTALL.md#requirements)).

```text
"start a new project"                                 →  /sdlc-studio init, then prd create
"extract the spec from this code"                     →  /sdlc-studio prd generate
"plan the next sprint"                                →  /sdlc-studio sprint --crs Proposed --goal plan
"build the proposed change requests"                  →  /sdlc-studio sprint --crs Proposed --goal done
"create a change request to delete archived records"  →  /sdlc-studio cr create
"log an issue: checkout 500s intermittently"          →  /sdlc-studio issue create
"triage that issue into bugs"                         →  /sdlc-studio triage apply --issue IS0001
"what should I work on next?"                         →  /sdlc-studio hint
"where is the project up to?"                         →  /sdlc-studio status
```

## FAQ

<details>
<summary>How do I upgrade?</summary>

Re-run the installer, or `/sdlc-studio skill-update`. Each release's steps are a section of
**[docs/existing-users.md](docs/existing-users.md)**: on 6.0, reinstall, then run `migrate` and
`migrate --apply`, and **[From 6.0 to 6.1](docs/existing-users.md#from-60-to-61)** names what 6.1
retires and what replaces it. To carry a v5 project to v6, run `migrate` (a dry run naming what
it would change), then `migrate --apply`: it removes the config keys and `[check:]` tags v6
retired and restamps the project version, keeping every other byte.

</details>

More answers: [what it needs and where it writes](docs/INSTALL.md#requirements), and
[the ideas in plain words](docs/why-sdlc-studio.md#common-questions).

## Documentation

- **[sdlc-studio.com](https://sdlc-studio.com)** - the documentation home: guided
  walkthroughs, the concept guides, the FAQ and the install guide for every tool.
- [Why SDLC Studio](docs/why-sdlc-studio.md) - the argument, the evidence, the economics, how it
  works and worked examples; [the white paper](docs/whitepaper.md) ([PDF](docs/whitepaper.pdf))
  is the deep version.
- [docs/existing-users.md](docs/existing-users.md) - the upgrade steps, and what a new version
  refuses and how to clear it.
- [docs/INSTALL.md](docs/INSTALL.md) - the installer reference, requirements and troubleshooting.
- `/sdlc-studio help` - the command catalogue ([help/help.md](.claude/skills/sdlc-studio/help/help.md)),
  with the [greenfield](.claude/skills/sdlc-studio/help/getting-started.md) and
  [brownfield](.claude/skills/sdlc-studio/help/brownfield-runbook.md) runbooks.
- [docs/known-issues.md](docs/known-issues.md) - the defects this release ships with, and the bar
  it was held to.
- [CHANGELOG.md](CHANGELOG.md), [SECURITY.md](SECURITY.md) and [SUPPORT.md](SUPPORT.md).

Release notes:

- [docs/release-notes-v6.4.0.md](docs/release-notes-v6.4.0.md) - the current release: a release carries the evidence a change board accepts, a run's cost is forecast before it starts and set beside what it cost, and the 6.3 upgrade path
- [docs/release-notes-v6.3.0.md](docs/release-notes-v6.3.0.md), [docs/release-notes-v6.2.0.md](docs/release-notes-v6.2.0.md), [docs/release-notes-v6.1.0.md](docs/release-notes-v6.1.0.md) and [docs/release-notes-v6.0.0.md](docs/release-notes-v6.0.0.md) - the earlier v6 releases, each with its upgrade path
- [docs/release-notes-v6.0.0-rc.1.md](docs/release-notes-v6.0.0-rc.1.md) - the release candidate, and every surface it retired
- [docs/release-notes-v5.1.0.md](docs/release-notes-v5.1.0.md), [docs/release-notes-v5.0.1.md](docs/release-notes-v5.0.1.md) and [docs/release-notes-v5.0.0.md](docs/release-notes-v5.0.0.md) - the v5 releases

## Contributing

Dev instructions live in [AGENTS.md](AGENTS.md), read natively by Codex, Copilot, Cursor and
Gemini; Claude Code imports it through CLAUDE.md. Behavioural eval scenarios live in
[evals/](evals/README.md). See [CONTRIBUTING.md](CONTRIBUTING.md).

## Acknowledgements

Proudly supported by **Anthropic** through the **Claude for Open Source** programme. Sponsorship
supports the project's development; it is not an endorsement of any claim made here, and the
benchmark evidence is published whichever way it points. SDLC Studio does not require Anthropic
products: it runs in any of the six harnesses above.

## Licence

[MIT](LICENSE). Runs entirely in your own repository: no account, no server, no data leaves your
machine.
