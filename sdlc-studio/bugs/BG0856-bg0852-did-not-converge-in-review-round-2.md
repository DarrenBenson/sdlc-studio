# BG0856: BG0852 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** install.sh,docs/INSTALL.md,tools/tests/test_install_copilot_global.py,changelog.d/BG0852.md,changelog.d/BG0856.md
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T09:16:11Z

## Summary

BG0852 was rejected at round 2, the review cap, by qa-seat reviewer (subagent a37dc96c), so it was carried as a known issue rather than reviewed again. The findings still open: [new] round-1 blocking finding 1 MOVED to a sibling folder: undetected\_hint checks for a copy only in each tool's install target (install.sh:235), never the other folders the tool reads, so with the copilot binary and a stale copy in ~/.copilot/skills the default run prints 'refreshed: ~/.copilot/skills/sdlc-studio' then 'Detected but not installed for: Copilot CLI', and following the hint installs a duplicate copy - the same shape hits opencode (~/.claude/skills) and Gemini CLI (~/.agents/skills) per docs/INSTALL.md:82-83 [LC-002] [LC-006]; [new] changelog.d/BG0852.md and docs/INSTALL.md:67 claim the hint names only tools whose folder holds no copy, false for the three repros; [pre-existing] --local --target copilot writing .github/skills is untested (M14 survives), same at 04325bdd; [pre-existing] --list-targets prints full HOME paths under bash 5.3, same at base; [pre-existing] BG0855 covers install.ps1

## Steps to Reproduce

On c00784d1, with a HOME holding the `copilot` binary on PATH and a stale sdlc-studio copy in `~/.copilot/skills`, run the default `bash install.sh`: it prints `refreshed: ~/.copilot/skills/sdlc-studio (1.0.0 -> 2.0.0)` and then `Detected but not installed for: Copilot CLI. To add: --target claude,copilot`. Following the hint installs a second copy in `~/.agents/skills`, so Copilot CLI loads the skill twice. The same shape: an `opencode` stub with the default install (which writes `~/.claude/skills`, a folder opencode reads) hints opencode; a `gemini` stub with a copy in `~/.agents/skills` hints Gemini CLI.

## Proposed Fix

In install.sh, count a copy in ANY folder a tool reads as served, not only the tool's install target: derive the per-tool read folders from one table in install.sh (the same facts docs/INSTALL.md:82-83 documents), and have `undetected_hint` consult it. Correct the claims in changelog.d/BG0852.md and docs/INSTALL.md:67 so they say exactly that. Delivering this closes BG0852.

## Acceptance Criteria

- [ ] **AC1** Given a HOME with the `copilot` binary on a curated PATH and an sdlc-studio copy only in `~/.copilot/skills`, when the default `install.sh` runs, then no line names Copilot CLI as detected but not installed. Fails on: c00784d1's hint, which checks only the install target `~/.agents/skills`
  - **Verify:** pytest tools/tests/test_install_copilot_global.py::CopilotGlobalTests::test_no_hint_when_a_folder_the_tool_reads_holds_a_copy
  - **Verified:** yes (2026-09-30)
- [ ] **AC2** Given an `opencode` stub alone (the default install writes `~/.claude/skills`, which opencode reads), and separately a `gemini` stub with a copy in `~/.agents/skills`, when the default `install.sh` runs, then neither opencode nor Gemini CLI is hinted. Fails on: a fix that special-cases `~/.copilot/skills` rather than reading one per-tool folder table
  - **Verify:** pytest tools/tests/test_install_copilot_global.py::CopilotGlobalTests::test_no_hint_for_a_tool_served_by_a_shared_folder
  - **Verified:** yes (2026-09-30)
- [ ] **AC3** Given a HOME with the `copilot` binary and no sdlc-studio copy in any folder Copilot CLI reads, when the default `install.sh` runs, then the hint still names Copilot CLI and `--target claude,copilot`. Fails on: a fix that silences the hint whenever any copy exists anywhere
  - **Verify:** pytest tools/tests/test_install_copilot_global.py::CopilotGlobalTests::test_hint_still_names_a_tool_with_no_copy_in_any_folder_it_reads
  - **Verified:** yes (2026-09-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Groomed into RUN-01M3RPSK on the operator's ruling (the carry answered by a groomed unit, not a third round): repro from the round-2 REJECT, three criteria with Verify lines, points 5 to 2, Affects narrowed to the hint. |
