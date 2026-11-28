# EP0379: v6.5.0 ships with paperwork that matches the code

> **Status:** Done
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The 6.5.0 release paperwork: the release notes and the document updates for what 6.5 ships, then
the cut. 6.5 is the release the operator held to a stricter bar (D0560): fewer than 50 open defects
and none at Medium or above. Open bugs fell from 473 (99 Medium) after run twenty to 46, all Low, at
RPT0045's sign, by re-checking every open bug at HEAD (D0563), fixing most of the rest, and the
operator's two approved Won't Fix lists (139 under D0564, 128 under D0613). Beside that drive, 6.5
ships: every persona and seat card held to a written standard (EP0285, EP0287); a sprint that walks
a wave from build to paperwork and wakes the model only at a stop, with the author's own mutants
replayed to the reviewer (EP0326, EP0327); a delegated signature that names the decision that
authorised it, and a run awaiting its signature that no longer holds up the next (EP0366); PyYAML
required, so a gate a project switched on is never read as off (EP0368); a written policy for a red
CI run on main (EP0340); harness-agnostic public pages (EP0377); and a duplicate-finding refusal and
the plan's test advisories (EP0378). Modelled on EP0314 (v6.4.0). The tag, the evidence pack, the
publish and the site stay with the operator (D0545's exclusions).

### Story order and wave plan

| Wave | Story | Points | Depends on |
| --- | --- | --- | --- |
| 1 | US1327: The v6.5 release notes lead with what changed for the person answering for the release | 5 | none |
| 1 | US1328: The help, upgrade and public pages describe what 6.5 ships | 5 | none |
| 1 | US1329: The PRD, TRD and TSD describe what 6.5 ships | 5 | none |
| 2 | US1331: v6.5.0 discloses what it ships with: the known-issues page under the operator's bar, and the evidence page through the last signed run | 3 | US1327 |
| 3 | US1330: v6.5.0 is cut: version, changelog, install pins and the specs' baseline | 5 | US1327, US1328, US1329, US1331 |

- **Wave one builds in parallel.** The three stories' Affects share no file: US1327 writes only
  `docs/release-notes-v6.5.0.md` and its own test; US1328 only help pages, README, llms.txt and two
  docs pages; US1329 only the three specs and `tools/tests/test_lean_trd_refresh.py`. Each writes
  its own `changelog.d/<ID>.md`.
- **The disclosure follows the notes.** US1331 writes the known-issues page, the notes' disclosure
  line and the evidence page; it shares `docs/release-notes-v6.5.0.md` with US1327, so it lands
  after it, and may build while US1328 and US1329 finish (D0631).
- **The cut goes last, alone.** It depends on all four, and it shares files with each:
  `docs/release-notes-v6.5.0.md` (US1327, US1331), `README.md` (US1328), `sdlc-studio/prd.md`,
  `trd.md`, `tsd.md` and `tools/tests/test_lean_trd_refresh.py` (US1329), and `changelog.d/`, which
  it empties, so every story's fragment is in the 6.5.0 section. It is the release commit.
- Total 23 points.

## Story Breakdown

- [x] [US1327: The v6.5 release notes lead with what changed for the person answering for the release](../stories/US1327-the-v6-5-release-notes-lead-with-what.md)
- [x] [US1328: The help, upgrade and public pages describe what 6.5 ships](../stories/US1328-the-help-upgrade-and-public-pages-describe-what.md)
- [x] [US1329: The PRD, TRD and TSD describe what 6.5 ships](../stories/US1329-the-prd-trd-and-tsd-describe-what-6.md)
- [x] [US1330: v6.5.0 is cut: version, changelog, install pins and the specs' baseline](../stories/US1330-v6-5-0-is-cut-version-changelog-known.md)
- [x] [US1331: v6.5.0 discloses what it ships with: the known-issues page under the operator's bar, and the evidence page through the last signed run](../stories/US1331-v6-5-0-discloses-what-it-ships-with.md)
- [x] [US1341: The v6.5 release notes describe the whole widened release, from the spend ceiling to the release record](../stories/US1341-the-v6-5-release-notes-describe-the-whole.md)
- [x] [US1342: The help and public pages tell a 6.4 team how to cap a run's spend, answer a cache-read fall and read a release's change failure rate](../stories/US1342-the-help-and-public-pages-tell-a-6.md)
- [x] [US1343: The PRD, TRD and TSD describe the widened 6.5 and no longer say a token figure never stops a run](../stories/US1343-the-prd-trd-and-tsd-describe-the-widened.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-25 | orchestrator (delegate under D0545) | Groomed for run twenty-seven from the product seat's draft, modelled on EP0314 |
| 2026-11-25 | orchestrator (delegate under D0631) | US1330 split at the 8-point ceiling: the disclosure is US1331 (3 points, wave 2), the cut US1330 (5 points, wave 3); still 23 points |
