# US1294: A shipped command adds a delegation disclosure line to a signed report, and the report check still reads it VALID

> **Status:** Done
> **Depends on:** US1233, US1333, US1338
> **Risk-class:** elevated
> **Delivers:** CR0730
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, docs/evidence.md, .claude/skills/sdlc-studio/scripts/tests/test_delegation_disclosure.py, changelog.d/US1294.md, sdlc-studio/reviews/command-audit.md
> **Epic:** EP0367
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who takes each release's evidence to the change board (Abena)
**I want** a shipped command that adds a delegation disclosure to a report already signed, and
the evidence pack and the evidence page to state it
**So that** a signature entered on the principal's behalf before `sprint sign --delegated`
existed says so on every record a board reads, without re-signing and without editing a sealed
page by hand

## Context

### Background

Since US1292, `sprint sign --delegated --decision Dnnnn` writes `delegated: true` and the
decision into the signature block of the report and the run record at the seal, the report's
Signed by cell says the signature was entered under delegation (`sprint_report.signed_by`), and
the evidence pack's Accountable line says the same. Reports signed under delegation before that
(RPT0030 to RPT0034, D0504) carry nothing, and no command can add it now. D0504 rules that those
signatures stand and gain a disclosure; US1295 applies this command to them.

---

## Acceptance Criteria

### AC1: the command discloses a delegation and the report still checks VALID

- **Given** a throwaway project with a report filed, signed through `sprint.py`'s signature writer and committed with its tracked run record, which `sprint_report.py check` reads VALID, and a decisions log holding an accepted D0001
- **When** `sprint_report.py disclose --report RPT0001 --decision D0001` runs
- **Then** the report's JSON signature block carries `delegated: true` and `decision: D0001`, its Markdown twin's Signed by cell reads that the signature was entered under delegation, authorised by decision D0001, the fingerprint and the tracked run record are byte-identical to before, and `sprint_report.py check` reads VALID before and after the change is committed. Fails on: HEAD, where `sprint_report.py disclose` exits 2 with `invalid choice: 'disclose'`; a disclosure that rewrites the run record's signature, which HEAD's check reads INVALID ("no reopen is recorded between them"); or one that leaves the twin as it was, which HEAD's check reads INVALID (the twin's wording differs from its JSON)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegation_disclosure.py::DelegationDisclosureTests::test_a_disclosure_leaves_the_signed_report_valid
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint_report.py disclose`, which US1295 runs over RPT0030 to RPT0034; `sprint_report.py check` reads the result

### AC2: a disclosure is refused for an unsigned report, an unaccepted decision or a delegation already recorded

- **Given** an unsigned report; a signed report beside a decisions log in which the named decision is absent, and one in which it is superseded; and a report signed with `--delegated --decision D0002`
- **When** the command runs on each, the last naming D0001
- **Then** each run exits non-zero naming why, and the report's JSON, its twin and the reports index are byte-identical to before. Fails on: HEAD, which has no such command; a disclosure written onto a page nobody signed, one citing a decision the log does not show as accepted, or one replacing the decision a signature was sealed with
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegation_disclosure.py::DelegationDisclosureTests::test_a_disclosure_is_refused_for_an_unsigned_report_or_an_unaccepted_decision
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint_report.py disclose`

### AC3: repeating a disclosure changes no byte

- **Given** a signed report the command has already disclosed under D0001
- **When** the command runs again with D0001
- **Then** it exits 0 saying nothing changed, no byte of the report, its twin or the index moves, the twin carries the statement once, and the report still reads VALID. Fails on: HEAD, which has no such command; a second statement for the same decision, or a re-run that rewrites the page
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegation_disclosure.py::DelegationDisclosureTests::test_repeating_a_disclosure_writes_it_once
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint_report.py disclose`, re-run by US1295's builder after an interrupted pass

### AC4: the evidence pack states a disclosed delegation

- **Given** two committed signed reports, RPT0001 disclosed by the command under D0001 and RPT0002 signed by its principal, with D0001 accepted in the committed decisions log
- **When** `release_cut.py evidence-pack --version 1.0.0 --reports RPT0001,RPT0002` runs
- **Then** the pack is written, each change from RPT0001 says on its Accountable line that the signature on its report was entered under delegation, authorised by decision D0001, each change from RPT0002 says its principal signed it, and the delegation refusals `test_evidence_pack_build.py` holds for US1292 still pass. Fails on: HEAD, where the pack refuses a report-side delegation the run record does not hold ("the report's signature and its run record ... disagree on delegation"), and refuses one written into the run record too ("the signature was rewritten after it was sealed")
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegation_disclosure.py::DelegationDisclosureTests::test_the_evidence_pack_states_a_disclosed_delegation
- **Verified:** yes (2026-11-27)
- **Caller:** `release_cut.py evidence-pack`, which US1295 runs to rebuild the 6.4.0 pack

### AC5: the evidence page names each delegated signature

- **Given** three signed reports: one signed with `--delegated --decision D0001`, one disclosed by the command under D0002 and one signed by its principal
- **When** `sprint_report.py evidence --out docs/evidence.md` writes the page
- **Then** its table carries a column, after the existing ones, giving each run's signer as the report's Signed by cell gives it, so the two delegated rows name the delegation and their decisions and the third names the principal alone, and its legend names the field the column reads; and this repository's `docs/evidence.md` is regenerated in the same commit, so `evidence --check` exits 0. Fails on: HEAD, whose seven columns (Run, Report, Goal verdict, Verdict note, Dollars per point, Model, Hours to signature) name no signer, and whose `docs/evidence.md` says nothing of delegation (`grep -ci delegat` prints 0) though RPT0035 to RPT0045 were signed under D0528, D0535, D0539 and D0545
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegation_disclosure.py::DelegationDisclosureTests::test_the_evidence_page_names_each_delegated_signature
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint_report.py evidence`, and `release_cut.py tag-check`, which refuses a tag over an evidence page that differs from what the signed reports render

---

## Scope

### In Scope

- `sprint_report.py disclose --report RPTxxxx --decision Dnnnn`
- The evidence pack accepting a disclosed delegation, and its module docstring saying so
- A signer column on the evidence page, and `docs/evidence.md` regenerated
- `help/sprint.md` and `reference-scripts-domain.md` naming the route; `reference-scripts-surface.md` regenerated

### Out of Scope

- Applying it to RPT0030 to RPT0034 and rebuilding the 6.4.0 pack (US1295)
- Any change to `sprint sign` or to the signatures already sealed
- A disclosure on the tracked run record

---

## Technical Notes

- Grounded at HEAD af477fc6d on 2026-11-26, on a full clone of this repository under `$HOME/.cache/sdlc-tmp/run28-recheck/` (removed after), over RPT0034:
  - `delegated` and `decision` added to the report's signature through `sprint_report.write_report`, which re-renders the twin: the fingerprint is unchanged, one twin line changes (the Signed by cell), and `check` reads VALID uncommitted and committed. RPT0030 to RPT0033 done the same way each changed one twin line, and RPT0030 and RPT0033 checked VALID.
  - The same keys added to the JSON without re-rendering the twin: `check` reads INVALID, naming the twin's Signed by wording.
  - The same keys also written into the tracked run record's signature and committed: `check` reads INVALID ("the tracked run record ... signs RPT0034 at 2c27b3912b625cf6, but the version committed with the signature in e356db805d signs RPT0034 at 2c27b3912b625cf6, and no reopen is recorded between them").
  - `evidence_pack.build_pack` for 6.4.0 over RPT0028 to RPT0034 refused both: report only, "disagree on delegation: the report names a delegation under decision D0493, the run record no delegation"; run record too, "holds a signature that differs on decision, delegated from the one sealed at e356db805d0a ... the signature was rewritten after it was sealed". So the pack must change: accept a delegation the report holds and the run record does not when its decision is accepted in the decisions log committed at the revision built, and keep refusing a report that drops or changes a delegation the run record holds (US1292).
- So the command writes the report and its twin only, through `write_report`, and never the run record. No step needs the operator's signature: the sealed signature, its fingerprint and the run record stand (D0504), and nothing re-signs.
- `write_report` re-appends the report's row at the end of `sdlc-studio/reports/_index.md` (the probe moved RPT0034's row): the command keeps the row where it is.
- The accepted-decision check is the one `sprint._delegation` applies (`decisions.list_decisions`, status `accepted`); share it rather than copy it.
- `sprint_report.NON_CEREMONY_VERBS["sprint_report"]` gains `disclose`, or `cycle_drift()` reports it uncovered (`test_sprint_report.py`).
- Append the column: `_page_rows`, `cmd_evidence --check` and `release_cut._row_reports` read Run and Report as the first two cells. `test_evidence_page.py` reads cells by column name. Regenerate `docs/evidence.md` with `sprint_report.py evidence --out docs/evidence.md`; `tools/tests/test_evidence_page_committed.py` runs its `--check`.
- `reference-scripts-surface.md` is generated by `docgen.py surface`. `help/sprint.md` names the route beside the `--delegated --decision` paragraph.
- Run twenty-eight: `sprint_report.py` is edited in turn by US1334, US1338, this story, US1234 and US1235; `help/sprint.md` by US1333 first; `reference-scripts-domain.md` by US1233 first; `reference-scripts-surface.md` by this story, then US1234; `docs/evidence.md` by this story, then US1295.
- New test module carries `# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py`.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| The report names no tracked run record | Disclosed on the report alone, as for any signed page; the check reads as before |
| The decision id is written in another spelling (`d0001`, `1`) | Normalised to `D0001` as `decisions._norm_did` does, then checked; a value that is no id is refused |
| The report is signed by its principal and already disclosed under another decision | Refused, naming the decision it holds (AC2) |
| The report was filed under an older schema | Disclosed; `check` names the schema as before, and the disclosure changes nothing it reads |
| An interrupted write | `write_report` stages both files before replacing either, so the report and twin stay a pair |

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| US1338 | Sequencing | The last unit before this one on `sprint_report.py` | Ready |
| US1333 | Sequencing | Edits `help/sprint.md` first | Ready |
| US1233 | Sequencing | Edits `reference-scripts-domain.md` first | Draft |
| US1295 | Downstream | Runs this command over RPT0030 to RPT0034 | Draft |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Re-grounded against HEAD for run twenty-eight (D0638) |
| 2026-11-26 | orchestrator | Affects names sdlc-studio/reviews/command-audit.md (and, for US1333, `test_artifact.py`), the registry the plan says a new flag implies |
