# Help: skill-update

<!-- Load when: /sdlc-studio skill-update - updating the installed skill to the latest release -->

Update the **installed SDLC Studio skill** to the latest published release, on confirm.

## Commands

```bash
/sdlc-studio skill-update          # check, show installed -> latest, confirm, install, reload
```

Distinct from `/sdlc-studio upgrade` (which migrates a project's artifacts between
schema versions). `skill-update` updates the skill itself.

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
- `scripts/version_check.py` - `check` / `snooze` / `scope`
