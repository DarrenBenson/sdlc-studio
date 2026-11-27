# US1295: RPT0029 to RPT0034 and the 6.4.0 evidence pack name the decision behind each delegated signature

> **Status:** Ready
> **Depends on:** US1294
> **Risk-class:** standard
> **Delivers:** CR0730
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/reports/RPT0029.json, sdlc-studio/reports/RPT0029-sprint-report-run-01m77177.md, sdlc-studio/reports/RPT0030.json, sdlc-studio/reports/RPT0030-sprint-report-run-01m78tkd.md, sdlc-studio/reports/RPT0031.json, sdlc-studio/reports/RPT0031-sprint-report-run-01m7e52t.md, sdlc-studio/reports/RPT0032.json, sdlc-studio/reports/RPT0032-sprint-report-run-01m7eyr3.md, sdlc-studio/reports/RPT0033.json, sdlc-studio/reports/RPT0033-sprint-report-run-01m7gehm.md, sdlc-studio/reports/RPT0034.json, sdlc-studio/reports/RPT0034-sprint-report-run-01m7ha6r.md, sdlc-studio/reports/_index.md, sdlc-studio/reports/evidence-pack-6.4.0.md, docs/evidence.md, tools/tests/test_lean_delegated_reports_disclosed.py, changelog.d/US1295.md
> **Epic:** EP0367
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who takes the 6.4.0 evidence to the change board (Abena)
**I want** RPT0029 to RPT0034, the 6.4.0 evidence pack and the evidence page to say that those
six signatures were entered under delegation, each naming the decision that authorised it
**So that** the board does not read six delegated signatures as signatures the operator
entered

## Context

### Background

D0504: the signatures on RPT0030 to RPT0034 stand, and each report and the 6.4.0 evidence pack
gain a line naming the decision that authorised the delegated signature. US1294 ships the
command that adds it and the pack and page support; this story runs it over the six reports (RPT0029 too, D0640: D0504's list names D0467, which authorised it)
and regenerates the two records built from them. Nothing is re-signed.

| Report | Run | Seal commit | Decision |
| --- | --- | --- | --- |
| RPT0029 | RUN-01M77177 (run ten) | 8a199868b | D0467 (D0640) |
| RPT0030 | RUN-01M78TKD (run eleven) | f1b77e38e, "on the operator's authorisation" | D0472, which names RPT0030 |
| RPT0031 | RUN-01M7E52T (run twelve) | 1787393dd, "on the operator's flight authorisation" | D0475, run twelve only |
| RPT0032 | RUN-01M7EYR3 (run thirteen) | 45b97375b, "signed under D0479" | D0479 |
| RPT0033 | RUN-01M7GEHM (run fourteen) | 8fb4e7ebf, "D0479, renewed in D0493" | D0493, which names run fourteen's signature |
| RPT0034 | RUN-01M7HA6R (run fifteen) | e356db805, names no decision | D0493, the standing renewal ("sign off and start the next sprint when ready") |

---

## Acceptance Criteria

### AC1: each of the six reports names its decision and checks VALID

- **Given** the committed reports RPT0029 to RPT0034, after `sprint_report.py disclose` has run on each with the decision in the table above, and D0467, D0472, D0475, D0479 and D0493 accepted in `sdlc-studio/decisions.md`
- **When** each report's JSON and Markdown twin are read and `sprint_report.py check` runs on each
- **Then** each JSON signature block carries `delegated: true` and its decision from the table, each twin's Signed by cell says the signature was entered under delegation and names that decision, each report's fingerprint is the one its tracked run record signed, the six run records are unchanged, and each check prints VALID. Fails on: HEAD, where none of the six signature blocks carries `delegated` (RPT0035 is the first that does) and each twin's Signed by cell reads `Darren Benson` alone; a decision that does not cover that run; or a report the amendment left INVALID
- **Verify:** pytest tools/tests/test_lean_delegated_reports_disclosed.py::DelegatedReportsDisclosedTests::test_each_delegated_report_names_its_decision_and_checks_valid
- **Caller:** `sprint_report.py disclose` (US1294) writes the disclosure; `sprint_report.py check` and `sprint_report.py evidence` read it

### AC2: the 6.4.0 evidence pack and the evidence page name the delegated signatures

- **Given** `sdlc-studio/reports/evidence-pack-6.4.0.md` rewritten by `release_cut.py evidence-pack --version 6.4.0 --reports RPT0028,RPT0029,RPT0030,RPT0031,RPT0032,RPT0033,RPT0034` after the disclosures are committed, and `docs/evidence.md` rewritten by `sprint_report.py evidence --out docs/evidence.md`
- **When** the pack's Accountable lines and the page's rows are read, and `sprint_report.py evidence --out docs/evidence.md --check` runs
- **Then** every Accountable line of a change from RPT0029 to RPT0034 says the signature on its report was entered under delegation and names that report's decision, no Accountable line of a change from RPT0028 says so, the pack's header names the seven reports, the page's rows for RUN-01M78TKD, RUN-01M7E52T, RUN-01M7EYR3, RUN-01M7GEHM and RUN-01M7HA6R name the delegation and the same decisions, and `--check` exits 0. Fails on: HEAD, where none of the pack's 108 Accountable lines says "entered under delegation" and `docs/evidence.md` names no delegation (`grep -ci delegat` prints 0); a pack that shows the five signatures as entered by the operator; or a page edited by hand away from its generator
- **Verify:** pytest tools/tests/test_lean_delegated_reports_disclosed.py::DelegatedReportsDisclosedTests::test_the_evidence_pack_and_page_name_the_delegated_signatures
- **Caller:** `release_cut.py evidence-pack` and `sprint_report.py evidence`, which write the two records; `release_cut.py tag-check` judges the page at the 6.5.0 tag

---

## Scope

### In Scope

- Five runs of `sprint_report.py disclose`, one per report
- The 6.4.0 pack and `docs/evidence.md`, each rewritten by its own command
- One test module over the committed records

### Out of Scope

- RPT0035 onwards, which `sprint sign --delegated` already disclosed (RPT0029 joined the disclosure under D0640)
- Any re-signature, reopen or run-record change
- The command, the pack's acceptance rule and the page column (US1294)

---

## Technical Notes

- Grounded at HEAD af477fc6d on 2026-11-26. `sprint_report.py check` read each of RPT0030 to RPT0034 VALID at HEAD; on a full clone, the US1294 route (signature keys written through `write_report`) changed one twin line per report and RPT0030, RPT0033 and RPT0034 still checked VALID. Signature blocks: RPT0030 to RPT0034 hold principal, signed_at, report and fingerprint only; RPT0035 to RPT0045 carry `delegated` with D0528, D0535, D0539 or D0545.
- The decision for each report is read from its seal commit and the decision text (table above). D0504 and CR0730 list D0467, D0472, D0475, D0479 and D0493, but D0467 authorised run ten (RPT0029, seal commit 8a199868b), not run eleven.
- No step needs the operator's own signature: the disclosure is outside the fingerprint, the run records stay byte-identical and nothing re-signs. The one route that would need it, rewriting a run record's signature, reads INVALID and is not taken.
- Two commits: the pack reads records as committed (`git show <rev>:<path>`), so commit the six disclosures first, then write the pack and the page and commit them with the fragment.
- The rebuilt pack differs from the committed one beyond the delegation lines (since US1292 each Accountable line also names the fingerprint signed); that is the generator's own output. `tag-check` judges only the last cut version's pack, so after the 6.5.0 cut the 6.4.0 pack is not judged; `docs/evidence.md` is judged at the 6.5.0 tag.
- `check` timings at load 7 on this host: RPT0030 41 to 55 s, RPT0031 24 s, RPT0032 12 s, RPT0033 17 to 35 s, RPT0034 6 s. Run the six as concurrent subprocesses so AC1's node stays under 120 s. Read the pack and the page as files; do not rebuild the pack in the test, or any later edit to a unit it covers turns the test red.
- `write_report` re-appends a report's index row; US1294's command keeps it in place, so `_index.md` should not move.
- `docs/engineering-leaders.md` cites RPT0031 as a signed report; it stays true and needs no change.
- New test module carries `# test-census-subject: sdlc-studio/reports/evidence-pack-6.4.0.md`.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| A disclose run fails part-way through the six | Re-run: a disclosed report is left as it is (US1294 AC3) |
| The pack refuses a report | Nothing is written; fix the cause, never hand-edit the pack |
| A report is signed after the page is regenerated | `--check` notes it as newer, which does not fail (as at HEAD) |
| RPT0029, ruled in under D0640 | It takes its own `disclose` run, and AC1 and AC2 assert it like the other five, RUN-01M77177's page row included |

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| US1294 | Blocking | The `disclose` command, the pack's acceptance rule and the page column | Draft |
| US1330 | Downstream | The 6.5.0 cut and tag, after `docs/evidence.md` is regenerated here | Ready |

---

## Open Questions

- [x] RPT0029 (run ten) was signed by the orchestrator under D0467 and is in the 6.4.0 pack, but D0504 names RPT0030 to RPT0034. Disclose it too? - Yes, ruled by the delegate in D0640
- [ ] RPT0033: D0493 (which names run fourteen's signature) rather than D0479 (the flight, which had ended); RPT0034: D0493's standing renewal, since its seal commit names none. Confirm both. - Owner: operator

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Re-grounded against HEAD for run twenty-eight (D0638) |
| 2026-11-26 | orchestrator | RPT0029 joins the disclosure under D0640: Affects, the table, AC1 and AC2 name it |
| 2026-11-26 | sdlc-studio | Retitled: was 'RPT0030 to RPT0034 and the 6.4.0 evidence pack name the decision behind each delegated signature' |
| 2026-11-27 | orchestrator (D0545) | Out of Scope and Edge Cases now agree with D0640: RPT0029 is in, and AC1 and AC2 assert it (the approach panel found both lines stale) |
