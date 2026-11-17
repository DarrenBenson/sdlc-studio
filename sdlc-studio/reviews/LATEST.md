<!-- close-status:begin -->
> **RUN-01M7HA6R closed goal-reached.** 10 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

Signed on 2026-11-16 over RPT0034 (fingerprint 2c27b3912b625cf6), sealed goal-reached. The
operator authorised the orchestrator to sign each run it closed and open the next (D0479,
renewed under D0493); the orchestrator entered `sprint sign --principal "Darren Benson"` on that
authorisation. The operator then asked for the release itself (D0500).

**v6.4.0 is released (2026-11-16).** The tag is on f5317b26 (BG1506's acceptance), tagged by Darren
Benson; GitHub published the tar.gz and zip with their sha256 files, and a pinned install with
`SDLC_STUDIO_REQUIRE_CHECKSUM=1` verified and matched the tagged tree. The release boundary
refused the tag push twice on its module-alone lane alone (BG1514); the operator approved one
`git push --no-verify` for the tag (D0501). sdlc-studio.com serves 6.4.0 (web RUN-01M7JM21
SIGNED over RPT0007).

> **RUN-01M7HA6R, run fifteen.** Goal: "A head of engineering upgrades to 6.4 from notes, pages
> and specs that match the code, nothing High open." 10 units, 34 points (27 planned, and BG1501,
> BG1498 and BG1503 added in-run under D0497 to D0499), all delivered on independent APPROVEs.
> Cost 25.9M priced tokens, 761k per point, $70.65 ($2.08 per point) against run fourteen's
> 794k and $2.18. Runs twelve to fifteen, the D0474 plan for 6.4, delivered 196 points.

## What landed

- **The release epic** (EP0314): the v6.4 release notes (US1170), the help, reference and public
  pages (US1171), the PRD, TRD and TSD (US1172) and the cut of v6.4.0 (US1173).
- **CHANGELOG**: `changelog.py compose` starts every fragment on its own bullet, and the 6.4.0
  section was re-cut so each of its 133 entries stands alone (BG1503).
- **Push gate matches CI**: the push gate runs the green-run noise gate CI's Lint runs (BG1493)
  and holds a full run to the recorded total only, as CI does (BG1498); the 6.4 notes test runs
  its text checks outside a git clone (BG1501).
- **Before the tag** (D0500): docs/evidence.md regenerated with RPT0033 and RPT0034,
  docs/known-issues.md rewritten for 6.4.0 (369 open defects: 65 Medium, 304 Low, nothing High),
  the 6.4.0 evidence pack written from RPT0028 to RPT0034, and `sdlc-studio/.version` restamped.

## What is owed

- **Carried, not stop-ship** (RETRO0148): BG1495 to BG1497, BG1499, BG1500, BG1502, BG1504 and
  BG1505, and CR0713 (the LC-019 graduation).
- **Deferred out of 6.4**: CR0673, CR0710 (the effort trial) and US1168 (needs a regroom).
- **After the tag**: BG1507 (High: reviewer agents rewrote the operator's global git identity
  through XDG_CONFIG_HOME; restored by hand, backup beside it), BG1514 (the module-alone flake
  that refused the tag push), BG1508, BG1510 to BG1513, and BG1301 (the .version restamp, its
  fourth recurrence; BG1509 closed as its duplicate).
- **The audit** (AUDIT-2026-11-17, project profile, after the tag): 68 survivors of 76 candidates,
  filed as BG1516 to BG1566, CR0714 to CR0728, RFC0065 and RFC0066, with BG1567 and BG1568 for
  two frictions met filing them. Twelve are High, among them gates that pass work they never
  judged (BG1519, BG1521, BG1522, BG1524). D0502 plans runs sixteen to twenty to deliver them,
  about 225 points. RFC0065 and RFC0066 are ruled (D0503 to D0505): a run closed while the
  operator is away waits for signature, and PyYAML is required.
- **The backlog is broken down and groomed** (D0506 to D0514): every Proposed CR is refined
  into stories (EP0315 to EP0368) and every Draft story and Open bug passed the readiness
  report on 2026-11-17. Only the audit's units are placed in runs (D0502); the older CRs'
  stories are groomed but unplaced.
- **Competitor review** (RFC0067, D0515 to D0518): CR0732 to CR0738, broken down into
  EP0369 to EP0375 and US1300 to US1312 (35 points), groomed and unplaced.
- **Headroom**: the green-run noise total sits at 104 of 104, so one more leaked line reddens
  both CI and the push.

## Learned the hard way

- A finding filed after the cut leaves docs/known-issues.md behind the corpus until it is written
  again: write it after the last filing and before the tag.
- A failing git is not proof the tree is no clone: BG1501's first fix skipped every check on that
  one signal (LC-006).
- A builder that cleans up with a glob over a shared directory deletes what other lanes made
  (BG1504): remove only the paths you created.
- Redirecting HOME does not isolate git: with XDG_CONFIG_HOME exported, `git config --global` in
  a throwaway HOME writes the real ~/.config/git/config (BG1507). Pass identity with `-c`.
- A lane that passes alone on the same host can still be red in the gate's full lane sequence:
  reproduce with the lanes that ran before it, not the module alone (BG1514).
