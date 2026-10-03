# US0983: The v6.1 release notes lead with what changed for the person using it

> **Status:** In Progress
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/release-notes-v6.1.0.md, tools/tests/test_lean_release_notes_v61.py, changelog.d/US0983.md
> **Epic:** EP0273
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer on 6.0.0 deciding whether to take 6.1 (Maya)
**I want** release notes that open with what changed for me, list every change that will break a 6.0 habit with its replacement, and give the 6.0 upgrade path
**So that** I learn about a retired command from the notes, not from being refused by it

## Acceptance Criteria

- **AC1:** Given docs/release-notes-v6.1.0.md, then it opens with a one-sentence headline naming 6.1.0 as the current release; its first section leads with what changed for the person using it under five themes (a run ends with its signed report; the report states what it measured; a plain install is the latest verified release; `migrate` tells you more of what it leaves you; fewer hand moves at the close); it links the CHANGELOG section holding 6.1's entries (`[Unreleased]` before the cut, `[6.1.0]` after it) and docs/existing-users.md; it names no unit id outside its known-issues and sources passages; and every sentence or table row holding a figure names its source (an RPT id, `gate_timing.py`, the CHANGELOG). Fails on: the 6.0.0 notes copied with the version changed (headline '6.0.0 is the current release', themes 'one plan, one review, one signature'); notes composed from the 102 fragments, which are id-laden; a figure with no source, such as '29 of 34 units read NOT MEASURED'; the `#unreleased` link left in place after the cut has moved 6.1's entries under `[6.1.0]`
  - **Verify:** pytest tools/tests/test_lean_release_notes_v61.py::ReleaseNotesTests::test_the_notes_lead_with_what_changed_for_you
- **AC2:** Given the notes' 'Breaking changes' section, then it names each change a 6.0 user meets by being refused or surprised, each beside its replacement: `handoff.py generate` and `artifact.py new --type handoff` (the signed report, and `sprint.py plan --worklist RPTxxxx`); `gate.py --require-handoff` (the signed report from `sprint.py sign`); the `review.policy` key (removed by `migrate --apply`; a unit is carried at the review cap); a plain install no longer tracking `main` (`--version main`); Copilot CLI's global target moving to `~/.agents/skills`; the release gate's `revert-check` lane gone (the per-unit `verify_ac.py revert-check` stays); and `validate.py check` exiting 1 where there is no `sdlc-studio/` workspace. Fails on: a section copied from the two fragments filed under Breaking alone, which names the handoff writers and `review.policy` but not the install default or the Copilot target, so a 6.0 user finds those by surprise; a retired surface listed with no replacement
  - **Verify:** pytest tools/tests/test_lean_release_notes_v61.py::ReleaseNotesTests::test_every_breaking_change_names_its_replacement
- **AC3:** Given the notes' 'Upgrading from 6.0' section, then it says to reinstall (a plain install now fetches the latest verified release), then gives `migrate` before `migrate --apply` as commands, says what each leaves to the reader (the dry run writes nothing; `--apply` removes `review.policy` and, with BG0929 shipped, names the retired handoff commands where the reader's markdown docs use them in code, while it does not search CI yaml or scripts), says the HO files already written stay readable, and links docs/existing-users.md. Fails on: notes telling a 6.0 project that a reinstall is all it needs, while `migrate --apply` removes `review.policy` from its config; the two steps in the wrong order; a path that implies `migrate` finds `gate.py --require-handoff` in a project's CI, which it does not
  - **Verify:** pytest tools/tests/test_lean_release_notes_v61.py::ReleaseNotesTests::test_the_60_upgrade_path_is_given
- **AC4:** Given the notes, then `tools/check_links.py` and `tools/lint-style.sh` pass and the notes carry exactly one `**v6.1.0 discloses N open defects: N Medium, N Low.**` line for `known_issues.py write --release 6.1.0` to fill. Fails on: a broken CHANGELOG anchor, an em dash, or a missing count line, which makes the cut refuse (`_cut` requires exactly one)
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && test "$(grep -cE '^\*\*v6\.1\.0 discloses [0-9]+ open defects: [0-9]+ Medium, [0-9]+ Low\.\*\*$' docs/release-notes-v6.1.0.md)" = 1

## Notes

- Measured 2026-10-03 at 6589fbf0: 102 fragments in `changelog.d/`, 2 under Breaking (BG0831, US0978), 2 under Removed (BG0861, US0784), 12 under Changed, 86 under Fixed, none under Added. The Breaking list in AC2 is wider than the two Breaking fragments on purpose: US0968 (install default off `main`), BG0852/BG0855 (Copilot global target), US0784 (release lane) and US0969 (`validate.py check` exit 1) each change what a 6.0 user's command or script sees, though they were filed as Changed, Removed or Fixed.
- Measured: `migrate` on a 6.0-shaped fixture with `review: policy:` set reports `review.policy removed` (deterministic); a project file naming `handoff.py generate` and `gate.py --require-handoff` is not reported, because `handoff.py` carries no `RETIRED_VERBS` entry and no CHANGELOG `#### Retired flags` table names `--require-handoff`. BG0929 (this sprint) registers the retired handoff surface, so after it migrate names those commands in a project's markdown docs; CI yaml and scripts are not scanned, and AC3 states that limit.
- Name the mutant first (best-practices/testing.md): each test's docstring names the 6.0.0 notes with the version changed, or a fragment-composed draft, as the control it must refuse, as `test_lean_release_notes_v6.py` does. Reuse that module's `sections`, `_blank` and `units` helpers by import rather than copying them.
- The notes are written before the cut, so AC1's link check reads the CHANGELOG's layout at the time, as the v6.0 test did with `pre_cut`. US0985 re-points the link at the cut.
- Figures available: RPT0012-RPT0016 (the runs since 6.0.0); the push-gate median from `gate_timing.py estimate --suite boundary-push`. A figure is optional; an unsourced one is refused.
- Built before US0985 (the cut fills the count line and README links these notes); independent of US0984, so the two can build in parallel. AC1 and AC3 link the upgrade page itself, not an anchor US0984 has yet to write.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-03 | engineering seat (grooming) | Groomed for EP0273 under D0325: user story, four criteria with Verify lines, Affects and notes from the 102 fragments |
| 2026-10-03 | engineering seat | AC3 and its note re-groomed for BG0929 (QA seat, goal-review round 87) |
