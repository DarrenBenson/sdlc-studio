# The Mill, Not the Engine

## Running a full engineering discipline through the AI coding agent you already have

**An SDLC Studio white paper · v4.0 · July 2026**

---

## At a glance

Five findings, each expanded in the paper and each traceable to shipped behaviour or
published measurement (the [claims register](#claims-register) at the end maps every
one to its evidence):

1. **The bottleneck in AI-assisted delivery is procedural, not technical.** Knowing
   what to build and proving it was built are the constraints; faster code generation
   attacks neither. The industry's own research agrees: aggressive AI adoption has
   correlated with *worse* delivery outcomes, and most enterprise AI pilots extract no
   measurable value. (Sections 1-2.)
2. **What you enforce matters more than what you spend.** In our benchmark,
   mandating the planning pass took a mid-tier model from five-in-five escapes
   (process left to its judgement) to one in five, and a premium model from
   three-in-three to zero - at 7-18% more tokens than no process at all. The
   premium model *without* the process shipped the defect every run at a higher
   price than the governed mid-tier: at that tier, buying the bigger model was
   measurably worse value than enforcing the discipline. (Section 4.)
3. **Judgement-gated process is not process.** When engagement with the discipline
   was left to the model's own judgement, base models skipped it precisely on the
   tasks that needed it, and performed no better than no process at all. SDLC Studio
   v4 therefore ships the engagement floor as a default rule, not a recommendation. (Section 4.)
4. **The proof is the product.** Every unit of work carries its requirements, its
   executable acceptance criteria, its verification results, and an independent
   review verdict signed by a reviewer who is mechanically prevented from being the
   author. This is the audit trail a change-approval board accepts, produced as a
   by-product of delivery rather than as an afterthought. (Sections 7-8.)
5. **The team is grown from your project, not shipped to it.** v4 generates named
   working seats and stakeholder panels from your codebase and requirements, on Alan
   Cooper's goal-directed method, so the reviewer who signs off payments code is
   paranoid about idempotency rather than generically diligent. (Section 5.)

**The thesis in one sentence:** the value of industrialised software delivery was
never the machine but the mill - the organisation of specification, evidence, and
independent review around the machine - and SDLC Studio is a mill you can install,
as an open-format agent skill, into the coding agent you already run.

**Who should read this:** engineering leaders evaluating agentic delivery; platform
and compliance owners who must answer for what agents ship; teams whose AI pilots
produced demos that could not survive scrutiny.

---

## 1. The problem is procedural, not technical

Every experienced engineering leader already knows what good delivery looks like:
requirements written down, acceptance criteria before code, traceability from intent
to implementation, independent review, a definition of done that means done. Almost
no team sustains it, because every step spends the most expensive currency there is -
engineer attention. Under deadline pressure the criteria thin out, the review becomes
a skim, and the spec goes stale the week it is written. This is not a failure of
individuals; it is the predictable economics of hand-maintained discipline.

AI coding made this worse before it made it better. Prompt-and-hope development
produces a demo quickly, but the intent lives only in a chat that scrolls away and
nothing checks the result against what was asked. The industry's correction -
spec-driven development - writes intent down first, which is a real step up. But the
spec is prose the agent produced and is then *trusted* to honour, and nothing
recomputes whether code and documents still agree ten changes later. Trust-based
process decays under pressure whether the executor is carbon or silicon.

The project's design philosophy, published in its author's Real World Engineering
essays, states the constraint plainly: "the bottleneck was never typing speed. It
was, and remains, knowing what to build and being able to prove it worked." The
essays' industrial analogy gives this paper its title. At Cromford it was not any
single machine that changed the economics of cotton; it was the mill - the
organisation of machines, flow, and accountability around them. "The code is the
cloth. The organisation around it is where the money is." A steam engine in every
cottage made the old work a little faster; building the mill was the revolution.

Two consequences follow, and SDLC Studio is built on both. **The specification
becomes the durable artefact and code becomes disposable output** - so the system's
centre of gravity is the spec, the acceptance criteria, and the proof, not the diff.
And **the human stays in the lead, not merely in the loop**: of the available
futures - full automation, humans rubber-stamping machines, humans directing them -
only the third survives contact with accountability. The 2024 DORA report's finding
that aggressive AI adoption correlated with worse throughput and stability is what
the first two futures look like from the outside.

In 2026 we measured the procedural bottleneck directly, on the current model
generation, and found it alive and well. Section 4 gives the numbers.

## 2. The layer nobody governs

The enterprise agentic-SDLC literature of 2025-26 has converged, with striking
unanimity, on a diagnosis this paper shares: **the constraint is governance, not
model capability.** A platform-engineering research paper puts it as constraining
probabilistic agents within deterministic guardrails, and observes that failures
will come from governance structures, not bad models. A consultancy's agentic-SDLC
paper argues the bottleneck is deciding whether work is ready to move, not writing
code. An AI-systems playbook finds pilots fail on system design rather than model
choice. A developer-productivity guide insists automation does not equal autonomy.
We agree with all of it.

Then each of them governs a different layer. Others argue for governing the
**pipeline**: declarative CI/CD with policy-as-code and automated rollback. Some
put the boundary at the **workspace**: identity, sandboxes, and network controls
around the agent's environment. Others again would govern the **organisation**:
platform teams, metrics reviews, new collaboration norms. And a fourth school
governs the **AI product itself**: retrieval, context, and evaluation harnesses. Each of
these is real and useful, and none of them is this paper's subject, because every
one of them leaves a gap: they constrain what an agent may *touch* and how its
output *moves*, but not whether the work is *right*.

Correctness lives in a layer none of them govern: **the artefact layer** - the
requirement, the acceptance criterion, the test that proves it, the review that
attests to it, and the traceable chain between them. A workspace boundary cannot
tell you a quiet-hours rule was silently violated by a feature that passed every
pipeline stage. Only an acceptance criterion derived from the specification can -
and only if something forces it to exist and runs it.

That is the position SDLC Studio occupies: deterministic, mechanical governance of
the artefact layer, inside whichever coding agent and pipeline you already run. It
composes with workspace and pipeline governance rather than competing with them.

One more difference of register matters. The genre's evidence is asserted: ship
multiples, productivity percentages, and maturity-curve promises appear without
methodology, sample sizes, or raw data - and some of the strongest current pitches
argue for dissolving gates into confidence scores and replacing requirements with
intent. We hold the opposite line on both counts: gates harden rather than dissolve,
stories and their criteria are kept because that is where proof attaches - and every
number in this paper comes from a pre-registered, adversarially reviewed benchmark
whose raw rows are published, including the results that flatter us least.

## 3. The operating model: five instruments

The essays describe five capabilities that only work as an integrated system - a
cockpit of instruments, in this paper's framing. Each maps to a shipped subsystem;
none works alone.

| Instrument | What it means | Where it lives in SDLC Studio |
| --- | --- | --- |
| **Specification** | Intent written down precisely enough to act on and check against | PRD, TRD, epics, and stories; every acceptance criterion may carry an executable `Verify:` line that actually runs |
| **Governed platform** | The agent is a channel, not an exception: same permissions, same audit trail for every consumer, human or AI | One set of gates binds both - status transitions, verification-depth tiers, and reviewer independence apply to any writer |
| **Measurement** | Knowing the state of the system without asking anyone | `status` and `reconcile` recompute truth from the files - counts derived from a census, never asserted; the published benchmark measures the tool itself |
| **Evidence** | "Can we prove this works?" as a first-class question | `verify_ac` runs the criteria; depth tiers record how a fix was verified; the critic-verdict record is an attestation log - reviewer and author identities per unit, in the separation-of-duties sense |
| **Identity and persistence** | Durable values and judgement rather than ephemeral chat sessions | The personas ARE this instrument: a generated team whose non-negotiables persist across every session, consult, and review |

The loop that runs across these instruments is the essays' operating maxim made
executable: **"specify together, build apart, review independently."** Specification
is where the human leads - the interview, the consults, the plan gate. The build
fans out to agents working alone against the shared spec. Review runs against that
spec, never against the conversation that produced the code. And the loop is
batch-to-goal rather than time-boxed: a unit of work closes when its criteria are
verified, whether that takes an hour or a week.

## 4. The evidence: what you enforce matters more than what you spend

We benchmark the tool against plain AI coding with a genuinely good agent
configuration, on fixture repositories with **held-back acceptance suites the agent
never sees**, under a pre-registered protocol whose task set, metrics, and analysis
were frozen in git before any measured run. Results are published whichever way they
point. Two measured campaigns exist: the original July 2026 study (five runs per
cell, thirty in all) on the previous model generation, and a 72-run rerun
(10 July 2026) of the same frozen fixtures against the v4 release candidate across
three model tiers, extended by a ten-run mandated-arm addendum. The full
reports, raw rows, and grading harness are in the repository.

The fixtures are traps by construction. The headline fixture's ticket asks for a
digest-notification feature whose naive implementation silently violates an
*existing* quiet-hours rule elsewhere in the specification - the hidden-requirement
interaction that ships from real backlogs every week. Everything needed to get it
right is present in the visible workspace; the held-back suite decides pass or fail,
never judgement.

**The quadrant.** Defect escapes on the trap fixture, by model and by how the
discipline was engaged:

| | Process left to the model's judgement | No process (good baseline setup) | Process mandated |
| --- | --- | --- | --- |
| Mid-tier model (Sonnet 5) | 5/5 escaped | 2/5 | **1/5** |
| Premium model (Opus 4.8) | 3/3 | 3/3 | **0/5** |
| Frontier model (Fable 5) | 0/5 | 0/5 | not run |

(The premium tier's judgement and baseline arms ran three times each as a bridge
sample; every other cell is five runs.)

Three findings, stated with their edges:

- **On the frontier model, these single-ticket traps no longer bite** - 30 of 30
  runs clean in every arm. Where the model alone clears the bar, the pipeline's
  measurable single-ticket value is the evidence trail, at roughly 1.4x tokens.
- **On the models most teams actually deploy, the trap still ships in most runs -
  and judgement-gated process gave no protection**, because every mid-tier and
  premium agent judged the ticket too small for ceremony and skipped the planning
  pass, exactly when it was needed. One premium run named the dangerous interaction
  "the one genuinely ambiguous edge" in its delivery summary - as recorded in the
  benchmark write-up - and still shipped without resolving it.
- **Mandating the planning pass reversed the result**: escapes fell from five in
  five to one in five on the mid-tier model, and from three in three (both arms) to
  zero in five on the premium model, at 1.07-1.18x the baseline's tokens. The one
  remaining escape is itself instructive: that run's plan surfaced the interaction,
  resolved it wrongly, and shipped the wrong call with the full authority of the
  process behind it - which is why the plan itself gets an independent review gate.

**The prices.** At July 2026 list rates, assuming the typical agentic 80/20
input/output split (the assumption and arithmetic are in the benchmark report):

| Approach | Cost per delivered ticket | Escapes | Audit trail |
| --- | --- | --- | --- |
| Frontier model, no process | $0.98 | 0/5 | none |
| Frontier model, full pipeline | $1.39 | 0/5 | full |
| Premium model, no process | $0.49 | 3/3 | none |
| Premium model, mandated process | $0.52 | 0/5 | full |
| Mid-tier model, no process | $0.24-0.36 * | 2/5 | none |
| Mid-tier model, mandated process | $0.29-0.43 | 1/5 | full |

\* The mid-tier ranges reflect the model's announced list-price change (an
introductory rate until the end of August 2026), not run-to-run variance.

The process premium is three to seven cents per ticket. Enforced process on a
mid-tier model undercuts frontier prompt-and-hope by 47-70% while
producing the evidence trail the frontier run does not produce at any price. And the
worst value measured anywhere in the table is the premium model without the process:
it costs more than the governed mid-tier run and shipped the defect every time.
Spending on the model without enforcing the discipline bought nothing measurable.

**Solution quality, independently double-checked.** A post-hoc rubric review (one
reviewer per cell, five anchored dimensions) converged with the hidden suites on
every behavioural verdict - and added a finding the pass/fail oracle cannot see:
the failures were *requirements* failures, never code-quality failures. Design-fit
scores stayed high (4.0-5.0 of 5) even in the runs that shipped the defect. Every
run looked professional; roughly a quarter were wrong. Code that merely looks good is
exactly what an ungoverned base model produces.

**Auditability is measurable too.** In the July study, an independent auditor agent
answering maintainer questions from the finished workspace alone - with cited
evidence mechanically validated - scored the governed arm 0.88 against the
baseline's 0.60 on the harder fixture, and the audit score identified precisely the
runs that had shipped the defect. The rerun's sample reproduced the shape: what the
un-governed workspaces could not evidence was exactly the interaction their authors
had missed.

Because of these results, v4 ships finding 3 as product, not advice: **the
engagement floor**. A multi-file change in a spec-bearing repository requires the
planning pass - a spec delta naming every interacting requirement, one acceptance
criterion per interaction - before code. It is doctrine rule 16 and part of the
agent-instructions every consuming project inherits, with an explicit config opt-out
for operators who accept the measured risk. Judgement still scales everything above
the floor.

## 5. The team is grown, not shipped

Most agentic tooling that uses personas ships the same fixed cast of role-prompts to
every project. SDLC Studio v4 generates the team from the project itself.

`persona generate --team` reads the requirements, the stack, and the risk signals,
asks the operator only the questions it cannot infer (hard-capped, multiple-choice),
and writes fresh named working seats into the repository: three core seats
(engineering, quality, product) plus up to two signal-earned specialists such as
security or reliability, on Alan Cooper's goal-directed method - defined by goals
and refusal instincts, never demographics. A payments project gets a QA seat who is
paranoid about idempotency and reconciliation; a games project gets one who guards
frame budgets. `--stakeholders` generates the other side of the table: buyer,
compliance, operations, and served-but-not-using panels whose cards carry their veto
lines, the evidence they read, and the arbitration rule that a buyer's wants never
override the primary user's interface.

The mechanics are deterministic where they must be. Generated cards carry a
provenance stamp and content hash: an operator's edit promotes a card to authored,
and the generation flow refuses to regenerate over it. Cards stay labelled provisional-unverified -
Cooper's rule for assumption personas - until a human reviews and accepts them, and
the status dashboard counts the unreviewed until someone does. A validation floor
checks every seat has a declared role, a review render, and no demographic filler.

Why this matters beyond flavour: **the seats are load-bearing.** They consult on
designs before they freeze, score the backlog, and hold the review gate - and the
review gate is mechanical: a recorded verdict whose reviewer identity matches the
author's never clears a terminal status, and the seat that wrote the tests cannot
sign them off. Alongside the mechanical gate sits a consult discipline carried by
the templates and graded by the eval suite - each consulted seat raises at least one
concrete objection or states why none exists, because a favourable-and-vague panel
is a failed consult. For higher stakes, the reviewing seat can run on a different
model entirely: a separate instance of one model catches self-favouritism; a
different model also catches shared misreadings - the class of unreviewed
misresolution our one mandated-arm escape shipped, and the reason the plan itself
gets an independent review gate. We claim coverage from this, not intelligence: a
project-specific cast is built to catch the blind spots a generic prompt walks past.
It does not make the model smarter, and nothing in this paper says it does.

## 6. Proven practice, operationalised

SDLC Studio's second structural bet is that the practices which survived decades of
software engineering literature work as a *system*, and that an agent finally makes
running the full system affordable. What ships is not advice about these methods but
machinery that refuses to proceed without them:

| Practice | As enforced machinery |
| --- | --- |
| Goal-directed personas (Cooper) | Generated cast, one-Primary-per-interface validation, provisional labelling, persona-tagged requirements coverage |
| Three Amigos | Resolvable seats with a mechanical author-never-reviews-own-work gate |
| WSJF prioritisation | Seat-scored backlog ordering in the sprint planner |
| TDD / BDD | Given-When-Then criteria with executable `Verify:` lines; red-first default; a story cannot reach Done while its criteria fail |
| Change control | RFC-before-CR design exploration; gated status transitions; every change an artefact |
| Retrospectives | Sprint close files a retro artefact; lessons accumulate in a registry recalled before decisions |
| Separation of duties | The critic-verdict attestation log: reviewer and author recorded per unit, identity-checked |
| Audit readiness | The census-reconciled workspace: indexes derived from files, drift detected and repaired mechanically |

The pattern all of these share - and the reason they hold when deadline pressure
arrives - is the benchmark's lesson generalised: **refuse to proceed without
compliance.** The check is a script that blocks, not a guideline that hopes.

## 7. Architecture and a worked example

Everything lives as plain markdown and small deterministic scripts inside your
repository - no server, no database, no vendor account. The skill installs into the
agent you already use (one install covers the major agent runtimes), and its
mechanical spine is a set of standard-library scripts: id allocation, status
transitions with cascade, census-based reconciliation, executable-criteria
verification, the portable quality gate, the persona generator, the critic ledger.
The model does the judgement; the scripts do the arithmetic; neither is asked to do
the other's job.

What one unit of work actually looks like - this trail is from the tool's own
repository, which builds itself through its own pipeline:

1. A defect is found (in this case by an agent dogfooding the release candidate
   during the benchmark). `file_finding.py` creates the bug artefact with an
   allocated id, reproduction steps, and severity - the index row is written
   mechanically, never by hand.
2. The fix is developed test-first: the regression test fails against the old code,
   then passes.
3. Close is a gated, single call: the transition records the verification depth
   (what was actually run to prove the fix) and an independent reviewer's verdict.
   The gate refuses a reviewer id equal to the author id, and refuses a terminal
   status with no recorded depth. The verdict lands in the attestation ledger.
4. `reconcile` recomputes the indexes from the file census; the pre-commit gate
   re-runs style, links, structural validation, conformance, and - for any commit
   touching code - the full test suite. The paperwork ships in the same commit as the code.

The result, for an auditor, is that any change can be walked backwards: commit to
artefact, artefact to criteria, criteria to verification output, verification to an
independent identity that attested to it. That chain is what a change-approval
board actually asks for, and it was produced by delivering the fix, not by a
documentation sprint afterwards.

For scale, the same loop fans out: an epic decomposes into stories, waves of
implementation agents run in parallel worktrees against collision-free artefact ids
(ULIDs, so concurrent humans and agents on different machines never fight over
sequential numbers), and quality gates hold at every wave boundary. The field
results below all have this shape: one planning structure, many units delivered
under it.

## 8. Governance and attestation

For the reader who answers to a regulator, the properties that matter:

- **Everything is in your repository.** Specs, criteria, verdicts, and evidence are
  version-controlled files you own. Nothing leaves; there is no platform to trust.
  The exit cost is correspondingly honest: removing the skill leaves you with plain
  markdown and your own git history - nothing to migrate off.
- **The skill itself is inspectable.** Its mechanical layer is standard-library
  Python and shell inside your repository - no network calls, no binaries, nothing
  to audit beyond what you can read.
- **Separation of duties is enforced, not asserted.** The author of a change cannot
  be its reviewer; the check is an identity comparison in a script, and the verdict
  record carries both identities per unit - the shape SOC 2 CC8.1 auditors ask for.
- **Evidence has a checkable form.** A criterion's `Verify:` line either ran and
  passed or it did not - the Done gate reads only the machine-written report, so a
  hand-stamped verification state is a detectable lie, recomputable on demand. A
  bug's verification depth is recorded or its close is refused. The review ledger's
  protections are identity distinctness and version-controlled history; it is an
  append-only record, not a cryptographic one.
- **The agent is not an exception path.** Human and agent writers pass the same
  gates, produce the same trail, and are refused by the same checks - the essays'
  "same permissions, same audit trail" made literal.
- **Drift is detected mechanically.** Because indexes and status are recomputed
  from a census of the files, a workspace that claims more than it contains is
  caught by reconciliation, not by hoping someone notices.

## 9. Adoption

The pipeline scales to the size of what you run it on, and the honest path in is
incremental:

- **Ten minutes, zero setup:** point it at an existing repository and run a
  read-only three-leg review. Findings arrive as filed bug and change-request
  artefacts; nothing else is touched. This is also the moment it offers to generate
  your team from what it just read.
- **First week:** adopt the lite profile - requirements, stories, implement - on one
  small project. Executable criteria and the review gate come with it; the heavier
  ceremony does not, until you ask.
- **Brownfield estates:** `prd generate` reads the code first and writes the
  specification as a migration blueprint, validated by running tests against the
  real implementation - requirements written with full technical context, an idea
  the closed-platform school articulates well and which an open skill can deliver
  against your own repository.
- **The human load shifts rather than grows.** Someone ratifies specs, approves
  plans, reviews generated personas, and tags releases - the bookend roles stay
  human by design. The reading load is real; the typing load largely disappears;
  the lite profile keeps the ceremony proportionate while the habits form.
- **Existing projects are never auto-switched.** Upgrades ask explicit questions
  (identity scheme, team generation, defaults) and apply nothing without consent.

Field results from production use - reported by the tool's author, at real scale
and stakes but without a counterfactual arm, so read them as experience reports: a
thirty-site maintenance deliverable estimated at twelve months delivered in under
seven days with a CAB-grade audit trail; features estimated at five engineers for
twenty weeks delivered in under a week. The common shape is the fan-out economics of
section 7: the pipeline's fixed costs spread across every unit delivered under them.

## 10. Limitations and non-goals

Stated with the same discipline the tool enforces:

- **The benchmark is small.** Two fixture families carry the escape signal; five
  runs per cell; the mandated-arm study was designed after the matrix results were
  known and is labelled exploratory. Direction is consistent; formal significance
  at this sample size is not claimed. The protocol, fixtures, and raw rows are
  published for anyone to re-run.
- **On frontier models, single-ticket defect prevention is not the pitch.** The
  current frontier cleared our traps unaided. There, the measurable value is the
  evidence trail and the discipline's persistence; the defect-prevention value
  concentrates on the mid-tier and premium models most teams actually run.
- **Two escapes in our own published table are harness artefacts** (a
  phrasing-brittle check in one frozen fixture), disclosed and kept as recorded
  because the oracle is the oracle. The fix ships in the next protocol revision.
- **Compounding value on long-lived, multi-team estates is argued, not yet
  benchmarked.** Single-ticket fixtures structurally cannot show specification
  drift across a sequence of dependent changes; a longitudinal protocol is designed
  and queued. Until then that story rests on the field reports and the mechanism.
- **Personas buy coverage, not capability.** The literature is clear that personas
  do not make models smarter, and neither do we.
- **This is not an autonomy play.** The operator gates remain human by design:
  specs are ratified, plans are approved, releases are tagged by a person who
  answers for them. Teams seeking lights-out software factories are reading the
  wrong paper.

## 11. Claims register {#claims-register}

Every load-bearing claim in this paper, with its verification path. An unverifiable
claim in a paper about verifiable delivery would be a poor start.

| Claim | Evidence |
| --- | --- |
| Quadrant escape figures; 1.07-1.18x mandated token overhead | `docs/benchmarks/2026-07-10-v4-rerun.md`; raw rows `tools/bench/results/runs.jsonl`; every figure independently recomputed by a reviewer agent before publication (archived summary: `tools/bench/results/v4-rerun/verification-note.md`) |
| Pricing table and the 3-7 cent process premium | Pricing appendix of the same report; July 2026 list rates; 80/20 blend assumption stated |
| July 10/10 vs 2/5 escape result; auditability 0.88 vs 0.60 | `docs/benchmarks/2026-07-08-n5-run.md` (previous model generation, kept dated) |
| Rubric convergence with the hidden suites; requirements-not-code-quality failures | Rubric archive `tools/bench/results/v4-rerun/`; convergence claim restricted to behavioural verdicts, artefact rows disclosed |
| Engagement floor as default | Doctrine rule 16; `templates/agent-instructions.md`; `engagement_floor` in the config reference |
| Independence gate, depth-gated closes, attestation ledger | `scripts/transition.py`, `scripts/critic.py`; the tool's own repository history is the working example |
| Generated team mechanics (never-clobber, provisional labels, validation floor) | `scripts/persona_gen.py`, `scripts/validate.py`; flow in `reference-persona-generate.md` |
| Operationalised-practice table rows (WSJF, red-first, retros, coverage checks) | Each row's machinery is named in-repo: `reference-sprint.md`, `scripts/validate.py serves`, `scripts/artifact.py` retro type |
| "One install covers the major agent runtimes" | `install.sh --list-targets` |
| Genre characterisations and the fixed-cast observation (sections 2 and 5) | The project's competitive-research record (RFC0028); specific citations held by the project and available on request - anonymised here under the no-competitor policy |
| DORA 2024 correlation; ~5% of pilots extract value | 2024 DORA Accelerate State of DevOps report; MIT "GenAI Divide" (2025) |
| Twelve-months-to-seven-days and related field results | Operator-reported production deliveries; explicitly uncontrolled, labelled as experience reports |
| "The bottleneck was never typing speed..." and the mill argument | The author's Real World Engineering essays (linked below), quoted as the project's philosophical basis |

## Sources and further reading

- Darren Benson, *The Future of Software Engineering* and *A Steam Engine in Every
  Cottage*, Real World Engineering (realworldengineering.substack.com) - the
  philosophical basis, quoted throughout.
- SDLC Studio benchmark reports: protocol v2 pre-registration, the July 2026 N=5
  study, and the 10 July 2026 v4 rerun with the mandated-arm addendum and pricing
  appendix - all under `docs/benchmarks/` with raw data in-repo.
- *Why SDLC Studio* (`docs/why-sdlc-studio.md`) - the evidence argument at article
  length; the README for the ten-minute start.
- DORA, *Accelerate State of DevOps* (2024); MIT, *The GenAI Divide* (2025).

---

*SDLC Studio is an open-source agent skill (MIT licence) in the open Agent Skills format. It is
not affiliated with any model vendor or platform named in its benchmark disclosures.
This paper names no competitors by design: the positions engaged under "others
argue" are held by several current products and papers, and the disagreement is
with the arguments, not the vendors.*
