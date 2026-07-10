# Why SDLC Studio

> The short version: disciplined software process has always worked and has almost never
> been sustained, because it spends the expensive currency - engineer attention. Agents move
> that cost into the cheap currency (tokens), and deterministic gates make the discipline
> enforced rather than aspirational. SDLC Studio is that trade, packaged: the proven
> SDLC discipline, run by the agent and policed by the tooling. This document lays out the argument, the
> evidence for it (including the unflattering parts), and the economics - each section
> deeper than the last. Read as far as you need.

## The problem is not knowledge, it is pressure

Every experienced engineering leader knows what good delivery looks like: clear
requirements, acceptance criteria written before code, traceability from intent to
implementation, independent review, a definition of done that means done. Almost no team
sustains it. Under deadline pressure the acceptance criteria thin out, the review becomes a
skim, the spec goes stale the week after it is written, and the test inventory is whatever
survived the sprint. This is not a failing of individuals - it is the predictable economics
of a process whose every step costs scarce human attention.

AI coding made this worse before it made it better. "Vibe coding" - prompt, generate, hope -
produces a demo fast, but the intent lives only in a chat that scrolls away, nothing checks
the result against what was asked, and by release nobody (the model included) can say what
done meant. The industry's first correction, spec-driven development, writes intent down
first - a real step up. But the spec is prose the agent produced and is then *trusted* to
honour, and nothing recomputes whether code and documents still agree ten changes later.
Trust-based process decays under pressure whether the executor is a human or a model.

SDLC Studio's bet is the third step: keep the specs and plans, and add a source of truth the
tooling **recomputes from the files and holds the agent to**. Status is derived from a
census, never asserted. Acceptance criteria carry executable `Verify:` lines that actually
run. A story cannot reach Done while its criteria are red (an operator override exists,
and is recorded - never silent). A review verdict whose reviewer id matches its author id
never clears the Done gate, so nobody signs off their own work. The discipline stops
depending on anyone (carbon or silicon) remembering it under pressure.

## The mill, not the engine

The project's design philosophy is published in its author's Real World Engineering essays
([The Future of Software Engineering](https://realworldengineering.substack.com/p/the-future-of-software-engineering),
[A Steam Engine in Every Cottage](https://realworldengineering.substack.com/p/a-steam-engine-in-every-cottage)),
and SDLC Studio is the executable form of that argument. The claim, in his words: "the
bottleneck was never typing speed. It was, and remains, knowing what to build and being able to prove it
worked." Faster code generation attacks the wrong constraint. The essays' industrial
analogy: "the code is the cloth. The organisation around it is where the money is" - at
Cromford it was not any single machine that changed the economics of cotton, it was the
mill: the organisation of machines, flow, and accountability around them. Prompt-and-hope
AI coding is "a steam engine in every cottage" - the old way of working, a bit faster.
Building the mill is the actual revolution, and it does not feel like one while you are
laying it out. SDLC Studio is a mill you can install.

Two more commitments follow from the essays. **The specification becomes the durable
artifact and code becomes disposable output** - which is why the pipeline's centre of
gravity is the spec, the acceptance criteria, and the proof, not the diff. And **the human
stays in the lead, not merely in the loop**: of the three futures (full automation, human
rubber-stamping the machine, human directing it), only the third survives contact with
accountability. The unsaid is where damage happens, so the instruments exist to make the
unsaid visible - and the person "who reads the dashboard, frames the wish and answers for
the outcome becomes more necessary with each cycle, not less."

## The cockpit: five instruments

The essays describe five capabilities that only work as an integrated system - a cockpit of
instruments, in this document's framing. Each maps to a shipped subsystem:

| Instrument | What it means | Where it lives here |
| --- | --- | --- |
| **Specification** | Intent written down, precise enough to act on and check against | PRD/TRD/epics/stories; executable `Verify:` lines on acceptance criteria |
| **Governed platform** | AI as a channel, not an exception: "same permissions, same audit trail" for every consumer, human or agent | The same gates bind both - transitions, independence, depth tiers apply to any writer |
| **Measurement** | Knowing the state of the system without asking anyone | `status`/`reconcile` recompute truth from the files; the published benchmark measures the tool itself |
| **Evidence** | "Can we prove this works?" as a first-class question | `verify_ac`, verification-depth tiers, and the critic-verdict record - an **attestation log** in the separation-of-duties sense (the reviewer who approved is recorded, distinct from the author, per unit; the shape auditors ask for when they ask who attested to this change) |
| **Identity / persistence** | Durable values and judgement, not ephemeral chat sessions | The personas ARE this instrument: a generated team whose non-negotiables persist across every session, consult, and review |

One consequence of instrument two worth stating plainly: because review is a seat with an
identity, not a pass of the same context, the reviewer may run on **a different model or
instance** than the author. Prompt-level independence on one model still shares that model's
blind spots; cross-model review is the stronger form, and the critic flow supports it
(see the doctrine's independence gate).

## The founding observation, reproduced in agents

The design thesis came from years of building and reforming engineering teams: humans under
pressure skip hygiene, so process survives only when it is infrastructure rather than
virtue. What we did not expect was how literally that observation would transfer.

In our controlled benchmark (below), the arm that had the full pipeline *installed and
available*, with judgement about when to use it, behaved exactly like the plain-AI baseline:
under effort pressure it skipped the process, implemented the ticket text directly, went
green on its own tests - and shipped the same requirements-interaction defect the baseline
shipped. The only arm that caught that defect class was the one where the planning pass was
**mandatory**. Agents, it turns out, are lazy under pressure in precisely the way engineers
are. Which is the whole argument for gates over goodwill, and why SDLC Studio's checks are
deterministic scripts the model cannot skip, not instructions it is asked to follow.

## Proven practice, operationalised

Most tooling in this space operationalises one methodology, if any. SDLC Studio's thesis is
that the practices that survived decades of software engineering literature work as a
system, and it enforces them together: Alan Cooper's goal-directed personas (generated from
your project, one Primary per interface, validation scenarios never driving layout), the
Three Amigos (as resolvable seats with an author-never-reviews-own-work gate), WSJF backlog
scoring, TDD/BDD with executable acceptance criteria, retrospectives that file artifacts,
RFC-before-CR design exploration, CAB-grade audit trails, and separation of duties. The
pattern shared by every practice here - and the reason they hold when deadline pressure
arrives - is **refuse to proceed without compliance**: the check is a script that blocks,
not a guideline that hopes.

The sprint loop maps the essays' operating maxim verbatim - **"specify together, build
apart, review independently."** Specification is where the human leads (the interview, the
consults, the plan gate); the build fans out to agents working alone against the shared
spec; review runs against that spec, never against the conversation that produced the code.
And the loop is deliberately **batch-to-goal, not time-boxed**: the essays' "railway time"
point is that coordination regimes change when the machine does - a fixed-length sprint is
local sun time kept after the trains arrived. A batch closes when its goal is verified,
whether that takes an afternoon or a week.

## Others argue for a different shape

Others argue that the way to enterprise-grade agentic delivery is a closed platform: give
the vendor's models unbounded context over your estate, let requirements flow straight to
code, and eliminate intermediate artifacts - user stories included - as drag. We think the
opposite, and the disagreement is precise. **Stories are where the proof lives.** A story
carries its acceptance criteria, its executable verifications, its depth tier, and its
per-unit review verdict; delete the story and you have deleted the place evidence attaches.
Our stance: enforced process with verifiable artifacts, independent review that no author
can waive, and everything - specs, verdicts, audit trail - as plain files in **your**
repository, portable to any agent you already run. If the category is autonomous delivery
platforms, then a disciplined open stack - this skill plus the coding agent you already
have - is that category on your own terms. One idea from that school is worth adopting
rather than opposing: requirements written with full technical context beat requirements
written blind, which is exactly what `prd generate` does for a brownfield repo - it reads
the code first, so feasibility is in the requirement from the start. On evidence, the
register differs too: that school quotes multiples; we publish an adversarial benchmark
with the unflattering findings left in (below).

## The evidence

We hold positioning claims to the same standard the tool holds code to, so the evidence
below is labelled by what it is, includes the results that flatter us and the results that
do not, and links to the raw data. (In a category full of framework hype, publishing the
unflattering findings is itself the differentiator.)

### Production field results (operator-reported, uncontrolled)

Reported by the tool's author from his own production deliveries with SDLC Studio - real
scale and stakes, no counterfactual arm, so read these as experience reports rather than
measurements:

- A maintenance deliverable estimated at twelve months - thirty production websites -
  delivered in under seven days, with every action auditable and a full test inventory
  sufficient for CAB sign-off to production deployment.
- Production features estimated at a team of five for twenty weeks, delivered in under a
  week.
- This repository dogfoods the skill on itself: its features are delivered through its
  own pipeline, with the audit trail in the repo to inspect.

The common shape: one planning structure fanned out across many units of work, an audit
trail that a change-approval board would accept, and the elapsed-time compression coming
from agents executing a process that no human team could afford to run at that fidelity.

### Controlled benchmark (small n, adversarially reviewed, raw data published)

We built a measurement harness ([protocol](benchmarks/protocol-v2.md), pre-registered before
the runs so results could not be quietly reshaped) comparing three arms on fixture repos
with **held-back acceptance suites the agent never sees**: plain AI coding with a genuinely
good CLAUDE.md (independently reviewed against straw-manning), the pipeline available with
judgement, and the pipeline with a mandated planning pass. Findings from the measured N=5
run ([N=5 report](benchmarks/2026-07-08-n5-run.md); spikes:
[v1](benchmarks/2026-07-08-n1-spike.md), [v2](benchmarks/2026-07-08-v2-respike.md)):

- **On small, well-specified tasks the pipeline adds nothing** - the baseline matched it.
  The tool's own scale-to-size doctrine says the same; run `profile: lite` there.
- **On a multi-file task whose existing spec silently interacted with the ticket, every
  unstructured run shipped the same defect - ten out of ten.** Both non-mandated arms, all
  five runs each, missed a quiet-hours rule the ticket never mentioned and declared done on
  green self-written tests. The held-back suite caught all ten.
- **The mandated-planning arm escaped in two runs of five.** Forced to write acceptance
  criteria from the spec before code, it pinned the interacting requirements correctly in
  three runs and passed the full hidden suite; in two runs the planner misread the rule,
  the reviewer approved against the plan's wrong oracle, and the error shipped - in one of
  those two, written into the spec itself. Direction is consistent (10/10 vs 2/5) but
  below conventional
  significance at this sample size (one-sided Fisher p 0.083), and it names the honest
  boundary: mandated planning changes *where* an error must occur, it does not make errors
  impossible. A bad plan propagates with authority - which is why the next pipeline change
  this data points at is an independent check of the plan against the spec.
- **Auditability is measurable - and it graded us honestly.** An independent auditor agent
  answering maintainer questions from the finished workspace alone (with cited evidence
  mechanically validated - a cited test must fail against a seeded mutant to count) scored
  the harder fixture at N=5: mandated-planning arm 0.88, judgement-scaled pipeline arm
  0.68, plain-AI baseline 0.60 - and within the mandated arm the audit score identified
  precisely the two runs that shipped the defect. On the easier fixture all arms scored
  0.97-1.0. Nothing in the scoring rewards the tool's own artifacts; the baseline could
  have scored 1.0 with good tests and docs.
- Honest caveats: n=5 per cell and one fixture pair carries the escape signal; fixtures
  were authored in-ecosystem (independently fairness-reviewed, and everything needed to
  pass is present in each visible workspace); planning-versus-review contributions remain
  partially entangled. Raw rows and the grading harness are in the repo.

## The economics

Tokens are the wrong denominator; engineer time and defect cost are the right ones. Three
facts to price honestly:

1. **Per single ticket, the full pipeline costs more tokens** - about 3.1 times the
   baseline, measured at N=5 (the overhead is the planning and review passes, not a slower
   implementation). If your unit of work is one small, well-specified change, that
   overhead buys little (see the lite profile).
2. **The overhead amortises with fan-out.** One planning structure driving many units is
   where the field results live: the pipeline's fixed costs (spec extraction, planning,
   gates) spread across every unit delivered under them, while the per-unit defect
   protection repeats.
3. **Model-tier routing attacks the variable cost.** The pipeline estimates each unit's
   difficulty from deterministic signals (blast-radius complexity, churn risk, scope,
   novelty, spec size) and recommends a model tier from a map you declare - trivial work
   runs on your cheapest model, hard work on your strongest, and the independent critic is
   never a smaller model than the author. At N=5 the router sent four of five deliveries on
   the easy fixture to the smallest tier (a 0.40 mean cost index against an all-mid-tier
   mix) with zero defect escapes, and correctly refused to down-tier the harder fixture.

Against those costs, the comparison that matters: a defect that reaches production - or an
audit you cannot pass - is priced in engineer-days and trust, not tokens. The benchmark's
one measured escape-prevention was a bug both unstructured runs shipped confidently.

## Built for teams - human and agentic

The direction of travel is trunk-based delivery by small human teams directing larger
agentic ones, and the foundations for that are shipped: distributed artifact identity
(ULIDs, so concurrent agents in parallel worktrees never fight over sequential numbers, with
friendly aliases for humans), atomic index writes with advisory locking, typed authorship
(`raised_by`/`triaged_by`) with a separation-of-duties lint, and evidence-as-schema so
"proof" has a checkable shape. As of v4 this is the default for every new project
(`schema_version: 3`); an existing project is never auto-switched - `project upgrade` asks
the numbering question explicitly, and forward-only adoption (old ids stay valid, new
artifacts mint ULIDs) is fully supported.

## What we are still proving

- Statistical significance: the N=5 escape difference (10/10 vs 2/5) is directionally
  consistent across runs but needs a larger sample to clear conventional thresholds.
- The fix for the measured failure mode: an independent check of the plan's acceptance
  criteria against the source spec, so a mis-read rule cannot propagate with authority.
- Whether the value is *having* good acceptance criteria or *mechanically enforcing* them -
  a planned arm with ticket-grade ACs but no gates.
- Fan-out economics as a measurement rather than a field report.

## Try it in ten minutes

- **On an existing repo, zero setup:** `/sdlc-studio review generate` - a three-leg review
  of your actual codebase, findings filed as bugs and change requests, remediation-only on
  anything sensitive.
- **On a small project without the ceremony:** set `profile: lite` and the pipeline
  collapses to PRD, story, implement - promotable to the full discipline later.
- **From an idea:** "start a new project", answer the interview, and watch the spec, plan,
  code, tests and proof arrive as reviewable files.

The [README](../README.md) has the full quick start.
