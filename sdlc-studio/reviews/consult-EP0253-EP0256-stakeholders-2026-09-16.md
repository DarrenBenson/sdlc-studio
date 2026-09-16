# Stakeholder Review: the next run's four epics (EP0253, EP0254, EP0255, EP0256)

> **Date:** 2026-09-16
> **Artefacts:** EP0253 (CR0586), EP0254 (CR0585), EP0255 (RFC0059), EP0256 (RFC0058), stories US0824-US0842
> **Mode:** ADVISORY under D0210 - a persona verdict INFORMS and holds no gate, and an unanswered Reject is reported at the close. The operator rules.
> **Run at:** refine, before grooming, under D0210's ruling that a consult belongs where feedback becomes criteria rather than rework
> **Personas:** each consulted in a fresh context, one subagent per persona, with the objection quota in force

## Verdicts

| Persona | Perspective | Verdict |
| --- | --- | --- |
| Maya Okafor | solo founder-engineer, Primary | Concerns |
| Jonah Reyes | team lead, brownfield adoption, Secondary | Concerns |
| Trevor Hale | enterprise delivery manager, Negative | Concerns |

No persona accepted the batch as scoped. Two independently rejected EP0253's shape, from
different arguments.

## Where the three converged, independently

Convergence is the signal a consult exists to produce: three fresh contexts, no shared state.

1. **No story stamps the token meter, so the report ships its headline cost row hollow.** All
   three raised it. RFC0059 states in its own text that a report printing unknown in that row
   every run is worse than no report, and D3 already ruled the attribution run-level and
   cheap. The authoring session dropped it from the epic.
2. **The seal is a convention, not a transaction.** US0833 writes a fingerprint and nothing in
   the batch ever reads it, so a report stays signed while the tree moves. RFC0059's option E
   has two halves and only the first is in the batch.
3. **The narrowing may miss the defect it was built for.** `module-alone` exists because a
   module passed only when a sibling imported a name first. That coupling has no import edge,
   so "changed modules plus their importers" can select everything except the victim.
4. **EP0254 ships to nobody outside this repository.** Every file in its four stories is
   `tools/` or `.github/`, which AGENTS.md calls repo-only and not shipped.

## Findings verified by execution

Claims were checked rather than taken:

| Finding | Verdict |
| --- | --- |
| `scripts/consult.py` does not exist, so US0840 and US0842 are sized as field additions when they build the machinery | CONFIRMED |
| EP0255 and EP0256 carry no epic-level acceptance criteria, unlike EP0253 and EP0254 | CONFIRMED |
| `gate.py:3881` reads `at_boundary = resolve_boundary(args) in ("push", "release")`, so narrowing the push boundary narrows release too | CONFIRMED |
| US0826's `Affects` names `tools/verify-corpus.sh`, which belongs to EP0254, putting the epics in needless file contention | CONFIRMED |
| Trevor: `module-alone` runs 131 of 133 with `test_gate` and `test_rehearse_release` both serial | OVER-CLAIMED - the measured lane line reads 132 parallel on 16 workers, 1 serial (`test_rehearse_release`); `test_gate` is in the parallel phase |
| Trevor: the lane is already parallel, so narrowing the selection targets the small part and the expected saving is stated nowhere | CONFIRMED in substance - the parallel phase is bounded by its slowest module, and EP0253's own delivery touches `gate.py` |

## Objections carried, by epic

### EP0253 - the narrowed push lane

- No acceptance criterion states what the push gate must COST after this lands, so it can be
  delivered in full and still leave a ten-minute push (Maya, Trevor).
- The selection runs along the import graph while the founding defect does not (all three).
- A weekly sweep that goes red reaches nobody, which is BG0653's exact shape, recorded in this
  repository's own AGENTS.md as three weeks red and unread (Jonah, Trevor).
- The selection names no base ref, so with concurrent authors a helper change and a dependent
  module can land in separate pushes covered by neither (Jonah).
- One predicate serves both boundaries, so a release cut silently gets the narrowed lane
  unless a story forbids it (Jonah).
- US0827's miss ledger has no threshold at which anything happens, making it a third
  permanent advisory instrument beside `claim-drift` and `revert-check` (Maya, Trevor).

### EP0254 - sharding the corpus lane

- No criterion proves the sharded VERDICTS equal the serial ones. Cold shard checkouts flip
  any criterion that depended on state an earlier one left behind, and the cheapest response
  to the resulting red is to move the baseline (Trevor).
- A matrix with fewer entries than the partitioner's N drops a slice of the corpus while
  every criterion is still ASSIGNED to exactly one shard: assignment is not execution (Trevor).
- Wall clock is recorded and billed runner minutes are not, so the lane trades a visible cost
  for an invisible one (Jonah).
- The corpus grows with every Done story, so sharding buys latency once with no cap, no
  subsetting by touched `Affects`, and no trigger for revisiting N (Jonah, Maya).

### EP0255 - the derived report and the seal

- No story stamps the run-level token meter (all three).
- Nothing reads the fingerprint, so the transaction is ordering advice (all three).
- No acceptance criterion says `sprint.py sign` inherits `critic.py`'s refusal of a principal
  the authoring session controls, which is CR0571 returning in a new command (Trevor).
- Five of RFC0059's seven decisions are open, four of them load-bearing here: the report's id
  and location, what invalidates a signature, whether the report absorbs the handoff, and
  retention. Decomposed, they get invented during delivery (Trevor).
- The report's stakeholder section reads an artefact schema EP0256 has not yet defined (Maya).
- The run-level total must name its session coverage: this run was closed across sessions, so
  an unqualified total is a partial one (Trevor).

### EP0256 - stakeholder consults at refine

- The consult runs inside `refine.py`, the session that just wrote the stories, with no
  fresh-context provenance field of the kind `critic record` already demands. Without it the
  epic builds a machine for rubber-stamping at scale (Trevor).
- The trigger has no report-only mode, so a brownfield adopter learns whether it over-fires
  across live delivery. `claim-drift` and `revert-check` both ship advisory while their yield
  is measured (Jonah, Maya).
- The owed list is read at the close, the most expensive moment, in an epic titled "while it
  is still cheap to act on". Print it at `sprint plan`, refusing nothing (Trevor).
- Persona validity (D5) is open, so the yield metric cannot separate "consults work" from
  "these three personas were well written" (Maya).
- Anti-persona findings should be counted separately in the yield, or a structurally
  overruled Reject depresses the number the requirement is judged on (Trevor).
- Nothing says what `refine` does in a project with no personas authored, which is every
  project's first run. It must degrade to a recorded skip, never a refusal (Jonah).

## What each persona would deliver first

| Persona | Order | Argument |
| --- | --- | --- |
| Maya | EP0253, EP0255, EP0256, trimmed EP0254 | the gate saving compounds across every push in the same sprint |
| Jonah | EP0255, EP0256, EP0253, EP0254 | the report must exist before you narrow the gate it measures, or nothing can tell you whether the narrowing raised the failure rate |
| Trevor | EP0254, EP0255 (split only), EP0256, EP0253 last and only if measured | EP0253 is the only epic of the four that REMOVES a control rather than adding one |

## The Primary test

Each persona was required to say where their want would bend the Primary's interface.

- The weekly sweep's owner and notification: not built as alerting. One machine-readable
  field in run state, one line in `status` and one in the report's ship guardrail. Maya pays
  nothing; an adopting team wires the same field into what it already pages on (Jonah).
- Who may sign: default the principal to the single configured operator so `sign` asks Maya
  nothing, and make multi-principal config an adopting team sets (Jonah).
- A report-only consult mode: claimed as the team's want, then withdrawn as the Primary's too,
  since a trigger never measured against a real backlog cannot be said to earn its keep
  (Jonah, Maya).
- Signing for a third party: git already signs. Write a signed tag or commit trailer when a
  key is present, and record plainly that it was unsigned when none is. Costs Maya nothing
  (Trevor).
- Trevor's own reflection, recorded because it is the sharpest thing in the consult: every
  story in the batch carries `Persona: Maya Okafor`, including those that are plainly not
  hers. A fingerprint, a re-open path and a notion of what invalidates a seal are the
  anti-persona's requirements wearing the Primary's name, which is how ceremony enters a
  product that says it excludes it.

## Dispositions

Every finding is folded, filed or declined. Nothing is left to rot.

| Finding | Disposition |
| --- | --- |
| No token-meter story in EP0255 | FOLD: add a story to EP0255 stamping the meter at run open and report time, naming session coverage |
| Fingerprint written, never read | FOLD: add the INVALIDATED read to EP0255 in the same batch |
| `sign` must inherit the author-controlled principal refusal | FOLD: an acceptance criterion on the sign story |
| EP0255 and EP0256 carry no epic-level acceptance criteria | FOLD: author them before planning |
| US0840 and US0842 declare a script that does not exist | FOLD: re-point `Affects` and re-size, or split the machinery out as its own story |
| US0826's `Affects` names another epic's file | FOLD: correct it |
| EP0253 states no expected saving | FOLD: measure first with a 2-point per-module timing story, which may retire the epic |
| The narrowing runs along the import graph, missing the founding defect | FOLD: the criteria must state a test-to-production, transitive graph, or the epic loses its yield |
| One predicate narrows release as well as push | FOLD: pin the full sweep at the release boundary |
| A red weekly sweep reaches nobody | FOLD: a run-state field surfaced in `status` and the report |
| Sharded verdicts never proved equal to serial | FOLD: a dual-run equivalence criterion on one real commit |
| Assignment is not execution | FOLD: the collector asserts exactly N reports from a shared source of truth |
| Consult with no fresh-context provenance | FOLD: a provenance field, mirroring `critic record --brief` |
| No report-only mode for the consult trigger | FOLD: ship advisory, measure yield, gate later |
| The owed list surfaces only at the close | FOLD: print it at `sprint plan`, refusing nothing |
| No personas authored in a project | FOLD: a recorded skip, never a refusal |
| Billed CI minutes unrecorded | FILE: a CR against EP0254's measurement |
| The corpus grows without cap or subsetting | FILE: the question CR0585 makes affordable rather than answers |
| Nothing in the batch strengthens detection while the change failure rate is 33% | OPERATOR RULING OWED: three of four epics make gates cheaper or reporting better, and the fourth removes a control |
| The blanket ruling over 76 findings is a count, not a control | OPERATOR RULING OWED: name the predicate, group the carried findings by it, list violations by id |
| Persona validity (D5) open while yield is measured on it | OPERATOR RULING OWED at refine |
| Anti-persona findings depress the yield they are measured by | FOLD: count them separately |
| Cost in money and hours rather than tokens | DECLINED for this batch: the rate card is a project setting, not a report defect - revisit when the token figure is real |
