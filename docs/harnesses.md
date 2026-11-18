# Harness compatibility

SDLC Studio is a standard Agent Skill: a `SKILL.md`, its reference pages and Python 3 scripts.
It needs no particular harness. The installers write it where each of six harnesses reads
skills, and its gates are scripts, so they hold the same whichever harness runs the work. The
skill installs no git hooks in a project; a project that wants them wires its own from the
examples in the gate help. People own intent and sign-off; the harness runs the steps.

This page shows what each harness gives, and what happens where a harness lacks a feature. Each
cell names the file in this repository that shows it, or opens with Untested. A cell that claims
one part and leaves another untested names the file for the part it claims. Untested means
nothing in the repository exercises it yet. It does not mean the feature fails.

## Capability matrix

| Harness | Install path | Invocation | Skill discovery | Parallel or sub-agents | Token and cost reporting | Hooks and gates | Live reload |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Code | `--target claude`: `~/.claude/skills`, `.claude/skills` ([install.sh][install]) | `/sdlc-studio`, or chosen by the model ([install.sh][install]) | `.claude/skills` only; it does not read `.agents/skills` ([install.sh][install]) | `sdlc-builder` and `sdlc-reviewer` subagents that `init` installs ([init.py][init]); headless lanes ([harness_usage.py][usage]) | Session and subagent transcripts ([token_meters.py][meters]) | `gate.py`, and git hooks a project wires ([gate.md][gate]); optional Stop hook ([close_guard.py][closeguard]) | Skill edits take effect mid-session ([CLAUDE.md][claudemd]) |
| Codex | `--target codex`: `~/.agents/skills`, `.agents/skills` ([install.sh][install]) | `$sdlc-studio`, `/skills`, or chosen by its description ([install.sh][install]) | `.agents/skills`, `.codex/skills` ([install.sh][install]) | Headless lanes, `sprint lane run --harness codex` ([harness_usage.py][usage]); in-session sub-agents untested | Codex state store under `CODEX_HOME` ([meter_codex.py][codex]) | `gate.py`, and git hooks a project wires ([gate.md][gate]) | Untested |
| Cursor | `--target agents`: `~/.agents/skills`, `.agents/skills` ([install.sh][install]) | Untested | `.agents/skills`, `.cursor/skills`, `.claude/skills`, `.codex/skills` ([install.sh][install]) | Headless lanes, `sprint lane run --harness cursor` ([harness_usage.py][usage]); in-session sub-agents untested | Cloud usage API (opt-in) or the CLI hook's ledger ([meter_cursor.py][cursor]) | `gate.py`, and git hooks a project wires ([gate.md][gate]); `afterAgentResponse` usage hook ([cursor_usage_hook.py][cursorhook]) | Untested |
| Gemini CLI | `--target gemini`: `~/.gemini/skills`, `.gemini/skills` ([install.sh][install]) | `/skills` confirms it is found, then it is used automatically ([install.sh][install]) | `.gemini/skills`, `.agents/skills` ([install.sh][install]) | Untested | Untested: no reader | `gate.py`, and git hooks a project wires ([gate.md][gate]) | Untested |
| GitHub Copilot | `--target copilot`: `~/.agents/skills`, `.github/skills` ([install.sh][install]) | `copilot skill list` confirms it, then ask in chat ([install.sh][install]) | `~/.copilot/skills`, `~/.agents/skills`; in a repository `.github/skills`, `.agents/skills`, `.claude/skills` ([install.sh][install]) | Headless lanes, `sprint lane run --harness copilot` ([harness_usage.py][usage]); in-session sub-agents untested | Session events under `COPILOT_HOME` ([meter_copilot.py][copilot]) | `gate.py`, and git hooks a project wires ([gate.md][gate]) | Untested |
| opencode | `--target opencode`: `~/.config/opencode/skills`, `.opencode/skills` ([install.sh][install]) | Found by its skill tool ([install.sh][install]) | `.opencode/skills`, `.claude/skills`, `.agents/skills` ([install.sh][install]) | Headless lanes, `sprint lane run --harness opencode` ([harness_usage.py][usage]); in-session sub-agents untested | `opencode.db`, or the file `OPENCODE_DB` names ([meter_opencode.py][opencode]) | `gate.py`, and git hooks a project wires ([gate.md][gate]) | Untested |

The GitHub Copilot row is Copilot CLI, the client the installer and the token meter read; Copilot
in an editor is untested. The install path is the folder each installer writes, global first,
then the one `--local` writes; one `--target agents` install also serves Codex, Gemini CLI and
Copilot CLI.

## Fallbacks

| Feature | Works in | Without it |
| --- | --- | --- |
| `epic implement --agentic` (concurrent waves of stories) | Claude Code, through its Agent tool with worktree isolation | Plain `epic implement`: the same stories run one at a time in dependency order, through the same gates ([epic.md][epic]) |
| Sub-agents for sprint lanes | Claude Code | `sprint lane run --harness <h>` runs each lane as one fresh headless session in Cursor, Codex, Copilot CLI or opencode; in any other harness, start a fresh session per unit from the brief `sprint lane brief` prints ([sprint.md][sprint]) |
| The token meter | Claude Code, Codex, Cursor, GitHub Copilot, opencode | A run with no reading reports no figure, never zero; give the total read from your harness with `sprint report --tokens N` ([sprint.md][sprint]) |
| Git hooks a project wires from the gate help's examples (`pre-commit`, `commit-msg`) | Every harness: git runs them, not the harness | Where a project wires none, or they are off, run `gate.py --root .` in CI or any shell; the help shows CI jobs, a pre-commit hook and a commit-msg hook ([gate.md][gate]) |
| Live reload of skill edits | Claude Code | Start a new session after an install, upgrade or edit; `skill-update` tells you to reload when it installs ([skill-update.md][skillupdate]) |
| The Stop hook that flags an owed sprint close | Claude Code | `status` reports an owed close as an advisory ([gate.md][gate]) |
| The `afterAgentResponse` usage hook | Cursor CLI | The opt-in cloud usage API reading; with neither, no figure, as for the token meter ([meter_cursor.py][cursor]) |

## How each cell was verified

- **Install path.** The folders in `install.sh`'s `target_dir` and `install.ps1`'s target map.
  `tools/tests/test_harness_matrix_doc.py` reads both installers and fails when a path on this
  page differs from them, or when the two installers differ from each other.
- **Invocation.** The note each installer prints after an install, per target. Cursor gets none,
  so its cell is untested.
- **Skill discovery.** The folders `install.sh`'s `read_dirs` records for each tool, which its
  next-step hint reads to tell whether a tool already has a copy.
- **Parallel or sub-agents.** The agent definitions `init` installs into `.claude/agents/`, and
  the five CLIs whose headless output `harness_usage.py` parses from captured sessions.
- **Token and cost reporting.** The reader each harness has in `scripts/lib/`, chosen by
  `token_meters.py`. Gemini CLI has no reader.
- **Hooks and gates.** `gate.py` is a script, so it runs the same under every harness. The skill
  installs no git hooks; a project wires its own from the gate help, and git runs them whatever
  the harness. This repository's own are [pre-commit][precommit] and the others beside it,
  enabled by [enable-hooks.sh][enable]. Harness hooks are the two scripts named in the matrix.
- **Live reload.** This repository's own development, which edits the skill in a running Claude
  Code session. Nothing in the repository exercises reload in the other harnesses.

The test above also fails when a cell names no source, unless it opens with Untested and has no
second clause after a semicolon; when a source a cell names is missing; and when a fallbacks row
leaves Without it empty, or says there is none in a phrasing the test lists, such as "No
fallback.", "Nothing." or "not available".

[install]: ../install.sh
[init]: ../.claude/skills/sdlc-studio/scripts/init.py
[usage]: ../.claude/skills/sdlc-studio/scripts/lib/harness_usage.py
[meters]: ../.claude/skills/sdlc-studio/scripts/lib/token_meters.py
[codex]: ../.claude/skills/sdlc-studio/scripts/lib/meter_codex.py
[copilot]: ../.claude/skills/sdlc-studio/scripts/lib/meter_copilot.py
[cursor]: ../.claude/skills/sdlc-studio/scripts/lib/meter_cursor.py
[opencode]: ../.claude/skills/sdlc-studio/scripts/lib/meter_opencode.py
[cursorhook]: ../.claude/skills/sdlc-studio/scripts/cursor_usage_hook.py
[closeguard]: ../.claude/skills/sdlc-studio/scripts/hooks/close_guard.py
[gate]: ../.claude/skills/sdlc-studio/help/gate.md
[epic]: ../.claude/skills/sdlc-studio/help/epic.md
[sprint]: ../.claude/skills/sdlc-studio/help/sprint.md
[skillupdate]: ../.claude/skills/sdlc-studio/help/skill-update.md
[claudemd]: ../CLAUDE.md
[precommit]: ../.githooks/pre-commit
[enable]: ../tools/enable-hooks.sh
