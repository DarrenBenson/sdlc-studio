# US0968: With no --version, install.sh installs the latest published release, verified against its .sha256

> **Status:** Done
> **Delivers:** CR0603
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** install.sh, README.md, docs/INSTALL.md, tools/tests/test_lean_install_latest_release.py, changelog.d/US0968.md
> **Epic:** EP0269
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the one-line quick-start install to fetch the latest published release and check it against its `.sha256`
**So that** the install most new users run is the verified one, and `main` is something I ask for

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0603 bullet 4 (bullets 1-3 rejected), 2 points. `install.sh` defaults `VERSION="$BRANCH"` (`main`, install.sh:106), and `main` publishes no `.sha256`, so the README quick start (README.md:53) installs unverified with a warning. A tagged version already prefers the release asset and verifies it (`verify_download`). The fix resolves the latest published release (GitHub's `releases/latest`, which skips pre-releases) when no `--version` is given and sends it down that existing tagged path; `--version main` keeps today's behaviour. If the lookup fails, the installer falls back to `main` with the warning it already prints, so an offline or rate-limited machine still installs: no new refusal. The README one-liner itself does not change (the script is still fetched from `main`); the text that says the default tracks `main` (README.md:82, docs/INSTALL.md:178) is rewritten. `install.ps1` is out of scope.

## Premise at HEAD

Executed at `85042135`:

```text
$ bash install.sh --dry-run
SDLC Studio Installer
==> Targets: claude
==> Scope: global
==> Version: main
exit=0
```

## Acceptance Criteria

- [ ] **AC1** Given a stub `curl` first on `PATH` that answers the GitHub latest-release query with `{"tag_name": "v9.9.9"}`, when `bash install.sh --dry-run` runs with no `--version`, then it prints `Version: v9.9.9`. Fails on: HEAD prints `Version: main` (install.sh:106)
  - **Verify:** pytest tools/tests/test_lean_install_latest_release.py::InstallLatestReleaseTests::test_no_version_resolves_the_latest_release
  - **Verified:** yes (2026-10-01)
- [ ] **AC2** Given the same stub, when `bash install.sh --dry-run --version main` runs, then it prints `Version: main` and the stub's request log holds no latest-release query. Fails on: a resolver that overrides an explicit `--version`
  - **Verify:** pytest tools/tests/test_lean_install_latest_release.py::InstallLatestReleaseTests::test_version_main_is_installed_only_when_asked
  - **Verified:** yes (2026-10-01)
- [ ] **AC3** Given a stub `curl` that fails the latest-release query, when `bash install.sh --dry-run` runs, then it exits 0, prints `Version: main` and one line saying the latest release could not be resolved. Fails on: a resolver that aborts the install when the lookup fails
  - **Verify:** pytest tools/tests/test_lean_install_latest_release.py::InstallLatestReleaseTests::test_an_unresolvable_latest_falls_back_to_main
  - **Verified:** yes (2026-10-01)
- [ ] **AC4** Given `README.md` and `docs/INSTALL.md`, when each is read, then neither says the default install tracks `main`. Fails on: HEAD README.md:82 and docs/INSTALL.md:178 ("The default install tracks `main`")
  - **Verify:** pytest tools/tests/test_lean_install_latest_release.py::InstallLatestReleaseTests::test_the_docs_no_longer_say_the_default_tracks_main
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
