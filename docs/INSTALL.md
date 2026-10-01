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
- [Verifying the download](#verifying-the-download)
- [Installing unreleased work (dev testing)](#installing-unreleased-work-dev-testing)
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
| Copilot CLI | `copilot` (the personal `~/.agents/skills`; with `--local`, the repo's `.github/skills`) |
| Several at once | `gemini,codex` |
| Codex + Gemini + Copilot + Cursor in one copy | `agents` (the generic `.agents/skills` dir) |
| Every tool you have | `auto` |
| Every supported tool | `all` |

The generic `.agents/skills` directory is read by Codex, Gemini CLI, Copilot,
and Cursor, so one `agents` install serves all four (`codex`, `copilot` and
`agents` resolve to the same directory globally; the installer dedups). Claude
Code does not read it - keep the `claude` target for Claude Code.

`auto` detects a tool when its CLI is on `PATH` or its config directory exists.
Copilot is detected by the `copilot` CLI or `~/.copilot`; `gh` and a `.github`
folder count only for a `--local` install. The default install (Claude Code
only) names each other tool on the host that finds no copy of the skill in any
folder it reads, and the `--target` that would add one. A tool counts as on the
host by its CLI or its own config folder, never a shared `~/.agents` or a repo's
`gh` or `.github`. Since opencode and Cursor also read `~/.claude/skills`, the
default install serves them and they are not named.
`--list-targets` (`-ListTargets`) prints the full map and what was detected
without installing anything.

## Where each tool reads skills

| Tool | Global (per-user) | Local (per-project) |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.agents/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| opencode | `~/.config/opencode/skills/` | `.opencode/skills/` |
| Copilot | `~/.agents/skills/` | `.github/skills/` |

Two of these are shared aliases: `~/.agents/skills/` is read by Codex, Gemini
**and** opencode, and `~/.claude/skills/` is read by Claude Code and opencode.
Copilot CLI reads two personal folders, `~/.agents/skills/` and
`~/.copilot/skills/`. `copilot` installs into `~/.agents/skills/` globally, so
one copy serves Copilot CLI and the `agents` tools, and into the project's
`.github/skills/` with `--local`. The installer never writes
`~/.copilot/skills/`, but a global install refreshes a copy it finds there.
`install.ps1` does not do this yet: a `-Global` copilot request there still goes
to the project's `.github\skills`, so use `-Target agents` on Windows.

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
  If you installed the 6.0.0-rc.1 candidate, its version check will not offer a later 6.0.0:
  reinstall rather than waiting for the prompt. Carrying a v5 project to v6 is a separate step,
  `migrate` then `migrate --apply`; see [existing users](existing-users.md).
- **Stale-copy sweep**: after installing, the installer also refreshes every
  other sdlc-studio copy it finds in the known tool locations within its reach
  (it never touches a directory without an sdlc-studio `SKILL.md`), reporting
  each refresh as `old -> new`. A global install reaches the personal and the
  current project's tool directories; a local install (`--local` / `-Local`)
  reaches only the project's, so pinning a version in one project never moves
  the personal copies every other project loads. Skip the sweep with
  `--no-sweep` (bash) or `-NoSweep` (PowerShell); preview it with `--dry-run`.
- **A personal copy wins in Claude Code**: Claude Code loads a personal skill
  ahead of a project skill of the same name, so a local install under a
  personal copy warns, naming both paths and versions, and leaves the personal
  copy as it is.
- **Specific version**: `--version <tag>` (bash) or `-Version <tag>`
  (PowerShell), for example `--version v6.0.0`.
- **Uninstall**: `--uninstall` (bash) or `-Uninstall` (PowerShell), with the same
  `--target` / scope you installed with. Preview first with `--dry-run`. The
  uninstall does not sweep other locations.

## Verifying

After installing, start your tool in any project and check the skill loads:

- Claude Code: `/sdlc-studio status`
- Codex: mention `$sdlc-studio`, or run `/skills` to confirm it is listed
- Gemini CLI: `/skills` to confirm discovery
- opencode: it is discovered automatically via the skill tool
- Copilot CLI: `copilot skill list` shows it; it reads `~/.agents/skills/`,
  `~/.copilot/skills/` and, in a repo, `.github/skills/`

## Verifying the download

The default install fetches the latest published release and verifies it against its
published digest. If the release cannot be looked up (offline, rate-limited), the installer
says so and falls back to `main`, a moving branch with no published digest, and proceeds
unverified; `--version main` asks for `main` by name. If you need the download verified,
pin a tag and make the check mandatory. The example pins the current release; name any later tag the same way.

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh \
  | SDLC_STUDIO_REQUIRE_CHECKSUM=1 bash -s -- --version v6.0.0
```

```powershell
$env:SDLC_STUDIO_REQUIRE_CHECKSUM = '1'
irm https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.ps1 | iex
```

| Variable | Effect |
| --- | --- |
| `SDLC_STUDIO_REQUIRE_CHECKSUM=1` | A missing digest is fatal. Without it, an unverifiable download warns and proceeds |
| `SDLC_STUDIO_SHA256=<digest>` | Verify against a digest you supply, instead of the published one |

**What is verified.** For a tagged version the installer downloads a `.tar.gz` (or `.zip` on
Windows) that this project built from the tag and published as a release asset, and checks it
against a `.sha256` published beside it in the same automated step. Both the bytes and the
digest are produced together, so they cannot drift apart. Verification happens before
extraction, so a swapped archive is never unpacked.

The installer deliberately does **not** verify GitHub's generated source archives. Those are
regenerated by GitHub rather than published by us, and are not guaranteed byte-stable, so a
recorded digest for one can stop matching with nobody touching the tag. That failure arrives
as `Checksum mismatch`, which is indistinguishable from an attack.

**Tags before v5.0.1 have no published assets.** `SDLC_STUDIO_REQUIRE_CHECKSUM=1` refuses
them, because there is genuinely nothing to verify against. Use `v5.0.0` or later, or supply
your own `SDLC_STUDIO_SHA256`.

## Installing unreleased work (dev testing)

`install.sh` normally downloads the copy published on GitHub (the `main` branch),
so it cannot install local work you have not pushed yet. To test the working tree (e.g. before a GA tag),
install it as the source directly:

```bash
./install.sh --from .claude/skills/sdlc-studio        # from inside the source repo
```

The same identity and downgrade guards apply: `--from` refuses a directory that
is not an sdlc-studio skill, and it will not overwrite an install that is NEWER
than the tree being installed (force with `--allow-downgrade`). Running the
plain downloader from inside the source repo is safe too - the installer refuses
to downgrade the repo's own newer working copy - but `--no-sweep` keeps it from
touching other copies at all.

## Troubleshooting

- **Skill not picked up**: confirm the files landed in the right directory for
  your tool (see [Where each tool reads skills](#where-each-tool-reads-skills)),
  then restart the tool (Codex, Gemini and opencode have a skills-reload command,
  e.g. `/skills reload`).
- **`--target auto` skipped a tool**: detection keys off the CLI on `PATH` or the
  config directory. Name the tool explicitly with `--target <tool>` instead.
- **Copilot CLI lists no sdlc-studio**: install with `--target copilot` (or
  `agents`) into `~/.agents/skills/`, which Copilot CLI reads; `--local` installs
  into the repo's `.github/skills/` instead.
- **Windows piping**: `iex` cannot take arguments; download the script first (see
  [Windows](#windows)).
