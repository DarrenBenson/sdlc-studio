<!--
Template: Agent-instructions setup guide
Usage: Reference for whoever sets up a consuming project. Not copied into the project.
Related: agent-instructions.md, agent-instructions.CLAUDE.md, help/init.md
-->
# Agent instructions: one source of truth, per-tool pointers

Different agents read different filenames. To avoid maintaining the same rules in
several places, keep **one canonical file** and have each tool's file point to it.

| Tool | File it reads | What to put there |
| --- | --- | --- |
| Codex, Cursor, Gemini, Aider, Windsurf, Zed | `AGENTS.md` | The canonical content (`agent-instructions.md`) |
| Claude Code | `CLAUDE.md` | One line: `@AGENTS.md` (`agent-instructions.CLAUDE.md`) |
| GitHub Copilot | `.github/copilot-instructions.md` | A pointer or short summary referencing `AGENTS.md` |

`AGENTS.md` is the cross-tool standard (an open spec at <https://agents.md/>, read
natively by most coding agents). Claude Code reads `CLAUDE.md`; the supported bridge
is a `CLAUDE.md` that imports `@AGENTS.md`.

## Setup

1. Copy `agent-instructions.md` to your project root as `AGENTS.md`. Fill in every
   `{{placeholder}}` and delete the guidance comments.
2. Copy `agent-instructions.CLAUDE.md` to your project root as `CLAUDE.md`.
3. (Copilot users) Add `.github/copilot-instructions.md` that references `AGENTS.md`.
4. Keep `AGENTS.md` lean. For each line ask: "would removing this cause the agent to
   make a mistake?" If not, cut it. A bloated file gets ignored.

The canonical file deliberately does **not** restate the sdlc-studio doctrine - it
points at `.claude/skills/sdlc-studio/reference-doctrine.md` so the rules live in one
place and stay current as the skill updates.
