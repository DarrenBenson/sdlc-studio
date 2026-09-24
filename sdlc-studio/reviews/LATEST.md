<!-- close-status:begin -->
> **RUN-01M3891F closed running.** 11 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M39MC0, Sprint 3 of back to basics: commits under ninety seconds, lanes that show their
> yield.** Goal: "A commit clears in ninety seconds, and every commit lane left standing shows what
> it caught." 16 of 21 planned units delivered (32 of 45 points), each reviewed by one QA-seat
> reviewer under the two-round cap; four were carried at the cap and BG0754 stays open. Verdict:
> partial.
>
> Closing review of record: RETRO0123.

## What landed

- **Lanes deleted, not tuned.** The warning ratchet and its baselines (US0896), the verify
  ratchet (US0897), the boundary roster (US0901) and the hand-edited release-notes count, now
  derived by `known_issues.py` (US0898), are gone. Eight advisory gate lanes left the commit and
  run on demand or at the close (US0895, D0263).
- **Commits got faster.** The decisions scan is memoised (US0890), xdist takes one test at a time
  where supported (US0892), live-repository tests wait for the push (US0893), and `close_owed`
  walks the corpus once, 58s to 0.4s (US0894). A one-line gate.py commit measured 93s end to end
  at the close, against 229s at the start; its suites took 43s.
- **Drift is fixed at commit, not refused.** Mechanical index and epic drift is settled by the
  pre-commit hook itself (US0899). Each hook lists its own lanes with `--list` (US0901).
- **The ratchet is watched.** Lesson class LC-008 and the PRD principle "Every gate earns its
  place"; lesson graduation proposes retiring a check as readily as adding one (US0903), and the
  seats push back on new pins (US0906). Python 3.10 works again, with a CI step (US0908).
- **The backlog matches the lean direction.** D0265 closed 197 items and holds 47 open until the
  deletion work they wait on ships (US0907, D0264). 121 of the 327 reviewed items stay open.

## What is owed

- **Four units carried at the review cap, each with its fix filed:** US0891, concurrent
  pre-commit lanes (BG0759, a one-line HUP trap); US0900 (BG0756); US0904, the lane-yield log
  (BG0761, a one-character same-second join); US0905, the lane cap (BG0760, controls to derive
  from `--list`). Carried patches are in `sdlc-studio/.local/`.
- **A commit is 3s over budget.** BG0754 stays open until BG0759 lands: the sequential
  pre-commit is the remaining cost.
- Also open: BG0757 (repo map null byte under Python 3.10), BG0758 (a command-audit module leak),
  BG0750-BG0753 from Sprint 2, and CR0592 for the Low findings.
- **Next: Sprint 4, led by CR0594** (the record informs the work), then EP0263's deletions.
