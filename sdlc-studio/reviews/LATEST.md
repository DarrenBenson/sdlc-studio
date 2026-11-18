<!-- close-status:begin -->
> **RUN-01M7NTY5 closed running.** 17 unit(s) in the batch. **The run signature is OWED and is the operator's** - `sprint sign` seals the batch in one signature.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

**RUN-01M7NTY5, run sixteen, is closed and awaits the operator's signature (D0503).** The stamp
above says "closed running" because the record keeps that outcome until `sprint sign` seals it
(BG1589). Read RPT0035 (fingerprint a9daaca50ef063ce) and its page, then sign it with
`sprint.py sign --report RPT0035 --principal "<the operator>"`. The orchestrator did not sign.

> Goal: "No gate passes work it never judged, and a run closed in the operator's absence awaits
> a trustworthy signature." Judged **partial**: 17 units, 51 points (48 planned; BG1579 and
> BG1580 under D0525 and BG1586 under D0526 taken in-run to repair push reds), all delivered on
> independent APPROVEs and pushed green at 9925e144 (9,219 passed). Cost 37.3M priced tokens,
> 732k per point, $102.01 ($2.00 per point) against run fifteen's 761k and $2.08, and under the
> plan's forecast of 43.0M and $172.05 ($3.37 per point), even with five units needing a second
> review round and three push repairs. (This paragraph first quoted the forecast as the cost;
> corrected from RPT0035's Actual column.)

## For the operator at signature

- **BG1582 (Medium, High priority), deferred to you:** once HEAD has moved past the close
  commit with no later run open, `sprint sign` judges the run against that commit and skips the
  whole-tree check. This run is in that state: the commit after the close (LATEST.md and BG1589)
  means sign will judge RUN-01M7NTY5 against 59763d63, whose tree is the one the close recorded.
- **D0524:** how sign judges a waiting run once HEAD has moved on (against the commit that filed
  its record, report pair and run record byte-identical to it).
- **BG1578:** the scheduled corpus-verify run (43869298579) fails US0926 AC1 and US0996 AC3 in CI
  while both pass on the push gate; the push acknowledged it by its run id.

## What landed

- **Gates that judge what they pass:** a full-suite lane with no test run fails (BG1519); the
  commit gate no longer reuses another selection's green verdict (BG1522); the tag gate reads
  the release bar (BG1521); the push reads the weekly corpus-verify run (BG1518); the evidence
  pack checks the report fingerprint and run record (BG1524).
- **The deferred signature (D0503, CR0729 Complete):** a run can be planned while a closed one
  awaits signature and status names each waiting run (US1290); a delegated sign needs an accepted
  decision id, recorded in the signature (US1291) and shown on the report page and evidence pack
  (US1292); ADR-013 in the TRD and the sprint pages describe it (US1293).
- **Review seats:** lane accept records the seat (BG1520); the second seat states its interim
  behaviour on the single-sequence round ledger (BG1523).
- **Safety:** a test or agent that redirects HOME can no longer rewrite the operator's git
  identity through XDG_CONFIG_HOME (BG1507).
- **Risk map (D0520, CR0739 Complete):** reconcile raises a story stamped below its Affects' class
  (US1314); this repository's config classes the gate scripts high (US1313), raising 102 open
  stories' stamps.

## What is owed

- **The signature** on RUN-01M7NTY5.
- **Runs seventeen to twenty** are replanned after this run (D0519), from the swept backlog
  (D0521). Four sweep questions wait for the operator: BG1404, BG1103 (recommend keep open),
  BG1181 and BG1201.
- **Filed in the run, not taken:** BG1570 to BG1578, BG1581 to BG1585, BG1587 to BG1589, and
  CR0740 (the LC-021 graduation). RETRO0149 carries them not-stop-ship, BG1582 deferred.
- **Carried from run fifteen:** BG1495 to BG1497, BG1499, BG1500, BG1502, BG1504, BG1505,
  CR0713, CR0673, CR0710, US1168, and the after-tag bugs BG1508, BG1510 to BG1514 and BG1301.

## Learned the hard way

- A guard only the push runs finds a unit's regression after the unit is Done: three this run
  (BG1579, BG1580, BG1586). A lane that adds a test file or a spec row runs the census, boundary
  marker and docs tests before handing back (LC-019, BG1587).
- Builders leave out the changelog fragment unless the brief says it is part of the Affects, and
  no gate requires one (BG1574, LC-021).
- After a close that waits for signature, any change to the tree moves it away from the close's
  record: commit the close's paperwork exactly as the close left it, and put later edits in a
  commit on top (D0524).
- Redirecting HOME does not isolate git while XDG_CONFIG_HOME is exported: pass identity with
  `-c` (BG1507, now guarded).
