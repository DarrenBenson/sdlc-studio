<!-- close-status:begin -->
> **RUN-01M7GEHM closed goal-reached.** 21 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

Signed on 2026-11-15 over RPT0032 (fingerprint dfa4679614cfeb00), sealed goal-reached. The
operator, away on a ten-hour flight, authorised the orchestrator to sign every run it closes
meanwhile and to open the next (D0479); the orchestrator entered `sprint sign --principal
"Darren Benson"` on that authorisation.

> **RUN-01M7EYR3, run thirteen.** Goal: "A head of engineering sees each review seat's record,
> and an escaped defect traced to the approval that missed it." 16 units, 54 points (44 of the
> 49 planned, and 10 added in-run: D0483 to D0487), all delivered on independent APPROVEs.
> US1058 was carried at the review cap and delivered through BG1460; US1064, US1065, US1067,
> US1068 and BG1471 converged at round 2. Machinery share by theme 2 points (about 4%). Cost
> 46.7M priced tokens, 864k per point, $126.86 ($2.35 per point) against run twelve's 843k and
> $2.27.

## What landed

- **Seat record**: each review seat's record lists its approvals and rejections, the round each
  unit converged in, the units it built and the defects found only after it approved
  (US1061, US1062, US1064).
- **Escaped defects**: a bug records that it escaped, the release it shipped in and the unit
  that let it through; `escape.py` traces it to the approving verdict, and a lesson class
  records the cause for the next build and review (US1157, US1158, US1159).
- **Persona learning**: each seat keeps evidenced learnings in its own memory file
  (US1058 via BG1460, US1059), proposes them from its own record, another seat approves or
  rejects them (US1065, US1066), the close lists every learning about to go live and the
  signature can strike one (US1067, US1068). Only a signed run's learnings reach a brief
  (D0488), and every write to the store is read back as stamped, so no forged body, duplicate
  id or multi-line reason can approve a learning (BG1460, BG1471).
- **Main kept green**: BG1459 and BG1468 fixed the two boundary reds the persona-memory lanes
  caused; BG1469 pins the fields-file paths on `propose` and `approve`.

## What is owed

- **Carried, not stop-ship** (RETRO0146): BG1455-BG1458, BG1461-BG1467, BG1470, BG1472 and
  BG1473 from the reviews and the run's tooling frictions, and CR0706 (CR0693's remainder),
  CR0707 (a lane rebase step) and CR0708 (file_finding's stub criteria).
- **Pushed**: pending - the push gate's full suite runs next.
- **Run fourteen**: groomed and Ready (the front door: EP0310 to EP0313 and six consumer bugs,
  42 points), opening next under D0479.

## Learned the hard way

- A review-cap carry bug inherits the carried unit's Affects, including its changelog fragment,
  so the carry's self-check is refused at the land (BG1467): point the carry at its own fragment
  before building it.
- A builder's self-check rows left unstaged in its worktree make the land's rebase fail after
  the full hook run (BG1470): restore `author-self-checks.md` in the worktree before handing back.
- The full suite mid-run found two boundary reds (BG1468) the lanes' selections never ran; run it
  after each wave, not only before the close.
- The close's dry run takes about half an hour, mostly the review-currency check's per-file
  `git log`; start it early, in the background.
