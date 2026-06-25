# SDLC Studio Reference - Skill Update

`skill-update` upgrades the **installed skill** to the latest published release, on
explicit confirm - it updates the skill itself, not any project. It is one of three "upgrade"
surfaces (the other two migrate a *project's* artifacts); all three are named side by side in
`reference-upgrade.md#three-upgrades`.

<!-- Load when: the user runs /sdlc-studio skill-update or accepts an update notice -->

## When it runs

The skill checks for a newer release on the first `status`/`hint` of a session (see
`scripts/version_check.py`) and prints a one-line notice if one exists. The user then
runs `skill-update` to act on it. The check is on by default, opt-out via
`version_check.enabled: false`, silent offline, and cached (`version_check.ttl_hours`).

## Workflow {#skill-update-workflow}

1. **Read the status (deterministic):**

   ```bash
   python3 "$CLAUDE_SKILL_DIR/scripts/version_check.py" check --format json
   python3 "$CLAUDE_SKILL_DIR/scripts/version_check.py" scope
   ```

   `check` gives `{installed, latest, status, scope}`; `scope` is `user` / `project` /
   `agents` (detected from where the skill is installed).

2. **If already current** (`status` is `up-to-date` / `offline` / `disabled`): say so and
   stop. Nothing to do.

3. **Show the change and ask** - present `installed -> latest` and the scope, then ask
   the user to confirm. Do **not** upgrade without an explicit yes.

4. **On confirm, run the installer for the detected scope.** The installer replaces the
   skill in place and sweeps every tool's copy to the same version:

   | scope | command |
   | --- | --- |
   | user | `./install.sh` (default ~ targets) - or the published `curl … | bash` installer |
   | project | `./install.sh --local` (from a repo clone) |
   | agents | `./install.sh --target agents` |

   Prefer a local repo clone if present (`install.sh --local`); otherwise use the
   published remote installer. Running an installer is a side-effecting action - confirm
   first, and never pipe a remote script to a shell without the user's explicit ok.

5. **Tell the user to reload** so the new version activates (the running session keeps the
   old one until reloaded).

   Then **offer a project upgrade** if the consuming project is behind the new skill: run
   `python3 "$CLAUDE_SKILL_DIR/scripts/project_upgrade.py" --root <project>` (dry-run); if it
   reports BEHIND, surface the one-line gap and suggest `/sdlc-studio project upgrade` to migrate
   the project's artefacts (config, provenance cutoff, index drift, and a report of the
   judgement items). Never auto-applies - see `reference-upgrade.md#project-upgrade-workflow`.

6. **On decline, snooze** so the notice does not nag until a newer release:

   ```bash
   python3 "$CLAUDE_SKILL_DIR/scripts/version_check.py" snooze
   ```

## Notes

- Scope detection reads the running script's path: a tool dir directly in `$HOME` is a
  user install; otherwise it is a project (`.agents/` is the shared agents target).
- The version compared is the latest **published GitHub release tag**, not `main`.
- This never changes a project's `sdlc-studio/` artifacts directly; to migrate a project to the
  new conventions use `project upgrade` (`reference-upgrade.md#project-upgrade-workflow`), which
  skill-update offers after a bump.

## See Also

| Document | Relationship |
| --- | --- |
| `scripts/version_check.py` | the deterministic check / snooze / scope |
| `reference-upgrade.md` | project schema migration (the other `upgrade`) |
| `docs/INSTALL.md` | the installer reference |
