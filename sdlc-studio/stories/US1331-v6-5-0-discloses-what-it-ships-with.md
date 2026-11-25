# US1331: v6.5.0 discloses what it ships with: the known-issues page under the operator's bar, and the evidence page through the last signed run

> **Status:** Ready
> **Depends on:** US1327
> **Release:** 6.5
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/known-issues.md, docs/release-notes-v6.5.0.md, docs/evidence.md, tools/known_issues.py, tools/tests/test_known_issues.py, tools/tests/test_lean_release_disclosure_v65.py, .githooks/pre-push, tools/tests/test_pre_push_hook.py, changelog.d/US1331.md
> **Epic:** EP0379
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who takes the release to the change board (Abena)
**I want** v6.5.0 to disclose what it ships with: a known-issues page that states the bar 6.5 was
held to and shows it met, the same count in the release notes, and an evidence page that lists
every signed run
**So that** the board is shown every defect the release ships with against the bar it was promised,
and can read each run's record without running the tool

## Acceptance Criteria

- **AC1:** Given `known_issues.py write --release 6.5.0` run for the release, then, judged at the release (the
  v6.5.0 tag once it exists, else the commit that last wrote docs/known-issues.md, else the working
  tree while that write is uncommitted), `known_issues.py check` exits 0, the page's heading names the v6.5 bar and states
  it as D0560 rules it (fewer than 50 open defects and none at Medium or above), which needs a 6.5
  entry in `tools/known_issues.py`'s `BARS` with the v6.0 bar kept as history, and the 6.5.0 notes
  carry exactly one filled `**v6.5.0 discloses N open defects: N Medium, N Low.**` line whose figures
  equal the page's. Fails on: the page at HEAD, cut for v6.4 with 369 findings (65 Medium);
  `known_issues.render(REPO, "6.5.0")` at HEAD, which heads "The bar v6.5 is held to" with v6.0's
  sentence, "Zero open Critical or High finding at the tag, and every open Medium ruled by one triage
  decision"; or a count line that disagrees with the page.
  - **Verify:** pytest tools/tests/test_lean_release_disclosure_v65.py::DisclosureTests::test_the_known_issues_page_is_cut_for_650
- **AC2:** Given the bug corpus at the release (judged as AC1 judges it), then `known_issues.py bar`
  judged there exits 0 (`bar --at v6.5.0` once the tag exists, the working tree before it), and the
  operator's bar holds there: the test counts the open findings in that commit's corpus and finds
  fewer than 50, and none at Medium, High or Critical. Fails on: the commit that last wrote
  docs/known-issues.md at HEAD (cd0e478ec, the 6.4.0 page), whose corpus holds 369 open findings, 65
  of them Medium; `bar --at v6.5.0` at HEAD, which exits 2 because no such tag exists; or a cut made
  while 50 or more findings, or any at Medium or above, are open.
  - **Verify:** pytest tools/tests/test_lean_release_disclosure_v65.py::DisclosureTests::test_the_release_bars_hold_at_the_cut
- **AC3:** Given docs/evidence.md, then it is regenerated with `sprint_report.py evidence --out
  docs/evidence.md` and lists every signed report through RPT0045 at least, and `--check` exits 0.
  Fails on: the page at HEAD, whose newest report is RPT0035 and on which `--check` notes RPT0036 to
  RPT0045 as not yet on the page.
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/sprint_report.py evidence --out docs/evidence.md --check && grep -q 'RPT0045' docs/evidence.md

## Notes

- Serves: Abena Osei, End goals 1 and 3 (quoted under US1327).
- Split from US1330 at grooming's 8 points (D0631); its criteria are US1330's AC2, AC3 and AC6 as
  groomed, with the test moved to this story's own module. It lands after US1327, whose notes
  page holds the disclosure line, and before the cut, US1330, so that `changelog-cut` composes this
  story's fragment into the 6.5.0 section.
- `tools/known_issues.py` and `tools/tests/test_known_issues.py` are in Affects for AC1's `BARS`
  entry. Without it the 6.5.0 page states the v6.0 bar under a v6.5 heading, which is weaker than
  the bar 6.5 was held to. The severities a bar refuses belong to that bar: the v6.5 entry bars
  Medium as well as Critical and High, so `bar`, `check` and the page's Not carried section judge a
  6.5 release by it, and an older tag keeps its own release's bar (the qa seat's round-one REJECT,
  which superseded grooming's note that `bar` stays Critical and High). AC2's count test holds the
  operator's ceiling of under 50. Existing `test_known_issues` cases render 5.1.1,
  6.0.0 and 6.1.0 and are unaffected by a (6, 5) entry; add one for 6.5.0.
- The page and the count are written before the cut and regenerated after the run's sign if
  anything is filed or signed later (as D0500 did for 6.4.0), so each test judges the page as the
  release holds it, never a count fixed in the test.
- The criteria must stay true after later releases, because `gate.py --release` executes every
  story's Verify at each cut: AC1 and AC2 judge the release as AC1 states, and AC3 reads 'RPT0045
  at least'.
- Run `tools/run-suite.sh all` on the gate host before review. A file outside Affects that needs a
  change is a finding to report, not an edit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-25 | orchestrator (delegate under D0631) | Groomed from US1330's AC2, AC3 and AC6, split off at the 8-point ceiling US0854::AC1 refuses: user story, criteria with Verify lines in this story's own test module, Depends on US1327, Release 6.5 |
| 2026-11-25 | orchestrator (delegate under D0545) | Notes: the barred severities follow each release's bar, per the qa seat's round-one REJECT, replacing grooming's note that `bar` stays Critical and High |
| 2026-11-25 | orchestrator (delegate under D0545) | Affects take .githooks/pre-push and tools/tests/test_pre_push_hook.py for round three: the hook's refusal still names only Critical and High once the v6.5 bar refuses a Medium (the qa seat's round-two REJECT, carried as BG1760) |
