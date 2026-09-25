# US0946: The known-issues page names the release being cut

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py, changelog.d/US0946.md, tools/tests/test_lean_release_notes.py, tools/tests/test_pre_push_hook.py
> **Epic:** EP0265
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer publishing v6's disclosure
**I want** `known_issues.py write --release 6.0.0` to state the bar v6.0 is held to and to triage the open Mediums to v6.1
**So that** the v6 page does not tell readers its findings were triaged to v5.1 under v5.1's bar

## Acceptance Criteria

- **AC1:** Given a fixture corpus with one open Medium, when `known_issues.py write --release 6.0.0` runs, then the page carries `## The bar v6.0 is held to`, says the Mediums are `triaged to v6.1`, and holds no `triaged to v5.1`. Fails on: HEAD's literals at tools/`known_issues.py`:72, 89 and 104
  - **Verify:** pytest tools/tests/test_known_issues.py::ReleaseNamedTests::test_the_page_names_the_release_cut
  - **Verified:** yes (2026-09-25)
- **AC2:** Given the page written for 6.0.0, then v5.0.0's bar section is still present as history. Fails on: templating the heading by deleting the history prose
  - **Verify:** pytest tools/tests/test_known_issues.py::ReleaseNamedTests::test_the_v5_history_survives
  - **Verified:** yes (2026-09-25)
- **AC3:** Given the page just written for 6.0.0, when `known_issues.py check` runs against the same corpus, then it exits 0. Fails on: a `check` that re-renders with no release and so disagrees with the page it was asked to judge
  - **Verify:** pytest tools/tests/test_known_issues.py::ReleaseNamedTests::test_check_round_trips_the_written_release
  - **Verified:** yes (2026-09-25)

## Notes

Repo-only tool. `check` must read the release from the page's own heading (or `write` records it in the page) so AC3 round-trips without a hand-kept pin. The v6.0 bar sentence is the one ruled in TRIAGE: zero open Critical or High at the tag, every open Medium ruled by one triage decision.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (N7) |
