# BG0993: The open sprint run lives in one machine's gitignored .local/run-state.json: another checkout can open a second run beside it, and cannot sign it

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_shows_the_page.py, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/BG0993.md
> **Evidence:** homelab 2026-10-08: RPT0002 (RUN-01M4BZZ9) committed and unsigned; studypc2 .local/run-state.json = RUN-01M4B5HP (sealed); StudyPC = RUN-01KYJXE7; RUN-01M4BZZ9's state not on either
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T08:50:26Z

## Summary

BG0989's class, for run state. `sprint plan` refuses while a run is open ('a project holds exactly one run at a time'), and `sprint sign` seals the open run - but both read `sdlc-studio/.local/run-state.json`, which is gitignored, so 'open' is a per-machine fact. Observed in the homelab consuming project on 2026-10-08: RUN-01M4BZZ9 was planned, built and closed on one workstation (RPT0002 committed, awaiting signature). On a second machine, after `git pull`, run-state.json still names the previous, SEALED run (RUN-01M4B5HP) - so on that machine (a) `sprint plan` would NOT refuse, opening a second concurrent run whose batch could re-select RUN-01M4BZZ9's seven carried units, and (b) `sprint sign --report RPT0002` cannot seal RPT0002, because the run it belongs to is not in this checkout's state. Nothing in the committed tree says a run is open: the report is committed, the run record (`reports/runs/RUN-*.json`) is written only at sign. The agent had already told the operator to run the sign command on the wrong machine before finding this.

## Steps to Reproduce

1. Machine A: sprint plan / build / close -> RPTxxxx committed, run left open for signature
2. Machine B: git pull; read sdlc-studio/.local/run-state.json -> names an older, sealed run
3. Machine B: sprint plan --write -> not refused (no open run known here)
4. Machine B: sprint sign --report RPTxxxx -> the report's run is not this checkout's run

## Proposed Fix

Commit the run's open/closed marker with the report: when `close` files RPTxxxx, write `reports/runs/RUN-xxx.json` (status: awaiting-signature, report, fingerprint) and commit it; `plan` refuses while ANY committed run record is unsigned, naming it and the machine-independent remedy; `sign` can seal from any checkout that has the committed record (the signature needs only the report fingerprint and the batch, both committed). Test: a run closed in one tree, signed from a fresh clone; a plan in a fresh clone refused while the first is unsigned.

## Acceptance Criteria

- [ ] **AC1** When `sprint close` files a report, a committed run record names the run as awaiting signature, with its report and fingerprint, so a fresh clone sees that a run is open
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py -k close_commits_an_awaiting_signature_record
  - **Verified:** yes (2026-10-08)
- [ ] **AC2** `sprint plan --write` in a checkout whose local state names no open run still refuses while a committed run record awaits signature, naming the run, its report and the sign command
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py -k plan_refused_by_an_unsigned_committed_run
  - **Verified:** yes (2026-10-08)
- [ ] **AC3** `sprint sign --report <id>` seals the run from a fresh clone that holds the committed record but not the closing machine's `.local/` state
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py -k sign_from_a_fresh_clone
  - **Verified:** yes (2026-10-08)
- [ ] **AC4** Once signed, the run's committed record no longer blocks a plan anywhere
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py -k signed_record_does_not_block
  - **Verified:** yes (2026-10-08)

## Triage

- Confirmed at 978083c6 by the code path: the open run is `sdlc-studio/.local/run-state.json` (lib/run_state.py:51) and the run archive is `sdlc-studio/.local/run-archive/` (:60), both gitignored; the only committed run record is `reports/runs/RUN-*.json`, written when the run is signed. So whether a run is open is a per-machine fact, and on another machine `plan` does not refuse and `sign` cannot find the run. Not a regression.
- BG0989's class (LL0029: a record kept in a gitignored working directory is not a record), for run state. Related to CR-0610 (make the report of record reviewable without `.local/`), which moves the report's sources to committed files; this bug is the operational half, the open-run marker.
- Affects paths corrected to repository paths; `lib/run_state.py` added, since the one-run guard lives there. Points stay 5 as filed; refinement may find 8 (three commands change).
- Until fixed: sign a run on the machine that closed it, and do not plan on another machine while a committed report is unsigned.

## Fix

- `sprint close` files the run's record, still running, at `sdlc-studio/reports/runs/<RUN-ID>.json` after it stamps the tree, so the record carries `close_tree`, `report` and `report_fingerprint`.
- `sprint plan --write` refuses, before any selection, while a tracked record names a report and is still running for a run this checkout does not hold open. A run held open here whose tracked record is signed is taken up as sealed first (`run_state.adopt_tracked`), so the closing machine is not blocked after a signature elsewhere.
- `sprint sign` takes the awaiting record up as the live state when this checkout does not hold the run the close filed. An older closed run held here is archived; a different open run is never discarded (refused).
- `tree_digest` drops `reports/runs/` from its index, so a clone at the close's commit matches `close_tree` without the tree object, which only the closing machine holds. `tree_moved_since_close` ignores paths under it, so a run closed before this change (its `close_tree` holds the records) still signs.
- `run_state.close_run` refreshes a tracked record that is still running, so a run ended without a signature (`stop`) stops awaiting one.
- Not covered: between a `reopen` and the next close, the tracked record still reads sealed, so another clone is not refused a plan in that window.
- Tests: `test_run_open_across_checkouts.py`, 7 tests through `sprint.main` across real clones; 10 mutants, each killed.
- Two existing tests changed with the behaviour, each because the close now commits the record: `test_lean_tracked_run_record`'s re-seal test counts the signatures in the record's history rather than the commits that touched it, and `test_lean_report_integrity`'s archived-run fixture seals as `sign` does (the tracked record as well as the archive) instead of the archive alone.

## Repair after review round 1 (REJECT)

Each blocking finding, ruled:

- `test_lean_close_shows_the_page` red at 3bc1620e: CLOSED. The test now expects the run record the close files under `reports/runs/`, and names it. The full suite is run before this repair is committed.
- A plan after a reopen in the same checkout discarded the reopen: CLOSED. One predicate, `run_state.sealed_elsewhere`, decides every take-up: the record is sealed and signed, and this checkout's copy is the same run, still open, with no more reopens than the record and no differing signature of its own. A run signed here and reopened here fails it, so the plan gives the base refusal and keeps the reopen.
- A sign after reopening an unsigned run sealed the broken page and wiped the reopen: CLOSED. `sign` never takes up the run this checkout holds, and it takes a record up only after every check has passed, so a refused sign writes nothing.
- A re-close after a signature elsewhere stripped it: CLOSED. `close` and `sign` in the closing checkout take a signature made elsewhere up (sealed), so the close refuses instead of filing a second page, and `_file_awaiting_record` never files over a signed record unless the run was reopened after it.
- The docs claimed the named refusal in every clone: CLOSED by narrowing. The help and the fragment say the clone that does not hold the run open gets the named refusal, and the closing checkout the one-run refusal; a test pins the latter.
- Non-blocking, also done: an unreadable record refusing the plan, `--report` choosing between two awaiting runs, and the fingerprint equal to the filed page's are each pinned; `stop` names the record to commit; the `file_tracked` docstring is corrected. Not done, carried to BG1001: a clone that never held the run can end it only by signing it.
- Tests: 15 in `test_run_open_across_checkouts.py`. Eighteen mutants: seventeen killed. The survivor is equivalent: removing `sign`'s early refusal of a different open run leaves `adopt_tracked` to refuse the same case, with the same names and nothing written.

## Repair after review round 2 (REJECT, third round authorised in D0352)

Round 2 ruled findings 1, 2, 3 and 5 CLOSED and finding 4 MOVED into two sequences; each is answered:

- A reopen made before a signature elsewhere was pulled let the re-close file an unsigned record over the signed one: CLOSED. The close never strips a signature. A sealed, signed record this copy has not reopened past is left as it is, and any other signed record is filed over with its signature carried forward, since only `sign` writes one. The sequence is pinned: the record keeps the signature, the run awaits the re-closed page's signature in every clone, and the signed page reads INVALIDATED (overtaken by the reopen, as after any reopen), never INVALID.
- A re-signature made elsewhere after a local reopen was never taken up: CLOSED. `run_state.sealed_elsewhere` drops the own-signature clause; equal reopen counts decide. The sequence is pinned: the closing checkout's plan takes the re-seal up, no third page is filed, and the re-signed page checks VALID.
- The follow-up claimed in the round-1 repair is now filed as BG1001.
- Tests: 17 in `test_run_open_across_checkouts.py`. 21 mutants, 20 killed; the survivor is the equivalent one named in round 2.

## Review round 3 (REJECT, D0352) - kept here because the ledger refuses a round past the cap

`critic.py record` refused this verdict ("BG0993 has 2 review round(s) recorded, at the cap of 2"), though D0352 authorised the round; the gap is filed as BG1003. The verdict, verbatim:

> VERDICT: REJECT
> ISSUES: [new] The close files a stale copy over a newer awaiting record (sprint.py:8783-8788). Sequence: A closes and commits. Fresh clone B signs RPT0001, commits, reopens, re-closes (RPT0002, record reopened=1) and commits. A pulls while it still holds its unsigned running copy (reopened=0). A's plan returns rc 2 "already open", and A's sign returns rc 2 "6 file(s) changed since the close ... Re-run the close". A's re-close then returns rc 0 and files its copy over B's record: report RPT0002, B's signature carried forward, reopened back to 0. B's reopen is gone from the committed record. A fresh clone C then signs RPT0002 (rc 0), and `sprint_report check --report RPT0002` reads INVALID ("the tracked run record in 1c9d46e9b8 signs RPT0002 at eb5a196b0ebb9ab4, but the version committed with the signature in 28d01c7ac7 signs RPT0001 ..."), because no reopen now lies between the two signatures. Cause: the branch compares reopen counts only against a sealed record. A running record that records more reopens than this copy, and so is newer, is filed over. Fix: never file over a record of the same run that records more reopens than the live copy. Refuse the close and name the record (or take it up), and pin this sequence. Unreachable at base e77cd2d5, where no clone but the closer could sign; [new] low: the outcome condition at sprint.py:8783 (`existing.get("outcome") in run_state.CLOSED`) has no test, yet it matters. Replacing it with `True` passes all 17 tests. Run alone on the race sequence plus a second re-close after a fix, that mutant leaves the record stale (its close_tree no longer equals the live one). A fresh clone's sign of RPT0002 is then refused "(the tree the close recorded ... cannot be read)", and the run stays open in every clone. Pin a repeated re-close over a carried signature; [new] Review record, not a defect. Round-2 findings ruled. The race (a reopen made before pulling a signature) is CLOSED: re-probed, the record keeps B's signature, RPT0001 reads INVALIDATED with no "never removed", and clones are refused while RPT0002 awaits its signature. The author's judgement on INVALIDATED holds: a same-checkout sign, reopen and re-close gives INVALIDATED at base e77cd2d5 and at be92626b alike. Once the re-closed page is signed, RPT0001 reads INVALID "signed on RPT0002, not RPT0001" at base too, so that verdict is existing design. The re-signature not taken up is CLOSED: A's plan returns rc 0 and takes the re-seal up, no third page is filed, and RPT0002 checks VALID. Both killing tests fail against 82257e07's code, so they are not vacuous. BG1001 is filed, so the round-2 low is CLOSED. Every earlier probe re-run at be92626b holds: plan after a reopen returns rc 2 with the reopen kept, sign after a reopen returns rc 2 with the state untouched (refused variant included), a re-close after a pulled signature returns rc 2 with RPT0001 VALID, a stale sign answers "already sealed", and a realistic record signed from a fresh clone checks VALID in a further clean clone. Mutants: 29, of which 26 were killed. The three survivors are adopt_tracked's open-run refusal and sealed_elsewhere's running check (both equivalent, as in round 2) and the outcome condition (the low above). Every mutant ran in an extracted copy and the worktree stayed byte-identical. Selected suite at be92626b: 1443 passed, 1 failed (the timing test below). Claims: "a close never strips a signature, only sign writes one" TRUE (race probe). "a sealed, signed record that checkout has not reopened past is left as it is" TRUE. The sealed_elsewhere docstring TRUE. "7141 tests, OK" and "21 mutants, 20 killed" UNVERIFIABLE (not listed). The help's "any other signed record keeps its signature when the close files over it" is TRUE, and it is also the path by which a stale copy overwrites a newer record (the first finding); [pre-existing] test_status.py::GatherPerformanceTests::test_the_shipped_command_answers_a_corpus_shaped_fixture_with_the_headline_first fails on timing under load at base e77cd2d5 as well - not this unit
> BLOCKING: [new] a stale closing checkout's re-close files its older copy over a newer awaiting record from another clone, which erases that clone's reopen, and the next legitimate signature of the re-closed page reads INVALID (sprint.py:8783-8788) - never file over a record of the same run that records more reopens than the live copy, refuse or take it up instead, and pin the sequence

## Repair after review round 3 (REJECT, fourth round authorised in D0353)

- A stale closing checkout's re-close filed its older copy over a newer awaiting record: CLOSED. One predicate, `run_state.supersedes`, says when a record of the run this checkout holds is newer than its copy: it records more reopens, or it is sealed and signed with no fewer (`sealed_elsewhere`). `plan`, `sign` and `close` take a newer record up instead of filing over it; the close then refuses, naming what happened and the next command (`sign --report <the re-closed page>`). `_file_awaiting_record` also never files over a record with more reopens. The sequence is pinned through to the stale checkout signing the re-closed page, which checks VALID in a clean clone.
- The untested outcome condition: CLOSED. A repeated re-close over a carried signature is pinned: the second re-close refreshes the record's tree, and a fresh clone signs the page.
- Tests: 20 in `test_run_open_across_checkouts.py`. 24 mutants, 23 killed; the survivor is the equivalent one named in rounds 2 and 3.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Filed |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: confirmed by the code path; tool-derived criteria replaced with four executable ones; Affects corrected; CR-0610 related; workaround recorded |
| 2026-10-08 | Claude Opus 5.5 (engineering seat) | Fixed in the working tree (D0351 fast-track); Affects narrowed to the files changed: sprint_report.py and its tests were not needed, test_lean_tracked_run_record.py and help/sprint.md were |
| 2026-10-08 | Claude Opus 5.5 (engineering seat) | Repaired after QA round 1 REJECT: every blocking finding ruled CLOSED; Affects gains test_lean_close_shows_the_page.py |
| 2026-10-08 | Claude Opus 5.5 (engineering seat) | Repaired after QA round 2 REJECT under D0352: both moved sequences closed and pinned; BG1001 filed |
| 2026-10-08 | Claude Opus 5.5 (engineering seat) | Round 3 REJECT kept verbatim (the ledger refused it past the cap, BG1003); repaired under D0353 |
