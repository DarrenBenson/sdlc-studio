# RFC-0059: A run ends with one signed report: the sign-off becomes a transaction over frozen, derived facts

> **Status:** Accepted
> **Decomposed-into:** EP0255
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** operator request, RUN-01M2JA6J 2026-09-16 ("I would like a proper report producing at the end of a run for sign off ... when I say signed off it should be a very simple and quick action")
> **Priority:** High
> **Related:** RFC0058 (stakeholder feedback), CR0571 (who may rule), D0194 (one stop-ship store), LL0027 (gate it in the command people run)
> **Size:** L

## Summary

A run's sign-off is currently a step in the middle of the machinery, not the end of it. In RUN-01M2JA6J the operator's approval was applied and then roughly two hours of work followed: three CI dispatches of 85 minutes each, two adversarial reviews, a repair round, a sign-off fan-out cut short by a timeout, two status cascades and a paperwork repair. The signature therefore covers a state nobody could inspect when it was given.

There is also nothing to sign. The facts a reader would want are spread across at least nine files - the retro, `VELOCITY.md`, three critic ledgers, the mutation ledger, the verify report, the disclosure page and the run state - and no artefact assembles them. The operator is asked to approve a run on the strength of a conversation.

This RFC proposes that a run ends with ONE derived report, that the report is the last thing produced, and that signing it is a transaction of seconds: a signature bound to that report's fingerprint, with nothing that can change the facts permitted after it.

## Context & Problem

Three problems, and they are separable.

**1. Ordering.** `sprint close` runs ten steps, applies the sign-off, then fans it out into per-unit transitions, then cascades epics and requests. Any of those can fail, and in this run several did: the fan-out stopped after one story, an epic and a request needed closing afterwards, and a warning ratchet surfaced a defect in a request's own paperwork the moment it reached its terminal. Each fix was a write to the batch AFTER the signature. The rule the repository already believes - "sign-off is a transaction, not a checkpoint" - is stated nowhere a command enforces it.

**2. Assembly.** The run's own account is derivable but never derived into one place. A reader wanting "was this well tested" today reads a verdict ledger by hand. A reader wanting "what did it cost" reads a velocity table whose last column, for this run, says `not attributable`.

**3. Hollow metrics.** The two numbers the operator asked for first - tokens used and tokens per point - cannot be produced today. RUN-01M2JA6J forecast 3,114,687 tokens across 103 points; every unit's actual reads **UNMEASURED (no telemetry token record)** and the sprint total reads **not attributable: no unit carries per-unit telemetry**. A report that prints "unknown" in its headline row every run is worse than no report, so the attribution has to be fixed as part of this, or the report must say plainly and permanently that the figure is not available in interactive runs.

## Goals / Non-Goals

**Goals**

- One artefact per run, derived end to end, readable by someone who was not in the room.
- Sign-off is the LAST action and takes seconds: it writes a signature and seals, nothing else.
- Every figure carries its source, so a disputed number can be re-derived rather than argued.
- What was NOT proven is a section, not an omission: manual criteria, ruled-equivalent lines, surviving mutants, advisory lanes left red.
- The signature binds to the report's content, so a later change is visibly outside what was signed.

**Non-Goals**

- A single confidence SCORE. A number that compresses mutation, coverage, review rounds and manual criteria into one figure is a number people will optimise. The report shows the facts that make up confidence and names the gaps.
- Replacing the retro. The retro is judgement - lessons, rulings, what to change. The report is measurement. The report may quote the retro's rulings; it must not restate its reasoning.
- New CI, new gates at delivery time, or any change to how units are built.

---

## Design Options

### Option A - Render what exists into HTML at the close

**Approach:** A thin renderer over the retro and the ledgers, run as the last close step.
**Pros:** Small; no new data; ships in one unit.
**Cons:** Fixes neither the ordering nor the hollow metrics; a prettier view of the same scattering, and the signature still floats free of it.
**Effort / risk:** S. Risk: it looks like the problem is solved while the signature still covers nothing in particular.

### Option B - A derived report artefact, JSON first, with HTML and text renderings

**Approach:** `sprint.py report --close` writes `RPTxxxx.json` - every figure with its source - and renders it to a self-contained HTML page and a Markdown twin. The JSON is the artefact of record; the HTML is for reading; the Markdown is for diffing and for terminals. The report carries a fingerprint over its own facts.
**Pros:** One place, derived not authored; the HTML is genuinely readable by a non-participant; a fingerprint makes "what was signed" answerable.
**Cons:** A rendering layer to maintain; HTML in git churns unless it is generated on demand.
**Effort / risk:** M.

### Option C - Re-order the close so the report is terminal, and sign-off is a transaction

**Approach:** Split `close` into PREPARE (everything that can change facts: gates, fan-out, cascades, forward-port, retro validation, LATEST.md) and SEAL (`sprint.py sign --report RPTxxxx --principal ...`), which writes the signature and the run's `closed_at`, and nothing else. PREPARE refuses to produce a report while any batch unit is non-terminal, any review is unanswered, or any index drift remains.
**Pros:** Makes the operator's minute the last minute; the failure this run hit - work after the signature - becomes impossible rather than discouraged.
**Cons:** A long PREPARE is still long; it just stops being the operator's problem. Re-running PREPARE after a late fix must be cheap and idempotent.
**Effort / risk:** M.

### Option D - Make the cost figures real

**Approach:** Stamp the harness token meter at run open and at report time, and record a per-unit delta at each unit's terminal transition. Where a run cannot attribute (a different session closed it), the report says so in the row rather than printing a plausible total.
**Pros:** Turns tokens, tokens-per-point and estimate accuracy from placeholders into measurements; the estimator can then be judged on evidence.
**Cons:** Per-unit attribution in an interactive run is approximate - the meter is per session and cumulative, and work interleaves.
**Effort / risk:** M. Risk: a number that looks precise and is not; the report must show the method beside the figure.

### Option E - Bind the signature, and refuse writes after it

**Approach:** The signature records the report fingerprint. A batch-affecting write after a sealed run is refused, naming the report; re-opening is explicit and recorded. A report whose fingerprint no longer matches the tree reads INVALIDATED wherever it is shown.
**Pros:** The signature means something specific; drift is visible rather than assumed away.
**Cons:** Needs a defined re-open path, or people will work around it.
**Effort / risk:** S-M.

---

## Recommendation

**B + C + E, with D as the prerequisite for B's cost section.** A is rejected: it leaves the signature covering a state that is still moving, which is the actual complaint.

Sequence it as three shippable slices. The operator ruled on 2026-09-16 that **slice 1 leads the next run on its own**: the split is small, testable today, and fixes the operator's minute without waiting on the report or on token attribution.

1. **C first, without the report.** Split PREPARE from SEAL and make `sign` a transaction. This alone fixes the operator's experience, and it is testable today.
2. **B on top.** The report generated at the end of PREPARE, JSON plus HTML plus Markdown, with the sections below. Signing binds to its fingerprint (E's first half).
3. **D and the rest of E.** Token attribution, then the refusal of post-seal writes.

### What the report contains

The section list is SETTLED and shipped as a template: `templates/core/sprint-report.md` is
the Markdown twin and the canonical section spec, and `templates/reports/sprint-report.html`
is the rendering. Both were derived from a worked prototype built over RUN-01M2JA6J's own
artefacts, so the shape is one a real run fills rather than one invented for a specification.

| Section | Content | Source |
| --- | --- | --- |
| Header and filing | Run id, dates, batch size, retro id, verified sha, report fingerprint | run state |
| Sprint goal | The goal VERBATIM, first, before any number, with its verdict and note | run state, goal verdict |
| Ship guardrail | One line: is the trunk green on the commit carrying this batch | named CI run on a named commit |
| Delivered | Points, cost with the MODEL named beside it, rework rate, carried risk | run record, harness meter, verdict ledger |
| Estimate accuracy | Forecast against actual and the ratio, with per-unit UNMEASURED named | run state, velocity table |
| DORA | The four keys with the project's own mapping stated, against the elite bands | CI runs, git history |
| Evidence by unit | Criteria, mutants killed against planned, lines ruled, entry-point depth, review rounds | verify report, mutation ledger, critic ledgers |
| Not proven | Manual criteria, ruled lines, surviving mutants, advisory lanes red, budgets inside tolerance | the same ledgers, read for absence |
| Who judged this | Every reviewer and agent, each with its MODEL and what it found | critic ledgers, sign-off record |
| Stakeholder consult | Each persona's verdict and what it changed | the consult artefact |
| Carried open | Findings filed, rulings, and the review volume behind them | retro carried table |
| Sign-off | Principal, date, fingerprint | written by `sign` |
| Provenance | Every figure's source | generated |

Three of those earn their place against the alternative of showing more:

- **The goal leads.** Quoting it verbatim at the top of a document somebody senior reads is
  what exposed this run's goal as a shopping list of unit ids rather than a statement of
  value (CR0587). A goal nobody re-reads is a goal nobody corrects.
- **Rework rate replaces volume.** Mutants killed and seat verdicts are output: they say the
  run was busy. Rework - the share of units that needed a repair round after review - is the
  stability signal, and it is the one the 2026 DORA reporting says degrades first when more
  of the code is machine-written.
- **The guardrail replaces a table of CI runs.** One line and one decision, the shape
  feature-flag tooling settled on: guardrail metrics attached to every release, and a
  regression stated as ship or roll back rather than as telemetry to interpret.

**Confidence is reported as a profile, not a score** (RULED 2026-09-16 by the operator): how much of the surface the criteria reach (entry-point depth), whether the tests can fail (mutation), what no test reaches (ruled lines), who reviewed it and how many rounds it took, and what is carried open. A reader can then form a judgement the report has not pre-chewed.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | **RULED 2026-09-17 (operator):** a META `RPT` type under `sdlc-studio/reports/`, so the report carries an id, an index row and a history like every other artefact and a ledger can name it | Settled |
| D2a | **RULED 2026-09-16 (operator):** the JSON is the artefact of record, the Markdown twin is committed for diffing, and the HTML is GENERATED ON DEMAND from the committed JSON - no rendered page churns in git | Settled |

| D3 | **RULED 2026-09-16 (operator):** RUN-LEVEL ONLY. The harness meter is stamped at run open and at report time, giving an honest run total and a batch tokens-per-point. Per-unit actuals stay UNMEASURED and the report says so by name rather than splitting an interleaved session into per-unit figures it cannot defend | Settled |
| D4 | **RULED 2026-09-17 (operator):** RE-DERIVATION. A report is INVALIDATED when re-deriving its figures produces different ones - not on any tracked write, which would fire for every change that moves nothing the report states | Settled |
| D5 | Whether PREPARE may be run by a delegate while SEAL stays the operator's, and whether SEAL is offline-capable (no forge reads). **PARTLY RULED 2026-09-17:** the run carries ONE signature, written in SEAL from ONE principal, and PREPARE fans out nothing - so PREPARE takes no principal at all. **RULED 2026-09-20 (operator):** a delegate MAY run PREPARE. It writes no signature, fans nothing out and is re-runnable by contract, so a delegate running it can move no fact the operator is accountable for; the SEAL stays the operator's sole act, which is the separation the split exists for. The offline half is unaffected and stays as ruled | Settled |
| D6 | Whether the report absorbs the handoff or links to it. **RULED 2026-09-20 (operator):** the report ABSORBS it. One page per run, whose remaining-work section reads `none` when the run reached its goal - RUN-01M2SPNS's HO0075 said `9 delivered, 0 remaining`, so the second artefact carried nothing and still had to be kept in agreement with the first. This is the drift this RFC exists to remove, and it is not removed by linking to it | Settled |
| D7 | Retention. **RULED 2026-09-20 (operator):** ONE report per run, kept forever, indexed and diffable - a run owns exactly one RPT id, stable across every re-prepare. BG0716 is the gap: PREPARE allocates a fresh id on every re-file, so RUN-01M2SPNS produced RPT0001 and then RPT0002 for one run, only the last of them true. Its fix follows from this ruling - take the id from the run record when the run already names one, and allocate only when it does not | Settled |

## Evidence

- RUN-01M2JA6J, 2026-09-16: sign-off applied, then three CI dispatches, two delivery reviews, one repair round, a cut-short fan-out, two cascades and a paperwork repair followed it.
- `sdlc-studio/retros/VELOCITY.md`: RETRO0117 records 23 units, 103 points, a 3,114,687-token forecast and an actual of `not attributable`.
- RETRO0117's accuracy block: every one of the 23 units reads **UNMEASURED (no telemetry token record)**.
- The facts a report would assemble are spread across `retros/`, `VELOCITY.md`, `reviews/critic-verdicts.md`, `reviews/critic-evidence.md`, `reviews/repair-record.md`, `reviews/signoff-record.md`, `.local/mutation-runs.json`, `.local/verify-report.json`, `docs/known-issues.md` and `.local/run-state.json`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-16 | Claude Opus 5 (authoring session) | Written on the operator's request at the RUN-01M2JA6J close: five options weighed, B+C+E recommended with D as the cost section's prerequisite, report contents tabled with their sources, seven open decisions. |
| 2026-09-16 | Claude Opus 5 (authoring session) | Operator rulings recorded: slice 1 (the PREPARE/SEAL split) leads the next run alone; token attribution is run-level only, per-unit stays UNMEASURED and named; JSON of record with a committed Markdown twin and HTML generated on demand; confidence is a profile with a NOT-proven section, never a score. |
| 2026-09-16 | Claude Opus 5 (authoring session) | Report contents settled against a worked prototype over RUN-01M2JA6J and shipped as `templates/core/sprint-report.md` plus `templates/reports/sprint-report.html`: the goal leads verbatim, the model is named beside the cost, DORA's four keys carry this project's own mapping, rework rate replaces mutant and verdict volume on the top line, and the CI history collapses to a single ship guardrail. |
| 2026-09-17 | Claude Opus 5 (authoring session) | D1 and D4 ruled by the operator after grooming, confirming the pins the grooming stated as assumptions. The signing question they exposed is ruled too: one signature, written in SEAL, which fans out the per-unit rows and the transitions from that single principal. Its consequence is recorded in US0832 - no unit is terminal when the report is produced, so the report states that each unit has CLEARED ITS TERMINAL GATE rather than that it is Done. |
