<!-- close-status:begin -->
> **RUN-01M78TKD closed running.** 24 unit(s) in the batch. **The run signature is OWED and is the operator's** - `sprint sign` seals the batch in one signature.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

Closed on 2026-11-13 over RPT0030 (fingerprint 82ced251b004932d) and awaiting the operator's
signature: run ten's authorisation to sign (D0467) covered that run only.

> **RUN-01M78TKD, run eleven.** Goal: "Lanes land and die cleanly, verifiers never read green
> wrongly, and every unit's cost is priced." A declared maintenance run (D0469, D0470, D0471):
> 24 bugs, 49 points, all delivered on independent APPROVEs, four of them after one repair round.
> Goal judged partial: every lane was multi-unit, and a multi-unit lane's builder cannot yet be
> priced per unit (BG1397); BG1420 was carried. Machinery share by theme 36 points (73%), declared.
> Cost 41.4M priced tokens, 845k per point, $111.66 ($2.28 per point) against run ten's 791k and
> $2.22.

## What landed

- **Lanes** land without hand repair and die with their caller: verify_ac's artefact edit no
  longer blocks a land (BG1336), a lane is replayed onto main before its commit (BG1337), a
  rejoinder verdict is accepted (BG1339), a home-isolated unit is briefed for the main checkout
  (BG1344), a timed-out lane gets SIGTERM first and a lane dies with `sprint.py` (BG1262, BG1261).
- **Verification** no longer reads green wrongly or leaks: a partial skip is not stamped
  (BG1005), the revert check reads an unmeasurable criterion honestly (BG1009), a later
  section's Verify line is not attached (BG0991), and a caller's signal reaches its verifiers
  (BG1190, BG1228, BG1112).
- **Cost**: a re-close after a reopen re-reads the meter (BG1279), a landed lane is priced from
  its builder's transcript and an unpriced unit is a close gap (BG1330), Grok's long-context
  rates are recorded and a session-total figure is labelled a lower bound (BG1331), and the
  Cursor meter keeps each line's model (BG1305).
- **Integrity and upgrade**: BG1340, BG1341, BG0990, BG1343, BG1333 (AGENTS.md's trunk rule),
  BG1371, BG0965, and the five Dependabot alerts cleared by upgrading markdownlint-cli (BG1372).

## What is owed

- **The signature**: `sprint.py sign --report RPT0030 --principal "<the operator>"`.
- **BG1420 (High) carried as BG1425**: it fixed the five tests the push gate found red, but its
  repair's round-2 review found a new unbounded wait (a caller whose SIGTERM handler waits for its
  pool hangs). It is unruled on RPT0030; ruling it is the signer's call.
- **Known issues carried, all not-stop-ship** (RETRO0144): BG1382-BG1417 and BG1421-BG1425, every
  finding filed as its own bug, closely related test gaps merged; BG1418 and BG1419 were filed twice
  and are superseded.
- **Main is not yet pushed**: the push gate refused b7ead759 (the five tests, fixed by BG1420),
  92c84b10 (a census timing test, fixed) and 1caffe6d (RETRO0144's missing velocity row, which the
  close has now written). Push the close paperwork and read the gate.
- **Run twelve**: EP0275, CR0694 and US0999 (moved by D0469), with BG1425 and the Medium findings.

## Learned the hard way

- Run the full suite after each wave, not at the run's first push: five red tests reached main
  that no lane's selected run had selected (BG1420).
- On this eight-core host, four builders at once is the ceiling; six drove the load to 18 and
  commit hooks to 857 s. Put every temporary file under ~/.cache/sdlc-tmp: /tmp is a small tmpfs.
- Record a carried unit's re-review under the reviewer id that rejected it (BG1400).
