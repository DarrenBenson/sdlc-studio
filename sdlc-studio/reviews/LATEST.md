<!-- close-status:begin -->
> **RUN-01M3ZAGE closed goal-reached.** 35 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M3ZAGE, the whole groomed backlog.** Goal: "Maya signs a sprint report whose every
> figure is true, and every tool reports only what it judged." Two lanes run one after the other
> (D0314): lane A the report and close, lane B the tools, ids and gates. Every unit reviewed by
> one independent QA seat; BG0913 and BG0885 were carried at the cap and discharged by the
> reviewer who rejected them. Builder spend recorded per unit through `lane return`, reviewer
> spend at run level.

## What landed

- **The report's figures.** Minutes compare like for like (BG0898), the delegated total survives
  a meter of zero (BG0900), partial agent minutes are labelled (BG0901), DORA ignores cancelled
  runs (BG0904), calibration reads measured wall (BG0907), and a re-close keeps the first close's
  window for cost while findings run to the re-close (BG0913, BG0916, BG0920). Every new rule
  mark round-trips through revalidate (BG0900, BG0913, BG0919), and the templates' prose follows
  the page's own rule (BG0898).
- **The close shows what it judged.** The note is checked against the filed page (BG0911,
  BG0918), the readable page is written to the ignored .local/reports and named before the sign
  command (BG0912, D2a), and a step hands over only its failures (BG0908, BG0915).
- **Lanes and lessons.** The lane brief tells a repair to carry only its blocking fix and pins
  (US0982, CR0608, so LC-005 graduates); a terminal unit's span stays closed (BG0899, BG0917);
  lane totals say what they did not record (BG0903); a sealed run takes no late total (BG0902);
  a carry bug filed at the cap does not count against the triage cap (US0981, D0297).
- **Tools and gates.** The pre-push hook fails closed and peels annotated tags (BG0870); the push
  boundary judges the pushed artefacts (BG0871); next_id mints v3 ids on a v3 project (BG0872);
  reconcile reads v3 meta rows (BG0873); config shows code defaults (BG0878); index tables pad by
  display width (BG0889); migrate reads code, not prose, including fenced blocks (BG0896,
  BG0925); critic record escapes a finding so the verdict log lints, and reads it back as typed
  (BG0885); and several doc and message corrections (BG0882, BG0886, BG0887, BG0888, BG0914).

## What is owed

- **Filed from this run, groomed, in the backlog:** BG0921, BG0922, BG0924 (wrong messages a
  user sees), BG0926 (a lane return between close and sign invalidates the page), BG0927 (the
  long-path transcript scan crashes on a broken link).
- Every seat ruling is in the decision log (D0311-D0324), per D0295; the operator's plan
  approval is D0314.
