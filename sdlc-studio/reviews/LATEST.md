<!-- close-status:begin -->
> **RUN-01M7E52T closed running.** 24 unit(s) in the batch. **The run signature is OWED and is the operator's** - `sprint sign` seals the batch in one signature.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

Signed on 2026-11-14 over RPT0030 (fingerprint 82ced251b004932d), sealed partial. Asked at the
close, the operator answered "Authorise you to sign", so the orchestrator entered `sprint sign
--principal "Darren Benson"` on that authorisation, for this run only (D0472).

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

- **BG1420 (High) carried as BG1425**: it fixed the five tests the push gate found red, but its
  repair's round-2 review found a new unbounded wait (a caller whose SIGTERM handler waits for its
  pool hangs). The operator ruled it not stop-ship at the signature (D0472); run twelve.
- **Known issues carried, all not-stop-ship** (RETRO0144): BG1382-BG1417 and BG1421-BG1425, every
  finding filed as its own bug, closely related test gaps merged; BG1418 and BG1419 were filed twice
  and are superseded.
- **Pushed**: e7d1a5c9 passed the push gate's full suite and GitHub's Lint run. The gate had
  refused three earlier pushes, at b7ead759, 92c84b10 and 1caffe6d: five red tests (BG1420), a
  census timing test, and RETRO0144 committed before the close wrote its velocity row.
- **Run twelve**: set by D0474 after the backlog triage below.

## Since the run: backlog triage and the 6.4 plan (2026-11-14)

- **Triage (D0473)**: all 483 open items got a verdict at HEAD; eleven closed as already done
  or duplicated, criteria carried to each survivor; a deep re-check of 20 sampled keeps found
  none already fixed.
- **Rulings (D0474)**: seven items closed as not beneficial or not real; RFC0062, RFC0063 and
  RFC0064 Accepted (forced past BG1020's refusal); US0999 built in 6.4; CR0702 filed for the
  front door.
- **6.4, four runs, about 160 points**: twelve, evidence and honest cost (BG1425 and BG1420's
  re-review clear the tag's bar; EP0275, US0999, CR0696, CR0692's first part, CR0694, the cost
  bugs, BG1268, BG1019); thirteen, EP0287's 40-point slice and CR0693; fourteen, CR0702, six
  consumer-visible bugs and three cost levers; fifteen, the release. Groom each run at its start.

## Learned the hard way

- Run the full suite after each wave, not at the run's first push: five red tests reached main
  that no lane's selected run had selected (BG1420).
- On this eight-core host, four builders at once is the ceiling; six drove the load to 18 and
  commit hooks to 857 s. Put every temporary file under ~/.cache/sdlc-tmp: /tmp is a small tmpfs.
- Record a carried unit's re-review under the reviewer id that rejected it (BG1400).
