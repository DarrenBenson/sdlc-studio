# Installing SDLC Studio

SDLC Studio is a standard [Agent Skill](https://code.claude.com/docs/en/skills)
(`SKILL.md`). Any tool that reads the agent-skills directory can use it: Claude
Code, OpenAI Codex, Gemini CLI, opencode, and GitHub Copilot all read the same
skill. Installing is therefore just copying the skill into the tool's skills
folder - which the installer scripts do for you.

- [Quick start](#quick-start)
- [Choosing tools](#choosing-tools)
- [Where each tool reads skills](#where-each-tool-reads-skills)
- [Global vs local](#global-vs-local)
- [Windows](#windows)
- [Native installers](#native-installers)
- [Manual install](#manual-install)
- [Updating and uninstalling](#updating-and-uninstalling)
- [Verifying](#verifying)
- [Troubleshooting](#troubleshooting)

## Quick start

macOS / Linux (installs the Claude Code skill, globally):

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
```

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.ps1 | iex
```

To install into every coding agent you have, add `--target auto` (PowerShell:
`-Target auto`). See below.

## Choosing tools

Pass `--target` (bash) or `-Target` (PowerShell) a comma-separated list, or one
of the shortcuts `all` / `auto`. Default is `claude`. The table shows the value;
append it to the one-liner, e.g.
`curl -fsSL .../install.sh | bash -s -- --target gemini` (PowerShell:
`.\install.ps1 -Target gemini`).

| You want | `--target` / `-Target` value |
| --- | --- |
| Claude Code | (default - no flag needed) |
| Codex | `codex` |
| Gemini CLI | `gemini` |
| opencode | `opencode` |
| Copilot | `copilot` (with `--local`) |
| Several at once | `gemini,codex` |
| Every tool you have | `auto` |
| Every supported tool | `all` |

`auto` detects a tool when its CLI is on `PATH` or its config directory exists.
`--list-targets` (`-ListTargets`) prints the full map and what was detected
without installing anything.

## Where each tool reads skills

| Tool | Global (per-user) | Local (per-project) |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.agents/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| opencode | `~/.config/opencode/skills/` | `.opencode/skills/` |
| Copilot | (repo-scoped) | `.github/skills/` |

Two of these are shared aliases: `~/.agents/skills/` is read by Codex, Gemini
**and** opencode, and `~/.claude/skills/` is read by Claude Code and opencode.
Copilot skills are repo-scoped, so `copilot` always installs into the project's
`.github/skills/` (a `--global copilot` request is redirected there with a
warning).

## Global vs local

- **Global** (default): the skill is available in every project for that tool.
- **Local** (`--local` / `-Local`): the skill is installed into the current
  project only, so you can commit it with the repo and share it with your team.

## Windows

Use `install.ps1` with the same semantics: `-Target`, `-Global` / `-Local`,
`-Uninstall`, `-ListTargets`, `-DryRun`, `-Version`. To pass options when piping
through `iex`, download first:

```powershell
irm https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.ps1 -OutFile install.ps1
.\install.ps1 -Target auto
```

Note: opencode's Windows global skills path follows its cross-platform
`~/.config/opencode/` convention.

## Native installers

Because SDLC Studio is a standard skill, each tool's own installer also works:

```bash
gh skills install DarrenBenson/sdlc-studio sdlc-studio          # GitHub Copilot (gh >= 2.90)
gemini skills install https://github.com/DarrenBenson/sdlc-studio   # Gemini CLI
```

Codex auto-discovers skills placed in its skills directory; you can also use its
in-session `$skill-installer`.

## Manual install

Clone and copy the skill folder into whichever directory from the
[map](#where-each-tool-reads-skills) you want:

```bash
git clone https://github.com/DarrenBenson/sdlc-studio.git
mkdir -p ~/.claude/skills
cp -r sdlc-studio/.claude/skills/sdlc-studio ~/.claude/skills/
```

The skill is self-contained (markdown plus pure-stdlib Python helpers), so no
build or dependency install is needed.

## Updating and uninstalling

- **Update**: re-run the installer; it replaces the existing copy in place.
- **Stale-copy sweep**: after installing, the installer also refreshes every
  other sdlc-studio copy it finds in the known tool locations (it never touches
  a directory without an sdlc-studio `SKILL.md`), reporting each refresh as
  `old -> new`. Skip this with `--no-sweep` (bash) or `-NoSweep` (PowerShell);
  preview it with `--dry-run`.
- **Specific version**: `--version v1.8.0` (bash) or `-Version v1.8.0`
  (PowerShell).
- **Uninstall**: `--uninstall` (bash) or `-Uninstall` (PowerShell), with the same
  `--target` / scope you installed with. Preview first with `--dry-run`. The
  uninstall does not sweep other locations.

## Verifying

After installing, start your tool in any project and check the skill loads:

- Claude Code: `/sdlc-studio status`
- Codex: mention `$sdlc-studio`, or run `/skills` to confirm it is listed
- Gemini CLI: `/skills` to confirm discovery
- opencode: it is discovered automatically via the skill tool
- Copilot: it reads `.github/skills/` in the repo

## Troubleshooting

- **Skill not picked up**: confirm the files landed in the right directory for
  your tool (see [Where each tool reads skills](#where-each-tool-reads-skills)),
  then restart the tool (Codex, Gemini and opencode have a skills-reload command,
  e.g. `/skills reload`).
- **`--target auto` skipped a tool**: detection keys off the CLI on `PATH` or the
  config directory. Name the tool explicitly with `--target <tool>` instead.
- **Copilot**: skills live in the repo at `.github/skills/`; install with
  `--local` from inside the project.
- **Windows piping**: `iex` cannot take arguments; download the script first (see
  [Windows](#windows)).
