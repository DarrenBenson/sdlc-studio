# Help: skill-update

<!-- Load when: /sdlc-studio skill-update - updating the installed skill to the latest release -->

Update the **installed SDLC Studio skill** to the latest published release, on confirm.

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Is there a new version of SDLC Studio?" | `/sdlc-studio skill-update` |
| "Update the skill to the latest release" | `/sdlc-studio skill-update` |
| "Stop telling me about updates for now" | decline `/sdlc-studio skill-update` (snoozes the notice) |
| "What version am I on, and is it the newest?" | `/sdlc-studio skill-update` |

## Commands

```bash
/sdlc-studio skill-update          # check, show installed -> latest, confirm, install, reload
```

`skill-update` updates the **installed skill itself**. It is distinct from `/sdlc-studio upgrade`
(a project's artifact schema, v1 -> v2) and `/sdlc-studio project upgrade` (a project's conventions).
All three are named side by side in `reference-upgrade.md#three-upgrades`.

## What it does

1. Checks the installed version against the latest GitHub release (`version_check.py`).
2. If newer, shows `installed -> latest` and the detected scope (user / project / agents).
3. On your explicit confirm, runs the installer for that scope (sweeps every tool's copy).
4. Tells you to reload to activate; on decline, snoozes until a newer release.

## The startup notice

On the first `/sdlc-studio status` or `hint` of a session, the skill prints a one-line
notice when a newer release exists:

```text
SDLC Studio 2.2.0 is available (installed 2.1.0) - run /sdlc-studio skill-update, ...
```

It is on by default, silent offline, and checks at most once per `version_check.ttl_hours`
(default 24). Turn it off with `version_check.enabled: false` in
`sdlc-studio/.config.yaml`. Declining `skill-update` keeps it quiet until a newer release.

## See also

- `reference-skill-update.md` - the workflow
- `reference-upgrade.md#three-upgrades` - the three "upgrade" surfaces named side by side
- `scripts/version_check.py` - `check` / `snooze` / `scope`
