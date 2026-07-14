# CR-0243: Disposition: every retro finding becomes a filed artefact or a recorded decline

> **Status:** Complete
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 D1
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P1
> **Type:** feature

## Summary

No retro finding has ever become a Bug or CR: `file_finding.py` is wired to review and never to retro. In sdlc-studio-lens, 9 retros carry a Lessons section and reference exactly 1 artefact id between them. Wire `file_finding` into retro, and add a BLOCKING gate leg: each finding must be filed (BG/CR) or declined with a reason. Declining is equally green, so honesty costs what noise costs and there is nothing to game. Untouched prose blocks the close.

## Impact

Every project running a retro. Today the ceremony is performed and produces nothing: findings are
written under a heading and never become work. Nothing "breaks" - that is the problem. The change
adds a blocking gate, so a sprint close that would previously have passed on an undispositioned
finding will now fail until each one is filed or declined.

**Effort:** M

## The question is the mechanism

The template is what drives behaviour, and we have the evidence: **8 of 9 retros in a consuming
project carry a `## Lessons` section because the template prompts for one.** Those same 9 retros
reference exactly **1** artefact id between them - because nothing ever asked what to file.

So the template must ask, in as many words:

> **Are there any CRs or Bugs you want to raise in this project to address any of the issues
> found?**

That single prompt is what converts a finding into work. The gate below makes it un-skippable; the
question makes it natural. Ask first, enforce second - a gate on a question nobody was asked is
just a wall.

## Acceptance Criteria

- [ ] **AC1:** The retro template asks, explicitly, whether any CRs or Bugs should be raised to
      address the issues found, and carries a section for the answer - so an agent writing a retro
      cannot reach the end without having been asked.
- [ ] **AC2:** A retro finding can be filed as a Bug or CR through the deterministic filer, exactly
      as a review finding already is: one command, a real id, an index row.
- [ ] **AC3:** A sprint close FAILS while any retro finding is neither filed nor declined.
- [ ] **AC4:** A finding declined WITH a recorded reason passes that gate - decline is a
      first-class disposition, not a workaround, so honesty costs exactly what noise costs.
- [ ] **AC5:** The gate leg is validated against the bug it defends (LL0010): a retro carrying an
      undispositioned finding FAILS the close, and an empty retro FAILS it (BG0123), before the leg
      is trusted.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
