<!-- close-status:begin -->
> **RUN-01M3BK9Y closed running.** 35 unit(s) in the batch. **The run signature is OWED and is the operator's** - `sprint sign` seals the batch in one signature.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M3BK9Y, Sprint 4 of back to basics: history-aware review, and the review paperwork
> deleted.** Goal: "Maya's units are reviewed once against their files' history, and the review
> paperwork nobody reads is deleted." 35 of 36 batch units delivered (111 points against 110
> planned), each reviewed by one QA-seat reviewer under the two-round cap; US0914 was cut under
> the plan's cut order (D0269) and the repair ledger it deletes is still read. Verdict: partial.
>
> Closing review of record: RETRO0124.

## What landed

- **The record informs the work (CR0594, EP0264).** A goal traces to a PRD outcome or persona
  (`plan --serves`, US0927), the goal review shows the PRD's outcomes and persona End goals
  (US0928), the PRD states outcomes O1-O8 (US0929), and every lane brief carries the history of
  the files it touches, with a prior-art instruction (US0930, US0931). The TRD gains a
  constraints column (US0932) and restatements of what the code derives are cut (US0933).
- **The review paperwork is deleted (EP0263).** Plan review (US0909 via BG0767), the test-plan
  gate and tooling (US0911, US0912), the repair plan (US0913), the two-role gate and per-unit
  sign-off (US0916, US0917: `sign` seals the run once), depth tiers and derived depth (US0934,
  US0910), the gate's mutation lane and evidence drift (US0921, US0920), the repair mutation
  gate (US0935) and the plan-review phase (US0915 via BG0769). Each retired criterion is
  recorded in the D0259 pattern.
- **Sprint 3's carries landed:** the lane cap (BG0760, US0905 Done), the lane-yield join
  (BG0761), concurrent pre-commit lanes (BG0759), the CR evidence rule (BG0756), and the
  report-window races (BG0750, BG0751). CI's bandit finding (BG0762) is fixed.

## What is owed

- **US0914, the repair ledger, is cut (D0269).** Its build passes all six criteria and is kept
  at `sdlc-studio/.local/US0914-built.patch`; landing it strips `critiqued` from 35 historical
  Done units, so Sprint 5 first rules a date-scoped historical answer as a criterion.
- **A commit is 7s over budget.** A one-line gate.py commit measured 97s at the close (load
  0.65), against 93s at Sprint 3's close; BG0754 stays open.
- **Main was red on CI's unittest run** for an afternoon (BG0770, fixed): the push gate runs
  pytest and CI runs unittest discover. Pick one runner.
- **25 held backlog items wait on BG0772.** Their closing stories shipped, but a test pins
  every held item open, so closing them turned the push red; the closure was reverted.
- **The close's tick-verification row cannot read the lean criterion shape** (BG0771), so it
  is handed over as a close gap rather than waived (D0271 retracts D0270).
- Also open: CR0592 (Low findings, several added this run), BG0752, and the prose US0924 owns.
- **Next: Sprint 5** - US0914 with its historical ruling, then EP0263's remaining waves
  (US0918, US0919, US0922-US0926, US0936).
