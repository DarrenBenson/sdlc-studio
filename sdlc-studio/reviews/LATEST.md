<!-- close-status:begin -->
> **RUN-01M3CK1K closed goal-reached.** 37 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M3HR74, Sprint 6 of the v6 release: v6.0.0 is ready to cut.** Goal: "v6.0.0 ships:
> Maya and Jonah install, upgrade and learn it from docs and notes that match the code." 55 of 55
> batch units delivered, each by one independent QA-seat reviewer under the two-round cap. BG0818
> needed an operator-granted third round (D0285) and landed by a recorded override (D0286), because
> the cap has no per-unit exception path (BG0841). Verdict: achieved; the tag is cut after the
> signature.

## What landed

- **The docs match the code (EP0266).** The skill docs name no retired verb (US0924), every
  script's `--help` describes the v6 loop (US0964), the upgrade page takes a v5, v4 or older
  project across (US0955), and the v6.0.0 release notes lead with what changed for the reader,
  every figure sourced (US0953).
- **The upgrade is rehearsed on copies of two real projects (US0962).** A v4.1 project (687
  stories) and a v2.4 project (593): every `migrate` run exited 0 in under ten seconds, added no
  validation error, and found nothing left on a second run. Four Medium findings in what its report
  names or omits are filed (BG0842-BG0845); the record is docs/upgrade-rehearsal-v6.md.
- **The evals run against v6 (US0963, US0965).** Eval 09 is new: a fresh agent runs a two-story
  lean sprint from the docs alone and passed every blocking behaviour, which gated v6.0.0 (D0280).
  Eval 06 failed on rc.1 (an agent approved its own fix); after BG0812 and BG0815 one final run on
  main passed 11 of 11 (D0282), with three earlier attempts disclosed. Eval 02's two skipped
  reviews are fixed (BG0814, BG0816).
- **A signed report is checkable from any clone (CR0599).** The signature is tracked (US0959),
  every report signed before that has its run record filed (US0960), and a report's Verified on
  names the commit the close's gate ran against (BG0819).
- **Six first-week defects fixed before the cut (D0284):** `init guided` holds a drafted stage
  (BG0818), an approved story or bug awaits only the signature at any status (BG0820),
  `install.ps1 -Local` leaves personal copies alone (BG0821), the close and sign speak v6's
  vocabulary (BG0822), and `close --dry-run` reads the open run (BG0823).
- Smaller fixes: the forecast rate follows the newest runs and can be pinned (BG0798), the
  report's Lessons section cites the store it read (BG0804), stop-ship rulings read one constant
  (BG0725), and two tests that went red on a new filing now hold still (BG0810, BG0813).

## What is owed

- **The v6.0.0 cut, after the signature:** rename `[6.0.0]` to `[6.0.0-rc.1]`, re-point the
  release notes' two CHANGELOG anchors, bump the version homes, `changelog-cut`, the README and
  INSTALL pins, `known_issues write`, the release gate, forward-port (lifting the soak pin), and
  the website's landing page and deploy (its own sprint).
- **35 open Medium defects are disclosed in the notes**, 28 in code a user runs: the upgrade's
  four (BG0842-BG0845), the review brief's base ref and hand-over (BG0827, BG0817), a carried unit
  `sprint plan` cannot take (BG0829), ULID ids, retro run ids and token capture in the close
  (BG0825, BG0826, BG0835), and `init guided`'s personas stage (BG0824, BG0840).
- **Sprint 7 (v6.1):** one command for the loop and automatic token capture (CR0602), the review
  cap's exception path (BG0841), and moving the tests that read this repository's live artefacts
  off the commit path: three turned main red this sprint with no code change.
