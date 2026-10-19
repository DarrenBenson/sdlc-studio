# Stakeholder Review: EP0289 - the persona registry matches the work it serves (US1079-US1083)

**Consulted:** 2026-10-19
**Artefact:** sdlc-studio/epics/EP0289-the-persona-registry-matches-the-work-it-serves.md and its stories US1079-US1083. Context: CR0648; D0373, D0374, D0377, D0378 and D0379; RV0028 findings PER-1 to PER-11.
**Stakeholders Consulted:** 3
**Provisional (unverified) cards:** none on the panel.

- `persona_gen.py classify --root .` grades only `personas/seats/`, where all three cards read `authored`, so it did not grade these three.
- The card under consultation, the skill maintainer's, does not exist yet. It will be agent-authored, and should be read as provisional until a seat that did not write it has reviewed it.

**Mode:** required by D0374, which owes a stakeholder consult before any epic that changes a persona or its goals is built.

- D0374 makes the consult owed, not a verdict binding. The verdicts inform, and the operator rules.
- D0379 is taken as ruled. The consult judges the breakdown that implements it.
- Verdicts were **not** recorded through `critic.py` / `ledger.py`, because this run was read-only on the repo.

**Method:**

- Each persona ran as an isolated subagent in a fresh context, per `reference-consult.md`. Each was briefed with its own card, the artefact and an evidence surface, never with the synthesiser's findings.
- The synthesiser re-checked every claim a persona cited, three of them by fixture. Corrections are listed under Findings verified by execution.
- The cards declare a cast role, not a `<!-- stakeholder: -->` type, so groups follow the cast role, as in consult-CR0526.
- Trevor Hale is the Negative persona. His objections are weighed on their evidence and not adopted as requirements.

---

## Verdicts

| Persona | Perspective | Verdict |
| --- | --- | --- |
| Maya Okafor | solo founder-engineer, Primary for the shipped skill | Concerns - supports the second Primary, not the breakdown |
| Jonah Reyes | team lead, brownfield adoption, Secondary | Concerns |
| Trevor Hale | enterprise delivery manager, Negative | Concerns |

No persona opposes D0379. All three, working independently, reject the breakdown as written, largely on the same evidence.

## Where the three converged, independently

1. **US1079 cannot land on its own.**
   - Its Affects omits `sdlc-studio/prd.md`.
   - `test_persona_coherence.py:70-87` fails as soon as the registry names someone the PRD's Target Users section does not. Confirmed by fixture.
   - US1079 lands in the second run (D0377), and the PRD story in the third (D0378).
   - Raised by all three.
2. **The predicate misses the work that motivated it.**
   - Epic AC1 enumerates "wholly tools/, .githooks/ or .github/".
   - All four of EP0288's stories, the case D0377 names, carry `changelog.d/`.
   - Three of them also add CONTRIBUTING.md, AGENTS.md or a shipped reference file.
   - Raised by all three.
3. **US1081 would write the maintainer's frustration onto Maya's card.**
   - RPT0020's goal, "her gates say up front what they need and cost", was delivered by US1003-US1006, every one of them repository tooling.
   - Raised by Maya and Trevor. Jonah asks that the maintainer's gate-cost frustration be bounded.
4. **With two Primaries, the mint default is index order.**
   - `PersonaRegistry.primary` returns the first `## Primary` bullet (sdlc_md.py:2720-2722), and `_resolve_persona` falls back to it (artifact.py:310-317).
   - Until US1080 lands, the order in which US1079 writes the bullets decides every default.
   - Raised by all three. Confirmed by fixture.
5. **The seat and the goal review still speak of one Primary.**
   - The project product seat says "the Primary design persona is Maya Okafor" (seats/product.md:5), and judges against "the Primary persona's" End goals (:42, :50, :89).
   - `goal_trace` counts any non-Negative persona as designed-for (sprint.py:10062).
   - `_goal_served_lines` lists every Primary's End goals with no interface (sprint.py:11131).
   - BG1066 rewrites the seat's sentence for a Secondary only, and is scheduled in neither run (D0377, D0378).
   - Raised by all three.
6. **The epic still describes the card D0379 rejected.**
   - AC1 (EP0289:25, copied from CR0648:25) says "A supplemental skill-maintainer card ... (D0373)".
   - CR0648's title cites D0373.
   - Raised by all three.
7. **The epic reproduces PER-1.**
   - All five stories read "As a Maya Okafor", including US1079, which creates the maintainer's own card.
   - Trevor first named this pattern on 2026-09-16 (consult-EP0253-EP0256:131-135).
   - Raised by all three.

## Findings verified by execution

| Finding | Verdict |
| --- | --- |
| A copy of the index with a second linked bullet under `## Primary`, and the PRD unchanged, fails `test_target_users_names_every_declared_persona` with `['Primary: Rowan Achterberg'] != []`. The registry as on main passes | CONFIRMED (fixture) |
| With two Primaries, `_resolve_persona(root, None)` returns Maya Okafor when her bullet is first and Rowan Achterberg when his is, with no warning either way | CONFIRMED (fixture) |
| Under D0373's form, a `## Supplemental` heading, the registry parses only Maya and Trevor. `--persona "Rowan Achterberg"` warns "not declared", and is refused under `--strict` (`PERSONA_ROLES`, sdlc_md.py:2696-2698) | CONFIRMED (fixture). D0379's promotion is also what makes the card visible to the tooling |
| Maya stories created since 2026-09-01: 264. Touching no shipped skill path: 39. Of those 39: 5 are wholly tools/, .githooks/ or .github/ (US0828-US0831, US0891); 9 with `changelog.d/` ignored; 12 with AGENTS.md, CONTRIBUTING.md and the other root paperwork ignored as well; 21 touch the `sdlc-studio/` workspace | CONFIRMED. Maya's count of 9 reproduced |
| All four of EP0288's stories, US1075-US1078, carry `changelog.d/`. US1075 and US1077 add CONTRIBUTING.md; US1078 adds AGENTS.md and the shipped `reference-sprint-toolchain.md` | CONFIRMED |
| Trevor: the "wholly" predicate "matches no real unit", because "every unit carries a changelog.d fragment" | OVER-CLAIMED. Five units since September match it. It matches none of EP0288's four and none of US1003-US1006, so it is confirmed for the cases that motivated the epic |
| US1003, US1004, US1005 and US1006, which delivered RPT0020's "her gates" goal (RPT0020:5), touch no shipped file | CONFIRMED |
| `outcome_problems` (test_lean_prd_refresh.py:45-62) checks only that a cited End goal number exists, so O5 citing Maya's End goal 3 (prd.md:103) passes today | CONFIRMED (Jonah) |
| Every story from US1050 to US1078 carries a `changelog.d/` fragment in its Affects. None of EP0289's five does | CONFIRMED |
| Stories naming each persona: Maya 549, Jonah 8 | CONFIRMED |
| The legacy file says it "records no Primary" (`personas.md:19`), yet calls the operator the "primary user" (`:46`) | CONFIRMED (PER-10) |
| `install.sh` ships only the skill directory, so the registry and the PRD never reach a consuming project, but the resolver does | CONFIRMED (Jonah) |
| Trevor: the maintainer is the operator who rules and signs, and there is "one human author" | OVER-CLAIMED in the letter: `git shortlog` shows 2,654 commits by Darren Benson, 8 by dependabot and 1 by one other human. CONFIRMED in substance |
| Trevor: no record exists of the goal-coverage sweep reference-persona.md requires | OVER-CLAIMED as a rule. reference-persona.md:106-110 asks for a recorded pick naming the unserved End goals only where the interface is NOT split. D0379 splits it, and states its coverage argument in one clause: "the maintainer's tooling is exactly what Maya never sees". The substance is folded in as a test of the card's End goals |
| Trevor cites his card's line 26 for per-change approval | CORRECTED: approval gates are line 25; line 26 is the corporate stack |
| The two interfaces meet in shipped code, at the push boundary's scope (`_pushed_scope`, gate.py:360) and BG1065's budget (Affects: scripts/gate.py) | CONFIRMED |
| Outside contributors use the same tooling: `enable-hooks.sh`, three hooks and the push gate (CONTRIBUTING.md:73-89) | CONFIRMED (synthesiser) |

---

## Users (Primary) Perspectives

### Maya Okafor (solo founder-engineer, Primary for the shipped skill)

**Verdict:** Concerns

"A second Primary makes me sharper, not weaker. Today my name is stamped on push-gate work I never see, so 'Maya' stops meaning the skill I install. But this epic would then write that same push-gate work onto my card as a frustration, and its 'wholly tools/' rule misses most of the stories the finding counted. Give the maintainer his own card, keep mine about the shipped skill in my own repo, and let the tooling choose a mint's default by the Interface each card declares, never by which name comes first in the index."

**Objection (or why none):**

- **US1081 would make PER-1's inflation legitimate.**
  - The last run's goal (RPT0020:5) was delivered by work that was minted as hers:
    - US1003: tools/gate_prereqs.py and tools/enable-hooks.sh;
    - US1004: .github/workflows/lint.yml;
    - US1005 and US1006: .githooks/pre-push and tools/gate_timing.py.
  - Writing "the gate cost and prerequisites frustration" (EP0289:26) onto her card turns that misattribution into her stated goal.
  - Her real cost frustration (maya card:51-52) is about the shipped gate in her own repo: `gate.py`, and the `coverage` prerequisite `verify_ac run --coverage` needs.
- **The predicate does not reach the finding.**
  - Of the 39 stories in her name since September that touch no shipped path, only 9 are wholly in the three directories, even with `changelog.d/` ignored.
  - So three of EP0288's four stories would still mint as hers. US1076 is the only exception.

**Questions:**

- Which predicate is ruled: "wholly tools/, .githooks/ or .github/", or "no shipped-skill path"? Does a mixed unit default to her?
- Does the predicate live in this project's declarations, or in the shipped `artifact.py`?
  - Hard-coded, it ships this repo's layout into hers, where `.github/` is her product's CI.
  - Her card says she owns "a single repo ... end to end" (maya card:40).
- Who repoints US1075-US1078 before review, as D0377 requires? And who repoints US1084-US1086, which were minted today in her name for the TRD's and TSD's gate sections?
- O5 is to cite "a Maya goal that says it", but none of her End goals says it (maya card:25-28). Her Experience goal does (maya card:36). Is a fifth End goal intended, and in which story?

**Conditions:**

- **The mint default follows the declared Interface, never bullet order.**
  - Any unit touching a shipped-skill path defaults to her.
  - A regression test pins that a one-Primary cast mints exactly as now.
- **The tooling predicate is project data,** not paths written into the shipped scripts.
- **Her card's changes concern the shipped skill:**
  - an Interface row;
  - "autosprint" becomes `sprint` (maya card:58; help/sprint.md:28 records the rename);
  - the sign-once step: she signs the run once, after the close;
  - a gate-cost line only if it cites a shipped command. The hooks, the gate host, the ssh keepalive and this repo's prerequisites go on the maintainer's card.
- **Her End goals keep their numbers and order.** O1-O4 cite them by number (prd.md:99-102), and so do 29 story `Serves:` lines.
- **The maintainer card is written to EP0287's standard,** so that it is not reworked in the third run.
  - It carries a boundary line: his goals never justify a change to the shipped skill on their own.
- **Before the second run's reviews,** the product seat and the seat brief say which Primary governs which interface, or a ruling says why not.

---

## Users (Secondary) Perspectives

### Jonah Reyes (team lead, brownfield adoption, Secondary)

**Verdict:** Concerns

"Splitting the interface is honest. Thirty-eight repo-only stories were never Maya's work, and I'd rather the registry said so than padded her count. But D0379 gives the maintainer an approving lens because of BG1066 while my stories stay without one, and US1080 changes the mint default in code my team installs, with no changelog fragment and no stated behaviour for a cast with one Primary. I am Secondary to Maya on the shipped skill, and now that 'the Primary' names two people, my card and the PRD have to say so."

**Objection (or why none):**

- **US1080 changes a shipped convention silently.**
  - That is the upgrade frustration on his card (jonah card:52), and it works against his End goal 4 (jonah card:29).
  - Its Affects (US1080:8) names `artifact.py`, `lib/sdlc_md.py` and `test_artifact.py`, with no changelog fragment and no `reference-persona.md`.
  - If the epic's paths (EP0289:25) are hard-coded, his team's `.github/`-only CI stories would be routed to an interface the team does not have.
  - The registry and the PRD never reach his team, because `install.sh` ships only the skill directory. The resolver change does.
- **BG1066 is fixed for the maintainer by promotion, not for him.**
  - D0379 (decisions.md:393) chooses Primary because a Secondary "would leave every repo-only story ... without an approving lens".
  - BG1066 is Open and scheduled in neither run.
  - US1082, the one story that serves him, names Maya (US1082:11).

**Questions:**

- Where does the map from Affects to interface live: a card row, config or code? With none declared, does a single-Primary cast mint exactly as it does today?
- Is `changelog.d/` part of the tooling interface?
  - If not, no well-formed unit is ever "wholly" tooling: US1076:8 carries `changelog.d/US1076.md`.
  - US1078 touches the shipped `reference-sprint-toolchain.md`, yet D0377 repoints it.
- Why is his card in US1082's Affects (US1082:8)? Rewording End goal 4 is a goal change under D0374, and should be named as one.
- Will the maintainer's End goals become PRD outcomes? `goal_trace` already accepts a persona by name (sprint.py:10045-10052), so they need not.

**Conditions:**

- **US1080:**
  - a fixture criterion that a single-Primary cast mints unchanged;
  - a two-Primary cast with no declared interfaces keeps today's behaviour and warns, never refuses;
  - the project declares the interface paths;
  - a changelog fragment and the `reference-persona.md` doc ship in the same commit.
- **His card** gains an Interface row naming the shipped skill. Line 68 keeps Maya as his Primary.
- **The Secondary headings** (index.md:11, prd.md:180) say which Primary.
- **PRD Target Users** labels the maintainer as Primary for an interface that does not ship.
- **The registry's preamble,** "who the product is *for*" (index.md:3-4), is revised to match.
- **The maintainer card:**
  - an End goal of tagging a release a consuming team can upgrade to;
  - a gate-cost frustration bounded so that a cheaper gate never cuts the release boundary (D0375);
  - a scenario that covers the forward-port.
- **BG1066** is scheduled no later than US1079, or the dependency is recorded on the epic.
- **US1082** adds an outcome for End goal 4 without rewriting that goal.

---

## Negative (anti-persona) Perspectives

### Trevor Hale (enterprise delivery manager, Negative)

**Verdict:** Concerns

"For four months you've told me a gate on every step is my want, not yours. Now the gates get a Primary of their own, so your product seat's one test for machinery, 'does it serve a persona goal', passes automatically for anything under tools/ or .githooks/. I don't object to splitting the interface. I object to drawing it by directory, ruling it into place on a seat-defect workaround, and sending it out beside a Maya card that takes the gate-cost frustration as hers."

**Objection (or why none):** each one is weighed on its evidence.

- **The second Primary switches off the product seat's machinery test.**
  - The seat pushes back when "a unit serves the machinery (a gate, a ledger, a report field) rather than a persona goal" (seats/product.md:65).
  - Once a Primary's End goals are the gate, every repo-only gate unit serves a persona goal by definition.
  - This is the pattern he named on 2026-09-16: the anti-persona's requirements wearing a Primary's name (consult-EP0253-EP0256:131-135; trevor card:25, :34).
  - *Weighed:* CONFIRMED and adopted. The remedy lies in the card's wording, not in a gate (see the load-bearing card below).
- **A directory is not an interface.**
  - RPT0020's gate goal was delivered in tools/ and .githooks/, while BG1065's gate cost lives in the shipped `scripts/gate.py`.
  - *Weighed:* CONFIRMED.
- **The "wholly" predicate matches no real unit.**
  - *Weighed:* OVER-CLAIMED, because five units since September match it. Confirmed for EP0288 and US1003-US1006.

**Questions:**

- On a unit that spans both interfaces, which Primary governs? US1078 is one. Where is that written for a reviewer to cite?
- The maintainer wants a shorter push; Maya wants "shipped means verified" (O1, prd.md:99). When the two collide, who arbitrates? Is it the same operator who is the maintainer, ruled D0379 and signs the run (AGENTS.md:88)?
- Does the mint default become order-dependent with two Primaries? `PersonaEntry` carries no Interface (sdlc_md.py:2700-2706). Answered by fixture: yes.
- Which outcome does a repo-only Sprint Goal cite with `--serves` (prd.md:94-95)? None cites the maintainer.

**Conditions:**

- **Record the goal-coverage sweep,** naming the End goals each Primary's design fails the other on.
  - *Weighed:* OVER-CLAIMED as a rule for a split interface. Folded in as a test of the card.
- **An arbitration line on both Primary cards.**
  - On a mixed unit, the shipped skill's Primary governs.
  - The maintainer's want is met in repo-only surface, never by adding a step to Maya's run.
  - *Weighed:* adopted.
- **The interface is defined by what the person touches, as a full partition.** `changelog.d/`, AGENTS.md, CONTRIBUTING.md and the `sdlc-studio/` workspace each get an owner.
  - *Weighed:* adopted in part (see Dispositions).
- **The maintainer card:**
  - End goals a unit can fail against: gate seconds, the forward-port window and prerequisites named;
  - a frustration that cites BG1065's figures;
  - a scenario in which a push is refused;
  - a statement that the maintainer is the operator, so the seat's "not the loudest voice" (seats/product.md:30, :69-71) is applied knowing it.
  - *Weighed:* adopted, except the last item, which is declined in the form asked.
- **His own card (US1081)** states three things:
  - **Sign-once:**
    - The run carries one human signature, at `sprint sign`, which refuses a principal who is a unit's author or a recorded reviewer (D0213; AGENTS.md:49, :88).
    - The signature is the Primary's control.
    - A per-unit sign-off, a second signature, or an approver on a ruling or on `--force` is his want, and is declined (trevor card:25, :48).
  - **Weighing:** an objection of his is adopted when evidence shows a Primary's End goal is harmed, as at consult-CR0526:134. It is declined when it serves only him, and it is never adopted or dismissed for being his.
  - **Scope:** he is the Negative on both interfaces.
  - *Weighed:* adopted.

---

## Summary by Group

| Group | Consulted | Support | Concerns | Oppose |
| ------- | ----------- | --------- | ---------- | -------- |
| Users (Primary) | 1 | 0 | 1 | 0 |
| Users (Secondary) | 1 | 0 | 1 | 0 |
| Negative | 1 | 0 | 1 | 0 |
| **Total** | **3** | **0** | **3** | **0** |

---

## The four questions put to the panel

### Does a second Primary dilute Maya as the design target?

No, provided the boundary follows the declared interface and the seats know about it. Yes, if it is drawn by a path list and the seat keeps a singular "the Primary".

- **Why it sharpens her:**
  - 39 of the 264 stories in Maya's name since September touch no shipped path.
  - The last signed run's goal named "her gates" for work done wholly in tools/ and .githooks/.
  - Her name currently means "whatever the agent minted", not "the skill she installs" (maya card:48-49).
- **Why it can dilute her:** the epic leaves four ways open.
  - The headings call the Primary "the design target" (index.md:6, prd.md:178).
  - The mint default follows index order (fixture).
  - The seat names a single Primary (seats/product.md:5, :42, :89).
  - US1081 puts a gate-cost line on her card.

### Do the maintainer's goals belong in the registry?

All three accept that they do, Trevor included.

- The registry is the only source that `_resolve_persona`, `goal_trace` and the product seat read.
- A card outside it, or under a Supplemental heading, is invisible to all three (fixture).

The conditions:

- the preamble (index.md:3-4), "who the product is *for*", says the registry now covers two interfaces;
- PRD Target Users names the maintainer as Primary for an interface that does not ship;
- the PRD's `## Outcomes` stays the product's, unless the operator rules otherwise (Jonah; ruling owed).

`install.sh` ships only the skill directory, so the card never reaches a consuming project. The resolver change in US1080 does.

### What must the maintainer card state to be load-bearing?

This is drawn from all three, and from the legacy section the card replaces (personas.md:196-249).

- **Quick Reference:**
  - a Cast role of Primary, matching the index (EP0287's persona-registry-role rule);
  - an Interface row naming the repository tooling: tools/, .githooks/, .github/ and the forward-port to the installed copy;
  - the machines the maintainer works across.
- **End goals, stated as outcomes a unit can fail against, never as machinery,** so that seats/product.md:65 still bites. In order, each with its evidence:
  1. A push is judged against exactly the commit pushed, in minutes the work can absorb. D0366 records 26-64 minutes locally and two low-memory kills in a week, against 634-636 seconds on devserver1.
  2. A fix landed here is in force in the installed copy the same day. Evidence: `forward-port.sh --check`, and AGENTS.md's "a fix believed shipped is in force nowhere".
  3. A release ships that a consuming team can upgrade to: the release boundary green, known issues named, the changelog complete. Evidence: D0375. Jonah's End goal 4 depends on this one.
  4. Main is never left red and unread (D0181; BG0709).
- **Frustrations, with figures:**
  - the push gate's cost (D0366, D0370);
  - the gate's 45-second budget exceeded on every run: 127 seconds locally and 143 in CI (BG1065);
  - a prerequisite found only after the suite has run (US1003, US1005);
  - a push that dies on an idle connection after the gate passed (the keepalive in AGENTS.md);
  - a scheduled job red for weeks with nobody reading it (BG1054);
  - a mirror that drifts silently.
- **A key-path scenario:** a push from the workstation is judged on the gate host, one refusal is read and acted on, then the fix is forward-ported.
- **Boundary lines:**
  - Maya is Primary for the shipped skill. A maintainer want is met in repo-only surface, never by shipped surface Maya pays for. A unit touching a shipped path is judged against Maya.
  - The interfaces meet in `gate.py` (gate.py:360; BG1065), which ships.
  - Trevor bounds both interfaces.
  - Outside contributors (CONTRIBUTING.md:73-89) are served by the same interface, and need no card of their own.
- **An Evidence section** citing ids that resolve (EP0287's persona-evidence rule). End goals are written so that a Verify line can be added later (US1039), and the third run does not have to rework the card.

### The two-Primary risks

| Risk | Where | State today | What closes it |
| --- | --- | --- | --- |
| The default persona | sdlc_md.py:2720-2722; artifact.py:310-317 | The first `## Primary` bullet wins, silently (fixture) | US1079 keeps Maya first and pins it with a test. US1080 chooses by declared interface, and warns rather than guessing when nothing matches |
| The goal trace | sprint.py:10028-10066, :11120-11145 | Any non-Negative persona counts. The goal review lists both Primaries with no interface, so a run that serves only the maintainer under Maya's name is never flagged (RPT0020:5) | The goal-review brief prints each Primary's Interface. No story in the epic does this |
| The product seat's lens | seats/product.md:5, :42, :50, :65, :80, :89; reference-consult.md:80-82 | "A Primary-persona goal" admits either Primary. A shipped unit could be approved against the maintainer's goals, and the machinery push-back stops biting on tooling | The seat judges a unit against the Primary of the interface its Affects touches. BG1066 rewrites the same sentence for a Secondary, and is in neither run |

---

## Cross-Group Analysis

### Consensus Points

- D0379's split is right, and the card belongs in the registry (all three).
- Each of the seven convergent findings above was reached by at least two personas, arguing from different goals.
- On a mixed unit, the shipped skill's Primary governs. Maya and Trevor state it; Jonah's Secondary line assumes it.

### Conflicts Identified

- **Primary vs Primary: where the two interfaces meet.**
  - The maintainer wants a cheaper push. Maya wants "shipped means verified" (O1).
  - They meet in shipped code: `gate.py`'s push-boundary scope (gate.py:360) and BG1065's budget.
  - Arbitration:
    - A unit touching a shipped path is judged against Maya. The maintainer's want is met in repo-only surface.
    - Both cards state this.
    - A collision this rule cannot settle goes to the operator, and the ruling is recorded as a decision (reference-persona.md:106-110).
- **Secondary vs the ruling's rationale.**
  - D0379 promotes the maintainer partly because the seat admits only Primaries (BG1066). That leaves Jonah's stories without an approving lens.
  - Arbitration: schedule BG1066 with or before US1079, or record the dependency. It costs Maya nothing, by Jonah's own Primary test.
- **Jonah vs Trevor on the PRD.**
  - Trevor asks which outcome a repo-only goal cites. Jonah asks that the PRD a consuming team reads keep the product's outcomes only.
  - `goal_trace` accepts a persona by name, so a repo-only goal can name the maintainer without any outcome.
  - A ruling is owed.
- **Negative vs the card's author.**
  - Trevor asks that the card say the maintainer is the operator. The substance is confirmed: 2,654 of the 2,663 commits have one author.
  - But a persona card that names a real principal stops being a persona.
  - Declined in that form. Met instead by End goals that cite evidence, and by a review of the card, by a seat that did not write it, before it becomes the approving lens.

*Arbitration:* a Buyer or Customer conflict with the Primary persona's interface is recorded here and routed elsewhere (reporting, admin surfaces, policy). Buyer goals never override the Primary's interface. With two Primaries, "the Primary" means the Primary of the interface the unit touches.

### Patterns

- **One cause, three defects.**
  - The breakdown was refined from CR0648, which was written under D0373. It was not re-read against D0379, which superseded D0373 the same day.
  - That is why AC1 says "supplemental", why US1081 gives Maya the gate cost, and why US1080 carries the CR's path list.
- **The registry half without the reader half.**
  - The epic adds a card and rows.
  - The default by interface may land a run later, and nothing makes the seat or the goal review interface-aware.
  - Epic AC1, "a card exists and is indexed", is satisfied by touch (LL0023).
- **An enumerated predicate exempts what it forgot** (LL0013, LL0043).
  - `changelog.d/` is in nearly every well-formed unit (AGENTS.md: "Ship the paperwork in the same commit").
  - A "wholly" rule that omits it almost never fires.
- **The epic spans two runs and does not say so.**
  - D0377 takes the card into the second run, "written first", with EP0288's stories repointed before review.
  - D0378 takes "the rest of CR0648" into the third.
  - Whether US1080 is in the second run is not stated. Without it, every repo-only unit minted in that run defaults by index order.
- **The five stories are a cluster, not parallel lanes.**
  - test_persona_coherence.py is in US1079, US1081 and US1083.
  - Maya's card is in US1079 and US1081.
  - index.md is in US1079 and US1083.
  - prd.md belongs in both US1079 and US1082.
- **The default applies only at mint.**
  - `_resolve_persona` takes no Affects (artifact.py:282), so a story whose Affects change at grooming keeps the persona it was minted with.
  - No persona asked for a check, and LL0056 counsels against one before the default has a measured yield.

---

## The Primary test

Each persona was asked where their want would bend the Primary's interface.

- **Jonah:**
  - He declined his own impulse to mark repo-only changelog entries "not shipped", because it would add ceremony to every unit Maya runs.
  - An optional interface-paths key is acceptable only if leaving it out keeps today's behaviour.
  - Widening the seat's lens costs Maya nothing.
- **Maya** applied the test to the maintainer. His goals never justify a change to the shipped skill on their own. The place they would bend her interface is `gate.py`'s push-boundary code, which ships.
- **Trevor:**
  - He drew his own line: one signature per run is the Primary's control, and anything finer is his want.
  - He named the risk this epic carries: a Primary whose End goals are the gate turns his requirements into a Primary's, unless those goals are written as outcomes a unit can fail against.

---

## Recommendations

1. **Re-read the breakdown against D0379 before grooming.**
   - Reword AC1: a Primary card, an Interface row on each Primary, citing D0379.
   - Retitle US1081, so the gate cost on Maya's card is the shipped gate's only.
   - Re-decide each story's Persona once US1079 lands.
   - Priority: High. Addresses concerns from Maya, Jonah and Trevor.
2. **Make US1079 land green on its own.**
   - Add `sdlc-studio/prd.md` (Target Users) to its Affects.
   - Keep Maya first in the index, pinned by a test.
   - Revise the index preamble.
   - Write the card to EP0287's standard.
   - Add the repointing of US1075-US1078 that D0377 requires before their reviews.
   - Priority: High. Addresses concerns from Maya, Jonah and Trevor.
3. **Design US1080's predicate as project data.**
   - The project declares the interface. Where nothing is declared, today's behaviour holds.
   - A shipped path means the shipped skill's Primary.
   - Paperwork paths do not decide.
   - A unit touching only the workspace names its persona.
   - An explicit `--persona` always wins.
   - Ship a changelog fragment and the `reference-persona.md` doc in the same commit.
   - Add a fixture for a single Primary, and one for two Primaries with no interfaces.
   - Priority: High. Addresses concerns from Maya, Jonah and Trevor.
4. **Close the reader half.**
   - The product seat judges a unit against the Primary of the interface it touches.
   - The goal-review brief prints each Primary's Interface.
   - Either extend BG1066 and schedule it no later than US1079, or file a unit and record the dependency.
   - Priority: High. Addresses concerns from Maya, Jonah and Trevor.
5. **Write the cards' boundaries in.**
   - the arbitration line on both Primary cards;
   - Trevor's sign-once, weighing and two-interface scope lines;
   - Jonah's "Secondary to Maya on the shipped skill";
   - Maya's End goals appended to, never renumbered.
   - Priority: Medium. Addresses concerns from Maya, Jonah and Trevor.

---

## Dispositions

Every finding is folded, filed, declined or put to the operator.

| Finding | Disposition |
| --- | --- |
| US1079's Affects omits `sdlc-studio/prd.md`, so the coherence test goes red (fixture) | FOLD: add prd.md. Target Users names the maintainer as Primary for an interface that does not ship |
| AC1 says "supplemental" and cites D0373 | FOLD: reword against D0379, with an Interface-row criterion |
| The mint default follows index order (fixture) | FOLD: US1079 keeps Maya first and pins it with a test. US1080 resolves by declared interface |
| The "wholly" predicate misses EP0288 and US1003-US1006 | FOLD into US1080: declared by the project, not hard-coded. Paperwork does not decide, a shipped path means Maya, and an explicit `--persona` wins |
| US1080 changes shipped behaviour with no changelog fragment or doc | FOLD: add `changelog.d/US1080.md` and `reference-persona.md` to its Affects, with one-Primary and two-Primary fixtures |
| US1081 puts the maintainer's gate cost on Maya's card | FOLD: split it. Maya's line cites only a shipped command; the rest goes on the maintainer card in US1079 |
| Renumbering Maya's End goals would break O1-O4 and 29 `Serves:` lines | FOLD: append only |
| O5 needs a Maya End goal that says it, and US1082 cannot edit her card | FOLD: decide at grooming whether US1081 appends End goal 5 (from maya card:36, :51-52). Declare US1082's dependency on US1081, and pin the citation literally, since `outcome_problems` checks only the number |
| Jonah's card is in US1082's Affects with no stated change | FOLD: add the outcome for End goal 4 without rewording that goal. Name any change to his card as a goal change (D0374) |
| "Secondary to whom?" | FOLD: Jonah's Interface row and the Secondary headings (index.md:11, prd.md:180) name Maya's interface |
| Trevor's card: sign-once, weighing, scope | FOLD into US1081, in Trevor's words |
| The index preamble says the registry describes the product's users | FOLD into US1079 |
| No story repoints US1075-US1078 (D0377) | FOLD: a criterion on US1079, or a planned step before their reviews, that each names the maintainer and cites one of his End goals |
| US1084-US1086 and EP0289's own stories also default to Maya | OPERATOR RULING OWED: D0377 names only EP0288's four |
| The seat and the goal review know one Primary and no interface | FILE a unit, or extend BG1066. OPERATOR RULING OWED on whether BG1066 joins the second run, since D0379's rationale rests on the seat |
| A Primary whose goals are the gate disarms seats/product.md:65 | FOLD into US1079: End goals as outcomes a unit can fail against, and a cost frustration with figures |
| The maintainer card should meet EP0287's standard | FOLD into US1079: a Cast role matching the index, an Evidence section, and End goals a Verify can attach to |
| The maintainer is the operator who rules and signs | CONFIRMED in substance and DECLINED in the form asked. Met by evidence-cited End goals and an independent review of US1079 |
| A recorded goal-coverage sweep | OVER-CLAIMED as a rule for a split interface. Folded in as a test: each maintainer End goal is one Maya's design does not serve |
| A full ownership partition of every path | FOLD in part: recommendation 3's rule gives every unit an owner without enumerating paths |
| A maintainer outcome in the PRD | OPERATOR RULING OWED. Recommended: none in `## Outcomes`; a repo-only goal names the maintainer, which `goal_trace` accepts |
| The epic does not say which run takes which story | FOLD: record it on the epic. OPERATOR RULING OWED on whether US1080 joins the second run |
| None of the five stories carries a changelog fragment | FOLD: add one to each Affects |
| Shared files make the five stories a cluster | FOLD: declare the order: US1079 first, then US1080 and US1081, then US1082, then US1083 |
| Placeholder "So that" lines, and Persona Maya on all five | FOLD at grooming |
| The legacy personas.md calls the operator "primary user" (:46), and its maintainer section is now duplicated | FOLD into US1083: the banner's contradiction includes :46, and the maintainer section points at the new card |
| Outside contributors share the interface | FOLD into US1079: one footer line, and no card of their own |
| A per-unit sign-off, a second signature, an approver on a ruling or on `--force` | DECLINED: serves only the Negative persona |

---

## Next Steps

**Concerns raised.**

- No persona opposes D0379. All three ask for the breakdown to be re-read against it before grooming.
- Recommendations 1 to 3 are owed before US1079 enters the second run.

Four rulings are owed to the operator:

1. whether US1080 joins the second run;
2. whether BG1066 joins it, or the seat's two-Primary wording gets a unit of its own;
3. whether US1084-US1086 and EP0289's own stories are repointed;
4. whether the maintainer gets a PRD outcome.

---

*Generated by SDLC Studio `/sdlc-studio consult stakeholders`*
