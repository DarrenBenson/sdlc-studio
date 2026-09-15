# Stakeholder Review: CR0526 - US0625, US0626, US0627, US0628

**Consulted:** 2026-09-15
**Artefact:** sdlc-studio/stories/US0625-*.md, US0626-*.md, US0627-*.md, US0628-*.md (context: CR0526, EP0206, D0193, D0194, D0196, D0197)
**Stakeholders Consulted:** 3
**Provisional (unverified) cards:** none. `persona_gen.py classify --root .` reads only `personas/seats/`, so it did not grade these cards. By `personas/index.md` history, Maya and Trevor were seeded by the operator (2026-06-21), and Jonah was written by an agent under operator direction (2026-07-16). None is a generated-pristine card, but Jonah's has the least human verification.
**Mode:** ADVISORY, folded into delivery. It is not a gate. Verdicts were **not** recorded through `critic.py` / `ledger.py` because this run was read-only on the repo.
**Method:**

- Each persona ran as an isolated subagent in a fresh context, per `reference-consult.md`.
- Cited tree evidence was re-checked by the synthesiser. The one correction is noted inline.
- The cards declare a cast role, not a `<!-- stakeholder: -->` type. Groups follow the cast role (legacy Users grouping, split Primary and Secondary).

---

## Users (Primary) Perspectives

### Maya Okafor (solo founder-engineer, Primary)

**Verdict:** Concerns

"I want this. The last time a sprint 'closed', 19 rejected units sat in Review and were then moved to Ready, and nothing stopped it. One predicate that close and stop both read, plus a `Findings-filed-to` line on the closed story, tells me the true state after I've been away. What worries me is that the hold is answered by a markdown row the agent can write itself. That's a sign I never wrote, not a gate."

**Objection (or why none):** US0626 AC3 lets a `not-stop-ship`, `accepted-risk` or `deferred` row in the carried table answer an In Progress unit. Nothing in the four stories checks who wrote that row:

- `retro.carried_issues` only requires the `Ruled by` cell to be non-empty (`scripts/retro.py:296-300`).
- Across every retro there are 1,081 valid rulings. About 124 name the operator. The rest name the authoring session, the agent, a delivery session or a seat. Re-counted by the synthesiser through `retro.carried_issues`.
- All 46 rows in RETRO0116 say "Claude Opus 5". That includes deferring CR0526 itself (`RETRO0116:111`).
- `critic signoff` already refuses a principal the authoring session controls. The stop-ship table does not.

A second, smaller objection: a rejected unit can leave the batch as Superseded, Won't Implement or Won't Fix with only a printed warning (US0627 AC12, and US0626's abandoned exemption). While I'm away, that warning just scrolls past.

**Questions:**

- When the close refuses, what exactly do I run? Is it a hand-edited table row with my name and today's date? Is there a bulk form for twenty units?
- If every non-stop-ship finding becomes a bug, what stops the backlog filling with reviewer nits? Can several findings be filed to one bug?
- Does the filed bug point back to the story and REJECT it came from? Or does only the story point to the bug? (`file_finding.py` stamps only `Raised-in-batch`, around line 1513.)
- At the close, where do I see every unit that was abandoned or `--force`d past a REJECT during the run?

**Conditions:**

- The close can tell a ruling I made from one the agent proposed. If that needs a new unit, file it now and name it in the retro. Don't let US0625's doctrine claim something no gate enforces.
- Units abandoned or forced over a REJECT appear in the close report or handoff, not only in transition output.

---

## Users (Secondary) Perspectives

### Jonah Reyes (team lead, brownfield adoption, Secondary)

**Verdict:** Concerns

"The rule is right, and the close failure it answers is real: RUN-01KYZKY5 left 19 units open twice and nothing refused it. The shared predicate means my team can't argue about whether the close or `stop` is 'the real one'. But two things here hurt a three-person team with agents on an inherited repo. The ruling that releases the close can be written by anyone. And the new transition gate switches on for the whole backlog on the day of the upgrade."

**Objection (or why none):**

- **Anyone can write the ruling.** Same finding as Maya's: the ruler is unchecked (`retro.py:296-300`), and US0625 AC4 states "the operator or a recorded delegate" only in prose. `critic signoff` holds a delegate to a separate trust boundary. The carried table does not.
- **US0627 has no adoption switch.** Every neighbouring gate has a dated cutoff: `review.two_role_after`, `review.test_plan_after` and `review.line_coverage_after` (`transition.py` around lines 213, 906, 2183-2197). US0627 has none.
  - In this repo, 16 bugs at Fixed carry an unanswered delivery REJECT (US0627 AC2). Every one of them will refuse Verified or Closed the moment this lands.
  - On an upgraded consuming repo, the only way through is `--force` or a filing sweep nobody scheduled.
  - That is "an upgrade that silently changes conventions mid-flight".

**Questions:**

- On a team of three, who is "the operator"? Where is a delegate "recorded"?
- Will `migrate`, or the upgrade notes, tell me how many units will refuse their delivered terminal, before I take the upgrade?
- When my developer hits `unanswered delivery REJECT`, does the message give the way out (`critic.py repair` with `filed:`, a same-brief re-review, `--force`), or only the reviewer and the date?
- Is `Findings-filed-to` documented anywhere a human reader or `validate` would find it?

**Conditions:**

- A carried-table ruler is checked on the same terms as sign-off. Or the release notes state plainly that it is not checked yet, and a unit is filed against that.
- US0627 ships behind a cutoff key, or ships with a changelog or `migrate` disclosure giving the count of units it will refuse.

---

## Negative (anti-persona) Perspectives

### Trevor Hale (enterprise delivery manager, Negative)

**Verdict:** Reject

"You're telling me a sprint can't end with anything open unless somebody rules on it. Your own retros show who that somebody is: the machine. That isn't a gate. It's a form the thing being gated fills in about itself, and I can't take that to a steering board. And `--force` still walks straight round the REJECT guard, leaving a note afterwards instead of an approval."

**Objection (or why none):**

- The hold opens itself. US0626 AC3 answers a unit on any ruling, whoever made it. Rulers on record include "sdlc-studio (agent)" (RETRO0112), "Claude Fable 5.1" (RETRO0115) and "Claude Opus 5" deferring CR0526 itself (`RETRO0116:111`).
- `--force` (US0627 AC13) waives the guard with no approver.
- Nothing rolls known defects up across releases: `release_cut.py` has no carried-table reader.

**Questions:**

- Who signs a `not-stop-ship` row when the operator isn't there? Does the close refuse a row the authoring session wrote?
- `accepted-risk` has no owner, no expiry and no review date. Whose risk is it, and until when?
- Where is the list of every defect that shipped under a `not-stop-ship` ruling since the last tag?
- Who may use `--force` on US0627's guard, and who reviews those overrides afterwards?

**Conditions:**

- A carried-table row counts as a ruling only if its ruler is outside the authoring session.
- `--force` names an approver.
- Carried rulings roll up into the release notes.
- `accepted-risk` carries an owner and an expiry.

---

## Summary by Group

| Group | Consulted | Approve | Concerns | Reject |
| ------- | ----------- | --------- | ---------- | -------- |
| Users (Primary) | 1 | 0 | 1 | 0 |
| Users (Secondary) | 1 | 0 | 1 | 0 |
| Negative | 1 | 0 | 0 | 1 |
| **Total** | **3** | **0** | **2** | **1** |

---

## Cross-Group Analysis

### Consensus Points

- **What all three value.** A rejection can no longer be outlived by the unit that earned it (US0627), and the closed unit names where its findings went (US0628). Maya and Jonah both credit the single predicate shared by close and stop (US0626 AC5).
- **The same gap, found independently by all three.** The stop-ship ruler is unchecked, so D0193's hold can be released by the session it holds.
  - US0625 will write "the operator or a recorded delegate" into the doctrine with no gate behind it. That is the LL0027 shape, and here it is also the exit from the gate this CR builds.
  - The evidence is in the tree, as set out under Maya's objection.
- **Refusals should name the way out.** Maya and Jonah both asked what to run when US0626 or US0627 refuses. The criteria pin which ids appear, not the remedy.

### Conflicts Identified

- **Primary vs Negative (autonomy vs a human gate).**
  - Trevor wants an approver on every `--force` and every ruling, plus owners and expiry on `accepted-risk` and a portfolio view.
  - Maya wants to rule once, quickly, at the close, and otherwise step away.
  - Arbitration: decline Trevor's approval chain, approver on `--force`, risk owner and expiry, and any board. AC13's recorded override is the Primary's escape hatch.
  - The ruler-identity check is **not** a Trevor-only want. D0194's own title is "the operator rules at the close" (`decisions.md:208`), and whether a defect stops a release is exactly Maya's call. It can be met with one attribution check that reuses `critic signoff`'s principal predicate, with no GUI and no chain.
- **Primary vs Secondary (unconditional guard vs incremental adoption).**
  - Jonah wants US0627 behind a dated cutoff.
  - A cutoff that exempts old REJECTs re-creates what CR0526 exists to stop, and silently grandfathers them, which is CR0497's complaint.
  - Arbitration: serve Jonah with disclosure, not exemption. The changelog, and ideally `migrate`, should count the units that will refuse and name the exits. Only add a cutoff key if the operator rules for one.
- **Who rules vs ceremony (inside the Primary).**
  - A checked ruler means the operator rules every carried row. RETRO0116 has 46 of them.
  - Without a bulk ruling command, the fix for the hold turns the close into table editing, which is the "ceremony becomes the work" frustration (CR0507's territory).

*Arbitration:* when a Buyer or Customer conflicts with the Primary persona's interface, the conflict is recorded here and routed elsewhere (reporting, admin surfaces, policy). Buyer goals never override the Primary's interface.

### Patterns

- The four stories are strong on the **refusal** half: which units hold, which answer, and one reader.
- They are thin on the **exit** half:
  - who may answer (ruler identity)
  - how to answer cheaply (bulk ruling, remedy text)
  - what an answer leaves visible afterwards (abandoned or forced units, back-links, release roll-up)
- Every persona's pushback lands on the exit half, not on the criteria.
- Title vs delivery: CR0526 promises a sprint that "ends with nothing open", but D0193's form delivers a sprint that ends with nothing **unanswered**. A unit that is ruled, dropped or parked stays open into the next plan. That is defensible, but the doctrine should say which one it means.
- Jonah's worry about hand edits bypassing `transition.py` is partly met already. `conformance.critiqued_unmet` enforces the verdict half for a Done story (`conformance.py:437-447`). Its reach to bugs was not verified.

---

## Recommendations

1. **Gate the stop-ship ruler, or disclose that it is ungated.**
   - Reuse `critic signoff`'s principal-control predicate on the carried table's `Ruled by` cell.
   - Until then, release notes say the doctrine's who-rules claim is not enforced.
   - Priority: High. Addresses concerns from: Maya, Jonah, Trevor.
2. **Name the exits in every new refusal (US0626, US0627), within the approved criteria.**
   - Priority: High. Addresses concerns from: Maya, Jonah.
3. **Disclose the upgrade impact of US0627 and of US0626 AC6 (a waiver no longer answers a unit).**
   - Priority: Medium. Addresses concerns from: Jonah.
4. **Make the answer cheap and visible afterwards.**
   - A bulk ruling command.
   - Abandoned or forced-past-REJECT units shown at the close.
   - A back-link from the filed bug to its source.
   - A roll-up of rulings since the last tag.
   - Priority: Medium. Addresses concerns from: Maya, Trevor (the roll-up only).

---

## Actionable for delivery

### A. Can be folded into the four stories' delivery WITHOUT changing their approved criteria

**Wording traps for any US0625 doctrine edit.** Any added sentence in the `{#stop-ship}` passage must avoid all of the following:

- **Recording phrasing.** No `is|are|be` + `recorded|stored|kept|logged`, and no `live in` / `lives in`. AC3 counts exactly one recording sentence, so "whose delegation is recorded" breaks it.
- **Other-store terms.** None of `ledger`, `decisions.md`, `decision log`, `handoff`, `LATEST.md`, `charter` (AC3's vocabulary check).
- **A second `propos` + `not a ruling` sentence.** It would satisfy AC4's probe after the reviewer-proposal sentence is deleted, so AC4's mutant row "delete the sentence denying a reviewer's proposal the force of a ruling" would survive.
  - The Trevor seat's suggested sentence, "a row ruled by the authoring agent is a proposal, not a ruling", has exactly this defect. Reword it or leave it out.
- **Unit, CR or decision ids.** `lint-style.sh` refuses internal provenance tags in consuming-facing `reference-*.md`, so the doctrine cannot cite the candidate below. Put that disclosure in the changelog.

1. **US0625, the who-rules sentence.** Qualify the delegate on sign-off's own terms, e.g. "the operator, or a recorded delegate in a separate trust boundary, never the session that did the work". This mirrors `reference-sprint.md:140-141`. It still carries `the operator` and `or a recorded delegate` for AC4, and keeps clear of the traps above.
2. **US0625, scope wording.** State D0193's actual promise: a sprint ends with nothing *unanswered*. A unit ruled, dropped with a reason, or parked stays open and carries into the next plan. This stops "ends with nothing open" overpromising.
3. **US0625, bug-inflation wording.** Add a separate sentence saying several findings may be filed to one artefact. `critic.record_repair` checks only that each filed id resolves (`critic.py:1279-1285`), so a shared id is accepted. Check it against AC1's filing-sentence probe before adding it.
4. **US0626, the refusal's exits.**
   - After the ids, name the ways out:
     - finish the unit
     - file its findings with `critic.py repair` (`filed:`)
     - rule it in the named retro's `## Known issues carried`
     - `sprint.py batch drop --reason`, and say this one answers only a unit with no standing REJECT (AC5's US0117)
   - For `ruling unreadable` (AC8), say which run id the retro must carry. For `adversarial pass owed`, name `critic.py brief --unit <id>`.
   - Put this on a **separate line**, or keep it free of other unit ids. AC5 compares the ids on the `known-issues:` line with a literal set.
5. **US0626, who answered.** If the ruler of each answering row is shown, so a self-ruled release is visible at the close, print it on a **separate advisory line**, never the `known-issues:` line. Answered ids on that line would break AC5's set equality.
6. **US0627, the refusal's exits.**
   - Append the ways out: `critic.py repair` per finding (`filed:` to an existing artefact, or `fixed:`), a same-brief independent re-review, or `--force` (named in `Forced-override`).
   - Say outright that a carried-table ruling does not discharge the REJECT (AC11). That pre-empts the most likely wrong move.
   - In AC12's warning, add that the REJECT stays unanswered and the abandonment is the operator's call.
7. **US0628, the Revision History row.** The closing transition's Revision History row can name the filed ids too. The detector reads only the metadata line, so this is harmless, and it gives a reader of the history the pointer as well.
8. **Changelog fragments (US0626, US0627, US0625).** State:
   - US0627 applies to the existing backlog with **no cutoff**. In this repo, 16 bugs at Fixed will refuse Verified or Closed. Give the exits.
   - A standing `rule:sprint-checklist:known-issues` waiver **no longer** answers an unfinished unit (US0626 AC6). A project that relied on one will see its next close refuse.
   - The carried table's `Ruled by` cell is **not** checked against the doctrine's who-rules sentence. That is the honest disclosure until candidate N1 lands.

### B. Would need a new unit (candidate findings: NOT filed)

- **N1. The carried-table ruler is not principal-checked, so D0193's hold is self-releasable.**
  - `retro.carried_issues` accepts any non-empty `Ruled by` (`retro.py:296-300`), and US0626 AC3 answers a unit on any ruling.
  - About 124 of 1,081 valid rulings name the operator.
  - Remedy: treat a row whose ruler is in the authoring session's trust boundary as a proposal (UNRULED), reusing `critic signoff`'s principal predicate.
  - This conflicts with US0626 AC3 as approved, so it needs an operator ruling against D0194 on how an unattended close proceeds. Under D0194's "the operator rules at the close", it would hold at the checklist until the operator rules.
  - The team case, "who is the operator on a team of three", belongs in the same design.
  - Suggested severity: High for the Primary.
- **N2. A bulk ruling command,** e.g. `retro.py rule --retro RETRO#### --ruling not-stop-ship --by <principal> ID...`, optionally pre-filling reviewers' proposed rulings for one-pass acceptance. Without it, N1 turns every close into editing dozens of table rows. Related to CR0507.
- **N3. An adoption report for US0627.** Neither `migrate` nor the upgrade path counts the units the new guard will refuse. Unlike the `review.*_after` gates, there is no cutoff key.
  - Preferred remedy: a report line (CR0497's principle, that nothing is forgiven silently).
  - A dated key only if the operator rules for one.
- **N4. Abandoned or forced units at the close.** List units abandoned (Won't Implement, Superseded, Won't Fix) or `--force`d past an unanswered delivery REJECT within the run's window, in the close report or handoff. US0627 AC12 only prints. US0823 AC2 covers `stop --force`, not transition-level forces.
- **N5. A back-link on the filed artefact.** A structured field naming the unit and REJECT the artefact discharges: the reverse of US0628's line. `file_finding` stamps only `Raised-in-batch`.
- **N6. A release roll-up.** `release_cut` lists carried `not-stop-ship` and `accepted-risk` ids since the previous tag, as plain text. It has no carried-table reader today. This serves Maya's "what shipped" and the non-declined half of Trevor's ask.
- **N7. Visibility of `Findings-filed-to`.** Document it where metadata fields are catalogued. Let `status` and the sprint report distinguish "Done, findings filed to X" from a clean Done. Maya and Trevor both read a bare Done over a REJECT as overstated.

**Declined (serve only the Negative persona):**

- an approver on `--force`
- an approval chain per ruling
- an owner and expiry on `accepted-risk`
- any board or portfolio view

---

*Generated by SDLC Studio `/sdlc-studio consult stakeholders`*
