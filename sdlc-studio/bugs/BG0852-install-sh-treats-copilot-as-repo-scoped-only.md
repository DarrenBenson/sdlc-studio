# BG0852: install.sh treats Copilot as repo-scoped only, so a Copilot CLI user following the quick start or --target auto gets no sdlc-studio and no hint why

> **Status:** Fixed
> **Override ruling:** D0288
> **Closed with findings in:** BG0856 (approved round 2, RUN-01M3RPSK)
> **Forced-override:** 2026-09-30: --force waived 1 gate(s) on Fixed - BG0852 carries an unanswered delivery REJECT (qa-seat reviewer (subagent a37dc96c)'s REJECT of 2026-09-30; qa-seat reviewer (subagent a37dc96c)'s REJECT of 2026-09-30): 15 finding(s) outstanding - undetected\_hint prints 'not installed for' a tool whose folder the same run's sweep refreshed, and names Codex on a copilot-only host once ~/.agents exists (install.sh:215-231) [LC-006]; a --local default install prints 'Detected ... Copilot CLI' from a .github folder or gh alone, with no Copilot CLI present (install.sh:164 feeding the hint) [LC-006]; declared behaviour 3 untested: printing the hint for an explicit --target survives all 28 install tests (install.sh:665); declared behaviour 1 untested: gh/.github counting on a global install survives all 28 (install.sh:164) [LC-002] .... A REJECT has two exits: a round-2 APPROVE from the reviewer who rejected, or carrying the unit at the review cap: that reviewer's round-2 REJECT, recorded in the open run, files the findings as a bug and drops the unit from the batch, so the run closes without it. A carried unit is still refused Done: it is delivered again in a later run and reaches Done on an APPROVE from the reviewer who rejected it (the same reviewer id). A ruling in a retro's `Known issues carried` table does not discharge it, and a `--force` waiver is recorded in the artefact's `Forced-override` field
> **Severity:** High
> **Points:** 5
> **Affects:** install.sh,README.md,docs/INSTALL.md,tools/tests/test_install_copilot_global.py,tools/tests/test_install_sweep.py,tools/tests/test_install_atomic.py, changelog.d/BG0852.md
> **Evidence:** Field report 2026-09-29 (Copilot CLI 1.0.89); `copilot skill --help` on this host (1.0.71); install.sh target_dir `copilot:global) echo ""`, resolve_targets auto skip, is_detected copilot/agents; README.md install table
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T15:37:25Z

## Summary

Field report (upgrading a v5.0.1 project to v6.0.0 under GitHub Copilot CLI 1.0.89 on WSL2; reproduced on this host's Copilot CLI 1.0.71): `copilot skill --help` lists personal skill folders `~/.copilot/skills/` and `~/.agents/skills/`, but install.sh maps `copilot:global` to empty ('repo-scoped only'), `--target auto` skips copilot on a global install on purpose, `is_detected copilot` looks for `gh` or `.github` rather than the `copilot` binary, and `is_detected agents` does not look for `copilot` either. On a host with only Copilot CLI, the default install (claude only) and `--target auto` both leave Copilot with nothing, and the installer prints no hint that a supported tool went uninstalled; `copilot skill list` shows only its built-ins. `sweep_stale` walks `target_dir` per target, so with `copilot:global` empty it never visits `~/.copilot/skills` and a copy placed there by hand stays stale silently. README and docs/INSTALL.md state Copilot is repo-scoped (README table row `Copilot | (repo-scoped)`), although the README's own `agents` row says Copilot reads `~/.agents/skills`. install.ps1 carries the same mapping and detection. Workaround: `--target claude,agents`.

## Steps to Reproduce

On a host with `copilot` on PATH and no `~/.agents`, `codex`, `cursor` or `gh`: run `bash install.sh --target auto --dry-run`; no target writes to `~/.agents/skills` or `~/.copilot/skills`, and no line names Copilot. Then `copilot skill list` shows no sdlc-studio.

## Proposed Fix

Map `copilot:global` to `~/.agents/skills` (the folder Copilot shares with `agents`, so one copy serves both) in install.sh; let `--target auto` select it on a global install; add `command -v copilot` to the copilot and agents detections; include `~/.copilot/skills` in the sweep so a hand-placed copy is refreshed or named; when the default claude-only install detects Copilot CLI (or another supported tool) it did not install for, print one line naming the `--target` that would; correct the README and docs/INSTALL.md rows. `tools/tests/test_install_atomic.py::test_global_auto_excludes_copilot` (CR0208) asserts the opposite of AC1; its intent - a global install must never write `.github/skills` into the current directory - is kept by AC5, and the test is rewritten to it. install.ps1 carries the same mapping but cannot be exercised on a host without pwsh, so its parity is a separate unit (see Revision History).

## Acceptance Criteria

- [ ] **AC1** Given a HOME with only a `copilot` executable on a curated PATH (no gh, codex, cursor, ~/.agents), when `install.sh --target auto --dry-run` runs globally, then it plans an install into a personal folder Copilot CLI reads (`~/.agents/skills` or `~/.copilot/skills`). Fails on: today's auto, which skips copilot globally and detects agents only by ~/.agents, codex or cursor
  - **Verify:** pytest tools/tests/test_install_copilot_global.py::CopilotGlobalTests::test_auto_selects_a_copilot_personal_folder
  - **Verified:** yes (2026-09-30)
- [ ] **AC2** Given the same host and the default target (claude only), when install.sh runs, then its output names Copilot CLI as detected-but-not-installed and the `--target` that would install for it. Fails on: silence
  - **Verify:** pytest tools/tests/test_install_copilot_global.py::CopilotGlobalTests::test_default_install_hints_an_undetected_copilot
  - **Verified:** yes (2026-09-30)
- [ ] **AC3** Given a stale sdlc-studio copy under `~/.copilot/skills`, when install.sh runs with the sweep on, then the copy is refreshed or named in the output. Fails on: a sweep that never visits ~/.copilot/skills
  - **Verify:** pytest tools/tests/test_install_sweep.py::SweepTests::test_sweep_visits_copilot_personal_folder
  - **Verified:** yes (2026-09-30)
- [ ] **AC4** README.md and docs/INSTALL.md no longer describe Copilot as repo-scoped only, and name the personal folder the installer uses. Fails on: the `(repo-scoped)` row surviving
  - **Verify:** pytest tools/tests/test_install_copilot_global.py::CopilotGlobalTests::test_docs_do_not_call_copilot_repo_scoped
  - **Verified:** yes (2026-09-30)
- [ ] **AC5** Given a global `install.sh --target auto` run from inside a directory holding a `.github` folder, then nothing is written under that directory's `.github/skills`, and copilot's global target is the personal folder. Fails on: a fix that re-enables copilot on a global auto by pointing it at `.github/skills` in the current directory (the side effect CR0208 removed)
  - **Verify:** pytest tools/tests/test_install_atomic.py::ResolveTargetsAuto::test_global_auto_never_writes_github_skills_in_cwd
  - **Verified:** yes (2026-09-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Regroomed after goal-review round 78 (product, engineering and QA seats): points 3 to 5; install.ps1 dropped from Affects (no pwsh on the build host, parity filed separately); test_install_atomic.py added, since its CR0208 test asserts the opposite of AC1; AC5 keeps CR0208's intent. |
| 2026-09-30 | transition set --force | forced BG0852 -> Fixed, waiving 1 gate(s): BG0852 carries an unanswered delivery REJECT (qa-seat reviewer (subagent a37dc96c)'s REJECT of 2026-09-30; qa-seat reviewer (subagent a37dc96c)'s REJECT of 2026-09-30): 15 finding(s) outstanding - undetected\_hint prints 'not installed for' a tool whose folder the same run's sweep refreshed, and names Codex on a copilot-only host once ~/.agents exists (install.sh:215-231) [LC-006]; a --local default install prints 'Detected ... Copilot CLI' from a .github folder or gh alone, with no Copilot CLI present (install.sh:164 feeding the hint) [LC-006]; declared behaviour 3 untested: printing the hint for an explicit --target survives all 28 install tests (install.sh:665); declared behaviour 1 untested: gh/.github counting on a global install survives all 28 (install.sh:164) [LC-002] .... A REJECT has two exits: a round-2 APPROVE from the reviewer who rejected, or carrying the unit at the review cap: that reviewer's round-2 REJECT, recorded in the open run, files the findings as a bug and drops the unit from the batch, so the run closes without it. A carried unit is still refused Done: it is delivered again in a later run and reaches Done on an APPROVE from the reviewer who rejected it (the same reviewer id). A ruling in a retro's `Known issues carried` table does not discharge it, and a `--force` waiver is recorded in the artefact's `Forced-override` field |
