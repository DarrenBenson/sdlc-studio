# US0942: The release tag is refused only for what a release needs, not for close-owed debt

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_tag_no_close_owed.py, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, sdlc-studio/stories/US0166-ship-a-stop-hook-installer-and-redefine-sprint.md, sdlc-studio/tsd.md, changelog.d/US0942.md, .claude/skills/sdlc-studio/scripts/hooks/close_guard.py, sdlc-studio/bugs/BG0311-close-owed-push-release-guard-is-enforced-at.md, sdlc-studio/bugs/BG0668-tag-check-refuses-on-a-close-the-close.md, sdlc-studio/stories/US0165-gate-grows-an-auto-detecting-close-owed-lane.md, sdlc-studio/stories/US0226-rewrite-us0166-ac3-as-a-two-file-shell.md
> **Epic:** EP0265
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer cutting a release
**I want** `release_cut.py tag-check` to ask only whether the gate was green on the tagged commit and CI passed on the forge, and `gate.py --require-close` to be retired
**So that** the v6 tag is not refused by 17 units the close-owed detector cannot account for (carried units such as US0909 via BG0767, and units closed by rulings such as D0265 and D0267), when `sprint sign` already seals every run

## Acceptance Criteria

- **AC1:** Given a fixture where the gate is recorded green on the tagged commit, forge CI is green and three delivery units are terminal with no retro naming them, when `release_cut.py tag-check --commit <sha>` runs, then it allows the tag. Fails on: HEAD, which refuses naming the three units (`close_owed.py detect` exits 1 on 17 units in this repository at 013a46d0)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tag_no_close_owed.py::TagNoCloseOwedTests::test_uncovered_units_do_not_refuse_the_tag
- **AC2:** Given the same fixture with the gate recorded green on a different commit, then `tag-check` still refuses and names both commits. Fails on: deleting the whole tag guard rather than its close-owed half
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tag_no_close_owed.py::TagNoCloseOwedTests::test_a_green_on_another_commit_still_refuses
- **AC3:** Given `gate.py --require-close`, then it exits 2 with a message that the flag is retired and that `sprint sign` seals each run. Fails on: removing the flag so argparse exits with a usage error that names nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tag_no_close_owed.py::TagNoCloseOwedTests::test_require_close_is_retired
- **AC4:** Given a fixture with an owed unit, when `status.py hint` runs, then it still prints the close-owed advisory. Fails on: deleting `close_owed.py` with the bindings, which N2 does not ask for (the advisory and `hooks/close_guard.py` stay)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tag_no_close_owed.py::TagNoCloseOwedTests::test_the_status_advisory_stays
- **AC5:** Given US0166 AC3, whose shell verifier greps help/gate.md and reference-retro.md for `require-close`, then it is retired in the D0259 pattern and `test_verify_ac.py`'s US0166 pins are updated, and `docgen.py surface --check` reports 0 drift. Fails on: removing the doc lines while US0166 AC3 stays `Verified: yes` over text that no longer exists
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tag_no_close_owed.py::TagNoCloseOwedTests::test_no_stamp_names_the_retired_flag

## Notes

Release-blocking: without it the v6 tag-check refuses. Retires TagRefusesAnOwedCloseTests and TagCheckReadsTheBlockingPredicateTests in test_release_cut.py and the RequireClose tests in test_gate.py (about test_gate.py:2021 and 2104-2140); record each retired criterion in the D0259 pattern. Closes BG0688 (gate._close_owed), BG0689 and BG0694 (tag-check's reader) as Superseded by this unit. BG0739 is NOT closed: close_owed's stamp reader still feeds the status advisory, so it stays open as an advisory-only Medium on the known-issues page (re-ruled in TRIAGE). Ratchet (LC-008): deletes a blocking lane and a tag refusal; the retired constraint is 'every terminal unit must be named in a retro Batch before a tag', which D0265's closures and carry bugs cannot meet. Add `--require-close` to gate.py's retired-flag handling beside the other v6 retirements so the release notes' breaking-change inventory picks it up.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (N2) |
