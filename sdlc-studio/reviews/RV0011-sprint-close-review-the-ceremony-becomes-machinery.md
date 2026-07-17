# RV0011 – Sprint-close review – the ceremony-becomes-machinery sprint (RUN-01KXPJG9)

> **Review type:** Sprint-close (CODE leg = adversarial full-diff critic pass; document legs assessed for currency)
> **Reviewer:** Sam Eriksson QA seat (independent subagent a0323623d3bb61d66), full-diff refute framing; per-unit passes by the same seat (8 reviews)
> **Date:** 2026-07-17
> **Triggered by:** the RUN-01KXPJG9 close (`sprint close`, mandatory reconcile + review)
> **Scope:** git diff 5f864bf..HEAD - 8 delivered units (EP0063-EP0070), 30 points
> **Predecessor:** RV0010 (unified, 2026-07-16); sprint-close records RV0009/RETRO0043 lineage

## Headline

Eight units delivered and adversarially reviewed; the closing full-diff pass REJECTed
first (three findings the per-unit reviews were structurally blind to - a stranded live
mutant from a killed mutation run, a cross-unit two-role/DoD silent disarm, and the
close brief laundering a red-baseline mutation report), all three repaired test-first
and re-verified by the same critic re-executing its own probes before APPROVE.

## CODE leg (the sprint diff)

- Verdict: **APPROVE** after one REJECT-repair round (recorded in critic-verdicts.md
  under US0196/US0198 for the cross-unit repairs; per-unit verdicts under each unit).
- Mutation evidence: clean-tree run at close - baseline pass, 25 applied, 22 killed,
  3 survived (inspected benign: a debug-only stderr guard, two conditional asserts in
  tests), 0 errors; 4,023 enumerated mutants beyond the cost ceiling not run.
- Gate: PASS end-to-end (style, links, budgets, neutrality, tests, reconcile).

## Document legs

- **PRD/TRD/TSD:** unchanged this sprint; RV0010's findings (the audit backlog
  BG0152-BG0174 / CR0280-CR0306) remain the open synthesis debt - nothing this sprint
  worsened them, and the new capabilities are catalogued in help/ + reference-* in the
  same units that built them (doc-coverage green).
- **Personas:** the QA seat carried all nine reviews; seat cards unchanged.
- **New documents of record:** definition-of-ready/done templates ship with the skill;
  reference-decisions.md#dor-dod is their authority section.

## Sprint Goal verdict

"Every remaining hand-carried quality ceremony - review sign-off, sprint close,
re-verdict, the ready/done bar, forward-port - becomes deterministic, refusing
machinery." - **ACHIEVED**: the sign-off is `critic.py signoff`/`signoff-brief` with
refusals, the close is `sprint close`, the re-verdict is `brief --rejoinder`, the bar
is the DoR/DoD documents the gates read, and the port is `tools/forward-port.sh` -
each shipped with loud refusal paths and used live at this very close.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | Claude Fable 5 | Sprint-close review recorded |
