# RFC-0063: Human in the lead: the accountable engineering lead becomes the Primary, and every change carries evidence a change board accepts and a cost a team can read

> **Status:** Draft
> **Decomposed-into:** CR0689
> **Priority:** High
> **Size:** XL
> **Author:** Darren Benson (operator); drafted with Claude Opus 5.5
> **Date:** 2026-11-09
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** Darren Benson (operator), drafted with Claude Opus 5.5; human; v1
> **Spans:** sdlc-studio (personas, PRD, docs, sprint and report scripts) + the companion dashboard (a consuming project; read side only)
> **Related:** RFC0060, RFC0061, RFC0062, EP0275, EP0276, EP0280, EP0281, EP0287, EP0300, CR0621, CR0629, CR0670, CR0672, CR0680, CR0685; the companion dashboard's RFC-01M46B5Y
> **Supersedes / Superseded by:** none

## Summary

The product has outgrown the user it is designed for. The persona registry names a solo founder-engineer as the Primary and declares the enterprise delivery manager, whose goals include compliance audit trails and reporting, a Negative persona. Yet the white paper sells to "the reader who answers to a regulator", the operator's own production use is teams of three people working through change approval boards, and an industry analyst who reviewed the skill on 2026-11-06 named governance and first-class artefacts as its differentiator.

This RFC makes the accountable engineering lead the Primary, keeps the solo builder as the way in, adds a change approver who never runs the tool as a served persona, and narrows the Negative persona to what the skill still declines: a GUI-first operator, non-technical staff running it, and a human approval on every change. It then sets the 6.4 to 7.0 direction around four themes (evidence that stands up, cost you can predict, learning that compounds, teams and adoption), adds a guardrail that keeps machinery work in proportion, and names a read-only companion dashboard over the committed record as the human view in place of a tracker.

Every decision of direction below was taken by the operator on 2026-11-09. What remains open is how, not whether: the Open Decisions table lists those for the seats.

## Context & Problem

- **The design target contradicts the selling point.** `personas/index.md` declares Maya Okafor (solo founder-engineer) Primary for the shipped skill and Trevor Hale Negative. Trevor's card lists "audit trails for compliance" among his needs and "compliance reporting" among the End goals stated to exclude. Section 8 of `docs/whitepaper.md` sells exactly those properties, including the SOC 2 CC8.1 separation-of-duties shape.
- **Every unit is judged against the wrong person.** 233 of the 272 stories created since 2026-09-23 name Maya; 15 name Jonah. Work for a change approver has no persona to serve: a Sprint Goal for it could trace only to Trevor, a Negative persona, and `sprint.py plan` would print `goal serves: NONE`.
- **The ratchet is coming back.** A rough count of the 832 stories and bugs created since 2026-09-23, bucketed by their `Affects` paths, puts about 44% on sprint, review and gate machinery, 16% on repository-only tooling and 1% on public docs. Since 2026-10-20 repository-only tooling is 22% of new units, and Rowan Achterberg is named on 16 of 53 new stories. Of the 59 open change requests, 29 are machinery, 8 repository-only tooling and 2 adoption. The back-to-basics review (2026-09-23) found 82% of the last 116 v5 units on machinery; O5 says a check that catches nothing is deleted, but nothing measures the mix as it builds up.
- **The front door is written for no one in particular.** The README is 5,209 words for five audiences and leads with "the antidote to vibe coding". The website's evidence page stops at RPT0011 (2026-09-29) with no dollars, while 25 signed reports exist and RPT0027 states $2.89 a point. 6 of the last 7 runs (RPT0021 to RPT0027) were judged partial, and the page shows none of them. SUPPORT.md still installs by copying into Claude Code only.
- **The words disagree with the practice.** In the skill, "Three Amigos" names the agent seats (Dani, Sam, Lena). In the operator's practice it names the three people who each own one specification (product owner the PRD, engineer the TRD, QA the TSD) and to whom the seats report. The website's Three Amigos page never assigns a specification to a human.
- **What the analyst probed, and what is missing.** Asked how a model choice is justified ("based on what data?"), the honest answer today is per-run cost and an opt-in tier map, with no comparison across runs. Asked how the system learns, the answer is retros and failure classes, but a production escape is not traced back to the unit and verdict that let it through (the analyst cited a case where feeding root-cause reports back cut defect escapes by 31%). Asked who owns AI-generated artefacts, the skill has no field that names the accountable human.
- **The human view is a separate product, and it has fallen behind.** The companion dashboard, a consuming project, is a read-only view over the committed `sdlc-studio/` files. Its last commit is 2026-10-06, its workspace is on skill 6.1, and its 13 change requests are unstarted. Its observability gap analysis (RV0003) raised CR0609 and CR0610 here, now EP0275 and EP0276.
- **The models the operator recommends cannot be priced.** `templates/model-prices.json` holds no xAI Grok or Cursor Composer entry, so a run on the recommended delivery model reads "not priced".

## Goals / Non-Goals

**Goals**

- The persona registry and the PRD's Target Users name the accountable engineering lead as Primary for the shipped skill, Maya as Secondary, a change approver as a served persona, and a narrowed Trevor; the persona-coherence test passes on the change.
- The PRD's Mission leads with "human in the lead, not just in the loop", and its Outcomes gain outcomes a Sprint Goal can serve for the change approver, for cost a team can budget, for learning from escapes, and for the committed record a dashboard reads.
- One vocabulary everywhere: the Three Amigos are the people; the agent personas are seats.
- The front door (README, SUPPORT.md, the website's evidence page, a page for engineering leaders) is written for an evaluator who arrives with no context.
- 6.4 lands the evidence and cost work an evaluator checks first.
- Each run's mix of product work and machinery is visible in its plan and its report.
- The committed record is the versioned contract the companion dashboard reads.

**Non-Goals**

- No GUI, boards, or per-change human approval in the skill. Viewing belongs to the companion dashboard, which stays read-only.
- No second signature: one signature per run stays (D0213).
- No sync to Jira, Azure Boards or another tracker. The specifications live in the repository and the companion dashboard shows them.
- No rewrite of the PRD's Feature Inventory, the TRD or the TSD. They are amended as the work lands; the claim-drift checks (EP0167) keep them true.
- No new gate without a named yield. The machinery guardrail reports first.
- No change to licence, distribution or the no-account, no-server model.

---

## Design Options

### Option A - Keep Maya as Primary; reposition in the docs only

**Approach:** Change the README, website and white paper to speak to engineering leaders; leave the persona registry and PRD as they are.
**Pros:** No product churn; the lean loop stays protected by the existing Primary.
**Cons:** The message and the design target disagree; evaluators arrive at a tool built for someone else; enterprise work keeps tracing to a Negative persona and is declined by the persona check.
**Effort / risk:** S; high risk of drift between what is said and what is built.

### Option B - The accountable engineering lead becomes Primary (recommended, decided)

**Approach:** Promote or replace the Secondary card so the Primary is an engineering lead in an audited or regulated organisation running several three-person teams on agents the organisation already licenses. Maya becomes Secondary. A change approver who never runs the tool is added as a served persona whose goals become standing criteria (CR0621's mechanism). Trevor is narrowed.
**Pros:** The design target matches the validated market and the operator's own use; governance and evidence work gains a persona to serve; the solo builder keeps the on-ramp.
**Cons:** Some open backlog needs re-judging against the new Primary; an enterprise persona can pull ceremony back in.
**Effort / risk:** M for the registry and PRD; the risk is held by the Non-Goals above and the guardrail in WS7.

### Option C - Two editions, lite and enterprise

**Approach:** Ship separate profiles or packages, each with its own Primary.
**Pros:** Clear segmentation.
**Cons:** Doubles the documentation, tests and release work for one maintainer; the `profile: lite` setting already covers the small case.
**Effort / risk:** XL; high maintenance risk.

---

## Recommendation

**Option B**, decided by the operator on 2026-11-09, with the workstreams below. WS1 goes first because every later unit is judged against the persona it sets.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Who the Primary is | A keep Maya; B accountable engineering lead; C two editions | Operator | Operator call | Decided: B (operator, 2026-11-09) |
| D2 | The Primary's card | Promote Jonah Reyes and widen his card to an audited organisation with several three-person teams; or write a new card and keep Jonah as Secondary | Product seat | Consult the seats against the cast; operator confirms | Resolved: Decided by the operator (D0436): a new Primary card for a head of engineering in an audited organisation leading several three-person teams, named by the seats; Jonah stays Secondary unchanged; Maya moves to Secondary |
| D3 | The change approver's form | A served persona with standing criteria (CR0621), never designed for as an operator; or a Secondary persona | Product seat | Consult | Resolved: Decided by the operator (D0437): the change approver joins as a Served persona with three End goals, standing criteria when EP0285 lands |
| D4 | New PRD outcomes | Proposed O10 to O13 below, wording to be settled | Product seat | Stakeholder consult, then operator | Resolved: Decided by the operator (D0438): O10-O13 start from the operator's draft; the seats refine the wording only, dissent shown at plan approval |
| D5 | Vocabulary | "Three Amigos" for the people, "seats" for the agent personas; template file names may stay | Operator | Operator call | Decided (operator, 2026-11-09) |
| D6 | The human view | The read-only companion dashboard in place of a tracker; no tracker sync | Operator | Operator call | Decided (operator, 2026-11-09) |
| D7 | The 6.4 goal | Evidence and cost first: EP0280, EP0276, EP0275, CR0670, EP0300, CR0685; RFC0062 accepted | Operator | Operator call | Decided (operator, 2026-11-09) |
| D8 | Machinery guardrail strength | Report the mix in the plan and the report only; or refuse a plan over the cap without a recorded maintenance declaration | Engineering seat | Spike against the run archive, then operator | Resolved: Decided by the operator (D0440): report and declare; the plan and report show points by area, and a plan over a third machinery records a maintenance declaration; nothing refuses |
| D9 | What counts as machinery | A declared path map (loop scripts, `tools/`, `.githooks/`, `.github/`) or a per-unit tag set at refine | Engineering seat | Spike: re-bucket the v6 units both ways | Resolved: Decided by the operator (D0439): a per-unit area tag set at refine, with a path map flagging a tag that disagrees with the files touched |
| D10 | The dashboard contract | The evidence annex (EP0275) carries a schema version the dashboard pins; or the dashboard adapts per schema, as its RFC-01M46B5Y proposes | Engineering seat | Cross-repo consult with the dashboard | Resolved: Decided by the operator (D0441): the evidence annex carries a schema version the dashboard pins; the dashboard upgrades its workspace first |

Proposed outcomes for D4, each citing an End goal on the new cards:

- **O10:** Every change that reaches a change board carries its criteria results, its independent verdict, its known issues and a named human owner, in a form the approver reads without running the tool (change approver).
- **O11:** A team knows what its delivery costs per point, in money, from whichever harness ran it, and can hold it to a monthly budget (Primary).
- **O12:** A defect that escapes to production is traced to the unit and the verdict that let it through, and the next plan, build and review learn from it (Primary; change approver).
- **O13:** The committed record (reports, run records, verdicts, lessons) is versioned and complete enough that a read-only dashboard shows progress, evidence and cost without the operator's machine (Primary; change approver).

O1 to O9 stay; their persona citations are re-pointed if D2 renumbers a card's End goals.

---

## Architecture Impact

| Layer / System | Impact | Change Type |
| --- | --- | --- |
| `sdlc-studio/personas/` | Primary, Secondary, served and Negative cards change; the index and revision history follow | Enhancement |
| `sdlc-studio/prd.md` | Mission, Target Users and Outcomes amended; Feature Inventory untouched | Enhancement |
| `sdlc-studio/trd.md`, `tsd.md` | ADRs added as WS4 to WS7 are designed; test objectives added as features land | Enhancement |
| README, SUPPORT.md, `docs/`, the website | Front door rewritten; evidence page generated from `reports/*.json` | Enhancement |
| `sprint.py plan`, `sprint_report.py` | Points by area in the plan; the area mix and any maintenance declaration on the report | Enhancement |
| `templates/model-prices.json`, `lib/prices.py` | xAI Grok and Cursor Composer priced from dated provider sources | Enhancement |
| Report and evidence tooling | A change evidence pack per release | New |
| Triage, retro and verdict ledger | An escape names the unit it escaped from; seats are scored on it through RFC0061 | Enhancement |
| `reference-schema.md` and the evidence annex | The versioned contract the dashboard reads (EP0275, EP0276) | Enhancement |
| The companion dashboard | Reads the contract; its own change requests carry the views | Cross-repo |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| The enterprise Primary pulls ceremony back in | Medium | High | The Non-Goals; one signature per run; every gate names its yield; Trevor stays Negative for GUI and per-change approval |
| Persona churn breaks the persona-coherence test or strands open units | Medium | Medium | WS1 changes the registry and the PRD's Target Users in one unit; open units are re-pointed by a sweep, not by hand |
| The RFC is too large to deliver | Medium | Medium | Decompose into the workstreams below; 6.4 takes WS1, WS3's first items and the existing evidence and cost epics only |
| The dashboard drifts from the skill | High | Medium | WS8 makes the annex the versioned contract; the dashboard upgrades its workspace before building views |
| The guardrail becomes another gate | Low | Medium | D8 leans to reporting and a recorded declaration, not a refusal |

---

## Phased Plan / Workstreams

| WS | Workstream | Repo | Becomes | Depends on |
| --- | --- | --- | --- | --- |
| WS1 | Persona registry and PRD: the new Primary (D2), the change approver (D3), Maya Secondary, Trevor narrowed; PRD Mission, Target Users and Outcomes O10 to O13 (D4) | sdlc-studio | CR (new) | - |
| WS2 | Role model and vocabulary: the Three Amigos are the people, seats are the agent personas; an owner field naming the accountable human on the PRD, TRD and TSD | sdlc-studio | CR (new) | WS1 |
| WS3 | The front door: README cut to about 1,500 words with three routes in (evaluate, try, upgrade); SUPPORT.md current and honest about support; the evidence page generated from the reports with partial verdicts and waiting time explained; a page for engineering leaders (change approval, separation of duties, the signed report, cost); the white paper refreshed with 6.3 cost data; release notes led by plain-English bullets; a guide to running the discovery track beside delivery | sdlc-studio | CR (new) | WS1; WS2 for the role-model wording |
| WS4 | Evidence that stands up: EP0280, EP0276, EP0275 in 6.4; then EP0281 and a change evidence pack per release | sdlc-studio | Existing epics; CR (new) for the evidence pack | - |
| WS5 | Cost you can predict: RFC0062 with CR0670 and EP0300; CR0685; xAI Grok and Cursor Composer pricing; then CR0672, CR0680 and a monthly team budget view | sdlc-studio | Existing CRs and epics; CR (new) for pricing; CR (new) for the budget view | - |
| WS6 | Learning that compounds: EP0287 (CR0632, CR0633); then an escape loop (O12) and a model scorecard per seat and model from signed runs (rounds, rejections upheld, escapes, dollars a point) | sdlc-studio | Existing epic; CR (new) each for the escape loop and the scorecard | WS4 (EP0280) |
| WS7 | Machinery guardrail: points by area in the plan and on the report; a recorded maintenance declaration over the cap (one third of the run's points); gate yield reviewed at each retro (O5) | sdlc-studio | CR (new) | D8, D9 |
| WS8 | The dashboard contract: the evidence annex and the committed report as the versioned record the dashboard reads; the dashboard upgrades its workspace and builds its views against it | sdlc-studio + the companion dashboard | EP0275, EP0276 here; the dashboard's existing change requests there | WS4 |

Sequencing for 6.4 (to the end of 2026): WS1 first; then WS4's three epics, WS5's first items (CR0670, EP0300, CR0685 and the new pricing), EP0287 from WS6, and WS3's README, SUPPORT.md, evidence page and engineering-leaders page. WS2, the rest of WS3, WS5 and WS6, WS7 and the dashboard side of WS8 follow in 2027 Q1. Until WS7 is tooled, the operator applies the one-third cap at plan approval.

---

## Decision

> *Filled on acceptance.*

**Outcome:** pending `rfc decide` (Option B is already the operator's decision; D2, D3, D4, D8, D9 and D10 remain open)
**Rationale:** pending
**Spawned CRs:** pending, one or more per new-CR row in the workstream table

---

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| RFC | RFC0060 | the dark factory | Accepted | sibling: where the line stops for a human |
| RFC | RFC0061 | Personas become accountable team members | Accepted | sibling: seat scoring that WS6 extends |
| RFC | RFC0062 | Token-efficient delivery | Draft | workstream WS5 |
| EP | EP0275 | A versioned evidence annex | Draft | workstreams WS4, WS8 |
| EP | EP0276 | The report of record is reviewable from the committed tree | Draft | workstreams WS4, WS8 |
| EP | EP0280 | A recorded review verdict is what the reviewer wrote | Draft | workstream WS4 |
| EP | EP0281 | A unit's criteria are shown to fail without its change | Draft | workstream WS4 |
| EP | EP0287 | Personas become accountable team members | Draft | workstream WS6 |
| EP | EP0300 | Every consuming agent starts leaner | Draft | workstream WS5 |
| CR | CR0621 | A served persona's goals as standing criteria | In Progress | mechanism for D3 |
| CR | CR0629 | A served persona's End goal run at the close | In Progress | evidence for O10 |
| CR | CR0670, CR0672, CR0680, CR0685 | Cost workstream items | Proposed | workstream WS5 |
| RFC (companion dashboard) | RFC-01M46B5Y | A delivery-observability plane for the dashboard | Draft | cross-repo sibling for WS8 |

> **Cross-repo note:** WS8 spans this repository and the companion dashboard's. The dashboard uses ULID ids; confirm the next free number here against `origin/main` before filing.

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Darren Benson; drafted with Claude Opus 5.5 | RFC drafted from the operator's strategy review: context with measured evidence, three options, the operator's decisions (D1, D5, D6, D7), six open decisions, proposed outcomes O10 to O13, impact, risks and eight workstreams |
| 2026-11-09 | rfc resolve (operator decision) | resolve: D2 - Decided by the operator (D0436): a new Primary card for a head of engineering in an audited organisation leading several three-person teams, named by the seats; Jonah stays Secondary unchanged; Maya moves to Secondary |
| 2026-11-09 | rfc resolve (operator decision) | resolve: D3 - Decided by the operator (D0437): the change approver joins as a Served persona with three End goals, standing criteria when EP0285 lands |
| 2026-11-09 | rfc resolve (operator decision) | resolve: D4 - Decided by the operator (D0438): O10-O13 start from the operator's draft; the seats refine the wording only, dissent shown at plan approval |
| 2026-11-09 | rfc resolve (operator decision) | resolve: D9 - Decided by the operator (D0439): a per-unit area tag set at refine, with a path map flagging a tag that disagrees with the files touched |
| 2026-11-09 | rfc resolve (operator decision) | resolve: D8 - Decided by the operator (D0440): report and declare; the plan and report show points by area, and a plan over a third machinery records a maintenance declaration; nothing refuses |
| 2026-11-09 | rfc resolve (operator decision) | resolve: D10 - Decided by the operator (D0441): the evidence annex carries a schema version the dashboard pins; the dashboard upgrades its workspace first |
